"""Attendance endpoints with tenancy + UBAC."""

from datetime import date as date_type
from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.rbac import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.attendance import AttendanceCreate, AttendanceRead, AttendanceUpdate
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/", response_model=List[AttendanceRead])
def list_attendance(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[int] = None,
    student_id: Optional[int] = None,
    attendance_date: Optional[date_type] = None,
    current_user: User = Depends(require_permission("attendance:read")),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        school_id = current_user.school_id
    return AttendanceService(db).list_records(
        school_id=school_id,
        student_id=student_id,
        attendance_date=attendance_date,
        skip=skip,
        limit=limit,
    )


@router.get("/{attendance_id}", response_model=AttendanceRead)
def get_attendance(
    attendance_id: int,
    current_user: User = Depends(require_permission("attendance:read")),
    db: Session = Depends(get_db),
):
    record = AttendanceService(db).get_record(attendance_id)
    if not current_user.is_superuser and record.school_id != current_user.school_id:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found"
        )
    return record


@router.post("/", response_model=AttendanceRead, status_code=201)
def create_attendance(
    payload: AttendanceCreate,
    request: Request,
    current_user: User = Depends(require_permission("attendance:create")),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        payload.school_id = current_user.school_id
    record = AttendanceService(db).upsert(payload)
    log_action(
        db,
        user_id=current_user.id,
        action="upsert_attendance",
        entity="attendance",
        entity_id=record.id,
        ip_address=request.client.host if request.client else None,
    )
    return record


@router.put("/{attendance_id}", response_model=AttendanceRead)
def update_attendance(
    attendance_id: int,
    payload: AttendanceUpdate,
    request: Request,
    current_user: User = Depends(require_permission("attendance:update")),
    db: Session = Depends(get_db),
):
    record = AttendanceService(db).update_record(attendance_id, payload)
    log_action(
        db,
        user_id=current_user.id,
        action="update_attendance",
        entity="attendance",
        entity_id=record.id,
        ip_address=request.client.host if request.client else None,
    )
    return record


@router.delete("/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    request: Request,
    current_user: User = Depends(require_permission("attendance:delete")),
    db: Session = Depends(get_db),
):
    AttendanceService(db).delete_record(attendance_id)
    log_action(
        db,
        user_id=current_user.id,
        action="delete_attendance",
        entity="attendance",
        entity_id=attendance_id,
        ip_address=request.client.host if request.client else None,
    )
    return {"message": "Attendance record deleted successfully"}
