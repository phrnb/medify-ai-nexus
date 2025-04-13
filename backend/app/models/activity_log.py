
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base_class import Base

class ActivityTypeEnum(str, enum.Enum):
    login = "login"
    logout = "logout"
    create = "create"
    update = "update"
    delete = "delete"
    view = "view"
    download = "download"
    analyze = "analyze"
    generate_report = "generate_report"
    verify_analysis = "verify_analysis"

class ActivityLog(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    activity_type = Column(Enum(ActivityTypeEnum), nullable=False)
    resource_type = Column(String, nullable=True)  # "patient", "image", "report", etc.
    resource_id = Column(String, nullable=True)  # ID of the affected resource
    description = Column(Text, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)  # Any relevant metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="activities")
