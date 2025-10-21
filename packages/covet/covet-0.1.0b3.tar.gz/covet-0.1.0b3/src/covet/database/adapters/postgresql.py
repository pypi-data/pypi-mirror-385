"""
PostgreSQL Database Adapter

Production-ready PostgreSQL adapter using asyncpg for high-performance async operations.
Supports connection pooling, transactions, prepared statements, and PostgreSQL-specific features.
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple, Union

import asyncpg

from ..security.sql_validator import (
    DatabaseDialect,
    InvalidIdentifierError,
    validate_schema_name,
    validate_table_name,
)
from .base import DatabaseAdapter

logger = logging.getLogger(__name__)


class PostgreSQLAdapter(DatabaseAdapter):
    """
    High-performance PostgreSQL database adapter using asyncpg.

    Features:
    - Async/await support with asyncpg
    - Connection pooling (5-100 connections)
    - Automatic retries with exponential backoff
    - Prepared statement caching
    - Transaction management with savepoints
    - PostgreSQL-specific types (JSON, UUID, Arrays, etc.)
    - Query result streaming for large datasets
    - Comprehensive error handling

    Example:
        adapter = PostgreSQLAdapter(
            host='localhost',
            port=5432,
            database='mydb',
            user='postgres',
            password='secret',
            min_pool_size=5,
            max_pool_size=20
        )
        await adapter.connect()
        result = await adapter.execute("SELECT * FROM users WHERE id = $1", (1,))
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: str = "",
        min_pool_size: int = 5,
        max_pool_size: int = 20,
        command_timeout: float = 60.0,
        query_timeout: float = 30.0,
        statement_cache_size: int = 100,
        max_cached_statement_lifetime: int = 300,
        max_cacheable_statement_size: int = 1024 * 15,
        ssl: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize PostgreSQL adapter.

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Username
            password: Password
            min_pool_size: Minimum pool connections (default: 5)
            max_pool_size: Maximum pool connections (default: 20)
            command_timeout: Timeout for commands in seconds
            query_timeout: Timeout for queries in seconds
            statement_cache_size: Number of prepared statements to cache
            max_cached_statement_lifetime: Max lifetime of cached statements (seconds)
            max_cacheable_statement_size: Max size of cacheable statement (bytes)
            ssl: SSL mode ('require', 'prefer', 'allow', 'disable')
            **kwargs: Additional asyncpg connection parameters
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.command_timeout = command_timeout
        self.query_timeout = query_timeout
        self.statement_cache_size = statement_cache_size
        self.max_cached_statement_lifetime = max_cached_statement_lifetime
        self.max_cacheable_statement_size = max_cacheable_statement_size
        self.ssl = ssl
        self.extra_params = kwargs

        self.pool: Optional[asyncpg.Pool] = None
        self._connected = False

    async def connect(self) -> None:
        """
        Establish connection pool to PostgreSQL database.

        Creates a connection pool with configured min/max sizes.
        Includes retry logic for transient connection failures.

        Raises:
            asyncpg.PostgresError: If connection fails after retries
        """
        if self._connected and self.pool:
            return

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Connecting to PostgreSQL: {self.user}@{self.host}:{self.port}/{self.database} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                # Prepare connection parameters
                conn_params = {
                    "host": self.host,
                    "port": self.port,
                    "database": self.database,
                    "user": self.user,
                    "password": self.password,
                    "min_size": self.min_pool_size,
                    "max_size": self.max_pool_size,
                    "command_timeout": self.command_timeout,
                    "statement_cache_size": self.statement_cache_size,
                    "max_cached_statement_lifetime": self.max_cached_statement_lifetime,
                    "max_cacheable_statement_size": self.max_cacheable_statement_size,
                }

                # Add SSL configuration if specified
                if self.ssl:
                    conn_params["ssl"] = self.ssl

                # Add extra parameters
                conn_params.update(self.extra_params)

                # Create connection pool
                self.pool = await asyncpg.create_pool(**conn_params)

                # Test connection
                async with self.pool.acquire() as conn:
                    await conn.execute("SELECT 1")

                self._connected = True
                logger.info(
                    f"Connected to PostgreSQL: {self.database} "
                    f"(pool size: {self.min_pool_size}-{self.max_pool_size})"
                )
                return

            except asyncpg.PostgresError as e:
                logger.warning(f"PostgreSQL connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to PostgreSQL after {max_retries} attempts")
                    raise

    async def disconnect(self) -> None:
        """
        Close all connections in the pool.

        Gracefully closes all active connections and releases resources.
        """
        if self.pool:
            await self.pool.close()
            self.pool = None
            self._connected = False
            logger.info(f"Disconnected from PostgreSQL: {self.database}")

    async def execute(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Execute a SQL command (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query with $1, $2... placeholders
            params: Query parameters
            timeout: Query timeout in seconds (overrides default)

        Returns:
            Command result string (e.g., "INSERT 0 1", "UPDATE 5")

        Example:
            result = await adapter.execute(
                "INSERT INTO users (name, email) VALUES ($1, $2)",
                ("Alice", "alice@example.com")
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.command_timeout

        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *params, timeout=timeout)
                logger.debug(f"Executed: {query[:100]}... -> {result}")
                return result

        except asyncpg.PostgresError as e:
            logger.error(f"Execute failed: {query[:100]}... Error: {e}")
            raise

    async def fetch_one(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row as a dictionary.

        Args:
            query: SQL query with $1, $2... placeholders
            params: Query parameters
            timeout: Query timeout in seconds

        Returns:
            Dictionary with column names as keys, or None if no rows

        Example:
            user = await adapter.fetch_one(
                "SELECT * FROM users WHERE id = $1",
                (42,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.query_timeout

        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, *params, timeout=timeout)
                if row:
                    result = dict(row)
                    logger.debug(f"Fetched one: {query[:100]}... -> 1 row")
                    return result
                logger.debug(f"Fetched one: {query[:100]}... -> None")
                return None

        except asyncpg.PostgresError as e:
            logger.error(f"Fetch one failed: {query[:100]}... Error: {e}")
            raise

    async def fetch_all(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows as list of dictionaries.

        Args:
            query: SQL query with $1, $2... placeholders
            params: Query parameters
            timeout: Query timeout in seconds

        Returns:
            List of dictionaries with column names as keys

        Example:
            users = await adapter.fetch_all(
                "SELECT * FROM users WHERE active = $1",
                (True,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.query_timeout

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params, timeout=timeout)
                result = [dict(row) for row in rows]
                logger.debug(f"Fetched all: {query[:100]}... -> {len(result)} rows")
                return result

        except asyncpg.PostgresError as e:
            logger.error(f"Fetch all failed: {query[:100]}... Error: {e}")
            raise

    async def fetch_value(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
        column: int = 0,
    ) -> Optional[Any]:
        """
        Fetch a single value from the first row.

        Args:
            query: SQL query
            params: Query parameters
            timeout: Query timeout
            column: Column index (default: 0 for first column)

        Returns:
            Single value or None

        Example:
            count = await adapter.fetch_value("SELECT COUNT(*) FROM users")
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.query_timeout

        try:
            async with self.pool.acquire() as conn:
                value = await conn.fetchval(query, *params, column=column, timeout=timeout)
                logger.debug(f"Fetched value: {query[:100]}... -> {value}")
                return value

        except asyncpg.PostgresError as e:
            logger.error(f"Fetch value failed: {query[:100]}... Error: {e}")
            raise

    @asynccontextmanager
    async def transaction(self, isolation: str = "read_committed"):
        """
        Context manager for database transactions.

        Args:
            isolation: Transaction isolation level
                - 'read_uncommitted'
                - 'read_committed' (default)
                - 'repeatable_read'
                - 'serializable'

        Yields:
            asyncpg.Connection: Database connection within transaction

        Example:
            async with adapter.transaction() as conn:
                await conn.execute("INSERT INTO users ...")
                await conn.execute("UPDATE accounts ...")
                # Automatically commits on success, rolls back on exception
        """
        if not self._connected or not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.transaction(isolation=isolation):
                yield conn

    async def execute_many(
        self,
        query: str,
        params_list: List[Union[Tuple, List]],
        timeout: Optional[float] = None,
    ) -> None:
        """
        Execute the same query with multiple parameter sets.

        Uses executemany for efficient batch operations.

        Args:
            query: SQL query with placeholders
            params_list: List of parameter tuples
            timeout: Query timeout

        Example:
            await adapter.execute_many(
                "INSERT INTO users (name, email) VALUES ($1, $2)",
                [
                    ("Alice", "alice@example.com"),
                    ("Bob", "bob@example.com"),
                    ("Charlie", "charlie@example.com"),
                ]
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        timeout = timeout or self.command_timeout

        try:
            async with self.pool.acquire() as conn:
                await conn.executemany(query, params_list, timeout=timeout)
                logger.debug(f"Executed many: {query[:100]}... with {len(params_list)} param sets")

        except asyncpg.PostgresError as e:
            logger.error(f"Execute many failed: {query[:100]}... Error: {e}")
            raise

    async def copy_records_to_table(
        self,
        table_name: str,
        records: List[Tuple],
        columns: Optional[List[str]] = None,
        schema_name: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Efficiently bulk insert records using COPY protocol.

        Much faster than INSERT for large datasets (10-100x faster).

        SECURITY: Validates table and schema names to prevent SQL injection.

        Args:
            table_name: Target table name (will be validated)
            records: List of tuples with record data
            columns: Column names (optional, uses all columns if None)
            schema_name: Schema name (optional, will be validated)
            timeout: Operation timeout

        Returns:
            COPY result string

        Raises:
            ValueError: If table/schema name is invalid

        Example:
            result = await adapter.copy_records_to_table(
                'users',
                [
                    (1, 'Alice', 'alice@example.com'),
                    (2, 'Bob', 'bob@example.com'),
                ],
                columns=['id', 'name', 'email']
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        # SECURITY: Validate table and schema names
        try:
            validated_table = validate_table_name(table_name, DatabaseDialect.POSTGRESQL)
            validated_schema = None
            if schema_name:
                validated_schema = validate_schema_name(schema_name, DatabaseDialect.POSTGRESQL)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table or schema name: {e}")

        timeout = timeout or self.command_timeout * 5  # COPY can take longer

        try:
            async with self.pool.acquire() as conn:
                result = await conn.copy_records_to_table(
                    validated_table,
                    records=records,
                    columns=columns,
                    schema_name=validated_schema,
                    timeout=timeout,
                )
                logger.info(f"COPY {len(records)} records to {table_name}: {result}")
                return result

        except asyncpg.PostgresError as e:
            logger.error(f"COPY to {table_name} failed: {e}")
            raise

    async def stream_query(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        chunk_size: int = 1000,
        timeout: Optional[float] = None,
    ):
        """
        Stream query results in chunks for large datasets.

        Memory-efficient for processing millions of rows.

        Args:
            query: SQL query
            params: Query parameters
            chunk_size: Number of rows per chunk
            timeout: Query timeout

        Yields:
            List of dictionaries for each chunk

        Example:
            async for chunk in adapter.stream_query(
                "SELECT * FROM large_table",
                chunk_size=1000
            ):
                for row in chunk:
                    process_row(row)
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.query_timeout * 10  # Streaming can take longer

        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    cursor = await conn.cursor(query, *params, timeout=timeout)

                    while True:
                        rows = await cursor.fetch(chunk_size)
                        if not rows:
                            break
                        yield [dict(row) for row in rows]

        except asyncpg.PostgresError as e:
            logger.error(f"Stream query failed: {query[:100]}... Error: {e}")
            raise

    async def get_table_info(self, table_name: str, schema: str = "public") -> List[Dict[str, Any]]:
        """
        Get column information for a table.

        Args:
            table_name: Table name
            schema: Schema name (default: 'public')

        Returns:
            List of column info dictionaries with keys:
                - column_name
                - data_type
                - is_nullable
                - column_default
                - character_maximum_length
        """
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
        """
        return await self.fetch_all(query, (schema, table_name))

    async def table_exists(self, table_name: str, schema: str = "public") -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Table name
            schema: Schema name

        Returns:
            True if table exists
        """
        query = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = $1 AND table_name = $2
            )
        """
        return await self.fetch_value(query, (schema, table_name))

    async def get_version(self) -> str:
        """
        Get PostgreSQL server version.

        Returns:
            Version string (e.g., "PostgreSQL 14.5")
        """
        return await self.fetch_value("SELECT version()")

    async def get_pool_stats(self) -> Dict[str, int]:
        """
        Get connection pool statistics.

        Returns:
            Dictionary with pool statistics:
                - size: Current pool size
                - free: Number of free connections
                - used: Number of connections in use
        """
        if not self.pool:
            return {"size": 0, "free": 0, "used": 0}

        return {
            "size": self.pool.get_size(),
            "free": self.pool.get_idle_size(),
            "used": self.pool.get_size() - self.pool.get_idle_size(),
        }

    def __repr__(self) -> str:
        """String representation of adapter."""
        conn_status = "connected" if self._connected else "disconnected"
        return (
            f"PostgreSQLAdapter("
            f"{self.user}@{self.host}:{self.port}/{self.database}, "
            f"pool={self.min_pool_size}-{self.max_pool_size}, "
            f"{conn_status}"
            f")"
        )


__all__ = ["PostgreSQLAdapter"]
