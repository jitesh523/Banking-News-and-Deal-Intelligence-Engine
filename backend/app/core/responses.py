"""
Standardized API response models for consistent pagination and envelope format.
"""

import math
from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated responses."""

    page: int = Field(..., description="Current page number (1-indexed)")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items across all pages")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether a next page exists")
    has_prev: bool = Field(..., description="Whether a previous page exists")

    @classmethod
    def create(cls, *, page: int, per_page: int, total: int) -> "PaginationMeta":
        total_pages = max(1, math.ceil(total / per_page))
        return cls(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


class APIResponse(BaseModel):
    """Standard envelope for all API responses."""

    success: bool = True
    message: Optional[str] = None
    data: Any = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def ok(cls, data: Any = None, message: str = "Success") -> "APIResponse":
        return cls(success=True, data=data, message=message)

    @classmethod
    def error(cls, message: str, data: Any = None) -> "APIResponse":
        return cls(success=False, data=data, message=message)


class PaginatedResponse(BaseModel):
    """Standard paginated response with data and pagination metadata."""

    success: bool = True
    data: List[Any] = Field(default_factory=list)
    pagination: PaginationMeta
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def create(
        cls,
        items: List[Any],
        total: int,
        page: int,
        per_page: int,
    ) -> "PaginatedResponse":
        return cls(
            data=items,
            pagination=PaginationMeta.create(page=page, per_page=per_page, total=total),
        )
