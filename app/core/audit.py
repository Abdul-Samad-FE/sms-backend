"""Audit logging helper.

Wraps inserts to the audit_log table so endpoints can record who did what,
mirroring GreenX 2.0's `core/audit.py`. Failures are swallowed — auditing
must never break the request.
"""

import json
import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    *,
    user_id: Optional[int],
    action: str,
    entity: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Best-effort audit insert. Commits its own row so the calling
    transaction's success/failure does not affect the trail.
    """
    try:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=json.dumps(details, default=str) if details else None,
            ip_address=ip_address,
        )
        db.add(entry)
        db.commit()
    except Exception as exc:  # pragma: no cover — never raise from the audit path
        db.rollback()
        logger.warning("Failed to write audit log entry: %s", exc)
