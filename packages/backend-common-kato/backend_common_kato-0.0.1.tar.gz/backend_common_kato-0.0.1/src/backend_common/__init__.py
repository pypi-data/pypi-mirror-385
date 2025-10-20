# src/backend_common/__init__.py
"""
Backend Common - Shared utilities for Python backend services.

This package provides common functionality for backend microservices including:
- Exception handling
- Authentication and authorization
- HTTP client utilities
- Database management
- Logging utilities
- Middleware components
"""

__version__ = "0.1.0"
__author__ = "Your Team"

from .auth import *
from .config import *
from .database import *
from .exceptions import *
from .http import *
from .middleware import *
from .models import *
from .utils import *

__all__ = [
    # Exceptions
    "BaseError",
    "NotFoundError",
    "UnauthorizedError",
    "ValidationError",
    "BusinessLogicError",
    # Auth
    "AuthManager",
    "JWTAuthManager",
    "require_auth",
    "require_service_auth",
    # HTTP
    "ServiceClient",
    "HTTPClient",
    # Database
    "DatabaseManager",
    "get_db_session",
    # Middleware
    "CorrelationMiddleware",
    "LoggingMiddleware",
    "AuthMiddleware",
    # Models
    "BaseModel",
    "HealthResponse",
    "PaginationParams",
    # Utils
    "TimeUtils",
    "ValidationUtils",
    # Config
    "BaseConfig",
    "ServiceConfig",
]
