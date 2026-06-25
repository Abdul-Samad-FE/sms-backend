"""Role model — top of the RBAC hierarchy.

A Role groups a set of UBAC `Permission` rows (via `RolePermission`) and
a set of dashboard modules (via `RoleDefaultModule`). Users are assigned
exactly one role.
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    users = relationship("User", back_populates="role_obj")
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    default_modules = relationship(
        "RoleDefaultModule",
        back_populates="role",
        cascade="all, delete-orphan",
    )
