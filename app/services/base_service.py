"""Generic CRUD service — thin wrapper around BaseRepository.

Concrete services extend this and add domain-specific orchestration
(validation, audit calls, cross-aggregate checks). Adapted from GreenX
2.0 `app/services/base_service.py`.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

from app.repositories.base_repository import BaseRepository

ModelT = TypeVar("ModelT")


class BaseService(Generic[ModelT]):
    def __init__(self, repository: BaseRepository[ModelT]):
        self._repository = repository

    @property
    def repository(self) -> BaseRepository[ModelT]:
        return self._repository

    def get_by_id(self, id: int) -> ModelT:
        return self._repository.read_by_id(id)

    def get_optional(self, id: int) -> Optional[ModelT]:
        return self._repository.get_by_id(id)

    def list_all(self, skip: int = 0, limit: int = 100) -> List[ModelT]:
        return self._repository.list_all(skip=skip, limit=limit)

    def add(self, schema: BaseModel | Dict[str, Any]) -> ModelT:
        return self._repository.create(schema)

    def update(self, id: int, schema: BaseModel | Dict[str, Any]) -> ModelT:
        return self._repository.update(id, schema)

    def remove_by_id(self, id: int) -> None:
        self._repository.delete_by_id(id)
