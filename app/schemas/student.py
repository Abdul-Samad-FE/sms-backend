from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    school_id: int
    name: str
    enroll_no: str
    father_name: str
    father_contact: str
    address: str

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    school_id: Optional[int] = None
    name: Optional[str] = None
    enroll_no: Optional[str] = None
    father_name: Optional[str] = None
    father_contact: Optional[str] = None
    address: Optional[str] = None

class StudentRead(StudentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
