# Schema Reader - Enterprise Database Introspection System

## Overview

The SchemaReader is a production-grade database introspection system that provides comprehensive schema metadata extraction across PostgreSQL, MySQL, and SQLite. It's designed for migration generation, schema analysis, and database documentation tools.

## Features

- **Multi-Database Support**: PostgreSQL, MySQL, SQLite
- **Complete Schema Introspection**: Tables, columns, indexes, constraints, foreign keys
- **Type Normalization**: Unified type system across database platforms
- **Production-Ready**: Comprehensive error handling, logging, and retry logic
- **Performance-Optimized**: Parallel reads, connection pooling integration
- **Enterprise-Grade**: Battle-tested queries for complex database features

## Architecture

### Data Structures

The SchemaReader uses strongly-typed dataclasses to represent database schema:

```python
ColumnDefinition      # Complete column metadata
IndexDefinition       # Index structure and properties
ConstraintDefinition  # All constraint types (PK, FK, UNIQUE, CHECK)
ForeignKeyDefinition  # Foreign key relationships
TableDefinition       # Complete table with all metadata
```

### Database Support Matrix

| Feature | PostgreSQL | MySQL | SQLite |
|---------|-----------|-------|--------|
| Tables | ✓ | ✓ | ✓ |
| Columns | ✓ | ✓ | ✓ |
| Data Types | ✓ | ✓ | ✓ |
| Indexes | ✓ | ✓ | ✓ |
| Primary Keys | ✓ | ✓ | ✓ |
| Foreign Keys | ✓ | ✓ | ✓ |
| Unique Constraints | ✓ | ✓ | Limited |
| Check Constraints | ✓ | ✓ (8.0.16+) | Limited |
| Comments | ✓ | ✓ | - |
| Partial Indexes | ✓ | - | - |
| Deferrable Constraints | ✓ | - | ✓ |

## Installation

```bash
# Install required dependencies
pip install asyncpg aiomysql aiosqlite
```

## Usage Examples

### Basic Usage - PostgreSQL

```python
from covet.database.adapters.postgresql import PostgreSQLAdapter
from covet.database.migrations.schema_reader import SchemaReader, DatabaseType

# Initialize adapter
adapter = PostgreSQLAdapter(
    host='localhost',
    port=5432,
    database='mydb',
    user='postgres',
    password='secret'
)
await adapter.connect()

# Create schema reader
reader = SchemaReader(adapter, DatabaseType.POSTGRESQL)

# Read all tables in schema
tables = await reader.read_tables('public')
print(f"Found {len(tables)} tables: {tables}")

# Read complete table definition
table_def = await reader.read_table_complete('users', 'public')
print(f"Table: {table_def.name}")
print(f"Columns: {len(table_def.columns)}")
print(f"Indexes: {len(table_def.indexes)}")
print(f"Foreign Keys: {len(table_def.foreign_keys)}")

# Iterate through columns
for col in table_def.columns:
    print(f"  {col.name}: {col.data_type} "
          f"{'NOT NULL' if not col.is_nullable else 'NULL'}")

# Cleanup
await adapter.disconnect()
```

### MySQL Example

```python
from covet.database.adapters.mysql import MySQLAdapter
from covet.database.migrations.schema_reader import SchemaReader, DatabaseType

# Initialize adapter
adapter = MySQLAdapter(
    host='localhost',
    port=3306,
    database='mydb',
    user='root',
    password='secret'
)
await adapter.connect()

# Create schema reader
reader = SchemaReader(adapter, DatabaseType.MYSQL)

# Read tables
tables = await reader.read_tables('mydb')

# Read column details
columns = await reader.read_columns('users', 'mydb')
for col in columns:
    nullable = "NULL" if col.is_nullable else "NOT NULL"
    pk = " PRIMARY KEY" if col.is_primary_key else ""
    auto = " AUTO_INCREMENT" if col.is_auto_increment else ""
    print(f"{col.name} {col.data_type} {nullable}{pk}{auto}")

await adapter.disconnect()
```

### SQLite Example

```python
from covet.database.adapters.sqlite import SQLiteAdapter
from covet.database.migrations.schema_reader import SchemaReader, DatabaseType

# Initialize adapter
adapter = SQLiteAdapter(database='/path/to/database.db')
await adapter.connect()

# Create schema reader
reader = SchemaReader(adapter, DatabaseType.SQLITE)

# Read all tables
tables = await reader.read_tables()

# Read foreign keys
fks = await reader.read_foreign_keys('orders')
for fk in fks:
    print(f"{fk.name}: {fk.columns} -> {fk.referenced_table}({fk.referenced_columns})")
    print(f"  ON DELETE {fk.on_delete}, ON UPDATE {fk.on_update}")

await adapter.disconnect()
```

### Complete Schema Analysis

```python
# Read entire schema with all tables
reader = SchemaReader(adapter, DatabaseType.POSTGRESQL)
all_tables = await reader.read_schema_complete('public')

for table in all_tables:
    print(f"\nTable: {table.schema}.{table.name}")

    # Primary key columns
    pk_cols = table.get_primary_key_columns()
    if pk_cols:
        print(f"  Primary Key: {', '.join(pk_cols)}")

    # Columns
    print(f"  Columns ({len(table.columns)}):")
    for col in table.columns:
        print(f"    {col}")

    # Indexes
    if table.indexes:
        print(f"  Indexes ({len(table.indexes)}):")
        for idx in table.indexes:
            unique = "UNIQUE " if idx.is_unique else ""
            print(f"    {unique}{idx.name} on {idx.columns}")

    # Foreign keys
    if table.foreign_keys:
        print(f"  Foreign Keys ({len(table.foreign_keys)}):")
        for fk in table.foreign_keys:
            print(f"    {fk}")
```

## API Reference

### SchemaReader Class

#### Constructor

```python
SchemaReader(adapter: Any, db_type: DatabaseType)
```

**Parameters:**
- `adapter`: Database adapter instance (PostgreSQLAdapter, MySQLAdapter, or SQLiteAdapter)
- `db_type`: Database type enum (DatabaseType.POSTGRESQL, MYSQL, or SQLITE)

**Raises:**
- `DatabaseNotSupportedError`: If database type is not supported

#### Methods

##### read_tables(schema: Optional[str] = None) -> List[str]

Get list of all tables in schema/database.

**Parameters:**
- `schema`: Schema name (PostgreSQL) or database name (MySQL/SQLite). Defaults to 'public' for PostgreSQL, current database for MySQL, 'main' for SQLite.

**Returns:** List of table names

**Raises:** `SchemaReadError` if reading fails

##### read_columns(table: str, schema: Optional[str] = None) -> List[ColumnDefinition]

Get complete column definitions for a table.

**Parameters:**
- `table`: Table name
- `schema`: Schema/database name (optional)

**Returns:** List of ColumnDefinition objects

**Raises:** `SchemaReadError` if reading fails

##### read_indexes(table: str, schema: Optional[str] = None) -> List[IndexDefinition]

Get index definitions for a table.

**Parameters:**
- `table`: Table name
- `schema`: Schema/database name (optional)

**Returns:** List of IndexDefinition objects

**Raises:** `SchemaReadError` if reading fails

##### read_constraints(table: str, schema: Optional[str] = None) -> List[ConstraintDefinition]

Get constraint definitions for a table.

**Parameters:**
- `table`: Table name
- `schema`: Schema/database name (optional)

**Returns:** List of ConstraintDefinition objects

**Raises:** `SchemaReadError` if reading fails

##### read_foreign_keys(table: str, schema: Optional[str] = None) -> List[ForeignKeyDefinition]

Get foreign key definitions for a table.

**Parameters:**
- `table`: Table name
- `schema`: Schema/database name (optional)

**Returns:** List of ForeignKeyDefinition objects

**Raises:** `SchemaReadError` if reading fails

##### read_table_complete(table: str, schema: Optional[str] = None) -> TableDefinition

Get complete table definition including all metadata. Reads columns, indexes, constraints, and foreign keys in parallel for optimal performance.

**Parameters:**
- `table`: Table name
- `schema`: Schema/database name (optional)

**Returns:** Complete TableDefinition object

**Raises:** `SchemaReadError` if reading fails

##### read_schema_complete(schema: Optional[str] = None) -> List[TableDefinition]

Get complete schema definition for all tables. Reads all tables with complete metadata in parallel with concurrency limiting.

**Parameters:**
- `schema`: Schema/database name (optional)

**Returns:** List of complete TableDefinition objects

**Raises:** `SchemaReadError` if reading fails

## Data Structures

### ColumnDefinition

```python
@dataclass
class ColumnDefinition:
    name: str                                    # Column name
    data_type: str                              # Native database type
    normalized_type: str                        # Normalized cross-DB type
    is_nullable: bool = True                    # NULL allowed?
    default_value: Optional[str] = None         # Default value expression
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    is_primary_key: bool = False
    is_unique: bool = False
    is_auto_increment: bool = False
    column_comment: Optional[str] = None
    ordinal_position: int = 0
    extra_attributes: Dict[str, Any] = field(default_factory=dict)
```

### IndexDefinition

```python
@dataclass
class IndexDefinition:
    name: str                                   # Index name
    table_name: str                            # Table name
    columns: List[str]                         # Column names in index
    is_unique: bool = False                    # Uniqueness constraint
    is_primary: bool = False                   # Primary key index?
    index_type: IndexType = IndexType.BTREE    # Index algorithm
    where_clause: Optional[str] = None         # Partial index clause (PG)
    index_comment: Optional[str] = None
    extra_attributes: Dict[str, Any] = field(default_factory=dict)
```

### ConstraintDefinition

```python
@dataclass
class ConstraintDefinition:
    name: str                                  # Constraint name
    table_name: str                           # Table name
    constraint_type: ConstraintType           # Type (PK, FK, UNIQUE, CHECK)
    columns: List[str]                        # Column names
    check_clause: Optional[str] = None        # CHECK expression
    constraint_comment: Optional[str] = None
    is_deferrable: bool = False               # Deferrable? (PostgreSQL)
    initially_deferred: bool = False          # Initially deferred?
    extra_attributes: Dict[str, Any] = field(default_factory=dict)
```

### ForeignKeyDefinition

```python
@dataclass
class ForeignKeyDefinition:
    name: str                                 # FK constraint name
    table_name: str                          # Source table
    columns: List[str]                       # Source columns
    referenced_table: str                    # Referenced table
    referenced_columns: List[str]            # Referenced columns
    on_delete: str = "NO ACTION"             # ON DELETE action
    on_update: str = "NO ACTION"             # ON UPDATE action
    is_deferrable: bool = False
    initially_deferred: bool = False
    extra_attributes: Dict[str, Any] = field(default_factory=dict)
```

### TableDefinition

```python
@dataclass
class TableDefinition:
    name: str                                # Table name
    schema: str                              # Schema/database name
    columns: List[ColumnDefinition] = field(default_factory=list)
    indexes: List[IndexDefinition] = field(default_factory=list)
    constraints: List[ConstraintDefinition] = field(default_factory=list)
    foreign_keys: List[ForeignKeyDefinition] = field(default_factory=list)
    table_comment: Optional[str] = None
    engine: Optional[str] = None             # MySQL storage engine
    row_count: Optional[int] = None
    table_size: Optional[int] = None
    extra_attributes: Dict[str, Any] = field(default_factory=dict)

    # Helper methods
    def get_column(self, column_name: str) -> Optional[ColumnDefinition]
    def get_primary_key_columns(self) -> List[str]
```

## Type Normalization

The SchemaReader normalizes database-specific types to a common type system for cross-platform compatibility:

### PostgreSQL Type Mapping

| PostgreSQL Type | Normalized Type |
|----------------|-----------------|
| integer, int4 | INTEGER |
| bigint, int8 | BIGINT |
| smallint, int2 | SMALLINT |
| serial | INTEGER |
| bigserial | BIGINT |
| character varying | VARCHAR |
| character | CHAR |
| text | TEXT |
| boolean, bool | BOOLEAN |
| timestamp without time zone | TIMESTAMP |
| timestamp with time zone | TIMESTAMPTZ |
| numeric, decimal | DECIMAL |
| real, float4 | FLOAT |
| double precision, float8 | DOUBLE |
| bytea | BLOB |
| json | JSON |
| jsonb | JSONB |
| uuid | UUID |

### MySQL Type Mapping

| MySQL Type | Normalized Type |
|-----------|-----------------|
| int, tinyint, mediumint | INTEGER |
| bigint | BIGINT |
| varchar | VARCHAR |
| char | CHAR |
| text, mediumtext, longtext | TEXT |
| blob, mediumblob, longblob | BLOB |
| datetime | DATETIME |
| timestamp | TIMESTAMP |
| decimal | DECIMAL |
| float | FLOAT |
| double | DOUBLE |

### SQLite Type Mapping

| SQLite Type | Normalized Type |
|------------|-----------------|
| INTEGER | INTEGER |
| TEXT | TEXT |
| REAL | FLOAT |
| BLOB | BLOB |
| NUMERIC | NUMERIC |

## Error Handling

The SchemaReader provides comprehensive error handling:

```python
from covet.database.migrations.schema_reader import (
    SchemaReaderError,          # Base exception
    DatabaseNotSupportedError,  # Unsupported database type
    SchemaReadError            # Schema reading failure
)

try:
    tables = await reader.read_tables('public')
except DatabaseNotSupportedError as e:
    print(f"Database not supported: {e}")
except SchemaReadError as e:
    print(f"Failed to read schema: {e}")
except SchemaReaderError as e:
    print(f"Schema reader error: {e}")
```

## Performance Optimization

### Parallel Reads

The SchemaReader uses asyncio to read schema components in parallel:

```python
# read_table_complete() reads columns, indexes, constraints,
# and foreign keys concurrently
table_def = await reader.read_table_complete('users', 'public')
```

### Concurrency Limiting

For complete schema reads, concurrency is limited to avoid overwhelming the database:

```python
# read_schema_complete() limits to 5 concurrent table reads
all_tables = await reader.read_schema_complete('public')
```

### Connection Pooling

Leverage the adapter's connection pooling for optimal performance:

```python
# Configure adapter with appropriate pool size
adapter = PostgreSQLAdapter(
    host='localhost',
    database='mydb',
    min_pool_size=5,
    max_pool_size=20
)
```

## Production Considerations

### Logging

The SchemaReader uses Python's logging module:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('covet.database.migrations.schema_reader')
logger.setLevel(logging.DEBUG)
```

### Connection Management

Always properly manage database connections:

```python
adapter = PostgreSQLAdapter(...)
try:
    await adapter.connect()
    reader = SchemaReader(adapter, DatabaseType.POSTGRESQL)

    # Perform schema operations
    tables = await reader.read_tables('public')

finally:
    # Always disconnect
    await adapter.disconnect()
```

### Error Recovery

Implement retry logic for transient failures:

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def read_schema_with_retry():
    adapter = PostgreSQLAdapter(...)
    await adapter.connect()

    try:
        reader = SchemaReader(adapter, DatabaseType.POSTGRESQL)
        return await reader.read_schema_complete('public')
    finally:
        await adapter.disconnect()
```

## Migration Generation Use Case

```python
async def generate_migration_from_schema():
    """Generate migration from current database schema."""
    adapter = PostgreSQLAdapter(...)
    await adapter.connect()

    try:
        reader = SchemaReader(adapter, DatabaseType.POSTGRESQL)
        tables = await reader.read_schema_complete('public')

        # Generate CREATE TABLE statements
        for table in tables:
            print(f"-- Table: {table.name}")
            print(f"CREATE TABLE {table.name} (")

            # Columns
            col_defs = []
            for col in table.columns:
                null_str = "NOT NULL" if not col.is_nullable else "NULL"
                default_str = f"DEFAULT {col.default_value}" if col.default_value else ""
                col_defs.append(f"  {col.name} {col.data_type} {null_str} {default_str}".strip())

            # Primary key
            pk_cols = table.get_primary_key_columns()
            if pk_cols:
                col_defs.append(f"  PRIMARY KEY ({', '.join(pk_cols)})")

            print(",\n".join(col_defs))
            print(");\n")

            # Indexes
            for idx in table.indexes:
                if not idx.is_primary:
                    unique = "UNIQUE " if idx.is_unique else ""
                    print(f"CREATE {unique}INDEX {idx.name} ON {table.name} ({', '.join(idx.columns)});")

            # Foreign keys
            for fk in table.foreign_keys:
                print(f"ALTER TABLE {table.name} ADD CONSTRAINT {fk.name}")
                print(f"  FOREIGN KEY ({', '.join(fk.columns)})")
                print(f"  REFERENCES {fk.referenced_table} ({', '.join(fk.referenced_columns)})")
                print(f"  ON DELETE {fk.on_delete} ON UPDATE {fk.on_update};")

            print()

    finally:
        await adapter.disconnect()
```

## Testing

Run the comprehensive test suite:

```bash
# Run unit tests (no database required)
pytest tests/test_schema_reader.py -v -k "not integration"

# Run SQLite integration tests (no external database required)
pytest tests/test_schema_reader.py -v -k "TestSchemaReaderSQLite"

# Run all tests including PostgreSQL and MySQL (requires running databases)
pytest tests/test_schema_reader.py -v --markers=integration
```

## Best Practices

1. **Always use context managers or try/finally for connection cleanup**
2. **Configure appropriate connection pool sizes for your workload**
3. **Use read_table_complete() for single tables, read_schema_complete() for entire schemas**
4. **Implement proper error handling and logging in production**
5. **Consider caching schema metadata for frequently accessed schemas**
6. **Monitor database load when performing large schema reads**
7. **Use type normalization for cross-database compatibility**
8. **Test with production-like data volumes to validate performance**

## Troubleshooting

### Issue: Slow schema reads

**Solution:**
- Increase connection pool size
- Use read_table_complete() instead of individual method calls
- Check database server performance
- Verify network latency

### Issue: Missing foreign keys in SQLite

**Solution:**
- Ensure foreign key constraints are enabled: `PRAGMA foreign_keys=ON`
- SQLite adapter enables this by default

### Issue: Type mapping errors

**Solution:**
- Check TYPE_MAPPINGS dictionary in SchemaReader
- Add custom type mappings if needed
- Use normalized_type for cross-database compatibility

### Issue: Permission errors

**Solution:**
- Ensure database user has SELECT permissions on information_schema
- PostgreSQL: Grant access to pg_catalog tables
- MySQL: Grant SHOW DATABASES, SHOW TABLES privileges

## Version History

- **1.0.0** (2025-10-10): Initial release with PostgreSQL, MySQL, and SQLite support

## License

Proprietary - Part of NeutrinoPy/CovetPy Framework

## Support

For issues and questions, please refer to the main project documentation.
