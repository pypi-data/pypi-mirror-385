# tests/unit/test_exceptions.py
"""Unit tests for exception handling."""

import pytest
from backend_common.exceptions import (
    BaseError,
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    BusinessLogicError,
    ErrorCode,
)


def test_base_error_creation():
    """Test basic error creation and properties."""
    error = BaseError(
        message="Test error",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        context={"key": "value"}
    )

    assert error.message == "Test error"
    assert error.error_code == ErrorCode.INTERNAL_SERVER_ERROR
    assert error.context == {"key": "value"}
    assert error.status_code == 500


def test_not_found_error():
    """Test NotFoundError specific functionality."""
    error = NotFoundError("User", "123")

    assert "User with id '123' not found" in error.message
    assert error.error_code == ErrorCode.RESOURCE_NOT_FOUND
    assert error.context["resource_type"] == "User"
    assert error.context["resource_id"] == "123"
    assert error.status_code == 404


def test_validation_error():
    """Test ValidationError specific functionality."""
    error = ValidationError("email", "invalid", "Must be valid email")

    assert "Validation failed for field 'email'" in error.message
    assert error.error_code == ErrorCode.VALIDATION_ERROR
    assert error.context["field"] == "email"
    assert error.status_code == 400


def test_unauthorized_error():
    """Test UnauthorizedError functionality."""
    error = UnauthorizedError("Invalid token")

    assert "Unauthorized: Invalid token" in error.message
    assert error.error_code == ErrorCode.UNAUTHORIZED
    assert error.status_code == 401


def test_business_logic_error():
    """Test BusinessLogicError functionality."""
    error = BusinessLogicError("Cannot delete active user")

    assert error.message == "Cannot delete active user"
    assert error.error_code == ErrorCode.BUSINESS_LOGIC_ERROR
    assert error.status_code == 400


def test_error_to_dict():
    """Test error serialization to dictionary."""
    error = BaseError(
        message="Test error",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        context={"test": "data"}
    )

    error_dict = error.to_dict()
    assert error_dict["message"] == "Test error"
    assert error_dict["error_code"] == ErrorCode.INTERNAL_SERVER_ERROR.value
    assert error_dict["status_code"] == 500
    assert error_dict["context"] == {"test": "data"}
