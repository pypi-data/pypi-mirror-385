# src/backend_common/models/pagination.py
"""
Pagination models for consistent API responses.

Provides standardized pagination parameters and response models
for paginated endpoints across all services.
"""

from typing import Generic, List, Optional, TypeVar

from pydantic import Field, validator

from .base import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Standard pagination parameters for API endpoints.

    Provides consistent pagination behavior across all services
    with configurable limits and validation.
    """

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @validator("size")
    def validate_size(cls, v):
        """Validate page size is within reasonable limits."""
        if v > 100:
            raise ValueError("Page size cannot exceed 100")
        return v

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response wrapper.

    Provides consistent pagination metadata and data structure
    for all paginated API responses.
    """

    items: List[T] = Field(description="List of items for current page")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        pagination: PaginationParams,
    ) -> "PaginatedResponse[T]":
        """
        Create paginated response from items and pagination params.

        Args:
            items: List of items for current page
            total: Total number of items across all pages
            pagination: Pagination parameters used

        Returns:
            PaginatedResponse with calculated metadata
        """
        pages = (
            total + pagination.size - 1
        ) // pagination.size  # Ceiling division

        return cls(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=pages,
        )

    @property
    def has_next(self) -> bool:
        """Check if there are more pages after current."""
        return self.page < self.pages

    @property
    def has_previous(self) -> bool:
        """Check if there are pages before current."""
        return self.page > 1
