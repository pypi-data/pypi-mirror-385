# src/backend_common/exceptions/__init__.py
"""
Common exception classes for backend services.

This module provides standardized exception handling across all services.
"""

from .base import BaseError
from .business import (
    BusinessLogicError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from .http import (
    BadRequestError,
    ServiceUnavailableError,
    TimeoutError,
    UnauthorizedError,
)

__all__ = [
    "BaseError",
    "BusinessLogicError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "ForbiddenError",
    "UnauthorizedError",
    "BadRequestError",
    "ServiceUnavailableError",
    "TimeoutError",
]
