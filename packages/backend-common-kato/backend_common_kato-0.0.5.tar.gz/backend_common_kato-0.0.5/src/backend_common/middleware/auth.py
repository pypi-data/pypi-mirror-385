# src/backend_common/middleware/auth.py
"""
Authentication middleware for FastAPI applications.
"""

import logging
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from ..auth.dependencies import get_auth_manager
from ..exceptions import UnauthorizedError

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication across all requests."""

    def __init__(self, app, exclude_paths: Optional[list[str]] = None) -> None:
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]

    async def dispatch(self, request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )

        try:
            token = auth_header.split(" ")[1]
            auth_manager = get_auth_manager()
            user = await auth_manager.verify_token(token)
            request.state.user = user
        except UnauthorizedError as e:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

        return await call_next(request)
