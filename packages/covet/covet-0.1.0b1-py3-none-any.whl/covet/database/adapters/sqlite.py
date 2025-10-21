"""
SQLite Database Adapter

Production-ready SQLite adapter using aiosqlite for async operations.
Supports connection pooling, transactions, and SQLite-specific features.
"""

import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import aiosqlite

from ..security.sql_validator import (
    DatabaseDialect,
    InvalidIdentifierError,
    validate_schema_name,
    validate_table_name,
)
from .base import DatabaseAdapter

logger = logging.getLogger(__name__)


class SQLiteConnectionPool:
    """
    Connection pool for SQLite to manage concurrent access.
    SQLite doesn't have native pooling, so we implement it ourselves.
    """

    def __init__(self, database: str, max_size: int = 10, timeout: float = 30.0, **kwargs):
        self.database = database
        self.max_size = max_size
        self.timeout = timeout
        self.kwargs = kwargs
        self._pool: List[aiosqlite.Connection] = []
        self._available: List[aiosqlite.Connection] = []
        self._lock = asyncio.Lock()
        self._closed = False

    async def initialize(self):
        """Initialize the connection pool."""
        async with self._lock:
            for _ in range(self.max_size):
                conn = await aiosqlite.connect(self.database, timeout=self.timeout, **self.kwargs)
                # Enable WAL mode for better concurrency
                await conn.execute("PRAGMA journal_mode=WAL")
                # Enable foreign keys
                await conn.execute("PRAGMA foreign_keys=ON")
                self._pool.append(conn)
                self._available.append(conn)

    async def acquire(self) -> aiosqlite.Connection:
        """Acquire a connection from the pool."""
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        start_time = asyncio.get_event_loop().time()
        while True:
            async with self._lock:
                if self._available:
                    return self._available.pop()

            # Wait and retry
            if asyncio.get_event_loop().time() - start_time > self.timeout:
                raise TimeoutError("Timeout waiting for connection")
            await asyncio.sleep(0.01)

    async def release(self, conn: aiosqlite.Connection):
        """Release a connection back to the pool."""
        async with self._lock:
            if conn in self._pool and conn not in self._available:
                self._available.append(conn)

    async def close(self):
        """Close all connections in the pool."""
        async with self._lock:
            self._closed = True
            for conn in self._pool:
                await conn.close()
            self._pool.clear()
            self._available.clear()

    def get_size(self) -> int:
        """Get total pool size."""
        return len(self._pool)

    def get_idle_size(self) -> int:
        """Get number of idle connections."""
        return len(self._available)


class SQLiteAdapter(DatabaseAdapter):
    """
    High-performance SQLite database adapter using aiosqlite.

    Features:
    - Async/await support with aiosqlite
    - Custom connection pooling for concurrency
    - Automatic retries with exponential backoff
    - Transaction management with savepoints
    - WAL mode for better concurrent access
    - Foreign key constraint enforcement
    - Query timeout support
    - Comprehensive error handling

    Example:
        adapter = SQLiteAdapter(
            database='/path/to/database.db',
            max_pool_size=10,
            timeout=30.0
        )
        await adapter.connect()
        result = await adapter.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            ("Alice", "alice@example.com")
        )
    """

    def __init__(
        self,
        database: str = ":memory:",
        max_pool_size: int = 10,
        timeout: float = 30.0,
        check_same_thread: bool = False,
        isolation_level: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize SQLite adapter.

        Args:
            database: Database file path or ':memory:' for in-memory database
            max_pool_size: Maximum number of connections in pool
            timeout: Database timeout in seconds
            check_same_thread: Whether to check same thread (default: False for async)
            isolation_level: Transaction isolation level (DEFERRED, IMMEDIATE, EXCLUSIVE)
            **kwargs: Additional aiosqlite connection parameters
        """
        self.database = database
        self.max_pool_size = max_pool_size
        self.timeout = timeout
        self.check_same_thread = check_same_thread
        self.isolation_level = isolation_level
        self.extra_params = kwargs

        self.pool: Optional[SQLiteConnectionPool] = None
        self._connected = False

        # Create database directory if it doesn't exist
        if database != ":memory:":
            Path(database).parent.mkdir(parents=True, exist_ok=True)

    async def connect(self) -> None:
        """
        Establish connection pool to SQLite database.

        Creates a connection pool with configured size.
        Includes retry logic for transient connection failures.

        Raises:
            aiosqlite.Error: If connection fails after retries
        """
        if self._connected and self.pool:
            return

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Connecting to SQLite: {self.database} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                # Create connection pool
                self.pool = SQLiteConnectionPool(
                    database=self.database,
                    max_size=self.max_pool_size,
                    timeout=self.timeout,
                    check_same_thread=self.check_same_thread,
                    isolation_level=self.isolation_level,
                    **self.extra_params,
                )

                await self.pool.initialize()

                # Test connection
                conn = await self.pool.acquire()
                try:
                    await conn.execute("SELECT 1")
                finally:
                    await self.pool.release(conn)

                self._connected = True
                logger.info(
                    f"Connected to SQLite: {self.database} " f"(pool size: {self.max_pool_size})"
                )
                return

            except Exception as e:
                logger.warning(f"SQLite connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to SQLite after {max_retries} attempts")
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
            logger.info(f"Disconnected from SQLite: {self.database}")

    async def execute(self, query: str, params: Optional[Union[Tuple, List]] = None) -> int:
        """
        Execute a SQL command (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query with ? placeholders
            params: Query parameters

        Returns:
            Number of affected rows

        Example:
            rows_affected = await adapter.execute(
                "UPDATE users SET active = ? WHERE id = ?",
                (True, 42)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            await conn.execute(query, params)
            await conn.commit()
            affected_rows = conn.total_changes
            logger.debug(f"Executed: {query[:100]}... -> {affected_rows} rows affected")
            return affected_rows

        except Exception as e:
            logger.error(f"Execute failed: {query[:100]}... Error: {e}")
            await conn.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def execute_insert(self, query: str, params: Optional[Union[Tuple, List]] = None) -> int:
        """
        Execute an INSERT command and return the last insert ID.

        Args:
            query: SQL INSERT query with ? placeholders
            params: Query parameters

        Returns:
            Last inserted row ID (rowid/autoincrement value)

        Example:
            user_id = await adapter.execute_insert(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                ("Alice", "alice@example.com")
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            cursor = await conn.execute(query, params)
            last_id = cursor.lastrowid
            await conn.commit()
            logger.debug(f"Executed insert: {query[:100]}... -> last_id={last_id}")
            return last_id

        except Exception as e:
            logger.error(f"Execute insert failed: {query[:100]}... Error: {e}")
            await conn.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def fetch_one(
        self, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row as a dictionary.

        Args:
            query: SQL query with ? placeholders
            params: Query parameters

        Returns:
            Dictionary with column names as keys, or None if no rows

        Example:
            user = await adapter.fetch_one(
                "SELECT * FROM users WHERE id = ?",
                (42,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            await cursor.close()

            if row:
                result = dict(row)
                logger.debug(f"Fetched one: {query[:100]}... -> 1 row")
                return result
            logger.debug(f"Fetched one: {query[:100]}... -> None")
            return None

        except Exception as e:
            logger.error(f"Fetch one failed: {query[:100]}... Error: {e}")
            raise
        finally:
            await self.pool.release(conn)

    async def fetch_all(
        self, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows as list of dictionaries.

        Args:
            query: SQL query with ? placeholders
            params: Query parameters

        Returns:
            List of dictionaries with column names as keys

        Example:
            users = await adapter.fetch_all(
                "SELECT * FROM users WHERE active = ?",
                (True,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            await cursor.close()

            result = [dict(row) for row in rows]
            logger.debug(f"Fetched all: {query[:100]}... -> {len(result)} rows")
            return result

        except Exception as e:
            logger.error(f"Fetch all failed: {query[:100]}... Error: {e}")
            raise
        finally:
            await self.pool.release(conn)

    async def fetch_value(
        self, query: str, params: Optional[Union[Tuple, List]] = None, column: int = 0
    ) -> Optional[Any]:
        """
        Fetch a single value from the first row.

        Args:
            query: SQL query
            params: Query parameters
            column: Column index (default: 0 for first column)

        Returns:
            Single value or None

        Example:
            count = await adapter.fetch_value("SELECT COUNT(*) FROM users")
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            await cursor.close()

            if row:
                value = row[column] if len(row) > column else None
                logger.debug(f"Fetched value: {query[:100]}... -> {value}")
                return value
            return None

        except Exception as e:
            logger.error(f"Fetch value failed: {query[:100]}... Error: {e}")
            raise
        finally:
            await self.pool.release(conn)

    @asynccontextmanager
    async def transaction(self, isolation: Optional[str] = None):
        """
        Context manager for database transactions.

        Args:
            isolation: Transaction isolation level (DEFERRED, IMMEDIATE, EXCLUSIVE)

        Yields:
            aiosqlite.Connection: Database connection within transaction

        Example:
            async with adapter.transaction(isolation='IMMEDIATE') as conn:
                await conn.execute("INSERT INTO users ...")
                await conn.execute("UPDATE accounts ...")
                # Automatically commits on success, rolls back on exception
        """
        if not self._connected or not self.pool:
            await self.connect()

        conn = await self.pool.acquire()
        try:
            # Start transaction with isolation level
            if isolation:
                await conn.execute(f"BEGIN {isolation}")
            else:
                await conn.execute("BEGIN")

            yield conn
            await conn.commit()

        except Exception:
            await conn.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def execute_many(self, query: str, params_list: List[Union[Tuple, List]]) -> int:
        """
        Execute the same query with multiple parameter sets.

        Uses executemany for efficient batch operations.

        Args:
            query: SQL query with placeholders
            params_list: List of parameter tuples

        Returns:
            Total number of affected rows

        Example:
            affected = await adapter.execute_many(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                [
                    ("Alice", "alice@example.com"),
                    ("Bob", "bob@example.com"),
                    ("Charlie", "charlie@example.com"),
                ]
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        conn = await self.pool.acquire()
        try:
            await conn.executemany(query, params_list)
            await conn.commit()
            affected_rows = conn.total_changes
            logger.debug(
                f"Executed many: {query[:100]}... with {len(params_list)} param sets "
                f"-> {affected_rows} rows affected"
            )
            return affected_rows

        except Exception as e:
            logger.error(f"Execute many failed: {query[:100]}... Error: {e}")
            await conn.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def stream_query(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        chunk_size: int = 1000,
    ):
        """
        Stream query results in chunks for large datasets.

        Memory-efficient for processing millions of rows.

        Args:
            query: SQL query
            params: Query parameters
            chunk_size: Number of rows per chunk

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

        conn = await self.pool.acquire()
        try:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)

            while True:
                rows = await cursor.fetchmany(chunk_size)
                if not rows:
                    break
                yield [dict(row) for row in rows]

            await cursor.close()

        except Exception as e:
            logger.error(f"Stream query failed: {query[:100]}... Error: {e}")
            raise
        finally:
            await self.pool.release(conn)

    async def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a table.

        SECURITY FIX: Validates table name to prevent SQL injection.

        Args:
            table_name: Table name (will be validated)

        Returns:
            List of column info dictionaries with keys:
                - cid: column id
                - name: column name
                - type: data type
                - notnull: 1 if NOT NULL, 0 otherwise
                - dflt_value: default value
                - pk: 1 if primary key, 0 otherwise

        Raises:
            ValueError: If table name is invalid or contains SQL injection patterns
        """
        # SECURITY: Validate table name before using in PRAGMA
        try:
            validated_table = validate_table_name(table_name, DatabaseDialect.SQLITE)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{table_name}': {e}")

        # PRAGMA statements don't support parameterization, so we must validate
        # the identifier before string formatting
        query = f"PRAGMA table_info({validated_table})"
        return await self.fetch_all(query)

    async def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Table name

        Returns:
            True if table exists
        """
        query = """
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='table' AND name=?
        """
        count = await self.fetch_value(query, (table_name,))
        return count > 0

    async def get_version(self) -> str:
        """
        Get SQLite version.

        Returns:
            Version string (e.g., "3.39.4")
        """
        return await self.fetch_value("SELECT sqlite_version()")

    async def get_table_list(self) -> List[str]:
        """
        Get list of all tables.

        Returns:
            List of table names
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        rows = await self.fetch_all(query)
        return [row["name"] for row in rows]

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

    async def vacuum(self) -> None:
        """
        Vacuum the database to reclaim space and optimize.

        This can take a while on large databases.
        """
        conn = await self.pool.acquire()
        try:
            await conn.execute("VACUUM")
            await conn.commit()
            logger.info(f"Vacuumed database: {self.database}")
        finally:
            await self.pool.release(conn)

    async def analyze(self, table_name: Optional[str] = None) -> None:
        """
        Analyze database or specific table to update query optimizer statistics.

        SECURITY FIX: Validates table name to prevent SQL injection.

        Args:
            table_name: Table name (optional, analyzes all tables if None)

        Raises:
            ValueError: If table name is invalid or contains SQL injection patterns
        """
        conn = await self.pool.acquire()
        try:
            if table_name:
                # SECURITY: Validate table name before using in ANALYZE
                try:
                    validated_table = validate_table_name(table_name, DatabaseDialect.SQLITE)
                except InvalidIdentifierError as e:
                    raise ValueError(f"Invalid table name '{table_name}': {e}")

                # ANALYZE doesn't support parameterization, so we must validate
                await conn.execute(f"ANALYZE {validated_table}")
            else:
                await conn.execute("ANALYZE")
            await conn.commit()
            logger.info(f"Analyzed: {table_name or 'all tables'}")
        finally:
            await self.pool.release(conn)

    def __repr__(self) -> str:
        """String representation of adapter."""
        conn_status = "connected" if self._connected else "disconnected"
        return (
            f"SQLiteAdapter("
            f"database={self.database}, "
            f"pool={self.max_pool_size}, "
            f"{conn_status}"
            f")"
        )


__all__ = ["SQLiteAdapter"]
