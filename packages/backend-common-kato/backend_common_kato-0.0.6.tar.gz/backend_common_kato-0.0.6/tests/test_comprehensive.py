"""
Comprehensive test for backend_common package.
"""

import pytest
import asyncio
from datetime import datetime


def test_main_imports():
    """Test that all main components can be imported."""
    from backend_common import (
        BaseError,
        ValidationError,
        NotFoundError,
        BusinessLogicError,
        BaseModel,
        HealthResponse,
        HealthStatus,
        PaginationParams,
        PaginatedResponse,
        utc_now,
        Timer,
        validate_email_address,
        validate_username,
    )
    assert True


def test_exception_system():
    """Test the exception handling system."""
    from backend_common.exceptions import (
        BaseError,
        ValidationError,
        NotFoundError,
        BusinessLogicError,
        ErrorCode
    )

    error = BaseError(
        message="Test error",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        context={"test": "data"}
    )

    assert error.message == "Test error"
    assert error.error_code == ErrorCode.INTERNAL_SERVER_ERROR
    assert error.context == {"test": "data"}
    assert error.status_code == 500


def test_models():
    """Test Pydantic models."""
    from backend_common.models import BaseModel, HealthResponse, HealthStatus

    health = HealthResponse(status=HealthStatus.HEALTHY, version="1.0.0")
    assert health.status == HealthStatus.HEALTHY
    assert health.version == "1.0.0"


def test_utils():
    """Test utility functions."""
    from backend_common.utils import utc_now, validate_email_address, validate_username

    now = utc_now()
    assert isinstance(now, datetime)

    assert validate_email_address("test@example.com") is True
    assert validate_email_address("invalid-email") is False

    assert validate_username("valid_user123") is True
    assert validate_username("") is False


@pytest.mark.asyncio
async def test_database_manager():
    """Test database manager initialization."""
    from backend_common.database import DatabaseManager

    db_manager = DatabaseManager("sqlite:///:memory:")
    assert db_manager.database_url == "sqlite:///:memory:"


def test_fastapi_optional_imports():
    """Test that FastAPI components are optional."""
    from backend_common import get_fastapi_handlers, get_auth_dependencies, get_middleware

    # These should raise ImportError if FastAPI is not installed
    with pytest.raises(ImportError):
        get_fastapi_handlers()

    with pytest.raises(ImportError):
        get_auth_dependencies()

    with pytest.raises(ImportError):
        get_middleware()


if __name__ == "__main__":
    pytest.main([__file__])
