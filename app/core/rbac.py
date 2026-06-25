"""Role-based + user-based access control enforcement.

Two layers, copied from GreenX 2.0's RBAC_UBAC.md:
  * RBAC — coarse module access (sidebar visibility) via Role → DashboardModule
  * UBAC — fine action permissions via Role → Permission (e.g. "student:delete")

Superusers bypass both. Use `Depends(require_permission("student:delete"))`
on any route that needs a specific action allowed.
"""

from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user import User


def get_user_permissions(db: Session, user: User) -> List[str]:
    """Return the list of permission keys (e.g. 'student:delete') this user holds.

    Superusers conceptually hold every permission — callers should special-case
    them and skip the check rather than invoking this function.
    """
    if user.role_id is None:
        return []
    rows = (
        db.query(Permission.permission_key)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id == user.role_id)
        .all()
    )
    return [r[0] for r in rows]


def get_user_modules(db: Session, user: User) -> List[str]:
    """Return the list of dashboard module names this user can see."""
    if user.is_superuser:
        # Lazy import to avoid circular models import at module load
        from app.models.dashboard_module import DashboardModule

        return [m.modules_name for m in db.query(DashboardModule).all()]

    if user.role_id is None:
        return []

    from app.models.dashboard_module import DashboardModule
    from app.models.role_default_module import RoleDefaultModule
    from app.models.user_modules_access import UserModulesAccess

    # User-specific overrides take precedence; if absent fall back to role defaults.
    user_specific = (
        db.query(DashboardModule.modules_name)
        .join(UserModulesAccess, UserModulesAccess.module_id == DashboardModule.id)
        .filter(UserModulesAccess.user_id == user.id)
        .all()
    )
    if user_specific:
        return [r[0] for r in user_specific]

    role_defaults = (
        db.query(DashboardModule.modules_name)
        .join(RoleDefaultModule, RoleDefaultModule.module_id == DashboardModule.id)
        .filter(RoleDefaultModule.role_id == user.role_id)
        .all()
    )
    return [r[0] for r in role_defaults]


def require_permission(permission_key: str):
    """Dependency factory enforcing a single UBAC permission key.

    Usage:
        @router.delete("/students/{id}")
        def delete_student(
            id: int,
            user: User = Depends(require_permission("student:delete")),
        ): ...
    """

    def _dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.is_superuser:
            return current_user
        permissions = get_user_permissions(db, current_user)
        if permission_key not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{permission_key}' is required",
            )
        return current_user

    return _dependency


def require_any_permission(*permission_keys: str):
    """Dependency factory — passes if the user holds ANY of the given keys."""

    def _dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.is_superuser:
            return current_user
        permissions = set(get_user_permissions(db, current_user))
        if not permissions.intersection(permission_keys):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: requires one of {list(permission_keys)}",
            )
        return current_user

    return _dependency
