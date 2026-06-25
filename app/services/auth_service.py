"""Authentication orchestration — sign-in, sign-up, password change, sign-out.

Composes UserRepository, RoleRepository, and BlacklistedTokenRepository
plus the JWT and password helpers from `app.core.security`. Returns
fully-formed Payload + token responses ready to ship to the frontend.
"""

import secrets
from datetime import datetime
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.rbac import get_user_modules, get_user_permissions
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.blacklisted_token_repository import BlacklistedTokenRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import ChangePassword, Payload, SignIn, SignInResponse, SignUp


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)
        self.tokens = BlacklistedTokenRepository(db)

    # ---------- Helpers ----------
    def _build_payload(self, user: User) -> Payload:
        permissions = get_user_permissions(self.db, user)
        modules = get_user_modules(self.db, user)
        return Payload(
            id=user.id,
            email=user.email,
            name=user.name,
            username=user.username,
            is_superuser=bool(user.is_superuser),
            is_active=bool(user.is_active),
            is_first_login=bool(user.is_first_login),
            user_token=user.user_token,
            role_id=user.role_id,
            user_role=user.role_obj.role_name if user.role_obj else None,
            school_id=user.school_id,
            school_name=user.school.name if user.school else None,
            accessible_modules=modules,
            permissions=permissions,
        )

    def _issue_token(self, user: User) -> Tuple[str, datetime]:
        return create_access_token(
            {
                "id": user.id,
                "email": user.email,
                "is_superuser": bool(user.is_superuser),
            }
        )

    # ---------- Public API ----------
    def sign_in(self, payload: SignIn) -> SignInResponse:
        user = self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive — contact your administrator",
            )

        # Rotate per-session token so stale tabs are forced to re-auth.
        user.user_token = secrets.token_urlsafe(32)
        self.db.commit()
        self.db.refresh(user)

        access_token, expiration = self._issue_token(user)
        return SignInResponse(
            access_token=access_token,
            expiration=expiration,
            user_info=self._build_payload(user),
        )

    def sign_up(self, payload: SignUp) -> SignInResponse:
        if self.users.get_by_email(payload.email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        role_id = payload.role_id
        if role_id is None:
            admin_role = self.roles.get_by_name("admin")
            if admin_role is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Default 'admin' role not seeded",
                )
            role_id = admin_role.id

        user = User(
            name=payload.name,
            email=payload.email,
            password=hash_password(payload.password),
            school_id=payload.school_id,
            role_id=role_id,
            is_active=True,
            is_superuser=False,
            is_first_login=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.sign_in(SignIn(email=payload.email, password=payload.password))

    def change_password(self, user: User, payload: ChangePassword) -> None:
        if not verify_password(payload.old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect",
            )
        user.password = hash_password(payload.new_password)
        user.is_first_login = False
        self.db.commit()

    def sign_out(self, user: User, token: str) -> None:
        if not self.tokens.is_blacklisted(token):
            self.tokens.blacklist(token, user_id=user.id)
        # Invalidate per-session token too (defence in depth)
        user.user_token = None
        self.db.commit()

    def me(self, user: User) -> Payload:
        # Reload via ORM to ensure relationships are populated for the payload
        fresh = self.users.get_with_role(user.id) or user
        return self._build_payload(fresh)
