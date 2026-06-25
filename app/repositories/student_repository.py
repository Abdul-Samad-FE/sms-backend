"""Student queries — Student rows joined with Class.class_name for list views."""

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.class_model import Class
from app.models.student import Student
from app.repositories.base_repository import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, db: Session):
        super().__init__(db, Student)

    def get_by_admission_number(self, admission_number: str) -> Optional[Student]:
        return (
            self.db.query(Student)
            .filter(Student.admission_number == admission_number)
            .first()
        )

    def list_with_class(
        self,
        school_id: Optional[int] = None,
        class_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tuple[Student, Optional[str]]]:
        """Return (Student, class_name) tuples — class_name is null when the
        student has no class assigned (FK is nullable).
        """
        query = self.db.query(Student, Class.class_name).outerjoin(
            Class, Student.class_id == Class.id
        )
        if school_id is not None:
            query = query.filter(Student.school_id == school_id)
        if class_id is not None:
            query = query.filter(Student.class_id == class_id)
        return query.offset(skip).limit(limit).all()

    def count_for_school(self, school_id: int) -> int:
        return self.db.query(Student).filter(Student.school_id == school_id).count()
