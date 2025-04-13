
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base_class import Base

class ReportStatusEnum(str, enum.Enum):
    draft = "draft"
    final = "final"
    amended = "amended"

class ReportFormatEnum(str, enum.Enum):
    html = "html"
    pdf = "pdf"

class Report(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(ReportStatusEnum), default=ReportStatusEnum.draft)
    file_path = Column(String, nullable=True)  # For generated PDFs
    format = Column(Enum(ReportFormatEnum), default=ReportFormatEnum.html)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    patient_id = Column(String, ForeignKey("patient.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("user.id"), nullable=False)
    analysis_id = Column(String, ForeignKey("analysis.id"), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="reports")
    doctor = relationship("User", back_populates="reports")
    analysis = relationship("Analysis", back_populates="reports")
    history = relationship("ReportHistory", back_populates="report")
