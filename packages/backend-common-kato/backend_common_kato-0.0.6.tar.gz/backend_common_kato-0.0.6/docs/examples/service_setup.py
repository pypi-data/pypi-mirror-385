# examples/service_setup.py
"""
Service Setup Example

This example demonstrates how to properly set up and configure a FastAPI service
using the backend-common package with best practices for production deployment.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from backend_common package
from backend_common.database import DatabaseManager, set_database_manager, get_database_manager
from backend_common.exceptions import setup_exception_handlers
from backend_common.models import HealthResponse, HealthStatus


class ServiceConfig:
    """Service configuration class."""

    def __init__(self):
        # Database configuration
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://user:password@localhost/myapp"
        )
        self.database_echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"

        # Service configuration
        self.service_name = os.getenv("SERVICE_NAME", "backend-service")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        # CORS configuration
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.cors_headers = ["*"]


def setup_logging(debug: bool = False) -> None:
    """Setup application logging."""
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Reduce SQLAlchemy logging noise in production
    if not debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


async def create_database_manager(config: ServiceConfig) -> DatabaseManager:
    """Create and configure database manager."""
    db_manager = DatabaseManager(
        database_url=config.database_url,
        echo=config.database_echo,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
    )

    # Test database connection
    if not await db_manager.health_check():
        raise RuntimeError("Failed to connect to database")

    return db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    config = app.state.config

    # Setup logging
    setup_logging(config.debug)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting {config.service_name} v{config.service_version}")

    try:
        # Initialize database
        db_manager = await create_database_manager(config)
        set_database_manager(db_manager)

        # Create database tables if needed
        await db_manager.create_tables()

        logger.info("Service startup completed successfully")

        yield

    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise
    finally:
        # Cleanup
        try:
            db_manager = get_database_manager()
            await db_manager.close()
            logger.info("Database connections closed")
        except:
            pass

        logger.info("Service shutdown completed")


def create_app(config: Optional[ServiceConfig] = None) -> FastAPI:
    """Create and configure FastAPI application."""
    if config is None:
        config = ServiceConfig()

    app = FastAPI(
        title=config.service_name,
        description="Backend service using backend-common package",
        version=config.service_version,
        debug=config.debug,
        lifespan=lifespan,
    )

    # Store config in app state
    app.state.config = config

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=config.cors_methods,
        allow_headers=config.cors_headers,
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Add health check endpoint
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Service health check endpoint."""
        from backend_common.database import check_database_health

        try:
            db_health = await check_database_health()

            overall_status = HealthStatus.HEALTHY
            services = [db_health]

            # Determine overall status
            if db_health.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif db_health.status == HealthStatus.DEGRADED:
                overall_status = HealthStatus.DEGRADED

            return HealthResponse(
                status=overall_status,
                version=config.service_version,
                services=services
            )

        except Exception as e:
            return HealthResponse.create_unhealthy(
                message=f"Health check failed: {str(e)}",
                version=config.service_version
            )

    # Add readiness endpoint for Kubernetes
    @app.get("/ready")
    async def readiness_check():
        """Readiness check for Kubernetes deployments."""
        try:
            from backend_common.database import get_database_manager
            db_manager = get_database_manager()

            if await db_manager.health_check():
                return {"status": "ready"}
            else:
                return {"status": "not ready"}, 503

        except Exception:
            return {"status": "not ready"}, 503

    # Add liveness endpoint for Kubernetes
    @app.get("/live")
    async def liveness_check():
        """Liveness check for Kubernetes deployments."""
        return {"status": "alive"}

    return app


# Example usage
if __name__ == "__main__":
    import uvicorn

    # Create configuration
    config = ServiceConfig()

    # Create application
    app = create_app(config)

    # Run application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        log_level="info" if not config.debug else "debug",
    )
