#!/usr/bin/env python3
"""
Basic validation test for backend_common package.
This test validates core functionality without external dependencies.
"""

def test_imports():
    """Test that core components can be imported."""
    print("Testing imports...")

    try:
        # Test exception imports
        from backend_common.exceptions import BaseError, ValidationError, ErrorCode
        print("✓ Exception classes imported successfully")

        # Test model imports
        from backend_common.models import BaseModel, HealthResponse, PaginationParams
        print("✓ Model classes imported successfully")

        # Test utility imports
        from backend_common.utils import utc_now, Timer, validate_email_address
        print("✓ Utility functions imported successfully")

        # Test database imports
        from backend_common.database import DatabaseManager
        print("✓ Database classes imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of core components."""
    print("\nTesting basic functionality...")

    try:
        # Test exceptions
        from backend_common.exceptions import ValidationError, ErrorCode
        error = ValidationError(message="Test error", field_errors={"email": "Invalid"})
        assert error.message == "Test error"
        assert error.status_code == 422
        print("✓ Exception handling works")

        # Test models
        from backend_common.models import BaseModel, PaginationParams

        class TestModel(BaseModel):
            name: str
            age: int = 25

        model = TestModel(name="John")
        assert model.name == "John"
        assert model.age == 25
        print("✓ Pydantic models work")

        # Test pagination
        pagination = PaginationParams(page=2, size=10)
        assert pagination.offset == 10
        assert pagination.limit == 10
        print("✓ Pagination works")

        # Test utilities
        from backend_common.utils import utc_now, Timer
        now = utc_now()
        assert now is not None
        print("✓ Time utilities work")

        timer = Timer()
        timer.start()
        import time
        time.sleep(0.001)  # Small delay
        elapsed = timer.stop()
        assert elapsed > 0
        print("✓ Timer utility works")

        return True
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all basic tests."""
    print("=== Backend Common Package Basic Validation ===\n")

    success = True

    # Test imports
    if not test_imports():
        success = False

    # Test functionality
    if not test_basic_functionality():
        success = False

    print("\n" + "="*50)
    if success:
        print("🎉 All basic tests passed! Your backend_common package is working.")
        print("\nNext steps:")
        print("1. Install the package: pip install -e .")
        print("2. Use the FastAPI examples in the examples/ folder")
        print("3. Check the comprehensive examples for production usage")
    else:
        print("❌ Some tests failed. Please check the errors above.")

    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
