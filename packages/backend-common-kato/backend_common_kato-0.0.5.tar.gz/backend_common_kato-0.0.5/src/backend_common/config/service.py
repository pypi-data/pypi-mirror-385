# src/backend_common/config/service.py
"""
Service-specific configuration extensions.

Provides specialized configuration classes for different types
of backend services with service-specific settings.
"""

from typing import Dict, Optional

from pydantic import Field

from .base import BaseConfig


class ServiceConfig(BaseConfig):
    """
    Extended configuration for microservices.

    Adds service discovery, inter-service communication,
    and monitoring configuration on top of base settings.
    """

    # Service discovery
    service_discovery_url: Optional[str] = Field(
        default=None, description="Service discovery endpoint URL"
    )
    service_registry_ttl: int = Field(
        default=30, description="Service registry TTL in seconds"
    )

    # Inter-service communication
    service_endpoints: Dict[str, str] = Field(
        default_factory=dict, description="Other service endpoints"
    )
    service_auth_enabled: bool = Field(
        default=True, description="Enable service-to-service authentication"
    )

    # Monitoring and observability
    metrics_enabled: bool = Field(
        default=True, description="Enable metrics collection"
    )
    metrics_port: int = Field(default=9090, description="Metrics server port")
    tracing_enabled: bool = Field(
        default=True, description="Enable distributed tracing"
    )
    tracing_endpoint: Optional[str] = Field(
        default=None, description="Tracing collector endpoint"
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(
        default=True, description="Enable rate limiting"
    )
    rate_limit_requests_per_minute: int = Field(
        default=60, description="Rate limit requests per minute"
    )

    # Circuit breaker
    circuit_breaker_enabled: bool = Field(
        default=True, description="Enable circuit breaker"
    )
    circuit_breaker_failure_threshold: int = Field(
        default=5, description="Circuit breaker failure threshold"
    )
    circuit_breaker_timeout: float = Field(
        default=60.0, description="Circuit breaker timeout in seconds"
    )

    # Cache configuration
    cache_enabled: bool = Field(default=False, description="Enable caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    redis_url: Optional[str] = Field(
        default=None, description="Redis connection URL"
    )

    def get_service_endpoint(self, service_name: str) -> Optional[str]:
        """Get endpoint URL for a specific service."""
        return self.service_endpoints.get(service_name)

    def add_service_endpoint(self, service_name: str, endpoint: str) -> None:
        """Add or update service endpoint."""
        self.service_endpoints[service_name] = endpoint
