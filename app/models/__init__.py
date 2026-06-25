"""Aggregate model imports so SQLAlchemy metadata is fully populated.

Importing `app.models` (or anything from it) is enough to register every
table on `Base.metadata` — required for `create_all` and Alembic
autogenerate to see the schema.
"""

from app.models.attendance import Attendance, AttendanceStatus
from app.models.audit_log import AuditLog
from app.models.blacklisted_token import BlacklistedToken
from app.models.class_model import Class
from app.models.dashboard_module import DashboardModule
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_default_module import RoleDefaultModule
from app.models.role_permission import RolePermission
from app.models.school import School
from app.models.student import Student
from app.models.user import User, UserRole
from app.models.user_modules_access import UserModulesAccess

__all__ = [
    "Attendance",
    "AttendanceStatus",
    "AuditLog",
    "BlacklistedToken",
    "Class",
    "DashboardModule",
    "Permission",
    "Role",
    "RoleDefaultModule",
    "RolePermission",
    "School",
    "Student",
    "User",
    "UserRole",
    "UserModulesAccess",
]
