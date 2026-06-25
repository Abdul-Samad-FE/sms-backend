"""Idempotent permission catalogue seeding.

Each entry is `(permission_key, display_name, module, action, description)`.
The `permission_key` follows the `<module>:<action>` convention enforced
by `app.core.rbac.require_permission`. Add new keys here — they will be
inserted on next startup, and existing rows are left untouched.
"""

from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.permission import Permission

PermissionDef = Tuple[str, str, str, str, str]

PERMISSIONS: List[PermissionDef] = [
    # School
    ("school:read", "View Schools", "school", "read", "View school records"),
    ("school:create", "Create School", "school", "create", "Create new schools"),
    ("school:update", "Update School", "school", "update", "Edit school records"),
    ("school:delete", "Delete School", "school", "delete", "Delete schools"),
    # User
    ("user:read", "View Users", "user", "read", "View user list and details"),
    ("user:create", "Create User", "user", "create", "Create new users"),
    ("user:update", "Update User", "user", "update", "Edit user records"),
    ("user:delete", "Delete User", "user", "delete", "Delete users"),
    # Role / RBAC admin
    ("role:read", "View Roles", "role", "read", "View roles and permissions"),
    ("role:manage", "Manage Roles", "role", "manage", "Create, update, delete roles"),
    # Class
    ("class:read", "View Classes", "class", "read", "View classes"),
    ("class:create", "Create Class", "class", "create", "Create new classes"),
    ("class:update", "Update Class", "class", "update", "Edit class records"),
    ("class:delete", "Delete Class", "class", "delete", "Delete classes"),
    # Student
    ("student:read", "View Students", "student", "read", "View student list and details"),
    ("student:create", "Create Student", "student", "create", "Enrol new students"),
    ("student:update", "Update Student", "student", "update", "Edit student records"),
    ("student:delete", "Delete Student", "student", "delete", "Remove students"),
    # Attendance
    ("attendance:read", "View Attendance", "attendance", "read", "View attendance records"),
    ("attendance:create", "Mark Attendance", "attendance", "create", "Record attendance"),
    ("attendance:update", "Update Attendance", "attendance", "update", "Edit attendance"),
    ("attendance:delete", "Delete Attendance", "attendance", "delete", "Remove attendance"),
    # Reports / dashboard
    ("dashboard:read", "View Dashboard", "dashboard", "read", "Access the main dashboard"),
    ("report:read", "View Reports", "report", "read", "View generated reports"),
    ("report:export", "Export Reports", "report", "export", "Export reports to file"),
    # Audit
    ("audit:read", "View Audit Log", "audit", "read", "Browse the audit trail"),
]


def seed_permissions(db: Session) -> int:
    """Insert any missing permission rows. Returns count of newly inserted."""
    existing_keys = {row[0] for row in db.query(Permission.permission_key).all()}
    new_count = 0
    for key, display, module, action, description in PERMISSIONS:
        if key in existing_keys:
            continue
        db.add(
            Permission(
                permission_key=key,
                display_name=display,
                module=module,
                action=action,
                description=description,
            )
        )
        new_count += 1
    if new_count:
        db.commit()
    return new_count
