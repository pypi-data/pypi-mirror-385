# src/backend_common/middleware/logging.py
"""
Request/response logging middleware for FastAPI applications.
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(
        self,
        app,
        log_requests: bool = True,
        log_responses: bool = True,
        exclude_paths: list[str] = None,
    ) -> None:
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.exclude_paths = exclude_paths or ["/health"]

    async def dispatch(self, request, call_next):
        start_time = time.time()

        if request.url.path in self.exclude_paths:
            return await call_next(request)

        if self.log_requests:
            await self._log_request(request)

        response = await call_next(request)

        if self.log_responses:
            process_time = time.time() - start_time
            await self._log_response(request, response, process_time)

        return response

    async def _log_request(self, request) -> None:
        correlation_id = getattr(request.state, "correlation_id", None)

        log_data = {
            "event": "request",
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "correlation_id": correlation_id,
        }

        logger.info("Incoming request", extra=log_data)

    async def _log_response(self, request, response, process_time: float) -> None:
        correlation_id = getattr(request.state, "correlation_id", None)

        log_data = {
            "event": "response",
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "correlation_id": correlation_id,
        }

        logger.info("Outgoing response", extra=log_data)
