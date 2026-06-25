"""Aggregation queries backing the overview dashboard.

Every method accepts an optional ``school_id``: when provided the query is
scoped to that tenant; when ``None`` it spans all schools (superadmin's
global view). Keeping these aggregates here — rather than spread across the
per-entity repositories — gives the dashboard a single, cohesive data source.
"""

from datetime import date as date_type
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.audit_log import AuditLog
from app.models.class_model import Class
from app.models.role import Role
from app.models.student import Student
from app.models.user import User


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_students(self, school_id: Optional[int] = None) -> int:
        query = self.db.query(func.count(Student.id))
        if school_id is not None:
            query = query.filter(Student.school_id == school_id)
        return query.scalar() or 0

    def count_teachers(self, school_id: Optional[int] = None) -> int:
        """Teachers are users whose assigned role is named ``teacher``."""
        query = (
            self.db.query(func.count(User.id))
            .join(Role, User.role_id == Role.id)
            .filter(Role.role_name == "teacher")
        )
        if school_id is not None:
            query = query.filter(User.school_id == school_id)
        return query.scalar() or 0

    def count_classes(self, school_id: Optional[int] = None) -> int:
        query = self.db.query(func.count(Class.id))
        if school_id is not None:
            query = query.filter(Class.school_id == school_id)
        return query.scalar() or 0

    def attendance_for_day(
        self, day: date_type, school_id: Optional[int] = None
    ) -> Tuple[int, int]:
        """Return ``(present_count, marked_count)`` for the given day."""
        marked_query = self.db.query(func.count(Attendance.id)).filter(
            Attendance.date == day
        )
        present_query = self.db.query(func.count(Attendance.id)).filter(
            Attendance.date == day,
            Attendance.status == AttendanceStatus.present,
        )
        if school_id is not None:
            marked_query = marked_query.filter(Attendance.school_id == school_id)
            present_query = present_query.filter(Attendance.school_id == school_id)
        return (present_query.scalar() or 0, marked_query.scalar() or 0)

    def recent_activity(
        self, school_id: Optional[int] = None, limit: int = 10
    ) -> List[Tuple[AuditLog, Optional[str]]]:
        """Return ``(AuditLog, user_name)`` tuples, newest first.

        Scoped to a tenant by filtering the acting user's ``school_id``;
        unscoped (global) for superadmins.
        """
        query = self.db.query(AuditLog, User.name).outerjoin(
            User, AuditLog.user_id == User.id
        )
        if school_id is not None:
            query = query.filter(User.school_id == school_id)
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
