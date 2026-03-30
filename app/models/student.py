from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    enroll_no = Column(String(50), nullable=False)
    father_name = Column(String(150), nullable=False)
    father_contact = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (UniqueConstraint("school_id", "enroll_no"),)

    # Relationships
    school = relationship("School", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
