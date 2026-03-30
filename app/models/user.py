from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    staff = "staff"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), server_default=UserRole.staff, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    school = relationship("School", back_populates="users")