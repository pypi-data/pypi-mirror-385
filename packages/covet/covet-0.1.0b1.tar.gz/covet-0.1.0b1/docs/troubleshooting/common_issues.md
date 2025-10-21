# CovetPy Troubleshooting Guide

**Version:** 1.0.0
**Last Updated:** 2025-10-11

## Table of Contents

- [Database Connection Issues](#database-connection-issues)
- [Transaction Problems](#transaction-problems)
- [Migration Failures](#migration-failures)
- [Performance Problems](#performance-problems)
- [Query Errors](#query-errors)
- [Authentication Issues](#authentication-issues)
- [Async/Await Errors](#asyncawait-errors)
- [Deployment Issues](#deployment-issues)
- [Debug Logging](#debug-logging)

---

## Database Connection Issues

### Problem: Connection Refused

**Error:**
```
covet.database.DatabaseError: Could not connect to database
Connection refused (localhost:5432)
```

**Causes:**
1. PostgreSQL not running
2. Wrong host/port
3. Firewall blocking connection
4. Database not accepting TCP connections

**Solutions:**

**Check if PostgreSQL is running:**
```bash
# Linux
sudo systemctl status postgresql

# macOS
brew services list | grep postgresql

# Docker
docker ps | grep postgres
```

**Test connection manually:**
```bash
psql -h localhost -U postgres -d covetpy
```

**Check PostgreSQL is listening on network:**
```bash
# postgresql.conf
listen_addresses = '*'  # or 'localhost'

# pg_hba.conf
host all all 0.0.0.0/0 md5
```

**Verify in CovetPy config:**
```python
# config/database.py
DATABASE = DatabaseConfig(
    host='localhost',  # Correct host
    port=5432,         # Correct port
    database='covetpy',
    user='postgres',
    password='your-password'
)
```

### Problem: Too Many Connections

**Error:**
```
psycopg2.OperationalError: FATAL:  sorry, too many clients already
```

**Causes:**
1. Connection pool too large
2. Connections not being released
3. PostgreSQL max_connections too low

**Solutions:**

**Reduce pool size:**
```python
DATABASE = DatabaseConfig(
    # ...
    pool_size=10,      # Reduce from 50
    max_overflow=5     # Reduce from 20
)
```

**Check active connections:**
```sql
SELECT count(*) FROM pg_stat_activity;
SELECT * FROM pg_stat_activity WHERE datname = 'covetpy';
```

**Increase PostgreSQL max_connections:**
```bash
# postgresql.conf
max_connections = 200  # Increase from 100

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**Debug connection leaks:**
```python
from covet.database import get_adapter

adapter = await get_adapter('default')
pool_status = adapter.pool.status()

print(f"Pool size: {pool_status['size']}")
print(f"In use: {pool_status['in_use']}")
print(f"Idle: {pool_status['idle']}")

# If in_use is always high, connections aren't being released
```

### Problem: Authentication Failed

**Error:**
```
psycopg2.OperationalError: FATAL:  password authentication failed for user "postgres"
```

**Solutions:**

**Check credentials:**
```python
DATABASE = DatabaseConfig(
    user='postgres',  # Correct username
    password='correct-password'  # Correct password
)
```

**Check pg_hba.conf:**
```bash
# /var/lib/postgresql/data/pg_hba.conf

# Allow password authentication
host all all 127.0.0.1/32 md5
host all all ::1/128 md5
```

**Reset PostgreSQL password:**
```sql
ALTER USER postgres WITH PASSWORD 'new-password';
```

---

## Transaction Problems

### Problem: Deadlock Detected

**Error:**
```
covet.database.TransactionError: deadlock detected
DETAIL:  Process 1234 waits for ShareLock on transaction 5678
```

**Causes:**
Two transactions waiting for each other to release locks.

**Solution:**

**Ensure consistent lock order:**
```python
# BAD: Inconsistent order can cause deadlocks
async def transfer_funds_bad(from_id, to_id, amount):
    async with transaction():
        from_account = await Account.objects.select_for_update().get(id=from_id)
        to_account = await Account.objects.select_for_update().get(id=to_id)
        # If another transaction locks to_account first, deadlock!

# GOOD: Always lock in same order (by ID)
async def transfer_funds_good(from_id, to_id, amount):
    async with transaction():
        # Lock accounts in ID order
        ids = sorted([from_id, to_id])
        accounts = await Account.objects.select_for_update().filter(id__in=ids)
        from_account = next(a for a in accounts if a.id == from_id)
        to_account = next(a for a in accounts if a.id == to_id)
```

**Retry on deadlock:**
```python
import asyncio

async def retry_on_deadlock(func, max_retries=3):
    """Retry function on deadlock."""
    for attempt in range(max_retries):
        try:
            return await func()
        except TransactionError as e:
            if 'deadlock' in str(e) and attempt < max_retries - 1:
                await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                continue
            raise
```

### Problem: Transaction Timeout

**Error:**
```
covet.database.TransactionError: transaction timeout after 30 seconds
```

**Solutions:**

**Increase timeout:**
```python
from covet.database.transaction import transaction

async with transaction(timeout=60):  # 60 seconds
    await slow_operation()
```

**Optimize query:**
```python
# BAD: Slow query in transaction
async with transaction():
    users = await User.objects.all()  # Fetches all users!
    for user in users:
        await process_user(user)

# GOOD: Process in batches
async with transaction():
    users = await User.objects.filter(processed=False).limit(100)
    for user in users:
        await process_user(user)
```

---

## Migration Failures

### Problem: Migration Conflict

**Error:**
```
covet.migration.MigrationError: Conflicting migrations detected
Both migrations 0003_auto.py and 0003_add_field.py exist
```

**Solution:**

**Check migration files:**
```bash
ls migrations/
# 0001_initial.py
# 0002_add_user.py
# 0003_auto.py        <-- Conflict
# 0003_add_field.py   <-- Conflict
```

**Rename one:**
```bash
mv migrations/0003_auto.py migrations/0004_auto.py
```

**Re-run migrations:**
```bash
covet migration apply
```

### Problem: Migration Fails Halfway

**Error:**
```
covet.migration.MigrationError: Error applying migration 0005_add_index.py
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint
```

**Solution:**

**Check migration status:**
```bash
covet migration list

# 0001_initial.py [APPLIED]
# 0002_add_user.py [APPLIED]
# 0003_add_field.py [APPLIED]
# 0004_add_index.py [APPLIED]
# 0005_bad_migration.py [FAILED]  <-- This one failed
```

**Mark migration as not applied:**
```bash
covet migration mark 0005_bad_migration.py --unapplied
```

**Fix migration file, then reapply:**
```bash
covet migration apply
```

### Problem: Reverse Migration Failed

**Error:**
```
covet.migration.MigrationError: Cannot reverse migration 0003_add_field.py
down() method not implemented
```

**Solution:**

**Add down() method:**
```python
# migrations/0003_add_field.py
class Migration(Migration):
    async def up(self):
        await self.add_column('users', 'phone', 'VARCHAR(20)')

    async def down(self):
        """Reverse migration."""
        await self.drop_column('users', 'phone')
```

---

## Performance Problems

### Problem: Slow Queries

**Symptom:** Requests taking > 500ms

**Debug:**

**Enable query logging:**
```python
# config/database.py
DATABASE = DatabaseConfig(
    # ...
    echo=True,  # Log all queries
)
```

**Check logs:**
```
[2025-10-11 10:15:23] SELECT * FROM users WHERE email = 'test@example.com' (125ms)
```

**Solutions:**

**Add index:**
```python
class User(Model):
    email = EmailField(unique=True)  # Auto-indexed

    class Meta:
        indexes = [
            Index(fields=['email'])  # Explicit index
        ]
```

**Use select_related:**
```python
# BAD: N+1 queries
posts = await Post.objects.all()
for post in posts:
    print(post.author.username)  # Separate query each time!

# GOOD: Join
posts = await Post.objects.select_related('author').all()
```

**Analyze query plan:**
```python
from covet.database import get_adapter

adapter = await get_adapter('default')
result = await adapter.fetch_all(
    'EXPLAIN ANALYZE SELECT * FROM users WHERE email = $1',
    ['test@example.com']
)
print(result)

# Look for "Seq Scan" (bad) vs "Index Scan" (good)
```

### Problem: Memory Usage High

**Symptom:** Application using > 1GB memory

**Debug:**

**Profile memory:**
```python
import tracemalloc

tracemalloc.start()

# Your code here
users = await User.objects.all()

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

**Solutions:**

**Use iterator for large queries:**
```python
# BAD: Loads all 1M users into memory
users = await User.objects.all()

# GOOD: Process in batches
async for user in User.objects.iterator(chunk_size=1000):
    await process_user(user)
```

**Limit query results:**
```python
# Only fetch what you need
users = await User.objects.limit(100)
```

---

## Query Errors

### Problem: Object Does Not Exist

**Error:**
```
covet.database.orm.ObjectDoesNotExist: User matching query does not exist.
```

**Solutions:**

**Use try/except:**
```python
try:
    user = await User.objects.get(id=999)
except User.DoesNotExist:
    # Handle not found
    return {'error': 'User not found'}, 404
```

**Use get_or_none:**
```python
user = await User.objects.get_or_none(id=999)
if user is None:
    # Handle not found
    pass
```

**Check existence first:**
```python
exists = await User.objects.filter(id=999).exists()
if not exists:
    # Handle not found
    pass
```

### Problem: Multiple Objects Returned

**Error:**
```
covet.database.orm.MultipleObjectsReturned: get() returned more than one User
```

**Solutions:**

**Use filter instead:**
```python
# BAD: get() expects single result
user = await User.objects.get(is_active=True)  # Multiple active users!

# GOOD: Use filter for multiple results
users = await User.objects.filter(is_active=True)
```

**Add unique constraint:**
```python
class User(Model):
    email = EmailField(unique=True)  # Ensure only one per email
```

---

## Authentication Issues

### Problem: Invalid JWT Token

**Error:**
```
covet.security.InvalidTokenError: Invalid JWT token
```

**Solutions:**

**Check token format:**
```python
# Valid format: "Bearer <token>"
auth_header = request.headers.get('Authorization')
if not auth_header or not auth_header.startswith('Bearer '):
    return {'error': 'Invalid authorization header'}, 401

token = auth_header[7:]  # Remove "Bearer "
```

**Verify token:**
```python
from covet.security.jwt import decode_jwt

try:
    payload = decode_jwt(token)
    user_id = payload['user_id']
except ValueError:
    return {'error': 'Invalid token'}, 401
```

**Check expiration:**
```python
import time

payload = decode_jwt(token)
if payload['exp'] < time.time():
    return {'error': 'Token expired'}, 401
```

---

## Async/Await Errors

### Problem: Forgot await

**Error:**
```
RuntimeWarning: coroutine 'get_user' was never awaited
```

**Solution:**

**Add await:**
```python
# BAD
user = User.objects.get(id=1)  # Returns coroutine!

# GOOD
user = await User.objects.get(id=1)
```

### Problem: Async in Sync Context

**Error:**
```
RuntimeError: This event loop is already running
```

**Solution:**

**Don't call async from sync:**
```python
# BAD
def sync_function():
    user = asyncio.run(User.objects.get(id=1))  # Error!

# GOOD: Make function async
async def async_function():
    user = await User.objects.get(id=1)
```

---

## Deployment Issues

### Problem: Environment Variables Not Set

**Error:**
```
KeyError: 'DATABASE_URL'
```

**Solution:**

**Check environment:**
```bash
printenv | grep DATABASE_URL
```

**Set in Docker Compose:**
```yaml
services:
  app:
    environment:
      - DATABASE_URL=postgresql://...
```

**Use .env file:**
```bash
# .env
DATABASE_URL=postgresql://localhost/covetpy
SECRET_KEY=your-secret-key
```

**Load in Python:**
```python
from dotenv import load_dotenv
load_dotenv()

import os
database_url = os.getenv('DATABASE_URL')
```

---

## Debug Logging

### Enable Debug Logging

```python
# config/logging.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Enable CovetPy debug logging
logging.getLogger('covet.database').setLevel(logging.DEBUG)
logging.getLogger('covet.orm').setLevel(logging.DEBUG)
```

### Log All Queries

```python
DATABASE = DatabaseConfig(
    # ...
    echo=True,  # Log all SQL queries
    echo_pool=True  # Log connection pool activity
)
```

### Custom Debug Middleware

```python
from covet.middleware import BaseMiddleware
import time

class DebugMiddleware(BaseMiddleware):
    """Log request details."""

    async def process_request(self, request):
        request.state.start_time = time.time()
        print(f"→ {request.method} {request.url}")

    async def process_response(self, request, response):
        duration = time.time() - request.state.start_time
        print(f"← {response.status_code} ({duration*1000:.2f}ms)")
        return response
```

---

## Getting Help

**Still stuck? Here's where to get help:**

1. **Check Documentation:** https://docs.covetpy.dev
2. **Search GitHub Issues:** https://github.com/covetpy/covetpy/issues
3. **Ask on Discord:** https://discord.gg/covetpy
4. **Stack Overflow:** Tag `covetpy`
5. **Email Support:** support@covetpy.dev

**When asking for help, include:**
- CovetPy version (`covet --version`)
- Python version
- Database type and version
- Full error traceback
- Minimal code example to reproduce
- What you've already tried

---

**Document Information:**
- Version: 1.0.0
- Last Updated: 2025-10-11
- Maintained by: CovetPy Team
