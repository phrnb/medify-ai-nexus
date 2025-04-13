
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

# Base Patient schema
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: GenderEnum
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    medical_record_number: str
    is_active: bool = True
    notes: Optional[str] = None

# Schema for creating a patient
class PatientCreate(PatientBase):
    @validator('date_of_birth')
    def validate_birthdate(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v

# Schema for updating a patient
class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    
    @validator('date_of_birth')
    def validate_birthdate(cls, v):
        if v is not None and v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v

# Schema for patient in DB
class PatientInDBBase(PatientBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Schema for returning patient
class Patient(PatientInDBBase):
    pass

# Schema for patient with additional info (for detailed views)
class PatientDetail(Patient):
    age: int

    @validator('age', pre=True, always=True)
    def calculate_age(cls, v, values):
        if 'date_of_birth' in values:
            today = date.today()
            born = values['date_of_birth']
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            return age
        return 0
