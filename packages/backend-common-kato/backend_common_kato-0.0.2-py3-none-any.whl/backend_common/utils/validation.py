# src/backend_common/utils/validation.py
"""
Validation utilities for backend applications.

Provides common validation patterns, input sanitization,
and data format checking across all backend services.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Union

from email_validator import EmailNotValidError, validate_email

from ..exceptions import ValidationError


def validate_email_address(email: str) -> str:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        str: Normalized email address

    Raises:
        ValidationError: If email format is invalid
    """
    try:
        # Validate and get normalized result
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError as e:
        raise ValidationError(
            message="Invalid email format",
            field_errors={"email": str(e)},
        )


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength.

    Requirements:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains number
    - Contains special character

    Args:
        password: Password to validate

    Returns:
        bool: True if password meets requirements

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character")

    if errors:
        raise ValidationError(
            message="Password does not meet security requirements",
            field_errors={"password": "; ".join(errors)},
        )

    return True


def validate_username(username: str) -> str:
    """
    Validate username format.

    Requirements:
    - 3-30 characters
    - Alphanumeric and underscores only
    - Cannot start with number or underscore

    Args:
        username: Username to validate

    Returns:
        str: Validated username

    Raises:
        ValidationError: If username format is invalid
    """
    if not username:
        raise ValidationError(
            message="Username is required",
            field_errors={"username": "Username cannot be empty"},
        )

    if len(username) < 3 or len(username) > 30:
        raise ValidationError(
            message="Invalid username length",
            field_errors={"username": "Username must be 3-30 characters long"},
        )

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", username):
        raise ValidationError(
            message="Invalid username format",
            field_errors={
                "username": "Username must start with a letter and contain only letters, numbers, and underscores"
            },
        )

    return username.lower()


def validate_phone_number(phone: str, country_code: str = "US") -> str:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate
        country_code: Country code for validation (default: US)

    Returns:
        str: Normalized phone number

    Raises:
        ValidationError: If phone number format is invalid
    """
    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # Basic US phone number validation
    if country_code == "US":
        if len(digits_only) == 10:
            # Format as (XXX) XXX-XXXX
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == "1":
            # Remove leading 1 and format
            digits_only = digits_only[1:]
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        else:
            raise ValidationError(
                message="Invalid phone number format",
                field_errors={
                    "phone": "Phone number must be 10 digits (or 11 with country code 1)"
                },
            )

    # For other countries, just return digits
    return digits_only


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that required fields are present and not empty.

    Args:
        data: Data dictionary to validate
        required_fields: List of required field names

    Raises:
        ValidationError: If any required fields are missing or empty
    """
    missing_fields = []
    empty_fields = []

    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)

    field_errors = {}

    for field in missing_fields:
        field_errors[field] = "This field is required"

    for field in empty_fields:
        field_errors[field] = "This field cannot be empty"

    if field_errors:
        raise ValidationError(
            message="Required fields validation failed",
            field_errors=field_errors,
        )


def validate_string_length(
    value: str,
    field_name: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> None:
    """
    Validate string length constraints.

    Args:
        value: String value to validate
        field_name: Name of the field being validated
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Raises:
        ValidationError: If length constraints are not met
    """
    if not isinstance(value, str):
        raise ValidationError(
            message=f"{field_name} must be a string",
            field_errors={field_name: "Expected string value"},
        )

    length = len(value)

    if min_length is not None and length < min_length:
        raise ValidationError(
            message=f"{field_name} is too short",
            field_errors={field_name: f"Must be at least {min_length} characters long"},
        )

    if max_length is not None and length > max_length:
        raise ValidationError(
            message=f"{field_name} is too long",
            field_errors={field_name: f"Must be at most {max_length} characters long"},
        )


def validate_numeric_range(
    value: Union[int, float],
    field_name: str,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
) -> None:
    """
    Validate numeric value is within specified range.

    Args:
        value: Numeric value to validate
        field_name: Name of the field being validated
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Raises:
        ValidationError: If value is outside specified range
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(
            message=f"{field_name} must be a number",
            field_errors={field_name: "Expected numeric value"},
        )

    if min_value is not None and value < min_value:
        raise ValidationError(
            message=f"{field_name} is too small",
            field_errors={field_name: f"Must be at least {min_value}"},
        )

    if max_value is not None and value > max_value:
        raise ValidationError(
            message=f"{field_name} is too large",
            field_errors={field_name: f"Must be at most {max_value}"},
        )
