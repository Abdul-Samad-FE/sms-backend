"""Blacklisted JWT lookups (used by sign-out + JWTBearer)."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.blacklisted_token import BlacklistedToken
from app.repositories.base_repository import BaseRepository


class BlacklistedTokenRepository(BaseRepository[BlacklistedToken]):
    def __init__(self, db: Session):
        super().__init__(db, BlacklistedToken)

    def is_blacklisted(self, token: str) -> bool:
        return (
            self.db.query(BlacklistedToken)
            .filter(BlacklistedToken.token == token)
            .first()
            is not None
        )

    def blacklist(
        self,
        token: str,
        user_id: Optional[int] = None,
        expires_at: Optional[datetime] = None,
    ) -> BlacklistedToken:
        entry = BlacklistedToken(token=token, user_id=user_id, expires_at=expires_at)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
