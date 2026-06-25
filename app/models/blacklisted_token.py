"""BlacklistedToken — revoked JWTs that should be rejected on validation.

Populated when a user signs out. JWTBearer consults this table on every
request. A periodic job could prune rows whose stored `expires_at` has
already passed (the JWT itself would already fail to decode).
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db.session import Base


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
