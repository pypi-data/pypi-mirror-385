# tests/unit/test_exceptions.py
"""Unit tests for exception handling."""

import pytest
from backend_common.exceptions import (
    BaseError,
    NotFoundError,
    ValidationError,
    UnauthorizedError,
)


def test_base_error_creation():
    """Test basic error creation and properties."""
    error = BaseError(
        message="Test error",
        error_code="TEST_ERROR",
        context={"key": "value"}
    )

    assert error.message == "Test error"
    assert error.error_code == "TEST_ERROR"
    assert error.context == {"key": "value"}
    assert error.correlation_id is not None


def test_not_found_error():
    """Test NotFoundError specific functionality."""
    error = NotFoundError("User", "123")

    assert "User with id '123' not found" in error.message
    assert error.error_code == "RESOURCE_NOT_FOUND"
    assert error.context["resource_type"] == "User"
    assert error.context["resource_id"] == "123"


def test_validation_error():
    """Test ValidationError specific functionality."""
    error = ValidationError("email", "invalid", "Must be valid email")

    assert "Validation failed for field 'email'" in error.message
    assert error.error_code == "VALIDATION_ERROR"
    assert error.context["field"] == "email"


def test_unauthorized_error():
    """Test UnauthorizedError functionality."""
    error = UnauthorizedError("Invalid token")

    assert "Unauthorized: Invalid token" in error.message
    assert error.error_code == "UNAUTHORIZED"


def test_error_to_dict():
    """Test error serialization to dictionary."""
    error = BaseError("Test", context={"test": True})
    error_dict = error.to_dict()

    assert "error_code" in error_dict
    assert "message" in error_dict
    assert "context" in error_dict
    assert "correlation_id" in error_dict
    assert error_dict["context"]["test"] is True
