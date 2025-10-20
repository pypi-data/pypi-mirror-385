# src/backend_common/utils/validation.py
"""
Validation utility functions for data validation and sanitization.

Provides common validation patterns, input sanitization,
and data format checking across all backend services.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Union

from email_validator import EmailNotValidError, validate_email


class ValidationUtils:
    """
    Utility class for data validation and sanitization.

    Provides common validation patterns for emails, UUIDs,
    phone numbers, and other data formats.
    """

    # Common regex patterns
    UUID_PATTERN = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    PHONE_PATTERN = re.compile(r"^\+?1?\d{9,15}$")
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")
    PASSWORD_PATTERN = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$"
    )

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            bool: True if email is valid
        """
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    @staticmethod
    def is_valid_uuid(value: str) -> bool:
        """
        Validate UUID format.

        Args:
            value: String to validate as UUID

        Returns:
            bool: True if valid UUID format
        """
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            bool: True if valid phone format
        """
        return bool(ValidationUtils.PHONE_PATTERN.match(phone))

    @staticmethod
    def is_valid_username(username: str) -> bool:
        """
        Validate username format.

        Args:
            username: Username to validate

        Returns:
            bool: True if valid username format
        """
        return bool(ValidationUtils.USERNAME_PATTERN.match(username))

    @staticmethod
    def is_strong_password(password: str) -> bool:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            bool: True if password meets strength requirements
        """
        return bool(ValidationUtils.PASSWORD_PATTERN.match(password))

    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input by removing dangerous characters.

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            str: Sanitized string
        """
        if not isinstance(value, str):
            return str(value)

        # Remove null bytes and control characters
        sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", value)

        # Trim whitespace
        sanitized = sanitized.strip()

        # Truncate if max_length specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized

    @staticmethod
    def validate_pagination_params(page: int, size: int) -> Dict[str, Any]:
        """
        Validate pagination parameters.

        Args:
            page: Page number
            size: Page size

        Returns:
            dict: Validation result with errors if any
        """
        errors = []

        if page < 1:
            errors.append("Page number must be greater than 0")

        if size < 1:
            errors.append("Page size must be greater than 0")

        if size > 100:
            errors.append("Page size cannot exceed 100")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any], required_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Validate that required fields are present and not empty.

        Args:
            data: Data dictionary to validate
            required_fields: List of required field names

        Returns:
            dict: Validation result with missing fields if any
        """
        missing_fields = []

        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)

        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
        }

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize email address to lowercase.

        Args:
            email: Email address to normalize

        Returns:
            str: Normalized email address
        """
        return email.lower().strip()

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Normalize phone number by removing non-digit characters.

        Args:
            phone: Phone number to normalize

        Returns:
            str: Normalized phone number
        """
        return re.sub(r"[^\d+]", "", phone)
