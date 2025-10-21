# CovetPy Framework - ORM and Serialization

## Table of Contents
1. [ORM Architecture](#orm-architecture)
2. [Database Connections](#database-connections)
3. [Model Definition](#model-definition)
4. [Query Builder](#query-builder)
5. [Serialization System](#serialization-system)
6. [Data Validation](#data-validation)
7. [Performance Optimizations](#performance-optimizations)
8. [Migration System](#migration-system)

## ORM Architecture

The CovetPy ORM is designed for high performance with support for both synchronous and asynchronous operations, leveraging Rust for query compilation and Python for ease of use.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Python ORM Layer                          │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │   Models    │ │Query Builder │ │   Serializers      │   │
│  └─────────────┘ └──────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                         PyO3 Bridge
                               │
┌─────────────────────────────────────────────────────────────┐
│                     Rust Query Engine                        │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │Query Parser │ │  Optimizer   │ │ Connection Pool    │   │
│  └─────────────┘ └──────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Model Layer**: Python classes with type hints
2. **Query Builder**: Fluent API for query construction
3. **Query Engine**: Rust-based query optimization
4. **Connection Pool**: High-performance connection management
5. **Serialization**: SIMD-optimized JSON/MessagePack

## Database Connections

### Connection Configuration

```python
from covet.db import Database, DatabaseConfig

# Single database configuration
db = Database(
    url="postgresql://user:pass@localhost/dbname",
    pool_size=50,
    max_overflow=10,
    pool_timeout=30,
    echo=False
)

# Multiple database support
databases = {
    'primary': Database(
        url="postgresql://localhost/main_db",
        pool_size=100
    ),
    'readonly': Database(
        url="postgresql://replica/main_db",
        pool_size=200,
        readonly=True
    ),
    'analytics': Database(
        url="clickhouse://localhost/analytics",
        pool_size=50
    ),
    'cache': Database(
        url="redis://localhost:6379/0",
        pool_size=20
    )
}
```

### Connection Pool Management

```python
# Rust-backed connection pool
class ConnectionPool:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._rust_pool = RustConnectionPool(
            url=config.url,
            min_size=config.min_size,
            max_size=config.max_size,
            max_idle_time=config.max_idle_time,
            connection_timeout=config.connection_timeout
        )
    
    async def acquire(self) -> Connection:
        """Acquire connection from pool"""
        conn = await self._rust_pool.acquire()
        return Connection(conn, self)
    
    async def release(self, conn: Connection):
        """Return connection to pool"""
        await self._rust_pool.release(conn._rust_conn)
    
    @contextmanager
    async def transaction(self):
        """Transaction context manager"""
        conn = await self.acquire()
        try:
            await conn.begin()
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await self.release(conn)
```

### Multi-Database Support

```python
from covet.db import MultiDB

# Configure multiple databases
db = MultiDB({
    'default': 'postgresql://localhost/main',
    'users': 'postgresql://localhost/users',
    'analytics': 'clickhouse://localhost/analytics',
    'cache': 'redis://localhost:6379'
})

# Use specific database
@app.get('/users')
async def get_users():
    async with db.bind('users') as conn:
        return await User.all(conn)

# Automatic routing based on model
class User(Model):
    __database__ = 'users'  # Automatically uses users DB
    
    id = Integer(primary_key=True)
    name = String(max_length=100)
    email = String(unique=True)

class Analytics(Model):
    __database__ = 'analytics'  # Uses ClickHouse
    
    event_id = UUID(primary_key=True)
    user_id = Integer()
    event_type = String()
    timestamp = DateTime()
```

## Model Definition

### Basic Model Structure

```python
from covet.orm import Model, fields

class User(Model):
    __tablename__ = 'users'
    __database__ = 'default'
    
    # Fields
    id = fields.Integer(primary_key=True)
    username = fields.String(max_length=50, unique=True, index=True)
    email = fields.String(max_length=255, unique=True)
    password_hash = fields.String(max_length=255)
    
    # Relationships
    profile = fields.OneToOne('UserProfile', back_populates='user')
    posts = fields.OneToMany('Post', back_populates='author')
    
    # Timestamps
    created_at = fields.DateTime(auto_now_add=True)
    updated_at = fields.DateTime(auto_now=True)
    
    # Indexes
    class Meta:
        indexes = [
            Index('idx_email_username', 'email', 'username'),
            Index('idx_created_at', 'created_at', order='DESC')
        ]
        constraints = [
            UniqueConstraint('email', name='unique_email'),
            CheckConstraint('length(username) >= 3', name='username_length')
        ]

class Post(Model):
    __tablename__ = 'posts'
    
    id = fields.UUID(primary_key=True, default=uuid4)
    title = fields.String(max_length=200)
    content = fields.Text()
    published = fields.Boolean(default=False)
    
    # Foreign keys
    author_id = fields.Integer(foreign_key='users.id')
    author = fields.ManyToOne('User', back_populates='posts')
    
    # JSON field
    metadata = fields.JSON(default=dict)
    
    # Custom field types
    tags = fields.Array(fields.String)
    view_count = fields.Integer(default=0)
```

### Advanced Field Types

```python
# Custom field with validation
class EmailField(fields.String):
    def __init__(self, **kwargs):
        super().__init__(max_length=255, **kwargs)
    
    def validate(self, value):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise ValidationError('Invalid email format')
        return value

# Encrypted field
class EncryptedField(fields.String):
    def __init__(self, key=None, **kwargs):
        super().__init__(**kwargs)
        self.key = key or settings.ENCRYPTION_KEY
    
    def to_db(self, value):
        if value is None:
            return None
        return encrypt(value, self.key)
    
    def from_db(self, value):
        if value is None:
            return None
        return decrypt(value, self.key)

# Usage
class SecureModel(Model):
    ssn = EncryptedField()
    credit_card = EncryptedField(key=settings.PCI_KEY)
```

## Query Builder

### Basic Queries

```python
# Simple queries
users = await User.all()
user = await User.get(id=1)
user = await User.first(username='john')

# Filtering
active_users = await User.filter(is_active=True).all()
recent_users = await User.filter(
    created_at__gte=datetime.now() - timedelta(days=7)
).all()

# Complex queries
users = await User.filter(
    Q(email__contains='@gmail.com') | Q(username__startswith='admin'),
    is_active=True
).order_by('-created_at').limit(10).all()
```

### Advanced Query Features

```python
# Aggregations
from covet.orm import Count, Sum, Avg, Max, Min

stats = await Post.aggregate(
    total=Count('id'),
    total_views=Sum('view_count'),
    avg_views=Avg('view_count'),
    max_views=Max('view_count')
)

# Group by
user_posts = await Post.values('author_id').annotate(
    post_count=Count('id'),
    total_views=Sum('view_count')
).group_by('author_id')

# Joins
posts_with_authors = await Post.select_related('author').all()
users_with_all_relations = await User.prefetch_related('posts', 'profile').all()

# Raw queries
results = await db.execute("""
    SELECT u.*, COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.author_id
    GROUP BY u.id
    HAVING COUNT(p.id) > 5
""")

# Query optimization hints
users = await User.filter(is_active=True)\
    .hint('INDEX(users idx_active_created)')\
    .order_by('-created_at')\
    .all()
```

### Query Chain API

```python
# Fluent query interface
query = User.filter(is_active=True)

# Add conditions dynamically
if search_term:
    query = query.filter(
        Q(username__icontains=search_term) |
        Q(email__icontains=search_term)
    )

if role:
    query = query.filter(role=role)

# Execute
users = await query.order_by('username').paginate(page=1, per_page=20)
```

## Serialization System

### Built-in Serializers

```python
from covet.serializers import ModelSerializer, fields

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    # Custom field
    full_name = fields.Method('get_full_name')
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class PostSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = fields.Integer(write_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
        depth = 1  # Serialize related objects
```

### High-Performance Serialization

```python
# SIMD-optimized JSON serialization
from covet.serializers import SimdJSONSerializer

# Automatic serialization
@app.get('/users')
async def list_users():
    users = await User.all()
    return SimdJSONSerializer(users, many=True).data

# Custom serialization
class FastUserSerializer(SimdJSONSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        # Use SIMD operations for these fields
        simd_fields = ['id', 'email']

# MessagePack for binary
from covet.serializers import MessagePackSerializer

@app.get('/binary/users')
async def binary_users():
    users = await User.all()
    return MessagePackSerializer(users).pack()
```

### Serialization Performance

```python
# Benchmark results
"""
JSON (standard): 1000 objects in 45ms
OrJSON: 1000 objects in 12ms
SIMD-JSON: 1000 objects in 3ms
MessagePack: 1000 objects in 2ms
"""

# Streaming serialization for large datasets
@app.get('/stream/users')
async def stream_users():
    async def generate():
        async for user in User.stream():
            yield SimdJSONSerializer(user).data + b'\n'
    
    return StreamingResponse(generate(), media_type='application/x-ndjson')
```

## Data Validation

### Model-Level Validation

```python
class User(Model):
    email = fields.String(max_length=255)
    age = fields.Integer(min_value=0, max_value=150)
    
    def validate_email(self, value):
        if not '@' in value:
            raise ValidationError('Invalid email')
        return value.lower()
    
    def validate(self):
        """Model-level validation"""
        super().validate()
        
        if self.age < 18 and self.is_premium:
            raise ValidationError('Premium accounts require age 18+')

# Async validation
class AsyncUser(Model):
    username = fields.String(unique=True)
    
    async def validate_username(self, value):
        if await User.exists(username=value):
            raise ValidationError('Username already taken')
        return value
```

### Serializer Validation

```python
class UserRegistrationSerializer(ModelSerializer):
    password = fields.String(write_only=True, min_length=8)
    password_confirm = fields.String(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate_password(self, value):
        if not any(c.isupper() for c in value):
            raise ValidationError('Password must contain uppercase')
        if not any(c.isdigit() for c in value):
            raise ValidationError('Password must contain digit')
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise ValidationError('Passwords do not match')
        
        # Remove confirmation field
        data.pop('password_confirm')
        
        # Hash password
        data['password_hash'] = hash_password(data.pop('password'))
        
        return data
```

## Performance Optimizations

### Query Optimization

```python
# N+1 query prevention
# Bad - N+1 queries
posts = await Post.all()
for post in posts:
    author = await post.author  # Additional query per post

# Good - Single query with join
posts = await Post.select_related('author').all()
for post in posts:
    author = post.author  # No additional query

# Batch loading
user_ids = [1, 2, 3, 4, 5]
users = await User.filter(id__in=user_ids).all()

# Query result caching
@cache(ttl=300)  # Cache for 5 minutes
async def get_popular_posts():
    return await Post.filter(
        view_count__gte=1000
    ).order_by('-view_count').limit(10).all()
```

### Connection Pooling

```python
# Rust-backed connection pool with health checks
class HealthCheckPool(ConnectionPool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.health_check_interval = 30  # seconds
        self.start_health_check()
    
    async def health_check(self):
        while True:
            await asyncio.sleep(self.health_check_interval)
            
            # Check all idle connections
            for conn in self.idle_connections:
                try:
                    await conn.execute('SELECT 1')
                except Exception:
                    await self.remove_connection(conn)
```

### Bulk Operations

```python
# Bulk insert
users = [
    User(username=f'user{i}', email=f'user{i}@example.com')
    for i in range(10000)
]
await User.bulk_create(users, batch_size=1000)

# Bulk update
await User.bulk_update(
    users,
    fields=['email', 'updated_at'],
    batch_size=1000
)

# Bulk upsert
await User.bulk_upsert(
    users,
    conflict_target=['username'],
    update_fields=['email', 'updated_at']
)
```

## Migration System

### Migration Management

```python
# Create migration
$ covet makemigration --name add_user_table

# Generated migration file
from covet.migrations import Migration

class AddUserTable(Migration):
    dependencies = ['0001_initial']
    
    operations = [
        CreateTable(
            'users',
            fields=[
                ('id', Integer(primary_key=True)),
                ('username', String(max_length=50, unique=True)),
                ('email', String(max_length=255, unique=True)),
                ('created_at', DateTime(auto_now_add=True))
            ],
            indexes=[
                Index('idx_username', 'username'),
                Index('idx_email', 'email')
            ]
        )
    ]
    
    async def forward(self, db):
        """Custom forward migration logic"""
        await db.execute("CREATE EXTENSION IF NOT EXISTS 'uuid-ossp'")
    
    async def backward(self, db):
        """Custom backward migration logic"""
        pass

# Run migrations
$ covet migrate
$ covet migrate --database analytics
$ covet migrate --fake  # Mark as applied without running
```

### Schema Evolution

```python
# Safe schema changes
class SafeMigration(Migration):
    atomic = False  # Run outside transaction for large tables
    
    operations = [
        # Add column with default
        AddColumn('users', 'is_active', Boolean(default=True)),
        
        # Create index concurrently
        CreateIndex(
            'idx_users_created',
            'users',
            ['created_at'],
            concurrently=True
        ),
        
        # Rename column safely
        RenameColumn('users', 'name', 'full_name'),
        
        # Add constraint with validation
        AddConstraint(
            'users',
            CheckConstraint('age >= 0', name='age_positive'),
            validate=True
        )
    ]
```

## Database-Specific Features

### PostgreSQL

```python
# PostgreSQL-specific features
from covet.db.postgres import ArrayField, JSONBField, TSVectorField

class PostgresModel(Model):
    tags = ArrayField(base_field=String())
    metadata = JSONBField(default=dict)
    search_vector = TSVectorField()
    
    class Meta:
        indexes = [
            GINIndex('search_vector'),
            GiSTIndex('location'),
            BRINIndex('created_at')
        ]

# Full-text search
results = await PostgresModel.filter(
    search_vector__match='python & framework'
).all()

# JSON queries
results = await PostgresModel.filter(
    metadata__contains={'type': 'article'},
    metadata__user__name='John'
).all()
```

### MongoDB

```python
# MongoDB support
from covet.db.mongo import Document, EmbeddedDocument

class Address(EmbeddedDocument):
    street = fields.String()
    city = fields.String()
    country = fields.String()

class MongoUser(Document):
    __collection__ = 'users'
    
    username = fields.String(unique=True)
    addresses = fields.List(EmbeddedDocument(Address))
    tags = fields.List(fields.String())
    
    class Meta:
        indexes = [
            {'fields': ['username'], 'unique': True},
            {'fields': ['tags'], 'sparse': True},
            {'fields': [('created_at', -1)]}
        ]

# Aggregation pipeline
pipeline = [
    {'$match': {'tags': {'$in': ['python', 'rust']}}},
    {'$group': {
        '_id': '$country',
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}}
]
results = await MongoUser.aggregate(pipeline)
```

### Redis

```python
# Redis caching and data structures
from covet.db.redis import RedisModel, TTL

class Session(RedisModel):
    __key_prefix__ = 'session'
    __ttl__ = 3600  # 1 hour
    
    user_id = fields.Integer()
    data = fields.JSON()
    
    @classmethod
    def generate_key(cls, user_id):
        return f"{cls.__key_prefix__}:{user_id}"

# Usage
session = Session(user_id=123, data={'theme': 'dark'})
await session.save()

# Redis data structures
await redis.zadd('leaderboard', {'user1': 100, 'user2': 200})
top_users = await redis.zrange('leaderboard', 0, 9, withscores=True)
```

This completes the comprehensive ORM and serialization documentation for the CovetPy Framework.