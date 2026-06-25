"""DashboardModule lookups."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.dashboard_module import DashboardModule
from app.repositories.base_repository import BaseRepository


class DashboardModuleRepository(BaseRepository[DashboardModule]):
    def __init__(self, db: Session):
        super().__init__(db, DashboardModule)

    def get_by_name(self, modules_name: str) -> Optional[DashboardModule]:
        return (
            self.db.query(DashboardModule)
            .filter(DashboardModule.modules_name == modules_name)
            .first()
        )

    def list_ordered(self) -> List[DashboardModule]:
        return self.db.query(DashboardModule).order_by(DashboardModule.sort_order).all()
