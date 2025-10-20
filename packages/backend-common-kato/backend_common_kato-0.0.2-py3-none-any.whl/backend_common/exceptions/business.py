# src/backend_common/exceptions/business.py
"""
Business logic exception classes.
"""

from typing import Any, Dict, Optional

from .base import BaseError, ErrorCode


class BusinessLogicError(BaseError):
    """Exception raised for business rule violations."""

    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code=ErrorCode.BUSINESS_RULE_VIOLATION,
            status_code=422,
            context=context,
        )
        self.rule = rule

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.rule:
            result["rule"] = self.rule
        return result


class AlreadyExistsError(BaseError):
    """Exception raised when trying to create a resource that already exists."""

    def __init__(
        self,
        resource: str,
        identifier: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        message = f"{resource} already exists"
        if identifier:
            message += f" with identifier: {identifier}"

        super().__init__(
            message=message,
            error_code=ErrorCode.ALREADY_EXISTS,
            status_code=409,
            context=context,
        )


class ExternalServiceError(BaseError):
    """Exception raised when an external service call fails."""

    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        status_code: int = 502,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        full_message = f"{service_name}: {message}"
        super().__init__(
            message=full_message,
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=status_code,
            context=context,
        )
        self.service_name = service_name
