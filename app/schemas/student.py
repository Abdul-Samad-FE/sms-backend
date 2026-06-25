from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    school_id: int
    name: str
    enroll_no: Optional[str] = None
    admission_number: str
    father_name: str
    father_contact: str
    address: str
    status: str = "Active"
    class_id: Optional[int] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    admission_date: Optional[datetime] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    school_id: Optional[int] = None
    name: Optional[str] = None
    enroll_no: Optional[str] = None
    admission_number: Optional[str] = None
    father_name: Optional[str] = None
    father_contact: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    class_id: Optional[int] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    admission_date: Optional[datetime] = None

class StudentRead(StudentBase):
    id: int
    created_at: datetime
    class_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
