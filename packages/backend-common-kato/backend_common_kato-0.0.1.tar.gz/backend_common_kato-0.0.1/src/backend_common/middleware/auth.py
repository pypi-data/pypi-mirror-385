# src/backend_common/middleware/auth.py
"""
Authentication middleware for automatic token validation.

Provides optional authentication middleware that can validate
JWT tokens for protected routes automatically.
"""

import logging
from typing import Callable, Optional, Set

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from ..auth.manager import AuthManager
from ..exceptions import UnauthorizedError

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Optional authentication middleware for automatic token validation.

    Can be configured to protect specific routes or exclude certain paths
    from authentication requirements.
    """

    def __init__(
        self,
        app,
        auth_manager: AuthManager,
        protected_paths: Optional[Set[str]] = None,
        exclude_paths: Optional[Set[str]] = None,
        require_auth_by_default: bool = False,
    ) -> None:
        """
        Initialize authentication middleware.

        Args:
            app: FastAPI application instance
            auth_manager: Authentication manager for token validation
            protected_paths: Specific paths that require authentication
            exclude_paths: Paths to exclude from authentication
            require_auth_by_default: Whether to require auth for all paths by default
        """
        super().__init__(app)
        self.auth_manager = auth_manager
        self.protected_paths = protected_paths or set()
        self.exclude_paths = exclude_paths or {
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc",
        }
        self.require_auth_by_default = require_auth_by_default

    def _should_authenticate(self, path: str) -> bool:
        """
        Determine if a path requires authentication.

        Args:
            path: Request path to check

        Returns:
            bool: True if authentication is required
        """
        # Always exclude certain paths
        if path in self.exclude_paths:
            return False

        # Check if path is explicitly protected
        if self.protected_paths and path in self.protected_paths:
            return True

        # Use default behavior
        return self.require_auth_by_default

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request with optional authentication.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain

        Returns:
            Response: HTTP response
        """
        path = request.url.path

        # Check if authentication is required for this path
        if not self._should_authenticate(path):
            return await call_next(request)

        # Extract authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]

        try:
            # Validate token and get user
            user = await self.auth_manager.verify_token(token)

            # Store user in request state for access in endpoints
            request.state.current_user = user

            correlation_id = getattr(request.state, "correlation_id", None)
            logger.info(
                f"Authenticated user {user.username} for {path}",
                extra={"correlation_id": correlation_id, "user_id": user.id},
            )

        except UnauthorizedError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
