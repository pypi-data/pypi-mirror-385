"""
Database Adapters

Multi-database support with unified interface for PostgreSQL, MySQL,
and SQLite with optimized drivers and connection pooling.
"""

from .base import AdapterFactory, DatabaseAdapter

# from .mongodb import MongoDBAdapter  # Temporarily disabled - has syntax
# errors
from .mysql import MySQLAdapter
from .postgresql import PostgreSQLAdapter
from .sqlite import SQLiteAdapter

__all__ = [
    "DatabaseAdapter",
    "AdapterFactory",
    "PostgreSQLAdapter",
    "MySQLAdapter",
    # "MongoDBAdapter",  # Temporarily disabled
    "SQLiteAdapter",
]
