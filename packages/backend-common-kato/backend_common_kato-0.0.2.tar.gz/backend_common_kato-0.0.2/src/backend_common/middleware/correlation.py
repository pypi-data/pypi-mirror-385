# src/backend_common/middleware/correlation.py
"""
Correlation ID middleware for request tracing.

Automatically generates or extracts correlation IDs from requests
to enable distributed tracing across microservices.
"""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle correlation IDs for distributed tracing.

    Automatically extracts correlation IDs from incoming requests or generates
    new ones, and ensures they're propagated to downstream services.
    """

    def __init__(
        self,
        app,
        header_name: str = "X-Correlation-ID",
        generate_if_missing: bool = True,
    ) -> None:
        """
        Initialize correlation middleware.

        Args:
            app: FastAPI application instance
            header_name: HTTP header name for correlation ID
            generate_if_missing: Whether to generate ID if not present
        """
        super().__init__(app)
        self.header_name = header_name
        self.generate_if_missing = generate_if_missing

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request and add correlation ID handling.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain

        Returns:
            Response: HTTP response with correlation ID header
        """
        # Extract or generate correlation ID
        correlation_id = request.headers.get(self.header_name)

        if not correlation_id and self.generate_if_missing:
            correlation_id = str(uuid.uuid4())

        if correlation_id:
            # Store correlation ID in request state for access in endpoints
            request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        if correlation_id:
            response.headers[self.header_name] = correlation_id

        return response
