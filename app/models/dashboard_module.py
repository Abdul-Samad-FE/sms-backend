"""DashboardModule — a frontend section gated by RBAC.

Each row corresponds to a sidebar entry (Dashboard, Students, Classes,
Attendance, Reports, Admin). Roles are linked via `RoleDefaultModule`;
per-user overrides go in `UserModulesAccess`.
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class DashboardModule(Base):
    __tablename__ = "dashboard_modules"

    id = Column(Integer, primary_key=True, index=True)
    modules_name = Column(String(150), unique=True, nullable=False, index=True)
    display_name = Column(String(150), nullable=False)
    icon = Column(String(100), nullable=True)
    route = Column(String(150), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user_accesses = relationship(
        "UserModulesAccess",
        back_populates="module",
        cascade="all, delete-orphan",
    )
    role_defaults = relationship(
        "RoleDefaultModule",
        back_populates="module",
        cascade="all, delete-orphan",
    )
