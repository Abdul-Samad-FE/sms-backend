from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.student import Student
from app.schemas.student import StudentRead

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/", response_model=List[StudentRead])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Fetch all students with optional pagination.
    """
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single student by ID.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
