"""FastAPI dependency providers for request-scoped objects.

Mirrors GreenX 2.0 `app/core/dependencies.py`. The chain
`get_current_user → get_current_active_user → get_current_admin_user`
escalates the authorisation requirement as you nest deps deeper.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import JWTBearer, decode_jwt
from app.db.session import get_db
from app.models.user import User


def get_current_user(
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the User from a verified JWT.

    JWTBearer has already validated signature, expiry, and blacklist.
    Here we just look up the row and surface a 401 if the user was
    deleted between token issuance and this request.
    """
    payload = decode_jwt(token) or {}
    user_id: Optional[int] = payload.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user id",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def get_current_super_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Superusers ignore RBAC entirely — used for cross-tenant ops."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Admin = superuser OR role named 'admin' inside their school."""
    if current_user.is_superuser:
        return current_user
    role = current_user.role_obj
    if role is None or role.role_name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
