# src/backend_common/database/manager.py
"""
Database manager for SQLAlchemy integration.

Provides centralized database connection management with connection pooling,
health monitoring, and automatic reconnection capabilities.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from ..exceptions import BaseError, ErrorCode

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions with common database operations."""

    def __init__(self, database_url: str, **engine_kwargs) -> None:
        """
        Initialize database manager.

        Args:
            database_url: Database connection URL
            **engine_kwargs: Additional engine configuration
        """
        self.database_url = database_url
        self._engine = None
        self._session_factory = None
        self._engine_kwargs = {
            "echo": False,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            **engine_kwargs
        }

    @property
    def engine(self):
        """Get the database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                self.database_url,
                **self._engine_kwargs
            )
        return self._engine

    @property
    def session_factory(self):
        """Get the session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_factory

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session context manager.

        Yields:
            AsyncSession: Database session
        """
        session = self.session_factory()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise BaseError(
                message="Database operation failed",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )
        finally:
            await session.close()

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """Get transactional session with explicit transaction control"""
        async with self.get_session() as session:
            async with session.begin():
                yield session

    async def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results as list of dictionaries.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries representing rows
        """
        try:
            async with self.get_session() as session:
                result = await session.execute(text(query), params or {})
                rows = result.fetchall()
                if not rows:
                    return []
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise BaseError(
                message="Query execution failed",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def execute_non_query(self, query: str, params: Optional[Dict] = None) -> int:
        """
        Execute INSERT/UPDATE/DELETE query and return affected rows count.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Number of affected rows
        """
        try:
            async with self.get_session() as session:
                result = await session.execute(text(query), params or {})
                await session.commit()
                return result.rowcount
        except Exception as e:
            logger.error(f"Non-query execution failed: {e}")
            raise BaseError(
                message="Non-query execution failed",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def execute_many(self, query: str, params_list: List[Dict]) -> int:
        """
        Execute query with multiple parameter sets.

        Args:
            query: SQL query string
            params_list: List of parameter dictionaries

        Returns:
            Total number of affected rows
        """
        try:
            total_affected = 0
            async with self.get_session() as session:
                for params in params_list:
                    result = await session.execute(text(query), params)
                    total_affected += getattr(result, 'rowcount', 0)
                await session.commit()
                return total_affected
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise BaseError(
                message="Batch execution failed",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def add_record(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a single record and return the inserted row.

        Args:
            table_name: Target table name (may be schema qualified)
            data: Column-value mapping

        Returns:
            Inserted row as dictionary
        """
        try:
            columns = list(data.keys())
            col_sql = ", ".join(f'"{c}"' for c in columns)
            placeholders = ", ".join(f":{c}" for c in columns)
            sql = f"INSERT INTO {table_name} ({col_sql}) VALUES ({placeholders}) RETURNING *"

            async with self.transaction() as session:
                result = await session.execute(text(sql), data)
                row = result.fetchone()
                inserted = dict(zip(result.keys(), row)) if row else {}
                logger.info(f"Inserted 1 record into {table_name}")
                return inserted
        except Exception as e:
            logger.error(f"Failed to insert record into {table_name}: {e}")
            raise BaseError(
                message=f"Failed to insert record into {table_name}",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def add_records(self, table_name: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Insert multiple records in a single transaction.

        Args:
            table_name: Target table
            records: List of column-value mappings

        Returns:
            List of inserted rows as dictionaries
        """
        if not records:
            return []

        try:
            first_columns = list(records[0].keys())
            col_sql = ", ".join(f'"{c}"' for c in first_columns)
            placeholders = ", ".join(f":{c}" for c in first_columns)
            sql = f"INSERT INTO {table_name} ({col_sql}) VALUES ({placeholders}) RETURNING *"

            inserted_rows: List[Dict[str, Any]] = []
            async with self.transaction() as session:
                for rec in records:
                    result = await session.execute(text(sql), rec)
                    row = result.fetchone()
                    if row:
                        inserted_rows.append(dict(zip(result.keys(), row)))

            logger.info(f"Inserted {len(inserted_rows)} records into {table_name}")
            return inserted_rows
        except Exception as e:
            logger.error(f"Failed to insert records into {table_name}: {e}")
            raise BaseError(
                message=f"Failed to insert records into {table_name}",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def get_schema_info(self, table_name: str, schema_name: str = None) -> Dict[str, Any]:
        """
        Get database schema information for a specific table.

        Args:
            table_name: Name of the table
            schema_name: Schema name (defaults to 'public' if not specified)

        Returns:
            Dictionary containing columns, constraints, and indexes information
        """
        if not schema_name:
            parts = table_name.split('.')
            if len(parts) <= 1:
                schema_name = 'public'
            else:
                schema_name = parts[0].strip('"')
            table_name = parts[-1].strip('"')

        try:
            # Get column information
            columns_query = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_name = :table_name AND table_schema = :schema_name
            ORDER BY ordinal_position
            """
            columns = await self.execute_query(columns_query, {
                'table_name': table_name,
                'schema_name': schema_name
            })

            # Get table constraints
            constraints_query = """
            SELECT 
                tc.constraint_name,
                constraint_type,
                column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = :table_name AND tc.table_schema = :schema_name
            """
            constraints = await self.execute_query(constraints_query, {
                'table_name': table_name,
                'schema_name': schema_name
            })

            # Get indexes (PostgreSQL specific)
            indexes_query = """
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = :table_name AND schemaname = :schema_name
            """
            indexes = await self.execute_query(indexes_query, {
                'table_name': table_name,
                'schema_name': schema_name
            })

            return {
                'columns': columns,
                'constraints': constraints,
                'indexes': indexes
            }
        except Exception as e:
            logger.error(f"Failed to retrieve schema info for {table_name}: {e}")
            raise BaseError(
                message=f"Failed to retrieve schema info for {table_name}",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def get_schemas(self) -> Dict[str, List[str]]:
        """
        Get all database schemas and their tables.

        Returns:
            Dictionary mapping schema names to lists of table names
        """
        try:
            query = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name
            """
            tables = await self.execute_query(query)
            schema = {}
            for row in tables:
                schema.setdefault(row['table_schema'], []).append(row['table_name'])
            return schema
        except Exception as e:
            logger.error(f"Schema retrieval failed: {e}")
            raise BaseError(
                message="Schema retrieval failed",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def create_tables(self) -> None:
        """Create all database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise BaseError(
                message="Failed to create database tables",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def drop_tables(self) -> None:
        """Drop all database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise BaseError(
                message="Failed to drop database tables",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                original_error=e
            )

    async def health_check(self) -> Dict[str, Any]:
        """
        Enhanced database health check with detailed information.

        Returns:
            Dictionary containing health status and database information
        """
        try:
            # Basic connectivity test
            version_result = await self.execute_query("SELECT version()")
            version = version_result[0]['version'] if version_result else None

            # Check current database
            db_result = await self.execute_query("SELECT current_database()")
            database = db_result[0]['current_database'] if db_result else None

            # Check active connections (PostgreSQL specific)
            try:
                conn_result = await self.execute_query(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                )
                active_connections = conn_result[0]['count'] if conn_result else None
            except:
                active_connections = None

            return {
                'status': 'healthy',
                'database_version': version,
                'current_database': database,
                'active_connections': active_connections,
                'initialized': True
            }
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'initialized': False
            }

    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connections closed")
