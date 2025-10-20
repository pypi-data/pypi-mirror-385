# src/backend_common/config/base.py
"""
Base configuration settings for backend services.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class BaseConfig(BaseSettings):
    """Base configuration class with common settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Key Configuration
    API_KEY: str = Field(..., description="API key for authentication")
    API_KEY_NAME: str = Field(
        default="X-API-Key", description="API key header name"
    )

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(..., description="Secret key for JWT tokens")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="JWT token expiration in minutes"
    )

    # Service Configuration
    SERVICE_NAME: str = Field(default="backend-service", description="Service name")
    SERVICE_VERSION: str = Field(default="1.0.0", description="Service version")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Database Configuration
    DATABASE_URL: Optional[str] = Field(
        default=None, description="Database connection URL"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")


# Global settings instance
settings = BaseConfig()
