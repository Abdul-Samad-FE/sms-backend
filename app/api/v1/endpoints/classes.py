"""Class endpoints with tenancy + UBAC."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.rbac import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.class_schema import ClassCreate, ClassRead, ClassUpdate
from app.services.class_service import ClassService

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("/", response_model=List[ClassRead])
def list_classes(
    school_id: Optional[int] = None,
    current_user: User = Depends(require_permission("class:read")),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        school_id = current_user.school_id
    return ClassService(db).list_classes(school_id=school_id)


@router.get("/{class_id}", response_model=ClassRead)
def get_class(
    class_id: int,
    current_user: User = Depends(require_permission("class:read")),
    db: Session = Depends(get_db),
):
    school_id = None if current_user.is_superuser else current_user.school_id
    return ClassService(db).get_class(class_id, school_id=school_id)


@router.post("/", response_model=ClassRead, status_code=201)
def create_class(
    payload: ClassCreate,
    request: Request,
    current_user: User = Depends(require_permission("class:create")),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        payload.school_id = current_user.school_id
    cls = ClassService(db).create_class(payload)
    log_action(
        db,
        user_id=current_user.id,
        action="create_class",
        entity="class",
        entity_id=cls.id,
        ip_address=request.client.host if request.client else None,
    )
    return cls


@router.put("/{class_id}", response_model=ClassRead)
def update_class(
    class_id: int,
    payload: ClassUpdate,
    request: Request,
    current_user: User = Depends(require_permission("class:update")),
    db: Session = Depends(get_db),
):
    school_id = None if current_user.is_superuser else current_user.school_id
    if not current_user.is_superuser:
        payload.school_id = current_user.school_id
    cls = ClassService(db).update_class(class_id, payload, school_id=school_id)
    log_action(
        db,
        user_id=current_user.id,
        action="update_class",
        entity="class",
        entity_id=cls.id,
        ip_address=request.client.host if request.client else None,
    )
    return cls


@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    request: Request,
    current_user: User = Depends(require_permission("class:delete")),
    db: Session = Depends(get_db),
):
    school_id = None if current_user.is_superuser else current_user.school_id
    ClassService(db).delete_class(class_id, school_id=school_id)
    log_action(
        db,
        user_id=current_user.id,
        action="delete_class",
        entity="class",
        entity_id=class_id,
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "Class deleted successfully"}
