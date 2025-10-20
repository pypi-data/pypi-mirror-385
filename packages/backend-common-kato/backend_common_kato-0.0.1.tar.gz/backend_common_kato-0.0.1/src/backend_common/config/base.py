# src/backend_common/config/base.py
"""
Base configuration classes for all backend services.

Provides foundation configuration with common settings like
database connections, authentication, and logging setup.
"""

import os
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """
    Base configuration class for all backend services.

    Provides common configuration patterns with environment variable
    support and validation for database, auth, and service settings.
    """

    # Service identification
    service_name: str = Field(..., description="Name of the service")
    service_version: str = Field(
        default="1.0.0", description="Service version"
    )
    environment: str = Field(
        default="development", description="Environment name"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # Database configuration
    database_url: str = Field(..., description="Database connection URL")
    database_pool_size: int = Field(
        default=10, description="Database pool size"
    )
    database_max_overflow: int = Field(
        default=20, description="Database max overflow"
    )
    database_pool_timeout: int = Field(
        default=30, description="Database pool timeout"
    )

    # Authentication configuration
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="JWT access token expiration minutes"
    )

    # HTTP client configuration
    http_timeout: float = Field(
        default=30.0, description="HTTP client timeout"
    )
    http_max_retries: int = Field(
        default=3, description="HTTP client max retries"
    )

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="json", description="Log format (json/text)"
    )

    # CORS configuration
    cors_origins: List[str] = Field(
        default=["*"], description="CORS allowed origins"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"],
        description="CORS allowed methods",
    )

    # Health check configuration
    health_check_interval: float = Field(
        default=30.0, description="Health check interval in seconds"
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment is one of allowed values."""
        allowed = ["development", "staging", "production", "testing"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v.lower()

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is valid."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()

    @validator("log_format")
    def validate_log_format(cls, v):
        """Validate log format is supported."""
        allowed = ["json", "text"]
        if v.lower() not in allowed:
            raise ValueError(f"Log format must be one of: {allowed}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
