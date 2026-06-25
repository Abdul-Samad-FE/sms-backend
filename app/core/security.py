"""JWT + password hashing helpers.

Adapted from GreenX 2.0 `app/core/security.py`. JWTBearer is a FastAPI
security scheme that validates the bearer token AND consults the
blacklist table so revoked tokens (sign-out) cannot be replayed.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

# bcrypt rounds=12 is the FastAPI default. We use the `bcrypt` library directly
# rather than passlib, which is unmaintained and incompatible with bcrypt >= 4.1.
_BCRYPT_ROUNDS = 12
# bcrypt only hashes the first 72 bytes of the input and raises on longer
# secrets, so we truncate to 72 bytes (the de-facto standard behaviour).
_BCRYPT_MAX_BYTES = 72


def _to_bcrypt_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]


# ---------- Password helpers ----------
def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(_to_bcrypt_bytes(plain), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(_to_bcrypt_bytes(plain), hashed.encode("utf-8"))
    except Exception:
        return False


# ---------- JWT helpers ----------
def create_access_token(
    subject: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, datetime]:
    """Sign a JWT carrying the given claim dict.

    Returns (token, expiration_datetime). The expiration is included in
    the response so the frontend can pre-empt token expiry without parsing
    the JWT itself.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {**subject, "exp": expire, "iat": datetime.now(timezone.utc)}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expire


def decode_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Return the decoded payload or None if signature/expiry fails."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


# ---------- HTTPBearer with blacklist check ----------
class JWTBearer(HTTPBearer):
    """Custom security scheme: validates signature, expiry, and blacklist."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(  # type: ignore[override]
        self,
        request: Request,
        db: Session = Depends(get_db),
    ) -> str:
        creds: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        if not creds:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing Authorization header",
            )
        if creds.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme",
            )
        token = creds.credentials
        payload = decode_jwt(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token",
            )

        # Blacklist check — imported here to avoid circular import at module load
        from app.models.blacklisted_token import BlacklistedToken

        revoked = (
            db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
        )
        if revoked is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token has been revoked",
            )
        return token
