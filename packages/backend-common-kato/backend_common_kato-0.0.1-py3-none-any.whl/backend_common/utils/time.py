# src/backend_common/utils/time.py
"""
Time utility functions for consistent datetime handling.

Provides standardized time operations, timezone handling,
and formatting utilities across all backend services.
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Union


class TimeUtils:
    """
    Utility class for time and datetime operations.

    Provides consistent datetime handling with timezone awareness,
    formatting, and common time calculations.
    """

    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC datetime with timezone info."""
        return datetime.now(timezone.utc)

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """Convert datetime to UTC timezone."""
        if dt.tzinfo is None:
            # Assume naive datetime is in UTC
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def from_timestamp(timestamp: Union[int, float]) -> datetime:
        """Convert Unix timestamp to UTC datetime."""
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    @staticmethod
    def to_timestamp(dt: datetime) -> float:
        """Convert datetime to Unix timestamp."""
        return dt.timestamp()

    @staticmethod
    def iso_format(dt: datetime) -> str:
        """Format datetime as ISO 8601 string."""
        return dt.isoformat()

    @staticmethod
    def from_iso_format(iso_string: str) -> datetime:
        """Parse ISO 8601 string to datetime."""
        return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))

    @staticmethod
    def add_seconds(dt: datetime, seconds: int) -> datetime:
        """Add seconds to datetime."""
        return dt + timedelta(seconds=seconds)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """Add minutes to datetime."""
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """Add hours to datetime."""
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """Add days to datetime."""
        return dt + timedelta(days=days)

    @staticmethod
    def time_ago(dt: datetime) -> str:
        """Get human-readable time difference from now."""
        now = TimeUtils.utc_now()
        diff = now - TimeUtils.to_utc(dt)

        if diff.total_seconds() < 60:
            return "just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(diff.total_seconds() / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"

    @staticmethod
    def is_expired(dt: datetime, ttl_seconds: int) -> bool:
        """Check if datetime is expired based on TTL."""
        expiry_time = dt + timedelta(seconds=ttl_seconds)
        return TimeUtils.utc_now() > TimeUtils.to_utc(expiry_time)
