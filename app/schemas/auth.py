"""Auth-flow DTOs — sign-in, sign-up, token payload, password change."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class SignUp(BaseModel):
    """Used by /auth/sign-up — restricted to creating a school admin during
    bootstrap. For ordinary user creation see admin endpoints.
    """

    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    school_id: int
    role_id: Optional[int] = None  # Defaults to the 'admin' role if omitted


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)


class Payload(BaseModel):
    """Identity bundle returned to the frontend after sign-in.

    Mirrors GreenX 2.0's `auth_schema.Payload` — `accessible_modules` drives
    sidebar rendering and `permissions` drives button-level gating.
    """

    id: int
    email: str
    name: str
    username: Optional[str] = None
    is_superuser: bool = False
    is_active: bool = True
    is_first_login: bool = True
    user_token: Optional[str] = None

    role_id: Optional[int] = None
    user_role: Optional[str] = None

    school_id: Optional[int] = None
    school_name: Optional[str] = None

    accessible_modules: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SignInResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expiration: datetime
    user_info: Payload


class GenericMessage(BaseModel):
    message: str
    extra: Optional[Dict[str, Any]] = None
