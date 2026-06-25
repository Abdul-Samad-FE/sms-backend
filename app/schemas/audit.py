"""AuditLog DTOs (read-only — there is no create/update path)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    entity: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
