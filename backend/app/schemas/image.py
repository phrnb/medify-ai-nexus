
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ImageTypeEnum(str, Enum):
    xray = "xray"
    mri = "mri"
    ct = "ct"
    ultrasound = "ultrasound"
    pet = "pet"
    other = "other"

class ImageStatusEnum(str, Enum):
    uploaded = "uploaded"
    pending_analysis = "pending_analysis"
    analyzed = "analyzed"
    verified = "verified"
    error = "error"

# Base Image schema
class ImageBase(BaseModel):
    image_type: ImageTypeEnum
    description: Optional[str] = None
    patient_id: str

# Schema for creating an image
class ImageCreate(ImageBase):
    original_filename: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    
    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size exceeds maximum allowed size of {max_size / 1024 / 1024}MB')
        return v

# Schema for updating an image
class ImageUpdate(BaseModel):
    image_type: Optional[ImageTypeEnum] = None
    description: Optional[str] = None
    status: Optional[ImageStatusEnum] = None

# Schema for image in DB
class ImageInDBBase(ImageBase):
    id: str
    file_path: str
    thumbnail_path: Optional[str] = None
    original_filename: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    status: ImageStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    uploaded_by: str

    class Config:
        orm_mode = True

# Schema for returning image
class Image(ImageInDBBase):
    pass

# Schema for detailed image view
class ImageDetail(Image):
    patient_name: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    
    @validator('patient_name', 'uploaded_by_name', pre=True)
    def default_none(cls, v):
        return v or None
