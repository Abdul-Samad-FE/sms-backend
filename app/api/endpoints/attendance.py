from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.db.session import get_db
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceRead

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/", response_model=List[AttendanceRead])
def get_attendance(
    skip: int = 0, 
    limit: int = 100, 
    school_id: int = None,
    student_id: int = None,
    attendance_date: date = None,
    db: Session = Depends(get_db)
):
    """
    Fetch attendance records with optional filtering by school, student, or date.
    """
    query = db.query(Attendance)
    if school_id:
        query = query.filter(Attendance.school_id == school_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if attendance_date:
        query = query.filter(Attendance.date == attendance_date)
        
    records = query.offset(skip).limit(limit).all()
    return records

@router.get("/{attendance_id}", response_model=AttendanceRead)
def get_attendance_record(attendance_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single attendance record by ID.
    """
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return record
