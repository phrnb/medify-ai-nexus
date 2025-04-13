
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AnalysisStatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class SeverityEnum(str, Enum):
    normal = "normal"
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
    critical = "critical"

# Base Analysis schema
class AnalysisBase(BaseModel):
    image_id: str
    model_version_id: Optional[str] = None

# Schema for creating an analysis
class AnalysisCreate(AnalysisBase):
    pass

# Schema for updating an analysis
class AnalysisUpdate(BaseModel):
    status: Optional[AnalysisStatusEnum] = None
    result: Optional[str] = None
    confidence: Optional[float] = None
    ai_diagnosis: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    doctor_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    raw_results: Optional[Dict[str, Any]] = None
    verified_by_id: Optional[str] = None
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Confidence must be between 0 and 1')
        return v

# Schema for analysis results from AI
class AIAnalysisResult(BaseModel):
    diagnosis: str
    confidence: float
    severity: SeverityEnum
    findings: List[str]
    details: Optional[Dict[str, Any]] = None

# Schema for doctor verification
class AnalysisVerification(BaseModel):
    doctor_diagnosis: str
    severity: SeverityEnum
    notes: Optional[str] = None
    override_ai: bool = False

# Schema for analysis in DB
class AnalysisInDBBase(AnalysisBase):
    id: str
    status: AnalysisStatusEnum
    result: Optional[str] = None
    confidence: Optional[float] = None
    ai_diagnosis: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    doctor_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    raw_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    verified_by_id: Optional[str] = None

    class Config:
        orm_mode = True

# Schema for returning analysis
class Analysis(AnalysisInDBBase):
    pass

# Schema for detailed analysis view
class AnalysisDetail(Analysis):
    image_type: Optional[str] = None
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    verified_by_name: Optional[str] = None
