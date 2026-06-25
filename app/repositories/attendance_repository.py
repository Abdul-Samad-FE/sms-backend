"""Attendance queries with optional school/student/date filters."""

from datetime import date as date_type
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.repositories.base_repository import BaseRepository


class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, db: Session):
        super().__init__(db, Attendance)

    def list_filtered(
        self,
        school_id: Optional[int] = None,
        student_id: Optional[int] = None,
        attendance_date: Optional[date_type] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Attendance]:
        query = self.db.query(Attendance)
        if school_id is not None:
            query = query.filter(Attendance.school_id == school_id)
        if student_id is not None:
            query = query.filter(Attendance.student_id == student_id)
        if attendance_date is not None:
            query = query.filter(Attendance.date == attendance_date)
        return query.offset(skip).limit(limit).all()

    def find_for_student_on_date(
        self, school_id: int, student_id: int, day: date_type
    ) -> Optional[Attendance]:
        return (
            self.db.query(Attendance)
            .filter(
                Attendance.school_id == school_id,
                Attendance.student_id == student_id,
                Attendance.date == day,
            )
            .first()
        )
