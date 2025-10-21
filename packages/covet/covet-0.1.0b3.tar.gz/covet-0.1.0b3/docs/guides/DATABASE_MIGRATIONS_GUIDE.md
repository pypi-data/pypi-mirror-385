# CovetPy Database Migrations Guide

## Production-Ready Migration System

Complete guide to using CovetPy's enterprise-grade database migration system for safe, reliable schema and data migrations.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Creating Migrations](#creating-migrations)
4. [Applying Migrations](#applying-migrations)
5. [Rolling Back Migrations](#rolling-back-migrations)
6. [Auto-Generating Migrations](#auto-generating-migrations)
7. [Data Migrations](#data-migrations)
8. [Safe Deployment Practices](#safe-deployment-practices)
9. [Zero-Downtime Migrations](#zero-downtime-migrations)
10. [Troubleshooting](#troubleshooting)
11. [Production Checklist](#production-checklist)

---

## Introduction

CovetPy's migration system provides production-grade database schema and data migration capabilities with comprehensive safety features:

- **Multi-Database Support**: PostgreSQL, MySQL, and SQLite
- **Automatic Discovery**: Intelligent migration file detection and sorting
- **Dry-Run Mode**: Preview changes before applying
- **Migration Locking**: Prevent concurrent migrations
- **Automatic Backup**: Create backups before applying changes
- **Rollback Safety**: Safe rollback with automatic state restoration
- **Progress Tracking**: Real-time progress for data migrations
- **Batch Processing**: Handle millions of rows efficiently

---

## Quick Start

### Installation

```python
# Migrations are included with CovetPy
from covet.database.migrations import MigrationManager
```

### Basic Usage

```python
import asyncio
from covet.database.adapters.postgresql import PostgreSQLAdapter
from covet.database.migrations import MigrationManager

async def run_migrations():
    # Connect to database
    adapter = PostgreSQLAdapter(
        host='localhost',
        database='myapp',
        user='postgres',
        password='secret'
    )
    await adapter.connect()

    # Create migration manager
    manager = MigrationManager(
        adapter=adapter,
        dialect='postgresql',
        migrations_dir='./migrations'
    )

    # Apply pending migrations
    result = await manager.migrate_up()

    if result['success']:
        print(f"Applied {len(result['applied'])} migrations")
    else:
        print(f"Migration failed: {result['error']}")

    await adapter.disconnect()

# Run
asyncio.run(run_migrations())
```

---

## Creating Migrations

### Manual Migration Creation

Create migrations manually for precise control:

```python
from covet.database.migrations import MigrationManager

manager = MigrationManager(adapter, 'postgresql', './migrations')

# Create new migration
filepath = await manager.create_migration(
    name='add_user_email_index',
    forward_sql=[
        'CREATE INDEX idx_user_email ON users(email)',
        'ANALYZE users',
    ],
    backward_sql=[
        'DROP INDEX idx_user_email',
    ]
)
```

### Migration File Structure

Generated migration files follow this structure:

```python
"""
Migration: add_user_email_index
Created: 2024-10-11T15:30:00
Database: postgresql
"""

from covet.database.migrations.runner import Migration


class AddUserEmailIndexMigration(Migration):
    """
    Add index on user email column for faster lookups.
    """

    dependencies = []  # List of migrations this depends on

    forward_sql = [
        """CREATE INDEX idx_user_email ON users(email)""",
        """ANALYZE users""",
    ]

    backward_sql = [
        """DROP INDEX idx_user_email""",
    ]
```

### Migration Naming Conventions

Follow these conventions for clear, sortable migrations:

- **Timestamp Format**: `YYYY_MM_DD_HHMMSS_description`
- **Example**: `2024_10_11_153000_add_user_email_index.py`
- **Descriptive Names**: Clearly indicate what the migration does
- **Action Prefixes**:
  - `create_` - Create new table/index
  - `add_` - Add column/constraint
  - `drop_` - Remove table/column
  - `alter_` - Modify existing structure
  - `rename_` - Rename table/column
  - `backfill_` - Data migration

---

## Applying Migrations

### Apply All Pending Migrations

```python
# Apply all pending migrations
result = await manager.migrate_up()

if result['success']:
    print(f"Duration: {result['duration']:.2f}s")
    for name in result['applied']:
        print(f"  ✓ {name}")
else:
    print(f"Error: {result['error']}")
```

### Apply Up To Specific Migration

```python
# Apply up to a specific migration
result = await manager.migrate_up(target='2024_10_11_153000_add_indexes')
```

### Dry-Run Mode

**ALWAYS** test migrations with dry-run first:

```python
# Preview what would be applied
result = await manager.migrate_up(dry_run=True)

print(f"Would apply {len(result['applied'])} migrations:")
for name in result['applied']:
    print(f"  - {name}")

# After verification, apply for real
if input("Apply migrations? (yes/no): ") == 'yes':
    result = await manager.migrate_up()
```

### Check Migration Status

```python
# Get status of all migrations
status_list = await manager.get_status()

for status in status_list:
    mark = "[X]" if status.applied else "[ ]"
    applied_at = f" (applied {status.applied_at})" if status.applied else ""
    print(f"{mark} {status.name}{applied_at}")
```

---

## Rolling Back Migrations

### Rollback Last Migration

```python
# Rollback the most recent migration
result = await manager.migrate_down(steps=1)

if result['success']:
    print(f"Rolled back: {result['rolled_back']}")
else:
    print(f"Rollback failed: {result['error']}")
```

### Rollback Multiple Migrations

```python
# Rollback last 3 migrations
result = await manager.migrate_down(steps=3)
```

### Dry-Run Rollback

```python
# Preview rollback without applying
result = await manager.migrate_down(steps=1, dry_run=True)
```

### Writing Rollback-Safe Migrations

**Critical**: Always provide reversible operations:

```python
# GOOD: Fully reversible
forward_sql = [
    "ALTER TABLE users ADD COLUMN phone VARCHAR(20)",
]
backward_sql = [
    "ALTER TABLE users DROP COLUMN phone",
]

# BAD: Data loss on rollback
forward_sql = [
    "ALTER TABLE users DROP COLUMN temporary_data",
]
backward_sql = [
    "-- Cannot restore dropped data!",
]
```

**Best Practices**:
- Always make operations reversible
- Backup data before destructive operations
- Test rollback in staging environment
- Document any non-reversible operations

---

## Auto-Generating Migrations

### From ORM Model Changes

CovetPy can automatically detect schema changes and generate migrations:

```python
from covet.database.migrations import MigrationGenerator
from covet.database.migrations.schema_diff import (
    SchemaReader,
    ModelSchemaReader,
    SchemaComparator
)

# Read current database schema
reader = SchemaReader(adapter, 'postgresql')
db_schema = await reader.read_schema()

# Read schema from ORM models
from myapp import models
model_reader = ModelSchemaReader([
    models.User,
    models.Post,
    models.Comment,
])
model_schema = model_reader.read_schema()

# Compare and find differences
comparator = SchemaComparator()
diff = comparator.compare(db_schema, model_schema)

if diff.has_changes():
    # Generate migration file
    generator = MigrationGenerator('postgresql', './migrations')
    filepath = generator.generate_from_diff(diff, 'auto_migration')
    print(f"Generated: {filepath}")
else:
    print("No changes detected")
```

### Rename Detection

The schema comparator intelligently detects renames vs drop+add:

```python
# This will be detected as a RENAME (not drop+add)
# Old schema: username column
# New schema: user_name column
# (High similarity + same type = detected as rename)

# Generated SQL will be:
# ALTER TABLE users RENAME COLUMN username TO user_name
```

---

## Data Migrations

### Basic Data Migration

For transforming existing data:

```python
from covet.database.migrations.data_migrations import DataMigration

class BackfillUserEmails(DataMigration):
    """Normalize all email addresses to lowercase."""

    async def transform_batch(self, rows, adapter):
        # Transform each row
        for row in rows:
            if row['email']:
                row['email'] = row['email'].lower()
        return rows

# Execute migration
migration = BackfillUserEmails(
    adapter=adapter,
    table_name='users',
    batch_size=1000
)

progress = await migration.execute()

print(f"Processed {progress.processed_rows} rows")
print(f"Success rate: {progress.success_rate:.1f}%")
print(f"Speed: {progress.rows_per_second:.0f} rows/sec")
```

### Bulk Data Migration (High Performance)

For large tables with millions of rows:

```python
from covet.database.migrations.data_migrations import BulkDataMigration

class BulkUserMigration(BulkDataMigration):
    """Use bulk operations for maximum performance."""

    async def transform_batch(self, rows, adapter):
        return [{**row, 'migrated': True} for row in rows]

migration = BulkUserMigration(
    adapter=adapter,
    table_name='users',
    batch_size=10000  # Larger batches for bulk ops
)

progress = await migration.execute()
```

### Parallel Data Migration

Process multiple batches concurrently:

```python
from covet.database.migrations.data_migrations import ParallelDataMigration

migration = ParallelDataMigration(
    adapter=adapter,
    table_name='users',
    batch_size=1000,
    max_workers=4  # Process 4 batches in parallel
)

progress = await migration.execute()
```

### Progress Tracking

Monitor long-running data migrations:

```python
def progress_callback(progress):
    print(f"Progress: {progress.processed_rows}/{progress.total_rows} "
          f"({progress.success_rate:.1f}% success) - "
          f"ETA: {progress.eta_seconds:.0f}s")

migration = BackfillUserEmails(
    adapter=adapter,
    table_name='users',
    batch_size=1000,
    progress_callback=progress_callback
)

await migration.execute()
```

### Resumable Migrations

Enable checkpointing for large migrations:

```python
migration = BackfillUserEmails(
    adapter=adapter,
    table_name='users',
    batch_size=1000,
    checkpoint_enabled=True  # Save progress after each batch
)

# If migration fails, resume from last checkpoint
progress = await migration.execute(resume=True)
```

---

## Safe Deployment Practices

### Pre-Deployment Checklist

Before deploying migrations to production:

- [ ] **Test in staging** with production-like data
- [ ] **Run dry-run** to preview changes
- [ ] **Review generated SQL** for correctness
- [ ] **Check rollback SQL** for reversibility
- [ ] **Verify backup** exists and is restorable
- [ ] **Estimate duration** based on table sizes
- [ ] **Schedule maintenance window** if needed
- [ ] **Prepare rollback plan** with steps
- [ ] **Monitor database metrics** during migration
- [ ] **Have DBA on standby** for large migrations

### Migration Deployment Strategy

#### Option 1: Automated Deployment

```bash
# In CI/CD pipeline
covet migrate up --dry-run  # Verify migrations
covet migrate up            # Apply migrations
```

#### Option 2: Manual Deployment

```python
# Connect to production database
adapter = PostgreSQLAdapter(
    host='prod-db.example.com',
    database='production',
    user='app_user',
    password=os.environ['DB_PASSWORD']
)

manager = MigrationManager(
    adapter=adapter,
    dialect='postgresql',
    migrations_dir='./migrations',
    enable_locking=True,   # Prevent concurrent migrations
    enable_backup=True,    # Create automatic backup
)

# 1. Check status
status = await manager.get_status()
pending = [s for s in status if not s.applied]
print(f"Pending migrations: {len(pending)}")

# 2. Dry run
print("\nDry run...")
result = await manager.migrate_up(dry_run=True)

# 3. Apply after confirmation
if input("\nProceed? (yes/no): ") == 'yes':
    result = await manager.migrate_up()

    if result['success']:
        print(f"\nSuccess! Duration: {result['duration']:.2f}s")
    else:
        print(f"\nFailed: {result['error']}")
        print("Database unchanged due to transaction rollback.")
```

### Monitoring During Migration

```python
import logging
import time

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

# Track metrics
start_time = time.time()
result = await manager.migrate_up()
duration = time.time() - start_time

# Log results
logger.info(f"Migration duration: {duration:.2f}s")
logger.info(f"Migrations applied: {len(result['applied'])}")

# Alert on errors
if not result['success']:
    send_alert(f"Migration failed: {result['error']}")
```

---

## Zero-Downtime Migrations

### Backwards-Compatible Schema Changes

Follow these patterns for zero-downtime deployments:

#### Phase 1: Add New Column (Nullable)

```python
# Migration 1: Add column as nullable
forward_sql = [
    "ALTER TABLE users ADD COLUMN email_v2 VARCHAR(255)",
]
backward_sql = [
    "ALTER TABLE users DROP COLUMN email_v2",
]
```

Deploy application that writes to both columns.

#### Phase 2: Backfill Data

```python
# Migration 2: Backfill existing data
class BackfillEmailV2(DataMigration):
    async def transform_batch(self, rows, adapter):
        for row in rows:
            if row['email'] and not row['email_v2']:
                row['email_v2'] = row['email']
        return rows
```

#### Phase 3: Make Non-Nullable

```python
# Migration 3: Add NOT NULL constraint
forward_sql = [
    "ALTER TABLE users ALTER COLUMN email_v2 SET NOT NULL",
]
```

Deploy application that reads from new column.

#### Phase 4: Drop Old Column

```python
# Migration 4: Remove old column
forward_sql = [
    "ALTER TABLE users DROP COLUMN email",
    "ALTER TABLE users RENAME COLUMN email_v2 TO email",
]
```

### Large Table Migrations

For tables with millions of rows:

**DON'T DO THIS** (locks table for hours):
```sql
ALTER TABLE users ADD COLUMN email VARCHAR(255) DEFAULT 'unknown@example.com' NOT NULL;
```

**DO THIS INSTEAD**:
```python
# Step 1: Add column as nullable (instant)
await adapter.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")

# Step 2: Backfill in small batches
migration = BulkDataMigration(
    adapter=adapter,
    table_name='users',
    batch_size=1000
)
await migration.execute()

# Step 3: Add NOT NULL after backfill
await adapter.execute("ALTER TABLE users ALTER COLUMN email SET NOT NULL")
```

### Online Schema Change Tools

For PostgreSQL with pg_repack:
```bash
pg_repack -d production -t users
```

For MySQL with pt-online-schema-change:
```bash
pt-online-schema-change --alter "ADD COLUMN email VARCHAR(255)" \
  D=production,t=users --execute
```

---

## Troubleshooting

### Common Issues

#### Migration Fails Midway

**Symptom**: Migration fails and database is in inconsistent state.

**Solution**: CovetPy uses transactions - the database is automatically rolled back:

```python
# The failed migration is automatically rolled back
# Check logs for error details
result = await manager.migrate_up()
if not result['success']:
    print(f"Error: {result['error']}")
    # Database is in the state BEFORE the migration
```

#### Cannot Acquire Migration Lock

**Symptom**: `Cannot acquire migration lock` error.

**Cause**: Another migration is running or lock wasn't released.

**Solution**:
```python
# Check if another process is running migrations
# If not, manually release lock:

if dialect == 'postgresql':
    await adapter.execute("SELECT pg_advisory_unlock_all()")
else:
    await adapter.execute("DELETE FROM _covet_migration_lock")
```

#### Large Table Migration Too Slow

**Symptom**: Migration takes hours on large table.

**Solution**: Use data migration with batching:
```python
migration = BulkDataMigration(
    adapter=adapter,
    table_name='large_table',
    batch_size=10000,  # Adjust based on table
    checkpoint_enabled=True  # Enable resume
)
```

#### Rollback Fails

**Symptom**: Cannot rollback migration.

**Cause**: Rollback SQL is missing or incorrect.

**Solution**:
1. Review the migration file
2. Manually write rollback SQL
3. Apply rollback SQL directly:
```python
await adapter.execute("DROP TABLE new_table")
await manager.history.record_rolled_back('migration_name')
```

---

## Production Checklist

### Before Deployment

- [ ] **All migrations tested in staging**
- [ ] **Rollback tested in staging**
- [ ] **Database backup completed**
- [ ] **Estimated duration calculated**
- [ ] **Maintenance window scheduled (if needed)**
- [ ] **Rollback plan documented**
- [ ] **Team notified of deployment**
- [ ] **Monitoring alerts configured**

### During Deployment

- [ ] **Dry-run executed successfully**
- [ ] **Migration lock acquired**
- [ ] **Progress monitored in real-time**
- [ ] **Database metrics tracked**
- [ ] **Error logs monitored**
- [ ] **Application health checked**

### After Deployment

- [ ] **All migrations applied successfully**
- [ ] **Application functionality verified**
- [ ] **Database performance checked**
- [ ] **No error logs**
- [ ] **Backup retention configured**
- [ ] **Documentation updated**
- [ ] **Team notified of completion**

### Rollback Procedure

If issues occur post-deployment:

1. **Stop new deployments**
2. **Assess impact** (data loss risk?)
3. **Execute rollback**:
   ```python
   result = await manager.migrate_down(steps=1)
   ```
4. **Verify rollback** success
5. **Restore from backup** if needed
6. **Document incident**
7. **Fix migration** for next deployment

---

## Performance Targets

CovetPy migration system achieves:

- **Schema Diff**: <5 seconds for 100 tables
- **Migration Speed**: 1000+ operations/second
- **Rollback Time**: <30 seconds for typical migration
- **Data Migration**: 10,000+ rows/second with bulk operations
- **Lock Acquisition**: <100ms

---

## Additional Resources

- **API Reference**: `/docs/api/migrations`
- **Examples**: `/examples/migrations`
- **Video Tutorial**: [YouTube Link]
- **Community Forum**: [Forum Link]

---

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/covetpy/covetpy/issues
- **Discord**: https://discord.gg/covetpy
- **Email**: support@covetpy.io

---

**Last Updated**: 2024-10-11
**Version**: 1.0.0
**Status**: Production Ready
