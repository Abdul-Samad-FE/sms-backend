"""School orchestration."""

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.school import School
from app.repositories.base_repository import DuplicatedError, NotFoundError
from app.repositories.school_repository import SchoolRepository
from app.schemas.school import SchoolCreate, SchoolUpdate
from app.services.base_service import BaseService


class SchoolService(BaseService[School]):
    def __init__(self, db: Session):
        self.db = db
        self.schools = SchoolRepository(db)
        super().__init__(self.schools)

    def list_schools(self, skip: int = 0, limit: int = 100) -> List[School]:
        return self.schools.list_all(skip=skip, limit=limit)

    def get_school(self, school_id: int) -> School:
        try:
            return self.schools.read_by_id(school_id)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="School not found"
            )

    def create_school(self, payload: SchoolCreate) -> School:
        if self.schools.get_by_emis_code(payload.emis_code) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A school with this EMIS code already exists",
            )
        try:
            return self.schools.create(payload)
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    def update_school(self, school_id: int, payload: SchoolUpdate) -> School:
        try:
            return self.schools.update(school_id, payload)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="School not found"
            )
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    def delete_school(self, school_id: int) -> None:
        try:
            self.schools.delete_by_id(school_id)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="School not found"
            )
