
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.notification import Notification, NotificationStatusEnum, NotificationTypeEnum
from app.schemas.notification import NotificationCreate, NotificationUpdate

class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    def get_notifications_by_user(
        self,
        db: Session,
        *,
        user_id: str,
        status: Optional[NotificationStatusEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if status:
            query = query.filter(Notification.status == status)
            
        return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
        
    def count_unread_notifications(
        self,
        db: Session,
        *,
        user_id: str
    ) -> int:
        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.status == NotificationStatusEnum.unread
            )
            .count()
        )
        
    def mark_as_read(
        self,
        db: Session,
        *,
        notification_id: str
    ) -> Notification:
        notification = self.get(db, id=notification_id)
        if not notification:
            return None
            
        notification.status = NotificationStatusEnum.read
        notification.read_at = datetime.now()
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
        
    def mark_all_as_read(
        self,
        db: Session,
        *,
        user_id: str
    ) -> int:
        unread_notifications = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.status == NotificationStatusEnum.unread
            )
            .all()
        )
        
        count = 0
        for notification in unread_notifications:
            notification.status = NotificationStatusEnum.read
            notification.read_at = datetime.now()
            count += 1
            
        db.commit()
        return count

notification = CRUDNotification(Notification)
