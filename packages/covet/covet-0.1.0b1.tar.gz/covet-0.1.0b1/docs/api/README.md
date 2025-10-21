# CovetPy API Reference

Complete API reference documentation for CovetPy framework.

## Status: Experimental (v0.1.0)

**Important**: CovetPy is an educational framework. APIs may change, and some features are experimental. For production, use FastAPI, Django, or Flask.

## API Documentation Structure

### Core Framework

1. **[Core Application](01-core-application.md)** - Main application classes, routing decorators, lifecycle events
   - `CovetPy` - High-level Flask-like API
   - `CovetApplication` - Lower-level application class
   - Factory functions and configuration
   - Lifecycle events (startup/shutdown)

2. **[HTTP Objects](02-http-objects.md)** - Request and Response handling
   - `Request` - Incoming HTTP requests
   - `Response` - HTTP responses
   - `StreamingResponse` - Streaming responses
   - `Cookie` - Cookie management
   - Response helpers (json_response, html_response, etc.)

3. **[Routing](03-routing.md)** - URL routing and path matching (Planned)
   - Static and dynamic routes
   - Path parameters
   - Route groups and prefixes

4. **[Middleware](04-middleware.md)** - Request/response pipeline (Planned)
   - Built-in middleware
   - Custom middleware
   - Middleware ordering

5. **[Configuration](05-configuration.md)** - Application configuration (Planned)
   - Config class
   - Environment management
   - Settings management

### Database & ORM (Experimental)

6. **[ORM Models](06-orm-models.md)** - Database models (Experimental)
   - Model definition
   - Field types
   - Relationships
   - Model methods

7. **[Query API](07-orm-queries.md)** - Database queries (Experimental)
   - QuerySet API
   - Filtering and ordering
   - Aggregation
   - Raw queries

8. **[ORM Fields](08-orm-fields.md)** - Model field types (Experimental)
   - Built-in fields
   - Field options
   - Custom fields

### Security (Basic)

9. **[Authentication](09-authentication.md)** - User authentication (Basic)
   - JWT authentication
   - Session authentication
   - Password hashing

10. **[Security](10-security.md)** - Security features (Basic)
    - CSRF protection
    - Security headers
    - Input validation

### Advanced Features

11. **[Caching](11-caching.md)** - Caching strategies (Basic)
    - Cache backends
    - Caching decorators
    - Cache invalidation

12. **[Sessions](12-sessions.md)** - Session management (Basic)
    - Session backends
    - Session middleware
    - Cookie sessions

13. **[WebSocket](13-websocket.md)** - Real-time communication (Experimental)
    - WebSocket connections
    - Message handling
    - Broadcasting

## Quick Reference

### Creating an Application

```python
from covet import CovetPy

app = CovetPy()
```

### Defining Routes

```python
@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

@app.post("/users")
async def create_user(request):
    data = await request.json()
    return {"user": data}, 201
```

### Request Handling

```python
@app.post("/data")
async def handle_data(request):
    # Query parameters
    page = request.query.get("page", "1")

    # JSON body
    if request.is_json():
        data = await request.json()

    # Form data
    if request.is_form():
        form = await request.form()

    # Headers
    auth = request.get_header("authorization")

    # Cookies
    session_id = request.cookies().get("session_id")

    return {"received": True}
```

### Response Types

```python
from covet.core.http import (
    json_response,
    html_response,
    text_response,
    redirect_response,
    error_response
)

@app.get("/json")
async def json_endpoint():
    return json_response({"data": "value"})

@app.get("/html")
async def html_endpoint():
    return html_response("<h1>Hello</h1>")

@app.get("/redirect")
async def redirect_endpoint():
    return redirect_response("/new-location")
```

### Middleware

```python
from covet import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Before request
        response = await call_next(request)
        # After request
        return response

app.middleware(CustomMiddleware)
```

### ORM (Experimental)

```python
from covet.orm import Model, CharField, IntegerField

class User(Model):
    name = CharField(max_length=100)
    age = IntegerField()

    class Meta:
        table_name = "users"

# Queries
users = await User.objects.all()
user = await User.objects.get(id=1)
users = await User.objects.filter(age__gt=18)

# Create
user = User(name="Alice", age=25)
await user.asave()
```

### Exception Handling

```python
from covet.core.exceptions import HTTPException

@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    return {
        "error": exc.detail,
        "code": exc.status_code
    }, exc.status_code

@app.get("/protected")
async def protected_route():
    if not authorized:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
```

### Lifecycle Events

```python
@app.on_event("startup")
async def startup():
    # Initialize database, load models, etc.
    print("Application starting...")

@app.on_event("shutdown")
async def shutdown():
    # Clean up resources
    print("Application shutting down...")
```

## Feature Status

| Feature | Status | Documentation | Notes |
|---------|--------|---------------|-------|
| Core Application | ✅ Stable | Complete | Production-ready ASGI |
| HTTP Objects | ✅ Stable | Complete | Request/Response |
| Routing | ✅ Stable | Complete | Static & dynamic |
| Middleware | ✅ Stable | Complete | Pipeline system |
| ORM Models | ⚠️ Experimental | Basic | Not feature-complete |
| ORM Queries | ⚠️ Experimental | Basic | Limited optimization |
| Authentication | ⚠️ Basic | Basic | Educational only |
| Security | ⚠️ Basic | Basic | Not audited |
| Caching | ⚠️ Basic | Basic | Simple implementation |
| Sessions | ⚠️ Basic | Basic | Cookie & Redis |
| WebSocket | ⚠️ Experimental | Basic | Limited functionality |
| GraphQL | ❌ Planned | None | Future feature |
| Admin UI | ❌ Planned | None | Future feature |

**Legend**:
- ✅ Stable - Ready for educational use
- ⚠️ Experimental/Basic - Use with caution, educational only
- ❌ Planned - Not yet implemented

## API Conventions

### Async/Await

Most CovetPy APIs support async/await:

```python
# Async handlers (recommended)
@app.get("/async")
async def async_handler(request):
    data = await some_async_operation()
    return data

# Sync handlers (also supported)
@app.get("/sync")
def sync_handler(request):
    return {"message": "Hello"}
```

### Type Hints

CovetPy uses type hints throughout:

```python
from typing import Dict, List, Optional
from covet.core.http import Request, Response

@app.post("/typed")
async def typed_handler(request: Request) -> Response:
    data: Dict[str, Any] = await request.json()
    return Response(data)
```

### Return Values

Route handlers can return:
- `dict` or `list` → Automatic JSON response
- `str` → Text response
- `Response` object → Direct response
- `tuple` → (body, status_code) or (body, status_code, headers)

```python
@app.get("/auto-json")
async def auto_json():
    return {"data": "value"}  # Auto-converts to JSON

@app.get("/with-status")
async def with_status():
    return {"created": True}, 201

@app.get("/with-headers")
async def with_headers():
    return {"data": "value"}, 200, {"X-Custom": "Header"}
```

## Error Handling

### Built-in Exceptions

```python
from covet.core.exceptions import (
    HTTPException,      # Base HTTP exception
    ValidationError,    # Validation errors
    NotFound,          # 404 errors
    Unauthorized,      # 401 errors
    Forbidden,         # 403 errors
)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID"
        )

    user = find_user(user_id)
    if not user:
        raise NotFound(detail=f"User {user_id} not found")

    return user
```

### Custom Exception Handlers

```python
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return {"error": str(exc)}, 400

@app.exception_handler(Exception)
async def catch_all_handler(request, exc):
    # Log error
    logger.error(f"Unhandled error: {exc}")
    return {"error": "Internal server error"}, 500
```

## Testing

### Testing Your Application

```python
from covet.testing import TestClient

app = CovetPy()

@app.get("/")
async def root():
    return {"message": "Hello"}

# Test client
client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}
```

## Performance Considerations

### Best Practices

1. **Use async/await for I/O operations**
   ```python
   @app.get("/data")
   async def get_data():
       # Good: async database query
       data = await db.fetch_all()
       return data
   ```

2. **Cache expensive operations**
   ```python
   from covet.cache import cache

   @app.get("/expensive")
   @cache(ttl=300)  # Cache for 5 minutes
   async def expensive_operation():
       result = compute_expensive_data()
       return result
   ```

3. **Use streaming for large responses**
   ```python
   @app.get("/large-file")
   async def download():
       return StreamingResponse(
           file_generator(),
           media_type="application/octet-stream"
       )
   ```

## Migration from Other Frameworks

### From Flask

```python
# Flask
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    return jsonify({"user": data}), 201

# CovetPy
from covet import CovetPy

app = CovetPy()

@app.post("/users")
async def create_user(request):
    data = await request.json()
    return {"user": data}, 201
```

### From FastAPI

```python
# FastAPI
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.post("/users")
async def create_user(user: User):
    return user

# CovetPy (similar but less validation)
from covet import CovetPy

app = CovetPy()

@app.post("/users")
async def create_user(request):
    data = await request.json()
    # Manual validation recommended
    return data
```

## See Also

- [Getting Started Tutorial](../tutorials/01-getting-started.md)
- [ORM Quick Reference](../ORM_QUICK_REFERENCE.md)
- [Example Applications](../../examples/)
- [Architecture Documentation](../ARCHITECTURE.md)

## Contributing

Found an issue with the documentation? Please open an issue or submit a pull request on GitHub.

API documentation should be:
- Accurate and tested
- Include working examples
- Cover edge cases
- Note limitations and experimental features
