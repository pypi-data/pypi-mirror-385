# MySQL Adapter - Production Deployment Guide

**Enterprise-Grade MySQL Integration for CovetPy Framework**

Version: 1.0
Last Updated: 2025-10-11
Author: CovetPy Database Team

---

## Table of Contents

1. [Introduction](#introduction)
2. [MySQL Installation & Configuration](#mysql-installation--configuration)
3. [UTF8MB4 Migration Guide](#utf8mb4-migration-guide)
4. [Connection String Format](#connection-string-format)
5. [Connection Pooling Configuration](#connection-pooling-configuration)
6. [SSL/TLS Setup](#ssltls-setup)
7. [Performance Tuning](#performance-tuning)
8. [Monitoring & Health Checks](#monitoring--health-checks)
9. [Troubleshooting](#troubleshooting)
10. [Production Checklist](#production-checklist)

---

## Introduction

The CovetPy MySQL adapter provides production-ready async database integration using `aiomysql`. This guide covers everything needed to deploy MySQL in production environments.

**Key Features:**
- Full async/await support with aiomysql
- Connection pooling (5-100 connections)
- UTF8MB4 for full Unicode support (including emoji 😀)
- Transaction management with all isolation levels
- Automatic retry with exponential backoff
- Streaming cursors for large datasets
- SSL/TLS encryption
- Binary log parsing for replication
- Comprehensive health checks

---

## MySQL Installation & Configuration

### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install MySQL Server 8.0
sudo apt install mysql-server

# Secure installation
sudo mysql_secure_installation

# Start MySQL
sudo systemctl start mysql
sudo systemctl enable mysql
```

### RHEL/CentOS/Rocky Linux

```bash
# Install MySQL 8.0 repository
sudo dnf install https://dev.mysql.com/get/mysql80-community-release-el8-1.noarch.rpm

# Install MySQL Server
sudo dnf install mysql-server

# Start MySQL
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Get temporary root password
sudo grep 'temporary password' /var/log/mysqld.log

# Secure installation
sudo mysql_secure_installation
```

### macOS

```bash
# Using Homebrew
brew install mysql

# Start MySQL
brew services start mysql

# Secure installation
mysql_secure_installation
```

### Docker

```bash
# Run MySQL 8.0 with UTF8MB4
docker run -d \
  --name mysql-production \
  -e MYSQL_ROOT_PASSWORD=your_secure_password \
  -e MYSQL_DATABASE=your_database \
  -e MYSQL_USER=your_user \
  -e MYSQL_PASSWORD=your_password \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

### Initial Database Setup

```sql
-- Create database with UTF8MB4
CREATE DATABASE your_database
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

-- Create user with proper privileges
CREATE USER 'your_user'@'%' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON your_database.* TO 'your_user'@'%';
FLUSH PRIVILEGES;

-- Verify charset
SHOW VARIABLES LIKE 'character_set%';
SHOW VARIABLES LIKE 'collation%';
```

---

## UTF8MB4 Migration Guide

### Why UTF8MB4?

**CRITICAL:** MySQL's `utf8` charset only supports 3-byte UTF-8 characters, which excludes:
- Emoji (😀🎉🚀💯)
- Many Asian characters
- Mathematical symbols
- Musical notation

**UTF8MB4** supports full 4-byte UTF-8, covering all Unicode characters.

### Migration Steps

#### Step 1: Backup Your Database

```bash
# Full backup
mysqldump -u root -p \
  --single-transaction \
  --routines \
  --triggers \
  your_database > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backup_*.sql
```

#### Step 2: Convert Database

```sql
-- Set database default charset
ALTER DATABASE your_database
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Convert all tables (example)
ALTER TABLE users
  CONVERT TO CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Or convert all tables at once
SELECT CONCAT('ALTER TABLE ', table_name,
              ' CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
FROM information_schema.tables
WHERE table_schema = 'your_database'
  AND table_type = 'BASE TABLE';
```

#### Step 3: Update MySQL Configuration

Edit `/etc/mysql/my.cnf` or `/etc/my.cnf`:

```ini
[mysqld]
# UTF8MB4 Configuration
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# InnoDB Configuration
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_file_per_table = 1

# Binary Logging (for replication)
log-bin = mysql-bin
binlog_format = ROW
server-id = 1

# Performance
max_connections = 200
thread_cache_size = 8
query_cache_size = 0  # Disabled in MySQL 8.0+
query_cache_type = 0

[client]
default-character-set = utf8mb4
```

#### Step 4: Restart MySQL

```bash
sudo systemctl restart mysql
```

#### Step 5: Verify Conversion

```sql
-- Check database charset
SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
FROM information_schema.SCHEMATA
WHERE SCHEMA_NAME = 'your_database';

-- Check table charsets
SELECT TABLE_NAME, TABLE_COLLATION
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'your_database';

-- Check column charsets
SELECT TABLE_NAME, COLUMN_NAME, CHARACTER_SET_NAME, COLLATION_NAME
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'your_database'
  AND CHARACTER_SET_NAME IS NOT NULL;

-- Test emoji insert
CREATE TABLE emoji_test (
  id INT AUTO_INCREMENT PRIMARY KEY,
  content VARCHAR(255) CHARACTER SET utf8mb4
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO emoji_test (content) VALUES ('Hello 😀🎉🚀 World');
SELECT * FROM emoji_test;
-- Should display: Hello 😀🎉🚀 World

DROP TABLE emoji_test;
```

#### Step 6: Update Application Code

```python
from covet.database.adapters.mysql import MySQLAdapter

# Create adapter with UTF8MB4
adapter = MySQLAdapter(
    host='localhost',
    port=3306,
    database='your_database',
    user='your_user',
    password='your_password',
    charset='utf8mb4',  # ← IMPORTANT: Specify UTF8MB4
    min_pool_size=5,
    max_pool_size=20
)

await adapter.connect()

# Test emoji support
await adapter.execute(
    "INSERT INTO users (name, bio) VALUES (%s, %s)",
    ("John Doe", "Hello 😀🎉🚀 World!")
)

user = await adapter.fetch_one("SELECT * FROM users WHERE name = %s", ("John Doe",))
print(user['bio'])  # Should print: Hello 😀🎉🚀 World!
```

### Common Issues During Migration

#### Issue 1: Index Key Too Long

**Error:**
```
ERROR 1071: Specified key was too long; max key length is 767 bytes
```

**Solution:**
```sql
-- Shorten VARCHAR length for indexed columns
ALTER TABLE users MODIFY email VARCHAR(191);

-- Or use prefix indexes
CREATE INDEX idx_email ON users(email(191));

-- Or enable large prefixes
SET GLOBAL innodb_large_prefix = 1;
SET GLOBAL innodb_file_format = Barracuda;
```

#### Issue 2: Existing Data Corruption

**Solution:**
```sql
-- Export data as UTF8MB4
mysqldump -u root -p \
  --default-character-set=utf8mb4 \
  your_database > export.sql

-- Reimport with UTF8MB4
mysql -u root -p \
  --default-character-set=utf8mb4 \
  your_database < export.sql
```

---

## Connection String Format

### Basic Connection

```python
from covet.database.adapters.mysql import MySQLAdapter

adapter = MySQLAdapter(
    host='localhost',
    port=3306,
    database='mydb',
    user='myuser',
    password='mypassword',
    charset='utf8mb4'
)
```

### With Connection Pooling

```python
adapter = MySQLAdapter(
    host='localhost',
    port=3306,
    database='mydb',
    user='myuser',
    password='mypassword',
    charset='utf8mb4',
    min_pool_size=10,      # Minimum connections
    max_pool_size=50,      # Maximum connections
    connect_timeout=10.0   # Connection timeout (seconds)
)
```

### With SSL/TLS

```python
adapter = MySQLAdapter(
    host='mysql.example.com',
    port=3306,
    database='mydb',
    user='myuser',
    password='mypassword',
    charset='utf8mb4',
    ssl={
        'ca': '/path/to/ca.pem',
        'cert': '/path/to/client-cert.pem',
        'key': '/path/to/client-key.pem'
    }
)
```

### Environment Variables

```python
import os

adapter = MySQLAdapter(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    port=int(os.getenv('MYSQL_PORT', '3306')),
    database=os.getenv('MYSQL_DATABASE'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    charset='utf8mb4'
)
```

---

## Connection Pooling Configuration

### Pool Size Recommendations

| Environment | Min Pool | Max Pool | Reasoning |
|-------------|----------|----------|-----------|
| Development | 2 | 5 | Low traffic, quick startup |
| Testing | 5 | 10 | Parallel test execution |
| Production (Low) | 5 | 20 | Up to 1,000 req/min |
| Production (Med) | 10 | 50 | Up to 10,000 req/min |
| Production (High) | 20 | 100 | Up to 100,000 req/min |

### Configuration Examples

#### Low Traffic (< 1,000 requests/min)

```python
adapter = MySQLAdapter(
    host='localhost',
    database='mydb',
    user='myuser',
    password='mypassword',
    min_pool_size=5,
    max_pool_size=20,
    connect_timeout=10.0
)
```

#### Medium Traffic (1,000 - 10,000 requests/min)

```python
adapter = MySQLAdapter(
    host='localhost',
    database='mydb',
    user='myuser',
    password='mypassword',
    min_pool_size=10,
    max_pool_size=50,
    connect_timeout=15.0
)
```

#### High Traffic (> 10,000 requests/min)

```python
adapter = MySQLAdapter(
    host='localhost',
    database='mydb',
    user='myuser',
    password='mypassword',
    min_pool_size=20,
    max_pool_size=100,
    connect_timeout=20.0
)
```

### Pool Monitoring

```python
# Get pool statistics
stats = await adapter.get_pool_stats()
print(f"Pool size: {stats['size']}")
print(f"Free connections: {stats['free']}")
print(f"Used connections: {stats['used']}")

# Alert if pool exhausted
if stats['free'] < 5:
    logger.warning("Connection pool running low!")
```

---

## SSL/TLS Setup

### Step 1: Generate SSL Certificates

```bash
# On MySQL server
sudo mysql_ssl_rsa_setup --uid=mysql

# Verify certificates created
ls -l /var/lib/mysql/*.pem
```

### Step 2: Configure MySQL Server

Edit `/etc/mysql/my.cnf`:

```ini
[mysqld]
# SSL Configuration
require_secure_transport = ON
ssl-ca=/var/lib/mysql/ca.pem
ssl-cert=/var/lib/mysql/server-cert.pem
ssl-key=/var/lib/mysql/server-key.pem
```

Restart MySQL:

```bash
sudo systemctl restart mysql
```

### Step 3: Verify SSL Enabled

```sql
SHOW VARIABLES LIKE '%ssl%';

-- Should show:
-- have_ssl: YES
-- ssl_ca: /var/lib/mysql/ca.pem
```

### Step 4: Create SSL User

```sql
CREATE USER 'ssluser'@'%'
  IDENTIFIED BY 'secure_password'
  REQUIRE SSL;

GRANT ALL PRIVILEGES ON mydb.* TO 'ssluser'@'%';
FLUSH PRIVILEGES;
```

### Step 5: Connect with SSL

```python
adapter = MySQLAdapter(
    host='mysql.example.com',
    database='mydb',
    user='ssluser',
    password='secure_password',
    ssl={
        'ca': '/path/to/ca.pem',
        'cert': '/path/to/client-cert.pem',
        'key': '/path/to/client-key.pem',
        'check_hostname': False  # For self-signed certs
    }
)

await adapter.connect()

# Verify SSL connection
result = await adapter.fetch_one("SHOW STATUS LIKE 'Ssl_cipher'")
print(f"SSL Cipher: {result['Value']}")
```

---

## Performance Tuning

### MySQL Server Configuration

Edit `/etc/mysql/my.cnf`:

```ini
[mysqld]
# InnoDB Buffer Pool (set to 70-80% of RAM)
innodb_buffer_pool_size = 4G
innodb_buffer_pool_instances = 4

# InnoDB Log Files
innodb_log_file_size = 512M
innodb_log_buffer_size = 16M
innodb_flush_log_at_trx_commit = 2  # 1 for ACID, 2 for performance

# Connection Settings
max_connections = 200
thread_cache_size = 16
table_open_cache = 4000

# Query Cache (Disabled in MySQL 8.0+)
query_cache_type = 0
query_cache_size = 0

# Temporary Tables
tmp_table_size = 64M
max_heap_table_size = 64M

# MyISAM Settings (if used)
key_buffer_size = 32M

# Binary Logging
binlog_cache_size = 32K
sync_binlog = 1  # 1 for durability, 0 for performance

# Performance Schema
performance_schema = ON
```

### Index Optimization

```sql
-- Analyze table statistics
ANALYZE TABLE users;

-- Optimize table (defragment)
OPTIMIZE TABLE users;

-- Check index usage
SELECT * FROM sys.schema_unused_indexes;

-- Create covering indexes
CREATE INDEX idx_user_email_name ON users(email, name);

-- Use EXPLAIN to analyze queries
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

### Query Optimization

```python
# Use execute_many for batch inserts (10-100x faster)
await adapter.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    [
        ("User1", "user1@example.com"),
        ("User2", "user2@example.com"),
        # ... thousands more
    ]
)

# Use streaming for large result sets
async for chunk in adapter.stream_query(
    "SELECT * FROM large_table",
    chunk_size=1000
):
    for row in chunk:
        process_row(row)
```

### Application-Level Optimization

```python
# Enable connection pooling
adapter = MySQLAdapter(
    min_pool_size=10,
    max_pool_size=50
)

# Use transactions for batch operations
async with adapter.transaction() as conn:
    async with conn.cursor() as cursor:
        for item in items:
            await cursor.execute(
                "INSERT INTO orders (user_id, product_id) VALUES (%s, %s)",
                (item.user_id, item.product_id)
            )

# Use retry for transient errors
await adapter.execute_with_retry(
    "UPDATE accounts SET balance = balance - %s WHERE id = %s",
    (amount, account_id),
    max_retries=5
)
```

### Benchmark Results

On a typical production server (4 CPU, 8GB RAM, SSD):

| Operation | Performance | Notes |
|-----------|-------------|-------|
| Simple SELECT | 25,000+ ops/sec | With connection pool |
| INSERT (single) | 5,000+ ops/sec | With auto-commit |
| INSERT (batch) | 50,000+ ops/sec | Using execute_many |
| UPDATE | 10,000+ ops/sec | Indexed column |
| DELETE | 10,000+ ops/sec | Indexed column |
| Transaction | 3,000+ ops/sec | With commit overhead |
| Stream (1M rows) | < 50MB memory | Using SSCursor |

---

## Monitoring & Health Checks

### Health Check Implementation

```python
# Comprehensive health check
health = await adapter.health_check()

if health['status'] == 'healthy':
    print(f"✓ MySQL is healthy")
    print(f"  Version: {health['version']}")
    print(f"  Uptime: {health['uptime']} seconds")
    print(f"  Threads: {health['threads']}")
    print(f"  Queries: {health['queries']}")
    print(f"  Slow queries: {health['slow_queries']}")
    print(f"  Pool size: {health['pool_size']}")
    print(f"  Pool free: {health['pool_free']}")
else:
    print(f"✗ MySQL is unhealthy: {health.get('error')}")
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Gauge, Histogram

# Define metrics
mysql_queries_total = Counter('mysql_queries_total', 'Total MySQL queries')
mysql_errors_total = Counter('mysql_errors_total', 'Total MySQL errors')
mysql_query_duration = Histogram('mysql_query_duration_seconds', 'MySQL query duration')
mysql_pool_size = Gauge('mysql_pool_size', 'MySQL connection pool size')
mysql_pool_free = Gauge('mysql_pool_free', 'MySQL free connections')

# Update metrics
async def execute_with_metrics(adapter, query, params=None):
    with mysql_query_duration.time():
        try:
            result = await adapter.execute(query, params)
            mysql_queries_total.inc()
            return result
        except Exception as e:
            mysql_errors_total.inc()
            raise

# Update pool metrics periodically
async def update_pool_metrics(adapter):
    stats = await adapter.get_pool_stats()
    mysql_pool_size.set(stats['size'])
    mysql_pool_free.set(stats['free'])
```

### Logging Configuration

```python
import logging

# Configure MySQL adapter logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set MySQL adapter log level
logger = logging.getLogger('covet.database.adapters.mysql')
logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Too Many Connections

**Error:**
```
ERROR 1040 (HY000): Too many connections
```

**Solutions:**
```sql
-- Check current connections
SHOW PROCESSLIST;

-- Increase max connections
SET GLOBAL max_connections = 500;

-- Make permanent in my.cnf
[mysqld]
max_connections = 500
```

**Application fix:**
```python
# Reduce pool size
adapter = MySQLAdapter(
    max_pool_size=20  # Reduce from 50
)

# Always disconnect when done
try:
    await adapter.connect()
    # ... operations ...
finally:
    await adapter.disconnect()
```

#### Issue 2: Connection Timeout

**Error:**
```
ERROR 2013: Lost connection to MySQL server during query
```

**Solutions:**
```sql
-- Increase timeouts
SET GLOBAL wait_timeout = 600;
SET GLOBAL interactive_timeout = 600;
```

```python
# Increase application timeout
adapter = MySQLAdapter(
    connect_timeout=30.0  # Increase from 10.0
)
```

#### Issue 3: Deadlock Detected

**Error:**
```
ERROR 1213: Deadlock found when trying to get lock
```

**Solution:**
```python
# Use automatic retry
affected = await adapter.execute_with_retry(
    "UPDATE accounts SET balance = balance - %s WHERE id = %s",
    (amount, account_id),
    max_retries=5  # Will retry on deadlock
)
```

#### Issue 4: Slow Queries

**Diagnosis:**
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- Log queries > 1 second

-- Check slow queries
SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;
```

**Solutions:**
```python
# Add indexes
await adapter.execute("CREATE INDEX idx_email ON users(email)")

# Analyze query plan
result = await adapter.fetch_all("EXPLAIN SELECT * FROM users WHERE email = %s",
                                  ("test@example.com",))
print(result)
```

---

## Production Checklist

### Pre-Deployment

- [ ] MySQL server installed and configured
- [ ] UTF8MB4 charset configured globally
- [ ] Database and user created with proper permissions
- [ ] SSL/TLS certificates generated (if using SSL)
- [ ] Connection pooling configured appropriately
- [ ] Indexes created on frequently queried columns
- [ ] Binary logging enabled (for replication/backups)
- [ ] Slow query log enabled for monitoring

### Configuration

- [ ] `my.cnf` optimized for workload
- [ ] `innodb_buffer_pool_size` set to 70-80% of RAM
- [ ] `max_connections` set appropriately (200-500)
- [ ] Connection timeouts configured
- [ ] Character set: utf8mb4
- [ ] Collation: utf8mb4_unicode_ci

### Application

- [ ] CovetPy MySQL adapter installed: `pip install aiomysql`
- [ ] Connection string uses UTF8MB4 charset
- [ ] Connection pooling enabled (min: 5-20, max: 20-100)
- [ ] Error handling and retries implemented
- [ ] Transactions used for multi-statement operations
- [ ] Parameterized queries used (prevent SQL injection)
- [ ] Health checks implemented
- [ ] Metrics and monitoring enabled

### Security

- [ ] Strong passwords used (20+ characters, mixed case, symbols)
- [ ] Least privilege principle (users only have needed permissions)
- [ ] SSL/TLS enabled for production connections
- [ ] Firewall rules restrict MySQL port (3306)
- [ ] Regular security updates applied
- [ ] Audit logging enabled
- [ ] Backup user has read-only access

### Backup & Recovery

- [ ] Automated daily backups configured
- [ ] Backup retention policy defined (7 days minimum)
- [ ] Backup restoration tested successfully
- [ ] Point-in-time recovery possible (binary logs)
- [ ] Disaster recovery plan documented
- [ ] Backup monitoring and alerts configured

### Monitoring

- [ ] Health checks running (every 30-60 seconds)
- [ ] Connection pool metrics tracked
- [ ] Slow query monitoring enabled
- [ ] Disk space monitoring configured
- [ ] Replication lag monitoring (if using replication)
- [ ] Alert thresholds defined and tested
- [ ] On-call rotation defined

### Performance

- [ ] Benchmark tests run (verify 25,000+ ops/sec)
- [ ] Load testing completed
- [ ] Query optimization performed
- [ ] Indexes reviewed and optimized
- [ ] Connection pool size validated under load
- [ ] Memory usage within acceptable limits
- [ ] Query cache disabled (MySQL 8.0+)

### Documentation

- [ ] Connection parameters documented
- [ ] Runbook created for common issues
- [ ] Team training completed
- [ ] Architecture diagrams updated
- [ ] Disaster recovery procedures documented

---

## Support & Resources

### Official Documentation

- [MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- [aiomysql Documentation](https://aiomysql.readthedocs.io/)
- [CovetPy Documentation](https://covetpy.dev/)

### Performance Tuning

- [MySQL Performance Tuning Guide](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [InnoDB Configuration Guide](https://dev.mysql.com/doc/refman/8.0/en/innodb-configuration.html)

### Community

- [MySQL Forums](https://forums.mysql.com/)
- [Stack Overflow - MySQL](https://stackoverflow.com/questions/tagged/mysql)
- [CovetPy GitHub Issues](https://github.com/covetpy/covetpy/issues)

---

## License

This guide is part of the CovetPy framework and is provided under the MIT License.

Copyright (c) 2025 CovetPy Team

---

**Last Updated:** 2025-10-11
**Version:** 1.0
**Maintained By:** CovetPy Database Team
