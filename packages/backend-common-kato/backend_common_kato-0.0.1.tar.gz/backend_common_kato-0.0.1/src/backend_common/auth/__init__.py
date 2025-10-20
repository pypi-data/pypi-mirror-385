# src/backend_common/auth/__init__.py
"""
Authentication and authorization utilities for backend services.

Provides JWT-based authentication, service-to-service auth,
and FastAPI dependencies for securing endpoints.
"""

from .dependencies import get_current_user, require_auth, require_service_auth
from .manager import AuthManager, JWTAuthManager

__all__ = [
    "AuthManager",
    "JWTAuthManager",
    "require_auth",
    "require_service_auth",
    "get_current_user",
]
