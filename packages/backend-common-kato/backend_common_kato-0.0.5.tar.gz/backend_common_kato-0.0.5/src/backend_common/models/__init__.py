# src/backend_common/models/__init__.py
"""
Shared data models for backend services.

Provides common Pydantic models for health checks, pagination,
and base model classes with standardized validation.
"""

from .base import (
    BaseModel,
    TimestampMixin,
    IdentifiableMixin,
    SQLAlchemyBase,
    SQLAlchemyTimestampMixin,
    BaseResponse,
    ErrorResponse,
)
from .pagination import (
    PaginationParams,
    PaginationMeta,
    PaginatedResponse,
)
from .health import (
    HealthStatus,
    ServiceHealth,
    HealthResponse,
)

__all__ = [
    # Base models
    "BaseModel",
    "TimestampMixin",
    "IdentifiableMixin",
    "SQLAlchemyBase",
    "SQLAlchemyTimestampMixin",
    "BaseResponse",
    "ErrorResponse",
    # Pagination
    "PaginationParams",
    "PaginationMeta",
    "PaginatedResponse",
    # Health
    "HealthStatus",
    "ServiceHealth",
    "HealthResponse",
]
