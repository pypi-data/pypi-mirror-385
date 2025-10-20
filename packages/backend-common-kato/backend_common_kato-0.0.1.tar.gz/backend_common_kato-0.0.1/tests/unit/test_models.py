# tests/unit/test_models.py
"""Unit tests for shared models."""

import pytest
from datetime import datetime, timezone
from backend_common.models import (
    BaseModel,
    HealthResponse,
    HealthStatus,
    PaginationParams,
    PaginatedResponse,
)


def test_health_response_healthy():
    """Test healthy response creation."""
    response = HealthResponse.healthy("test-service", response_time=0.5)

    assert response.service_name == "test-service"
    assert response.status == HealthStatus.HEALTHY
    assert response.response_time == 0.5
    assert isinstance(response.timestamp, datetime)


def test_health_response_unhealthy():
    """Test unhealthy response creation."""
    response = HealthResponse.unhealthy(
        "test-service",
        "Connection failed",
        details={"error": "timeout"}
    )

    assert response.service_name == "test-service"
    assert response.status == HealthStatus.UNHEALTHY
    assert response.message == "Connection failed"
    assert response.details["error"] == "timeout"


def test_pagination_params():
    """Test pagination parameters."""
    params = PaginationParams(page=2, size=50)

    assert params.page == 2
    assert params.size == 50
    assert params.offset == 50  # (2-1) * 50
    assert params.limit == 50


def test_pagination_params_validation():
    """Test pagination validation."""
    with pytest.raises(ValueError):
        PaginationParams(page=0)  # Page must be >= 1

    with pytest.raises(ValueError):
        PaginationParams(size=101)  # Size must be <= 100


def test_paginated_response():
    """Test paginated response creation."""
    items = [{"id": 1}, {"id": 2}]
    pagination = PaginationParams(page=1, size=10)

    response = PaginatedResponse.create(
        items=items,
        total=25,
        pagination=pagination
    )

    assert len(response.items) == 2
    assert response.total == 25
    assert response.page == 1
    assert response.size == 10
    assert response.pages == 3  # ceil(25/10)
    assert response.has_next is True
    assert response.has_previous is False
