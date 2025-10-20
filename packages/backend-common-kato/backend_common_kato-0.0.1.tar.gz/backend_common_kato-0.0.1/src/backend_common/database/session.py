# src/backend_common/database/session.py
"""
Database session utilities and FastAPI dependencies.

Provides FastAPI dependencies for database session injection
and session lifecycle management.
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .manager import DatabaseManager

# Global database manager instance (should be configured by the application)
_db_manager: Optional[DatabaseManager] = None


def set_database_manager(db_manager: DatabaseManager) -> None:
    """Set the global database manager instance."""
    global _db_manager
    _db_manager = db_manager


def get_database_manager() -> DatabaseManager:
    """Get the configured database manager."""
    if _db_manager is None:
        raise RuntimeError(
            "Database manager not configured. Call set_database_manager() first."
        )
    return _db_manager


async def create_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create database session for FastAPI dependency injection.

    Yields:
        AsyncSession: Database session with automatic cleanup
    """
    db_manager = get_database_manager()
    async with db_manager.get_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# FastAPI dependency for database session injection
async def get_db_session(
    session: AsyncSession = Depends(create_db_session),
) -> AsyncSession:
    """
    FastAPI dependency to inject database session.

    Args:
        session: Database session from dependency

    Returns:
        AsyncSession: Database session
    """
    return session
