"""Dashboard endpoint — tenant-scoped overview statistics."""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.rbac import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    school_id: Optional[int] = None,
    current_user: User = Depends(require_permission("dashboard:read")),
    db: Session = Depends(get_db),
):
    """Aggregate counts, today's attendance rate, recent activity and school info.

    Non-superusers are pinned to their own school. Superadmins receive a global
    view, or a single tenant's view when ``school_id`` is supplied.
    """
    return DashboardService(db).get_stats(current_user, school_id=school_id)
