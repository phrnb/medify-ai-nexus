
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class ReportStatusEnum(str, Enum):
    draft = "draft"
    final = "final"
    amended = "amended"

class ReportFormatEnum(str, Enum):
    html = "html"
    pdf = "pdf"

# Base Report schema
class ReportBase(BaseModel):
    title: str
    content: str
    patient_id: str
    doctor_id: str
    analysis_id: Optional[str] = None

# Schema for creating a report
class ReportCreate(ReportBase):
    status: ReportStatusEnum = ReportStatusEnum.draft
    format: ReportFormatEnum = ReportFormatEnum.html

# Schema for updating a report
class ReportUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ReportStatusEnum] = None
    format: Optional[ReportFormatEnum] = None
    
# Schema for finalizing a report
class ReportFinalize(BaseModel):
    notes: Optional[str] = None

# Schema for report history entry
class ReportHistoryEntry(BaseModel):
    user_id: str
    changes: Dict
    previous_content: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

# Schema for report in DB
class ReportInDBBase(ReportBase):
    id: str
    status: ReportStatusEnum
    file_path: Optional[str] = None
    format: ReportFormatEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    finalized_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Schema for returning report
class Report(ReportInDBBase):
    pass

# Schema for detailed report view
class ReportDetail(Report):
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    history: List[ReportHistoryEntry] = []
