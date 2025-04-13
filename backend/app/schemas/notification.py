
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class NotificationTypeEnum(str, Enum):
    analysis_complete = "analysis_complete"
    analysis_error = "analysis_error"
    report_ready = "report_ready"
    system_update = "system_update"
    model_update = "model_update"
    critical_finding = "critical_finding"

class NotificationStatusEnum(str, Enum):
    unread = "unread"
    read = "read"
    archived = "archived"

# Base Notification schema
class NotificationBase(BaseModel):
    user_id: str
    type: NotificationTypeEnum
    title: str
    message: str
    link: Optional[str] = None

# Schema for creating a notification
class NotificationCreate(NotificationBase):
    pass

# Schema for updating a notification
class NotificationUpdate(BaseModel):
    status: NotificationStatusEnum

# Schema for notification in DB
class NotificationInDBBase(NotificationBase):
    id: str
    status: NotificationStatusEnum
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Schema for returning notification
class Notification(NotificationInDBBase):
    pass
