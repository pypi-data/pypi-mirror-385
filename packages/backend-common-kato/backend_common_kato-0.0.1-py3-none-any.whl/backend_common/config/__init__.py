# src/backend_common/config/__init__.py
"""
Configuration utilities for backend services.

Provides standardized configuration management using Pydantic settings
with environment variable support and validation.
"""

from .base import BaseConfig
from .service import ServiceConfig

__all__ = [
    "BaseConfig",
    "ServiceConfig",
]
