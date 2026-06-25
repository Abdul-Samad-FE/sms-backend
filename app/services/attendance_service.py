"""Attendance orchestration with idempotent upsert per (school, student, day)."""

from datetime import date as date_type
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.base_repository import DuplicatedError, NotFoundError
from app.schemas.attendance import (
    AttendanceBulkCreate,
    AttendanceCreate,
    AttendanceUpdate,
)
from app.services.base_service import BaseService


class AttendanceService(BaseService[Attendance]):
    def __init__(self, db: Session):
        self.db = db
        self.attendance = AttendanceRepository(db)
        super().__init__(self.attendance)

    def list_records(
        self,
        school_id: Optional[int] = None,
        student_id: Optional[int] = None,
        attendance_date: Optional[date_type] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Attendance]:
        return self.attendance.list_filtered(
            school_id=school_id,
            student_id=student_id,
            attendance_date=attendance_date,
            skip=skip,
            limit=limit,
        )

    def get_record(self, attendance_id: int) -> Attendance:
        record = self.attendance.get_by_id(attendance_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found"
            )
        return record

    def upsert(self, payload: AttendanceCreate) -> Attendance:
        """Create or replace the attendance row for (school, student, date).

        The unique constraint on (school_id, student_id, date) means a naive
        create would fail on resubmits — we treat the second submission as
        an edit instead, since that's almost always the user's intent.
        """
        existing = self.attendance.find_for_student_on_date(
            payload.school_id, payload.student_id, payload.date
        )
        if existing is not None:
            existing.status = payload.status
            existing.remarks = payload.remarks
            self.db.commit()
            self.db.refresh(existing)
            return existing
        try:
            return self.attendance.create(payload)
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    def bulk_upsert(self, payload: AttendanceBulkCreate) -> List[Attendance]:
        """Upsert a whole day's attendance for many students in one transaction."""
        items = [(r.student_id, r.status, r.remarks) for r in payload.records]
        try:
            return self.attendance.bulk_upsert(payload.school_id, payload.date, items)
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    def update_record(self, attendance_id: int, payload: AttendanceUpdate) -> Attendance:
        try:
            return self.attendance.update(attendance_id, payload)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found"
            )
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    def delete_record(self, attendance_id: int) -> None:
        try:
            self.attendance.delete_by_id(attendance_id)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found"
            )
