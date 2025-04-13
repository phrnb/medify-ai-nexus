
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Path, BackgroundTasks
from sqlalchemy.orm import Session
import requests
import json
from datetime import datetime

from app.api.v1.deps import get_db, get_current_verified_user, log_user_activity
from app.crud.crud_analysis import analysis as crud_analysis
from app.crud.crud_image import image as crud_image
from app.crud.crud_notification import notification as crud_notification
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.models.analysis import AnalysisStatusEnum, SeverityEnum
from app.models.notification import NotificationTypeEnum
from app.models.image import ImageStatusEnum
from app.schemas.analysis import Analysis, AnalysisCreate, AnalysisUpdate, AnalysisDetail, AnalysisVerification, AIAnalysisResult
from app.schemas.notification import NotificationCreate
from app.core.config import settings

router = APIRouter()

def process_image_analysis(
    db: Session, 
    image_id: str, 
    analysis_id: str, 
    user_id: str
) -> None:
    """Background task to process image analysis with AI"""
    try:
        # Get the image
        image = crud_image.get(db, id=image_id)
        if not image:
            # Log error and update analysis
            analysis = crud_analysis.get(db, id=analysis_id)
            analysis.status = AnalysisStatusEnum.failed
            analysis.result = "Image not found"
            db.add(analysis)
            db.commit()
            return
        
        # Update image status
        image.status = ImageStatusEnum.pending_analysis
        db.add(image)
        
        # Update analysis status
        analysis = crud_analysis.get(db, id=analysis_id)
        analysis.status = AnalysisStatusEnum.processing
        db.add(analysis)
        db.commit()
        
        # In a real application, we would send the image to a neural network service
        # For this demo, we'll simulate an API call with a mock response
        
        try:
            # Simulate calling an AI service
            # In production, this would be a real API call to your AI service
            # response = requests.post(
            #     f"{settings.NN_SERVICE_URL}/analyze",
            #     files={"image": open(image.file_path, "rb")},
            #     data={"image_type": image.image_type}
            # )
            # ai_result = response.json()
            
            # For demo: simulate AI analysis with mock data
            import random
            import time
            
            # Simulate processing time
            time.sleep(2)
            
            # Mock AI result
            conditions = {
                "xray": ["Pneumonia", "Tuberculosis", "Lung Cancer", "Normal"],
                "mri": ["Brain Tumor", "Multiple Sclerosis", "Stroke", "Normal"],
                "ct": ["Pulmonary Embolism", "Appendicitis", "Kidney Stones", "Normal"],
                "ultrasound": ["Gallstones", "Liver Cyst", "Normal"],
                "pet": ["Metastatic Cancer", "Alzheimer's Disease", "Normal"],
                "other": ["Abnormal Finding", "Normal"]
            }
            
            # Choose random condition based on image type
            image_type = image.image_type
            available_conditions = conditions.get(image_type, conditions["other"])
            diagnosis = random.choice(available_conditions)
            
            # Generate random confidence level
            confidence = round(random.uniform(0.65, 0.99), 2)
            
            # Determine severity based on diagnosis and confidence
            if "Normal" in diagnosis:
                severity = SeverityEnum.normal
            elif confidence > 0.9:
                severity = random.choice([SeverityEnum.moderate, SeverityEnum.severe])
            elif confidence > 0.8:
                severity = random.choice([SeverityEnum.mild, SeverityEnum.moderate])
            else:
                severity = SeverityEnum.mild
                
            # Generate mock findings
            findings = []
            if "Normal" not in diagnosis:
                possible_findings = [
                    f"Detected {diagnosis} with {confidence*100:.1f}% confidence",
                    f"Abnormal tissue density observed in affected area",
                    f"Contrast enhancement indicates potential {diagnosis.lower()} activity",
                    f"Structural changes consistent with {diagnosis.lower()}"
                ]
                findings = random.sample(possible_findings, random.randint(1, len(possible_findings)))
            else:
                findings = ["No significant abnormalities detected"]
            
            # Create mock AI result
            ai_result = {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "severity": severity,
                "findings": findings,
                "details": {
                    "regions_of_interest": [
                        {"x": random.randint(100, 300), "y": random.randint(100, 300), 
                         "width": random.randint(50, 150), "height": random.randint(50, 150),
                         "confidence": confidence}
                    ],
                    "model_version": "v1.2.3"
                }
            }
            
            # Update analysis with results
            analysis.status = AnalysisStatusEnum.completed
            analysis.result = diagnosis
            analysis.confidence = confidence
            analysis.ai_diagnosis = diagnosis
            analysis.severity = severity
            analysis.raw_results = ai_result
            
            # Update image status
            image.status = ImageStatusEnum.analyzed
            
            db.add(analysis)
            db.add(image)
            db.commit()
            
            # Create notification for the user
            notification_data = NotificationCreate(
                user_id=user_id,
                type=NotificationTypeEnum.analysis_complete,
                title="Analysis Complete",
                message=f"Analysis for image {image.original_filename} is now complete.",
                link=f"/analyses/{analysis.id}"
            )
            crud_notification.create(db, obj_in=notification_data)
            
        except Exception as e:
            # Handle errors in AI processing
            analysis.status = AnalysisStatusEnum.failed
            analysis.result = f"Error: {str(e)}"
            image.status = ImageStatusEnum.error
            
            db.add(analysis)
            db.add(image)
            db.commit()
            
            # Create error notification
            notification_data = NotificationCreate(
                user_id=user_id,
                type=NotificationTypeEnum.analysis_error,
                title="Analysis Error",
                message=f"Error during analysis of image {image.original_filename}: {str(e)}",
                link=f"/images/{image.id}"
            )
            crud_notification.create(db, obj_in=notification_data)
            
    except Exception as e:
        # Handle any other errors
        try:
            # Try to update analysis status
            analysis = crud_analysis.get(db, id=analysis_id)
            if analysis:
                analysis.status = AnalysisStatusEnum.failed
                analysis.result = f"System error: {str(e)}"
                db.add(analysis)
                db.commit()
        except:
            # If that fails too, just log the error
            pass

@router.get("", response_model=List[Analysis])
def read_analyses(
    request: Request,
    db: Session = Depends(get_db),
    status: Optional[AnalysisStatusEnum] = Query(None, description="Filter by status"),
    severity: Optional[SeverityEnum] = Query(None, description="Filter by severity"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Retrieve analyses with optional filtering.
    """
    analyses = crud_analysis.get_filtered_analyses(
        db, 
        status=status, 
        severity=severity, 
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
        description=f"User viewed analyses list",
        resource_type="analysis"
    )
    
    return analyses

@router.post("", response_model=Analysis)
def create_analysis(
    request: Request,
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    analysis_in: AnalysisCreate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Request a new AI analysis for an image.
    """
    # Check if image exists
    image = crud_image.get(db, id=analysis_in.image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    # Check if image already has an ongoing analysis
    existing_analysis = crud_analysis.get_by_image_id(db, image_id=analysis_in.image_id)
    if existing_analysis and existing_analysis.status in [AnalysisStatusEnum.pending, AnalysisStatusEnum.processing]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This image already has an ongoing analysis",
        )
    
    # Create analysis record
    analysis = crud_analysis.create(db, obj_in=analysis_in)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.analyze,
        description=f"User requested analysis for image: {image.original_filename}",
        resource_type="analysis",
        resource_id=analysis.id
    )
    
    # Start background processing
    background_tasks.add_task(
        process_image_analysis, 
        db=db, 
        image_id=analysis_in.image_id, 
        analysis_id=analysis.id,
        user_id=current_user.id
    )
    
    return analysis

@router.get("/{analysis_id}", response_model=AnalysisDetail)
def read_analysis(
    request: Request,
    *,
    db: Session = Depends(get_db),
    analysis_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get specific analysis by ID.
    """
    analysis = crud_analysis.get(db, id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    
    # Create detailed response
    analysis_detail = AnalysisDetail.from_orm(analysis)
    
    # Add additional info
    if analysis.image:
        analysis_detail.image_type = analysis.image.image_type
        if analysis.image.patient:
            analysis_detail.patient_id = analysis.image.patient.id
            analysis_detail.patient_name = f"{analysis.image.patient.first_name} {analysis.image.patient.last_name}"
    
    if analysis.verified_by:
        analysis_detail.verified_by_name = analysis.verified_by.full_name
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed analysis details",
        resource_type="analysis",
        resource_id=analysis.id
    )
    
    return analysis_detail

@router.post("/{analysis_id}/verify", response_model=Analysis)
def verify_analysis(
    request: Request,
    *,
    db: Session = Depends(get_db),
    analysis_id: str = Path(...),
    verification: AnalysisVerification,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Verify an analysis result by a doctor.
    """
    analysis = crud_analysis.get(db, id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    
    # Ensure analysis is completed
    if analysis.status != AnalysisStatusEnum.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed analyses can be verified",
        )
    
    # Update the analysis with doctor's verification
    verified_analysis = crud_analysis.verify_analysis(
        db,
        analysis_id=analysis_id,
        doctor_diagnosis=verification.doctor_diagnosis,
        severity=verification.severity,
        notes=verification.notes,
        verified_by_id=current_user.id
    )
    
    # Update image status
    if analysis.image:
        image = analysis.image
        image.status = ImageStatusEnum.verified
        db.add(image)
        db.commit()
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.verify_analysis,
        description=f"User verified analysis with diagnosis: {verification.doctor_diagnosis}",
        resource_type="analysis",
        resource_id=analysis.id
    )
    
    return verified_analysis
