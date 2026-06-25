"""User-specific queries layered on top of BaseRepository."""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.role_obj), joinedload(User.school))
            .filter(User.email == email)
            .first()
        )

    def get_with_role(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.role_obj), joinedload(User.school))
            .filter(User.id == user_id)
            .first()
        )

    def list_by_school(self, school_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.role_obj))
            .filter(User.school_id == school_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def superuser_exists(self) -> bool:
        return self.db.query(User).filter(User.is_superuser.is_(True)).first() is not None
