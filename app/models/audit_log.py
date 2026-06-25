"""AuditLog — immutable trail of user actions.

Populated by `app.core.audit.log_action`. Designed to be append-only;
there is no service-level update or delete path.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(100), nullable=False, index=True)
    entity = Column(String(100), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    details = Column(Text, nullable=True)  # JSON-encoded
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="audit_logs")
