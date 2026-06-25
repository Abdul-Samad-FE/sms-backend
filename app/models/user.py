"""User model — adapted for RBAC.

The legacy `role` enum (admin/teacher/staff) has been replaced with a FK to
the `roles` table. The old enum is kept as `UserRole` for backwards
compatibility with code that still imports it, but it is no longer mapped
to a column.
"""

import enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class UserRole(str, enum.Enum):
    """Legacy enum — retained for callers that still import it.

    New code should reference `Role.role_name` via the `role_obj` relationship
    instead. Seed roles match these names so existing data migrates cleanly.
    """

    admin = "admin"
    teacher = "teacher"
    staff = "staff"
    superadmin = "superadmin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=True,  # Superusers are not tied to a single school
        index=True,
    )
    role_id = Column(
        Integer,
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name = Column(String(150), nullable=False)
    username = Column(String(150), nullable=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    # Renamed from `password_hash` to match GreenX naming. Stores bcrypt hash.
    password = Column(String(255), nullable=False)

    # Opaque per-session token used by the frontend to detect session
    # invalidation across tabs (rotated on every sign-in).
    user_token = Column(String(255), nullable=True, unique=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_first_login = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Relationships ---
    school = relationship("School", back_populates="users")
    role_obj = relationship("Role", back_populates="users", foreign_keys=[role_id])
    module_accesses = relationship(
        "UserModulesAccess",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
