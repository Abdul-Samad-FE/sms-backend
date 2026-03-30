from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, UniqueConstraint
from app.db.session import Base
from sqlalchemy.orm import relationship
import enum

class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    leave = "leave"

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    remarks = Column(String(255))

    # Constraints
    __table_args__ = (UniqueConstraint("school_id", "student_id", "date"),)

    # Relationships
    school = relationship("School", back_populates="attendance")
    student = relationship("Student", back_populates="attendance_records")
