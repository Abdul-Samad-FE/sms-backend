from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from enum import Enum

class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"
    leave = "leave"

class AttendanceBase(BaseModel):
    school_id: int
    student_id: int
    date: date
    status: AttendanceStatus
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    school_id: Optional[int] = None
    student_id: Optional[int] = None
    date: Optional[date] = None
    status: Optional[AttendanceStatus] = None
    remarks: Optional[str] = None

class AttendanceRead(AttendanceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
