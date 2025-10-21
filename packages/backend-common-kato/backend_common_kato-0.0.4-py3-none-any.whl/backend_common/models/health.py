# src/backend_common/models/health.py
"""
Health check models for service monitoring.

Provides standardized models for health status reporting
and service monitoring across all backend services.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import Field

from .base import BaseModel


class HealthStatus(str, Enum):
    """Health check status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ServiceHealth(BaseModel):
    """Health status for a service component."""

    name: str = Field(description="Name of the service component")
    status: HealthStatus = Field(description="Current health status")
    message: Optional[str] = Field(default=None, description="Additional status information")
    response_time_ms: Optional[float] = Field(default=None, description="Response time in milliseconds")
    last_checked: datetime = Field(default_factory=datetime.utcnow, description="Last health check time")


class HealthResponse(BaseModel):
    """Complete health check response."""

    status: HealthStatus = Field(description="Overall system health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: Optional[str] = Field(default=None, description="Application version")
    uptime_seconds: Optional[float] = Field(default=None, description="System uptime in seconds")
    services: List[ServiceHealth] = Field(default_factory=list, description="Individual service health statuses")

    @classmethod
    def create_healthy(cls, version: str = None, uptime_seconds: float = None) -> "HealthResponse":
        """Create a healthy response."""
        return cls(
            status=HealthStatus.HEALTHY,
            version=version,
            uptime_seconds=uptime_seconds,
        )

    @classmethod
    def create_unhealthy(cls, message: str, version: str = None) -> "HealthResponse":
        """Create an unhealthy response."""
        return cls(
            status=HealthStatus.UNHEALTHY,
            version=version,
            services=[ServiceHealth(name="system", status=HealthStatus.UNHEALTHY, message=message)],
        )
