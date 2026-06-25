"""Role + permission DTOs used by the admin endpoints."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PermissionRead(BaseModel):
    id: int
    permission_key: str
    display_name: str
    module: str
    sub_module: Optional[str] = None
    action: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoleBase(BaseModel):
    role_name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: List[int] = []
    module_ids: List[int] = []


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None
    module_ids: Optional[List[int]] = None


class RoleRead(RoleBase):
    id: int
    created_at: datetime
    permissions: List[PermissionRead] = []
    modules: List["DashboardModuleRead"] = []

    model_config = ConfigDict(from_attributes=True)


class DashboardModuleRead(BaseModel):
    id: int
    modules_name: str
    display_name: str
    icon: Optional[str] = None
    route: Optional[str] = None
    sort_order: int = 0

    model_config = ConfigDict(from_attributes=True)


# Forward-ref resolution for RoleRead.modules
RoleRead.model_rebuild()
