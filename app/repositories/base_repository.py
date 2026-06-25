"""Generic CRUD repository — every concrete repo extends this.

Adapted from GreenX 2.0 `app/repository/base_repository.py`. Schemas
arriving here are already validated Pydantic v2 models, so we use
`.model_dump(exclude_unset=True)` to honour partial updates.
"""

import math
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class NotFoundError(Exception):
    """Raised when read_by_id / delete_by_id cannot find the requested row."""


class DuplicatedError(Exception):
    """Raised on unique-constraint violations during create/update."""


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: Type[ModelT]):
        self.db = db
        self.model = model

    # ---------- Read ----------
    def read_by_id(self, id: int) -> ModelT:
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} id={id} not found")
        return obj

    def get_by_id(self, id: int) -> Optional[ModelT]:
        """Non-raising variant of read_by_id."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def find_one(self, **filters: Any) -> Optional[ModelT]:
        return self.db.query(self.model).filter_by(**filters).first()

    def find_many(self, **filters: Any) -> List[ModelT]:
        return self.db.query(self.model).filter_by(**filters).all()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[ModelT]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def list_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[ModelT], int]:
        """Return (items, total_count). Page is 1-indexed."""
        page = max(1, page)
        page_size = max(1, min(page_size, 500))
        query = self.db.query(self.model)
        if filters:
            query = query.filter_by(**filters)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    # ---------- Write ----------
    def create(self, schema: BaseModel | Dict[str, Any]) -> ModelT:
        data = schema.model_dump() if isinstance(schema, BaseModel) else dict(schema)
        try:
            obj = self.model(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicatedError(str(exc.orig)) from exc

    def create_from_dict(self, data: Dict[str, Any]) -> ModelT:
        return self.create(data)

    def update(self, id: int, schema: BaseModel | Dict[str, Any]) -> ModelT:
        obj = self.read_by_id(id)
        data = (
            schema.model_dump(exclude_unset=True)
            if isinstance(schema, BaseModel)
            else dict(schema)
        )
        for key, value in data.items():
            setattr(obj, key, value)
        try:
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicatedError(str(exc.orig)) from exc

    def delete_by_id(self, id: int) -> None:
        obj = self.read_by_id(id)
        self.db.delete(obj)
        self.db.commit()

    # ---------- Helpers ----------
    @staticmethod
    def page_count(total: int, page_size: int) -> int:
        return max(1, math.ceil(total / max(1, page_size)))
