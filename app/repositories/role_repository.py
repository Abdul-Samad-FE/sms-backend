"""Role + permission + module wiring queries."""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.dashboard_module import DashboardModule
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_default_module import RoleDefaultModule
from app.models.role_permission import RolePermission
from app.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(db, Role)

    def get_by_name(self, role_name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.role_name == role_name).first()

    def get_with_relations(self, role_id: int) -> Optional[Role]:
        return (
            self.db.query(Role)
            .options(
                joinedload(Role.role_permissions).joinedload(RolePermission.permission),
                joinedload(Role.default_modules).joinedload(RoleDefaultModule.module),
            )
            .filter(Role.id == role_id)
            .first()
        )

    # ---------- Permission wiring ----------
    def set_permissions(self, role_id: int, permission_ids: List[int]) -> None:
        """Replace the role's permission set with the given ids."""
        self.db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        for pid in permission_ids:
            self.db.add(RolePermission(role_id=role_id, permission_id=pid))
        self.db.commit()

    def get_permissions(self, role_id: int) -> List[Permission]:
        return (
            self.db.query(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .filter(RolePermission.role_id == role_id)
            .all()
        )

    # ---------- Module wiring ----------
    def set_modules(self, role_id: int, module_ids: List[int]) -> None:
        self.db.query(RoleDefaultModule).filter(
            RoleDefaultModule.role_id == role_id
        ).delete()
        for mid in module_ids:
            self.db.add(RoleDefaultModule(role_id=role_id, module_id=mid))
        self.db.commit()

    def get_modules(self, role_id: int) -> List[DashboardModule]:
        return (
            self.db.query(DashboardModule)
            .join(RoleDefaultModule, RoleDefaultModule.module_id == DashboardModule.id)
            .filter(RoleDefaultModule.role_id == role_id)
            .order_by(DashboardModule.sort_order)
            .all()
        )
