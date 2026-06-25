"""Dashboard DTOs — aggregate stats for the main overview screen.

Read-only response models consumed by `GET /dashboard/stats`. All values are
tenant-scoped at the service layer; superadmins receive a cross-tenant
(global) view when no `school_id` is supplied.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DashboardSchoolInfo(BaseModel):
    """Identity card for the tenant the stats belong to.

    Null on the superadmin's global view (stats span every school).
    """

    id: int
    name: str
    emis_code: str
    uc_name: str
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RecentActivityItem(BaseModel):
    """A single audit-trail entry surfaced on the dashboard feed."""

    id: int
    action: str
    entity: Optional[str] = None
    entity_id: Optional[int] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    """Top-level payload for the overview dashboard.

    `today_attendance_percentage` is the share of *marked* attendance records
    for the current day with status ``present`` (0 when nothing is marked yet).
    `today_present` / `today_marked` are exposed so the frontend can show the
    raw counts alongside the percentage.
    """

    total_students: int
    total_teachers: int
    total_classes: int

    today_present: int
    today_marked: int
    today_attendance_percentage: float

    recent_activity: List[RecentActivityItem]
    school: Optional[DashboardSchoolInfo] = None
    generated_at: datetime
