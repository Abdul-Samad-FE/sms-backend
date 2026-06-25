"""Seed default roles with sensible permission + module assignments.

Each role is created if absent and then re-synced to the canonical
permission/module sets defined here. Custom roles created via the admin
panel are ignored — only the names below are touched.
"""

from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.dashboard_module import DashboardModule
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_default_module import RoleDefaultModule
from app.models.role_permission import RolePermission

# --- Permission templates ---
# A role's permission list is taken from these tuples; "*" expands to all keys.
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "superadmin": ["*"],
    "admin": [
        "school:read",
        "user:read",
        "user:create",
        "user:update",
        "user:delete",
        "role:read",
        "class:read",
        "class:create",
        "class:update",
        "class:delete",
        "student:read",
        "student:create",
        "student:update",
        "student:delete",
        "attendance:read",
        "attendance:create",
        "attendance:update",
        "attendance:delete",
        "dashboard:read",
        "report:read",
        "report:export",
        "audit:read",
    ],
    "teacher": [
        "dashboard:read",
        "class:read",
        "student:read",
        "attendance:read",
        "attendance:create",
        "attendance:update",
        "report:read",
    ],
    "staff": [
        "dashboard:read",
        "student:read",
        "class:read",
        "attendance:read",
    ],
}

ROLE_MODULES: Dict[str, List[str]] = {
    "superadmin": [
        "dashboard",
        "schools",
        "students",
        "classes",
        "attendance",
        "reports",
        "admin",
    ],
    "admin": [
        "dashboard",
        "students",
        "classes",
        "attendance",
        "reports",
        "admin",
    ],
    "teacher": ["dashboard", "students", "classes", "attendance", "reports"],
    "staff": ["dashboard", "students", "classes", "attendance"],
}

ROLE_DESCRIPTIONS: Dict[str, str] = {
    "superadmin": "Cross-tenant administrator with full system access",
    "admin": "School administrator — manages users, classes, students within their school",
    "teacher": "Classroom teacher — marks attendance, views own students",
    "staff": "Read-only operational staff",
}


def _sync_permissions(db: Session, role: Role, keys: List[str]) -> None:
    if keys == ["*"]:
        permissions = db.query(Permission).all()
    else:
        permissions = db.query(Permission).filter(Permission.permission_key.in_(keys)).all()
    db.query(RolePermission).filter(RolePermission.role_id == role.id).delete()
    for perm in permissions:
        db.add(RolePermission(role_id=role.id, permission_id=perm.id))


def _sync_modules(db: Session, role: Role, names: List[str]) -> None:
    modules = db.query(DashboardModule).filter(DashboardModule.modules_name.in_(names)).all()
    db.query(RoleDefaultModule).filter(RoleDefaultModule.role_id == role.id).delete()
    for mod in modules:
        db.add(RoleDefaultModule(role_id=role.id, module_id=mod.id))


def seed_roles(db: Session) -> int:
    """Upsert the canonical roles and re-sync their permission/module sets."""
    touched = 0
    for name, perm_keys in ROLE_PERMISSIONS.items():
        role = db.query(Role).filter(Role.role_name == name).first()
        if role is None:
            role = Role(role_name=name, description=ROLE_DESCRIPTIONS.get(name))
            db.add(role)
            db.flush()  # populate role.id
            touched += 1
        _sync_permissions(db, role, perm_keys)
        _sync_modules(db, role, ROLE_MODULES.get(name, []))
    db.commit()
    return touched
