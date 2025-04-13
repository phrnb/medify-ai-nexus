
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

# Base User schema
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role: Optional[str] = "doctor"
    specialty: Optional[str] = None
    profile_image: Optional[str] = None

# Schema for creating a user
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    specialty: Optional[str] = None
    profile_image: Optional[str] = None
    
    @validator('password')
    def password_min_length(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

# Schema for user in DB
class UserInDBBase(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    two_factor_enabled: bool

    class Config:
        orm_mode = True

# Schema for returning user
class User(UserInDBBase):
    pass

# Schema for DB that includes the hashed password
class UserInDB(UserInDBBase):
    hashed_password: str
