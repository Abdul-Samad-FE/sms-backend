from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.school import School
from app.schemas.school import SchoolRead

router = APIRouter(prefix="/schools", tags=["Schools"])

@router.get("/", response_model=List[SchoolRead])
def get_schools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Fetch all schools with optional pagination.
    """
    schools = db.query(School).offset(skip).limit(limit).all()
    return schools

@router.get("/{school_id}", response_model=SchoolRead)
def get_school(school_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single school by ID.
    """
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school
