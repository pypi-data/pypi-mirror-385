# src/backend_common/database/manager.py
"""
Database manager for connection and session handling.

Provides centralized database connection management with connection pooling,
health monitoring, and automatic reconnection capabilities.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import QueuePool

from ..exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Centralized database connection and session manager.

    Manages PostgreSQL connections with pooling, health checks,
    and automatic session lifecycle management.
    """

    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
    ) -> None:
        """
        Initialize database manager.

        Args:
            database_url: PostgreSQL connection URL
            pool_size: Number of connections to maintain in pool
            max_overflow: Maximum overflow connections
            pool_timeout: Timeout for getting connection from pool
            pool_recycle: Time to recycle connections (seconds)
            echo: Whether to echo SQL statements (for debugging)
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    def create_engine(self) -> AsyncEngine:
        """Create and configure database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=self.echo,
                future=True,
            )

            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            logger.info("Database engine created successfully")

        return self._engine

    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine, creating it if necessary."""
        if self._engine is None:
            return self.create_engine()
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker:
        """Get the session factory, creating it if necessary."""
        if self._session_factory is None:
            self.create_engine()
        return self._session_factory

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session with automatic cleanup.

        Yields:
            AsyncSession: Database session

        Raises:
            ServiceUnavailableError: If database connection fails
        """
        try:
            async with self.session_factory() as session:
                yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise ServiceUnavailableError(
                service_name="database",
                reason=f"Database connection failed: {str(e)}",
            )

    async def create_session(self) -> AsyncSession:
        """
        Create a new database session.

        Note: Caller is responsible for closing the session.

        Returns:
            AsyncSession: New database session
        """
        return self.session_factory()

    async def health_check(self) -> bool:
        """
        Perform database health check.

        Returns:
            bool: True if database is healthy, False otherwise
        """
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False

    async def close(self) -> None:
        """Close database engine and cleanup resources."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database engine closed")

    async def __aenter__(self):
        """Async context manager entry."""
        self.create_engine()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
