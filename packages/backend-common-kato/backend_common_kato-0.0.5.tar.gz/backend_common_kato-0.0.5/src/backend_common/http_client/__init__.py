# src/backend_common/http/__init__.py
"""
HTTP client utilities for service communication.

Provides standardized HTTP clients with retry logic, timeout handling,
and service discovery capabilities.
"""

from .client import HTTPClient, ServiceClient
from .health import HealthChecker

__all__ = [
    "HTTPClient",
    "ServiceClient",
    "HealthChecker",
]
