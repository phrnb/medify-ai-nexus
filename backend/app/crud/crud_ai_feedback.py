
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.ai_feedback import AIFeedback, FeedbackTypeEnum, FeedbackSeverityEnum, FeedbackStatusEnum
from app.schemas.ai_feedback import AIFeedbackCreate, AIFeedbackUpdate

class CRUDAIFeedback(CRUDBase[AIFeedback, AIFeedbackCreate, AIFeedbackUpdate]):
    def create_with_user(
        self, db: Session, *, obj_in: AIFeedbackCreate, user_id: str
    ) -> AIFeedback:
        """Create a new feedback with user ID"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = AIFeedback(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_filtered_feedback(
        self,
        db: Session,
        *,
        feedback_type: Optional[FeedbackTypeEnum] = None,
        severity: Optional[FeedbackSeverityEnum] = None,
        status: Optional[FeedbackStatusEnum] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIFeedback]:
        query = db.query(AIFeedback)
        
        if feedback_type:
            query = query.filter(AIFeedback.feedback_type == feedback_type)
            
        if severity:
            query = query.filter(AIFeedback.severity == severity)
            
        if status:
            query = query.filter(AIFeedback.status == status)
            
        if user_id:
            query = query.filter(AIFeedback.user_id == user_id)
            
        if start_date:
            query = query.filter(AIFeedback.created_at >= start_date)
            
        if end_date:
            query = query.filter(AIFeedback.created_at <= end_date)
            
        return query.order_by(desc(AIFeedback.created_at)).offset(skip).limit(limit).all()
        
    def count_feedback(
        self,
        db: Session,
        *,
        feedback_type: Optional[FeedbackTypeEnum] = None,
        severity: Optional[FeedbackSeverityEnum] = None,
        status: Optional[FeedbackStatusEnum] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        query = db.query(AIFeedback)
        
        if feedback_type:
            query = query.filter(AIFeedback.feedback_type == feedback_type)
            
        if severity:
            query = query.filter(AIFeedback.severity == severity)
            
        if status:
            query = query.filter(AIFeedback.status == status)
            
        if user_id:
            query = query.filter(AIFeedback.user_id == user_id)
            
        if start_date:
            query = query.filter(AIFeedback.created_at >= start_date)
            
        if end_date:
            query = query.filter(AIFeedback.created_at <= end_date)
            
        return query.count()
        
    def mark_as_reviewed(
        self,
        db: Session,
        *,
        feedback_id: str,
        reviewer_id: str,
        status: FeedbackStatusEnum = FeedbackStatusEnum.reviewed
    ) -> Optional[AIFeedback]:
        feedback = self.get(db, id=feedback_id)
        if not feedback:
            return None
            
        feedback.status = status
        feedback.reviewed_at = datetime.now()
        feedback.reviewed_by = reviewer_id
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

ai_feedback = CRUDAIFeedback(AIFeedback)
