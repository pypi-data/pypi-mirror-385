# src/backend_common/__init__.py
"""
Backend Common - Shared utilities for Python backend services.

Provides common functionality for backend microservices including exception handling,
database management, health monitoring, Pydantic models, and utility functions.
"""

__version__ = "0.0.5"
__author__ = "Kato"

from . import database, models, utils

from .exceptions.base import (
    BaseError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ErrorCode,
)
from .exceptions.business import (
    BusinessLogicError,
    AlreadyExistsError,
    ExternalServiceError,
)
from .models import (
    BaseModel,
    HealthResponse,
    HealthStatus,
    PaginationParams,
    PaginatedResponse,
    SQLAlchemyBase,
    TimestampMixin,
)
from .database import DatabaseManager
from .utils import (
    utc_now,
    Timer,
    validate_email_address,
    validate_username,
)

def get_fastapi_handlers():
    """Get FastAPI exception handlers (requires FastAPI installation)."""
    try:
        from .exceptions.handlers import setup_exception_handlers
        return setup_exception_handlers
    except ImportError:
        raise ImportError("FastAPI is required for exception handlers")

def get_auth_dependencies():
    """Get FastAPI auth dependencies (requires FastAPI installation)."""
    try:
        from .auth import dependencies
        return dependencies
    except ImportError:
        raise ImportError("FastAPI is required for auth dependencies")

def get_middleware():
    """Get FastAPI middleware classes (requires FastAPI installation)."""
    try:
        from .middleware import auth, correlation, logging
        return {
            'AuthMiddleware': auth.AuthMiddleware,
            'CorrelationMiddleware': correlation.CorrelationMiddleware,
            'LoggingMiddleware': logging.LoggingMiddleware,
        }
    except ImportError:
        raise ImportError("FastAPI is required for middleware")

__all__ = [
    "database", "models", "utils",
    "BaseError", "ValidationError", "NotFoundError", "UnauthorizedError",
    "ForbiddenError", "BusinessLogicError", "AlreadyExistsError",
    "ExternalServiceError", "ErrorCode",
    "BaseModel", "HealthResponse", "HealthStatus", "PaginationParams",
    "PaginatedResponse", "SQLAlchemyBase", "TimestampMixin",
    "DatabaseManager",
    "utc_now", "Timer", "validate_email_address", "validate_username",
    "get_fastapi_handlers", "get_auth_dependencies", "get_middleware",
]
