"""
Comprehensive test for backend_common package.

This test validates that all components work together correctly
and demonstrates the usage patterns for your FastAPI applications.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Optional

# Test the main imports work correctly
def test_main_imports():
    """Test that all main components can be imported."""
    try:
        from backend_common import (
            BaseError,
            ValidationError,
            NotFoundError,
            BusinessLogicError,
            BaseModel,
            HealthResponse,
            HealthStatus,
            PaginationParams,
            PaginatedResponse,
            utc_now,
            Timer,
            validate_email_address,
            validate_username,
        )
        print("✓ All main imports successful")
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_exception_system():
    """Test the exception handling system."""
    from backend_common.exceptions import (
        BaseError,
        ValidationError,
        NotFoundError,
        BusinessLogicError,
        ErrorCode
    )

    # Test BaseError
    error = BaseError(
        message="Test error",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        context={"test": "data"}
    )

    assert error.message == "Test error"
    assert error.status_code == 500
    assert error.context == {"test": "data"}

    error_dict = error.to_dict()
    assert "error_code" in error_dict
    assert "message" in error_dict

    # Test ValidationError
    validation_error = ValidationError(
        message="Validation failed",
        field_errors={"email": "Invalid format"}
    )

    validation_dict = validation_error.to_dict()
    assert "field_errors" in validation_dict
    assert validation_dict["field_errors"]["email"] == "Invalid format"

    # Test NotFoundError
    not_found = NotFoundError(
        resource="User",
        resource_id="123"
    )

    assert "User not found with ID: 123" in not_found.message
    assert not_found.status_code == 404

    print("✓ Exception system working correctly")


def test_models_system():
    """Test the Pydantic models system."""
    from backend_common.models import (
        BaseModel,
        PaginationParams,
        PaginatedResponse,
        HealthResponse,
        HealthStatus,
    )

    # Test BaseModel
    class TestModel(BaseModel):
        name: str
        age: Optional[int] = None

    model = TestModel(name="John", age=30)
    assert model.name == "John"
    assert model.age == 30

    # Test model_dump
    data = model.model_dump()
    assert data["name"] == "John"
    assert data["age"] == 30

    # Test PaginationParams
    pagination = PaginationParams(page=2, size=10)
    assert pagination.page == 2
    assert pagination.size == 10
    assert pagination.offset == 10  # (page - 1) * size
    assert pagination.limit == 10

    # Test PaginatedResponse
    test_items = [{"id": 1}, {"id": 2}]
    paginated = PaginatedResponse.create(
        items=test_items,
        params=pagination,
        total_items=25
    )

    assert len(paginated.items) == 2
    assert paginated.pagination.page == 2
    assert paginated.pagination.total_items == 25
    assert paginated.pagination.total_pages == 3  # ceil(25/10)
    assert paginated.pagination.has_previous is True
    assert paginated.pagination.has_next is True

    # Test HealthResponse
    health = HealthResponse.create_healthy(version="1.0.0")
    assert health.status == HealthStatus.HEALTHY
    assert health.version == "1.0.0"

    print("✓ Models system working correctly")


def test_utility_functions():
    """Test the utility functions."""
    from backend_common.utils import (
        utc_now,
        Timer,
        validate_email_address,
        validate_username,
        validate_password_strength,
        validate_required_fields,
    )
    from backend_common.exceptions import ValidationError

    # Test time utilities
    now = utc_now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None

    # Test Timer
    with Timer() as timer:
        # Simulate some work
        import time
        time.sleep(0.01)

    assert timer.elapsed_seconds > 0
    assert timer.elapsed_milliseconds > 0

    # Test email validation
    valid_email = validate_email_address("test@example.com")
    assert "@" in valid_email

    try:
        validate_email_address("invalid-email")
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected

    # Test username validation
    valid_username = validate_username("testuser123")
    assert valid_username == "testuser123"

    try:
        validate_username("123invalid")  # Cannot start with number
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected

    # Test password validation
    try:
        validate_password_strength("Password123!")
        # Should not raise exception
    except ValidationError:
        assert False, "Valid password should not raise error"

    try:
        validate_password_strength("weak")
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected

    # Test required fields validation
    data = {"name": "John", "email": "john@example.com"}
    validate_required_fields(data, ["name", "email"])  # Should not raise

    try:
        validate_required_fields(data, ["name", "email", "phone"])
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "phone" in str(e.field_errors)

    print("✓ Utility functions working correctly")


@pytest.mark.asyncio
async def test_database_components():
    """Test database components (mock test since we don't have a real DB)."""
    from backend_common.database import DatabaseManager
    from backend_common.models import SQLAlchemyBase
    from sqlalchemy import Column, Integer, String

    # Test DatabaseManager initialization
    db_manager = DatabaseManager(
        database_url="sqlite+aiosqlite:///:memory:",
        echo=False
    )

    # Test that we can access the engine
    engine = db_manager.engine
    assert engine is not None

    # Test that we can access the session factory
    session_factory = db_manager.session_factory
    assert session_factory is not None

    print("✓ Database components initialized correctly")


def test_integration_example():
    """Test that the integration patterns work as expected."""
    from backend_common.exceptions import setup_exception_handlers, BusinessLogicError
    from backend_common.models import BaseModel, HealthResponse
    from backend_common.utils import validate_email_address, Timer

    # Simulate a service model
    class UserCreate(BaseModel):
        email: str
        username: str
        full_name: Optional[str] = None

    # Test model creation and validation
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        full_name="Test User"
    )

    assert user_data.email == "test@example.com"
    assert user_data.username == "testuser"

    # Test business logic with exceptions
    def create_user_with_validation(user_data: UserCreate):
        # Validate email format
        validate_email_address(user_data.email)

        # Simulate business rule
        if user_data.username == "admin":
            raise BusinessLogicError(
                message="Username 'admin' is reserved",
                rule="reserved_username"
            )

        return {"id": 1, "email": user_data.email, "username": user_data.username}

    # Test successful creation
    result = create_user_with_validation(user_data)
    assert result["email"] == "test@example.com"

    # Test business rule violation
    admin_user = UserCreate(
        email="admin@example.com",
        username="admin"
    )

    try:
        create_user_with_validation(admin_user)
        assert False, "Should have raised BusinessLogicError"
    except BusinessLogicError as e:
        assert "reserved" in e.message
        assert e.rule == "reserved_username"

    # Test performance measurement
    with Timer() as timer:
        # Simulate some processing
        validate_email_address("performance@test.com")

    assert timer.elapsed_milliseconds > 0

    print("✓ Integration patterns working correctly")


def run_all_tests():
    """Run all tests manually."""
    print("Running comprehensive backend_common tests...\n")

    try:
        test_main_imports()
        test_exception_system()
        test_models_system()
        test_utility_functions()

        # Run async test
        asyncio.run(test_database_components())

        test_integration_example()

        print("\n🎉 All tests passed! Your backend_common package is working correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
