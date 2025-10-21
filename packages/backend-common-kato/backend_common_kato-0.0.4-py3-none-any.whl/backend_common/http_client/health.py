# src/backend_common/http/health.py
"""
Health check utilities for service monitoring.

Provides standardized health check endpoints and monitoring
capabilities for service discovery and load balancing.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..models.health import HealthResponse, HealthStatus
from .client import HTTPClient

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Service health checker for monitoring dependencies.

    Provides health checking capabilities for external services
    and dependencies with configurable check intervals.
    """

    def __init__(
        self,
        services: Dict[str, str],
        check_interval: float = 30.0,
        timeout: float = 5.0,
    ) -> None:
        """
        Initialize health checker.

        Args:
            services: Dictionary of service_name -> health_endpoint_url
            check_interval: Interval between health checks in seconds
            timeout: Timeout for health check requests
        """
        self.services = services
        self.check_interval = check_interval
        self.timeout = timeout
        self.health_status: Dict[str, HealthResponse] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def check_service_health(
        self, service_name: str, url: str
    ) -> HealthResponse:
        """
        Check health of a single service.

        Args:
            service_name: Name of the service to check
            url: Health check endpoint URL

        Returns:
            HealthResponse: Health status of the service
        """
        start_time = datetime.utcnow()

        try:
            async with HTTPClient(timeout=self.timeout) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    status = HealthStatus.HEALTHY
                    message = "Service is healthy"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"Service returned status {response.status_code}"

        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = f"Health check failed: {str(e)}"
            logger.warning(f"Health check failed for {service_name}: {e}")

        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds()

        return HealthResponse(
            service_name=service_name,
            status=status,
            message=message,
            timestamp=end_time,
            response_time=response_time,
        )

    async def check_all_services(self) -> Dict[str, HealthResponse]:
        """
        Check health of all configured services.

        Returns:
            Dictionary of service_name -> HealthResponse
        """
        tasks = [
            self.check_service_health(name, url)
            for name, url in self.services.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        health_results = {}
        for i, result in enumerate(results):
            service_name = list(self.services.keys())[i]

            if isinstance(result, Exception):
                health_results[service_name] = HealthResponse(
                    service_name=service_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check exception: {str(result)}",
                    timestamp=datetime.utcnow(),
                    response_time=self.timeout,
                )
            else:
                health_results[service_name] = result

        self.health_status = health_results
        return health_results

    async def start_monitoring(self) -> None:
        """Start continuous health monitoring."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Health monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Internal monitoring loop."""
        while self._running:
            try:
                await self.check_all_services()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    def get_service_status(
        self, service_name: str
    ) -> Optional[HealthResponse]:
        """Get current health status of a specific service."""
        return self.health_status.get(service_name)

    def get_all_status(self) -> Dict[str, HealthResponse]:
        """Get current health status of all services."""
        return self.health_status.copy()

    def is_service_healthy(self, service_name: str) -> bool:
        """Check if a specific service is currently healthy."""
        status = self.get_service_status(service_name)
        return status is not None and status.status == HealthStatus.HEALTHY
