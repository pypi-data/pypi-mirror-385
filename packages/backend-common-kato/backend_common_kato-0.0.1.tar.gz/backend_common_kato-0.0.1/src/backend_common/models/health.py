# src/backend_common/models/health.py
"""
Health check models for service monitoring.

Provides standardized models for health status reporting
and service monitoring across all backend services.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from .base import BaseModel


class HealthStatus(str, Enum):
    """Enumeration of possible health statuses."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class HealthResponse(BaseModel):
    """
    Standardized health check response model.

    Used for both service health endpoints and dependency monitoring.
    """

    service_name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time: Optional[float] = None
    details: Optional[dict] = None

    @classmethod
    def healthy(
        cls,
        service_name: str,
        message: str = "Service is healthy",
        response_time: Optional[float] = None,
    ) -> "HealthResponse":
        """Create a healthy status response."""
        return cls(
            service_name=service_name,
            status=HealthStatus.HEALTHY,
            message=message,
            timestamp=datetime.utcnow(),
            response_time=response_time,
        )

    @classmethod
    def unhealthy(
        cls,
        service_name: str,
        message: str,
        response_time: Optional[float] = None,
        details: Optional[dict] = None,
    ) -> "HealthResponse":
        """Create an unhealthy status response."""
        return cls(
            service_name=service_name,
            status=HealthStatus.UNHEALTHY,
            message=message,
            timestamp=datetime.utcnow(),
            response_time=response_time,
            details=details,
        )
