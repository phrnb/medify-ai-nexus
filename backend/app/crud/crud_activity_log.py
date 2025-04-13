
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.activity_log import ActivityLog, ActivityTypeEnum
from app.schemas.activity_log import ActivityLogCreate

class CRUDActivityLog(CRUDBase[ActivityLog, ActivityLogCreate, None]):
    def get_user_activities(
        self,
        db: Session,
        *,
        user_id: str,
        activity_type: Optional[ActivityTypeEnum] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ActivityLog]:
        query = db.query(ActivityLog).filter(ActivityLog.user_id == user_id)
        
        if activity_type:
            query = query.filter(ActivityLog.activity_type == activity_type)
            
        if resource_type:
            query = query.filter(ActivityLog.resource_type == resource_type)
            
        if resource_id:
            query = query.filter(ActivityLog.resource_id == resource_id)
            
        if start_date:
            query = query.filter(ActivityLog.created_at >= start_date)
            
        if end_date:
            query = query.filter(ActivityLog.created_at <= end_date)
            
        return query.order_by(desc(ActivityLog.created_at)).offset(skip).limit(limit).all()
        
    def get_resource_activities(
        self,
        db: Session,
        *,
        resource_type: str,
        resource_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ActivityLog]:
        return (
            db.query(ActivityLog)
            .filter(
                ActivityLog.resource_type == resource_type,
                ActivityLog.resource_id == resource_id
            )
            .order_by(desc(ActivityLog.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def log_activity(
        self,
        db: Session,
        *,
        user_id: str,
        activity_type: ActivityTypeEnum,
        description: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> ActivityLog:
        activity_log = ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_data=additional_data
        )
        
        db.add(activity_log)
        db.commit()
        db.refresh(activity_log)
        return activity_log

activity_log = CRUDActivityLog(ActivityLog)
