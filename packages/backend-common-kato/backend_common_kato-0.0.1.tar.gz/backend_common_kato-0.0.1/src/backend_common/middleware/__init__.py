# src/backend_common/middleware/__init__.py
"""
Reusable middleware components for FastAPI applications.

Provides standardized middleware for logging, correlation IDs,
authentication, and request/response processing.
"""

from .auth import AuthMiddleware
from .correlation import CorrelationMiddleware
from .logging import LoggingMiddleware

__all__ = [
    "CorrelationMiddleware",
    "LoggingMiddleware",
    "AuthMiddleware",
]
