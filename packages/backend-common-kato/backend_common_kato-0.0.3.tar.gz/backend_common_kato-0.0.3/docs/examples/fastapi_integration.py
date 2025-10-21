# examples/fastapi_integration.py
"""
FastAPI Integration Example

This example demonstrates how to integrate and use the backend-common package
in a FastAPI application with database operations, exception handling, and health checks.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, Query
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.asyncio import AsyncSession

# Import from backend_common package
from backend_common.database import (
    DatabaseManager,
    set_database_manager,
    get_db_session,
    BaseRepository,
    check_database_health,
)
from backend_common.exceptions import (
    setup_exception_handlers,
    NotFoundError,
    ValidationError,
    BusinessLogicError,
)
from backend_common.models import (
    BaseModel,
    SQLAlchemyBase,
    SQLAlchemyTimestampMixin,
    PaginationParams,
    PaginatedResponse,
    HealthResponse,
    HealthStatus,
)


# Database Models
class User(SQLAlchemyBase, SQLAlchemyTimestampMixin):
    """User database model."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200))
    bio = Column(Text)
    is_active = Column(String(1), default="Y")


# Pydantic Models
class UserCreate(BaseModel):
    """User creation schema."""

    email: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: str
    created_at: datetime
    updated_at: datetime


# Repository
class UserRepository(BaseRepository[User]):
    """User repository with custom methods."""

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        from sqlalchemy import select

        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        from sqlalchemy import select

        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with validation."""
        # Check if email already exists
        existing_user = await self.get_by_email(user_data.email)
        if existing_user:
            raise BusinessLogicError(
                message="Email already registered",
                rule="unique_email"
            )

        # Check if username already exists
        existing_username = await self.get_by_username(user_data.username)
        if existing_username:
            raise BusinessLogicError(
                message="Username already taken",
                rule="unique_username"
            )

        # Create user
        return await self.create(**user_data.model_dump())


# Application Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    db_manager = DatabaseManager(
        database_url="sqlite+aiosqlite:///./example.db",
        echo=True
    )
    set_database_manager(db_manager)

    # Create tables
    await db_manager.create_tables()

    yield

    # Shutdown
    await db_manager.close()


# FastAPI Application
app = FastAPI(
    title="Backend Common Example API",
    description="Example API demonstrating backend-common package usage",
    version="1.0.0",
    lifespan=lifespan
)

# Setup exception handlers
setup_exception_handlers(app)


# Health Check Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check database health
        db_health = await check_database_health()

        if db_health.status == HealthStatus.HEALTHY:
            return HealthResponse.create_healthy(version="1.0.0")
        else:
            return HealthResponse(
                status=HealthStatus.DEGRADED,
                services=[db_health]
            )
    except Exception as e:
        return HealthResponse.create_unhealthy(
            message=f"Health check failed: {str(e)}"
        )


# User Endpoints
@app.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new user."""
    user_repo = UserRepository(User, session)
    user = await user_repo.create_user(user_data)
    return UserResponse.model_validate(user)


@app.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by username or email"),
    session: AsyncSession = Depends(get_db_session)
):
    """List users with pagination and search."""
    user_repo = UserRepository(User, session)

    filters = {}
    if search:
        # In a real application, you'd implement proper search logic
        # This is a simplified example
        pass

    result = await user_repo.get_paginated(pagination, filters)

    # Convert to response models
    user_responses = [UserResponse.model_validate(user) for user in result.items]

    return PaginatedResponse.create(
        items=user_responses,
        params=pagination,
        total_items=result.pagination.total_items
    )


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a user by ID."""
    user_repo = UserRepository(User, session)
    user = await user_repo.get_by_id_or_404(user_id)
    return UserResponse.model_validate(user)


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a user."""
    user_repo = UserRepository(User, session)

    # Validate update data
    update_dict = user_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise ValidationError(message="No fields provided for update")

    user = await user_repo.update(user_id, **update_dict)
    return UserResponse.model_validate(user)


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a user."""
    user_repo = UserRepository(User, session)
    await user_repo.delete(user_id)
    return {"message": "User deleted successfully"}


# Example of using custom exceptions
@app.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Activate a user account."""
    user_repo = UserRepository(User, session)
    user = await user_repo.get_by_id_or_404(user_id)

    if user.is_active == "Y":
        raise BusinessLogicError(
            message="User is already active",
            rule="user_activation"
        )

    await user_repo.update(user_id, is_active="Y")
    return {"message": "User activated successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
