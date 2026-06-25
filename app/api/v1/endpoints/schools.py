"""School endpoints — only superusers may create/update/delete (cross-tenant op)."""

from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.dependencies import get_current_active_user, get_current_super_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.school import SchoolCreate, SchoolRead, SchoolUpdate
from app.services.school_service import SchoolService

router = APIRouter(prefix="/schools", tags=["Schools"])


@router.get("/", response_model=List[SchoolRead])
def list_schools(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    schools = SchoolService(db).list_schools(skip=skip, limit=limit)
    if current_user.is_superuser:
        return schools
    # Non-superusers only see their own school
    return [s for s in schools if s.id == current_user.school_id]


@router.get("/{school_id}", response_model=SchoolRead)
def get_school(
    school_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    school = SchoolService(db).get_school(school_id)
    if not current_user.is_superuser and school.id != current_user.school_id:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
    return school


@router.post("/", response_model=SchoolRead, status_code=201)
def create_school(
    payload: SchoolCreate,
    request: Request,
    current_user: User = Depends(get_current_super_user),
    db: Session = Depends(get_db),
):
    school = SchoolService(db).create_school(payload)
    log_action(
        db,
        user_id=current_user.id,
        action="create_school",
        entity="school",
        entity_id=school.id,
        ip_address=request.client.host if request.client else None,
    )
    return school


@router.put("/{school_id}", response_model=SchoolRead)
def update_school(
    school_id: int,
    payload: SchoolUpdate,
    request: Request,
    current_user: User = Depends(get_current_super_user),
    db: Session = Depends(get_db),
):
    school = SchoolService(db).update_school(school_id, payload)
    log_action(
        db,
        user_id=current_user.id,
        action="update_school",
        entity="school",
        entity_id=school.id,
        ip_address=request.client.host if request.client else None,
    )
    return school


@router.delete("/{school_id}")
def delete_school(
    school_id: int,
    request: Request,
    current_user: User = Depends(get_current_super_user),
    db: Session = Depends(get_db),
):
    SchoolService(db).delete_school(school_id)
    log_action(
        db,
        user_id=current_user.id,
        action="delete_school",
        entity="school",
        entity_id=school_id,
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "School deleted successfully"}
