from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SchoolBase(BaseModel):
    emis_code: str
    name: str
    uc_name: str
    address: Optional[str] = None

class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(BaseModel):
    emis_code: Optional[str] = None
    name: Optional[str] = None
    uc_name: Optional[str] = None
    address: Optional[str] = None

class SchoolRead(SchoolBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
