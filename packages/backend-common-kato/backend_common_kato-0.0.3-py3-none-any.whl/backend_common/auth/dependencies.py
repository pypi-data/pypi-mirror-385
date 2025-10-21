# src/backend_common/auth/dependencies.py
"""
Authentication and API key validation for FastAPI applications.

Provides reusable dependencies for securing FastAPI endpoints
with JWT authentication, API key authentication, and service-to-service auth.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.api_key import APIKeyHeader

from ..config.base import BaseConfig
from ..exceptions import UnauthorizedError, ForbiddenError
from .manager import AuthManager, UserModel

# Global auth manager instance (should be configured by the application)
_auth_manager: Optional[AuthManager] = None
_config: Optional[BaseConfig] = None


def set_auth_manager(auth_manager: AuthManager) -> None:
    """Set the global authentication manager instance."""
    global _auth_manager
    _auth_manager = auth_manager


def set_config(config: BaseConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def get_auth_manager() -> AuthManager:
    """Get the configured authentication manager."""
    if _auth_manager is None:
        raise RuntimeError(
            "Auth manager not configured. Call set_auth_manager() first."
        )
    return _auth_manager


def get_config() -> BaseConfig:
    """Get the configured settings."""
    if _config is None:
        raise RuntimeError(
            "Config not configured. Call set_config() first."
        )
    return _config


security = HTTPBearer()

# API Key Security - Create header instance based on config
def get_api_key_header() -> APIKeyHeader:
    """Get API key header security instance."""
    config = get_config()
    return APIKeyHeader(name=config.API_KEY_NAME, auto_error=False)


async def validate_api_key(
    api_key_header: Optional[str] = Security(get_api_key_header())
) -> bool:
    """
    Authentication and API key validation for FastAPI applications.

    Args:
        api_key_header: API key from request headers

    Returns:
        bool: True if API key is valid

    Raises:
        HTTPException: If API key validation fails
    """
    config = get_config()

    if not config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server"
        )

    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key header missing"
        )

    if api_key_header == config.API_KEY:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Un-authorize: Could not validate api key"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> UserModel:
    """
    FastAPI dependency to get the current authenticated user.

    Args:
        credentials: HTTP Bearer token from request headers
        auth_manager: Authentication manager instance

    Returns:
        UserModel: The authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    try:
        user = await auth_manager.verify_token(credentials.credentials)
        if not user.is_active:
            raise UnauthorizedError("User account is disabled")
        return user
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_auth(
    required_scopes: Optional[list[str]] = None,
) -> callable:
    """
    Create a FastAPI dependency that requires authentication.

    Args:
        required_scopes: List of required scopes for access

    Returns:
        FastAPI dependency function
    """

    async def auth_dependency(
        current_user: UserModel = Depends(get_current_user),
    ) -> UserModel:
        if required_scopes:
            for scope in required_scopes:
                if scope not in current_user.scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Operation requires scope: {scope}",
                    )
        return current_user

    return auth_dependency


async def require_service_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> str:
    """
    FastAPI dependency for service-to-service authentication.

    Args:
        credentials: HTTP Bearer token from request headers
        auth_manager: Authentication manager instance

    Returns:
        str: The service name from the token

    Raises:
        HTTPException: If service authentication fails
    """
    try:
        # Assuming auth_manager has verify_service_token method
        if hasattr(auth_manager, "verify_service_token"):
            service_name = await auth_manager.verify_service_token(
                credentials.credentials
            )
            return service_name
        else:
            raise UnauthorizedError("Service authentication not supported")
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
