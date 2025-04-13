
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class FeedbackTypeEnum(str, Enum):
    accuracy = "accuracy"
    error_report = "error_report"
    suggestion = "suggestion"
    general = "general"

class FeedbackSeverityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

# Base AI Feedback schema
class AIFeedbackBase(BaseModel):
    analysis_id: Optional[str] = None  # Optional because feedback might be general
    feedback_type: FeedbackTypeEnum
    content: str
    severity: Optional[FeedbackSeverityEnum] = FeedbackSeverityEnum.medium
    additional_details: Optional[Dict[str, Any]] = None

# Schema for creating AI feedback
class AIFeedbackCreate(AIFeedbackBase):
    pass

# Schema for updating AI feedback
class AIFeedbackUpdate(BaseModel):
    content: Optional[str] = None
    severity: Optional[FeedbackSeverityEnum] = None
    status: Optional[str] = None
    additional_details: Optional[Dict[str, Any]] = None

# Schema for AI feedback in DB
class AIFeedbackInDBBase(AIFeedbackBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str = "pending"  # pending, reviewed, implemented, closed
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    class Config:
        orm_mode = True

# Schema for returning AI feedback
class AIFeedback(AIFeedbackInDBBase):
    pass

# Schema for detailed AI feedback view
class AIFeedbackDetail(AIFeedback):
    username: Optional[str] = None
    analysis_details: Optional[Dict[str, Any]] = None
    reviewed_by_name: Optional[str] = None
