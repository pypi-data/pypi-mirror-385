# CovetPy ORM - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install asyncpg aiomysql aiosqlite
```

### Step 2: Create Database Adapter

```python
from covet.database.adapters.postgresql import PostgreSQLAdapter
from covet.database.orm import register_adapter

# Create adapter
adapter = PostgreSQLAdapter(
    host='localhost',
    port=5432,
    database='myapp',
    user='postgres',
    password='password'
)

# Connect and register
await adapter.connect()
await register_adapter('default', adapter, make_default=True)
```

### Step 3: Define Models

```python
from covet.database.orm import Model, CharField, EmailField, DateTimeField

class User(Model):
    username = CharField(max_length=100, unique=True)
    email = EmailField(unique=True)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
```

### Step 4: Use the ORM

```python
# Create
user = await User.objects.create(
    username='alice',
    email='alice@example.com'
)

# Read
user = await User.objects.get(id=1)
users = await User.objects.filter(username__startswith='a').all()

# Update
user.email = 'newemail@example.com'
await user.save()

# Delete
await user.delete()
```

## 📚 Common Operations

### Querying

```python
# Get single record
user = await User.objects.get(id=1)

# Filter with lookups
users = await User.objects.filter(
    email__icontains='example.com',
    is_active=True
).all()

# Exclude
users = await User.objects.exclude(username='admin').all()

# Ordering
users = await User.objects.order_by('-created_at').all()

# Pagination
page = await User.objects.limit(10).offset(20).all()

# Count
count = await User.objects.filter(is_active=True).count()

# Check existence
exists = await User.objects.filter(email='test@example.com').exists()
```

### Field Lookups

```python
# Exact match
users = await User.objects.filter(username='alice').all()
users = await User.objects.filter(username__exact='alice').all()

# Case-insensitive
users = await User.objects.filter(username__iexact='ALICE').all()

# Contains
users = await User.objects.filter(email__contains='example').all()

# Case-insensitive contains
users = await User.objects.filter(email__icontains='EXAMPLE').all()

# Starts/ends with
users = await User.objects.filter(username__startswith='a').all()
users = await User.objects.filter(email__endswith='.com').all()

# Comparisons
users = await User.objects.filter(age__gte=18).all()  # >=
users = await User.objects.filter(age__lt=65).all()   # <

# In list
users = await User.objects.filter(id__in=[1, 2, 3]).all()

# NULL check
users = await User.objects.filter(deleted_at__isnull=True).all()
```

### Bulk Operations

```python
# Bulk create (using loop)
for i in range(100):
    await User.objects.create(
        username=f'user{i}',
        email=f'user{i}@example.com'
    )

# Bulk update
updated = await User.objects.filter(
    is_active=False
).update(is_active=True)

# Bulk delete
deleted = await User.objects.filter(
    created_at__lt=cutoff_date
).delete()
```

### Transactions

```python
from covet.database.orm import get_adapter

adapter = await get_adapter('default')

async with adapter.transaction():
    user = await User.objects.create(username='alice', email='alice@example.com')
    # More operations...
    # All committed together or rolled back on error
```

### Signals

```python
from covet.database.orm.signals import post_save, receiver

@receiver(post_save, sender=User)
async def on_user_saved(sender, instance, created, **kwargs):
    if created:
        print(f"New user: {instance.username}")
        # Send welcome email, etc.
```

## 🎯 Best Practices

1. **Always use async/await**
   ```python
   # Good
   user = await User.objects.get(id=1)
   
   # Bad
   user = User.objects.get(id=1)  # Won't work!
   ```

2. **Register adapters at startup**
   ```python
   async def startup():
       adapter = PostgreSQLAdapter(...)
       await adapter.connect()
       await register_adapter('default', adapter)
   ```

3. **Use connection pooling**
   ```python
   adapter = PostgreSQLAdapter(
       min_pool_size=5,   # Minimum connections
       max_pool_size=20,  # Maximum connections
   )
   ```

4. **Close connections on shutdown**
   ```python
   async def shutdown():
       from covet.database.orm import get_adapter_registry
       registry = get_adapter_registry()
       for alias in registry.list_aliases():
           adapter = registry.get(alias)
           await adapter.disconnect()
   ```

5. **Use values() for performance**
   ```python
   # When you don't need full model instances
   user_data = await User.objects.values('id', 'username', 'email').all()
   # Returns: [{'id': 1, 'username': 'alice', 'email': '...'}, ...]
   ```

6. **Use count() instead of len()**
   ```python
   # Good
   count = await User.objects.filter(is_active=True).count()
   
   # Bad (loads all records into memory)
   count = len(await User.objects.filter(is_active=True).all())
   ```

## 🔧 Multi-Database Setup

```python
# PostgreSQL (default)
pg_adapter = PostgreSQLAdapter(host='localhost', database='main_db')
await pg_adapter.connect()
await register_adapter('default', pg_adapter, make_default=True)

# MySQL (analytics)
mysql_adapter = MySQLAdapter(host='localhost', database='analytics_db')
await mysql_adapter.connect()
await register_adapter('analytics', mysql_adapter)

# SQLite (testing)
sqlite_adapter = SQLiteAdapter(database=':memory:')
await sqlite_adapter.connect()
await register_adapter('testing', sqlite_adapter)

# Use specific database
class AnalyticsEvent(Model):
    __database__ = 'analytics'  # Use MySQL
    # ...
```

## 🐛 Troubleshooting

### "Database adapter not registered"
```python
# Make sure you registered the adapter
await register_adapter('default', adapter, make_default=True)
```

### "RuntimeError: Event loop is closed"
```python
# Use asyncio.run() for top-level async code
asyncio.run(main())
```

### "Connection refused"
```python
# Check database is running and credentials are correct
adapter = PostgreSQLAdapter(
    host='localhost',  # Correct host?
    port=5432,         # Correct port?
    database='mydb',   # Database exists?
    user='postgres',   # User has permissions?
    password='...'     # Correct password?
)
```

## 📖 Complete Example

See `/src/covet/database/orm/INTEGRATION_EXAMPLE.py` for a comprehensive example with:
- Multi-database setup
- Model definitions
- All CRUD operations
- Signal handlers
- Transactions
- Advanced queries

## 📝 Next Steps

1. Read the full integration summary: `ORM_INTEGRATION_SUMMARY.md`
2. Check the example file: `src/covet/database/orm/INTEGRATION_EXAMPLE.py`
3. Explore the ORM source: `src/covet/database/orm/`
4. Explore adapter source: `src/covet/database/adapters/`

---

**Questions?** Check the integration summary or example code!
