# Core Application API Reference

Complete reference for CovetPy's core application classes and factory functions.

## Table of Contents

- [CovetPy](#covetpy)
- [CovetApplication](#covetapplication)
- [Factory Functions](#factory-functions)
- [Lifecycle Events](#lifecycle-events)
- [Configuration](#configuration)

## CovetPy

The main high-level application class providing a Flask-like API.

### Class: `CovetPy`

```python
class CovetPy:
    def __init__(
        self,
        debug: bool = False,
        middleware: Optional[List[Any]] = None,
        **kwargs
    ) -> None
```

**Description**: Main CovetPy application class using zero-dependency core. Provides a high-level wrapper around CovetPyASGI with a simple, Flask-like API.

**Parameters**:
- `debug` (bool): Enable debug mode for detailed error messages
- `middleware` (List[Any], optional): List of middleware to apply
- `**kwargs`: Additional arguments passed to CovetPyASGI

**Example**:
```python
from covet import CovetPy

# Basic application
app = CovetPy()

# With debug mode
app = CovetPy(debug=True)

# With custom middleware
from covet import CORSMiddleware

app = CovetPy(middleware=[CORSMiddleware])
```

### Route Decorators

#### `@app.route()`

```python
def route(
    self,
    path: str,
    methods: Optional[List[str]] = None,
    name: Optional[str] = None,
    **kwargs
) -> Callable
```

**Description**: Decorator to register a route handler.

**Parameters**:
- `path` (str): URL path pattern (e.g., "/users/{user_id}")
- `methods` (List[str], optional): HTTP methods (default: ["GET"])
- `name` (str, optional): Route name for URL generation
- `**kwargs`: Additional route options

**Example**:
```python
@app.route("/users", methods=["GET", "POST"])
async def users_handler(request):
    if request.method == "GET":
        return {"users": [...]}
    else:
        data = await request.json()
        return {"created": data}, 201
```

#### `@app.get()`, `@app.post()`, `@app.put()`, `@app.patch()`, `@app.delete()`

```python
def get(self, path: str, **kwargs) -> Callable
def post(self, path: str, **kwargs) -> Callable
def put(self, path: str, **kwargs) -> Callable
def patch(self, path: str, **kwargs) -> Callable
def delete(self, path: str, **kwargs) -> Callable
```

**Description**: Convenience decorators for specific HTTP methods.

**Example**:
```python
@app.get("/users")
async def list_users(request):
    return {"users": []}

@app.post("/users")
async def create_user(request):
    data = await request.json()
    return {"user": data}, 201

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Path parameters are automatically injected
    return {"user_id": user_id}
```

#### `@app.websocket()`

```python
def websocket(self, path: str, **kwargs) -> Callable
```

**Description**: Register WebSocket route handler.

**Example**:
```python
@app.websocket("/ws")
async def websocket_handler(websocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

### Middleware

#### `app.middleware()`

```python
def middleware(self, middleware_class: Union[Any, Callable]) -> None
```

**Description**: Add middleware to the application.

**Example**:
```python
from covet import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import time
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Process-Time"] = str(duration)
        return response

app.middleware(TimingMiddleware)
```

### Running the Application

#### `app.run()`

```python
def run(
    self,
    host: str = "127.0.0.1",
    port: int = 8000,
    **kwargs
) -> None
```

**Description**: Run the application using uvicorn (requires uvicorn to be installed).

**Parameters**:
- `host` (str): Host to bind to (default: "127.0.0.1")
- `port` (int): Port to bind to (default: 8000)
- `**kwargs`: Additional uvicorn configuration

**Example**:
```python
if __name__ == "__main__":
    # Development server
    app.run(host="127.0.0.1", port=8000)

    # Production-like settings
    app.run(
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info"
    )
```

### ASGI Interface

#### `app.__call__()`

```python
async def __call__(self, scope, receive, send)
```

**Description**: ASGI application interface for production servers.

**Example**:
```python
# In your_app.py
app = CovetPy()

@app.get("/")
async def root():
    return {"message": "Hello"}

# Run with uvicorn
# uvicorn your_app:app --host 0.0.0.0 --port 8000

# Run with gunicorn
# gunicorn your_app:app -k uvicorn.workers.UvicornWorker
```

## CovetApplication

Lower-level application class with full control over configuration and lifecycle.

### Class: `CovetApplication`

```python
class CovetApplication:
    def __init__(
        self,
        title: str = "CovetPy Application",
        version: str = "1.0.0",
        description: str = "High-performance web application built with CovetPy",
        config: Optional[Config] = None,
        container: Optional[Container] = None,
        debug: bool = False,
    ) -> None
```

**Description**: Pure CovetPy application with zero external dependencies. Provides full control over application configuration and lifecycle.

**Parameters**:
- `title` (str): Application title
- `version` (str): Application version
- `description` (str): Application description
- `config` (Config, optional): Configuration object
- `container` (Container, optional): Dependency injection container
- `debug` (bool): Debug mode

**Example**:
```python
from covet.core.app_pure import CovetApplication
from covet.core.config import Config

# Create custom config
config = Config(
    environment="production",
    debug=False
)

app = CovetApplication(
    title="My API",
    version="1.0.0",
    description="Production API",
    config=config,
    debug=False
)
```

### Route Management

#### `app.add_route()`

```python
def add_route(
    self,
    path: str,
    handler: Callable,
    methods: List[str],
    name: Optional[str] = None,
    middleware: Optional[List[Callable]] = None,
    **kwargs
) -> None
```

**Description**: Add route to the application programmatically.

**Parameters**:
- `path` (str): URL path pattern
- `handler` (Callable): Route handler function
- `methods` (List[str]): HTTP methods
- `name` (str, optional): Route name
- `middleware` (List[Callable], optional): Route-specific middleware

**Example**:
```python
async def user_handler(request):
    return {"user": "data"}

app.add_route(
    path="/users/{user_id}",
    handler=user_handler,
    methods=["GET", "PUT"],
    name="user_detail"
)
```

### Middleware Management

#### `app.add_middleware()`

```python
def add_middleware(
    self,
    middleware: Union[Type, Callable],
    **kwargs
) -> None
```

**Description**: Add middleware to the application.

**Example**:
```python
from covet import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)
```

### Exception Handling

#### `app.exception_handler()`

```python
def exception_handler(self, exc_class: Type[Exception]) -> Callable
```

**Description**: Decorator to register exception handler.

**Example**:
```python
from covet.core.exceptions import HTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }, exc.status_code

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return {"error": str(exc)}, 400
```

#### `app.add_exception_handler()`

```python
def add_exception_handler(
    self,
    exc_class: Type[Exception],
    handler: Callable
) -> None
```

**Description**: Add exception handler programmatically.

## Factory Functions

### `create_app()`

```python
def create_app(**kwargs) -> CovetApplication
```

**Description**: Create a CovetPy application with default settings.

**Example**:
```python
from covet import create_app

app = create_app(
    title="My API",
    version="1.0.0",
    debug=True
)
```

### `Covet.create_app()`

```python
@staticmethod
def create_app(
    title: str = "CovetPy Application",
    version: str = "1.0.0",
    description: str = "High-performance web application built with CovetPy",
    config: Optional[Config] = None,
    config_file: Optional[Path] = None,
    environment: Optional[Environment] = None,
    debug: Optional[bool] = None,
    **kwargs
) -> CovetApplication
```

**Description**: Create a new CovetPy application with full configuration options.

**Parameters**:
- `title` (str): Application title
- `version` (str): Application version
- `description` (str): Application description
- `config` (Config, optional): Configuration object
- `config_file` (Path, optional): Path to configuration file
- `environment` (Environment, optional): Target environment
- `debug` (bool, optional): Debug mode override
- `**kwargs`: Additional configuration

**Example**:
```python
from covet.core.app_pure import Covet
from pathlib import Path

app = Covet.create_app(
    title="Production API",
    version="2.0.0",
    config_file=Path("config.yaml"),
    environment="production",
    debug=False
)
```

## Lifecycle Events

### Startup Events

#### `app.on_event("startup")`

```python
@app.on_event("startup")
async def startup_handler():
    # Initialize resources
    pass
```

**Description**: Register startup event handler.

**Example**:
```python
@app.on_event("startup")
async def startup():
    # Connect to database
    await database.connect()
    print("Application started")

@app.on_event("startup")
async def load_ml_model():
    # Load ML model
    global model
    model = load_model("model.pkl")
```

### Shutdown Events

#### `app.on_event("shutdown")`

```python
@app.on_event("shutdown")
async def shutdown_handler():
    # Clean up resources
    pass
```

**Description**: Register shutdown event handler.

**Example**:
```python
@app.on_event("shutdown")
async def shutdown():
    # Close database connection
    await database.disconnect()
    print("Application stopped")
```

## Configuration

### Application State

#### `app.state()`

```python
def state(self) -> Dict[str, Any]
```

**Description**: Get application state information.

**Returns**: Dictionary containing application metadata and statistics.

**Example**:
```python
state = app.state()
print(f"Routes: {state['routes_count']}")
print(f"Middleware: {state['middleware_count']}")
```

### Mounting Sub-Applications

#### `app.mount()`

```python
def mount(
    self,
    path: str,
    app: Any,
    name: Optional[str] = None
) -> None
```

**Description**: Mount a sub-application at a specific path.

**Example**:
```python
# Create sub-application for admin panel
admin_app = CovetPy()

@admin_app.get("/users")
async def admin_users():
    return {"admin": "users"}

# Mount at /admin
app.mount("/admin", admin_app)

# Now accessible at /admin/users
```

### Including Routers

#### `app.include_router()`

```python
def include_router(
    self,
    router: Router,
    prefix: str = ""
) -> None
```

**Description**: Include routes from another router.

**Example**:
```python
from covet.core.routing import CovetRouter

# Create router
api_router = CovetRouter()

@api_router.route("/items", ["GET"])
async def list_items():
    return {"items": []}

# Include with prefix
app.include_router(api_router, prefix="/api/v1")

# Now accessible at /api/v1/items
```

## Response Helpers

### JSON Response

```python
app.json_response(
    data: Any,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Response
```

**Example**:
```python
@app.get("/users")
async def get_users():
    users = [{"id": 1, "name": "Alice"}]
    return app.json_response(users)
```

### Text Response

```python
app.text_response(
    content: str,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Response
```

### HTML Response

```python
app.html_response(
    content: str,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Response
```

## Complete Example

```python
from covet import CovetPy, BaseHTTPMiddleware
from covet.core.exceptions import HTTPException

# Create application
app = CovetPy(debug=True)

# Add middleware
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = request.headers.get("authorization")
        if not token and request.path.startswith("/api"):
            raise HTTPException(status_code=401, detail="Unauthorized")
        return await call_next(request)

app.middleware(AuthMiddleware)

# Startup event
@app.on_event("startup")
async def startup():
    print("Application starting...")

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to CovetPy!"}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}

@app.post("/users")
async def create_user(request):
    data = await request.json()
    # Validate and create user
    return {"user": data, "status": "created"}, 201

# Exception handler
@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    return {
        "error": exc.detail,
        "status": exc.status_code
    }, exc.status_code

# Run application
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
```

## See Also

- [HTTP Objects API](02-http-objects.md)
- [Routing API](03-routing.md)
- [Middleware API](04-middleware.md)
- [Configuration API](05-configuration.md)
