
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base_class import Base

class FeedbackTypeEnum(str, enum.Enum):
    accuracy = "accuracy"
    error_report = "error_report"
    suggestion = "suggestion"
    general = "general"

class FeedbackSeverityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class FeedbackStatusEnum(str, enum.Enum):
    pending = "pending"
    reviewed = "reviewed"
    implemented = "implemented"
    closed = "closed"

class AIFeedback(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    analysis_id = Column(String, ForeignKey("analysis.id"), nullable=True)
    feedback_type = Column(Enum(FeedbackTypeEnum), nullable=False)
    content = Column(Text, nullable=False)
    severity = Column(Enum(FeedbackSeverityEnum), default=FeedbackSeverityEnum.medium)
    status = Column(Enum(FeedbackStatusEnum), default=FeedbackStatusEnum.pending)
    additional_details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(String, ForeignKey("user.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    analysis = relationship("Analysis")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
