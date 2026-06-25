"""AuditLog queries — read-only listing."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(db, AuditLog)

    def list_filtered(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        query = self.db.query(AuditLog)
        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)
        if action is not None:
            query = query.filter(AuditLog.action == action)
        if entity is not None:
            query = query.filter(AuditLog.entity == entity)
        return (
            query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        )
