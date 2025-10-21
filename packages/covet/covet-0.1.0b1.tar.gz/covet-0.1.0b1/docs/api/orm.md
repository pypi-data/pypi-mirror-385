# ORM API Reference

**Last Updated:** 2025-10-10
**Version:** 1.0.0

The CovetPy ORM provides a Django-inspired, async-first object-relational mapping system for database operations. It supports PostgreSQL, MySQL, and SQLite with a unified Python API.

## Table of Contents

- [Overview](#overview)
- [Models](#models)
- [Fields](#fields)
- [Relationships](#relationships)
- [QuerySet API](#queryset-api)
- [Q Objects](#q-objects)
- [F Expressions](#f-expressions)
- [Managers](#managers)
- [Model Methods](#model-methods)
- [Exceptions](#exceptions)
- [Best Practices](#best-practices)

## Overview

The ORM system consists of several core components:

- **Model**: Base class for database models with metaclass magic
- **Field**: Column definitions with validation and type conversion
- **QuerySet**: Lazy query builder with filtering, ordering, and aggregation
- **Manager**: Model-level database operations interface
- **Q/F**: Complex query expressions

### Why Use CovetPy ORM?

```python
# Clean, declarative model definitions
class User(Model):
    username = CharField(max_length=100, unique=True)
    email = EmailField(unique=True)
    created_at = DateTimeField(auto_now_add=True)

# Intuitive, async-first query API
user = await User.objects.filter(username='alice').first()
users = await User.objects.filter(Q(active=True) | Q(staff=True)).all()

# Django-like convenience methods
await user.save()
await user.delete()
await user.refresh_from_db()
```

## Models

### Defining Models

Models are defined by subclassing `Model` and declaring fields as class attributes. The ORM automatically creates table schemas, primary keys, and manager instances.

```python
from covet.orm import Model
from covet.orm.fields import (
    AutoField, CharField, EmailField, DateTimeField,
    BooleanField, IntegerField, TextField
)

class User(Model):
    """User model with automatic primary key."""

    # Fields (id is auto-created as AutoField)
    username = CharField(max_length=100, unique=True, null=False)
    email = EmailField(unique=True, null=False)
    first_name = CharField(max_length=50, blank=True)
    last_name = CharField(max_length=50, blank=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        table_name = 'users'  # Override default table name
        ordering = ['-created_at']  # Default ordering
        indexes = [
            ('username',),
            ('email',),
        ]
        unique_together = [('username', 'email')]

# Access model metadata
print(User._meta.table_name)  # 'users'
print(User._meta.fields.keys())  # dict_keys(['id', 'username', 'email', ...])
print(User._meta.pk_field.name)  # 'id'
```

### Model Meta Options

Configure model behavior using the `Meta` inner class:

```python
class Article(Model):
    title = CharField(max_length=200)
    slug = CharField(max_length=200, unique=True)
    content = TextField()
    published_at = DateTimeField(null=True)

    class Meta:
        table_name = 'articles'  # Database table name
        db_table = 'blog_articles'  # Alternative to table_name
        ordering = ['-published_at', 'title']  # Default order_by
        indexes = [
            ('slug',),  # Single-column index
            ('published_at', 'title'),  # Multi-column index
        ]
        unique_together = [
            ('title', 'published_at'),  # Composite unique constraint
        ]
        constraints = []  # Custom database constraints
        abstract = False  # If True, this is an abstract base class
        managed = True  # If False, ORM won't create/drop tables
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
```

**Meta Options Reference:**

| Option | Type | Description |
|--------|------|-------------|
| `table_name` | `str` | Database table name (auto-generated from model name if not provided) |
| `db_table` | `str` | Alternative to `table_name` |
| `ordering` | `List[str]` | Default ordering for queries (prefix with '-' for descending) |
| `indexes` | `List[tuple]` | Database indexes to create |
| `unique_together` | `List[tuple]` | Composite unique constraints |
| `constraints` | `List` | Custom database constraints |
| `abstract` | `bool` | If `True`, model won't create a database table |
| `managed` | `bool` | If `False`, no database table operations |
| `verbose_name` | `str` | Human-readable model name |
| `verbose_name_plural` | `str` | Plural form of verbose_name |

### Abstract Models

Create reusable base models with common fields:

```python
class TimestampedModel(Model):
    """Abstract base model with timestamp fields."""
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Won't create database table

class Article(TimestampedModel):
    """Inherits created_at and updated_at from TimestampedModel."""
    title = CharField(max_length=200)
    content = TextField()
    # Automatically has: id, created_at, updated_at

class Comment(TimestampedModel):
    """Also inherits timestamp fields."""
    article = ForeignKey(Article, on_delete='CASCADE')
    text = TextField()
    # Automatically has: id, created_at, updated_at
```

### Custom Primary Keys

Override the default auto-incrementing primary key:

```python
from covet.orm.fields import UUIDField
import uuid

class Product(Model):
    """Model with UUID primary key."""
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=200)
    sku = CharField(max_length=50, unique=True)

# Or use a custom field as primary key
class Book(Model):
    isbn = CharField(max_length=13, primary_key=True)
    title = CharField(max_length=200)
    author = CharField(max_length=100)
```

## Fields

Fields define the structure and constraints of database columns. Each field type maps to appropriate SQL types for different database engines.

### Field Options

All fields accept these common parameters:

```python
class Product(Model):
    name = CharField(
        max_length=200,           # Field-specific options
        primary_key=False,        # Is this the primary key?
        unique=False,             # Must values be unique?
        null=True,                # Allow NULL in database?
        blank=True,               # Allow empty string in validation?
        default=None,             # Default value (can be callable)
        validators=[],            # List of validation functions
        db_column='product_name', # Override database column name
        db_index=False,           # Create database index?
        help_text='Product name', # Documentation
        verbose_name='Name',      # Human-readable name
        choices=[                 # Limit to specific values
            ('new', 'New'),
            ('used', 'Used'),
        ]
    )
```

**Common Field Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `primary_key` | `bool` | `False` | Is this the primary key? |
| `unique` | `bool` | `False` | Must all values be unique? |
| `null` | `bool` | `True` | Allow `NULL` in database? |
| `blank` | `bool` | `True` | Allow empty string in validation? |
| `default` | `Any` | `None` | Default value (can be callable) |
| `validators` | `List[Callable]` | `[]` | Custom validation functions |
| `db_column` | `str` | `None` | Override database column name |
| `db_index` | `bool` | `False` | Create a database index? |
| `help_text` | `str` | `""` | Help text for documentation |
| `verbose_name` | `str` | `""` | Human-readable field name |
| `choices` | `List[tuple]` | `None` | Limit to specific values |

### String Fields

#### CharField

Variable-length string with maximum length.

```python
from covet.orm.fields import CharField

class User(Model):
    username = CharField(max_length=100, unique=True, null=False)
    first_name = CharField(max_length=50, blank=True, default='')

    # With choices
    status = CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('banned', 'Banned'),
        ],
        default='active'
    )

# Usage
user = User(username='alice', first_name='Alice')
await user.save()

# Validation error if too long
user.username = 'a' * 101  # Raises ValidationError on save
```

**SQL Mapping:**
- PostgreSQL: `VARCHAR(max_length)`
- MySQL: `VARCHAR(max_length)`
- SQLite: `TEXT`

#### TextField

Large text field for long content (no length limit).

```python
from covet.orm.fields import TextField

class Article(Model):
    title = CharField(max_length=200)
    content = TextField()  # Unlimited length
    summary = TextField(blank=True, default='')

# Usage
article = Article(
    title='My Article',
    content='Very long article content...' * 1000
)
await article.save()
```

**SQL Mapping:**
- PostgreSQL: `TEXT`
- MySQL: `LONGTEXT`
- SQLite: `TEXT`

#### EmailField

Email address with validation.

```python
from covet.orm.fields import EmailField

class User(Model):
    email = EmailField(unique=True, null=False)
    backup_email = EmailField(blank=True, null=True)

# Usage
user = User(email='alice@example.com')
await user.save()

# Validation
user.email = 'invalid-email'  # Raises ValidationError
```

#### URLField

URL with validation.

```python
from covet.orm.fields import URLField

class Website(Model):
    name = CharField(max_length=100)
    url = URLField()
    favicon = URLField(blank=True, null=True)

# Usage
site = Website(name='Example', url='https://example.com')
await site.save()
```

### Numeric Fields

#### IntegerField

Standard 32-bit integer.

```python
from covet.orm.fields import IntegerField

class Product(Model):
    quantity = IntegerField(default=0)
    min_quantity = IntegerField(default=10)
    max_quantity = IntegerField(default=1000)

    # With validators
    rating = IntegerField(
        validators=[
            lambda v: v >= 1 and v <= 5 or ValueError('Rating must be 1-5')
        ]
    )

# Usage
product = Product(quantity=100, rating=4)
await product.save()

# Type conversion
product.quantity = "50"  # Automatically converted to int
```

**SQL Mapping:**
- PostgreSQL: `INTEGER`
- MySQL: `INT`
- SQLite: `INTEGER`

#### BigIntegerField

64-bit integer for large numbers.

```python
from covet.orm.fields import BigIntegerField

class Analytics(Model):
    page_views = BigIntegerField(default=0)
    total_bytes = BigIntegerField(default=0)

# Usage
analytics = Analytics(page_views=9999999999999)
await analytics.save()
```

**SQL Mapping:**
- PostgreSQL: `BIGINT`
- MySQL: `BIGINT`
- SQLite: `INTEGER`

#### FloatField

Floating-point number.

```python
from covet.orm.fields import FloatField

class Measurement(Model):
    temperature = FloatField()
    humidity = FloatField(default=0.0)
    pressure = FloatField(null=True)

# Usage
measurement = Measurement(temperature=23.5, humidity=65.2)
await measurement.save()
```

**SQL Mapping:**
- PostgreSQL: `REAL`
- MySQL: `FLOAT`
- SQLite: `REAL`

#### DecimalField

Fixed-precision decimal for monetary values.

```python
from covet.orm.fields import DecimalField

class Product(Model):
    name = CharField(max_length=200)
    price = DecimalField(max_digits=10, decimal_places=2)
    tax_rate = DecimalField(max_digits=5, decimal_places=4, default=0.0)

# Usage
product = Product(name='Widget', price=19.99, tax_rate=0.0825)
await product.save()

# Precise decimal arithmetic
from decimal import Decimal
product.price = Decimal('19.99')
```

**Parameters:**
- `max_digits`: Total number of digits (default: 10)
- `decimal_places`: Number of decimal places (default: 2)

**SQL Mapping:**
- PostgreSQL: `DECIMAL(max_digits, decimal_places)`
- MySQL: `DECIMAL(max_digits, decimal_places)`
- SQLite: `REAL`

### Boolean Fields

#### BooleanField

True/False values.

```python
from covet.orm.fields import BooleanField

class User(Model):
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    email_verified = BooleanField(default=False)

# Usage
user = User(is_active=True, is_staff=False)
await user.save()

# Flexible input types
user.is_active = 1     # Converted to True
user.is_active = "0"   # Converted to False
user.is_active = "yes" # Converted to True
```

**SQL Mapping:**
- PostgreSQL: `BOOLEAN`
- MySQL: `TINYINT(1)`
- SQLite: `INTEGER` (0 or 1)

### Date and Time Fields

#### DateTimeField

Date and time.

```python
from covet.orm.fields import DateTimeField
from datetime import datetime

class Article(Model):
    created_at = DateTimeField(auto_now_add=True)  # Set on creation
    updated_at = DateTimeField(auto_now=True)      # Updated on save
    published_at = DateTimeField(null=True)        # Manually set

# Usage
article = Article()
await article.save()
# article.created_at is set automatically
# article.updated_at is set automatically

# Manual setting
article.published_at = datetime.now()
await article.save()
```

**Parameters:**
- `auto_now`: Set to current time on every save
- `auto_now_add`: Set to current time on creation only

**SQL Mapping:**
- PostgreSQL: `TIMESTAMP`
- MySQL: `DATETIME`
- SQLite: `TEXT` (ISO format)

#### DateField

Date without time.

```python
from covet.orm.fields import DateField
from datetime import date

class Event(Model):
    name = CharField(max_length=200)
    start_date = DateField()
    end_date = DateField()

# Usage
event = Event(
    name='Conference',
    start_date=date(2025, 10, 15),
    end_date=date(2025, 10, 17)
)
await event.save()
```

**SQL Mapping:**
- PostgreSQL: `DATE`
- MySQL: `DATE`
- SQLite: `TEXT` (ISO format)

#### TimeField

Time without date.

```python
from covet.orm.fields import TimeField
from datetime import time

class Schedule(Model):
    name = CharField(max_length=100)
    start_time = TimeField()
    end_time = TimeField()

# Usage
schedule = Schedule(
    name='Office Hours',
    start_time=time(9, 0),    # 09:00
    end_time=time(17, 30)     # 17:30
)
await schedule.save()
```

**SQL Mapping:**
- PostgreSQL: `TIME`
- MySQL: `TIME`
- SQLite: `TEXT` (ISO format)

### Special Fields

#### JSONField

Store JSON data.

```python
from covet.orm.fields import JSONField

class User(Model):
    username = CharField(max_length=100)
    preferences = JSONField(default=dict)
    metadata = JSONField(null=True)

# Usage
user = User(
    username='alice',
    preferences={
        'theme': 'dark',
        'language': 'en',
        'notifications': True
    }
)
await user.save()

# Access JSON data
print(user.preferences['theme'])  # 'dark'
user.preferences['theme'] = 'light'
await user.save()
```

**SQL Mapping:**
- PostgreSQL: `JSONB` (binary JSON with indexing)
- MySQL: `JSON`
- SQLite: `TEXT` (JSON string)

#### BinaryField

Binary data storage.

```python
from covet.orm.fields import BinaryField

class Document(Model):
    name = CharField(max_length=200)
    content = BinaryField()  # PDF, image, etc.

# Usage
with open('document.pdf', 'rb') as f:
    doc = Document(name='Report', content=f.read())
    await doc.save()

# Read binary data
binary_data = doc.content
```

**SQL Mapping:**
- PostgreSQL: `BYTEA`
- MySQL: `LONGBLOB`
- SQLite: `BLOB`

#### UUIDField

UUID/GUID storage.

```python
from covet.orm.fields import UUIDField
import uuid

class Session(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKey(User, on_delete='CASCADE')
    token = UUIDField(default=uuid.uuid4, unique=True)

# Usage
session = Session(user=user)
await session.save()
# session.id and session.token are automatically generated UUIDs

print(session.id)  # UUID('123e4567-e89b-12d3-a456-426614174000')
```

**SQL Mapping:**
- PostgreSQL: `UUID`
- MySQL: `CHAR(36)`
- SQLite: `TEXT`

#### AutoField / BigAutoField

Auto-incrementing primary key (automatically added if no primary key is defined).

```python
from covet.orm.fields import AutoField, BigAutoField

class User(Model):
    # No need to define id field - automatically added as AutoField
    username = CharField(max_length=100)

# Or explicitly define
class Product(Model):
    id = BigAutoField(primary_key=True)  # Use 64-bit integers
    name = CharField(max_length=200)
```

**SQL Mapping (AutoField):**
- PostgreSQL: `SERIAL PRIMARY KEY`
- MySQL: `INT AUTO_INCREMENT PRIMARY KEY`
- SQLite: `INTEGER PRIMARY KEY AUTOINCREMENT`

**SQL Mapping (BigAutoField):**
- PostgreSQL: `BIGSERIAL PRIMARY KEY`
- MySQL: `BIGINT AUTO_INCREMENT PRIMARY KEY`
- SQLite: `INTEGER PRIMARY KEY AUTOINCREMENT`

## Relationships

Define relationships between models using relationship fields.

### ForeignKey (Many-to-One)

Each instance references one instance of another model.

```python
from covet.orm.fields import ForeignKey

class Author(Model):
    name = CharField(max_length=100)
    email = EmailField()

class Book(Model):
    title = CharField(max_length=200)
    author = ForeignKey(
        Author,
        on_delete='CASCADE',      # What to do when author is deleted
        related_name='books',     # Access books from author
        db_column='author_id'     # Database column name
    )

# Usage - Creating related objects
author = Author(name='Alice', email='alice@example.com')
await author.save()

book = Book(title='Python Guide', author=author)
await book.save()

# Or with author_id directly
book = Book(title='Python Guide', author_id=author.id)
await book.save()

# Access related object
print(book.author.name)  # 'Alice'

# Reverse access using related_name
author_books = await author.books.all()
for book in author_books:
    print(book.title)
```

**on_delete Options:**

| Option | Behavior |
|--------|----------|
| `'CASCADE'` | Delete related objects when parent is deleted |
| `'SET_NULL'` | Set foreign key to NULL (requires `null=True`) |
| `'SET_DEFAULT'` | Set foreign key to its default value |
| `'PROTECT'` | Prevent deletion if related objects exist |
| `'DO_NOTHING'` | No action (may cause database integrity errors) |

**String References:**

Reference models before they're defined using strings:

```python
class Comment(Model):
    text = TextField()
    article = ForeignKey('Article', on_delete='CASCADE')  # String reference

class Article(Model):
    title = CharField(max_length=200)
    content = TextField()
```

### OneToMany (Reverse ForeignKey)

Automatically created on the reverse side of a ForeignKey.

```python
class Author(Model):
    name = CharField(max_length=100)

class Book(Model):
    title = CharField(max_length=200)
    author = ForeignKey(Author, related_name='books', on_delete='CASCADE')

# OneToMany is accessed via related_name
author = await Author.objects.get(id=1)
books = await author.books.all()           # Get all books
recent_books = await author.books.filter(  # Filter books
    published_at__gte=datetime(2024, 1, 1)
).all()
```

### ManyToMany

Each instance can reference multiple instances, and vice versa.

```python
from covet.orm.fields import ManyToManyField

class Tag(Model):
    name = CharField(max_length=50, unique=True)

class Article(Model):
    title = CharField(max_length=200)
    tags = ManyToManyField(
        Tag,
        related_name='articles',    # Access articles from tag
        through='article_tags'       # Custom junction table name
    )

# Usage - Adding relationships
article = await Article.objects.create(title='Python Tips')
tag1 = await Tag.objects.create(name='python')
tag2 = await Tag.objects.create(name='tutorial')

await article.tags.add(tag1, tag2)

# Access related objects
tags = await article.tags.all()
for tag in tags:
    print(tag.name)

# Reverse access
tag = await Tag.objects.get(name='python')
articles = await tag.articles.all()

# Remove relationships
await article.tags.remove(tag1)

# Clear all relationships
await article.tags.clear()
```

### OneToOne

One-to-one relationship between models.

```python
from covet.orm.fields import OneToOneField

class User(Model):
    username = CharField(max_length=100)
    email = EmailField()

class Profile(Model):
    user = OneToOneField(
        User,
        on_delete='CASCADE',
        related_name='profile'
    )
    bio = TextField(blank=True)
    avatar = URLField(blank=True)
    birth_date = DateField(null=True)

# Usage
user = await User.objects.create(username='alice', email='alice@example.com')
profile = await Profile.objects.create(
    user=user,
    bio='Software developer'
)

# Access from both sides
print(profile.user.username)  # 'alice'
print(user.profile.bio)       # 'Software developer'
```

## QuerySet API

QuerySets provide a fluent interface for database queries. They are lazy - queries aren't executed until you request data.

### Creating QuerySets

```python
# Get the manager (automatic for all models)
User.objects  # Manager instance

# All() returns a QuerySet
queryset = User.objects.all()  # No query executed yet

# QuerySet methods return new QuerySets (chainable)
active_users = User.objects.filter(is_active=True).order_by('-created_at')
```

### Retrieving Objects

#### all()

Get all instances.

```python
# Async
users = await User.objects.all()
for user in users:
    print(user.username)

# Sync (if supported)
users = User.objects.all()
```

#### filter(**kwargs)

Filter instances by field values.

```python
# Simple equality
active_users = await User.objects.filter(is_active=True).all()

# Multiple conditions (AND)
staff_users = await User.objects.filter(is_active=True, is_staff=True).all()

# Field lookups
users = await User.objects.filter(username__startswith='a').all()
users = await User.objects.filter(created_at__gte=datetime(2024, 1, 1)).all()
```

**Field Lookups:**

| Lookup | Description | Example |
|--------|-------------|---------|
| `exact` | Exact match (default) | `username__exact='alice'` |
| `iexact` | Case-insensitive exact | `username__iexact='ALICE'` |
| `contains` | Case-sensitive containment | `title__contains='Python'` |
| `icontains` | Case-insensitive containment | `title__icontains='python'` |
| `in` | In a list | `id__in=[1, 2, 3]` |
| `gt` | Greater than | `age__gt=18` |
| `gte` | Greater than or equal | `price__gte=10.00` |
| `lt` | Less than | `quantity__lt=100` |
| `lte` | Less than or equal | `quantity__lte=50` |
| `startswith` | Starts with | `email__startswith='admin'` |
| `istartswith` | Case-insensitive starts with | `email__istartswith='ADMIN'` |
| `endswith` | Ends with | `domain__endswith='.com'` |
| `iendswith` | Case-insensitive ends with | `domain__iendswith='.COM'` |
| `range` | Between two values | `date__range=(start, end)` |
| `isnull` | Is NULL | `deleted_at__isnull=True` |
| `regex` | Regex match | `code__regex=r'^[A-Z]{3}$'` |
| `iregex` | Case-insensitive regex | `code__iregex=r'^[a-z]{3}$'` |

```python
# Field lookup examples
users = await User.objects.filter(username__icontains='john').all()
products = await Product.objects.filter(price__gte=10, price__lte=100).all()
articles = await Article.objects.filter(title__startswith='How to').all()
orders = await Order.objects.filter(status__in=['pending', 'processing']).all()
```

#### exclude(**kwargs)

Exclude instances matching criteria.

```python
# Get non-staff users
users = await User.objects.exclude(is_staff=True).all()

# Combine filter and exclude
active_non_staff = await User.objects.filter(
    is_active=True
).exclude(
    is_staff=True
).all()
```

#### get(**kwargs)

Get a single instance (raises exception if not found or multiple found).

```python
# Get by primary key
user = await User.objects.get(id=1)

# Get by unique field
user = await User.objects.get(username='alice')
user = await User.objects.get(email='alice@example.com')

# Raises DoesNotExist if not found
try:
    user = await User.objects.get(username='nonexistent')
except User.DoesNotExist:
    print('User not found')

# Raises MultipleObjectsReturned if multiple found
try:
    user = await User.objects.get(is_active=True)  # Multiple active users
except User.MultipleObjectsReturned:
    print('Multiple users found')
```

#### first() / last()

Get the first or last instance.

```python
# First instance (respects ordering)
first_user = await User.objects.order_by('created_at').first()

# Last instance
last_user = await User.objects.order_by('created_at').last()

# Returns None if no instances
user = await User.objects.filter(username='nonexistent').first()
if user is None:
    print('No user found')
```

#### count()

Count instances without fetching them.

```python
# Total users
total = await User.objects.count()

# Filtered count
active_count = await User.objects.filter(is_active=True).count()

# Efficient for existence checks
has_users = await User.objects.count() > 0
```

#### exists()

Check if any instances exist (more efficient than count).

```python
# Check existence
has_users = await User.objects.exists()
has_staff = await User.objects.filter(is_staff=True).exists()

# Use in conditionals
if await User.objects.filter(username='alice').exists():
    print('Username taken')
```

### Ordering

#### order_by(*fields)

Order results by fields.

```python
# Ascending order
users = await User.objects.order_by('username').all()

# Descending order (prefix with -)
users = await User.objects.order_by('-created_at').all()

# Multiple fields
users = await User.objects.order_by('-is_staff', 'username').all()

# Clear previous ordering
users = await User.objects.order_by('-created_at').order_by().all()
```

#### reverse()

Reverse the ordering.

```python
# Newest first, then reverse to oldest first
users = await User.objects.order_by('-created_at').reverse().all()
```

### Limiting Results

#### Slicing

Use Python slice syntax to limit results.

```python
# First 10 users
users = await User.objects.all()[:10]

# Users 10-20
users = await User.objects.all()[10:20]

# Every other user
users = await User.objects.all()[::2]

# Last 5 users (with ordering)
users = await User.objects.order_by('-created_at')[:5]
```

#### limit(n) / offset(n)

Explicit limit and offset.

```python
# First 10 users
users = await User.objects.limit(10).all()

# Skip first 20, get next 10
users = await User.objects.offset(20).limit(10).all()

# Pagination
page = 2
page_size = 20
users = await User.objects.offset((page - 1) * page_size).limit(page_size).all()
```

### Selecting Fields

#### only(*fields)

Select only specific fields (deferred loading).

```python
# Only load id and username
users = await User.objects.only('id', 'username').all()
for user in users:
    print(user.username)  # Loaded
    print(user.email)     # Triggers additional query
```

#### defer(*fields)

Defer loading of specific fields.

```python
# Load everything except bio
users = await User.objects.defer('bio').all()
for user in users:
    print(user.username)  # Loaded
    print(user.bio)       # Triggers additional query
```

#### values(*fields)

Return dictionaries instead of model instances.

```python
# Return dicts with specific fields
users = await User.objects.values('id', 'username').all()
for user in users:
    print(user)  # {'id': 1, 'username': 'alice'}

# All fields
users = await User.objects.values().all()
```

#### values_list(*fields, flat=False)

Return tuples instead of model instances.

```python
# Return tuples
users = await User.objects.values_list('id', 'username').all()
for user_id, username in users:
    print(f'{user_id}: {username}')

# Single field with flat=True
usernames = await User.objects.values_list('username', flat=True).all()
print(usernames)  # ['alice', 'bob', 'charlie']
```

### Aggregation

#### aggregate(**kwargs)

Compute aggregate values.

```python
from covet.orm.aggregates import Count, Sum, Avg, Min, Max

# Count all users
result = await User.objects.aggregate(total=Count('id'))
print(result['total'])  # {'total': 150}

# Average, min, max
result = await Product.objects.aggregate(
    avg_price=Avg('price'),
    min_price=Min('price'),
    max_price=Max('price'),
    total_quantity=Sum('quantity')
)
print(result)
# {'avg_price': 25.50, 'min_price': 5.00, 'max_price': 99.99, 'total_quantity': 1500}
```

#### annotate(**kwargs)

Add aggregated fields to each instance.

```python
from covet.orm.aggregates import Count

# Add book count to each author
authors = await Author.objects.annotate(
    book_count=Count('books')
).all()

for author in authors:
    print(f'{author.name}: {author.book_count} books')

# Filter by annotated field
popular_authors = await Author.objects.annotate(
    book_count=Count('books')
).filter(
    book_count__gte=5
).all()
```

### Distinct Values

#### distinct(*fields)

Remove duplicate rows.

```python
# Distinct usernames
usernames = await User.objects.values('username').distinct().all()

# Distinct with specific fields (PostgreSQL)
users = await User.objects.distinct('last_name').all()
```

### Creating and Updating

#### create(**kwargs)

Create and save a new instance.

```python
# Create user
user = await User.objects.create(
    username='alice',
    email='alice@example.com',
    is_active=True
)
print(user.id)  # Automatically assigned

# Shorthand for:
user = User(username='alice', email='alice@example.com')
await user.save()
```

#### get_or_create(**kwargs)

Get existing instance or create new one.

```python
# Returns (instance, created)
user, created = await User.objects.get_or_create(
    username='alice',
    defaults={'email': 'alice@example.com', 'is_active': True}
)

if created:
    print('Created new user')
else:
    print('User already exists')
```

#### update_or_create(**kwargs)

Update existing instance or create new one.

```python
# Returns (instance, created)
user, created = await User.objects.update_or_create(
    username='alice',
    defaults={'email': 'newemail@example.com', 'is_active': True}
)
```

#### update(**kwargs)

Update multiple instances.

```python
# Update all matching instances
updated = await User.objects.filter(is_active=False).update(is_active=True)
print(f'Updated {updated} users')

# Update with expressions
from covet.orm import F
await Product.objects.filter(quantity__lt=10).update(
    quantity=F('quantity') + 100
)
```

#### bulk_create(instances, batch_size=None)

Create multiple instances efficiently.

```python
# Create 100 users in one query
users = [
    User(username=f'user{i}', email=f'user{i}@example.com')
    for i in range(100)
]
created_users = await User.objects.bulk_create(users)

# With batch size
await User.objects.bulk_create(users, batch_size=50)  # 2 queries
```

### Deleting

#### delete()

Delete instances matching query.

```python
# Delete specific instances
deleted = await User.objects.filter(is_active=False).delete()
print(f'Deleted {deleted} users')

# Delete all (be careful!)
await User.objects.all().delete()

# Delete single instance
user = await User.objects.get(id=1)
await user.delete()
```

### Related Objects

#### select_related(*fields)

Perform SQL JOINs to fetch related objects in the same query (for ForeignKey and OneToOne).

```python
# Without select_related (N+1 queries problem)
books = await Book.objects.all()
for book in books:
    print(book.author.name)  # Separate query for each book

# With select_related (1 query with JOIN)
books = await Book.objects.select_related('author').all()
for book in books:
    print(book.author.name)  # No additional query

# Multiple relations
comments = await Comment.objects.select_related('article', 'user').all()

# Nested relations
comments = await Comment.objects.select_related('article__author').all()
```

#### prefetch_related(*lookups)

Fetch related objects in separate queries (for ManyToMany and reverse ForeignKey).

```python
# Without prefetch_related (N+1 queries)
articles = await Article.objects.all()
for article in articles:
    tags = await article.tags.all()  # Separate query for each article

# With prefetch_related (2 queries total)
articles = await Article.objects.prefetch_related('tags').all()
for article in articles:
    tags = await article.tags.all()  # No query, uses cached data

# Multiple relations
authors = await Author.objects.prefetch_related('books', 'articles').all()

# Nested prefetch
authors = await Author.objects.prefetch_related('books__publisher').all()
```

### Raw SQL

#### raw(sql, params=None)

Execute raw SQL and return model instances.

```python
# Raw SQL query
users = await User.objects.raw(
    'SELECT * FROM users WHERE created_at > %s',
    [datetime(2024, 1, 1)]
)

for user in users:
    print(user.username)
```

## Q Objects

Q objects enable complex queries with AND, OR, and NOT logic.

### Basic Usage

```python
from covet.orm import Q

# OR condition
users = await User.objects.filter(
    Q(is_staff=True) | Q(is_superuser=True)
).all()

# AND condition (same as multiple kwargs)
users = await User.objects.filter(
    Q(is_active=True) & Q(is_staff=True)
).all()

# NOT condition
users = await User.objects.filter(
    ~Q(is_staff=True)
).all()
```

### Complex Queries

```python
# (staff OR superuser) AND active
users = await User.objects.filter(
    (Q(is_staff=True) | Q(is_superuser=True)) & Q(is_active=True)
).all()

# NOT (inactive OR banned)
users = await User.objects.filter(
    ~(Q(is_active=False) | Q(status='banned'))
).all()

# Multiple conditions
articles = await Article.objects.filter(
    Q(title__icontains='python') | Q(tags__name='python'),
    Q(published_at__isnull=False),
    ~Q(status='draft')
).all()
```

### Combining Q Objects

```python
# Build queries dynamically
query = Q()

if search_term:
    query |= Q(title__icontains=search_term)
    query |= Q(content__icontains=search_term)

if category:
    query &= Q(category=category)

if is_published:
    query &= Q(published_at__isnull=False)

articles = await Article.objects.filter(query).all()
```

## F Expressions

F expressions reference model field values in database queries.

### Field References

```python
from covet.orm import F

# Find products where quantity is less than minimum
products = await Product.objects.filter(quantity__lt=F('min_quantity')).all()

# Compare two fields
articles = await Article.objects.filter(
    updated_at__gt=F('created_at')
).all()
```

### Arithmetic Operations

```python
# Increase prices by 10%
await Product.objects.update(price=F('price') * 1.1)

# Decrease quantity
await Product.objects.filter(id=1).update(quantity=F('quantity') - 1)

# Combined operations
await Product.objects.update(
    total_price=F('quantity') * F('unit_price')
)
```

### Annotations

```python
# Add calculated field
products = await Product.objects.annotate(
    total_value=F('quantity') * F('price')
).all()

for product in products:
    print(f'{product.name}: ${product.total_value}')

# Filter by calculated field
expensive_inventory = await Product.objects.annotate(
    total_value=F('quantity') * F('price')
).filter(
    total_value__gte=10000
).all()
```

## Managers

Managers provide the interface for database queries on models.

### Default Manager

```python
# Every model automatically gets a default manager called 'objects'
users = await User.objects.all()
```

### Custom Managers

```python
from covet.orm import Manager

class ActiveManager(Manager):
    """Manager that returns only active users."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class User(Model):
    username = CharField(max_length=100)
    is_active = BooleanField(default=True)

    objects = Manager()        # Default manager
    active = ActiveManager()   # Custom manager

# Usage
all_users = await User.objects.all()         # All users
active_users = await User.active.all()       # Only active users
```

### Custom Manager Methods

```python
class UserManager(Manager):
    async def create_user(self, username, email, password):
        """Create a user with hashed password."""
        from covet.security import PasswordHasher

        hasher = PasswordHasher()
        hashed_password = hasher.hash_password(password)

        return await self.create(
            username=username,
            email=email,
            password=hashed_password,
            is_active=True
        )

    async def get_by_email(self, email):
        """Get user by email."""
        return await self.get(email=email)

class User(Model):
    username = CharField(max_length=100)
    email = EmailField(unique=True)
    password = CharField(max_length=255)
    is_active = BooleanField(default=True)

    objects = UserManager()

# Usage
user = await User.objects.create_user(
    username='alice',
    email='alice@example.com',
    password='secret123'
)

user = await User.objects.get_by_email('alice@example.com')
```

## Model Methods

### Instance Methods

```python
class User(Model):
    username = CharField(max_length=100)
    email = EmailField()
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)

    def get_full_name(self):
        """Return full name."""
        return f'{self.first_name} {self.last_name}'.strip()

    async def send_email(self, subject, message):
        """Send email to user."""
        # Email sending logic
        pass

    def __str__(self):
        return self.username

# Usage
user = await User.objects.get(username='alice')
print(user.get_full_name())
await user.send_email('Welcome', 'Welcome to our site!')
```

### save()

Save instance to database.

```python
# Create new instance
user = User(username='alice', email='alice@example.com')
await user.save()  # INSERT

# Update existing instance
user.email = 'newemail@example.com'
await user.save()  # UPDATE

# Force insert
await user.save(force_insert=True)

# Force update
await user.save(force_update=True)

# Skip validation
await user.save(validate=False)
```

### delete()

Delete instance from database.

```python
user = await User.objects.get(username='alice')
await user.delete()
```

### refresh_from_db()

Reload instance from database.

```python
user = await User.objects.get(id=1)
user.username = 'modified'

# Discard changes and reload
await user.refresh_from_db()
print(user.username)  # Original value

# Refresh specific fields
await user.refresh_from_db(fields=['email', 'username'])
```

### clean()

Validate model instance.

```python
class User(Model):
    username = CharField(max_length=100)
    email = EmailField()

    def clean(self):
        """Custom validation."""
        super().clean()

        if self.username and len(self.username) < 3:
            from covet.orm.exceptions import ValidationError
            raise ValidationError({'username': 'Username must be at least 3 characters'})

# Usage
user = User(username='ab', email='test@example.com')
try:
    user.clean()
except ValidationError as e:
    print(e.errors)  # {'username': 'Username must be at least 3 characters'}
```

### to_dict() / from_dict()

Convert between model instances and dictionaries.

```python
user = await User.objects.get(username='alice')

# To dictionary
data = user.to_dict()
print(data)  # {'id': 1, 'username': 'alice', 'email': 'alice@example.com', ...}

# Specific fields only
data = user.to_dict(fields=['username', 'email'])

# From dictionary
new_user = User.from_dict({
    'username': 'bob',
    'email': 'bob@example.com'
})
await new_user.save()
```

## Exceptions

### DoesNotExist

Raised when get() finds no matching instance.

```python
from covet.orm.exceptions import DoesNotExist

try:
    user = await User.objects.get(username='nonexistent')
except User.DoesNotExist:
    print('User not found')

# Or catch generic exception
except DoesNotExist:
    print('Object not found')
```

### MultipleObjectsReturned

Raised when get() finds multiple instances.

```python
from covet.orm.exceptions import MultipleObjectsReturned

try:
    user = await User.objects.get(is_active=True)
except MultipleObjectsReturned:
    print('Multiple users found, use filter() instead')
```

### ValidationError

Raised when validation fails.

```python
from covet.orm.exceptions import ValidationError

user = User(username='ab')  # Too short
try:
    await user.save()
except ValidationError as e:
    print(e.errors)  # Dictionary of field errors
```

### IntegrityError

Raised when database constraints are violated.

```python
from covet.orm.exceptions import IntegrityError

try:
    # Duplicate username
    user = await User.objects.create(username='alice')
except IntegrityError as e:
    print('Constraint violation:', e)
```

## Best Practices

### 1. Use select_related and prefetch_related

Avoid N+1 query problems:

```python
# BAD: N+1 queries
books = await Book.objects.all()
for book in books:
    print(book.author.name)  # Extra query per book

# GOOD: 1 query with JOIN
books = await Book.objects.select_related('author').all()
for book in books:
    print(book.author.name)  # No extra query
```

### 2. Use only() and defer() for large models

```python
# Load only required fields
users = await User.objects.only('id', 'username').all()

# Defer large fields
articles = await Article.objects.defer('content').all()
```

### 3. Use bulk_create() for batch inserts

```python
# BAD: Multiple queries
for i in range(1000):
    await User.objects.create(username=f'user{i}')

# GOOD: One query
users = [User(username=f'user{i}') for i in range(1000)]
await User.objects.bulk_create(users)
```

### 4. Use Q objects for complex queries

```python
# Clear and maintainable
users = await User.objects.filter(
    (Q(is_staff=True) | Q(is_superuser=True)) & Q(is_active=True)
).all()
```

### 5. Use F expressions for field updates

```python
# BAD: Race condition
product = await Product.objects.get(id=1)
product.quantity -= 1
await product.save()

# GOOD: Atomic update
await Product.objects.filter(id=1).update(quantity=F('quantity') - 1)
```

### 6. Use transactions for related operations

```python
from covet.orm import transaction

async with transaction():
    user = await User.objects.create(username='alice')
    await Profile.objects.create(user=user, bio='Developer')
    # Automatically rolled back on exception
```

### 7. Index frequently queried fields

```python
class User(Model):
    username = CharField(max_length=100, unique=True, db_index=True)
    email = EmailField(unique=True, db_index=True)

    class Meta:
        indexes = [
            ('created_at',),
            ('username', 'email'),  # Composite index
        ]
```

### 8. Use custom managers for common queries

```python
class PublishedManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            published_at__isnull=False,
            published_at__lte=datetime.now()
        )

class Article(Model):
    title = CharField(max_length=200)
    published_at = DateTimeField(null=True)

    objects = Manager()
    published = PublishedManager()

# Clean, reusable
articles = await Article.published.all()
```

### 9. Validate in models, not views

```python
class User(Model):
    username = CharField(max_length=100)

    def clean(self):
        super().clean()
        if len(self.username) < 3:
            raise ValidationError('Username too short')

# Validation happens automatically on save
user = User(username='ab')
await user.save()  # Raises ValidationError
```

### 10. Use abstract models for common fields

```python
class TimestampedModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Article(TimestampedModel):
    title = CharField(max_length=200)
    # Inherits created_at and updated_at

class Comment(TimestampedModel):
    text = TextField()
    # Also inherits timestamp fields
```

---

**Next Steps:**
- [Query Builder API](./query-builder.md) - Advanced query construction
- [Migrations](./migrations.md) - Database schema management
- [Database Configuration](./database.md) - Connection and settings
- [ORM Tutorial](../tutorials/02-orm-guide.md) - Complete ORM guide

**Performance Tips:**
- Use `select_related()` and `prefetch_related()` to avoid N+1 queries
- Use `only()` and `defer()` to load only necessary fields
- Use `bulk_create()` for batch inserts
- Use database indexes on frequently queried fields
- Use F expressions for atomic field updates

**Related Documentation:**
- [Database Backends](./database.md)
- [Query Optimization](../performance.md#query-optimization)
- [Security Best Practices](../security-guide.md)
