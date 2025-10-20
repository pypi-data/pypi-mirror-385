# examples/service_setup.py
"""
Example of setting up a complete microservice with backend-common.

Shows how to initialize all components and create a production-ready
service with proper error handling and monitoring.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend_common.config import ServiceConfig
from backend_common.auth.manager import JWTAuthManager
from backend_common.auth.dependencies import set_auth_manager
from backend_common.database import DatabaseManager, set_database_manager
from backend_common.http import HealthChecker, ServiceClient
from backend_common.middleware import CorrelationMiddleware, LoggingMiddleware


class ServiceSetup:
    """Complete service setup with all backend-common components."""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.auth_manager = None
        self.db_manager = None
        self.health_checker = None
        self.service_clients = {}

    async def initialize(self):
        """Initialize all service components."""
        # Setup authentication
        self.auth_manager = JWTAuthManager(
            secret_key=self.config.jwt_secret_key,
            algorithm=self.config.jwt_algorithm,
            access_token_expire_minutes=self.config.jwt_access_token_expire_minutes,
        )
        set_auth_manager(self.auth_manager)

        # Setup database
        self.db_manager = DatabaseManager(
            database_url=self.config.database_url,
            pool_size=self.config.database_pool_size,
            max_overflow=self.config.database_max_overflow,
            pool_timeout=self.config.database_pool_timeout,
        )
        set_database_manager(self.db_manager)

        # Setup health checker
        health_endpoints = {
            "database": "internal",  # Internal check
        }
        # Add external service health endpoints
        for service_name, endpoint in self.config.service_endpoints.items():
            health_endpoints[service_name] = f"{endpoint}/health"

        self.health_checker = HealthChecker(
            services=health_endpoints,
            check_interval=self.config.health_check_interval,
        )

        # Setup service clients
        for service_name, endpoint in self.config.service_endpoints.items():
            self.service_clients[service_name] = ServiceClient(
                service_name=self.config.service_name,
                base_url=endpoint,
                auth_manager=self.auth_manager if self.config.service_auth_enabled else None,
                timeout=self.config.http_timeout,
                max_retries=self.config.http_max_retries,
            )

        # Start health monitoring
        await self.health_checker.start_monitoring()

        logging.info(f"Service {self.config.service_name} initialized successfully")

    async def cleanup(self):
        """Cleanup all service components."""
        if self.health_checker:
            await self.health_checker.stop_monitoring()

        # Close service clients
        for client in self.service_clients.values():
            await client.close()

        if self.db_manager:
            await self.db_manager.close()

        logging.info(f"Service {self.config.service_name} cleanup completed")

    def create_app(self) -> FastAPI:
        """Create FastAPI application with middleware and basic endpoints."""
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self.initialize()
            yield
            # Shutdown
            await self.cleanup()

        app = FastAPI(
            title=self.config.service_name,
            version=self.config.service_version,
            description=f"Microservice: {self.config.service_name}",
            lifespan=lifespan,
        )

        # Add middleware
        app.add_middleware(CorrelationMiddleware)
        app.add_middleware(LoggingMiddleware, exclude_paths=["/health", "/metrics"])

        # Add basic endpoints
        from backend_common.models import HealthResponse

        @app.get("/health", response_model=HealthResponse)
        async def health_check():
            return HealthResponse.healthy(self.config.service_name)

        @app.get("/health/dependencies")
        async def dependency_health():
            return self.health_checker.get_all_status()

        @app.get("/config")
        async def get_config():
            return {
                "service_name": self.config.service_name,
                "version": self.config.service_version,
                "environment": self.config.environment,
            }

        return app


# Example usage
if __name__ == "__main__":
    import uvicorn

    # Load configuration
    config = ServiceConfig(
        service_name="example-microservice",
        service_version="1.0.0",
        database_url="postgresql+asyncpg://user:pass@localhost/db",
        jwt_secret_key="your-secret-key",
        environment="development",
        service_endpoints={
            "user-service": "http://user-service:8000",
            "notification-service": "http://notification-service:8000",
        }
    )

    # Create service setup
    service_setup = ServiceSetup(config)
    app = service_setup.create_app()

    # Run the service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=config.log_level.lower(),
    )
