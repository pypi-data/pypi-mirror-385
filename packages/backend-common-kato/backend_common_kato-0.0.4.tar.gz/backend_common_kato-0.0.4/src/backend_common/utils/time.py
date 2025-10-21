# src/backend_common/utils/time.py
"""
Time utilities for backend applications.

Provides standardized time operations, timezone handling,
and formatting utilities across all backend services.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import time


def utc_now() -> datetime:
    """Get current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)


def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC timezone."""
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def from_timestamp(timestamp: Union[int, float]) -> datetime:
    """Convert Unix timestamp to UTC datetime."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def to_timestamp(dt: datetime) -> float:
    """Convert datetime to Unix timestamp."""
    return dt.timestamp()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime string to datetime object."""
    parsed = datetime.strptime(dt_str, format_str)
    return parsed.replace(tzinfo=timezone.utc)


def add_hours(dt: datetime, hours: int) -> datetime:
    """Add hours to datetime."""
    return dt + timedelta(hours=hours)


def add_days(dt: datetime, days: int) -> datetime:
    """Add days to datetime."""
    return dt + timedelta(days=days)


def get_start_of_day(dt: Optional[datetime] = None) -> datetime:
    """Get start of day (00:00:00) for given datetime or current UTC time."""
    if dt is None:
        dt = utc_now()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day(dt: Optional[datetime] = None) -> datetime:
    """Get end of day (23:59:59) for given datetime or current UTC time."""
    if dt is None:
        dt = utc_now()
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


class Timer:
    """Simple timer utility for measuring execution time."""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self) -> 'Timer':
        """Start the timer."""
        self.start_time = time.perf_counter()
        return self

    def stop(self) -> float:
        """Stop the timer and return elapsed time in seconds."""
        if self.start_time is None:
            raise RuntimeError("Timer not started")

        self.end_time = time.perf_counter()
        return self.elapsed_seconds

    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0

        end = self.end_time or time.perf_counter()
        return end - self.start_time

    @property
    def elapsed_milliseconds(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed_seconds * 1000

    def __enter__(self) -> 'Timer':
        """Context manager entry."""
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
