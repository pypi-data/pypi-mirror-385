# Shared Common Package Structure

## Recommended Repository: `backend-common`

```
backend-common/
├── pyproject.toml                 # Package configuration
├── README.md                      # Usage documentation
├── src/
│   └── backend_common/               # Main package
│       ├── __init__.py
│       ├── exceptions/           # Common exceptions
│       │   ├── __init__.py
│       │   ├── base.py          # Base exception classes
│       │   ├── http.py          # HTTP-specific exceptions
│       │   └── business.py      # Business logic exceptions
│       ├── middleware/           # Reusable middleware
│       │   ├── __init__.py
│       │   ├── correlation.py   # Correlation ID middleware
│       │   ├── logging.py       # Request/response logging
│       │   ├── auth.py          # Authentication middleware
│       │   └── rate_limit.py    # Rate limiting middleware
│       ├── auth/                 # Authentication utilities
│       │   ├── __init__.py
│       │   ├── dependencies.py  # FastAPI dependencies
│       │   ├── jwt_manager.py   # JWT handling
│       │   └── service_auth.py  # Service-to-service auth
│       ├── http/                 # HTTP client utilities
│       │   ├── __init__.py
│       │   ├── client.py        # HTTP client with retry/timeout
│       │   ├── service_client.py # Service communication
│       │   └── health.py        # Health check utilities
│       ├── database/             # Database utilities
│       │   ├── __init__.py
│       │   ├── connection.py    # Connection management
│       │   ├── session.py       # Session handling
│       │   └── health.py        # DB health checks
│       ├── logging/              # Enhanced logging
│       │   ├── __init__.py
│       │   ├── formatters.py    # Custom log formatters
│       │   ├── handlers.py      # Custom log handlers
│       │   └── context.py       # Logging context management
│       ├── models/               # Shared data models
│       │   ├── __init__.py
│       │   ├── base.py          # Base model classes
│       │   ├── health.py        # Health check models
│       │   └── pagination.py    # Pagination models
│       ├── utils/                # Utility functions
│       │   ├── __init__.py
│       │   ├── time.py          # Time utilities
│       │   ├── validation.py    # Validation helpers
│       │   └── serialization.py # Serialization helpers
│       └── config/               # Configuration utilities
│           ├── __init__.py
│           ├── base.py          # Base configuration
│           └── service.py       # Service-specific config
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/
│   └── integration/
└── examples/                     # Usage examples
    ├── fastapi_integration.py
    └── service_setup.py
```

## Installation in Services
```bash
# In each service (Leesin, Hemerdinger, Yasuo)
pip install git+https://github.com/your-org/backend-common.git

# Or if using uv
uv add git+https://github.com/your-org/backend-common.git
```

## Usage Example
```python
# In any service
from backend_common.exceptions import NotFoundError, ValidationError
from backend_common.middleware import CorrelationMiddleware, LoggingMiddleware
from backend_common.auth.dependencies import require_auth, require_service_auth
from backend_common.http import ServiceClient
from backend_common.database import DatabaseManager
```
