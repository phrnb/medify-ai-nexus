
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ActivityTypeEnum(str, Enum):
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

# Base ActivityLog schema
class ActivityLogBase(BaseModel):
    user_id: str
    activity_type: ActivityTypeEnum
    description: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

# Schema for creating an activity log
class ActivityLogCreate(ActivityLogBase):
    pass

# Schema for activity log in DB
class ActivityLogInDBBase(ActivityLogBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

# Schema for returning activity log
class ActivityLog(ActivityLogInDBBase):
    user_name: Optional[str] = None  # Populated when joining with user
