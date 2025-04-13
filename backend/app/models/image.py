
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base_class import Base

class ImageTypeEnum(str, enum.Enum):
    xray = "xray"
    mri = "mri"
    ct = "ct"
    ultrasound = "ultrasound"
    pet = "pet"
    other = "other"

class ImageStatusEnum(str, enum.Enum):
    uploaded = "uploaded"
    pending_analysis = "pending_analysis"
    analyzed = "analyzed"
    verified = "verified"
    error = "error"

class Image(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    image_type = Column(Enum(ImageTypeEnum), nullable=False)
    status = Column(Enum(ImageStatusEnum), default=ImageStatusEnum.uploaded)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    patient_id = Column(String, ForeignKey("patient.id"), nullable=False)
    uploaded_by = Column(String, ForeignKey("user.id"), nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="images")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    analyses = relationship("Analysis", back_populates="image")
