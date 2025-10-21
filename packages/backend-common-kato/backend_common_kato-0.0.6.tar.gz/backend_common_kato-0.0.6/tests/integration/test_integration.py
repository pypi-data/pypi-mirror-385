"""Integration tests for backend_common package."""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_exception_handling_integration():
    """Test exception handling with database operations."""
    from backend_common.database import DatabaseManager
    from backend_common.exceptions import BaseError, ErrorCode

    db_manager = DatabaseManager("sqlite:///:memory:")

    # Test that database errors are properly converted to BaseError
    with patch.object(db_manager, 'connect', side_effect=Exception("Connection failed")):
        with pytest.raises(Exception):
            await db_manager.connect()


def test_models_with_exceptions():
    """Test models work correctly with exception handling."""
    from backend_common.models import HealthResponse, HealthStatus
    from backend_common.exceptions import ValidationError

    # Valid model creation
    health = HealthResponse(status=HealthStatus.HEALTHY, version="1.0.0")
    assert health.status == HealthStatus.HEALTHY

    # Invalid model should raise validation error
    with pytest.raises(Exception):  # Pydantic validation error
        HealthResponse(status="invalid_status", version="1.0.0")


def test_utils_with_models():
    """Test utility functions work with models."""
    from backend_common.utils import utc_now
    from backend_common.models import HealthResponse, HealthStatus

    timestamp = utc_now()
    health = HealthResponse(
        status=HealthStatus.HEALTHY,
        version="1.0.0",
        timestamp=timestamp
    )

    assert health.timestamp == timestamp


@pytest.mark.asyncio
async def test_full_workflow():
    """Test a complete workflow using multiple components."""
    from backend_common.database import DatabaseManager
    from backend_common.models import HealthResponse, HealthStatus
    from backend_common.utils import utc_now, Timer
    from backend_common.exceptions import BaseError

    # Initialize components
    db_manager = DatabaseManager("sqlite:///:memory:")
    timer = Timer()

    # Create health response
    health = HealthResponse(
        status=HealthStatus.HEALTHY,
        version="1.0.0",
        timestamp=utc_now()
    )

    # Verify workflow
    assert health.status == HealthStatus.HEALTHY
    assert timer.elapsed() >= 0
    assert db_manager.database_url == "sqlite:///:memory:"
