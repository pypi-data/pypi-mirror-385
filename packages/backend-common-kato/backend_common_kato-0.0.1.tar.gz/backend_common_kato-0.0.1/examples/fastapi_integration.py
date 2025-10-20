# examples/fastapi_integration.py
"""
Example of integrating backend-common with a FastAPI application.

Demonstrates middleware setup, authentication, database integration,
and health monitoring in a complete FastAPI service.
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend_common.middleware import (
    CorrelationMiddleware,
    LoggingMiddleware,
    AuthMiddleware,
)
from backend_common.auth.manager import JWTAuthManager
from backend_common.auth.dependencies import require_auth, set_auth_manager
from backend_common.database import DatabaseManager, set_database_manager, get_db_session
from backend_common.config import ServiceConfig
from backend_common.models import HealthResponse, PaginationParams, PaginatedResponse
from backend_common.exceptions import NotFoundError
from backend_common.http import HealthChecker


# Initialize configuration
config = ServiceConfig(
    service_name="example-service",
    database_url="postgresql+asyncpg://user:pass@localhost/db",
    jwt_secret_key="your-super-secret-key",
    environment="development",
)

# Setup authentication
auth_manager = JWTAuthManager(
    secret_key=config.jwt_secret_key,
    algorithm=config.jwt_algorithm,
    access_token_expire_minutes=config.jwt_access_token_expire_minutes,
)
set_auth_manager(auth_manager)

# Setup database
db_manager = DatabaseManager(config.database_url)
set_database_manager(db_manager)

# Setup health checker
health_checker = HealthChecker({
    "database": "postgresql://localhost:5432",
    "redis": "redis://localhost:6379",
})

# Create FastAPI app
app = FastAPI(
    title=config.service_name,
    version=config.service_version,
    description="Example service using backend-common",
)

# Add middleware
app.add_middleware(CorrelationMiddleware)
app.add_middleware(LoggingMiddleware)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await health_checker.start_monitoring()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await health_checker.stop_monitoring()
    await db_manager.close()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check endpoint."""
    return HealthResponse.healthy(config.service_name)


@app.get("/health/dependencies")
async def dependency_health():
    """Check health of all dependencies."""
    return health_checker.get_all_status()


@app.get("/public")
async def public_endpoint():
    """Public endpoint that doesn't require authentication."""
    return {"message": "This is a public endpoint"}


@app.get("/protected", dependencies=[Depends(require_auth())])
async def protected_endpoint():
    """Protected endpoint that requires authentication."""
    return {"message": "This endpoint requires authentication"}


@app.get("/admin", dependencies=[Depends(require_auth(["admin"]))])
async def admin_endpoint():
    """Admin endpoint that requires specific scope."""
    return {"message": "This endpoint requires admin scope"}


@app.get("/users")
async def get_users(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """Example paginated endpoint with database access."""
    # This would typically query your User model
    # For demo purposes, return empty paginated response
    return PaginatedResponse.create(
        items=[],
        total=0,
        pagination=pagination,
    )


@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Example endpoint that can raise custom exceptions."""
    # This would typically query your User model
    # For demo purposes, always raise NotFoundError
    raise NotFoundError("User", user_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fastapi_integration:app",
        host="0.0.0.0",
        port=8000,
        reload=config.debug,
    )
