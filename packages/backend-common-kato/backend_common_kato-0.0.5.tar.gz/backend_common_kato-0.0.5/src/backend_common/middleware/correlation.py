# src/backend_common/middleware/correlation.py
"""
Correlation ID middleware for request tracing.
"""

import uuid
from typing import Callable, TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle correlation IDs for distributed tracing."""

    def __init__(
        self,
        app,
        header_name: str = "X-Correlation-ID",
        generate_if_missing: bool = True,
    ) -> None:
        super().__init__(app)
        self.header_name = header_name
        self.generate_if_missing = generate_if_missing

    async def dispatch(self, request, call_next: Callable):
        correlation_id = request.headers.get(self.header_name)

        if not correlation_id and self.generate_if_missing:
            correlation_id = str(uuid.uuid4())

        if correlation_id:
            request.state.correlation_id = correlation_id

        response = await call_next(request)

        if correlation_id:
            response.headers[self.header_name] = correlation_id

        return response
