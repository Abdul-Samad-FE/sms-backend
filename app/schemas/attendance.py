from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
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


class AttendanceBulkItem(BaseModel):
    """A single student's status within a bulk submission."""

    student_id: int
    status: AttendanceStatus
    remarks: Optional[str] = None


class AttendanceBulkCreate(BaseModel):
    """Mark/replace attendance for many students on one day in a single call.

    Each item is upserted on (school_id, student_id, date) — resubmitting the
    same day simply overwrites the prior status, matching the single-record
    endpoint's behaviour.
    """

    school_id: int
    date: date
    records: List[AttendanceBulkItem] = Field(min_length=1)


class AttendanceBulkResult(BaseModel):
    """Outcome of a bulk submission."""

    date: date
    processed: int
    records: List[AttendanceRead]
