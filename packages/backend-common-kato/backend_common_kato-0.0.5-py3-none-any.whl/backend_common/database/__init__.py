# src/backend_common/database/__init__.py
"""
Database module for backend common package.

Provides standardized database connection handling, session management,
and health checks for PostgreSQL databases using SQLAlchemy.
"""

from .manager import DatabaseManager

__all__ = [
    "DatabaseManager",
]
