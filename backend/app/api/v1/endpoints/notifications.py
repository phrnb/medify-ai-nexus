
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Path
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_verified_user, log_user_activity
from app.crud.crud_notification import notification as crud_notification
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.models.notification import NotificationStatusEnum
from app.schemas.notification import Notification, NotificationUpdate

router = APIRouter()

@router.get("", response_model=List[Notification])
def read_notifications(
    request: Request,
    db: Session = Depends(get_db),
    status: Optional[NotificationStatusEnum] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Retrieve notifications for the current user.
    """
    notifications = crud_notification.get_notifications_by_user(
        db, user_id=current_user.id, status=status, skip=skip, limit=limit
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed notifications",
        resource_type="notification"
    )
    
    return notifications

@router.get("/unread-count", response_model=dict)
def count_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Count unread notifications for the current user.
    """
    count = crud_notification.count_unread_notifications(db, user_id=current_user.id)
    
    return {"count": count}

@router.put("/{notification_id}/read", response_model=Notification)
def mark_notification_as_read(
    request: Request,
    *,
    db: Session = Depends(get_db),
    notification_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Mark a notification as read.
    """
    notification = crud_notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    
    # Ensure notification belongs to current user
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification",
        )
    
    # Already read, no need to update
    if notification.status != NotificationStatusEnum.unread:
        return notification
    
    # Mark as read
    notification = crud_notification.mark_as_read(db, notification_id=notification_id)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User marked notification as read",
        resource_type="notification",
        resource_id=notification.id
    )
    
    return notification

@router.put("/mark-all-read", response_model=dict)
def mark_all_notifications_as_read(
    request: Request,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Mark all notifications as read.
    """
    count = crud_notification.mark_all_as_read(db, user_id=current_user.id)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User marked all notifications as read",
        resource_type="notification"
    )
    
    return {"marked_as_read": count}
