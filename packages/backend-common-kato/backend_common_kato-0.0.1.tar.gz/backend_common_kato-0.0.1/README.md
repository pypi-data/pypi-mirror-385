# Backend Common Package

A shared utilities package for Python backend microservices, providing standardized components for authentication, HTTP communication, database management, and more.

## Features

✅ **Common Exceptions** - Standardized error handling with correlation tracking  
✅ **Authentication & Authorization** - JWT-based auth with FastAPI dependencies  
✅ **HTTP Client Utilities** - Robust HTTP clients with retry logic and service auth  
✅ **Database Management** - SQLAlchemy async session handling with health checks  
✅ **Middleware Components** - Logging, correlation IDs, and authentication middleware  
✅ **Health Monitoring** - Service health checks and dependency monitoring  
✅ **Configuration Management** - Pydantic-based settings with environment support  
✅ **Utility Functions** - Time handling, validation, and common operations  

## Installation

```bash
# Install from PyPI (once published)
pip install backend-common

# Or using uv
uv add backend-common

# Install from git repository
pip install git+https://github.com/your-org/backend-common.git
```

## Quick Start

### 1. Basic FastAPI Integration

```python
from fastapi import FastAPI, Depends
from backend_common.middleware import CorrelationMiddleware, LoggingMiddleware
from backend_common.auth.dependencies import require_auth
from backend_common.exceptions import NotFoundError
from backend_common.models import HealthResponse

app = FastAPI()

# Add middleware
app.add_middleware(CorrelationMiddleware)
app.add_middleware(LoggingMiddleware)

@app.get("/protected", dependencies=[Depends(require_auth())])
async def protected_endpoint():
    return {"message": "This endpoint requires authentication"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse.healthy("my-service")
```

### 2. Database Setup

```python
from backend_common.database import DatabaseManager, set_database_manager
from backend_common.config import ServiceConfig

# Initialize configuration
config = ServiceConfig(
    service_name="my-service",
    database_url="postgresql+asyncpg://user:pass@localhost/db"
)

# Setup database manager
db_manager = DatabaseManager(config.database_url)
set_database_manager(db_manager)

# Use in endpoints
from backend_common.database import get_db_session

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db_session)):
    # Use database session
    pass
```

### 3. Service Communication

```python
from backend_common.http import ServiceClient
from backend_common.auth.manager import JWTAuthManager

# Setup service client
auth_manager = JWTAuthManager(secret_key="your-secret")
client = ServiceClient(
    service_name="my-service",
    base_url="http://other-service:8000",
    auth_manager=auth_manager
)

# Make authenticated requests
async with client:
    response = await client.get("/api/data")
    data = response.json()
```

## Configuration

The package uses Pydantic settings for configuration management:

```python
from backend_common.config import ServiceConfig

config = ServiceConfig(
    service_name="my-service",
    database_url="postgresql+asyncpg://...",
    jwt_secret_key="your-secret-key",
    environment="production"
)
```

Environment variables are automatically loaded from `.env` files or system environment.

## Exception Handling

Standardized exceptions with correlation tracking:

```python
from backend_common.exceptions import NotFoundError, ValidationError

# Business logic exceptions
raise NotFoundError("User", "123")
raise ValidationError("email", "invalid@", "Must be valid email")

# HTTP exceptions  
raise UnauthorizedError("Invalid token")
raise ServiceUnavailableError("user-service", "Connection timeout")
```

## Health Checks

Built-in health monitoring for services and dependencies:

```python
from backend_common.http import HealthChecker
from backend_common.models import HealthStatus

# Setup health checker
health_checker = HealthChecker({
    "database": "http://localhost:5432/health",
    "redis": "http://localhost:6379/health"
})

await health_checker.start_monitoring()

# Check service health
status = health_checker.get_service_status("database")
is_healthy = status.status == HealthStatus.HEALTHY
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/backend-common.git
cd backend-common

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Publishing to PyPI

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
