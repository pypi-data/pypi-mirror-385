# CovetPy Database Migration System - Complete Guide

## Production-Grade Migration Management Based on 20 Years of Database Experience

This guide covers the comprehensive database migration system built into CovetPy, designed from two decades of enterprise database administration experience.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Features](#core-features)
4. [Intelligent Rename Detection](#intelligent-rename-detection)
5. [Rollback Safety System](#rollback-safety-system)
6. [SQLite Workarounds](#sqlite-workarounds)
7. [Migration Squashing](#migration-squashing)
8. [Audit Logging](#audit-logging)
9. [Production Best Practices](#production-best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What Makes This System Production-Grade?

✅ **Intelligent Rename Detection** - Prevents data loss from column renames
✅ **Rollback Safety** - Pre-validation, backups, and verification
✅ **SQLite Support** - Workarounds for limited ALTER TABLE support
✅ **Migration Squashing** - Optimize performance for fresh installs
✅ **Complete Audit Trail** - Compliance-ready tracking
✅ **Zero-Downtime Patterns** - Safe production deployments

### Critical Safety Features

🔒 **Path Traversal Protection** (CVE-SPRINT2-003)
🔒 **SQL Injection Prevention** (CVE-SPRINT2-002)
🔒 **Code Execution Safety** (CVE-SPRINT2-001)
🔒 **Automatic Rollback on Failure**
🔒 **Data Loss Prevention**

---

## Quick Start

### Basic Migration Workflow

```python
from covet.database.migrations import MigrationRunner
from covet.database.adapters import PostgreSQLAdapter

# Initialize adapter
adapter = PostgreSQLAdapter(
    host='localhost',
    database='mydb',
    user='admin',
    password='secure'
)
await adapter.connect()

# Create migration runner
runner = MigrationRunner(adapter, dialect='postgresql')

# Apply pending migrations
applied = await runner.migrate('./migrations')
print(f"Applied {len(applied)} migrations")

# Rollback last migration
await runner.rollback(steps=1)
```

### Creating Your First Migration

```bash
# Generate migration from model changes
python -m covet.migrations makemigrations --name add_user_table

# Review generated migration
cat migrations/0001_add_user_table.py

# Apply migration
python -m covet.migrations migrate
```

---

## Core Features

### 1. Automatic Migration Generation

The system automatically generates migrations by comparing your ORM models with the current database schema:

```python
from covet.database.migrations import MigrationGenerator, DiffEngine
from covet.database.migrations.model_reader import read_models_from_directory
from covet.database.migrations.schema_reader import read_database_schema

# Read current state
model_schemas = read_models_from_directory('./models')
db_schemas = await read_database_schema(adapter)

# Generate diff
diff_engine = DiffEngine()
operations = diff_engine.generate_diff(db_schemas, model_schemas)

# Generate migration file
generator = MigrationGenerator(dialect='postgresql')
migration = generator.generate_migration(
    operations=operations,
    migration_name='0042_update_users',
    app_name='accounts'
)

# Save to disk
path = generator.save_migration(migration, './migrations')
```

### 2. Dependency Resolution

Migrations automatically resolve dependencies:

```python
class Migration0042(Migration):
    dependencies = ['0041_add_users_table']

    operations = [
        # Operations here
    ]
```

The runner ensures migrations execute in correct dependency order, preventing foreign key violations.

---

## Intelligent Rename Detection

### The Problem

When you rename a column in your ORM model, naive migration systems generate:

```sql
-- DATA LOSS! ❌
ALTER TABLE users DROP COLUMN name;
ALTER TABLE users ADD COLUMN username VARCHAR(255);
```

All existing data in the `name` column is **permanently lost**.

### The Solution

Our rename detection system uses **Levenshtein distance** to identify renames:

```python
from covet.database.migrations.rename_detection import RenameDetector

detector = RenameDetector(
    similarity_threshold=0.80,  # 80% similarity required
    require_type_match=False,   # Allow type changes during rename
    enable_detection=True
)

# Detect renames in operations
operations = detector.detect_renames(
    operations=operations,
    model_schemas=model_schemas,
    db_schemas=db_schemas
)
```

### How It Works

1. **Candidate Identification**: Finds all DROP COLUMN + ADD COLUMN pairs in same table
2. **Similarity Calculation**: Computes Levenshtein distance between column names
3. **Threshold Filtering**: Keeps matches above similarity threshold (default 80%)
4. **Type Compatibility**: Checks if column types are compatible
5. **Confidence Scoring**: Combines similarity, type match, and constraint compatibility

### Examples

```python
# High Confidence (92% similarity)
'name' → 'username'          # Detected ✓
'email' → 'email_address'    # Detected ✓
'created' → 'created_at'     # Detected ✓

# Medium Confidence (75% similarity)
'status' → 'state'           # Detected if threshold lowered ✓

# Low Confidence (<70% similarity)
'id' → 'user_identifier'     # Not detected (too different) ✗
```

### Manual Override

Force a rename when auto-detection fails:

```python
detector.add_manual_rename(
    table_name='users',
    old_name='legacy_field',
    new_name='new_field_name'
)
```

### Configuration

```python
detector = RenameDetector(
    similarity_threshold=0.85,      # Higher = more conservative
    require_type_match=True,         # Only allow exact type matches
    max_length_diff=0.3,            # Prevent matching very different lengths
)

stats = detector.get_stats()
print(f"Detected {stats['renames_detected']} renames")
print(f"Prevented {stats['false_positives_prevented']} false positives")
```

---

## Rollback Safety System

### Never Lose Data on Rollback

Our rollback safety system implements **enterprise-grade validation**:

```python
from covet.database.migrations.rollback_safety import RollbackValidator, RollbackRisk

validator = RollbackValidator(
    adapter=adapter,
    require_backup=True,          # Always backup before rollback
    verify_checksums=True,        # Verify data integrity
    max_data_loss_rows=1000      # Threshold for high-risk operations
)
```

### Rollback Validation

**Always validate before rolling back in production:**

```python
# Step 1: Validate rollback safety
validation = await validator.validate_rollback(migration)

if not validation.is_safe:
    print(f"❌ Rollback unsafe: {validation.errors}")
    print(f"⚠️  Risk Level: {validation.risk_level.value}")
    print(f"📊 Data at Risk: {sum(validation.data_at_risk.values())} rows")

    for recommendation in validation.recommendations:
        print(f"💡 {recommendation}")

    return  # Don't proceed!

# Step 2: Create backup
backup_id = await validator.create_backup(migration)
print(f"✓ Backup created: {backup_id}")

# Step 3: Perform rollback with verification
result = await validator.safe_rollback(
    migration=migration,
    verify=True,
    backup_id=backup_id
)

if result.success:
    print(f"✓ Rollback successful ({result.duration_seconds:.2f}s)")
else:
    print(f"❌ Rollback failed: {result.errors}")
    # Automatic backup restoration already attempted
```

### Risk Levels

| Risk Level | Description | Action Required |
|------------|-------------|-----------------|
| **SAFE** | No data loss, fully reversible | Can proceed |
| **LOW** | Minimal risk, backup recommended | Review and proceed |
| **MEDIUM** | Some risk, backup required | Create backup, verify staging |
| **HIGH** | Significant risk, may lose data | Test in staging, backup required |
| **CRITICAL** | Destructive or irreversible | Manual intervention required |

### Dry-Run Mode

Test rollback without executing:

```python
result = await validator.dry_run_rollback(migration)

print(f"Would affect {len(result.affected_tables)} tables:")
for table in result.affected_tables:
    rows = result.data_at_risk.get(table, 0)
    print(f"  - {table}: {rows} rows at risk")
```

### Backup and Restore

```python
# Create backup
backup_id = await validator.create_backup(
    migration=migration,
    tables=['users', 'posts']  # Specific tables or auto-detect
)

# ... rollback fails ...

# Restore from backup
success = await validator.restore_backup(backup_id)
if success:
    print("✓ Database restored from backup")
```

---

## SQLite Workarounds

### The Problem

SQLite has limited ALTER TABLE support:

- ❌ No ALTER COLUMN (change type, nullability, default)
- ❌ No DROP COLUMN (before version 3.35)
- ❌ No ADD CONSTRAINT
- ❌ Cannot modify PRIMARY KEY

### The Solution

Our SQLite workaround system safely recreates tables:

```python
from covet.database.migrations.sqlite_workarounds import SQLiteWorkaround

workaround = SQLiteWorkaround(adapter)
await workaround.initialize()  # Detects SQLite version
```

### Supported Operations

#### 1. ALTER COLUMN (Change Type)

```python
await workaround.alter_column(
    table_name='products',
    column_name='price',
    old_schema=ColumnSchema('price', 'INTEGER', nullable=False),
    new_schema=ColumnSchema('price', 'DECIMAL(10,2)', nullable=False)
)
```

**What Happens Internally:**

```sql
-- 1. Create new table with updated schema
CREATE TABLE products_temp (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price DECIMAL(10,2) NOT NULL  -- New type
);

-- 2. Copy all data
INSERT INTO products_temp SELECT id, name, price FROM products;

-- 3. Drop old table
DROP TABLE products;

-- 4. Rename temp table
ALTER TABLE products_temp RENAME TO products;

-- 5. Recreate all indexes and triggers
CREATE INDEX idx_product_name ON products(name);
```

#### 2. DROP COLUMN

```python
await workaround.drop_column(
    table_name='users',
    column_name='deprecated_field'
)
```

For SQLite < 3.35, uses table recreation. For 3.35+, uses native DROP COLUMN.

#### 3. RENAME COLUMN

```python
await workaround.rename_column(
    table_name='users',
    old_name='name',
    new_name='full_name'
)
```

For SQLite < 3.25, uses table recreation. For 3.25+, uses native RENAME COLUMN.

#### 4. ADD CONSTRAINT

```python
await workaround.add_constraint(
    table_name='orders',
    constraint_type='FOREIGN_KEY',
    constraint_definition={
        'name': 'fk_orders_user',
        'column': 'user_id',
        'referenced_table': 'users',
        'referenced_column': 'id',
        'on_delete': 'CASCADE',
        'on_update': 'CASCADE'
    }
)
```

### Safety Features

✅ **Atomic Operations**: All changes in transaction
✅ **Data Verification**: Row count validation before/after
✅ **Index Preservation**: Recreates all indexes
✅ **Trigger Preservation**: Recreates all triggers
✅ **Foreign Key Preservation**: Maintains all constraints
✅ **Automatic Rollback**: On any error

### Version Detection

```python
# Automatically detects capabilities
if workaround.version.supports_drop_column():
    # Use native DROP COLUMN
    print("Using native DROP COLUMN (SQLite 3.35+)")
else:
    # Use table recreation
    print("Using table recreation for DROP COLUMN")
```

---

## Migration Squashing

### The Problem

After years of development, applications accumulate hundreds of migrations:

```
migrations/
├── 0001_initial.py
├── 0002_add_users.py
├── 0003_alter_users.py
├── 0004_add_email.py
...
├── 0498_add_index.py
├── 0499_alter_column.py
└── 0500_add_constraint.py
```

Fresh installation takes **10+ minutes** running all 500 migrations!

### The Solution

Squash old migrations into optimized single migration:

```python
from covet.database.migrations.squashing import MigrationSquasher

squasher = MigrationSquasher(dialect='postgresql')

# Squash migrations 1-400 into single migration
# Keep migrations 401-500 for rollback capability
result = await squasher.squash_migrations(
    migrations=all_migrations,
    target_name='0001_initial_squashed',
    preserve_recent=100  # Keep last 100 migrations separate
)

if result.is_valid:
    print(f"✓ Squashed {result.original_count} migrations")
    print(f"  Operations: {result.operation_count_before} → {result.operation_count_after}")
    print(f"  Optimization: {result.optimization_ratio:.1f}% reduction")

    # Save squashed migration
    squashed_path = generator.save_migration(
        result.squashed_migration,
        './migrations'
    )
else:
    print(f"❌ Squashing failed: {result.conflicts}")
```

### Optimization Examples

#### Column Evolution

```python
# Original migrations (3 operations):
ADD COLUMN email VARCHAR(100)
ALTER COLUMN email TYPE VARCHAR(255)
ALTER COLUMN email SET NOT NULL

# Squashed (1 operation):
ADD COLUMN email VARCHAR(255) NOT NULL
```

#### Index Optimization

```python
# Original migrations (3 operations):
CREATE INDEX idx_users_email ON users(email)
DROP INDEX idx_users_email
CREATE INDEX idx_users_email_lower ON users(LOWER(email))

# Squashed (1 operation):
CREATE INDEX idx_users_email_lower ON users(LOWER(email))
```

#### Redundancy Elimination

```python
# Original migrations (2 operations):
ADD COLUMN temp_field INTEGER
DROP COLUMN temp_field

# Squashed (0 operations):
-- No operation needed!
```

### Best Practices

1. **Preserve Recent Migrations**: Keep last 10-20 migrations unsquashed for easy rollback
2. **Test Thoroughly**: Verify squashed migration in staging first
3. **Document Changes**: Note which migrations were squashed
4. **Keep Backups**: Store original migrations before deletion

```python
# Production-safe squashing workflow
async def safe_squash(migrations_dir):
    # 1. Backup original migrations
    backup_migrations(migrations_dir)

    # 2. Load all migrations
    migrations = load_all_migrations(migrations_dir)

    # 3. Squash with preservation
    result = await squasher.squash_migrations(
        migrations=migrations,
        target_name='0001_initial_squashed',
        preserve_recent=20  # Keep last 20 migrations
    )

    # 4. Verify squashed migration
    if result.is_valid:
        verified = await squasher.verify_squash(
            adapter=test_adapter,
            original_migrations=migrations[:-20],
            squashed_migration=result.squashed_migration
        )

        if verified:
            # 5. Archive old migrations
            archive_old_migrations(migrations[:-20])

            # 6. Replace with squashed version
            save_squashed_migration(result.squashed_migration)
        else:
            print("Verification failed! Keeping original migrations.")
    else:
        print(f"Squashing failed: {result.conflicts}")
```

---

## Audit Logging

### Complete Migration History Tracking

Track every migration execution for compliance and debugging:

```python
from covet.database.migrations.audit_log import MigrationAuditLog

audit = MigrationAuditLog(adapter)
await audit.initialize()

# Record migration execution
exec_id = await audit.record_execution_start(
    migration_name='0042_add_indexes',
    executor='deploy_bot',
    environment='production',
    metadata={'ticket': 'JIRA-1234', 'approver': 'alice@example.com'}
)

# ... execute migration ...

await audit.record_execution_complete(
    execution_id=exec_id,
    success=True,
    duration=2.5,
    affected_rows=15000,
    sql_executed=['CREATE INDEX idx_users_email ON users(email)']
)
```

### Query History

```python
# Recent migrations
recent = await audit.get_recent_migrations(limit=20)
for migration in recent:
    print(f"{migration['migration_name']}: {migration['status']}")

# Failed migrations
failed = await audit.get_failed_migrations(
    since=datetime.now() - timedelta(days=7)
)

# Specific migration history
history = await audit.get_migration_history('0042_add_indexes')
for execution in history:
    print(f"  {execution['started_at']}: {execution['status']}")
```

### Dashboard Data

```python
dashboard = await audit.get_dashboard_data()

print(f"Total Migrations: {dashboard['statistics']['total_executions']}")
print(f"Success Rate: {dashboard['statistics']['success_rate']:.1f}%")
print(f"Avg Duration: {dashboard['statistics']['average_duration_seconds']:.2f}s")

# Migration velocity (migrations per day)
for day in dashboard['migration_velocity']:
    print(f"  {day['date']}: {day['count']} migrations")
```

### Compliance Reporting

Generate audit reports for compliance:

```python
# SOX/HIPAA/GDPR compliance report
stats = await audit.get_statistics()

report = {
    'period': '2024-Q1',
    'total_changes': stats['total_executions'],
    'success_rate': stats['success_rate'],
    'rollbacks': stats['rollbacks_performed'],
    'failed_changes': stats['failed_executions'],
    'data_affected': stats['total_rows_affected']
}

# Export to JSON for compliance systems
save_compliance_report(report)
```

---

## Production Best Practices

### 1. Zero-Downtime Migrations

**Expand-Contract Pattern** for schema changes:

```python
# Phase 1: Add new column (backward compatible)
class Migration0042(Migration):
    operations = [
        AddColumn('users', ColumnSchema('email_verified', 'BOOLEAN', default=False))
    ]

# Deploy application code that writes to both old and new columns

# Phase 2: Migrate data
class Migration0043(Migration):
    operations = [
        RunSQL("UPDATE users SET email_verified = (email_confirmed = 1)")
    ]

# Phase 3: Drop old column (after full deployment)
class Migration0044(Migration):
    operations = [
        DropColumn('users', 'email_confirmed')
    ]
```

### 2. Large Data Migrations

Use batch processing for large datasets:

```python
class Migration0042(Migration):
    async def apply(self, adapter):
        batch_size = 1000
        offset = 0

        while True:
            # Process in batches
            await adapter.execute(f"""
                UPDATE users
                SET status = 'active'
                WHERE id >= {offset} AND id < {offset + batch_size}
                AND status IS NULL
            """)

            # Check if more rows exist
            count = await adapter.fetch_value(
                f"SELECT COUNT(*) FROM users WHERE id >= {offset + batch_size}"
            )

            if count == 0:
                break

            offset += batch_size

            # Sleep to avoid overwhelming database
            await asyncio.sleep(0.1)
```

### 3. Migration Testing

Always test migrations before production:

```bash
# 1. Test in development
python -m covet.migrations migrate --dry-run

# 2. Test in staging with production data copy
python -m covet.migrations migrate --environment staging

# 3. Verify rollback works
python -m covet.migrations rollback --steps 1
python -m covet.migrations migrate

# 4. Deploy to production
python -m covet.migrations migrate --environment production
```

### 4. Monitoring

Monitor migration execution:

```python
# Production migration execution
async def execute_with_monitoring(migration):
    start_time = time.time()

    try:
        # Execute migration
        await runner.migrate('./migrations', target=migration)

        # Log success metrics
        duration = time.time() - start_time
        metrics.record('migration.success', duration)

        # Alert if slow
        if duration > 60:
            alert_ops(f"Slow migration: {migration} took {duration}s")

    except Exception as e:
        # Log failure
        metrics.record('migration.failure', 1)
        alert_ops(f"Migration failed: {migration} - {e}")

        # Automatic rollback
        await runner.rollback(steps=1)
        raise
```

---

## Troubleshooting

### Migration Conflicts

**Problem**: Migration fails with conflict error

```
Error: Migration 0042_add_column conflicts with existing schema
```

**Solution**:

```python
# Check what changed in database
current_schema = await schema_reader.read_database_schema(adapter)
print(current_schema['users'].columns)

# Regenerate migration
python -m covet.migrations makemigrations --name fix_conflict

# Or manually resolve in migration file
```

### Rename Not Detected

**Problem**: Column rename detected as DROP + ADD

**Solution**:

```python
from covet.database.migrations.rename_detection import RenameDetector

# Lower similarity threshold
detector = RenameDetector(similarity_threshold=0.70)

# Or manually specify rename
detector.add_manual_rename(
    table_name='users',
    old_name='old_column',
    new_name='new_column'
)
```

### Rollback Fails

**Problem**: Rollback fails with foreign key violation

**Solution**:

```python
# Check dependencies
validation = await validator.validate_rollback(migration)
print(f"Dependencies: {validation.dependencies}")

# Rollback in correct order
for migration in reversed(dependent_migrations):
    await runner.rollback(migration)
```

### SQLite Table Locked

**Problem**: Cannot ALTER TABLE - database locked

**Solution**:

```python
# Close all connections
await adapter.close_all_connections()

# Retry with isolation
async with adapter.transaction():
    await workaround.alter_column(...)
```

---

## Migration File Reference

### Complete Migration Example

```python
"""
Migration: 0042_add_user_verification
Generated: 2024-01-15 10:30:00
App: accounts
"""

from covet.database.migrations import Migration

class Migration0042AddUserVerification(Migration):
    """Add email verification fields to users table."""

    dependencies = ['0041_create_users_table']

    operations = [
        {
            'type': 'ADD_COLUMN',
            'table': 'users',
            'column': {
                'name': 'email_verified',
                'type': 'BOOLEAN',
                'nullable': False,
                'default': False
            }
        },
        {
            'type': 'ADD_COLUMN',
            'table': 'users',
            'column': {
                'name': 'verified_at',
                'type': 'TIMESTAMP',
                'nullable': True
            }
        },
        {
            'type': 'ADD_INDEX',
            'table': 'users',
            'index': {
                'name': 'idx_users_email_verified',
                'columns': ['email_verified'],
                'unique': False
            }
        }
    ]

    forward_sql = [
        "ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE users ADD COLUMN verified_at TIMESTAMP",
        "CREATE INDEX idx_users_email_verified ON users(email_verified)"
    ]

    backward_sql = [
        "DROP INDEX IF EXISTS idx_users_email_verified",
        "ALTER TABLE users DROP COLUMN verified_at",
        "ALTER TABLE users DROP COLUMN email_verified"
    ]

    async def apply(self, adapter):
        """Apply migration."""
        for sql in self.forward_sql:
            await adapter.execute(sql)

    async def rollback(self, adapter):
        """Rollback migration."""
        for sql in self.backward_sql:
            await adapter.execute(sql)
```

---

## Summary

This migration system provides:

✅ **Data Safety**: Rename detection, rollback validation, automatic backups
✅ **Production Ready**: Zero-downtime patterns, batch processing, monitoring
✅ **Database Agnostic**: PostgreSQL, MySQL, SQLite with dialect-specific optimizations
✅ **Performance**: Migration squashing for faster fresh installs
✅ **Compliance**: Complete audit trail for SOX/HIPAA/GDPR
✅ **Developer Friendly**: Automatic generation, dry-run mode, clear documentation

Built from **20 years of production database experience**, this system prevents the common migration failures that cause production outages and data loss.

---

## Additional Resources

- **API Reference**: `/docs/API.md`
- **Security Guide**: `/docs/SECURITY.md`
- **Example Migrations**: `/src/covet/database/migrations/examples/`
- **Test Suite**: `/tests/database/test_migrations.py`

For questions or issues, consult the documentation or file a GitHub issue.

**Remember**: Migrations affect your data. Always test in staging first!
