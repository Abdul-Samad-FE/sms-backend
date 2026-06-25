"""Bootstrap the default superuser if no superuser exists yet.

Reads credentials from settings (overridable via env vars):
  DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_NAME
"""

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User

logger = logging.getLogger(__name__)


def seed_default_admin(db: Session) -> bool:
    """Create the default superuser if none exists. Returns True if created."""
    existing = db.query(User).filter(User.is_superuser.is_(True)).first()
    if existing is not None:
        return False

    superadmin_role = db.query(Role).filter(Role.role_name == "superadmin").first()
    user = User(
        name=settings.DEFAULT_ADMIN_NAME,
        email=settings.DEFAULT_ADMIN_EMAIL,
        password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
        is_active=True,
        is_superuser=True,
        is_first_login=True,
        role_id=superadmin_role.id if superadmin_role else None,
        school_id=None,
    )
    db.add(user)
    db.commit()
    logger.warning(
        "Created default superuser %s — change the password on first login.",
        settings.DEFAULT_ADMIN_EMAIL,
    )
    return True
