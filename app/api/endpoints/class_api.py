from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.class_model import Class
from app.schemas.class_schema import ClassRead

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("/", response_model=List[ClassRead])
def get_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Fetch all classes with optional pagination.
    """
    classes = db.query(Class).offset(skip).limit(limit).all()
    return classes

@router.get("/{class_id}", response_model=ClassRead)
def get_class(class_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single class by ID.
    """
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls
