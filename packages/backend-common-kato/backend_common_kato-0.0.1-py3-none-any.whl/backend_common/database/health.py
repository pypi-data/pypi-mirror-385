# src/backend_common/database/health.py
"""
Database health check utilities.

Provides health monitoring capabilities for database connections
and performance metrics collection.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.health import HealthResponse, HealthStatus
from .manager import DatabaseManager

logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """
    Database health checker for monitoring database connectivity and performance.

    Provides comprehensive health checks including connection tests,
    query performance monitoring, and connection pool status.
    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize database health checker.

        Args:
            db_manager: Database manager instance to monitor
        """
        self.db_manager = db_manager

    async def check_connection(self) -> HealthResponse:
        """
        Check basic database connectivity.

        Returns:
            HealthResponse: Health status of database connection
        """
        start_time = datetime.utcnow()

        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    text("SELECT 1 as health_check")
                )
                health_value = result.scalar()

                if health_value == 1:
                    status = HealthStatus.HEALTHY
                    message = "Database connection successful"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = "Unexpected health check result"

        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = f"Database connection failed: {str(e)}"
            logger.warning(f"Database health check failed: {e}")

        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds()

        return HealthResponse(
            service_name="database",
            status=status,
            message=message,
            timestamp=end_time,
            response_time=response_time,
        )

    async def check_performance(self) -> Dict[str, Any]:
        """
        Check database performance metrics.

        Returns:
            Dictionary containing performance metrics
        """
        try:
            async with self.db_manager.get_session() as session:
                # Check active connections
                connections_result = await session.execute(
                    text(
                        "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                    )
                )
                active_connections = connections_result.scalar()

                # Check database size
                size_result = await session.execute(
                    text("SELECT pg_database_size(current_database())")
                )
                db_size_bytes = size_result.scalar()

                return {
                    "active_connections": active_connections,
                    "database_size_bytes": db_size_bytes,
                    "database_size_mb": (
                        round(db_size_bytes / (1024 * 1024), 2)
                        if db_size_bytes
                        else 0
                    ),
                }

        except Exception as e:
            logger.warning(f"Performance check failed: {e}")
            return {
                "active_connections": None,
                "database_size_bytes": None,
                "database_size_mb": None,
                "error": str(e),
            }
