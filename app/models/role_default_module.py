"""Default modules granted to a Role (sidebar template)."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class RoleDefaultModule(Base):
    __tablename__ = "role_default_modules"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(
        Integer,
        ForeignKey("dashboard_modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("role_id", "module_id", name="uq_role_default_module"),
    )

    role = relationship("Role", back_populates="default_modules")
    module = relationship("DashboardModule", back_populates="role_defaults")
