"""Student orchestration with school-scoped queries + class_name join."""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.base_repository import DuplicatedError, NotFoundError
from app.repositories.student_repository import StudentRepository
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate
from app.services.base_service import BaseService


class StudentService(BaseService[Student]):
    def __init__(self, db: Session):
        self.db = db
        self.students = StudentRepository(db)
        super().__init__(self.students)

    def list_students(
        self,
        school_id: Optional[int] = None,
        class_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StudentRead]:
        rows = self.students.list_with_class(
            school_id=school_id, class_id=class_id, skip=skip, limit=limit
        )
        results: List[StudentRead] = []
        for student, class_name in rows:
            dto = StudentRead.model_validate(student)
            dto.class_name = class_name
            results.append(dto)
        return results

    def get_student(self, student_id: int, school_id: Optional[int] = None) -> Student:
        student = self.students.get_by_id(student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        if school_id is not None and student.school_id != school_id:
            # Tenancy boundary — pretend it doesn't exist for cross-school callers.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        return student

    def create_student(self, payload: StudentCreate) -> Student:
        try:
            return self.students.create(payload)
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    def update_student(
        self, student_id: int, payload: StudentUpdate, school_id: Optional[int] = None
    ) -> Student:
        # Tenancy check first
        self.get_student(student_id, school_id=school_id)
        try:
            return self.students.update(student_id, payload)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    def delete_student(self, student_id: int, school_id: Optional[int] = None) -> None:
        self.get_student(student_id, school_id=school_id)
        self.students.delete_by_id(student_id)
