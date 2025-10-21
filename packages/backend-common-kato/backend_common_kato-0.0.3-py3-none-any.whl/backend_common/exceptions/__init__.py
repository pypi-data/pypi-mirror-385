# src/backend_common/exceptions/__init__.py
"""
Common exception classes for backend services.

This module provides standardized exception handling across all services.
"""

from .base import (
    ErrorCode,
    BaseError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
)
from .business import (
    BusinessLogicError,
    AlreadyExistsError,
    ExternalServiceError,
    ServiceUnavailableError,
    TimeoutError,
)
from .http import (
    HTTPError,
    BadRequestError,
    RateLimitExceededError,
)
from .handlers import setup_exception_handlers

__all__ = [
    # Error codes
    "ErrorCode",
    # Base exceptions
    "BaseError",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    # Business exceptions
    "BusinessLogicError",
    "AlreadyExistsError",
    "ExternalServiceError",
    "ServiceUnavailableError",
    "TimeoutError",
    # HTTP exceptions
    "HTTPError",
    "BadRequestError",
    "RateLimitExceededError",
    # Handlers
    "setup_exception_handlers",
]
