# src/backend_common/auth/__init__.py
"""
Authentication and authorization utilities for backend services.

Provides JWT-based authentication, API key authentication, service-to-service auth,
and FastAPI dependencies for securing endpoints.
"""

from .dependencies import (
    get_current_user,
    require_auth,
    require_service_auth,
    set_auth_manager,
    set_config,
    validate_api_key
)
from .manager import AuthManager, JWTAuthManager

__all__ = [
    "AuthManager",
    "JWTAuthManager",
    "require_auth",
    "require_service_auth",
    "get_current_user",
    "set_auth_manager",
    "set_config",
    "validate_api_key",
]
