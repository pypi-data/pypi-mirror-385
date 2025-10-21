# Backup & Recovery Runbook

## Production-Grade Backup & Recovery System for CovetPy

**Version:** 1.0.0
**Last Updated:** 2024-10-11
**Maintainer:** CovetPy DevOps Team

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Backup Operations](#backup-operations)
4. [Recovery Operations](#recovery-operations)
5. [Point-in-Time Recovery (PITR)](#point-in-time-recovery)
6. [Automated Scheduling](#automated-scheduling)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Troubleshooting](#troubleshooting)
9. [Emergency Procedures](#emergency-procedures)
10. [Architecture & Implementation](#architecture--implementation)

---

## Overview

### What This System Provides

✅ **Production-Ready Features:**
- Multi-database support (PostgreSQL, MySQL, SQLite)
- Compression (gzip, bzip2, lzma, zstd, lz4)
- Encryption (AES-256-GCM, AES-256-CBC, ChaCha20-Poly1305)
- Point-in-Time Recovery (PITR) for PostgreSQL
- Cloud storage integration (S3, GCS, Azure Blob)
- Automated scheduling with retention policies
- Comprehensive verification and validation
- KMS integration (AWS KMS, Azure Key Vault, GCP KMS, Local)

### System Requirements

**Minimum:**
- Python 3.10+
- 4GB RAM
- 100GB storage for backups
- Database client tools installed (pg_dump, mysqldump, sqlite3)

**Production:**
- Python 3.10+
- 16GB+ RAM
- 1TB+ storage for backups
- Cloud storage account (AWS S3/GCS/Azure)
- KMS account for encryption keys

### Dependencies

```bash
# Core dependencies
pip install cryptography aiosqlite asyncpg aiomysql

# Cloud storage (optional)
pip install boto3 google-cloud-storage azure-storage-blob

# Compression (optional)
pip install zstandard lz4
```

---

## Quick Start

### 1. Basic Backup

```python
import asyncio
from covet.database.backup import BackupManager

async def create_backup():
    # Initialize backup manager
    manager = BackupManager(
        backup_dir="/var/backups/covet",
        catalog_dir="/var/backups/covet/catalog"
    )

    # Create backup
    metadata = await manager.create_backup(
        database_config={
            "database_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "production_db",
            "user": "postgres",
            "password": "secret"
        },
        compress=True,
        encrypt=True,
        encryption_password="strong_password_here"
    )

    print(f"Backup created: {metadata.backup_id}")
    print(f"Size: {metadata.get_human_readable_size()}")

asyncio.run(create_backup())
```

### 2. Basic Restore

```python
import asyncio
from covet.database.backup import BackupManager, RestoreManager

async def restore_backup():
    # Initialize managers
    manager = BackupManager(backup_dir="/var/backups/covet")
    catalog = manager.catalog
    storage_backends = {"local": manager._storage_backends["local"]}

    restore_manager = RestoreManager(
        backup_catalog=catalog,
        storage_backends=storage_backends
    )

    # Restore backup
    await restore_manager.restore_backup(
        backup_id="20241011_120000_abc123",
        target_database={
            "database_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "restored_db",
            "user": "postgres",
            "password": "secret"
        }
    )

    print("Restore completed successfully")

asyncio.run(restore_backup())
```

---

## Backup Operations

### Full Database Backup

#### PostgreSQL

```python
metadata = await manager.create_backup(
    database_config={
        "database_type": "postgresql",
        "host": "db.example.com",
        "port": 5432,
        "database": "production",
        "user": "backup_user",
        "password": os.environ["DB_PASSWORD"]
    },
    compress=True,
    compression_type=CompressionType.GZIP,
    compress_level=9,
    encrypt=True,
    encryption_type=EncryptionType.AES_256_GCM,
    encryption_password="secure_password",
    storage_backend="s3",
    retention_days=30,
    tags={
        "environment": "production",
        "backup_type": "full",
        "created_by": "automated_scheduler"
    }
)
```

#### MySQL

```python
metadata = await manager.create_backup(
    database_config={
        "database_type": "mysql",
        "host": "mysql.example.com",
        "port": 3306,
        "database": "app_database",
        "user": "backup_user",
        "password": os.environ["MYSQL_PASSWORD"]
    },
    compress=True,
    encrypt=True,
    single_transaction=True,  # MySQL-specific: consistent backup
    master_data=2  # Capture binlog position for PITR
)
```

#### SQLite

```python
metadata = await manager.create_backup(
    database_config={
        "database_type": "sqlite",
        "database": "/var/lib/app/production.db"
    },
    method="backup_api",  # Use SQLite backup API for online backup
    compress=True,
    encrypt=True
)
```

### Selective Backup (Tables/Schemas)

```python
# Backup specific tables
metadata = await manager.create_backup(
    database_config=postgresql_config,
    tables=["users", "orders", "products"],
    compress=True
)

# Backup specific schemas
metadata = await manager.create_backup(
    database_config=postgresql_config,
    schemas=["public", "analytics"],
    compress=True
)
```

### Cloud Storage Integration

#### AWS S3

```python
from covet.database.backup import S3Storage

# Add S3 storage backend
s3_storage = S3Storage(
    bucket_name="my-backups",
    region="us-east-1",
    prefix="production/postgresql/"
)
manager.add_storage_backend("s3", s3_storage)

# Create backup to S3
metadata = await manager.create_backup(
    database_config=postgresql_config,
    storage_backend="s3",
    compress=True,
    encrypt=True
)
```

### Encryption with KMS

```python
from covet.database.backup.kms import KMSManager, KMSProvider

# Initialize KMS (AWS KMS)
kms = KMSManager(
    provider=KMSProvider.AWS_KMS,
    region="us-east-1"
)

# Generate encryption key
key, encrypted_key, metadata = await kms.generate_backup_key(
    backup_id="backup_20241011"
)

# Use key for backup
backup_metadata = await manager.create_backup(
    database_config=postgresql_config,
    encrypt=True,
    encryption_key=key
)
```

---

## Recovery Operations

### Full Database Restore

```python
# Restore full backup
result = await restore_manager.restore_backup(
    backup_id="20241011_120000_abc123",
    target_database={
        "database_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "restored_production",
        "user": "postgres",
        "password": "secret"
    },
    verify_before_restore=True,
    verify_after_restore=True
)

print(f"Restore completed in {result['duration_seconds']}s")
```

### Selective Restore

```python
# Restore specific tables
result = await restore_manager.restore_backup(
    backup_id="20241011_120000_abc123",
    target_database=target_config,
    tables=["users", "sessions"],  # Only restore these tables
    verify_after_restore=True
)

# Restore specific schemas
result = await restore_manager.restore_backup(
    backup_id="20241011_120000_abc123",
    target_database=target_config,
    schemas=["public"],  # Only restore public schema
    verify_after_restore=True
)
```

### Restore Verification

```python
from covet.database.backup.restore_verification import RestoreVerification

verifier = RestoreVerification()

# Comprehensive verification
verification_results = await verifier.verify_restore(
    source_config=original_db_config,
    target_config=restored_db_config,
    verification_level="comprehensive"  # quick, standard, comprehensive
)

print(f"Verification status: {verification_results['overall_status']}")
print(f"Pass rate: {verification_results['pass_rate']:.1f}%")

# Check specific results
if verification_results["checks_failed"]:
    print("Failed checks:")
    for check in verification_results["checks_failed"]:
        print(f"  - {check}")
```

---

## Point-in-Time Recovery

### PostgreSQL PITR

#### Step 1: Configure WAL Archiving

```python
from covet.database.backup.pitr_manager import PITRManager

pitr_manager = PITRManager(
    archive_dir="/var/lib/covet/wal_archive"
)

# Configure WAL archiving
config = await pitr_manager.setup_postgresql_wal_archiving(
    data_directory="/var/lib/postgresql/14/main",
    restart_required=True
)

print(config["instructions"])
# Output:
# WAL archiving has been configured.
# Archive directory: /var/lib/covet/wal_archive/postgresql
# PostgreSQL must be restarted for changes to take effect.
# Verify with: SHOW archive_mode; SHOW archive_command;
```

#### Step 2: Create Base Backup

```python
# Create base backup with WAL
backup_result = await pitr_manager.create_postgresql_base_backup(
    config={
        "database_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "production",
        "user": "postgres",
        "password": "secret"
    },
    output_dir="/var/backups/base_backup",
    wal_method="stream"  # stream, fetch, or none
)

print(f"Base backup created")
print(f"Current WAL LSN: {backup_result['current_wal_lsn']}")
```

#### Step 3: Perform Point-in-Time Recovery

```python
# Recover to specific time
pitr_result = await restore_manager.point_in_time_recovery(
    backup_id="base_backup_20241011",
    target_time="2024-10-11 14:30:00",  # Recover to this point in time
    target_database={
        "database_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "recovered_db",
        "user": "postgres",
        "password": "secret",
        "data_directory": "/var/lib/postgresql/14/recovered"
    }
)

print(pitr_result["instructions"])
# Start PostgreSQL to begin recovery:
#   pg_ctl start -D /var/lib/postgresql/14/recovered
```

### MySQL PITR (Binary Log)

```python
# Setup binary log streaming
binlog_config = await pitr_manager.setup_mysql_binlog_streaming(
    config={
        "database_type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "production",
        "user": "root",
        "password": "secret"
    }
)

# Create backup with binlog position
backup_result = await pitr_manager.create_mysql_backup_with_binlog(
    config=mysql_config,
    output_path="/var/backups/mysql_backup.sql",
    master_data=2  # Include binlog position
)

print(f"Binlog position: {backup_result['binlog_file_after']} @ {backup_result['binlog_position_after']}")
```

### Verify PITR Capability

```python
# Check if PITR is properly configured
capabilities = await pitr_manager.verify_pitr_capability(
    database_type="postgresql",
    config=postgresql_config
)

if capabilities["pitr_supported"]:
    print("✅ PITR is fully configured")
else:
    print("❌ PITR configuration incomplete:")
    if not capabilities["archiving_enabled"]:
        print("  - WAL archiving not enabled")
    if not capabilities["archive_directory_exists"]:
        print("  - Archive directory not found")
    if not capabilities["base_backup_possible"]:
        print("  - Cannot create base backup")
```

---

## Automated Scheduling

### Basic Schedule

```python
from covet.database.backup import BackupScheduler, BackupSchedule, ScheduleFrequency

scheduler = BackupScheduler(backup_manager=manager)

# Daily backup at 2 AM
daily_schedule = BackupSchedule(
    name="production_daily",
    description="Daily production database backup",
    database_config=postgresql_config,
    frequency=ScheduleFrequency.DAILY,
    hour=2,
    minute=0,
    compress=True,
    encrypt=True,
    storage_backend="s3",
    retention_days=30
)

scheduler.add_schedule(daily_schedule)
await scheduler.start()
```

### Advanced Scheduling with GFS Retention

```python
from covet.database.backup import RetentionPolicy

# Grandfather-Father-Son retention policy
gfs_schedule = BackupSchedule(
    name="production_gfs",
    database_config=postgresql_config,
    frequency=ScheduleFrequency.DAILY,
    hour=3,
    compress=True,
    encrypt=True,
    storage_backend="s3",

    # GFS retention policy
    retention_policy=RetentionPolicy.GFS,
    gfs_daily=7,      # Keep 7 daily backups
    gfs_weekly=4,     # Keep 4 weekly backups
    gfs_monthly=12,   # Keep 12 monthly backups

    # Notifications
    notify_on_failure=True,
    alert_email="ops@example.com",

    # Retry configuration
    max_retries=3,
    retry_delay_seconds=300
)

scheduler.add_schedule(gfs_schedule)
```

### Multiple Database Schedules

```python
# PostgreSQL production - hourly
pg_hourly = BackupSchedule(
    name="postgresql_hourly",
    database_config=postgresql_config,
    frequency=ScheduleFrequency.HOURLY,
    minute=30,
    compress=True,
    retention_policy=RetentionPolicy.SIMPLE,
    retention_count=24  # Keep last 24 hourly backups
)

# MySQL analytics - daily
mysql_daily = BackupSchedule(
    name="mysql_analytics_daily",
    database_config=mysql_config,
    frequency=ScheduleFrequency.DAILY,
    hour=1,
    compress=True,
    encrypt=True,
    retention_days=7
)

# SQLite app database - weekly
sqlite_weekly = BackupSchedule(
    name="sqlite_weekly",
    database_config=sqlite_config,
    frequency=ScheduleFrequency.WEEKLY,
    day_of_week=0,  # Monday
    hour=2,
    compress=True,
    retention_count=4  # Keep 4 weekly backups
)

scheduler.add_schedule(pg_hourly)
scheduler.add_schedule(mysql_daily)
scheduler.add_schedule(sqlite_weekly)

await scheduler.start()
```

### Manual Trigger

```python
# Manually trigger a scheduled backup
result = await scheduler.run_schedule_now("production_daily")

if result.success:
    print(f"Backup completed: {result.backup_id}")
else:
    print(f"Backup failed: {result.error_message}")
```

---

## Monitoring & Alerting

### Check Backup Status

```python
# List all backups
backups = manager.list_backups()
for backup in backups:
    print(f"{backup.backup_id}: {backup.status.value} - {backup.get_human_readable_size()}")

# Filter by status
from covet.database.backup import BackupStatus

failed_backups = manager.list_backups(status=BackupStatus.FAILED)
if failed_backups:
    print(f"⚠️  {len(failed_backups)} failed backups found!")

# Get statistics
stats = manager.get_statistics()
print(f"Total backups: {stats['total_backups']}")
print(f"Total size: {stats['total_size_bytes'] / (1024**3):.2f} GB")
print(f"Success rate: {stats['success_rate']:.1f}%")
```

### Verify Backups

```python
# Verify backup integrity
is_valid = await manager.verify_backup(
    backup_id="20241011_120000_abc123",
    verify_restore=True  # Also test restore
)

if is_valid:
    print("✅ Backup verified successfully")
else:
    print("❌ Backup verification failed")
```

### Scheduler Monitoring

```python
# Get recent backup results
results = scheduler.get_recent_results(limit=10)

for result in results:
    status = "✅" if result.success else "❌"
    print(f"{status} {result.schedule_name}: {result.duration_seconds:.1f}s")
    if not result.success:
        print(f"   Error: {result.error_message}")

# Check next run times
for schedule in scheduler.list_schedules():
    next_run = scheduler.get_next_run_time(schedule.name)
    print(f"{schedule.name}: Next run at {next_run}")
```

---

## Troubleshooting

### Common Issues

#### 1. Encrypted Backup Cannot Be Decrypted

**Problem:** Error when trying to restore encrypted backup.

**Solution:**
```python
# Ensure encryption metadata is present
metadata = manager.catalog.get(backup_id)
print(f"Encryption metadata: {metadata.custom_metadata}")

# Should contain: iv, tag/nonce
# If missing, backup may be corrupted

# Verify encryption key is available
key_file = manager.catalog_dir / f"{backup_id}.key"
if not key_file.exists():
    print("❌ Encryption key not found!")
else:
    print("✅ Encryption key found")
```

#### 2. PITR Not Working

**Problem:** Point-in-time recovery fails or WAL files not found.

**Solution:**
```python
# Verify WAL archiving is enabled
capabilities = await pitr_manager.verify_pitr_capability(
    database_type="postgresql",
    config=postgresql_config
)

if not capabilities["archiving_enabled"]:
    # Re-configure WAL archiving
    await pitr_manager.setup_postgresql_wal_archiving(
        data_directory="/var/lib/postgresql/14/main"
    )
    # Restart PostgreSQL
    print("Restart PostgreSQL for changes to take effect")

# Check WAL archive directory
import os
wal_dir = "/var/lib/covet/wal_archive/postgresql"
wal_files = os.listdir(wal_dir)
print(f"WAL files in archive: {len(wal_files)}")
```

#### 3. Backup Too Slow

**Problem:** Backup takes too long for large databases.

**Solution:**
```python
# Use parallel backup (PostgreSQL)
metadata = await manager.create_backup(
    database_config=postgresql_config,
    format="directory",
    jobs=4,  # Parallel jobs
    compress=True,
    compression_type=CompressionType.ZSTD  # Faster compression
)

# For MySQL, use --single-transaction for consistency without locks
metadata = await manager.create_backup(
    database_config=mysql_config,
    single_transaction=True
)
```

#### 4. Out of Disk Space

**Problem:** Backup directory running out of space.

**Solution:**
```python
# Clean up old backups
deleted = await manager.cleanup_expired_backups(dry_run=False)
print(f"Deleted {len(deleted)} expired backups")

# Adjust retention policy
schedule.retention_days = 14  # Reduce from 30 to 14 days

# Use higher compression
metadata = await manager.create_backup(
    database_config=postgresql_config,
    compress=True,
    compression_type=CompressionType.LZMA,  # Best compression
    compress_level=9
)
```

---

## Emergency Procedures

### Emergency Restore (Disaster Recovery)

**Scenario:** Production database is corrupted and needs immediate restore.

```bash
# 1. Stop application traffic
# 2. Identify last good backup
python -c "
from covet.database.backup import BackupManager
import asyncio

async def find_last_good_backup():
    manager = BackupManager(backup_dir='/var/backups/covet')
    backups = manager.list_backups(database_name='production')

    # Find most recent successful backup
    for backup in sorted(backups, key=lambda x: x.created_at, reverse=True):
        if backup.status.value == 'completed':
            print(f'Last good backup: {backup.backup_id}')
            print(f'Created: {backup.created_at}')
            break

asyncio.run(find_last_good_backup())
"

# 3. Restore backup
python -c "
from covet.database.backup import BackupManager, RestoreManager
import asyncio

async def emergency_restore():
    manager = BackupManager(backup_dir='/var/backups/covet')
    restore_manager = RestoreManager(
        backup_catalog=manager.catalog,
        storage_backends=manager._storage_backends
    )

    await restore_manager.restore_backup(
        backup_id='BACKUP_ID_FROM_STEP_2',
        target_database={
            'database_type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'database': 'production',
            'user': 'postgres',
            'password': 'secret'
        },
        verify_after_restore=True
    )

asyncio.run(emergency_restore())
"

# 4. Verify database
psql -h localhost -U postgres -d production -c "SELECT COUNT(*) FROM users;"

# 5. Resume application traffic
```

### Data Loss - Point-in-Time Recovery

**Scenario:** Data was accidentally deleted, need to recover to before deletion.

```python
# 1. Identify deletion time
deletion_time = "2024-10-11 14:25:00"

# 2. Restore to point before deletion
pitr_result = await restore_manager.point_in_time_recovery(
    backup_id="base_backup_20241011_020000",
    target_time="2024-10-11 14:20:00",  # 5 minutes before deletion
    target_database={
        "database_type": "postgresql",
        "host": "localhost",
        "port": 5433,  # Different port to avoid conflict
        "database": "production_recovered",
        "user": "postgres",
        "password": "secret",
        "data_directory": "/var/lib/postgresql/14/recovered"
    }
)

# 3. Start recovered database
# pg_ctl start -D /var/lib/postgresql/14/recovered

# 4. Extract deleted data
# pg_dump -h localhost -p 5433 -U postgres -t deleted_table production_recovered > recovered_data.sql

# 5. Import recovered data to production
# psql -h localhost -p 5432 -U postgres production < recovered_data.sql
```

---

## Architecture & Implementation

### System Components

```
┌─────────────────────────────────────────────────┐
│           Backup & Recovery System              │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌────────────────────────┐  │
│  │   Backup     │  │   Restore Manager      │  │
│  │   Manager    │  │   - Full restore       │  │
│  │              │  │   - Selective restore  │  │
│  │  - Create    │  │   - PITR              │  │
│  │  - Verify    │  │   - Verification      │  │
│  │  - Delete    │  └────────────────────────┘  │
│  │  - Schedule  │                               │
│  └──────────────┘                               │
│                                                 │
│  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Compression │  │   Encryption Engine    │  │
│  │  - GZIP      │  │   - AES-256-GCM       │  │
│  │  - BZIP2     │  │   - AES-256-CBC       │  │
│  │  - LZMA      │  │   - ChaCha20-Poly1305 │  │
│  │  - ZSTD      │  │   - KMS Integration   │  │
│  └──────────────┘  └────────────────────────┘  │
│                                                 │
│  ┌──────────────┐  ┌────────────────────────┐  │
│  │   Storage    │  │   PITR Manager         │  │
│  │  - Local     │  │   - WAL archiving      │  │
│  │  - S3        │  │   - Binlog streaming   │  │
│  │  - GCS       │  │   - Recovery config    │  │
│  │  - Azure     │  └────────────────────────┘  │
│  └──────────────┘                               │
│                                                 │
│  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Scheduler   │  │   Verification         │  │
│  │  - Cron      │  │   - Checksum          │  │
│  │  - Retention │  │   - Row counts        │  │
│  │  - GFS       │  │   - Schema validation │  │
│  └──────────────┘  └────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Backup Flow

```
1. Configure → 2. Create → 3. Compress → 4. Encrypt → 5. Upload → 6. Catalog
      │              │           │            │            │           │
      │              │           │            │            │           │
   Database      pg_dump/     gzip/       AES-256/       S3/        Metadata
    Config      mysqldump    zstd      ChaCha20        GCS         Storage
                             lzma                      Azure
```

### Restore Flow

```
1. Locate → 2. Download → 3. Decrypt → 4. Decompress → 5. Restore → 6. Verify
      │            │            │             │             │            │
      │            │            │             │             │            │
   Catalog       S3/GCS      Decrypt      gunzip/       pg_restore/   Validation
   Lookup        Azure       w/ Key       unzstd        mysql         Checks
```

### File Structure

```
/var/backups/covet/
├── catalog/                    # Backup metadata
│   ├── backup_id.json
│   ├── backup_id.key          # Encryption keys
│   └── catalog.db
├── backups/                    # Local backups
│   ├── postgresql/
│   │   └── production/
│   │       └── 2024/10/11/
│   │           └── backup_id.backup.gz.enc
│   └── mysql/
└── wal_archive/               # PITR archives
    ├── postgresql/            # WAL files
    └── mysql/                 # Binary logs
```

### Configuration Files

**PostgreSQL WAL Archiving:**
```sql
-- postgresql.auto.conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/covet/wal_archive/postgresql/%f && cp %p /var/lib/covet/wal_archive/postgresql/%f'
wal_keep_size = 1GB
max_wal_senders = 3
```

**MySQL Binary Logging:**
```ini
# my.cnf
[mysqld]
log-bin=mysql-bin
server-id=1
binlog_format=ROW
expire_logs_days=7
max_binlog_size=1G
```

---

## Best Practices

### Backup Best Practices

1. **Test Restores Regularly** - Verify backups work every week
2. **Use Encryption** - Always encrypt backups containing sensitive data
3. **Multiple Storage Locations** - Keep backups in at least 2 locations
4. **Monitor Backup Size** - Track backup growth trends
5. **Document Procedures** - Keep runbook updated
6. **Automate Everything** - Use scheduler for consistent backups
7. **Validate After Backup** - Always verify checksum

### Security Best Practices

1. **Use KMS** - Never store encryption keys with backups
2. **Rotate Keys** - Rotate encryption keys quarterly
3. **Least Privilege** - Backup user should have minimal permissions
4. **Audit Logs** - Enable and monitor backup/restore audit logs
5. **Secure Transfer** - Use TLS/SSL for all network transfers
6. **Access Control** - Restrict backup storage access

### Performance Best Practices

1. **Parallel Backups** - Use jobs parameter for large databases
2. **Compression Choice** - ZSTD for speed, LZMA for size
3. **Off-Peak Backups** - Schedule during low-traffic periods
4. **Incremental Backups** - Consider for very large databases
5. **Network Bandwidth** - Monitor and throttle if needed

---

## Appendix

### Supported Database Versions

- **PostgreSQL:** 12, 13, 14, 15, 16
- **MySQL:** 5.7, 8.0, 8.1
- **MariaDB:** 10.5, 10.6, 10.11
- **SQLite:** 3.35+

### Supported Compression Formats

| Format | Speed | Ratio | CPU | Use Case |
|--------|-------|-------|-----|----------|
| GZIP   | Fast  | Good  | Low | General purpose |
| BZIP2  | Slow  | Best  | High | Maximum compression |
| LZMA   | Slowest | Best | High | Archive storage |
| ZSTD   | Fastest | Good | Low | Real-time backups |
| LZ4    | Fastest | Fair | Low | Speed critical |

### Supported Encryption Algorithms

| Algorithm | Security | Speed | Use Case |
|-----------|----------|-------|----------|
| AES-256-GCM | Highest | Fast | Recommended |
| AES-256-CBC | High | Fast | Legacy compatibility |
| ChaCha20-Poly1305 | Highest | Fastest | Mobile/IoT |

### Support & Contact

- **Documentation:** https://docs.covetpy.dev/backup
- **Issues:** https://github.com/covetpy/covetpy/issues
- **Email:** support@covetpy.dev
- **Emergency:** oncall@covetpy.dev

---

**End of Runbook**
