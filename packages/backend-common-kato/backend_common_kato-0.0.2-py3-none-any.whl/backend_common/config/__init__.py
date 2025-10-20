# src/backend_common/config/__init__.py
"""
Configuration module for backend services.

Provides standardized configuration management using Pydantic settings
with environment variable support and validation.
"""

from .base import BaseConfig, settings

__all__ = [
    "BaseConfig",
    "settings",
]
