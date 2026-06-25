from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    enroll_no = Column(String(50), nullable=True) # Making enroll_no optional to deprecate
    admission_number = Column(String(50), nullable=False, unique=True)
    father_name = Column(String(150), nullable=False)
    father_contact = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    section = Column(String(50), nullable=True)
    gender = Column(String(20), nullable=True)
    dob = Column(DateTime, nullable=True)
    admission_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="Active")
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = ()

    # Relationships
    school = relationship("School", back_populates="students")
    student_class = relationship("Class", backref="students")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
