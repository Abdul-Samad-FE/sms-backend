"""Class queries."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.class_model import Class
from app.repositories.base_repository import BaseRepository


class ClassRepository(BaseRepository[Class]):
    def __init__(self, db: Session):
        super().__init__(db, Class)

    def list_by_school(self, school_id: int) -> List[Class]:
        return self.db.query(Class).filter(Class.school_id == school_id).all()

    def find_by_school_and_name(
        self, school_id: int, class_name: str, section: Optional[str]
    ) -> Optional[Class]:
        query = self.db.query(Class).filter(
            Class.school_id == school_id, Class.class_name == class_name
        )
        if section is None:
            query = query.filter(Class.section.is_(None))
        else:
            query = query.filter(Class.section == section)
        return query.first()
