# tests/unit/test_models.py
"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime
from backend_common.models import (
    BaseModel,
    HealthResponse,
    HealthStatus,
    PaginationParams,
    PaginatedResponse,
    SQLAlchemyBase,
    TimestampMixin,
)


def test_health_response():
    """Test HealthResponse model."""
    health = HealthResponse(
        status=HealthStatus.HEALTHY,
        version="1.0.0",
        timestamp=datetime.now(),
        details={"database": "connected"}
    )

    assert health.status == HealthStatus.HEALTHY
    assert health.version == "1.0.0"
    assert isinstance(health.timestamp, datetime)
    assert health.details["database"] == "connected"


def test_health_status_enum():
    """Test HealthStatus enum values."""
    assert HealthStatus.HEALTHY == "healthy"
    assert HealthStatus.UNHEALTHY == "unhealthy"
    assert HealthStatus.DEGRADED == "degraded"


def test_pagination_params():
    """Test PaginationParams model."""
    params = PaginationParams(page=2, size=50)

    assert params.page == 2
    assert params.size == 50
    assert params.offset == 50  # (page - 1) * size


def test_pagination_params_defaults():
    """Test PaginationParams default values."""
    params = PaginationParams()

    assert params.page == 1
    assert params.size == 20
    assert params.offset == 0


def test_paginated_response():
    """Test PaginatedResponse model."""
    items = [{"id": 1}, {"id": 2}]
    response = PaginatedResponse(
        items=items,
        total=100,
        page=1,
        size=20,
        pages=5
    )

    assert response.items == items
    assert response.total == 100
    assert response.page == 1
    assert response.size == 20
    assert response.pages == 5


def test_base_model():
    """Test BaseModel functionality."""
    class TestModel(BaseModel):
        name: str
        value: int

    model = TestModel(name="test", value=42)
    assert model.name == "test"
    assert model.value == 42


def test_timestamp_mixin():
    """Test TimestampMixin functionality."""
    class TestModel(TimestampMixin, BaseModel):
        name: str

    model = TestModel(name="test")
    assert isinstance(model.created_at, datetime)
    assert isinstance(model.updated_at, datetime)
    assert model.created_at == model.updated_at
