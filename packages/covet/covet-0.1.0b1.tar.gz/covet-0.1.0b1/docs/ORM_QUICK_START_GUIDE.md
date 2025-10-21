# CovetPy ORM - Quick Start Guide
## Django-Compatible ORM for Modern Python Applications

**Version:** 1.0.0-rc.1
**Last Updated:** 2025-10-11
**Compatibility:** Python 3.10+, AsyncIO-native

---

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Field Types](#field-types)
4. [Relationships](#relationships)
5. [QuerySet API](#queryset-api)
6. [Advanced Queries with F() and Q()](#advanced-queries)
7. [N+1 Query Prevention](#n1-query-prevention)
8. [Performance Optimization](#performance-optimization)
9. [Best Practices](#best-practices)

---

## Installation

```bash
pip install covetpy

# Or from source
git clone https://github.com/covetpy/covetpy.git
cd covetpy
pip install -e .
```

### Database Setup

```python
# config.py
from covet.database.orm import register_adapter
from covet.database.adapters.postgresql import PostgreSQLAdapter

# Register database adapter
adapter = PostgreSQLAdapter(
    host="localhost",
    port=5432,
    database="myapp",
    user="postgres",
    password="secret"
)
await adapter.connect()
register_adapter("default", adapter)
```

---

## Basic Usage

### Define Models

```python
from covet.database.orm import (
    Model, CharField, EmailField, DateTimeField,
    BooleanField, IntegerField, ForeignKey, CASCADE
)

class User(Model):
    """User account model."""

    username = CharField(max_length=100, unique=True)
    email = EmailField(unique=True)
    first_name = CharField(max_length=50, nullable=True)
    last_name = CharField(max_length=50, nullable=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['email']),
            Index(fields=['username', 'email'])
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"


class Profile(Model):
    """User profile with additional information."""

    user = ForeignKey(User, on_delete=CASCADE, related_name='profile')
    bio = TextField(nullable=True)
    avatar_url = URLField(nullable=True)
    birth_date = DateField(nullable=True)
    location = CharField(max_length=100, nullable=True)

    class Meta:
        db_table = 'profiles'
```

### CRUD Operations

```python
# CREATE
user = await User.objects.create(
    username='alice',
    email='alice@example.com',
    first_name='Alice',
    last_name='Smith'
)

# Or using save()
user = User(username='bob', email='bob@example.com')
await user.save()

# READ - Single object
user = await User.objects.get(id=1)
user = await User.objects.get(username='alice')

# READ - Multiple objects
all_users = await User.objects.all()
active_users = await User.objects.filter(is_active=True).all()

# UPDATE
user.first_name = 'Alice Updated'
await user.save()

# Bulk update
await User.objects.filter(is_active=False).update(is_active=True)

# DELETE
await user.delete()

# Bulk delete
await User.objects.filter(created_at__lt=one_year_ago).delete()
```

---

## Field Types

### All 17+ Supported Field Types

```python
from covet.database.orm import (
    CharField, TextField, IntegerField, BigIntegerField,
    SmallIntegerField, FloatField, DecimalField, BooleanField,
    DateTimeField, DateField, TimeField, JSONField, UUIDField,
    EmailField, URLField, BinaryField, ArrayField, EnumField
)

class Product(Model):
    # Text fields
    name = CharField(max_length=200)
    description = TextField()
    sku = CharField(max_length=50, unique=True)

    # Numeric fields
    price = DecimalField(max_digits=10, decimal_places=2)
    quantity = IntegerField(default=0)
    weight = FloatField()  # in kg

    # Boolean
    is_available = BooleanField(default=True)
    is_featured = BooleanField(default=False)

    # Date/Time
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    available_from = DateField()

    # Special types
    id = UUIDField(primary_key=True, auto_generate=True)
    metadata = JSONField(default=dict)
    tags = ArrayField(CharField(max_length=50))  # PostgreSQL only

    # Internet fields (with validation)
    website = URLField(nullable=True)
    support_email = EmailField()
```

### Field Options

```python
field = CharField(
    max_length=100,          # Maximum length
    min_length=3,            # Minimum length
    unique=True,             # Unique constraint
    nullable=False,          # Can be NULL
    default="default_value", # Default value
    default_factory=uuid.uuid4,  # Callable for default
    db_column="custom_name", # Database column name
    db_index=True,           # Create index
    validators=[my_validator],  # Custom validators
    verbose_name="Display Name",
    help_text="Help text for docs",
    editable=True,           # Can be edited
    choices=[('A', 'Option A'), ('B', 'Option B')]
)
```

---

## Relationships

### ForeignKey (Many-to-One)

```python
class Author(Model):
    name = CharField(max_length=100)

class Post(Model):
    title = CharField(max_length=200)
    content = TextField()
    author = ForeignKey(
        Author,
        on_delete=CASCADE,  # DELETE, SET_NULL, PROTECT, etc.
        related_name='posts'  # Reverse accessor
    )

# Forward relation
post = await Post.objects.get(id=1)
author = await post.author  # Loads Author instance

# Reverse relation
author = await Author.objects.get(id=1)
posts = await author.posts.all()  # QuerySet of Posts
post_count = await author.posts.count()
```

### OneToOneField

```python
class User(Model):
    username = CharField(max_length=100)

class Profile(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='profile')
    bio = TextField()

# Forward relation
profile = await Profile.objects.get(id=1)
user = await profile.user

# Reverse relation (single object, not QuerySet)
user = await User.objects.get(id=1)
profile = await user.profile  # Single Profile instance
```

### ManyToManyField

```python
class Tag(Model):
    name = CharField(max_length=50, unique=True)

class Post(Model):
    title = CharField(max_length=200)
    tags = ManyToManyField(Tag, related_name='posts')

# Add tags
post = await Post.objects.get(id=1)
tag1 = await Tag.objects.get(name='python')
tag2 = await Tag.objects.get(name='django')

await post.tags.add(tag1, tag2)
await post.tags.add(tag3.id)  # Can use PK

# Get all tags
tags = await post.tags.all()

# Remove tags
await post.tags.remove(tag1)

# Clear all
await post.tags.clear()

# Set exact list
await post.tags.set([tag1, tag2, tag3])

# Reverse relation
tag = await Tag.objects.get(name='python')
posts_with_tag = await tag.posts.all()
```

### Cascade Options

```python
from covet.database.orm.relationships import (
    CASCADE,      # Delete related objects
    PROTECT,      # Prevent deletion if related objects exist
    RESTRICT,     # Similar to PROTECT
    SET_NULL,     # Set FK to NULL (requires nullable=True)
    SET_DEFAULT,  # Set FK to default value
    DO_NOTHING    # No action (may cause integrity errors)
)

class Comment(Model):
    post = ForeignKey(Post, on_delete=CASCADE)  # Delete comment when post deleted
    author = ForeignKey(User, on_delete=SET_NULL, nullable=True)  # Keep comment, set author to NULL
```

---

## QuerySet API

### Filtering and Lookups

```python
# Exact match
users = await User.objects.filter(username='alice').all()

# Multiple conditions (AND)
users = await User.objects.filter(
    is_active=True,
    email__endswith='@example.com'
).all()

# Exclude
users = await User.objects.exclude(username='admin').all()

# Field lookups
results = await Product.objects.filter(
    price__gt=100,           # Greater than
    price__gte=100,          # Greater than or equal
    price__lt=1000,          # Less than
    price__lte=1000,         # Less than or equal
    name__exact='Widget',    # Exact match (case-sensitive)
    name__iexact='widget',   # Case-insensitive exact
    name__contains='idg',    # Contains substring
    name__icontains='IDG',   # Case-insensitive contains
    name__startswith='Wid',  # Starts with
    name__endswith='get',    # Ends with
    id__in=[1, 2, 3, 4],     # In list
    description__isnull=True,  # IS NULL check
    created_at__year=2024,   # Date part extraction
).all()

# Chaining filters
cheap_active = await Product.objects.filter(
    price__lt=100
).filter(
    is_available=True
).order_by('price').all()
```

### Ordering and Pagination

```python
# Order by single field
products = await Product.objects.order_by('price').all()

# Descending order
products = await Product.objects.order_by('-price').all()

# Multiple fields
products = await Product.objects.order_by('category', '-price').all()

# Limit and offset
top_10 = await Product.objects.order_by('-price').limit(10).all()

# Pagination
page_2 = await Product.objects.offset(20).limit(10).all()

# First and last
first = await Product.objects.order_by('created_at').first()
latest = await Product.objects.order_by('created_at').last()
```

### Aggregation

```python
from covet.database.orm import Count, Sum, Avg, Max, Min

# Aggregate over entire QuerySet
stats = await Product.objects.aggregate(
    total_count=Count('*'),
    avg_price=Avg('price'),
    max_price=Max('price'),
    min_price=Min('price'),
    total_value=Sum('price')
)
# Returns: {'total_count': 1000, 'avg_price': 45.67, ...}

# Annotate each object
products = await Product.objects.annotate(
    order_count=Count('orders')
).filter(order_count__gt=10).all()
```

### Utility Methods

```python
# Count
count = await User.objects.filter(is_active=True).count()

# Exists
exists = await User.objects.filter(email=email).exists()

# Get or Create
user, created = await User.objects.get_or_create(
    email='new@example.com',
    defaults={'username': 'newuser'}
)

# Update or Create
user, created = await User.objects.update_or_create(
    email='user@example.com',
    defaults={'username': 'updated_name', 'is_active': True}
)

# Distinct
usernames = await User.objects.values_list('username', flat=True).distinct()
```

### values() and values_list()

```python
# Return dictionaries
users = await User.objects.values('id', 'username', 'email').all()
# Returns: [{'id': 1, 'username': 'alice', 'email': 'alice@example.com'}, ...]

# Return tuples
users = await User.objects.values_list('id', 'username').all()
# Returns: [(1, 'alice'), (2, 'bob'), ...]

# Flat list (single field)
usernames = await User.objects.values_list('username', flat=True).all()
# Returns: ['alice', 'bob', 'charlie', ...]
```

---

## Advanced Queries

### F() Expressions

**Use F() for database-side field references and atomic operations.**

```python
from covet.database.orm.query_expressions import F

# Atomic increment (no race conditions!)
await Post.objects.filter(id=1).update(views=F('views') + 1)

# Field comparisons
expensive_products = await Product.objects.filter(
    price__gt=F('cost') * 2  # Price more than 2x cost
).all()

# Complex calculations
await Order.objects.filter(id=1).update(
    total=F('subtotal') + F('tax') - F('discount')
)

# Mathematical operations
await Statistic.objects.update(
    average=F('total_sum') / F('count'),
    variance=F('sum_of_squares') - (F('sum') ** 2 / F('n'))
)
```

### Q() Objects

**Use Q() for complex query logic with OR, AND, NOT.**

```python
from covet.database.orm.query_expressions import Q

# OR condition
results = await User.objects.filter(
    Q(username__startswith='admin') | Q(email__endswith='@admin.com')
).all()

# Complex nested conditions
active_admins_or_moderators = await User.objects.filter(
    Q(is_active=True) & (Q(role='admin') | Q(role='moderator'))
).all()

# NOT condition
non_deleted = await Post.objects.filter(~Q(status='deleted')).all()

# Combining Q objects
q1 = Q(category='electronics')
q2 = Q(price__gte=1000)
q3 = Q(is_featured=True)

premium_electronics = await Product.objects.filter(q1 & q2).all()
featured_or_premium = await Product.objects.filter(q3 | q2).all()

# Dynamic query building
filters = Q()
if search_term:
    filters |= Q(title__icontains=search_term)
if min_price:
    filters &= Q(price__gte=min_price)
if category:
    filters &= Q(category=category)

results = await Product.objects.filter(filters).all()
```

---

## N+1 Query Prevention

### Understanding N+1 Queries

```python
# ❌ BAD: N+1 queries (1 + N queries)
users = await User.objects.all()  # 1 query
for user in users:
    profile = await user.profile  # N queries! (one per user)
    print(f"{user.username}: {profile.bio}")

# ✅ GOOD: 2 queries total with select_related()
users = await User.objects.select_related('profile').all()  # 2 queries (with JOIN)
for user in users:
    profile = user.profile  # No query - already loaded!
    print(f"{user.username}: {profile.bio}")
```

### select_related() for ForeignKey/OneToOne

**Use select_related() for forward ForeignKey and OneToOne relationships.**

```python
# Load related objects with JOIN
posts = await Post.objects.select_related('author').all()
for post in posts:
    print(f"{post.title} by {post.author.name}")  # No extra queries!

# Multiple relationships
comments = await Comment.objects.select_related(
    'post',
    'author',
    'post__author'  # Nested relationship
).all()

# Can still filter
recent_posts = await Post.objects.select_related('author').filter(
    created_at__gte=last_week
).order_by('-created_at').all()
```

### prefetch_related() for ManyToMany and Reverse ForeignKey

**Use prefetch_related() for reverse relationships and ManyToMany.**

```python
# ❌ BAD: N+1 queries
authors = await Author.objects.all()  # 1 query
for author in authors:
    posts = await author.posts.all()  # N queries!
    print(f"{author.name} has {len(posts)} posts")

# ✅ GOOD: 2 queries with prefetch_related()
authors = await Author.objects.prefetch_related('posts').all()  # 2 queries
for author in authors:
    posts = await author.posts.all()  # No query - cached!
    print(f"{author.name} has {len(posts)} posts")

# ManyToMany
posts = await Post.objects.prefetch_related('tags').all()
for post in posts:
    tags = await post.tags.all()  # Cached!
    print(f"{post.title}: {', '.join(t.name for t in tags)}")

# Combine select_related and prefetch_related
posts = await Post.objects.select_related('author').prefetch_related(
    'comments',
    'tags'
).all()
```

### Automatic N+1 Detection (Development Mode)

```python
from covet.database.orm.n_plus_one_detector import enable_query_tracking

# Enable in development settings
enable_query_tracking(
    warn_threshold=10,      # Warn after 10 similar queries
    error_threshold=50,     # Error after 50 similar queries
    enable_stack_traces=True  # Capture stack traces for debugging
)

# Now all N+1 patterns are automatically detected:
# ================================================================================
# N+1 QUERY DETECTED (WARNING)
# ================================================================================
# Query executed 47 times:
#   SELECT * FROM profiles WHERE user_id = ?
#
# Total time wasted: 234.56ms
#
# OPTIMIZATION SUGGESTION:
#   Use select_related('profile') to load related Profile objects in a single
#   query with JOIN
#
# First occurrence stack trace:
#   File "app.py", line 42, in get_users_with_profiles
#     profile = await user.profile
# ================================================================================

# Get query report
from covet.database.orm.n_plus_one_detector import get_query_tracker

tracker = get_query_tracker()
report = tracker.get_query_report()

print(f"Total queries: {report['total_queries']}")
print(f"Total time: {report['total_query_time']}ms")
print(f"Detected N+1 patterns: {len(report['detected_patterns'])}")

# Print summary
tracker.print_query_summary()
```

---

## Performance Optimization

### only() and defer() for Field Selection

```python
# Load only specific fields (not yet implemented - coming soon)
users = await User.objects.only('id', 'username', 'email').all()
# Loads only id, username, email - saves memory

# Defer heavy fields
posts = await Post.objects.defer('content', 'rendered_html').all()
# Loads all fields except content and rendered_html
```

### Bulk Operations

```python
# Bulk create
users = [
    User(username=f'user{i}', email=f'user{i}@example.com')
    for i in range(1000)
]
await User.objects.bulk_create(users)  # Single transaction

# Bulk update (coming soon)
await User.objects.filter(is_active=False).update(is_active=True)
```

### Database Indexes

```python
class Product(Model):
    name = CharField(max_length=200, db_index=True)  # Single field index
    sku = CharField(max_length=50, unique=True)  # Unique index

    class Meta:
        indexes = [
            Index(fields=['category', 'price']),  # Composite index
            Index(fields=['-created_at']),  # Descending index
        ]
```

---

## Best Practices

### 1. Always Use Eager Loading for Relationships

```python
# ✅ GOOD: Load everything needed upfront
posts = await Post.objects.select_related('author').prefetch_related(
    'tags',
    'comments__author'
).all()

# ❌ BAD: Lazy loading in loops
posts = await Post.objects.all()
for post in posts:
    author = await post.author  # N+1!
```

### 2. Use Bulk Operations

```python
# ✅ GOOD: Bulk update
await User.objects.filter(last_login__lt=six_months_ago).update(is_active=False)

# ❌ BAD: Update in loop
users = await User.objects.filter(last_login__lt=six_months_ago).all()
for user in users:
    user.is_active = False
    await user.save()  # N queries!
```

### 3. Filter at Database Level

```python
# ✅ GOOD: Filter in database
active_users = await User.objects.filter(is_active=True).count()

# ❌ BAD: Filter in Python
all_users = await User.objects.all()
active_count = len([u for u in all_users if u.is_active])
```

### 4. Use F() for Atomic Updates

```python
# ✅ GOOD: Atomic increment
await Post.objects.filter(id=1).update(views=F('views') + 1)

# ❌ BAD: Race condition
post = await Post.objects.get(id=1)
post.views += 1
await post.save()  # Another request might update in between!
```

### 5. Index Frequently Queried Fields

```python
class User(Model):
    email = EmailField(unique=True, db_index=True)  # Frequently queried
    username = CharField(max_length=100, unique=True)  # Auto-indexed
    last_login = DateTimeField(db_index=True)  # Used in queries

    class Meta:
        indexes = [
            Index(fields=['email', 'is_active']),  # Composite for common query
        ]
```

### 6. Use Model Validation

```python
class User(Model):
    username = CharField(max_length=100)
    email = EmailField()
    age = IntegerField(min_value=0, max_value=150)

    def clean(self):
        """Custom validation."""
        if 'admin' in self.username and not self.is_superuser:
            raise ValueError("Admin username requires superuser flag")

    async def save(self, *args, **kwargs):
        """Validation runs automatically before save."""
        self.full_clean()  # Runs field + custom validation
        await super().save(*args, **kwargs)
```

### 7. Use Transactions for Data Consistency

```python
from covet.database.orm import transaction

async with transaction():
    # Create user
    user = await User.objects.create(username='alice', email='alice@example.com')

    # Create profile
    profile = await Profile.objects.create(
        user=user,
        bio="Alice's bio"
    )

    # If any operation fails, everything rolls back
```

### 8. Enable Query Tracking in Development

```python
# settings/development.py
from covet.database.orm.n_plus_one_detector import enable_query_tracking

enable_query_tracking(warn_threshold=10, error_threshold=50)
```

### 9. Use values() for Large Datasets

```python
# ✅ GOOD: Memory efficient
user_data = await User.objects.values('id', 'username', 'email').all()

# ❌ BAD: Loads full model instances (more memory)
users = await User.objects.all()
user_data = [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]
```

### 10. Document Complex Queries

```python
class UserManager(ModelManager):
    async def get_active_power_users(self):
        """
        Get users who:
        - Are active
        - Have >100 posts
        - Have logged in within last 30 days

        Uses select_related to avoid N+1 on profile access.
        """
        from datetime import datetime, timedelta

        thirty_days_ago = datetime.now() - timedelta(days=30)

        return await self.filter(
            is_active=True,
            last_login__gte=thirty_days_ago
        ).annotate(
            post_count=Count('posts')
        ).filter(
            post_count__gt=100
        ).select_related('profile').all()
```

---

## Migration from Django ORM

### Key Differences

1. **AsyncIO-First:**
   ```python
   # Django (sync)
   users = User.objects.all()

   # CovetPy (async)
   users = await User.objects.all()
   ```

2. **Field Import Path:**
   ```python
   # Django
   from django.db import models

   # CovetPy
   from covet.database.orm import CharField, IntegerField, etc.
   ```

3. **Most APIs are 100% compatible:**
   - QuerySet methods: `filter()`, `exclude()`, `order_by()`, `limit()`, etc.
   - Relationships: `ForeignKey`, `OneToOneField`, `ManyToManyField`
   - Field lookups: `__exact`, `__gt`, `__contains`, etc.
   - Aggregation: `Count`, `Sum`, `Avg`, `Max`, `Min`

4. **Unique CovetPy Features:**
   - Built-in N+1 query detection
   - Automatic query performance tracking
   - Comprehensive query reporting

---

## Troubleshooting

### Common Issues

**Issue:** `AttributeError: 'NoneType' object has no attribute 'username'`
**Solution:** Foreign key might be NULL. Always check:
```python
if post.author:
    print(post.author.username)
else:
    print("No author")
```

**Issue:** N+1 queries detected
**Solution:** Use `select_related()` or `prefetch_related()`:
```python
# Before
posts = await Post.objects.all()
for post in posts:
    author = await post.author  # N+1!

# After
posts = await Post.objects.select_related('author').all()
for post in posts:
    author = post.author  # Cached!
```

**Issue:** "Database adapter not registered"
**Solution:** Register adapter before using ORM:
```python
from covet.database.orm import register_adapter
from covet.database.adapters.postgresql import PostgreSQLAdapter

adapter = PostgreSQLAdapter(...)
await adapter.connect()
register_adapter("default", adapter)
```

---

## Next Steps

1. **Read the Full Documentation:** [docs/ORM_REFERENCE.md](./ORM_REFERENCE.md)
2. **See Examples:** [examples/orm/](../examples/orm/)
3. **Run Tests:** `pytest tests/orm/`
4. **Join Community:** [Discord](https://discord.gg/covetpy) | [GitHub](https://github.com/covetpy/covetpy)

---

**Happy Coding! 🚀**

For issues or questions: https://github.com/covetpy/covetpy/issues
