"""School queries."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.school import School
from app.repositories.base_repository import BaseRepository


class SchoolRepository(BaseRepository[School]):
    def __init__(self, db: Session):
        super().__init__(db, School)

    def get_by_emis_code(self, emis_code: str) -> Optional[School]:
        return self.db.query(School).filter(School.emis_code == emis_code).first()
