"""Class orchestration."""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.class_model import Class
from app.repositories.base_repository import DuplicatedError, NotFoundError
from app.repositories.class_repository import ClassRepository
from app.schemas.class_schema import ClassCreate, ClassUpdate
from app.services.base_service import BaseService


class ClassService(BaseService[Class]):
    def __init__(self, db: Session):
        self.db = db
        self.classes = ClassRepository(db)
        super().__init__(self.classes)

    def list_classes(self, school_id: Optional[int] = None) -> List[Class]:
        if school_id is not None:
            return self.classes.list_by_school(school_id)
        return self.classes.list_all(skip=0, limit=1000)

    def get_class(self, class_id: int, school_id: Optional[int] = None) -> Class:
        cls = self.classes.get_by_id(class_id)
        if cls is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
            )
        if school_id is not None and cls.school_id != school_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
            )
        return cls

    def create_class(self, payload: ClassCreate) -> Class:
        existing = self.classes.find_by_school_and_name(
            payload.school_id, payload.class_name, payload.section
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A class with this name + section already exists for the school",
            )
        try:
            return self.classes.create(payload)
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    def update_class(
        self, class_id: int, payload: ClassUpdate, school_id: Optional[int] = None
    ) -> Class:
        self.get_class(class_id, school_id=school_id)
        try:
            return self.classes.update(class_id, payload)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
            )
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    def delete_class(self, class_id: int, school_id: Optional[int] = None) -> None:
        self.get_class(class_id, school_id=school_id)
        self.classes.delete_by_id(class_id)
