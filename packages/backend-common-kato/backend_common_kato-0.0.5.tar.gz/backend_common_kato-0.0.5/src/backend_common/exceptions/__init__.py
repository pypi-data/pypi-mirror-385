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
from .http_client import (
    HTTPError,
    BadRequestError,
    RateLimitExceededError,
)

__all__ = [
    "ErrorCode",
    "BaseError",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "BusinessLogicError",
    "AlreadyExistsError",
    "ExternalServiceError",
    "ServiceUnavailableError",
    "TimeoutError",
    "HTTPError",
    "BadRequestError",
    "RateLimitExceededError",
]
