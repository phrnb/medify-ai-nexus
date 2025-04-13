
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base_class import Base

class NotificationTypeEnum(str, enum.Enum):
    analysis_complete = "analysis_complete"
    analysis_error = "analysis_error"
    report_ready = "report_ready"
    system_update = "system_update"
    model_update = "model_update"
    critical_finding = "critical_finding"

class NotificationStatusEnum(str, enum.Enum):
    unread = "unread"
    read = "read"
    archived = "archived"

class Notification(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    type = Column(Enum(NotificationTypeEnum), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String, nullable=True)  # Link to related resource
    status = Column(Enum(NotificationStatusEnum), default=NotificationStatusEnum.unread)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
