"""Per-user override of dashboard module access.

If any rows exist for a user, they override the role defaults entirely
(not additive). Same semantics as GreenX 2.0.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class UserModulesAccess(Base):
    __tablename__ = "user_modules_access"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(
        Integer,
        ForeignKey("dashboard_modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="uq_user_module_access"),
    )

    user = relationship("User", back_populates="module_accesses")
    module = relationship("DashboardModule", back_populates="user_accesses")
