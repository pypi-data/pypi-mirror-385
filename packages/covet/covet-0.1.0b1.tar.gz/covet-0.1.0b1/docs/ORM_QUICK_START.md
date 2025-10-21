# CovetPy ORM - Quick Start Guide

**Production-Ready ORM for CovetPy Framework**

---

## Table of Contents
1. [Installation & Setup](#installation--setup)
2. [Define Models](#define-models)
3. [Create Migrations](#create-migrations)
4. [Basic CRUD](#basic-crud)
5. [Querying](#querying)
6. [Relationships](#relationships)
7. [Advanced Queries](#advanced-queries)
8. [Bulk Operations](#bulk-operations)
9. [Transactions](#transactions)
10. [REST API Integration](#rest-api-integration)

---

## Installation & Setup

### 1. Configure Database Connection
```python
from covet.database.adapters import PostgreSQLAdapter

# PostgreSQL
adapter = PostgreSQLAdapter(
    host='localhost',
    port=5432,
    database='mydb',
    user='postgres',
    password='secret',
    min_pool_size=5,
    max_pool_size=20
)

await adapter.connect()
```

### 2. Import ORM Components
```python
from covet.orm import (
    Model,
    CharField, TextField, IntegerField, EmailField,
    DateTimeField, ForeignKey, ManyToMany,
    Q, F, Count, Sum, Avg,
    create_migration, MigrationRunner
)
```

---

## Define Models

### Basic Model
```python
class User(Model):
    name = CharField(max_length=100)
    email = EmailField(unique=True)
    age = IntegerField(min_value=0, max_value=150)
    bio = TextField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        table_name = 'users'
        ordering = ['-created_at']
        indexes = ['email']
```

### Model with Relationships
```python
class Post(Model):
    title = CharField(max_length=200)
    content = TextField()
    author = ForeignKey(User, on_delete='CASCADE', related_name='posts')
    tags = ManyToMany(Tag, related_name='posts')
    view_count = IntegerField(default=0)
    published_at = DateTimeField(null=True)

    class Meta:
        table_name = 'posts'
        indexes = ['title', 'published_at']
```

### All Field Types
```python
from covet.orm import (
    # Integers
    IntegerField, BigIntegerField, SmallIntegerField,
    AutoField, BigAutoField,

    # Strings
    CharField, TextField, EmailField, URLField, SlugField,

    # Numbers
    FloatField, DecimalField,

    # Boolean
    BooleanField,

    # Dates
    DateTimeField, DateField, TimeField,

    # Special
    JSONField, UUIDField, BinaryField,

    # Relationships
    ForeignKey, ManyToMany
)

class Example(Model):
    # Auto primary key (automatically added if not specified)
    # id = AutoField()

    # Strings
    name = CharField(max_length=100)
    description = TextField()
    email = EmailField()
    website = URLField()
    slug = SlugField()

    # Numbers
    price = DecimalField(max_digits=10, decimal_places=2)
    rating = FloatField(min_value=0, max_value=5)
    stock = IntegerField(default=0)

    # Boolean
    is_active = BooleanField(default=True)

    # Dates
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    published_date = DateField(null=True)

    # Special
    metadata = JSONField(default=dict)
    uuid = UUIDField(auto_create=True, unique=True)

    # Relationships
    owner = ForeignKey(User, on_delete='CASCADE')
    categories = ManyToMany(Category)
```

---

## Create Migrations

### Step 1: Create Migration
```python
from covet.orm import create_migration

migration = create_migration('0001_initial', app='myapp')

# Add table
migration.create_table('users', {
    'id': AutoField(),
    'name': CharField(max_length=100),
    'email': EmailField(unique=True),
    'age': IntegerField(),
    'created_at': DateTimeField(auto_now_add=True),
})

# Add index
migration.create_index('idx_users_email', 'users', ['email'])

# Add column to existing table
migration.add_column('users', 'bio', TextField(null=True))
```

### Step 2: Run Migration
```python
from covet.orm import MigrationRunner

runner = MigrationRunner()
runner.apply_migration(migration)

# Or rollback
runner.rollback_migration(migration)
```

---

## Basic CRUD

### Create
```python
# Method 1: create()
user = await User.objects.acreate(
    name='John Doe',
    email='john@example.com',
    age=25
)

# Method 2: save()
user = User(name='Jane Doe', email='jane@example.com', age=30)
await user.asave()
```

### Read
```python
# Get all
users = await User.objects.all()

# Get one by ID
user = await User.objects.get(id=1)

# Get one by field
user = await User.objects.get(email='john@example.com')

# Get first
user = await User.objects.first()

# Check existence
exists = await User.objects.filter(email='john@example.com').exists()

# Count
count = await User.objects.count()
```

### Update
```python
# Update instance
user = await User.objects.get(id=1)
user.name = 'John Smith'
await user.asave()

# Bulk update
await User.objects.filter(age__lt=18).update(status='minor')

# Increment
await Post.objects.filter(id=1).update(view_count=F('view_count') + 1)
```

### Delete
```python
# Delete instance
user = await User.objects.get(id=1)
await user.adelete()

# Bulk delete
await User.objects.filter(inactive=True).delete()
```

---

## Querying

### Basic Filtering
```python
# Exact match
users = await User.objects.filter(age=25).all()

# Multiple conditions (AND)
users = await User.objects.filter(age=25, is_active=True).all()

# Greater than
users = await User.objects.filter(age__gt=18).all()

# Less than or equal
users = await User.objects.filter(age__lte=65).all()

# In list
users = await User.objects.filter(id__in=[1, 2, 3]).all()

# Contains (substring)
users = await User.objects.filter(name__contains='John').all()

# Starts with
users = await User.objects.filter(email__startswith='john').all()

# Case-insensitive
users = await User.objects.filter(name__iexact='john doe').all()

# NULL checks
users = await User.objects.filter(bio__isnull=True).all()

# Range
users = await User.objects.filter(age__range=(18, 65)).all()
```

### Ordering
```python
# Ascending
users = await User.objects.order_by('name').all()

# Descending (- prefix)
users = await User.objects.order_by('-created_at').all()

# Multiple fields
users = await User.objects.order_by('age', '-name').all()

# Reverse
users = await User.objects.order_by('name').reverse().all()
```

### Limiting
```python
# First 10
users = await User.objects.limit(10).all()

# Offset and limit (pagination)
users = await User.objects.offset(20).limit(10).all()

# Slice notation
users = await User.objects.all()[10:20]

# First/Last
first_user = await User.objects.first()
last_user = await User.objects.last()
```

### Exclude
```python
# Exclude conditions
users = await User.objects.exclude(age__lt=18).all()

# Combine filter and exclude
users = await User.objects.filter(is_active=True).exclude(age__lt=18).all()
```

---

## Relationships

### ForeignKey (Many-to-One)
```python
# Define
class Post(Model):
    author = ForeignKey(User, on_delete='CASCADE', related_name='posts')

# Create with relationship
user = await User.objects.get(id=1)
post = await Post.objects.acreate(
    title='Hello World',
    author=user  # Pass the object
)

# Access related object (lazy loading)
post = await Post.objects.get(id=1)
author = post.author  # Triggers query

# Prevent N+1 with select_related
posts = await Post.objects.select_related('author').all()
for post in posts:
    print(post.author.name)  # No additional queries

# Reverse relationship
user = await User.objects.get(id=1)
posts = await user.posts.all()
```

### ManyToMany
```python
# Define
class Post(Model):
    tags = ManyToMany(Tag, related_name='posts')

# Add tags
post = await Post.objects.get(id=1)
tag1 = await Tag.objects.get(id=1)
tag2 = await Tag.objects.get(id=2)
await post.tags.add(tag1, tag2)

# Remove tags
await post.tags.remove(tag1)

# Clear all tags
await post.tags.clear()

# Get tags
tags = await post.tags.all()

# Prevent N+1 with prefetch_related
posts = await Post.objects.prefetch_related('tags').all()
for post in posts:
    for tag in post.tags.all():  # No additional queries
        print(tag.name)
```

---

## Advanced Queries

### Q Objects (Complex Conditions)
```python
from covet.orm import Q

# OR conditions
users = await User.objects.filter(
    Q(age__gte=18) | Q(is_admin=True)
).all()

# AND conditions
users = await User.objects.filter(
    Q(age__gte=18) & Q(is_active=True)
).all()

# NOT conditions
users = await User.objects.filter(
    ~Q(status='deleted')
).all()

# Complex combinations
users = await User.objects.filter(
    (Q(age__gte=18) & Q(is_active=True)) |
    Q(is_admin=True)
).all()
```

### F Objects (Field References)
```python
from covet.orm import F

# Update with field reference
await Post.objects.filter(id=1).update(
    view_count=F('view_count') + 1
)

# Arithmetic operations
await Product.objects.update(
    total_price=F('price') * F('quantity')
)

# Filter using field comparison
products = await Product.objects.filter(
    stock__lt=F('reorder_level')
).all()
```

### Aggregation
```python
from covet.orm import Count, Sum, Avg, Max, Min

# Count
user_count = await User.objects.count()

# Aggregations
stats = await Post.objects.aggregate(
    total_posts=Count('*'),
    avg_views=Avg('view_count'),
    max_views=Max('view_count'),
    min_views=Min('view_count'),
    total_views=Sum('view_count')
)
# Result: {'total_posts': 100, 'avg_views': 500.5, ...}

# Group by with annotation
users = await User.objects.annotate(
    post_count=Count('posts')
).filter(post_count__gt=10).all()
```

### Values & Values List
```python
# Return dictionaries
users = await User.objects.values('id', 'name', 'email').all()
# Result: [{'id': 1, 'name': 'John', 'email': '...'}, ...]

# Return tuples
user_ids = await User.objects.values_list('id', 'name').all()
# Result: [(1, 'John'), (2, 'Jane'), ...]

# Flat list (single field)
emails = await User.objects.values_list('email', flat=True).all()
# Result: ['john@example.com', 'jane@example.com', ...]
```

### Deferred Loading
```python
# Only load specific fields
users = await User.objects.only('id', 'name').all()
# Only id and name loaded, other fields loaded on access

# Defer specific fields
users = await User.objects.defer('bio', 'metadata').all()
# All fields except bio and metadata loaded
```

---

## Bulk Operations

### Bulk Create
```python
# Create 1000 users efficiently
users = [
    User(name=f'User{i}', email=f'user{i}@example.com')
    for i in range(1000)
]
await User.bulk_create(users, batch_size=100)
```

### Bulk Update
```python
# Update 1000 users efficiently
users = await User.objects.filter(age__lt=18).all()
for user in users:
    user.status = 'minor'

await User.bulk_update(users, fields=['status'], batch_size=100)
```

### Get or Create
```python
# Get existing or create new
user, created = await User.objects.get_or_create(
    email='john@example.com',
    defaults={'name': 'John Doe', 'age': 25}
)

if created:
    print("New user created")
else:
    print("User already existed")
```

### Update or Create
```python
# Update existing or create new
user, created = await User.objects.update_or_create(
    email='john@example.com',
    defaults={'name': 'John Smith', 'age': 26}
)
```

---

## Transactions

### Basic Transaction
```python
from covet.orm.connection import TransactionManager

async with TransactionManager(conn).atransaction():
    user = await User.objects.acreate(name='John', email='john@example.com')
    post = await Post.objects.acreate(title='Hello', author=user)
    # Commits on success, rolls back on error
```

### Nested Transactions (Savepoints)
```python
async with TransactionManager(conn).atransaction():
    user = await User.objects.acreate(name='John')

    try:
        async with TransactionManager(conn).atransaction():  # Savepoint
            post = await Post.objects.acreate(title='Hello', author=user)
            raise Exception("Oops")  # Inner transaction rolls back
    except:
        pass

    # User is still created (outer transaction continues)
```

### Manual Transaction Control
```python
from covet.orm.connection import TransactionManager

tx = TransactionManager(conn)

async with tx.atransaction():
    # Your operations here
    user = await User.objects.acreate(...)

    if error_condition:
        raise Exception("Rollback transaction")

    # Transaction commits if no exception
```

---

## REST API Integration

### Basic CRUD API
```python
from covet.api.rest import APIView
from covet.orm import User, ValidationError

class UserListAPI(APIView):
    async def get(self, request):
        """List all users."""
        users = await User.objects.all()
        return [user.to_dict() for user in users]

    async def post(self, request):
        """Create a user."""
        data = await request.json()
        try:
            user = await User.objects.acreate(**data)
            return user.to_dict(), 201
        except ValidationError as e:
            return {'error': str(e)}, 400

class UserDetailAPI(APIView):
    async def get(self, request, user_id: int):
        """Get user by ID."""
        try:
            user = await User.objects.get(id=user_id)
            return user.to_dict()
        except User.DoesNotExist:
            return {'error': 'User not found'}, 404

    async def put(self, request, user_id: int):
        """Update user."""
        try:
            user = await User.objects.get(id=user_id)
            data = await request.json()
            for key, value in data.items():
                setattr(user, key, value)
            await user.asave()
            return user.to_dict()
        except User.DoesNotExist:
            return {'error': 'User not found'}, 404

    async def delete(self, request, user_id: int):
        """Delete user."""
        try:
            user = await User.objects.get(id=user_id)
            await user.adelete()
            return {'status': 'deleted'}
        except User.DoesNotExist:
            return {'error': 'User not found'}, 404
```

### Advanced Query API
```python
class PostListAPI(APIView):
    async def get(self, request):
        """
        List posts with filtering, pagination, and ordering.

        Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - author_id: Filter by author
        - tag: Filter by tag name
        - search: Search in title
        - order_by: Order by field (default: -created_at)
        """
        # Pagination
        page = int(request.query.get('page', 1))
        per_page = int(request.query.get('per_page', 20))
        offset = (page - 1) * per_page

        # Build query
        query = Post.objects.all()

        # Filtering
        if author_id := request.query.get('author_id'):
            query = query.filter(author_id=author_id)

        if search := request.query.get('search'):
            query = query.filter(title__contains=search)

        # Ordering
        order_by = request.query.get('order_by', '-created_at')
        query = query.order_by(order_by)

        # Execute with pagination
        posts = await query.offset(offset).limit(per_page).select_related('author').prefetch_related('tags').all()

        # Count total
        total = await Post.objects.count()

        return {
            'posts': [post.to_dict() for post in posts],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
```

---

## Performance Tips

### 1. Use select_related() for ForeignKey
```python
# BAD: N+1 queries
posts = await Post.objects.all()
for post in posts:
    print(post.author.name)  # Query for each post

# GOOD: 1 query with JOIN
posts = await Post.objects.select_related('author').all()
for post in posts:
    print(post.author.name)  # No additional queries
```

### 2. Use prefetch_related() for ManyToMany
```python
# BAD: N+1 queries
posts = await Post.objects.all()
for post in posts:
    for tag in post.tags.all():  # Query for each post
        print(tag.name)

# GOOD: 2 queries total
posts = await Post.objects.prefetch_related('tags').all()
for post in posts:
    for tag in post.tags.all():  # No additional queries
        print(tag.name)
```

### 3. Use only() for large models
```python
# Only load needed fields
users = await User.objects.only('id', 'name', 'email').all()
```

### 4. Use bulk operations
```python
# BAD: 1000 queries
for i in range(1000):
    await User.objects.acreate(name=f'User{i}')

# GOOD: 10 queries (batch_size=100)
users = [User(name=f'User{i}') for i in range(1000)]
await User.bulk_create(users, batch_size=100)
```

### 5. Use aggregation instead of loading all objects
```python
# BAD: Load all objects to count
users = await User.objects.all()
count = len(users)

# GOOD: Count in database
count = await User.objects.count()
```

---

## Error Handling

```python
from covet.orm import (
    DoesNotExist,
    MultipleObjectsReturned,
    ValidationError,
    IntegrityError
)

# DoesNotExist
try:
    user = await User.objects.get(id=999)
except User.DoesNotExist:
    print("User not found")

# MultipleObjectsReturned
try:
    user = await User.objects.get(name='John')
except MultipleObjectsReturned:
    print("Multiple users found")

# ValidationError
try:
    user = User(name='', email='invalid')
    await user.asave()
except ValidationError as e:
    print(f"Validation failed: {e}")

# IntegrityError (unique constraint)
try:
    await User.objects.acreate(email='john@example.com')
    await User.objects.acreate(email='john@example.com')
except IntegrityError as e:
    print(f"Constraint violation: {e}")
```

---

## Complete Example

```python
from covet.orm import (
    Model, CharField, TextField, EmailField, IntegerField,
    DateTimeField, ForeignKey, ManyToMany,
    Q, Count, create_migration, MigrationRunner
)

# 1. Define models
class User(Model):
    name = CharField(max_length=100)
    email = EmailField(unique=True)
    created_at = DateTimeField(auto_now_add=True)

class Tag(Model):
    name = CharField(max_length=50, unique=True)

class Post(Model):
    title = CharField(max_length=200)
    content = TextField()
    author = ForeignKey(User, on_delete='CASCADE', related_name='posts')
    tags = ManyToMany(Tag, related_name='posts')
    view_count = IntegerField(default=0)
    published_at = DateTimeField(null=True)

# 2. Create migration
migration = create_migration('0001_blog_initial')
migration.create_table('users', {
    'id': AutoField(),
    'name': CharField(max_length=100),
    'email': EmailField(unique=True),
    'created_at': DateTimeField(auto_now_add=True),
})
migration.create_table('tags', {
    'id': AutoField(),
    'name': CharField(max_length=50, unique=True),
})
migration.create_table('posts', {
    'id': AutoField(),
    'title': CharField(max_length=200),
    'content': TextField(),
    'author_id': IntegerField(),
    'view_count': IntegerField(default=0),
    'published_at': DateTimeField(null=True),
})

runner = MigrationRunner()
runner.apply_migration(migration)

# 3. Use the ORM
async def main():
    # Create user
    user = await User.objects.acreate(
        name='John Doe',
        email='john@example.com'
    )

    # Create tags
    python_tag = await Tag.objects.acreate(name='Python')
    orm_tag = await Tag.objects.acreate(name='ORM')

    # Create post
    post = await Post.objects.acreate(
        title='Building an ORM',
        content='Here is how...',
        author=user
    )

    # Add tags
    await post.tags.add(python_tag, orm_tag)

    # Query with relationships
    posts = await Post.objects.filter(
        Q(published_at__isnull=False) & Q(author=user)
    ).select_related('author').prefetch_related('tags').order_by('-published_at').limit(10).all()

    # Aggregation
    stats = await Post.objects.aggregate(
        total_posts=Count('*'),
        total_views=Sum('view_count')
    )

    print(f"Total posts: {stats['total_posts']}")
    print(f"Total views: {stats['total_views']}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

---

## Next Steps

1. **Read the full documentation:** `/docs/SPRINT_2_AUDIT_REPORT.md`
2. **Check daily audits:** `/docs/DAILY_AUDIT_REPORTS.md`
3. **Write tests:** Create unit and integration tests for your models
4. **Production deployment:** Set up connection pooling, monitoring, backups
5. **Performance tuning:** Profile queries, add indexes, optimize relationships

---

**Happy Coding with CovetPy ORM!** 🚀
