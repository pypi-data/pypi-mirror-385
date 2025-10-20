# src/backend_common/exceptions/business.py
"""
Business logic exception classes.

These exceptions represent domain-specific errors that occur during
normal business operations.
"""

from typing import Any, Dict, Optional

from .base import BaseError


class BusinessLogicError(BaseError):
    """Base class for business logic related errors."""

    pass


class NotFoundError(BusinessLogicError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize not found error.

        Args:
            resource_type: Type of resource that was not found
            resource_id: Identifier of the missing resource
            context: Additional context data
            correlation_id: Request correlation ID
        """
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            context=context
            or {"resource_type": resource_type, "resource_id": resource_id},
            correlation_id=correlation_id,
        )


class ValidationError(BusinessLogicError):
    """Raised when input validation fails."""

    def __init__(
        self,
        field: str,
        value: Any,
        constraint: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize validation error.

        Args:
            field: Name of the field that failed validation
            value: The invalid value
            constraint: Description of the validation constraint
            context: Additional context data
            correlation_id: Request correlation ID
        """
        message = f"Validation failed for field '{field}': {constraint}"
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context
            or {
                "field": field,
                "value": str(value),
                "constraint": constraint,
            },
            correlation_id=correlation_id,
        )


class ConflictError(BusinessLogicError):
    """Raised when a resource conflict occurs."""

    def __init__(
        self,
        resource_type: str,
        conflict_reason: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize conflict error.

        Args:
            resource_type: Type of resource in conflict
            conflict_reason: Reason for the conflict
            context: Additional context data
            correlation_id: Request correlation ID
        """
        message = f"Conflict with {resource_type}: {conflict_reason}"
        super().__init__(
            message=message,
            error_code="RESOURCE_CONFLICT",
            context=context
            or {
                "resource_type": resource_type,
                "conflict_reason": conflict_reason,
            },
            correlation_id=correlation_id,
        )


class ForbiddenError(BusinessLogicError):
    """Raised when access to a resource is forbidden."""

    def __init__(
        self,
        resource: str,
        reason: str = "Insufficient permissions",
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Initialize forbidden error.

        Args:
            resource: Resource that access was denied to
            reason: Reason for denial
            context: Additional context data
            correlation_id: Request correlation ID
        """
        message = f"Access denied to {resource}: {reason}"
        super().__init__(
            message=message,
            error_code="ACCESS_FORBIDDEN",
            context=context or {"resource": resource, "reason": reason},
            correlation_id=correlation_id,
        )
