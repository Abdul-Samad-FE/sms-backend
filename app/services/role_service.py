"""Role + permission + module-assignment orchestration."""

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.role import Role
from app.repositories.base_repository import DuplicatedError
from app.repositories.dashboard_module_repository import DashboardModuleRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate
from app.services.base_service import BaseService


class RoleService(BaseService[Role]):
    def __init__(self, db: Session):
        self.db = db
        self.roles = RoleRepository(db)
        self.permissions = PermissionRepository(db)
        self.modules = DashboardModuleRepository(db)
        super().__init__(self.roles)

    def list_roles(self) -> List[Role]:
        return self.roles.list_all(skip=0, limit=1000)

    def get_role(self, role_id: int) -> Role:
        role = self.roles.get_with_relations(role_id)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        return role

    def create_role(self, payload: RoleCreate) -> Role:
        if self.roles.get_by_name(payload.role_name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Role name already exists"
            )
        try:
            role = Role(role_name=payload.role_name, description=payload.description)
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

        if payload.permission_ids:
            self.roles.set_permissions(role.id, payload.permission_ids)
        if payload.module_ids:
            self.roles.set_modules(role.id, payload.module_ids)
        return self.get_role(role.id)

    def update_role(self, role_id: int, payload: RoleUpdate) -> Role:
        role = self.get_role(role_id)
        if payload.role_name is not None:
            role.role_name = payload.role_name
        if payload.description is not None:
            role.description = payload.description
        self.db.commit()

        if payload.permission_ids is not None:
            self.roles.set_permissions(role.id, payload.permission_ids)
        if payload.module_ids is not None:
            self.roles.set_modules(role.id, payload.module_ids)
        return self.get_role(role.id)

    def delete_role(self, role_id: int) -> None:
        role = self.get_role(role_id)
        self.db.delete(role)
        self.db.commit()
