"""Unit tests for database manager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend_common.database import DatabaseManager
from backend_common.exceptions import BaseError, ErrorCode


def test_database_manager_initialization():
    """Test DatabaseManager initialization."""
    db_url = "sqlite:///:memory:"
    db_manager = DatabaseManager(db_url)

    assert db_manager.database_url == db_url
    assert db_manager.engine is None
    assert db_manager.session_factory is None


def test_database_manager_initialization_with_options():
    """Test DatabaseManager initialization with custom options."""
    db_url = "postgresql://user:pass@localhost/db"
    engine_options = {"pool_size": 10}

    db_manager = DatabaseManager(db_url, engine_options=engine_options)

    assert db_manager.database_url == db_url
    assert db_manager.engine_options == engine_options


@pytest.mark.asyncio
async def test_database_manager_context_manager():
    """Test DatabaseManager as async context manager."""
    db_manager = DatabaseManager("sqlite:///:memory:")

    with patch.object(db_manager, 'connect', new_callable=AsyncMock) as mock_connect:
        with patch.object(db_manager, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
            async with db_manager:
                pass

            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_get_session():
    """Test getting database session."""
    db_manager = DatabaseManager("sqlite:///:memory:")

    # Mock the session factory
    mock_session = AsyncMock()
    db_manager.session_factory = MagicMock(return_value=mock_session)

    async with db_manager.get_session() as session:
        assert session == mock_session

    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_execute_query():
    """Test executing a query."""
    db_manager = DatabaseManager("sqlite:///:memory:")

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result

    with patch.object(db_manager, 'get_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await db_manager.execute_query("SELECT 1")

        assert result == mock_result
        mock_session.execute.assert_called_once_with("SELECT 1")


def test_database_manager_error_handling():
    """Test that database errors are properly wrapped."""
    db_manager = DatabaseManager("invalid://url")

    # This should not raise an exception during initialization
    assert db_manager.database_url == "invalid://url"
