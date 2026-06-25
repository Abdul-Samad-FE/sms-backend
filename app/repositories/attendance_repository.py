"""Attendance queries with optional school/student/date filters."""

from datetime import date as date_type
from typing import List, Optional, Sequence, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.repositories.base_repository import BaseRepository, DuplicatedError


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

    def bulk_upsert(
        self,
        school_id: int,
        day: date_type,
        items: Sequence[Tuple[int, AttendanceStatus, Optional[str]]],
    ) -> List[Attendance]:
        """Create-or-update many (student, day) rows, committing exactly once.

        `items` is a sequence of ``(student_id, status, remarks)``. Existing
        rows for the day are updated in place; the rest are inserted. A single
        commit keeps the whole submission atomic.
        """
        results: List[Attendance] = []
        for student_id, status_value, remarks in items:
            existing = self.find_for_student_on_date(school_id, student_id, day)
            if existing is not None:
                existing.status = status_value
                existing.remarks = remarks
                results.append(existing)
            else:
                row = Attendance(
                    school_id=school_id,
                    student_id=student_id,
                    date=day,
                    status=status_value,
                    remarks=remarks,
                )
                self.db.add(row)
                results.append(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicatedError(str(exc.orig)) from exc
        for row in results:
            self.db.refresh(row)
        return results
