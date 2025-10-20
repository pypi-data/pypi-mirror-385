# src/backend_common/utils/__init__.py
"""
Utility functions and helper classes for backend services.

Provides common utilities for time handling, validation,
and other frequently used operations across services.
"""

from .time import (
    utc_now,
    to_utc,
    from_timestamp,
    to_timestamp,
    format_datetime,
    parse_datetime,
    add_hours,
    add_days,
    get_start_of_day,
    get_end_of_day,
    Timer,
)
from .validation import (
    validate_email_address,
    validate_password_strength,
    validate_username,
    validate_phone_number,
    validate_required_fields,
    validate_string_length,
    validate_numeric_range,
)

__all__ = [
    # Time utilities
    "utc_now",
    "to_utc",
    "from_timestamp",
    "to_timestamp",
    "format_datetime",
    "parse_datetime",
    "add_hours",
    "add_days",
    "get_start_of_day",
    "get_end_of_day",
    "Timer",
    # Validation utilities
    "validate_email_address",
    "validate_password_strength",
    "validate_username",
    "validate_phone_number",
    "validate_required_fields",
    "validate_string_length",
    "validate_numeric_range",
]
