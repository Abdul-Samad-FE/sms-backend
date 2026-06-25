"""User CRUD orchestration with password hashing + tenancy enforcement."""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.base_repository import DuplicatedError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.base_service import BaseService


class UserService(BaseService[User]):
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        super().__init__(self.users)

    def list_users(
        self,
        school_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        if school_id is not None:
            return self.users.list_by_school(school_id, skip=skip, limit=limit)
        return self.users.list_all(skip=skip, limit=limit)

    def get(self, user_id: int) -> User:
        user = self.users.get_with_role(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def create_user(self, payload: UserCreate) -> User:
        if self.users.get_by_email(payload.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        data = payload.model_dump()
        data["password"] = hash_password(data["password"])
        try:
            user = User(**data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as exc:  # IntegrityError, etc.
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    def update_user(self, user_id: int, payload: UserUpdate) -> User:
        user = self.get(user_id)
        data = payload.model_dump(exclude_unset=True)
        if "password" in data and data["password"]:
            data["password"] = hash_password(data["password"])
        elif "password" in data:
            data.pop("password")
        try:
            for k, v in data.items():
                setattr(user, k, v)
            self.db.commit()
            self.db.refresh(user)
            return user
        except DuplicatedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    def delete_user(self, user_id: int) -> None:
        user = self.get(user_id)
        self.db.delete(user)
        self.db.commit()
