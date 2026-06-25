"""Permission model — atomic UBAC unit.

`permission_key` follows the convention `<module>:<action>`, e.g.
`student:create`, `student:delete`, `attendance:read`. Seed data populates
this table at startup; new keys can be added by editing
`app/seeds/seed_permissions.py`.
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    permission_key = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    module = Column(String(100), nullable=False, index=True)
    sub_module = Column(String(100), nullable=True)
    action = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )
