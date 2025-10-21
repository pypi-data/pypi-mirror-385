# src/backend_common/__init__.py
"""
Backend Common - Shared utilities for Python backend services.

This package provides common functionality for backend microservices including:
- Exception handling with standardized error responses
- Database management with SQLAlchemy async support
- Health monitoring and metrics collection
- Pydantic models with validation
- Utility functions for common operations
"""

__version__ = "0.0.3"
__author__ = "Kato"

# Import all modules for easy access
from . import database
from . import exceptions
from . import models
from . import utils

# Import commonly used classes and functions for direct access
from .exceptions import (
    BaseError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    BusinessLogicError,
    AlreadyExistsError,
    ExternalServiceError,
    setup_exception_handlers,
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

from .database import (
    DatabaseManager,
)

from .utils import (
    utc_now,
    Timer,
    validate_email_address,
    validate_username,
)

__all__ = [
    # Modules
    "database",
    "exceptions",
    "models",
    "utils",
    # Exception classes
    "BaseError",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "BusinessLogicError",
    "AlreadyExistsError",
    "ExternalServiceError",
    "setup_exception_handlers",
    # Model classes
    "BaseModel",
    "HealthResponse",
    "HealthStatus",
    "PaginationParams",
    "PaginatedResponse",
    "SQLAlchemyBase",
    "TimestampMixin",
    # Database components
    "DatabaseManager",
    # Utility functions
    "utc_now",
    "Timer",
    "validate_email_address",
    "validate_username",
]
