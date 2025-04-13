
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Text, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base_class import Base

class AnalysisStatusEnum(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class SeverityEnum(str, enum.Enum):
    normal = "normal"
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
    critical = "critical"

class Analysis(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(AnalysisStatusEnum), default=AnalysisStatusEnum.pending)
    result = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    ai_diagnosis = Column(String, nullable=True)
    severity = Column(Enum(SeverityEnum), nullable=True)
    doctor_diagnosis = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    raw_results = Column(JSON, nullable=True)  # Store full AI output
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    image_id = Column(String, ForeignKey("image.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_version.id"), nullable=True)
    verified_by_id = Column(String, ForeignKey("user.id"), nullable=True)
    
    # Relationships
    image = relationship("Image", back_populates="analyses")
    model_version = relationship("ModelVersion")
    verified_by = relationship("User", back_populates="analyses")
    reports = relationship("Report", back_populates="analysis")
