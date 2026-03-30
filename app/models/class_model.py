from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    class_name = Column(String(100), nullable=False)
    section = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (UniqueConstraint("school_id", "class_name", "section"),)

    # Relationships
    school = relationship("School", back_populates="classes")
