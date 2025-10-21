# src/backend_common/models/base.py
"""
Base model classes for consistent data validation.

Provides foundation classes with standardized configuration
and validation behavior across all services.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class BaseModel(PydanticBaseModel):
    """
    Base Pydantic model with standardized configuration.

    Provides consistent model behavior across all services with
    proper serialization, validation, and field handling.
    """

    model_config = ConfigDict(
        # Enable ORM mode for SQLAlchemy integration
        from_attributes=True,
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate assignment
        validate_assignment=True,
        # Allow population by field name or alias
        populate_by_name=True,
        # Exclude unset fields from dict()
        exclude_unset=False,
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


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""

    created_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the record was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the record was last updated"
    )


class IdentifiableMixin(BaseModel):
    """Mixin for models with ID field."""

    id: Optional[int] = Field(
        default=None, description="Unique identifier for the record"
    )


# SQLAlchemy Models
SQLAlchemyBase = declarative_base()


class SQLAlchemyTimestampMixin:
    """SQLAlchemy mixin for timestamp fields."""

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Timestamp when the record was created",
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Timestamp when the record was last updated",
    )


class SQLAlchemyBase(SQLAlchemyBase):
    """Base SQLAlchemy model with common fields."""

    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique identifier for the record",
    )


# Response Models
class BaseResponse(BaseModel):
    """Base response model."""

    success: bool = Field(
        default=True, description="Whether the operation was successful"
    )
    message: Optional[str] = Field(default=None, description="Response message")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = Field(
        default=False, description="Whether the operation was successful"
    )
    error_code: str = Field(description="Error code identifying the type of error")
    message: str = Field(description="Human-readable error message")
    status_code: int = Field(description="HTTP status code")
    field_errors: Optional[Dict[str, str]] = Field(
        default=None, description="Field-specific validation errors"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context information"
    )
