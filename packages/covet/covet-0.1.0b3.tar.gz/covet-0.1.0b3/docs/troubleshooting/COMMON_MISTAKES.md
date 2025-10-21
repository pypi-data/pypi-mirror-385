# Common Mistakes and Pitfalls in CovetPy

This guide documents the most common mistakes developers make when using CovetPy, based on actual mismatches between documentation and implementation.

## Table of Contents

1. [Application Class Naming](#1-application-class-naming)
2. [Database API Differences](#2-database-api-differences)
3. [JWT Authentication Enums](#3-jwt-authentication-enums)
4. [Cache Module Imports](#4-cache-module-imports)
5. [ORM API Limitations](#5-orm-api-limitations)
6. [Import Paths](#6-import-paths)
7. [Async/Await Requirements](#7-asyncawait-requirements)

---

## 1. Application Class Naming

### The Problem

Old documentation refers to a class called `Application` that doesn't exist in the codebase.

### WRONG (from old docs):
```python
from covet import Application

app = Application()
```

**Error you'll get:**
```
ImportError: cannot import name 'Application' from 'covet'
```

### CORRECT (actual implementation):
```python
from covet import CovetPy

app = CovetPy()
```

**Alternative (also works):**
```python
from covet.core import CovetApplication

app = CovetApplication()
```

### Why This Matters

- `CovetPy` is the main high-level API class (Flask-like interface)
- `CovetApplication` is the lower-level application class
- `Application` is just an alias to `CovetApplication` in the exports
- Most users should use `CovetPy` for the best experience

### Migration Guide

If you have existing code using `Application`:

```python
# Old code
from covet import Application
app = Application(debug=True)

# New code
from covet import CovetPy
app = CovetPy(debug=True)
```

---

## 2. Database API Differences

### The Problem

Documentation shows a simplified Database API that doesn't match the actual implementation.

### WRONG (from old docs):
```python
from covet.database import Database

db = Database(adapter='sqlite', database='app.db')
await db.connect()
```

**Error you'll get:**
```
ImportError: cannot import name 'Database' from 'covet.database'
```

### CORRECT (actual implementation):
```python
from covet.database import DatabaseManager, SQLiteAdapter

adapter = SQLiteAdapter(database_path='app.db')
db = DatabaseManager(adapter)
await db.connect()
```

### Full Example with All Database Operations

```python
from covet.database import DatabaseManager, SQLiteAdapter

# 1. Create adapter
adapter = SQLiteAdapter(database_path='/tmp/myapp.db')

# 2. Create database manager
db = DatabaseManager(adapter)

# 3. Connect
await db.connect()

# 4. Create table
await db.create_table('users', {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'username': 'TEXT UNIQUE NOT NULL',
    'email': 'TEXT NOT NULL'
})

# 5. Insert data
await db.insert('users', {
    'username': 'alice',
    'email': 'alice@example.com'
})

# 6. Query data
users = await db.fetch_all("SELECT * FROM users")

# 7. Update data
await db.update('users',
    {'email': 'alice.new@example.com'},
    {'username': 'alice'}
)

# 8. Delete data
await db.delete('users', {'username': 'alice'})

# 9. Disconnect
await db.disconnect()
```

### Why This API?

The two-step adapter pattern allows:
- Easy switching between database backends (SQLite, PostgreSQL, MySQL)
- Connection pooling configuration
- Adapter-specific optimizations
- Better testing with mock adapters

### Supported Database Adapters

Currently, **only SQLite is fully implemented**:

```python
# SQLite (WORKS)
from covet.database import SQLiteAdapter
adapter = SQLiteAdapter(database_path='/tmp/app.db')

# PostgreSQL (STUB - not implemented)
from covet.database.adapters.postgresql import PostgreSQLAdapter
# This exists but is not functional

# MySQL (STUB - not implemented)
from covet.database.adapters.mysql import MySQLAdapter
# This exists but is not functional
```

---

## 3. JWT Authentication Enums

### The Problem

JWT configuration requires enum types, not string values. This is a type safety feature but catches many users off guard.

### WRONG (from old docs):
```python
from covet.security.jwt_auth import JWTConfig

config = JWTConfig(
    secret_key="my-secret",
    algorithm='HS256'  # String NOT accepted
)

token = auth.create_token("user_123", 'access')  # String NOT accepted
```

**Error you'll get:**
```
TypeError: algorithm must be JWTAlgorithm enum, not str
```

### CORRECT (actual implementation):
```python
from covet.security.jwt_auth import (
    JWTConfig,
    JWTAlgorithm,  # Import the enum
    TokenType,     # Import the enum
    JWTAuthenticator
)

# Use enum for algorithm
config = JWTConfig(
    secret_key="my-secret-key-must-be-32-chars-or-more",
    algorithm=JWTAlgorithm.HS256  # Use enum, not string
)

auth = JWTAuthenticator(config)

# Use enum for token type
token = auth.create_token(
    "user_123",
    TokenType.ACCESS  # Use enum, not string
)
```

### Available Enums

#### JWTAlgorithm Enum:
```python
JWTAlgorithm.HS256   # HMAC with SHA-256
JWTAlgorithm.HS384   # HMAC with SHA-384
JWTAlgorithm.HS512   # HMAC with SHA-512
JWTAlgorithm.RS256   # RSA with SHA-256
JWTAlgorithm.RS384   # RSA with SHA-384
JWTAlgorithm.RS512   # RSA with SHA-512
```

#### TokenType Enum:
```python
TokenType.ACCESS     # Short-lived access token
TokenType.REFRESH    # Long-lived refresh token
```

### Complete JWT Example

```python
from covet.security.jwt_auth import (
    JWTAuthenticator,
    JWTConfig,
    JWTAlgorithm,
    TokenType
)

# 1. Configure JWT
config = JWTConfig(
    secret_key="your-super-secret-key-at-least-32-characters-long",
    algorithm=JWTAlgorithm.HS256,
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)

# 2. Create authenticator
auth = JWTAuthenticator(config)

# 3. Create tokens
access_token = auth.create_token(
    subject="user_123",
    token_type=TokenType.ACCESS,
    custom_claims={'role': 'admin', 'permissions': ['read', 'write']}
)

refresh_token = auth.create_token(
    subject="user_123",
    token_type=TokenType.REFRESH
)

# 4. Verify tokens
try:
    claims = auth.verify_token(access_token)
    print(f"Token valid for user: {claims['sub']}")
    print(f"Role: {claims.get('role')}")
except Exception as e:
    print(f"Token invalid: {e}")
```

### Why Enums?

Enums provide:
- **Type safety**: Catch typos at import time, not runtime
- **IDE autocomplete**: Better developer experience
- **Clear API**: Shows all available options
- **Future-proof**: Easy to add new algorithms

---

## 4. Cache Module Imports

### The Problem

Cache module classes are not directly importable from `covet.cache` in some documentation examples.

### WRONG (might not work):
```python
from covet.cache import MemoryCache  # May fail depending on version

cache = MemoryCache()
```

### CORRECT (always works):
```python
from covet.cache import CacheManager

# Use the manager (recommended)
cache = CacheManager(backend='memory', prefix='myapp')
await cache.connect()
await cache.set('key', 'value', ttl=300)
```

### Alternative (direct backend access):
```python
from covet.cache.backends import MemoryCache

# Direct backend usage
cache = MemoryCache()
await cache.set('key', 'value', ttl=300)
```

### Cache Manager vs Direct Backend

**Use CacheManager when:**
- You want a unified API across backends
- You need automatic fallback mechanisms
- You want batch operations
- You're building a production application

**Use Direct Backend when:**
- You're writing tests
- You need backend-specific features
- You have specific performance requirements

### Complete Cache Example

```python
from covet.cache import CacheManager, CacheConfig

# 1. Configure cache
config = CacheConfig(
    backend='redis',  # or 'memory', 'memcached'
    prefix='myapp',
    default_ttl=300
)

# 2. Create cache manager
cache = CacheManager(backend='memory', prefix='myapp')

# 3. Connect
await cache.connect()

# 4. Set value
await cache.set('user:123', {'name': 'Alice'}, ttl=600)

# 5. Get value
user = await cache.get('user:123')

# 6. Delete value
await cache.delete('user:123')

# 7. Pattern operations
await cache.delete_pattern('user:*')

# 8. Disconnect
await cache.disconnect()
```

---

## 5. ORM API Limitations

### The Problem

The ORM documentation shows advanced features that are not yet fully implemented.

### WORKS:
```python
from covet.database.orm import Model, CharField, IntegerField

class User(Model):
    name = CharField(max_length=100)
    age = IntegerField()

# Basic CRUD
user = await User.objects.create(name="Alice", age=30)
users = await User.objects.filter(age__gte=18).all()
await user.save()
await user.delete()
```

### DOESN'T WORK (not implemented):
```python
# select_related() exists but has runtime errors
users = await User.objects.filter(...).select_related('foreign_key')

# prefetch_related() not fully functional
users = await User.objects.all().prefetch_related('related_set')

# Complex annotations not supported
users = await User.objects.annotate(post_count=Count('posts'))
```

### ORM Reality Check

The CovetPy ORM is **basic** and designed for learning, not production use. It supports:

SUPPORTED:
- Basic model definition
- Field types (CharField, IntegerField, etc.)
- Simple queries (`filter`, `all`, `get`)
- Basic WHERE clauses
- Simple relationships
- CRUD operations

NOT SUPPORTED:
- Complex JOINs via ORM
- Aggregations via ORM (use raw SQL)
- Transactions
- Migrations (manual SQL only)
- Connection pooling
- Query optimization
- Bulk operations

### Recommendation for Production

For production applications, use:
- **Django ORM** - Full-featured, battle-tested
- **SQLAlchemy** - Flexible, powerful
- **Tortoise ORM** - Async-native

For CovetPy, use **raw SQL** for complex queries:

```python
from covet.database import DatabaseManager, SQLiteAdapter

adapter = SQLiteAdapter(database_path='app.db')
db = DatabaseManager(adapter)
await db.connect()

# Use raw SQL for complex queries
results = await db.fetch_all("""
    SELECT u.*, COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    GROUP BY u.id
    HAVING post_count > 5
""")
```

---

## 6. Import Paths

### The Problem

Documentation sometimes shows shortened import paths that don't match the actual package structure.

### Common Import Mistakes

#### WRONG:
```python
from covet.auth import JWTConfig  # Does not exist
from covet.db import Database     # Does not exist
from covet import HTTPException   # Does not exist
```

#### CORRECT:
```python
from covet.security.jwt_auth import JWTConfig, JWTAuthenticator, JWTAlgorithm
from covet.database import DatabaseManager, SQLiteAdapter
from covet.api.rest import BadRequestError, NotFoundError
```

### Import Reference Guide

```python
# Main application
from covet import CovetPy, CovetApplication

# HTTP components
from covet.core import Request, Response, Cookie

# Database
from covet.database import DatabaseManager, SQLiteAdapter

# JWT authentication
from covet.security.jwt_auth import (
    JWTAuthenticator,
    JWTConfig,
    JWTAlgorithm,
    TokenType
)

# REST API
from covet.api.rest import (
    RESTFramework,
    BaseModel,
    Field,
    NotFoundError,
    BadRequestError,
    ValidationError
)

# Query builder
from covet.database.query_builder.builder import QueryBuilder

# Cache
from covet.cache import CacheManager, CacheConfig

# Middleware
from covet.core import (
    CORSMiddleware,
    SessionMiddleware,
    RateLimitMiddleware,
    GZipMiddleware
)
```

### Finding the Right Import

If you're not sure where something is imported from:

```python
# Python REPL method
import covet
print(covet.__file__)  # See where it's installed

# Find a specific class
import sys
import covet
for name, obj in vars(covet).items():
    if 'JWT' in name:
        print(f"{name}: {type(obj)}")
```

---

## 7. Async/Await Requirements

### The Problem

Many CovetPy APIs are async and require `await`, but documentation sometimes omits this.

### WRONG:
```python
# Missing async/await
def main():
    db.connect()  # Error: coroutine not awaited
    users = db.fetch_all("SELECT * FROM users")  # Error
```

### CORRECT:
```python
import asyncio

async def main():
    await db.connect()  # Properly awaited
    users = await db.fetch_all("SELECT * FROM users")  # Properly awaited

# Run with asyncio
asyncio.run(main())
```

### Which APIs are Async?

**Async (require await):**
- All database operations (`connect`, `fetch_all`, `insert`, `update`, `delete`)
- All ORM operations (`Model.objects.create()`, `.filter()`, `.save()`)
- Cache operations (`cache.set()`, `cache.get()`)
- REST API handlers

**Not Async:**
- JWT token creation (`auth.create_token()`) - synchronous
- JWT token verification (`auth.verify_token()`) - synchronous
- Configuration and setup
- Pydantic model validation

### Running Async Code

**In Scripts:**
```python
import asyncio

async def main():
    # Your async code here
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

**In Jupyter Notebooks:**
```python
# Top-level await works in Jupyter
await db.connect()
users = await db.fetch_all("SELECT * FROM users")
```

**In FastAPI/CovetPy Route Handlers:**
```python
@app.route("/users")
async def get_users(request):
    # Already in async context
    users = await User.objects.all()
    return users
```

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check Working Examples**: See `docs/examples/` for verified code
2. **Read Source Code**: The implementation is the truth
3. **Check GitHub Issues**: Someone may have reported it
4. **Ask in Discussions**: Community support
5. **Report Documentation Bugs**: Help improve the docs

## Contributing to This Guide

Found a common mistake not listed here? Please:

1. Document the problem clearly
2. Show the wrong way and the right way
3. Explain why it happens
4. Provide a complete working example
5. Submit a pull request

---

## Quick Reference Cheat Sheet

```python
# ❌ WRONG → ✅ CORRECT

# Application
from covet import Application
from covet import CovetPy

# Database
from covet.database import Database
from covet.database import DatabaseManager, SQLiteAdapter

# JWT
config = JWTConfig(algorithm='HS256')
config = JWTConfig(algorithm=JWTAlgorithm.HS256)

# Token
auth.create_token(user_id, 'access')
auth.create_token(user_id, TokenType.ACCESS)

# Cache
from covet.cache import MemoryCache
from covet.cache import CacheManager

# Async
db.connect()
await db.connect()
```

---

**Last Updated**: 2025-10-12
**CovetPy Version**: 0.9.0-beta
**Status**: Active development - expect changes

For the latest updates, see the [changelog](../../CHANGELOG.md) and [release notes](../../releases/).
