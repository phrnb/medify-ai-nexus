
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Path
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.v1.deps import get_db, get_current_verified_user, log_user_activity
from app.crud.crud_ai_feedback import ai_feedback
from app.crud.crud_analysis import analysis as crud_analysis
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.models.ai_feedback import FeedbackTypeEnum, FeedbackSeverityEnum, FeedbackStatusEnum
from app.schemas.ai_feedback import AIFeedback, AIFeedbackCreate, AIFeedbackUpdate, AIFeedbackDetail

router = APIRouter()

@router.get("", response_model=List[AIFeedback])
def read_ai_feedback(
    request: Request,
    db: Session = Depends(get_db),
    feedback_type: Optional[FeedbackTypeEnum] = Query(None, description="Filter by feedback type"),
    severity: Optional[FeedbackSeverityEnum] = Query(None, description="Filter by severity"),
    status: Optional[FeedbackStatusEnum] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Retrieve AI feedback with optional filtering.
    """
    # For non-superusers, only show their own feedback
    user_id = None
    if not current_user.is_superuser:
        user_id = current_user.id
        
    feedback_list = ai_feedback.get_filtered_feedback(
        db, 
        feedback_type=feedback_type, 
        severity=severity, 
        status=status,
        user_id=user_id,
        start_date=start_date, 
        end_date=end_date, 
        skip=skip, 
        limit=limit
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed AI feedback list",
        resource_type="ai_feedback"
    )
    
    return feedback_list

@router.post("", response_model=AIFeedback)
def create_ai_feedback(
    request: Request,
    *,
    db: Session = Depends(get_db),
    feedback_in: AIFeedbackCreate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Create new AI feedback.
    """
    # Validate analysis exists if provided
    if feedback_in.analysis_id:
        analysis = crud_analysis.get(db, id=feedback_in.analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found",
            )
    
    # Create feedback
    feedback = ai_feedback.create_with_user(
        db, obj_in=feedback_in, user_id=current_user.id
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.create,
        description=f"User submitted AI feedback of type {feedback.feedback_type}",
        resource_type="ai_feedback",
        resource_id=feedback.id
    )
    
    return feedback

@router.get("/{feedback_id}", response_model=AIFeedbackDetail)
def read_ai_feedback_by_id(
    request: Request,
    *,
    db: Session = Depends(get_db),
    feedback_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get specific AI feedback by ID.
    """
    feedback = ai_feedback.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI feedback not found",
        )
    
    # Check permissions: only superusers and the feedback creator can see it
    if not current_user.is_superuser and feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this feedback",
        )
    
    # Create detailed response
    feedback_detail = AIFeedbackDetail.from_orm(feedback)
    
    # Add additional info
    if feedback.user:
        feedback_detail.username = feedback.user.full_name
    if feedback.reviewer:
        feedback_detail.reviewed_by_name = feedback.reviewer.full_name
        
    # Add analysis details if available
    if feedback.analysis:
        feedback_detail.analysis_details = {
            "id": feedback.analysis.id,
            "result": feedback.analysis.result,
            "ai_diagnosis": feedback.analysis.ai_diagnosis,
            "severity": feedback.analysis.severity,
            "confidence": feedback.analysis.confidence,
            "status": feedback.analysis.status,
        }
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed AI feedback details",
        resource_type="ai_feedback",
        resource_id=feedback.id
    )
    
    return feedback_detail

@router.put("/{feedback_id}", response_model=AIFeedback)
def update_ai_feedback(
    request: Request,
    *,
    db: Session = Depends(get_db),
    feedback_id: str = Path(...),
    feedback_in: AIFeedbackUpdate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Update AI feedback.
    """
    feedback = ai_feedback.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI feedback not found",
        )
    
    # Check permissions: only feedback creator can update content
    # But superusers can update status
    if not current_user.is_superuser and feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this feedback",
        )
    
    # If user is not superuser, they can only update content and additional details
    if not current_user.is_superuser:
        feedback_in_dict = feedback_in.dict(exclude_unset=True)
        for field in ["status"]:
            if field in feedback_in_dict:
                del feedback_in_dict[field]
        
        feedback = ai_feedback.update(db, db_obj=feedback, obj_in=feedback_in_dict)
    else:
        # Superusers can update everything
        feedback = ai_feedback.update(db, db_obj=feedback, obj_in=feedback_in)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User updated AI feedback",
        resource_type="ai_feedback",
        resource_id=feedback.id
    )
    
    return feedback

@router.post("/{feedback_id}/review", response_model=AIFeedback)
def review_ai_feedback(
    request: Request,
    *,
    db: Session = Depends(get_db),
    feedback_id: str = Path(...),
    status: FeedbackStatusEnum = Query(FeedbackStatusEnum.reviewed),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Mark AI feedback as reviewed.
    """
    # Only superusers can review feedback
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to review feedback",
        )
    
    feedback = ai_feedback.mark_as_reviewed(
        db, feedback_id=feedback_id, reviewer_id=current_user.id, status=status
    )
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI feedback not found",
        )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User marked AI feedback as {status}",
        resource_type="ai_feedback",
        resource_id=feedback.id
    )
    
    return feedback
