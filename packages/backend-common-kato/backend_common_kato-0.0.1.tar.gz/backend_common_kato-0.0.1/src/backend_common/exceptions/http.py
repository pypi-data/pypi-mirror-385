# src/backend_common/exceptions/http.py
"""
HTTP-specific exception classes.

These exceptions represent errors that occur during HTTP communication
and service interactions.
"""

from typing import Any, Dict, Optional

from .base import BaseError


class UnauthorizedError(BaseError):
    """Raised when authentication fails or is missing."""

    def __init__(
        self,
        reason: str = "Authentication required",
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize unauthorized error.

        Args:
            reason: Reason for authentication failure
            context: Additional context data
            correlation_id: Request correlation ID
        """
        super().__init__(
            message=f"Unauthorized: {reason}",
            error_code="UNAUTHORIZED",
            context=context or {"reason": reason},
            correlation_id=correlation_id,
        )


class BadRequestError(BaseError):
    """Raised when the request is malformed or invalid."""

    def __init__(
        self,
        details: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize bad request error.

        Args:
            details: Details about what makes the request invalid
            context: Additional context data
            correlation_id: Request correlation ID
        """
        super().__init__(
            message=f"Bad request: {details}",
            error_code="BAD_REQUEST",
            context=context or {"details": details},
            correlation_id=correlation_id,
        )


class ServiceUnavailableError(BaseError):
    """Raised when a required service is unavailable."""

    def __init__(
        self,
        service_name: str,
        reason: str = "Service temporarily unavailable",
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize service unavailable error.

        Args:
            service_name: Name of the unavailable service
            reason: Reason for unavailability
            context: Additional context data
            correlation_id: Request correlation ID
        """
        super().__init__(
            message=f"Service '{service_name}' unavailable: {reason}",
            error_code="SERVICE_UNAVAILABLE",
            context=context
            or {"service_name": service_name, "reason": reason},
            correlation_id=correlation_id,
        )


class TimeoutError(BaseError):
    """Raised when an operation times out."""

    def __init__(
        self,
        operation: str,
        timeout_seconds: float,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize timeout error.

        Args:
            operation: Description of the operation that timed out
            timeout_seconds: Timeout duration in seconds
            context: Additional context data
            correlation_id: Request correlation ID
        """
        super().__init__(
            message=f"Operation '{operation}' timed out after {timeout_seconds}s",
            error_code="OPERATION_TIMEOUT",
            context=context
            or {
                "operation": operation,
                "timeout_seconds": timeout_seconds,
            },
            correlation_id=correlation_id,
        )
