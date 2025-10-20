"""Database health check functionality."""

import time
from sqlalchemy import text

from ..models import ServiceHealth, HealthStatus
from .session import get_database_manager


async def check_database_health() -> ServiceHealth:
    """
    Check database connectivity and performance.

    Returns:
        ServiceHealth: Database health status
    """
    start_time = time.time()

    try:
        db_manager = get_database_manager()

        async with db_manager.get_session() as session:
            # Simple connectivity test
            await session.execute(text("SELECT 1"))

        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Determine status based on response time
        if response_time < 100:
            status = HealthStatus.HEALTHY
            message = "Database is healthy"
        elif response_time < 500:
            status = HealthStatus.DEGRADED
            message = f"Database response slow ({response_time:.1f}ms)"
        else:
            status = HealthStatus.UNHEALTHY
            message = f"Database response very slow ({response_time:.1f}ms)"

        return ServiceHealth(
            name="database",
            status=status,
            message=message,
            response_time_ms=response_time,
        )

    except Exception as e:
        response_time = (time.time() - start_time) * 1000

        return ServiceHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"Database connection failed: {str(e)}",
            response_time_ms=response_time,
        )


async def check_database_connection_pool() -> ServiceHealth:
    """
    Check database connection pool status.

    Returns:
        ServiceHealth: Connection pool health status
    """
    try:
        db_manager = get_database_manager()
        engine = db_manager.engine

        pool = engine.pool

        # Calculate pool utilization safely
        total_connections = pool.size() + pool.overflow()
        if total_connections > 0:
            utilization = pool.checkedout() / total_connections
        else:
            utilization = 0

        if utilization < 0.7:
            status = HealthStatus.HEALTHY
            message = f"Connection pool healthy (utilization: {utilization:.1%})"
        elif utilization < 0.9:
            status = HealthStatus.DEGRADED
            message = f"Connection pool under pressure (utilization: {utilization:.1%})"
        else:
            status = HealthStatus.UNHEALTHY
            message = f"Connection pool exhausted (utilization: {utilization:.1%})"

        return ServiceHealth(
            name="database_pool",
            status=status,
            message=message,
        )

    except Exception as e:
        return ServiceHealth(
            name="database_pool",
            status=HealthStatus.UNHEALTHY,
            message=f"Failed to check connection pool: {str(e)}",
        )
