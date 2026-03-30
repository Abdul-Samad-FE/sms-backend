from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ClassBase(BaseModel):
    school_id: int
    class_name: str
    section: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    school_id: Optional[int] = None
    class_name: Optional[str] = None
    section: Optional[str] = None

class ClassRead(ClassBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
