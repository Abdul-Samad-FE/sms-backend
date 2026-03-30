from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship

class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    emis_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    uc_name = Column(String(150), nullable=False)
    address = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="school", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="school", cascade="all, delete-orphan")
    classes = relationship("Class", back_populates="school", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="school", cascade="all, delete-orphan")
