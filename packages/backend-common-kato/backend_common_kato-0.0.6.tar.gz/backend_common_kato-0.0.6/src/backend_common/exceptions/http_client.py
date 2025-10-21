# src/backend_common/exceptions/http.py
"""HTTP-specific exception classes."""

from typing import Any, Dict, Optional
from .base import BaseError, ErrorCode


class HTTPError(BaseError):
    """Base class for HTTP-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            context=context,
        )
        self.headers = headers or {}


class BadRequestError(HTTPError):
    """Exception for 400 Bad Request errors."""

    def __init__(
        self,
        message: str = "Bad request",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code=ErrorCode.VALIDATION_ERROR,
            context=context,
        )


class RateLimitExceededError(HTTPError):
    """Exception for rate limit exceeded errors."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)

        super().__init__(
            message=message,
            status_code=429,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            headers=headers,
            context=context,
        )
        self.retry_after = retry_after
