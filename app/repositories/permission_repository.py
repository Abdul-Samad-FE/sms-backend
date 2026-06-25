"""Permission lookups."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db: Session):
        super().__init__(db, Permission)

    def get_by_key(self, permission_key: str) -> Optional[Permission]:
        return (
            self.db.query(Permission)
            .filter(Permission.permission_key == permission_key)
            .first()
        )

    def list_by_module(self, module: str) -> List[Permission]:
        return self.db.query(Permission).filter(Permission.module == module).all()
