# Cache API Reference

**Last Updated:** 2025-10-10
**Version:** 1.0.0

The CovetPy caching system provides a unified, production-ready caching layer with multiple backend support including in-memory, Redis, Memcached, and database caching.

## Table of Contents

- [Overview](#overview)
- [Cache Manager](#cache-manager)
- [Cache Backends](#cache-backends)
- [Decorators](#decorators)
- [Middleware](#middleware)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Performance](#performance)

## Overview

CovetPy's caching system provides:

- **Multiple Backends**: In-memory, Redis, Memcached, database
- **Unified API**: Consistent interface across all backends
- **Multi-Tier Caching**: L1 (memory) + L2 (distributed) caching
- **Automatic Fallback**: Graceful degradation when backends fail
- **Decorators**: Function and page caching with minimal code
- **Batch Operations**: Efficient bulk get/set/delete
- **Pattern Operations**: Delete multiple keys by pattern
- **Statistics**: Hit/miss ratios, memory usage, performance metrics

### Quick Start

```python
from covet.cache import CacheManager, cache_result

# Create cache manager
cache = CacheManager(backend='memory', prefix='myapp')
await cache.connect()

# Basic operations
await cache.set('user:1', {'name': 'Alice'}, ttl=300)
user = await cache.get('user:1')

# Decorator caching
@cache_result(ttl=300, key_prefix='user')
async def get_user(user_id: int):
    return await db.query(User).get(user_id)
```

## Cache Manager

The `CacheManager` is the main interface for caching operations.

### Creating a Cache Manager

```python
from covet.cache import CacheManager, CacheConfig, CacheBackend

# Simple initialization
cache = CacheManager(backend='memory', prefix='myapp')

# With configuration
config = CacheConfig(
    backend=CacheBackend.REDIS,
    key_prefix='myapp',
    default_ttl=300,
    redis_config=RedisConfig(
        host='localhost',
        port=6379,
        db=0
    )
)
cache = CacheManager(config)

# Connect to backend
await cache.connect()
```

### Basic Operations

#### get(key, default=None)

Retrieve a value from cache.

```python
# Get single value
user = await cache.get('user:1')

# With default
user = await cache.get('user:1', default={'name': 'Unknown'})

# None if not found
result = await cache.get('nonexistent')  # Returns None
```

**Parameters:**
- `key` (str): Cache key
- `default` (Any): Value to return if key not found

**Returns:** Cached value or default

#### set(key, value, ttl=None)

Store a value in cache.

```python
# Set value
await cache.set('user:1', {'name': 'Alice', 'email': 'alice@example.com'})

# With TTL (time-to-live in seconds)
await cache.set('session:abc', session_data, ttl=3600)

# No expiration
await cache.set('config', config_data, ttl=None)

# Complex data types
await cache.set('data', {
    'list': [1, 2, 3],
    'nested': {'key': 'value'},
    'number': 42
}, ttl=300)
```

**Parameters:**
- `key` (str): Cache key
- `value` (Any): Value to cache (must be serializable)
- `ttl` (int, optional): Time-to-live in seconds

**Returns:** `True` if successful

#### delete(key)

Remove a key from cache.

```python
# Delete single key
await cache.delete('user:1')

# Check if deleted
deleted = await cache.delete('user:1')  # Returns True/False
```

**Parameters:**
- `key` (str): Cache key to delete

**Returns:** `True` if key was deleted

#### exists(key)

Check if a key exists.

```python
# Check existence
if await cache.exists('user:1'):
    print('User cached')

# Use in conditionals
has_cache = await cache.exists('expensive:computation')
if not has_cache:
    result = expensive_function()
    await cache.set('expensive:computation', result)
```

**Parameters:**
- `key` (str): Cache key to check

**Returns:** `True` if key exists

#### clear()

Clear all cached data.

```python
# Clear everything
await cache.clear()

# Use with caution in production!
if settings.DEBUG:
    await cache.clear()
```

**Returns:** `True` if successful

### Batch Operations

#### get_many(keys)

Get multiple values efficiently.

```python
# Get multiple keys
keys = ['user:1', 'user:2', 'user:3']
users = await cache.get_many(keys)

print(users)  # {'user:1': {...}, 'user:2': {...}, 'user:3': {...}}

# Missing keys are omitted
keys = ['exists', 'missing']
result = await cache.get_many(keys)  # {'exists': value}
```

**Parameters:**
- `keys` (List[str]): List of cache keys

**Returns:** Dictionary of key-value pairs (missing keys omitted)

#### set_many(mapping, ttl=None)

Set multiple values efficiently.

```python
# Set multiple values
await cache.set_many({
    'user:1': {'name': 'Alice'},
    'user:2': {'name': 'Bob'},
    'user:3': {'name': 'Charlie'}
}, ttl=300)

# Batch cache invalidation and reset
await cache.set_many({
    'config:feature_flags': new_flags,
    'config:settings': new_settings
})
```

**Parameters:**
- `mapping` (Dict[str, Any]): Dictionary of key-value pairs
- `ttl` (int, optional): Time-to-live in seconds for all keys

**Returns:** `True` if successful

#### delete_many(keys)

Delete multiple keys efficiently.

```python
# Delete multiple keys
deleted = await cache.delete_many(['user:1', 'user:2', 'user:3'])
print(f'Deleted {deleted} keys')

# Clear user-related caches
user_keys = [f'user:{user_id}' for user_id in user_ids]
await cache.delete_many(user_keys)
```

**Parameters:**
- `keys` (List[str]): List of cache keys to delete

**Returns:** Number of keys deleted

### Pattern Operations

#### keys(pattern=None)

List keys matching a pattern.

```python
# All keys
all_keys = await cache.keys()

# Pattern matching (depends on backend)
user_keys = await cache.keys('user:*')
session_keys = await cache.keys('session:*')

# List all cached data
for key in await cache.keys():
    value = await cache.get(key)
    print(f'{key}: {value}')
```

**Parameters:**
- `pattern` (str, optional): Pattern to match (e.g., `'user:*'`)

**Returns:** List of matching keys

**Note:** Pattern support varies by backend:
- Redis: Full glob pattern support (`*`, `?`, `[abc]`)
- Memory: Full Python regex support
- Memcached: Not supported
- Database: SQL LIKE patterns

#### delete_pattern(pattern)

Delete all keys matching a pattern.

```python
# Delete all user caches
await cache.delete_pattern('user:*')

# Clear session caches
await cache.delete_pattern('session:*')

# Namespace clearing
await cache.delete_pattern('temp:*')

# Count deleted
deleted = await cache.delete_pattern('old:*')
print(f'Cleared {deleted} old cache entries')
```

**Parameters:**
- `pattern` (str): Pattern to match

**Returns:** Number of keys deleted

### Atomic Operations

#### increment(key, delta=1)

Atomically increment a numeric value.

```python
# Page view counter
await cache.set('page:views', 0)
await cache.increment('page:views')  # 1
await cache.increment('page:views')  # 2
await cache.increment('page:views', delta=5)  # 7

# Concurrent-safe counters
await cache.increment('api:requests:count')

# Rate limiting
count = await cache.increment(f'rate:{user_id}:{minute}')
if count > rate_limit:
    raise TooManyRequestsError()
```

**Parameters:**
- `key` (str): Cache key
- `delta` (int): Amount to increment (default: 1)

**Returns:** New value after increment

#### decrement(key, delta=1)

Atomically decrement a numeric value.

```python
# Remaining quota
await cache.set('quota:user:1', 100)
await cache.decrement('quota:user:1')  # 99

# Inventory management
remaining = await cache.decrement(f'inventory:{product_id}')
if remaining < 0:
    raise OutOfStockError()
```

**Parameters:**
- `key` (str): Cache key
- `delta` (int): Amount to decrement (default: 1)

**Returns:** New value after decrement

### TTL Operations

#### touch(key, ttl)

Update the TTL of an existing key without changing its value.

```python
# Extend session timeout
await cache.touch('session:abc', ttl=3600)

# Keep-alive mechanism
await cache.touch('connection:123', ttl=300)

# Conditional extension
if user_active:
    await cache.touch(f'session:{session_id}', ttl=1800)
```

**Parameters:**
- `key` (str): Cache key
- `ttl` (int): New TTL in seconds

**Returns:** `True` if successful

#### expire(key, ttl)

Alias for `touch()`.

```python
# Same as touch()
await cache.expire('key', ttl=300)
```

### Statistics

#### get_stats()

Get cache performance statistics.

```python
# Get statistics
stats = await cache.get_stats()

print(f"Backend: {stats['backend']}")
print(f"Hits: {stats['primary']['hits']}")
print(f"Misses: {stats['primary']['misses']}")
print(f"Hit ratio: {stats['primary']['hit_ratio']:.2%}")
print(f"Size: {stats['primary']['size']}")
```

**Returns:** Dictionary with cache statistics

**Statistics Include:**
- `hits`: Number of cache hits
- `misses`: Number of cache misses
- `hit_ratio`: Cache hit ratio (0.0-1.0)
- `size`: Number of cached items
- `memory_bytes`: Memory usage (if available)
- `evictions`: Number of evicted items

### Context Manager

```python
# Automatic connect/disconnect
async with CacheManager(backend='redis') as cache:
    await cache.set('key', 'value')
    value = await cache.get('key')
# Automatically disconnects
```

## Cache Backends

CovetPy supports multiple cache backends with automatic fallback.

### Memory Cache

Fast in-process cache with LRU eviction.

```python
from covet.cache import MemoryCache

# Create memory cache
cache = MemoryCache(
    max_size=10000,        # Maximum number of items
    max_memory_mb=100,     # Maximum memory in MB
    default_ttl=300        # Default TTL in seconds
)

# Use directly
await cache.set('key', 'value')
value = await cache.get('key')

# Via CacheManager
config = CacheConfig(
    backend=CacheBackend.MEMORY,
    memory_max_size=10000,
    memory_max_memory_mb=100
)
cache = CacheManager(config)
```

**Characteristics:**
- **Speed**: Fastest (in-process memory access)
- **Persistence**: No (data lost on restart)
- **Distribution**: No (single-process only)
- **Use Cases**: Development, testing, single-server deployments

**Eviction Policy:**
- LRU (Least Recently Used)
- Size-based (max_size items)
- Memory-based (max_memory_mb)

### Redis Cache

Distributed cache using Redis.

```python
from covet.cache import RedisCache, RedisConfig, SerializerType

# Create Redis config
config = RedisConfig(
    host='localhost',
    port=6379,
    db=0,
    password=None,
    ssl=False,
    key_prefix='myapp:',
    socket_timeout=5.0,
    socket_connect_timeout=5.0,
    max_connections=50,
    serializer=SerializerType.JSON  # JSON, PICKLE, MSGPACK
)

# Create Redis cache
cache = RedisCache(config)
await cache.connect()

# Via CacheManager
from covet.cache import CacheManager, CacheBackend

manager = CacheManager(
    CacheConfig(
        backend=CacheBackend.REDIS,
        key_prefix='myapp',
        redis_config=config
    )
)
```

**Characteristics:**
- **Speed**: Very fast (network latency)
- **Persistence**: Optional (RDB/AOF)
- **Distribution**: Yes (shared across servers)
- **Use Cases**: Production, distributed systems, session storage

**Features:**
- Pub/sub for cache invalidation
- Atomic operations (increment/decrement)
- Pattern-based operations
- Persistence options

**Serialization Options:**
- `JSON`: Human-readable, slower, limited types
- `PICKLE`: Python-specific, faster, all types
- `MSGPACK`: Compact, fast, most types

### Memcached Cache

Distributed cache using Memcached.

```python
from covet.cache import MemcachedCache, MemcachedConfig

# Create Memcached config
config = MemcachedConfig(
    servers=[
        ('localhost', 11211),
        ('cache2.example.com', 11211),
    ],
    key_prefix='myapp:',
    connect_timeout=5.0,
    timeout=3.0,
    max_pool_size=10
)

# Create Memcached cache
cache = MemcachedCache(config)
await cache.connect()

# Via CacheManager
manager = CacheManager(
    CacheConfig(
        backend=CacheBackend.MEMCACHED,
        memcached_config=config
    )
)
```

**Characteristics:**
- **Speed**: Very fast (network latency)
- **Persistence**: No (pure in-memory)
- **Distribution**: Yes (sharded across servers)
- **Use Cases**: Production, high-throughput systems

**Features:**
- Consistent hashing for distribution
- LRU eviction
- Binary protocol support

**Limitations:**
- No persistence
- No pattern operations
- Limited atomic operations

### Database Cache

Persistent cache using database tables.

```python
from covet.cache import DatabaseCache, DatabaseCacheConfig

# Create database cache config
config = DatabaseCacheConfig(
    table_name='cache_entries',
    key_prefix='myapp:',
    # db_connection provided by CacheManager
)

# Via CacheManager (requires database setup)
manager = CacheManager(
    CacheConfig(
        backend=CacheBackend.DATABASE,
        database_config=config
    )
)
```

**Characteristics:**
- **Speed**: Slower (database queries)
- **Persistence**: Yes (survives restarts)
- **Distribution**: Yes (shared database)
- **Use Cases**: Persistent caching, audit requirements

**Use Cases:**
- Long-term cache (days/weeks)
- Persistent sessions
- Cache audit trail
- Fallback cache

### Multi-Tier Caching

Combine multiple backends for L1/L2 caching.

```python
from covet.cache import CacheManager, CacheConfig, CacheBackend

# L1 (memory) + L2 (Redis)
config = CacheConfig(
    backend=CacheBackend.REDIS,         # Primary cache
    fallback_backends=[
        CacheBackend.MEMORY                # Fallback cache
    ],
    redis_config=RedisConfig(host='localhost'),
    memory_max_size=1000
)

cache = CacheManager(config)
await cache.connect()

# Reads try Redis first, then memory
value = await cache.get('key')

# Writes go to both caches
await cache.set('key', value)

# Automatic promotion from L2 to L1
# If key found in memory (L2), it's promoted to Redis (L1)
```

**Benefits:**
- Hot data in fast L1 cache
- Cold data in distributed L2 cache
- Automatic failover
- Cache promotion

## Decorators

Decorators provide function and page caching with minimal code.

### @cache_result

Cache function results based on arguments.

```python
from covet.cache import cache_result

# Basic caching
@cache_result(ttl=300, key_prefix='user')
async def get_user(user_id: int):
    user = await db.query(User).get(user_id)
    return user

# Custom key generation
@cache_result(
    ttl=600,
    key_prefix='posts',
    key_func=lambda user_id, page: f'{user_id}:page:{page}'
)
async def get_user_posts(user_id: int, page: int = 1):
    posts = await db.query(Post).filter(
        user_id=user_id
    ).offset((page - 1) * 20).limit(20).all()
    return posts

# Conditional caching
@cache_result(
    ttl=60,
    unless=lambda: current_user.is_staff
)
async def get_dashboard_data():
    # Staff users always get fresh data
    return await compute_dashboard_data()

# Custom cache instance
app_cache = CacheManager(backend='redis')

@cache_result(ttl=300, cache=app_cache)
async def expensive_computation(n: int):
    return sum(range(n))
```

**Parameters:**
- `ttl` (int): Time-to-live in seconds (default: 300)
- `key_prefix` (str): Cache key prefix (default: 'func')
- `key_func` (callable): Custom key generation function
- `cache` (CacheManager): Cache instance (default: global cache)
- `unless` (callable): Skip caching if returns True

**How It Works:**
1. Generate cache key from function name and arguments
2. Check cache for existing value
3. Return cached value if found
4. Call function and cache result if not found
5. Return result

### @cache_page

Cache HTTP page/view responses.

```python
from covet.cache import cache_page

# Cache homepage
@cache_page(ttl=60)
async def homepage(request):
    return render_template('index.html', data=get_latest_posts())

# Vary by headers
@cache_page(
    ttl=300,
    vary=['Accept-Language', 'Accept-Encoding']
)
async def localized_page(request):
    language = request.headers.get('Accept-Language', 'en')
    return render_template(f'page_{language}.html')

# Cache API endpoints
@cache_page(ttl=60, key_prefix='api')
async def api_endpoint(request):
    return {'data': expensive_query()}
```

**Parameters:**
- `ttl` (int): Time-to-live in seconds (default: 60)
- `key_prefix` (str): Cache key prefix (default: 'page')
- `vary` (List[str]): Headers to vary cache on
- `cache` (CacheManager): Cache instance

**Vary Header Examples:**
- `Accept-Language`: Cache per language
- `Accept-Encoding`: Cache per encoding
- `User-Agent`: Cache per device type
- `Authorization`: Cache per user (be careful!)

### @cache_unless

Conditional caching based on condition.

```python
from covet.cache import cache_unless

# Don't cache for authenticated users
@cache_unless(lambda: request.user.is_authenticated)
async def public_page(request):
    return render_template('public.html')

# Don't cache during maintenance
@cache_unless(lambda: settings.MAINTENANCE_MODE)
async def get_data():
    return fetch_data()
```

**Parameters:**
- `condition` (callable): Skip caching if returns True

### @cache_invalidate

Invalidate cache keys after function execution.

```python
from covet.cache import cache_invalidate

# Fixed keys
@cache_invalidate(keys=['user:1', 'user:1:profile'])
async def update_user(user_id: int, data: dict):
    await User.query().filter(id=user_id).update(data)

# Dynamic keys
@cache_invalidate(
    keys=lambda user_id: [
        f'user:{user_id}',
        f'user:{user_id}:posts',
        f'user:{user_id}:profile'
    ]
)
async def update_user_profile(user_id: int, profile_data: dict):
    await Profile.query().filter(user_id=user_id).update(profile_data)

# Chaining invalidations
@cache_invalidate(keys=lambda article_id: [f'article:{article_id}'])
async def publish_article(article_id: int):
    await Article.query().filter(id=article_id).update(published=True)
    await notify_subscribers(article_id)
```

**Parameters:**
- `keys` (str | List[str] | callable): Keys to invalidate
- `cache` (CacheManager): Cache instance

### @cache_invalidate_pattern

Invalidate cache keys matching a pattern.

```python
from covet.cache import cache_invalidate_pattern

# Clear all user caches
@cache_invalidate_pattern(pattern='user:*')
async def reset_all_users():
    await User.query().update(reset_required=True)

# Dynamic pattern
@cache_invalidate_pattern(
    pattern=lambda user_id: f'user:{user_id}:*'
)
async def clear_user_cache(user_id: int):
    # Clears user:123:*, user:123:posts, user:123:profile, etc.
    pass

# Clear temporary caches
@cache_invalidate_pattern(pattern='temp:*')
async def cleanup_temp_data():
    pass
```

**Parameters:**
- `pattern` (str | callable): Pattern to match
- `cache` (CacheManager): Cache instance

### @memoize

Simple memoization decorator (similar to `functools.lru_cache` but with TTL).

```python
from covet.cache import memoize

# Memoize expensive computation
@memoize(maxsize=100, ttl=300)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Memoize database queries
@memoize(maxsize=1000, ttl=60)
async def get_user_by_email(email: str):
    return await User.query().filter(email=email).first()
```

**Parameters:**
- `maxsize` (int): Maximum cache size (default: 128)
- `ttl` (int): Time-to-live in seconds

## Middleware

HTTP caching middleware for automatic response caching.

### CacheMiddleware

```python
from covet.cache import CacheMiddleware, CacheMiddlewareConfig
from covet import CovetPy

# Create app
app = CovetPy()

# Configure cache middleware
config = CacheMiddlewareConfig(
    default_ttl=60,                    # Default cache TTL
    cache_get_only=True,               # Only cache GET requests
    cache_private=False,               # Cache public responses only
    cache_control_enabled=True,        # Respect Cache-Control headers
    vary_headers=['Accept-Language'],  # Vary on headers
    etag_enabled=True,                 # Generate ETags
    key_prefix='page',                 # Cache key prefix
)

# Add middleware
app.add_middleware(CacheMiddleware, config=config)

# Routes automatically cached
@app.get('/')
async def homepage(request):
    return {'message': 'Cached for 60 seconds'}

# Skip caching for specific routes
@app.get('/api/realtime')
async def realtime_data(request):
    # Set Cache-Control to skip caching
    return Response(
        data,
        headers={'Cache-Control': 'no-cache'}
    )
```

**Configuration Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_ttl` | `int` | `60` | Default cache TTL in seconds |
| `cache_get_only` | `bool` | `True` | Only cache GET requests |
| `cache_private` | `bool` | `False` | Cache authenticated responses |
| `cache_control_enabled` | `bool` | `True` | Respect Cache-Control headers |
| `vary_headers` | `List[str]` | `[]` | Headers to vary cache on |
| `etag_enabled` | `bool` | `True` | Generate and validate ETags |
| `key_prefix` | `str` | `'page'` | Cache key prefix |

**Cache-Control Support:**

```python
# Disable caching for response
return Response(data, headers={'Cache-Control': 'no-cache'})

# Custom TTL
return Response(data, headers={'Cache-Control': 'max-age=300'})

# Private cache only
return Response(data, headers={'Cache-Control': 'private'})
```

## Configuration

### CacheConfig

Main configuration class for CacheManager.

```python
from covet.cache import CacheConfig, CacheBackend
from covet.cache import RedisConfig, MemcachedConfig, DatabaseCacheConfig

config = CacheConfig(
    # Primary backend
    backend=CacheBackend.REDIS,

    # Fallback backends (in order)
    fallback_backends=[CacheBackend.MEMORY],

    # Backend-specific configs
    redis_config=RedisConfig(
        host='localhost',
        port=6379,
        db=0,
        password='secret',
        ssl=True
    ),
    memcached_config=MemcachedConfig(
        servers=[('localhost', 11211)]
    ),
    database_config=DatabaseCacheConfig(
        table_name='cache_entries'
    ),

    # Memory cache settings
    memory_max_size=10000,
    memory_max_memory_mb=100,

    # General settings
    default_ttl=300,
    key_prefix='myapp:'
)
```

### RedisConfig

Redis-specific configuration.

```python
from covet.cache import RedisConfig, SerializerType

config = RedisConfig(
    host='localhost',                      # Redis host
    port=6379,                             # Redis port
    db=0,                                  # Database number
    password=None,                         # Password
    ssl=False,                             # Use SSL/TLS
    key_prefix='',                         # Key prefix
    socket_timeout=5.0,                    # Socket timeout
    socket_connect_timeout=5.0,            # Connection timeout
    max_connections=50,                    # Connection pool size
    retry_on_timeout=True,                 # Retry on timeout
    health_check_interval=30,              # Health check interval
    serializer=SerializerType.JSON,        # Serializer (JSON/PICKLE/MSGPACK)
    decode_responses=True                  # Decode responses to str
)
```

### MemcachedConfig

Memcached-specific configuration.

```python
from covet.cache import MemcachedConfig

config = MemcachedConfig(
    servers=[
        ('localhost', 11211),
        ('cache2.example.com', 11211)
    ],
    key_prefix='',
    connect_timeout=5.0,
    timeout=3.0,
    no_delay=True,
    max_pool_size=10
)
```

### DatabaseCacheConfig

Database cache-specific configuration.

```python
from covet.cache import DatabaseCacheConfig

config = DatabaseCacheConfig(
    table_name='cache_entries',
    key_prefix='',
    # db_connection must be provided
)
```

## Best Practices

### 1. Choose the Right Backend

```python
# Development: Use memory
if settings.DEBUG:
    cache = CacheManager(backend='memory')

# Production: Use Redis
else:
    cache = CacheManager(
        backend='redis',
        redis_config=RedisConfig(host='redis.example.com')
    )
```

### 2. Use Multi-Tier Caching

```python
# Hot data in memory, cold data in Redis
config = CacheConfig(
    backend=CacheBackend.REDIS,
    fallback_backends=[CacheBackend.MEMORY],
    redis_config=redis_config,
    memory_max_size=1000
)
```

### 3. Set Appropriate TTLs

```python
# Frequently changing data: Short TTL
@cache_result(ttl=60)
async def get_stock_price(symbol: str):
    return await fetch_stock_price(symbol)

# Rarely changing data: Long TTL
@cache_result(ttl=3600)
async def get_country_list():
    return await db.query(Country).all()

# Static data: Very long TTL
@cache_result(ttl=86400)  # 24 hours
async def get_app_config():
    return load_config()
```

### 4. Use Key Prefixes

```python
# Organize cache keys with prefixes
cache = CacheManager(backend='redis', prefix='myapp')

await cache.set('user:1', data)        # Key: myapp:user:1
await cache.set('session:abc', data)   # Key: myapp:session:abc

# Easy to clear all app caches
await cache.delete_pattern('myapp:*')
```

### 5. Cache Invalidation Strategies

```python
# 1. Time-based (TTL)
await cache.set('data', value, ttl=300)

# 2. Event-based (manual invalidation)
@cache_invalidate(keys=lambda user_id: [f'user:{user_id}'])
async def update_user(user_id, data):
    await db.update_user(user_id, data)

# 3. Pattern-based (bulk invalidation)
@cache_invalidate_pattern(pattern='user:*')
async def reset_all_users():
    await db.reset_users()

# 4. Version-based (cache key versioning)
VERSION = '1'
cache_key = f'data:{VERSION}:user:{user_id}'
await cache.set(cache_key, data)
```

### 6. Handle Cache Failures Gracefully

```python
async def get_user(user_id: int):
    # Try cache first
    try:
        user = await cache.get(f'user:{user_id}')
        if user:
            return user
    except Exception as e:
        logger.error(f'Cache error: {e}')

    # Fallback to database
    user = await db.query(User).get(user_id)

    # Try to cache for next time
    try:
        await cache.set(f'user:{user_id}', user, ttl=300)
    except Exception:
        pass  # Don't fail if cache fails

    return user
```

### 7. Monitor Cache Performance

```python
# Regular monitoring
async def monitor_cache():
    stats = await cache.get_stats()

    hit_ratio = stats['primary']['hit_ratio']
    if hit_ratio < 0.8:  # Less than 80% hit ratio
        logger.warning(f'Low cache hit ratio: {hit_ratio:.2%}')

    size = stats['primary']['size']
    if size > 90000:  # Approaching max size
        logger.warning(f'Cache nearly full: {size} items')

# Log cache operations in development
if settings.DEBUG:
    logger.debug(f'Cache GET: {key}')
    logger.debug(f'Cache SET: {key} (ttl={ttl})')
```

### 8. Serialize Complex Objects

```python
# Use JSON for simple data
await cache.set('config', {'key': 'value'}, ttl=300)

# Use pickle for complex Python objects
from covet.cache import RedisConfig, SerializerType

config = RedisConfig(serializer=SerializerType.PICKLE)
cache = CacheManager(CacheConfig(
    backend=CacheBackend.REDIS,
    redis_config=config
))

# Now can cache complex objects
await cache.set('model', trained_ml_model, ttl=3600)
```

### 9. Avoid Caching Large Objects

```python
# BAD: Cache huge objects
await cache.set('all_users', list_of_10000_users)  # Too large!

# GOOD: Cache IDs, fetch on demand
user_ids = [user.id for user in users]
await cache.set('user_ids', user_ids, ttl=300)

# Or use pagination
await cache.set('users:page:1', users_page_1, ttl=300)
await cache.set('users:page:2', users_page_2, ttl=300)
```

### 10. Use Lazy Loading

```python
@cache_result(ttl=300)
async def get_expensive_data(key: str):
    # Only computed when not in cache
    return expensive_computation(key)

# First call: Computes and caches
result = await get_expensive_data('key')

# Subsequent calls: Returns from cache
result = await get_expensive_data('key')  # Fast!
```

## Performance

### Benchmark Results

Typical performance (operations per second):

| Backend | GET | SET | DELETE | GET_MANY (100 keys) |
|---------|-----|-----|--------|---------------------|
| Memory | 1,000,000+ | 1,000,000+ | 1,000,000+ | 100,000+ |
| Redis (local) | 100,000+ | 80,000+ | 100,000+ | 50,000+ |
| Redis (network) | 20,000-50,000 | 15,000-40,000 | 20,000-50,000 | 10,000-30,000 |
| Memcached | 30,000-60,000 | 25,000-50,000 | 30,000-60,000 | 15,000-40,000 |
| Database | 1,000-5,000 | 500-2,000 | 1,000-5,000 | 500-2,000 |

### Optimization Tips

```python
# 1. Use batch operations
# BAD: Multiple single operations
for user_id in user_ids:
    await cache.delete(f'user:{user_id}')

# GOOD: Single batch operation
keys = [f'user:{user_id}' for user_id in user_ids]
await cache.delete_many(keys)

# 2. Use pipelining (Redis)
# Batch sets
await cache.set_many({
    'key1': 'value1',
    'key2': 'value2',
    'key3': 'value3'
})

# 3. Use appropriate serialization
# JSON: Readable, slower
# PICKLE: Faster, Python-specific
# MSGPACK: Compact, fast, cross-language

# 4. Connection pooling (automatic in CovetPy)
config = RedisConfig(max_connections=50)

# 5. Use local cache for hot data
config = CacheConfig(
    backend=CacheBackend.REDIS,
    fallback_backends=[CacheBackend.MEMORY],
    memory_max_size=1000  # Keep hottest 1000 items in memory
)
```

### Memory Usage

```python
# Monitor memory usage
stats = await cache.get_stats()
memory_mb = stats['primary'].get('memory_bytes', 0) / 1024 / 1024
print(f'Cache using {memory_mb:.2f} MB')

# Limit memory usage
cache = MemoryCache(
    max_size=10000,          # Max 10k items
    max_memory_mb=100        # Max 100 MB
)

# Estimate item size
import sys
item_size = sys.getsizeof(value)
print(f'Item size: {item_size} bytes')
```

---

**Next Steps:**
- [Cache Tutorial](../tutorials/03-caching-guide.md) - Complete caching guide
- [Sessions API](./sessions.md) - Session management with caching
- [Performance Guide](../performance.md) - Optimization techniques
- [Security Guide](../tutorials/04-security-guide.md) - Secure caching practices

**Related Documentation:**
- [ORM API](./orm.md)
- [REST API](./rest.md)
- [Middleware](../architecture.md#middleware)
