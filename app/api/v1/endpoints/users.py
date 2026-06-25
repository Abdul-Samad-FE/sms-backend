"""User management endpoints — gated by user:* permissions."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.rbac import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def _to_read(user: User) -> UserRead:
    dto = UserRead.model_validate(user)
    dto.role_name = user.role_obj.role_name if user.role_obj else None
    return dto


@router.get("/", response_model=List[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[int] = None,
    current_user: User = Depends(require_permission("user:read")),
    db: Session = Depends(get_db),
):
    # Non-superusers may only list their own school's users.
    if not current_user.is_superuser:
        school_id = current_user.school_id
    users = UserService(db).list_users(school_id=school_id, skip=skip, limit=limit)
    return [_to_read(u) for u in users]


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:read")),
    db: Session = Depends(get_db),
):
    user = UserService(db).get(user_id)
    if not current_user.is_superuser and user.school_id != current_user.school_id:
        # Tenancy boundary
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _to_read(user)


@router.post("/", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    request: Request,
    current_user: User = Depends(require_permission("user:create")),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        # Force the new user into the creator's school
        payload.school_id = current_user.school_id
        # Non-superusers cannot mint other superusers
        payload.is_superuser = False
    user = UserService(db).create_user(payload)
    log_action(
        db,
        user_id=current_user.id,
        action="create_user",
        entity="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    return _to_read(user)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    current_user: User = Depends(require_permission("user:update")),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        payload.school_id = current_user.school_id
        payload.is_superuser = None  # ignored
    user = UserService(db).update_user(user_id, payload)
    log_action(
        db,
        user_id=current_user.id,
        action="update_user",
        entity="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    return _to_read(user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_permission("user:delete")),
    db: Session = Depends(get_db),
):
    UserService(db).delete_user(user_id)
    log_action(
        db,
        user_id=current_user.id,
        action="delete_user",
        entity="user",
        entity_id=user_id,
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "User deleted successfully"}
