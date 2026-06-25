"""Audit log read service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuditLogRepository(db)

    def list_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        return self.repository.list_filtered(
            user_id=user_id, action=action, entity=entity, skip=skip, limit=limit
        )
