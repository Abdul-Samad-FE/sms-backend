"""Student endpoints with school-scoped tenancy + UBAC permission gates."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.rbac import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


def _scope_school_id(current_user: User, requested: Optional[int]) -> Optional[int]:
    """Force tenancy: non-superusers see only their school regardless of query."""
    if current_user.is_superuser:
        return requested
    return current_user.school_id


@router.get("/", response_model=List[StudentRead])
def list_students(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[int] = None,
    class_id: Optional[int] = None,
    current_user: User = Depends(require_permission("student:read")),
    db: Session = Depends(get_db),
):
    school_id = _scope_school_id(current_user, school_id)
    return StudentService(db).list_students(
        school_id=school_id, class_id=class_id, skip=skip, limit=limit
    )


@router.post("/add", response_model=StudentRead, status_code=201)
def create_student(
    payload: StudentCreate,
    request: Request,
    current_user: User = Depends(require_permission("student:create")),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        payload.school_id = current_user.school_id
    student = StudentService(db).create_student(payload)
    log_action(
        db,
        user_id=current_user.id,
        action="create_student",
        entity="student",
        entity_id=student.id,
        ip_address=request.client.host if request.client else None,
    )
    return student


@router.get("/{id:int}", response_model=StudentRead)
def get_student(
    id: int,
    current_user: User = Depends(require_permission("student:read")),
    db: Session = Depends(get_db),
):
    school_id = None if current_user.is_superuser else current_user.school_id
    return StudentService(db).get_student(id, school_id=school_id)


@router.put("/{id:int}", response_model=StudentRead)
def update_student(
    id: int,
    payload: StudentUpdate,
    request: Request,
    current_user: User = Depends(require_permission("student:update")),
    db: Session = Depends(get_db),
):
    school_id = None if current_user.is_superuser else current_user.school_id
    if not current_user.is_superuser:
        payload.school_id = current_user.school_id
    student = StudentService(db).update_student(id, payload, school_id=school_id)
    log_action(
        db,
        user_id=current_user.id,
        action="update_student",
        entity="student",
        entity_id=student.id,
        ip_address=request.client.host if request.client else None,
    )
    return student


@router.delete("/{id:int}")
def delete_student(
    id: int,
    request: Request,
    current_user: User = Depends(require_permission("student:delete")),
    db: Session = Depends(get_db),
):
    school_id = None if current_user.is_superuser else current_user.school_id
    StudentService(db).delete_student(id, school_id=school_id)
    log_action(
        db,
        user_id=current_user.id,
        action="delete_student",
        entity="student",
        entity_id=id,
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "Student deleted successfully"}
