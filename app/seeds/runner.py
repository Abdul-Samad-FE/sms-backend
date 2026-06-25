"""Single entry point that runs every seeder in the right order.

Order matters:
  1. Permissions (referenced by roles)
  2. Dashboard modules (referenced by roles)
  3. Roles (reference both)
  4. Default superuser (references the superadmin role)
"""

import logging

from app.db.session import SessionLocal
from app.seeds.seed_default_admin import seed_default_admin
from app.seeds.seed_modules import seed_modules
from app.seeds.seed_permissions import seed_permissions
from app.seeds.seed_roles import seed_roles

logger = logging.getLogger(__name__)


def run_all_seeds() -> None:
    db = SessionLocal()
    try:
        added_perms = seed_permissions(db)
        added_modules = seed_modules(db)
        touched_roles = seed_roles(db)
        created_admin = seed_default_admin(db)
        logger.info(
            "Seeding complete — %d new permissions, %d new modules, %d roles touched, default admin %s",
            added_perms,
            added_modules,
            touched_roles,
            "created" if created_admin else "already present",
        )
    finally:
        db.close()
