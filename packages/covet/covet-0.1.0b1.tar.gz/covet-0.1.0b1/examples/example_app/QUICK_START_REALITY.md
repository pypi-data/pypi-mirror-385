# CovetPy Quick Start - Reality Edition

**What Actually Works** (Tested October 2025)

This guide shows REAL working code, not documentation promises.

---

## 1. Installation

```bash
cd /path/to/NeutrinoPy
# Add to Python path
export PYTHONPATH="/path/to/NeutrinoPy/src:$PYTHONPATH"
```

---

## 2. Hello World Application

```python
import sys
sys.path.insert(0, '/path/to/NeutrinoPy/src')

from covet.core import CovetApplication  # NOT 'Application'!

app = CovetApplication()

# App is ASGI-compatible
# Run with: uvicorn app:app
```

✅ **This works!**

---

## 3. REST API (FastAPI-Style)

```python
from covet.api.rest import RESTFramework, BaseModel, Field

# Create API
api = RESTFramework(
    title="My API",
    version="1.0.0",
    enable_docs=True
)

# Define input validation
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    age: int = Field(..., ge=0, le=150)

# Define routes
@api.get('/users')
async def list_users():
    return {'users': [], 'count': 0}

@api.post('/users')
async def create_user(user: UserCreate):
    return {'message': 'User created', 'username': user.username}

@api.get('/users/{user_id}')
async def get_user(user_id: int):
    return {'user': {'id': user_id}}
```

✅ **This works perfectly!** Very similar to FastAPI.

---

## 4. Database & ORM

### Step 1: Setup Database

```python
from covet.database import SQLiteAdapter, DatabaseManager

# Create adapter (NOT Database(adapter='sqlite')!)
adapter = SQLiteAdapter('app.db')
db = DatabaseManager(adapter)

# Connect
await db.connect()
```

### Step 2: Define Models

```python
from covet.database.orm import Model, CharField, TextField, ForeignKey, DateTimeField

class User(Model):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=100, unique=True)
    password_hash = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        table_name = "users"

class Post(Model):
    title = CharField(max_length=200)
    content = TextField()
    author = ForeignKey(User, related_name='posts')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        table_name = "posts"
```

✅ **This works!** Django-like API.

### Step 3: Use Database

```python
# Create table
await db.create_table('users', {
    'id': 'INTEGER PRIMARY KEY',
    'username': 'TEXT',
    'email': 'TEXT'
})

# Insert
await db.insert('users', {
    'username': 'john',
    'email': 'john@example.com'
})

# Query
users = await db.fetch_all('SELECT * FROM users')

# Disconnect
await db.disconnect()
```

✅ **This works!**

---

## 5. JWT Authentication

```python
from covet.security.jwt_auth import (
    JWTAuthenticator,
    JWTConfig,
    JWTAlgorithm,  # MUST use enum!
    TokenType,     # MUST use enum!
)

# Configure JWT
config = JWTConfig(
    secret_key="your_secret_key_minimum_32_characters_long",
    algorithm=JWTAlgorithm.HS256,  # NOT "HS256" string!
    access_token_expire_minutes=15,
    refresh_token_expire_days=30
)

auth = JWTAuthenticator(config)

# Create token
token = auth.create_token(
    subject="user123",
    token_type=TokenType.ACCESS,  # NOT "access" string!
    roles=["user"],
    permissions=["read:posts"]
)

# Verify token
claims = auth.verify_token(token)
print(f"User: {claims['sub']}")
print(f"Roles: {claims['roles']}")

# Create token pair (access + refresh)
token_pair = auth.create_token_pair(
    subject="user123",
    roles=["user"],
    permissions=["read:posts", "write:posts"]
)

print(f"Access: {token_pair.access_token}")
print(f"Refresh: {token_pair.refresh_token}")
print(f"Expires in: {token_pair.expires_in} seconds")
```

✅ **This works!** Production-ready security.

**IMPORTANT:** Must use enums (`JWTAlgorithm.HS256`, `TokenType.ACCESS`), not strings!

---

## 6. WebSocket Support

```python
from covet.websocket import CovetWebSocket, WebSocketEndpoint

# Create WebSocket app
ws = CovetWebSocket(max_connections=1000)

# Method 1: Decorator style
@ws.websocket('/ws/notifications')
async def notification_handler(websocket):
    await websocket.accept()
    await websocket.send_text("Connected!")

    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echo: {message}")

# Method 2: Endpoint class
class ChatEndpoint(WebSocketEndpoint):
    async def on_connect(self, websocket):
        await websocket.accept()
        print(f"Client connected: {websocket.client}")

    async def on_receive(self, websocket, message):
        # Broadcast to all
        await self.broadcast(message)

    async def on_disconnect(self, websocket, close_code):
        print(f"Client disconnected: {close_code}")

# Add endpoint
ws.add_route('/ws/chat', ChatEndpoint())

# Broadcasting
await ws.broadcast_to_all({"type": "notification", "message": "Hello everyone!"})
await ws.broadcast_to_room("room1", {"message": "Room message"})
await ws.broadcast_to_user("user123", {"message": "Private message"})
```

✅ **This works!** Excellent WebSocket support.

---

## 7. Error Handling

```python
from covet.api.rest import (
    NotFoundError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    InternalServerError
)

@api.get('/users/{user_id}')
async def get_user(user_id: int):
    # User not found
    if user_id not in users:
        raise NotFoundError(detail=f"User {user_id} not found")

    # Invalid input
    if user_id < 0:
        raise BadRequestError(detail="User ID must be positive")

    # Not authorized
    if not has_permission():
        raise UnauthorizedError(detail="Authentication required")

    return {'user': users[user_id]}
```

✅ **This works!** RFC 7807 Problem Details format.

---

## 8. Input Validation

```python
from covet.api.rest import BaseModel, Field, ValidationError
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters)"
    )
    email: str = Field(
        ...,
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        description="Valid email address"
    )
    age: int = Field(..., ge=0, le=150, description="Age (0-150)")
    bio: Optional[str] = Field(None, max_length=500)

@api.post('/users')
async def create_user(user: UserCreate):
    # Pydantic automatically validates!
    # Invalid data raises ValidationError
    return {'message': 'User created', 'username': user.username}
```

✅ **This works perfectly!** Full Pydantic integration.

---

## 9. Pagination

```python
from covet.api.rest import PaginationParams

@api.get('/users')
async def list_users(pagination: PaginationParams):
    # pagination.page = current page
    # pagination.page_size = items per page
    # pagination.offset = calculated offset

    offset = pagination.offset
    limit = pagination.page_size

    # Query with pagination
    query = f"SELECT * FROM users LIMIT {limit} OFFSET {offset}"
    users = await db.fetch_all(query)

    return {
        'data': users,
        'page': pagination.page,
        'page_size': pagination.page_size,
        'total': 100  # Total count from DB
    }
```

✅ **This works!**

---

## 10. Complete Working Example

See `/example_app/full_app.py` for a complete Blog API with:
- ✅ Application setup
- ✅ Database connectivity
- ✅ ORM models
- ✅ REST API endpoints
- ✅ JWT authentication
- ✅ WebSocket support

**Run it:**
```bash
cd example_app
python full_app.py
```

---

## What DOESN'T Work Yet

❌ **Avoid these features:**

### 1. Caching
```python
# DOESN'T WORK
from covet.cache import Cache  # Cache not exported
```

### 2. Middleware Configuration
```python
# DOESN'T WORK
from covet.core import CORSMiddleware
cors = CORSMiddleware(app=None, allowed_origins=["*"])  # Wrong signature
```

### 3. Query Builder
```python
# DOESN'T WORK
from covet.database.query_builder import QueryBuilder
qb = QueryBuilder('users')  # Runtime errors
```

### 4. OpenAPI Schema Generation
```python
# DOESN'T WORK
api = RESTFramework(...)
schema = api.get_openapi_schema()  # Method doesn't exist
```

**Workaround:** Use raw SQL, manual middleware, direct Redis/Memcached.

---

## Common Pitfalls

### ❌ Wrong: Using documentation class names
```python
from covet.core import Application  # ImportError!
```

### ✅ Correct: Using actual class names
```python
from covet.core import CovetApplication
```

---

### ❌ Wrong: JWT with strings
```python
config = JWTConfig(algorithm="HS256")  # Doesn't work!
token = auth.create_token(subject="user", token_type="access")  # Fails!
```

### ✅ Correct: JWT with enums
```python
config = JWTConfig(algorithm=JWTAlgorithm.HS256)
token = auth.create_token(subject="user", token_type=TokenType.ACCESS)
```

---

### ❌ Wrong: Database API from docs
```python
db = Database(adapter='sqlite', database='app.db')  # Wrong signature!
```

### ✅ Correct: Actual database API
```python
adapter = SQLiteAdapter('app.db')
db = DatabaseManager(adapter)
```

---

## Tips for Success

1. **Ignore the documentation** - Use this guide and source code
2. **Read the `__all__` exports** - Shows what's actually available
3. **Use type hints** - IDE autocomplete helps a lot
4. **Check example_app/** - Real working code
5. **Join the community** - Others have solved these issues

---

## Questions?

**Check these files:**
- `REALITY_AUDIT_REPORT.md` - Detailed test results
- `example_app/full_app.py` - Working complete application
- `example_app/test_*.py` - Individual feature tests

**Found a bug?** The framework is evolving. Check source code for latest API.

---

## Summary

**What Works:**
✅ REST API (excellent)
✅ JWT Auth (production-ready)
✅ WebSocket (comprehensive)
✅ ORM (intuitive)
✅ Validation (perfect Pydantic)
✅ Database (works, weird API)

**What Doesn't:**
❌ Caching
❌ Query Builder
❌ Middleware config
❌ OpenAPI generation

**Overall:** 60% of features work. Use what works, avoid what doesn't.

---

*Last Updated: October 12, 2025*
*Based on real build testing*
*Your mileage may vary - always test!*
