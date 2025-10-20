# src/backend_common/middleware/logging.py
"""
Request/response logging middleware.

Provides structured logging for all HTTP requests and responses
with timing, status codes, and correlation tracking.
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured request/response logging.

    Logs all HTTP requests and responses with timing information,
    status codes, and correlation IDs for monitoring and debugging.
    """

    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: list[str] = None,
    ) -> None:
        """
        Initialize logging middleware.

        Args:
            app: FastAPI application instance
            log_request_body: Whether to log request body content
            log_response_body: Whether to log response body content
            exclude_paths: Paths to exclude from logging (e.g., health checks)
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request with logging.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain

        Returns:
            Response: HTTP response
        """
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        start_time = time.time()
        correlation_id = getattr(request.state, "correlation_id", None)

        # Log request
        request_log = {
            "event": "request_started",
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "correlation_id": correlation_id,
            "user_agent": request.headers.get("user-agent"),
            "remote_addr": request.client.host if request.client else None,
        }

        if self.log_request_body and request.method in [
            "POST",
            "PUT",
            "PATCH",
        ]:
            try:
                body = await request.body()
                if body:
                    request_log["request_body_size"] = len(body)
            except Exception as e:
                request_log["request_body_error"] = str(e)

        logger.info("Request started", extra=request_log)

        # Process request
        response = await call_next(request)

        # Calculate timing
        process_time = time.time() - start_time

        # Log response
        response_log = {
            "event": "request_completed",
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "correlation_id": correlation_id,
        }

        # Add response headers for debugging
        if hasattr(response, "headers"):
            response_log["content_type"] = response.headers.get("content-type")
            response_log["content_length"] = response.headers.get(
                "content-length"
            )

        # Log level based on status code
        if response.status_code >= 500:
            logger.error(
                "Request completed with server error", extra=response_log
            )
        elif response.status_code >= 400:
            logger.warning(
                "Request completed with client error", extra=response_log
            )
        else:
            logger.info("Request completed successfully", extra=response_log)

        return response
