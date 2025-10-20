# src/backend_common/models/__init__.py
"""
Shared data models for backend services.

Provides common Pydantic models for health checks, pagination,
and base model classes with standardized validation.
"""

from .base import BaseModel
from .health import HealthResponse, HealthStatus
from .pagination import PaginatedResponse, PaginationParams

__all__ = [
    "BaseModel",
    "HealthResponse",
    "HealthStatus",
    "PaginationParams",
    "PaginatedResponse",
]
