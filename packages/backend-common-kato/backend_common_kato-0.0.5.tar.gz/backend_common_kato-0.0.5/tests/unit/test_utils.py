"""Unit tests for utility functions."""

import pytest
from datetime import datetime, timezone
from backend_common.utils import (
    utc_now,
    Timer,
    validate_email_address,
    validate_username,
)


def test_utc_now():
    """Test utc_now function returns UTC datetime."""
    now = utc_now()
    assert isinstance(now, datetime)
    assert now.tzinfo == timezone.utc


def test_timer():
    """Test Timer utility class."""
    import time

    timer = Timer()
    time.sleep(0.1)  # Sleep for 100ms
    elapsed = timer.elapsed()

    assert elapsed >= 0.1
    assert elapsed < 0.2  # Should be close to 100ms


def test_validate_email_address():
    """Test email validation function."""
    # Valid emails
    assert validate_email_address("test@example.com") is True
    assert validate_email_address("user.name@domain.org") is True
    assert validate_email_address("test+tag@example.co.uk") is True

    # Invalid emails
    assert validate_email_address("invalid-email") is False
    assert validate_email_address("@example.com") is False
    assert validate_email_address("test@") is False
    assert validate_email_address("") is False
    assert validate_email_address(None) is False


def test_validate_username():
    """Test username validation function."""
    # Valid usernames
    assert validate_username("user123") is True
    assert validate_username("test_user") is True
    assert validate_username("User-Name") is True

    # Invalid usernames
    assert validate_username("") is False
    assert validate_username("ab") is False  # Too short
    assert validate_username("a" * 51) is False  # Too long
    assert validate_username("user@name") is False  # Invalid character
    assert validate_username(None) is False


def test_timer_string_representation():
    """Test Timer string representation."""
    timer = Timer()
    timer_str = str(timer)
    assert "Timer" in timer_str
    assert "elapsed" in timer_str.lower()
