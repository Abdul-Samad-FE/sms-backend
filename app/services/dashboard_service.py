"""Dashboard orchestration — resolves tenancy scope and assembles stats.

Mirrors the scoping rule used across the API: non-superusers are pinned to
their own ``school_id``; superadmins see a global view unless they explicitly
request a single school via ``school_id``.
"""

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.school import School
from app.models.user import User
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardSchoolInfo,
    DashboardStats,
    RecentActivityItem,
)

RECENT_ACTIVITY_LIMIT = 10


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = DashboardRepository(db)

    def _resolve_scope(
        self, current_user: User, requested_school_id: Optional[int]
    ) -> Optional[int]:
        """Force tenancy: only superusers may widen/redirect the scope."""
        if current_user.is_superuser:
            return requested_school_id
        return current_user.school_id

    def _school_info(self, school_id: Optional[int]) -> Optional[DashboardSchoolInfo]:
        if school_id is None:
            return None
        school = self.db.query(School).filter(School.id == school_id).first()
        return DashboardSchoolInfo.model_validate(school) if school else None

    def get_stats(
        self, current_user: User, school_id: Optional[int] = None
    ) -> DashboardStats:
        scope = self._resolve_scope(current_user, school_id)

        present, marked = self.repository.attendance_for_day(date.today(), scope)
        percentage = round((present / marked) * 100, 1) if marked else 0.0

        activity_rows = self.repository.recent_activity(
            school_id=scope, limit=RECENT_ACTIVITY_LIMIT
        )
        recent_activity = [
            RecentActivityItem(
                id=log.id,
                action=log.action,
                entity=log.entity,
                entity_id=log.entity_id,
                user_id=log.user_id,
                user_name=user_name,
                ip_address=log.ip_address,
                created_at=log.created_at,
            )
            for log, user_name in activity_rows
        ]

        return DashboardStats(
            total_students=self.repository.count_students(scope),
            total_teachers=self.repository.count_teachers(scope),
            total_classes=self.repository.count_classes(scope),
            today_present=present,
            today_marked=marked,
            today_attendance_percentage=percentage,
            recent_activity=recent_activity,
            school=self._school_info(scope),
            generated_at=datetime.now(timezone.utc),
        )
