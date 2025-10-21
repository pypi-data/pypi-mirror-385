# examples/database_usage.py
"""
Example usage of the enhanced database operations in backend_common.
"""

from typing import Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from backend_common.database.manager import DatabaseManager, Base
from backend_common.database.session import (
    BaseRepository,
    set_database_manager,
    execute_query,
    add_record,
    health_check
)


# Example model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserRepository(BaseRepository[User]):
    """User-specific repository with additional methods."""

    async def get_by_email(self, email: str) -> User:
        """Get user by email or raise NotFoundError."""
        return await self.get_by_field("email", email)

    async def get_active_users(self) -> List[User]:
        """Get all active users using raw SQL."""
        query = """
        SELECT * FROM users 
        WHERE created_at > NOW() - INTERVAL '30 days'
        ORDER BY created_at DESC
        """
        rows = await self.execute_raw_query(query)
        # Convert to User objects if needed, or return raw data
        return rows


async def setup_database():
    """Initialize database manager and create tables."""
    # Database connection string (replace with your actual connection)
    DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

    # Initialize database manager
    db_manager = DatabaseManager(DATABASE_URL)
    set_database_manager(db_manager)

    # Create tables
    await db_manager.create_tables()

    return db_manager


async def example_usage():
    """Demonstrate various database operations."""

    # Setup database
    db_manager = await setup_database()

    # Example 1: Direct database operations (no ORM)
    print("=== Direct Database Operations ===")

    # Execute raw query
    users_data = await execute_query("SELECT * FROM users LIMIT 5")
    print(f"Found {len(users_data)} users")

    # Add single record
    new_user_data = {
        "name": "John Doe",
        "email": "john@example.com"
    }
    inserted_user = await add_record("users", new_user_data)
    print(f"Inserted user: {inserted_user}")

    # Health check
    health = await health_check()
    print(f"Database health: {health['status']}")

    # Example 2: Repository pattern with ORM
    print("\n=== Repository Pattern ===")

    async with db_manager.get_session() as session:
        user_repo = UserRepository(User, session)

        # Create user
        user = await user_repo.create(
            name="Jane Smith",
            email="jane@example.com"
        )
        print(f"Created user: {user.name} ({user.id})")

        # Get by ID
        found_user = await user_repo.get_by_id(user.id)
        print(f"Found user: {found_user.name}")

        # Get by email
        email_user = await user_repo.get_by_email("jane@example.com")
        print(f"Found by email: {email_user.name}")

        # Update user
        updated_user = await user_repo.update(
            user.id,
            name="Jane Doe"
        )
        print(f"Updated user: {updated_user.name}")

        # Bulk create
        bulk_data = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
        ]
        bulk_users = await user_repo.create_many(bulk_data)
        print(f"Created {len(bulk_users)} users in bulk")

        # Count users
        total_users = await user_repo.count()
        print(f"Total users: {total_users}")

        # Raw SQL in repository
        active_users = await user_repo.get_active_users()
        print(f"Active users: {len(active_users)}")

    # Example 3: FastAPI dependency injection
    print("\n=== FastAPI Usage Example ===")
    print("""
    # In your FastAPI route:
    from fastapi import Depends
    from backend_common.database.session import get_db_session
    
    @app.get("/users/{user_id}")
    async def get_user(
        user_id: int, 
        db: AsyncSession = Depends(get_db_session)
    ):
        user_repo = UserRepository(User, db)
        user = await user_repo.get_by_id_or_404(user_id)
        return {"id": user.id, "name": user.name, "email": user.email}
    """)

    await db_manager.close()


# Usage examples for different scenarios
async def simple_crud_example():
    """Simple CRUD operations without repositories."""

    # Raw database operations
    users = await execute_query("SELECT * FROM users WHERE name LIKE :pattern",
                               {"pattern": "%John%"})

    # Add records
    user_data = {"name": "Test User", "email": "test@example.com"}
    new_user = await add_record("users", user_data)

    # Bulk insert
    bulk_users = [
        {"name": "User 1", "email": "user1@example.com"},
        {"name": "User 2", "email": "user2@example.com"},
    ]
    from backend_common.database.session import add_records
    inserted_users = await add_records("users", bulk_users)

    return users, new_user, inserted_users


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
