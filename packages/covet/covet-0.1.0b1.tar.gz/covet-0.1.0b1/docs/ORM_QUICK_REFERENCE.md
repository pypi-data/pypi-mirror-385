# CovetPy ORM - Quick Reference Guide

## Installation

```bash
pip install covet

# Optional database drivers
pip install psycopg2-binary  # PostgreSQL
pip install pymysql          # MySQL
```

## Basic Setup

```python
from covet.orm import Database, Model, CharField, IntegerField, TextField, BooleanField

# Create database connection
db = Database('sqlite:///myapp.db')  # SQLite
# db = Database('postgresql://user:pass@localhost/mydb')  # PostgreSQL
# db = Database('mysql://user:pass@localhost/mydb')       # MySQL
```

## Define Models

```python
class User(Model):
    id = IntegerField(primary_key=True)
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255)
    is_active = BooleanField(default=True)

    class Meta:
        db = db
        table_name = 'users'
```

## Create Tables

```python
# Create all tables
db.create_tables([User])

# Drop tables (careful!)
db.drop_tables([User])
```

## Create Records

```python
# Method 1: Create and save
user = User(username='alice', email='alice@example.com')
user.save()

# Method 2: Create directly
user = User.objects.create(username='bob', email='bob@example.com')
```

## Query Records

```python
# Get all records
all_users = User.objects.all()

# Filter records
active_users = User.objects.filter(is_active=1)
user = User.objects.filter(username='alice').first()

# Count records
count = User.objects.count()
active_count = User.objects.filter(is_active=1).count()

# Check existence
has_users = User.objects.exists()
has_alice = User.objects.filter(username='alice').exists()

# Get first/last
first_user = User.objects.all().first()
last_user = User.objects.all().last()

# Order by
users = User.objects.order_by('username')  # ASC
users = User.objects.order_by('-id')       # DESC

# Limit/offset
first_10 = User.objects.all()[:10]
next_10 = User.objects.all()[10:20]
```

## Update Records

```python
# Update single record
user = User.objects.filter(username='alice').first()
user.email = 'newemail@example.com'
user.save()

# Bulk update
User.objects.filter(is_active=0).update(is_active=1)
```

## Delete Records

```python
# Delete single record
user = User.objects.filter(username='alice').first()
user.delete()

# Bulk delete
User.objects.filter(is_active=0).delete()
```

## Transactions

```python
# Automatic transaction management
with db.transaction():
    user1 = User(username='alice', email='alice@example.com')
    user1.save()

    user2 = User(username='bob', email='bob@example.com')
    user2.save()

    # Both saved or both rolled back on error
```

## Raw SQL

```python
# Execute query
results = db.fetch_all("SELECT * FROM users WHERE is_active = ?", (1,))

# Execute single row
user = db.fetch_one("SELECT * FROM users WHERE username = ?", ('alice',))

# Execute with commit (INSERT/UPDATE/DELETE)
db.execute_commit("UPDATE users SET is_active = 1 WHERE id = ?", (1,))
```

## Async Operations (Optional)

```python
import asyncio

async def async_example():
    # Async create
    user = await User.objects.acreate(username='charlie', email='charlie@example.com')

    # Async query
    users = await User.objects.filter(is_active=1).async_all()

    # Async save
    user.email = 'newemail@example.com'
    await user.asave()

    # Async delete
    await user.adelete()

# Run async function
asyncio.run(async_example())
```

## Field Types

```python
from covet.orm import (
    IntegerField,      # Integer
    CharField,         # String with max_length
    TextField,         # Large text
    BooleanField,      # True/False
    DateTimeField,     # Date and time
    DateField,         # Date only
    TimeField,         # Time only
    FloatField,        # Floating point
    DecimalField,      # Decimal with precision
    JSONField,         # JSON data
    BinaryField,       # Binary data
    AutoField,         # Auto-increment primary key
)

class Example(Model):
    id = AutoField()  # Primary key (auto-generated)
    name = CharField(max_length=100, null=False)
    description = TextField(blank=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Field Options

```python
field = CharField(
    max_length=100,      # Maximum length (for CharField)
    null=True,           # Allow NULL in database
    blank=True,          # Allow blank in validation
    default='value',     # Default value
    unique=True,         # Unique constraint
    primary_key=False,   # Primary key
    db_column='col_name',# Custom column name
    db_index=True,       # Create index
    choices=[('a', 'A'), ('b', 'B')],  # Choice constraint
)
```

## Relationships (Basic)

```python
from covet.orm import ForeignKey

class Author(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=100)

    class Meta:
        db = db
        table_name = 'authors'

class Book(Model):
    id = IntegerField(primary_key=True)
    title = CharField(max_length=200)
    author_id = IntegerField()  # Foreign key to Author

    class Meta:
        db = db
        table_name = 'books'

# Query with relationships
books = Book.objects.filter(author_id=1)
```

## Common Patterns

### Get or Create
```python
user, created = User.objects.get_or_create(
    username='alice',
    defaults={'email': 'alice@example.com', 'is_active': 1}
)
if created:
    print("User created")
else:
    print("User already exists")
```

### Update or Create
```python
user, created = User.objects.update_or_create(
    username='alice',
    defaults={'email': 'newemail@example.com', 'is_active': 1}
)
```

### Bulk Create
```python
users = [
    User(username='user1', email='user1@example.com'),
    User(username='user2', email='user2@example.com'),
    User(username='user3', email='user3@example.com'),
]
User.objects.bulk_create(users)
```

## Error Handling

```python
from covet.orm import DoesNotExist, MultipleObjectsReturned, IntegrityError

# Handle DoesNotExist
try:
    user = User.objects.filter(username='nonexistent').first()
    if user is None:
        print("User not found")
except DoesNotExist:
    print("User does not exist")

# Handle IntegrityError (unique constraint)
try:
    user = User(username='existing_user', email='test@example.com')
    user.save()
except IntegrityError as e:
    print(f"Integrity error: {e}")
```

## Best Practices

### 1. Use Transactions for Multiple Operations
```python
with db.transaction():
    user.save()
    post.save()
```

### 2. Close Database When Done
```python
db.close()
```

### 3. Use Context Managers (Future)
```python
with Database('sqlite:///app.db') as db:
    # Use db
    pass
# Automatically closed
```

### 4. Validate Data Before Saving
```python
user = User(username='alice', email='invalid')
try:
    user.clean()  # Validate
    user.save()
except ValidationError as e:
    print(f"Validation error: {e}")
```

### 5. Use Bulk Operations for Performance
```python
# Bad - N queries
for data in large_dataset:
    User(username=data['username']).save()

# Good - 1 query
users = [User(username=d['username']) for d in large_dataset]
User.objects.bulk_create(users)
```

## Performance Tips

1. **Use indexes** on frequently queried fields
2. **Use select_related** for foreign keys (future feature)
3. **Use prefetch_related** for many-to-many (future feature)
4. **Use bulk operations** for large datasets
5. **Use raw SQL** for complex queries
6. **Use async** for high-concurrency scenarios

## Common Issues

### Issue: "coroutine never awaited"
**Solution**: Use sync methods (default) or properly await async methods

```python
# Wrong
users = User.objects.async_all()  # Missing await

# Right (sync)
users = User.objects.all()

# Right (async)
users = await User.objects.async_all()
```

### Issue: Connection pool exhausted
**Solution**: Increase pool size or close connections

```python
db = Database('sqlite:///app.db', max_connections=20)
```

### Issue: UNIQUE constraint failed
**Solution**: Check if record already exists before saving

```python
existing = User.objects.filter(username='alice').exists()
if not existing:
    user.save()
```

## Database URLs

```python
# SQLite (local file)
Database('sqlite:///path/to/database.db')
Database('sqlite:///:memory:')  # In-memory

# PostgreSQL
Database('postgresql://user:password@localhost:5432/mydb')
Database('postgresql://user:password@localhost/mydb')

# MySQL
Database('mysql://user:password@localhost:3306/mydb')
Database('mysql://user:password@localhost/mydb')
```

## Configuration Options

```python
db = Database(
    'sqlite:///app.db',
    max_connections=10,      # Connection pool size
    timeout=30.0,            # Connection timeout (seconds)
    check_same_thread=False, # SQLite thread safety
)
```

## Next Steps

1. Read the [Full Documentation](./docs/)
2. Check out [Examples](./examples/)
3. Run the [Quick Start](./examples/orm_quickstart.py)
4. Join the [Community](#) for help

---

**Need Help?**
- GitHub Issues: [github.com/covetpy/covet/issues](https://github.com/covetpy/covet/issues)
- Documentation: [docs.covetpy.org](https://docs.covetpy.org)
- Discord: [discord.gg/covetpy](https://discord.gg/covetpy)
