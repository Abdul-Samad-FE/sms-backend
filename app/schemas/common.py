"""Shared DTOs — pagination envelope, generic responses."""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PageMeta(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int


class Page(BaseModel, Generic[T]):
    """Standard envelope for paginated list responses.

    Endpoints return `Page[StudentRead]` etc. so the frontend can render
    pagination controls without inspecting headers.
    """

    items: List[T]
    meta: PageMeta

    model_config = ConfigDict(from_attributes=True)
