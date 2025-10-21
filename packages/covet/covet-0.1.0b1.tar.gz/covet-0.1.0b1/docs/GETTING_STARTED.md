# Getting Started with CovetPy

**Time to Complete:** 30 minutes
**Difficulty:** Beginner
**Prerequisites:** Python 3.8+, basic SQL knowledge

Welcome to CovetPy! This guide will take you from zero to building your first database-backed application in under 30 minutes.

---

## Table of Contents

1. [Installation (5 minutes)](#installation-5-minutes)
2. [Hello World API (5 minutes)](#hello-world-api-5-minutes)
3. [Database Example (10 minutes)](#database-example-10-minutes)
4. [Next Steps](#next-steps)

---

## Installation (5 minutes)

### Prerequisites

Before installing CovetPy, ensure you have:

- **Python 3.8 or higher**
  ```bash
  python --version  # Should show 3.8+
  ```

- **pip** (usually comes with Python)
  ```bash
  pip --version
  ```

### Install CovetPy

```bash
# Install CovetPy (when published to PyPI)
pip install covetpy

# Or install from source
git clone https://github.com/yourorg/covetpy.git
cd covetpy
pip install -e .
```

### Verify Installation

```bash
# Test basic import
python -c "from covet.core.application import CovetPy; print('CovetPy installed successfully!')"
```

**Expected Output:**
```
CovetPy installed successfully!
```

---

## Hello World API (5 minutes)

Let's build your first API endpoint with CovetPy.

### Step 1: Create Your Application

Create a file called `app.py`:

```python
from covet import CovetPy
from covet.core.response import JSONResponse

app = CovetPy()

@app.route('/')
async def hello(request):
    return JSONResponse({'message': 'Hello, World!'})

if __name__ == '__main__':
    # Run with uvicorn (ASGI server)
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

### Step 2: Install ASGI Server

```bash
pip install uvicorn
```

### Step 3: Run Your Application

```bash
python app.py
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 4: Test It

Open another terminal:

```bash
curl http://localhost:8000/
```

**Response:**
```json
{"message": "Hello, World!"}
```

Congratulations! You've built your first CovetPy API.

---

## Database Example (10 minutes)

Now let's add database functionality to your application.

### Step 1: Define Your Model

Create a file called `models.py`:

```python
from covet.database.orm import Model
from covet.database.orm.fields import CharField, IntegerField

class User(Model):
    """User model - represents a user in our application."""

    username = CharField(max_length=100)
    age = IntegerField()

    class Meta:
        db_table = 'users'
        ordering = ['-id']

    def __str__(self):
        return f"User(id={self.id}, username={self.username})"
```

### Step 2: Connect to Database

Update your `app.py`:

```python
from covet import CovetPy
from covet.core.response import JSONResponse
from covet.database.adapters.sqlite import SQLiteAdapter
from covet.database.orm.adapter_registry import register_adapter
from models import User

app = CovetPy()

# Database setup
@app.on_startup
async def startup():
    """Initialize database connection on startup."""
    # Create SQLite adapter
    adapter = SQLiteAdapter(database='app.db')
    await adapter.connect()

    # Register as default adapter
    register_adapter('default', adapter)

    # Create table if it doesn't exist
    await adapter.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL
        )
    """)

    print("Database connected successfully!")

@app.route('/')
async def hello(request):
    return JSONResponse({'message': 'Hello, World!'})

# List all users
@app.route('/users', methods=['GET'])
async def list_users(request):
    users = await User.objects.all()
    return JSONResponse({
        'users': [
            {'id': u.id, 'username': u.username, 'age': u.age}
            for u in users
        ]
    })

# Create a user
@app.route('/users', methods=['POST'])
async def create_user(request):
    import json
    data = json.loads(request.body)

    user = await User.objects.create(
        username=data['username'],
        age=data['age']
    )

    return JSONResponse({
        'user': {
            'id': user.id,
            'username': user.username,
            'age': user.age
        }
    }, status=201)

# Get specific user
@app.route('/users/{id}', methods=['GET'])
async def get_user(request):
    user_id = int(request.path_params['id'])

    try:
        user = await User.objects.get(id=user_id)
        return JSONResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'age': user.age
            }
        })
    except User.DoesNotExist:
        return JSONResponse({'error': 'User not found'}, status=404)

# Update user
@app.route('/users/{id}', methods=['PUT'])
async def update_user(request):
    import json
    user_id = int(request.path_params['id'])
    data = json.loads(request.body)

    try:
        user = await User.objects.get(id=user_id)

        if 'username' in data:
            user.username = data['username']
        if 'age' in data:
            user.age = data['age']

        await user.save()

        return JSONResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'age': user.age
            }
        })
    except User.DoesNotExist:
        return JSONResponse({'error': 'User not found'}, status=404)

# Delete user
@app.route('/users/{id}', methods=['DELETE'])
async def delete_user(request):
    user_id = int(request.path_params['id'])

    try:
        user = await User.objects.get(id=user_id)
        await user.delete()
        return JSONResponse({'message': 'User deleted'})
    except User.DoesNotExist:
        return JSONResponse({'error': 'User not found'}, status=404)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

### Step 3: Run and Test

```bash
# Start the server
python app.py
```

In another terminal, test the API:

```bash
# Create a user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "age": 30}'

# List all users
curl http://localhost:8000/users

# Get specific user
curl http://localhost:8000/users/1

# Update user
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"age": 31}'

# Delete user
curl -X DELETE http://localhost:8000/users/1
```

---

## Next Steps

Congratulations! You've completed the Getting Started guide. Here's what you've learned:

- How to install CovetPy
- How to create a simple API endpoint
- How to connect to a database
- How to define models
- How to perform CRUD operations

### Where to Go Next

1. **Advanced ORM Features** - [ORM_ADVANCED.md](ORM_ADVANCED.md)
   - Learn about select_related() and prefetch_related() for query optimization
   - Master only(), defer(), values(), and values_list()
   - Understand relationships and eager loading

2. **Database Guide** - [DATABASE_QUICK_START.md](DATABASE_QUICK_START.md)
   - Connection pooling for production
   - Migrations and schema management
   - Query optimization techniques

3. **Security Guide** - [SECURITY_GUIDE.md](SECURITY_GUIDE.md)
   - JWT authentication
   - Rate limiting
   - Password security
   - Session management

4. **Performance Guide** - [PERFORMANCE.md](PERFORMANCE.md)
   - Benchmarks and optimization tips
   - Caching strategies
   - Query performance tuning

5. **Production Deployment** - [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
   - Production readiness checklist
   - Deployment best practices
   - Monitoring and logging

### Resources

- **Documentation:** [docs/README.md](README.md)
- **Examples:** [examples/](../examples/)
- **API Reference:** [API documentation](api/)
- **Issues:** [GitHub Issues](https://github.com/yourorg/covetpy/issues)

---

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'covet'`
- **Solution:** Make sure you installed CovetPy: `pip install covetpy` or `pip install -e .`

**Issue:** Database errors when creating tables
- **Solution:** Check database file permissions and ensure the directory is writable

**Issue:** API server won't start
- **Solution:** Check if port 8000 is already in use: `lsof -i :8000`

**Issue:** Import errors with models
- **Solution:** Ensure your models file is in the same directory or properly imported

### Getting Help

If you're stuck:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [existing issues](https://github.com/yourorg/covetpy/issues)
3. Ask in [Discussions](https://github.com/yourorg/covetpy/discussions)
4. Email: support@covetpy.org

---

**You're now ready to build production-grade applications with CovetPy!**
