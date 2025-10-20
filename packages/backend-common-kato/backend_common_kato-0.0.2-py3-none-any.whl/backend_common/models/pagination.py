# src/backend_common/models/pagination.py
"""Pagination models for API responses."""

from typing import Generic, List, Optional, TypeVar
from pydantic import Field, validator

from .base import BaseModel

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-based)"
    )
    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    )

    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Get the limit for database queries."""
        return self.size


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(description="Current page number")
    size: int = Field(description="Number of items per page")
    total_items: int = Field(description="Total number of items")
    total_pages: int = Field(description="Total number of pages")
    has_previous: bool = Field(description="Whether there is a previous page")
    has_next: bool = Field(description="Whether there is a next page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T] = Field(description="List of items for current page")
    pagination: PaginationMeta = Field(description="Pagination metadata")

    @classmethod
    def create(
        cls,
        items: List[T],
        params: PaginationParams,
        total_items: int
    ) -> 'PaginatedResponse[T]':
        """Create a paginated response."""
        import math

        total_pages = math.ceil(total_items / params.size) if total_items > 0 else 0

        pagination = PaginationMeta(
            page=params.page,
            size=params.size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=params.page > 1,
            has_next=params.page < total_pages
        )

        return cls(items=items, pagination=pagination)
