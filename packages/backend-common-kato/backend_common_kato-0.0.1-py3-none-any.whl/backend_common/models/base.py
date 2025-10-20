# src/backend_common/models/base.py
"""
Base model classes for consistent data validation.

Provides foundation classes with standardized configuration
and validation behavior across all services.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    """
    Base Pydantic model with standardized configuration.

    Provides consistent model behavior across all services with
    proper serialization, validation, and field handling.
    """

    model_config = ConfigDict(
        # Use enum values instead of names in serialization
        use_enum_values=True,
        # Validate assignment after model creation
        validate_assignment=True,
        # Allow extra fields but don't include them in serialization
        extra="forbid",
        # Use timezone-aware datetime serialization
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        },
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary with proper serialization.

        Returns:
            Dictionary representation of the model
        """
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        Create model instance from dictionary.

        Args:
            data: Dictionary containing model data

        Returns:
            Model instance
        """
        return cls(**data)
