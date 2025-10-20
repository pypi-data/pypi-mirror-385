# src/backend_common/exceptions/base.py
"""
Base exception classes for all backend services.

Provides a foundation for standardized error handling with context
and correlation tracking.
"""

import uuid
from typing import Any, Dict, Optional


class BaseError(Exception):
    """
    Base exception class for all custom exceptions.

    Provides common functionality like error codes, context data,
    and correlation tracking for debugging across services.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize base error with context and tracking.

        Args:
            message: Human-readable error description
            error_code: Machine-readable error identifier
            context: Additional context data for debugging
            correlation_id: Request correlation ID for tracing
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.correlation_id = correlation_id or str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for API responses.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "correlation_id": self.correlation_id,
        }

    def __str__(self) -> str:
        """String representation of the error."""
        return f"{self.error_code}: {self.message}"
