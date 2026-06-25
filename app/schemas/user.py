"""User DTOs — refactored to track the new RBAC-aware User model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    """Mirrors `app.models.user.UserRole` — kept for legacy callers."""

    admin = "admin"
    teacher = "teacher"
    staff = "staff"
    superadmin = "superadmin"


class UserBase(BaseModel):
    school_id: Optional[int] = None
    name: str
    username: Optional[str] = None
    email: EmailStr
    role_id: Optional[int] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    school_id: Optional[int] = None
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8)


class UserRead(BaseModel):
    id: int
    school_id: Optional[int] = None
    name: str
    username: Optional[str] = None
    email: EmailStr
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_first_login: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
