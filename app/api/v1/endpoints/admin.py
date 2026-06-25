"""Admin-only endpoints — roles, permissions, modules, audit logs.

These mirror GreenX 2.0's `app/api/v2/endpoints/admin.py` and exist
primarily to let the frontend admin panel manage the RBAC catalogue
without raw SQL.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.dependencies import get_current_admin_user, get_current_super_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit import AuditLogRead
from app.schemas.role import (
    DashboardModuleRead,
    PermissionRead,
    RoleCreate,
    RoleRead,
    RoleUpdate,
)
from app.services.audit_service import AuditService
from app.services.role_service import RoleService

router = APIRouter(prefix="/admin", tags=["Admin"])


# ---------- Roles ----------
def _serialize_role(role) -> RoleRead:
    dto = RoleRead.model_validate(role)
    dto.permissions = [
        PermissionRead.model_validate(rp.permission) for rp in role.role_permissions
    ]
    dto.modules = [
        DashboardModuleRead.model_validate(rdm.module) for rdm in role.default_modules
    ]
    return dto


@router.get("/roles", response_model=List[RoleRead])
def list_roles(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    service = RoleService(db)
    roles = service.list_roles()
    return [_serialize_role(service.get_role(r.id)) for r in roles]


@router.get("/roles/{role_id}", response_model=RoleRead)
def get_role(
    role_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return _serialize_role(RoleService(db).get_role(role_id))


@router.post("/roles", response_model=RoleRead, status_code=201)
def create_role(
    payload: RoleCreate,
    request: Request,
    current_user: User = Depends(get_current_super_user),
    db: Session = Depends(get_db),
):
    role = RoleService(db).create_role(payload)
    log_action(
        db,
        user_id=current_user.id,
        action="create_role",
        entity="role",
        entity_id=role.id,
        ip_address=request.client.host if request.client else None,
    )
    return _serialize_role(role)


@router.put("/roles/{role_id}", response_model=RoleRead)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    request: Request,
    current_user: User = Depends(get_current_super_user),
    db: Session = Depends(get_db),
):
    role = RoleService(db).update_role(role_id, payload)
    log_action(
        db,
        user_id=current_user.id,
        action="update_role",
        entity="role",
        entity_id=role.id,
        ip_address=request.client.host if request.client else None,
    )
    return _serialize_role(role)


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    request: Request,
    current_user: User = Depends(get_current_super_user),
    db: Session = Depends(get_db),
):
    RoleService(db).delete_role(role_id)
    log_action(
        db,
        user_id=current_user.id,
        action="delete_role",
        entity="role",
        entity_id=role_id,
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "Role deleted successfully"}


# ---------- Permissions (read-only catalog) ----------
@router.get("/permissions", response_model=List[PermissionRead])
def list_permissions(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    from app.repositories.permission_repository import PermissionRepository

    return PermissionRepository(db).list_all(skip=0, limit=1000)


# ---------- Dashboard modules ----------
@router.get("/modules", response_model=List[DashboardModuleRead])
def list_modules(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    from app.repositories.dashboard_module_repository import DashboardModuleRepository

    return DashboardModuleRepository(db).list_ordered()


# ---------- Audit logs ----------
@router.get("/audit-logs", response_model=List[AuditLogRead])
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return AuditService(db).list_logs(
        user_id=user_id, action=action, entity=entity, skip=skip, limit=limit
    )
