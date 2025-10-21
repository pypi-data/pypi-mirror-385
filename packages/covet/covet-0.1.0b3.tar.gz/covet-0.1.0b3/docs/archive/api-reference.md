# 📖 CovetPy API Reference

**Complete reference documentation for the CovetPy framework**

This comprehensive API reference covers all classes, methods, and utilities available in CovetPy. Use this as your go-to resource for detailed function signatures, parameters, and examples.

---

## 📚 Table of Contents

### Core Framework
- [CovetPy Application](#covet-application)
- [Configuration](#configuration)  
- [Dependency Injection](#dependency-injection)
- [Middleware](#middleware)
- [Exception Handling](#exception-handling)

### API Layer
- [HTTP Routing](#http-routing)
- [Request/Response](#requestresponse)
- [WebSocket](#websocket)
- [GraphQL](#graphql)
- [gRPC](#grpc)

### Data Layer  
- [ORM & Models](#orm--models)
- [Database](#database)
- [Query Builder](#query-builder)
- [Migrations](#migrations)

### Integration
- [Caching](#caching)
- [Message Queues](#message-queues)
- [Serialization](#serialization)
- [Authentication](#authentication)

### Utilities
- [Logging](#logging)
- [Testing](#testing)
- [CLI](#cli)
- [Performance](#performance)

---

## 🏗️ CovetPy Application

### `class CovetPy`

The main application class that provides the foundation for CovetPy applications.

#### Constructor

```python
def __init__(
    self,
    title: str = "CovetPy API",
    description: str = "",
    version: str = "1.0.0", 
    config: Optional[Config] = None,
    debug: bool = False,
    docs_url: Optional[str] = "/docs",
    redoc_url: Optional[str] = "/redoc",
    openapi_url: Optional[str] = "/openapi.json",
    **kwargs
) -> None
```

**Parameters:**
- `title` (str): Application title for documentation
- `description` (str): Application description
- `version` (str): API version
- `config` (Config): Configuration object
- `debug` (bool): Enable debug mode
- `docs_url` (str): Swagger UI documentation URL
- `redoc_url` (str): ReDoc documentation URL
- `openapi_url` (str): OpenAPI schema URL

**Example:**
```python
from covet import CovetPy

app = CovetPy(
    title="My High-Performance API",
    description="Built with CovetPy for maximum speed",
    version="2.1.0",
    debug=False
)
```

#### Methods

##### `create_app(config: Optional[Config] = None) -> CovetPy`

Factory method to create a configured CovetPy application.

```python
@classmethod
def create_app(cls, config: Optional[Config] = None) -> "CovetPy":
    """Create a configured CovetPy application"""
    app = cls(config=config)
    await app.initialize()
    return app
```

**Example:**
```python
from covet import CovetPy, Config

config = Config(debug=True, database_url="postgresql://...")
app = await CovetPy.create_app(config=config)
```

##### `include_router(router: APIRouter, prefix: str = "", tags: List[str] = None) -> None`

Include a router with optional prefix and tags.

```python
def include_router(
    self, 
    router: APIRouter, 
    prefix: str = "",
    tags: Optional[List[str]] = None,
    dependencies: Optional[List[Depends]] = None
) -> None
```

**Example:**
```python
from covet import APIRouter

user_router = APIRouter()

@user_router.get("/profile")
async def get_profile():
    return {"user": "profile"}

app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
```

##### `add_middleware(middleware_class: Type[BaseMiddleware], **options) -> None`

Add middleware to the application stack.

```python
def add_middleware(
    self, 
    middleware_class: Type[BaseMiddleware], 
    **options
) -> None
```

**Example:**
```python
from covet.middleware import CORSMiddleware, RateLimitMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True
)

app.add_middleware(
    RateLimitMiddleware,
    calls=100,
    period=60
)
```

##### `on_startup / on_shutdown`

Event handlers for application lifecycle.

```python
@app.on_startup
async def startup_handler():
    """Initialize resources on startup"""
    await database.connect()
    await cache.initialize()

@app.on_shutdown  
async def shutdown_handler():
    """Cleanup resources on shutdown"""
    await database.disconnect()
    await cache.close()
```

##### `run(host: str = "127.0.0.1", port: int = 8000, **kwargs) -> None`

Run the application server.

```python
def run(
    self,
    host: str = "127.0.0.1",
    port: int = 8000,
    workers: Optional[int] = None,
    reload: bool = False,
    **kwargs
) -> None
```

**Example:**
```python
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        workers=4,
        reload=True  # Development only
    )
```

---

## ⚙️ Configuration

### `class Config`

Configuration management with environment-based settings.

```python
class Config(BaseSettings):
    """Base configuration class"""
    
    # Application
    app_name: str = "CovetPy API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Environment = Environment.PRODUCTION
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(20, env="DATABASE_POOL_SIZE")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    allowed_hosts: List[str] = Field(default_factory=list, env="ALLOWED_HOSTS")
    
    # Performance
    workers: int = Field(4, env="WORKERS")
    worker_connections: int = Field(1000, env="WORKER_CONNECTIONS")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

#### Environment Classes

```python
class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class DatabaseConfig(BaseModel):
    url: str
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    echo: bool = False

class CacheConfig(BaseModel):
    backend: str = "redis"
    url: str = "redis://localhost:6379/0"
    default_ttl: int = 300
```

**Usage:**
```python
from covet import Config, Environment, DatabaseConfig

class MyConfig(Config):
    environment = Environment.PRODUCTION
    database = DatabaseConfig(
        url="postgresql://user:pass@host/db",
        pool_size=50
    )
    
    # Custom settings
    api_rate_limit: int = 1000
    external_api_key: str = Field(..., env="EXTERNAL_API_KEY")
```

---

## 💉 Dependency Injection

### `class Container`

High-performance dependency injection container with lifecycle management.

```python
class Container:
    """Dependency injection container"""
    
    def register_singleton(self, interface: Type[T], implementation: Optional[Type[T]] = None) -> None
    def register_transient(self, interface: Type[T], implementation: Optional[Type[T]] = None) -> None  
    def register_scoped(self, interface: Type[T], implementation: Optional[Type[T]] = None) -> None
    def register_factory(self, interface: Type[T], factory: Callable[..., T]) -> None
    def resolve(self, interface: Type[T]) -> T
```

#### Decorators

```python
@Singleton
class UserService:
    """Singleton service - single instance"""
    def __init__(self):
        self.users = []

@Transient  
class RequestLogger:
    """Transient service - new instance each time"""
    def log(self, message: str):
        print(f"LOG: {message}")

@Scoped
class DatabaseSession:
    """Scoped service - one instance per request"""
    def __init__(self):
        self.session = create_session()
```

#### Dependency Injection

```python
from covet import Depends

def get_user_service() -> UserService:
    return app.container.resolve(UserService)

@get("/users")
async def list_users(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    return await user_service.get_all()
```

#### Advanced DI Patterns

```python
# Factory registration
def create_redis_client(config: Config) -> Redis:
    return Redis(url=config.redis_url)

container.register_factory(Redis, create_redis_client)

# Interface binding
class IUserRepository(Protocol):
    async def get_user(self, user_id: int) -> Optional[User]: ...

class PostgreSQLUserRepository(IUserRepository):
    async def get_user(self, user_id: int) -> Optional[User]:
        # Implementation
        pass

container.register_singleton(IUserRepository, PostgreSQLUserRepository)
```

---

## 🌐 HTTP Routing

### Decorators

CovetPy provides clean, decorator-based routing.

```python
from covet import get, post, put, delete, patch, head, options

@get("/users")
async def list_users() -> List[User]:
    """GET endpoint"""
    return await User.all()

@post("/users", response_model=User, status_code=201)
async def create_user(user: UserCreate) -> User:
    """POST endpoint with validation"""
    return await User.create(**user.dict())

@put("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate) -> User:
    """PUT endpoint with path parameter"""
    existing = await User.get(user_id)
    return await existing.update(**user.dict(exclude_unset=True))

@delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int) -> None:
    """DELETE endpoint"""
    user = await User.get(user_id)
    await user.delete()
```

### `class APIRouter`

Group related routes together.

```python
from covet import APIRouter

router = APIRouter(prefix="/api/v1", tags=["users"])

@router.get("/profile")
async def get_profile():
    return {"profile": "data"}

@router.post("/settings")
async def update_settings(settings: UserSettings):
    return {"updated": True}

# Include in main app
app.include_router(router)
```

### Path Parameters

```python
@get("/users/{user_id}")
async def get_user(user_id: int) -> User:
    """Path parameter with automatic validation"""
    return await User.get(user_id)

@get("/posts/{post_id}/comments/{comment_id}")
async def get_comment(post_id: int, comment_id: int) -> Comment:
    """Multiple path parameters"""
    return await Comment.get(post_id=post_id, id=comment_id)

# Path parameter validation
@get("/users/{user_id}")
async def get_user(user_id: int = Path(..., gt=0, description="User ID")):
    """Validated path parameter"""
    return await User.get(user_id)
```

### Query Parameters

```python
from typing import Optional, List

@get("/users")
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, min_length=3),
    tags: Optional[List[str]] = Query(None),
    active: bool = Query(True)
) -> List[User]:
    """Query parameters with validation"""
    query = User.query().filter(active=active)
    
    if search:
        query = query.filter(User.name.contains(search))
    
    if tags:
        query = query.filter(User.tags.overlap(tags))
    
    return await query.offset((page-1) * per_page).limit(per_page).all()
```

### Request Body

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)

@post("/users")
async def create_user(user: UserCreate) -> User:
    """Automatic request body validation"""
    return await User.create(**user.dict())

# File uploads
@post("/users/{user_id}/avatar")
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(..., description="Avatar image")
):
    """File upload handling"""
    content = await file.read()
    await save_avatar(user_id, content, file.filename)
    return {"filename": file.filename, "size": len(content)}
```

### Response Models

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> User:
    """Automatic response serialization"""
    return await User.get(user_id)
```

---

## 📡 WebSocket

### WebSocket Endpoints

```python
from covet import websocket, WebSocket

@websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Basic WebSocket endpoint"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

# With path parameters
@websocket("/ws/room/{room_id}")
async def room_websocket(websocket: WebSocket, room_id: int):
    """WebSocket with path parameters"""
    await websocket.accept()
    await join_room(websocket, room_id)
    
    async for message in websocket.iter_text():
        await broadcast_to_room(room_id, message)
```

### Connection Manager

```python
class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
    
    async def disconnect(self, websocket: WebSocket, room: str):
        self.active_connections[room].remove(websocket)
    
    async def broadcast(self, message: str, room: str):
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                await connection.send_text(message)

manager = ConnectionManager()

@websocket("/ws/chat/{room}")
async def chat_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    
    try:
        async for message in websocket.iter_text():
            await manager.broadcast(f"Message: {message}", room)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, room)
```

---

## 🗃️ ORM & Models

### Base Model

```python
from covet.orm import Model, fields
from datetime import datetime

class BaseModel(Model):
    """Base model with common fields"""
    id = fields.Integer(primary_key=True)
    created_at = fields.DateTime(default=datetime.utcnow)
    updated_at = fields.DateTime(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    class Meta:
        abstract = True
```

### Field Types

```python
class User(Model):
    # Numeric fields
    id = fields.Integer(primary_key=True)
    age = fields.Integer(nullable=True, default=0)
    score = fields.Float(default=0.0)
    balance = fields.Decimal(max_digits=10, decimal_places=2)
    
    # String fields  
    username = fields.String(max_length=50, unique=True, index=True)
    email = fields.String(max_length=255, unique=True)
    bio = fields.Text(nullable=True)
    
    # Boolean fields
    is_active = fields.Boolean(default=True)
    is_verified = fields.Boolean(default=False)
    
    # Date/time fields
    created_at = fields.DateTime(auto_now_add=True)
    updated_at = fields.DateTime(auto_now=True)
    last_login = fields.Date(nullable=True)
    
    # JSON fields
    metadata = fields.JSON(default=dict)
    tags = fields.JSON(default=list)
    
    # Choice fields
    status = fields.Enum(UserStatus, default=UserStatus.ACTIVE)
    
    # Binary fields
    avatar = fields.Binary(nullable=True)
    
    class Meta:
        table_name = "users"
        indexes = [
            ("username",),
            ("email",),  
            ("created_at", "status"),
        ]
```

### Relationships

```python
class User(Model):
    id = fields.Integer(primary_key=True)
    username = fields.String(max_length=50)
    posts = fields.OneToMany("Post", back_populates="author")

class Post(Model):
    id = fields.Integer(primary_key=True) 
    title = fields.String(max_length=200)
    author_id = fields.Integer(foreign_key="users.id")
    author = fields.ManyToOne("User", back_populates="posts")
    categories = fields.ManyToMany("Category", through="post_categories")

class Category(Model):
    id = fields.Integer(primary_key=True)
    name = fields.String(max_length=100)
    posts = fields.ManyToMany("Post", through="post_categories")
```

### Query API

```python
# Basic queries
users = await User.all()
user = await User.get(id=1)
user = await User.first()

# Filtering
active_users = await User.filter(is_active=True).all()
recent_users = await User.filter(created_at__gte=datetime(2023, 1, 1)).all()

# Complex queries
users = await User.query()\
    .filter(is_active=True)\
    .filter(age__gte=18)\
    .order_by("-created_at")\
    .limit(10)\
    .all()

# Relationships
user_with_posts = await User.get(id=1).prefetch_related("posts")
posts_with_authors = await Post.query()\
    .select_related("author")\
    .filter(author__is_active=True)\
    .all()

# Aggregations
user_count = await User.filter(is_active=True).count()
avg_age = await User.aggregate(avg_age=Avg("age"))
stats = await User.aggregate(
    total=Count("id"),
    active=Count("id", filter=Q(is_active=True)),
    avg_age=Avg("age")
)
```

### Model Methods

```python
class User(Model):
    username = fields.String(max_length=50)
    email = fields.String(max_length=255)
    password_hash = fields.String(max_length=255)
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return verify_password(password, self.password_hash)
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    async def authenticate(cls, username: str, password: str) -> Optional["User"]:
        """Authenticate user"""
        user = await cls.filter(username=username, is_active=True).first()
        if user and user.verify_password(password):
            return user
        return None
    
    async def get_posts(self, limit: int = 10):
        """Get user's posts"""
        return await Post.filter(author_id=self.id)\
            .order_by("-created_at")\
            .limit(limit)\
            .all()
```

---

## 🔧 Database

### Database Configuration

```python
from covet.database import Database, DatabaseConfig

config = DatabaseConfig(
    url="postgresql://user:pass@localhost/db",
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    echo=False  # SQL logging
)

db = Database(config)
```

### Database Operations

```python
# Raw SQL queries
result = await db.execute("SELECT * FROM users WHERE age > :age", {"age": 18})
users = await db.fetch_all("SELECT id, username FROM users LIMIT 10")
user = await db.fetch_one("SELECT * FROM users WHERE id = :id", {"id": 1})

# Transactions
async with db.transaction():
    user = await User.create(username="john", email="john@example.com")
    profile = await Profile.create(user_id=user.id, bio="Hello world")
    # Automatic rollback on exception

# Connection pooling
async with db.connection() as conn:
    result = await conn.execute("SELECT 1")
```

### Migration System

```python
# Create migration
covet makemigration --name create_users_table

# Generated migration
class Migration:
    async def upgrade(self):
        await self.create_table(
            "users",
            self.integer("id", primary_key=True),
            self.string("username", max_length=50, unique=True),
            self.string("email", max_length=255, unique=True),
            self.datetime("created_at", default=self.now())
        )
        
        await self.create_index("idx_users_username", "users", ["username"])
    
    async def downgrade(self):
        await self.drop_table("users")

# Run migrations
covet migrate
covet migrate --rollback
```

---

## 🔐 Authentication

### JWT Authentication

```python
from covet.auth import JWTAuth, jwt_required, get_current_user

# Configure JWT
jwt_auth = JWTAuth(
    secret_key="your-secret-key",
    algorithm="HS256",
    expire_minutes=30
)

# Login endpoint
@post("/auth/login")
async def login(credentials: LoginRequest):
    user = await User.authenticate(credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    token = jwt_auth.create_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return {"access_token": token, "token_type": "bearer"}

# Protected endpoint
@get("/auth/me")
@jwt_required
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

# Role-based access
@delete("/admin/users/{user_id}")
@jwt_required(roles=["admin"])
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(403, "Admin access required")
    
    user = await User.get(user_id)
    await user.delete()
    return {"message": "User deleted"}
```

### OAuth2 Integration

```python
from covet.auth.oauth2 import OAuth2Provider

oauth2 = OAuth2Provider(app)

oauth2.register(
    "google",
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    client_kwargs={"scope": "openid email profile"}
)

@get("/auth/google")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth2.google.authorize_redirect(request, redirect_uri)

@get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth2.google.authorize_access_token(request)
    user_info = await oauth2.google.get("userinfo", token=token)
    
    # Create or update user
    user = await User.get_or_create(
        email=user_info["email"],
        defaults={
            "username": user_info["name"],
            "avatar_url": user_info.get("picture")
        }
    )
    
    # Create session
    access_token = jwt_auth.create_token(data={"sub": str(user.id)})
    return {"access_token": access_token}
```

---

## 🚀 Performance

### Caching

```python
from covet.cache import cache, Cache
from datetime import timedelta

# Configure cache
cache.init(
    backend="redis://localhost:6379",
    default_ttl=timedelta(minutes=5)
)

# Cache decorator
@cache(ttl=timedelta(hours=1))
async def get_expensive_data(param: str):
    # Expensive operation
    await asyncio.sleep(2)
    return f"Result for {param}"

# Manual caching
@get("/data/{key}")
async def get_data(key: str):
    # Try cache first
    cached = await cache.get(f"data:{key}")
    if cached:
        return cached
    
    # Compute and cache
    result = await compute_data(key)
    await cache.set(f"data:{key}", result, ttl=300)
    
    return result

# Cache invalidation
await cache.delete("data:key")
await cache.clear_pattern("user:*")
```

### Rate Limiting

```python
from covet.middleware import RateLimitMiddleware

# Global rate limiting
app.add_middleware(
    RateLimitMiddleware,
    calls=1000,
    period=3600,  # 1000 calls per hour
    key_func=lambda request: request.client.host
)

# Per-endpoint rate limiting
@get("/api/search")
@rate_limit("10/minute")
async def search(q: str):
    return await perform_search(q)

# Custom rate limit key
@post("/api/upload")
@rate_limit("5/hour", key_func=lambda request: request.user.id)
async def upload_file(file: UploadFile, user: User = Depends(get_current_user)):
    return await process_upload(file, user)
```

### Background Tasks

```python
from covet.tasks import BackgroundTask, background_task

@post("/send-email")
async def send_notification(
    email: str,
    background_tasks: BackgroundTask
):
    # Return immediately
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Email will be sent"}

@background_task
async def send_email(email: str, subject: str):
    """This runs in the background"""
    await email_service.send(email, subject)

# Scheduled tasks
@background_task(schedule="0 9 * * *")  # Daily at 9 AM
async def daily_report():
    """Generate daily report"""
    report = await generate_report()
    await send_report(report)
```

---

## 🧪 Testing

### Test Client

```python
from covet.testing import TestClient
import pytest

@pytest.fixture
def client():
    return TestClient(app)

def test_get_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_user(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com"
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "testuser"
```

### Async Testing

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users/1")
        assert response.status_code == 200

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_with_fixture(async_client):
    response = await async_client.post("/users", json={"username": "test"})
    assert response.status_code == 201
```

### Database Testing

```python
from covet.testing import DatabaseTest

class TestUserModel(DatabaseTest):
    """Test with automatic database setup/teardown"""
    
    async def test_create_user(self):
        user = await User.create(
            username="testuser",
            email="test@example.com"
        )
        
        assert user.id is not None
        assert user.username == "testuser"
    
    async def test_user_authentication(self):
        user = await User.create(
            username="testuser",
            email="test@example.com"
        )
        user.set_password("testpass")
        await user.save()
        
        authenticated = await User.authenticate("testuser", "testpass")
        assert authenticated is not None
        assert authenticated.id == user.id
```

---

## 🔧 CLI

### Command Line Interface

```bash
# Project management
covet new my-project                    # Create new project
covet new my-project --template=api     # Create from template
covet init                              # Initialize in existing directory

# Development
covet dev                               # Run development server
covet dev --host 0.0.0.0 --port 8080  # Custom host/port
covet dev --reload                      # Auto-reload on changes

# Database
covet makemigration --name create_users # Create migration
covet migrate                           # Apply migrations
covet migrate --rollback                # Rollback migration
covet showmigrations                    # Show migration history

# Testing
covet test                              # Run tests
covet test --coverage                   # Run with coverage
covet test --parallel                   # Parallel execution

# Production
covet build                             # Build Docker image
covet serve                             # Run production server
covet serve --workers 4                # Multi-worker

# Utilities
covet shell                             # Interactive shell
covet config show                       # Show configuration
covet benchmark                         # Performance benchmark
```

### Custom Commands

```python
from covet.cli import cli, command

@command("hello")
def hello_command(name: str = "World"):
    """Say hello"""
    print(f"Hello, {name}!")

@command("users:create")
async def create_user_command(username: str, email: str):
    """Create a new user"""
    user = await User.create(username=username, email=email)
    print(f"Created user: {user.id}")

# Usage:
# covet hello --name "CovetPy"
# covet users:create --username admin --email admin@example.com
```

---

## 📊 Monitoring & Observability

### Metrics Collection

```python
from covet.monitoring import metrics, Counter, Histogram, Gauge

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration'
)

active_connections = Gauge(
    'websocket_connections_active',
    'Active WebSocket connections'
)

# Use in code
@get("/users")
async def list_users():
    request_count.labels(method="GET", endpoint="/users", status="200").inc()
    
    with request_duration.time():
        users = await User.all()
    
    return users

# Expose metrics
@get("/metrics")
async def metrics_endpoint():
    return metrics.generate_latest()
```

### Structured Logging

```python
from covet.logging import get_logger, log_performance

logger = get_logger("my_service")

@get("/users/{user_id}")
@log_performance()
async def get_user(user_id: int):
    logger.info("Fetching user", user_id=user_id)
    
    try:
        user = await User.get(user_id)
        logger.info("User found", user_id=user_id, username=user.username)
        return user
    except Exception as e:
        logger.error("Failed to fetch user", user_id=user_id, error=str(e))
        raise
```

---

## 🔧 Advanced Features

### Custom Middleware

```python
from covet.middleware import BaseMiddleware
from covet import Request, Response

class CustomMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, call_next):
        # Pre-processing
        start_time = time.time()
        
        # Add custom header
        request.state.custom_data = "middleware_value"
        
        # Process request
        response = await call_next(request)
        
        # Post-processing
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

# Register middleware
app.add_middleware(CustomMiddleware)
```

### Plugin System

```python
from covet.plugins import Plugin, PluginMetadata

class MyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="Example plugin",
            author="Your Name"
        )
    
    async def install(self, app, container):
        """Install plugin"""
        # Register services
        container.register_singleton(MyService)
        
        # Add routes
        router = APIRouter()
        
        @router.get("/plugin-endpoint")
        async def plugin_endpoint():
            return {"plugin": "active"}
        
        app.include_router(router, prefix="/plugins")
    
    async def activate(self, app, container):
        """Activate plugin"""
        self.logger.info("Plugin activated")
    
    async def deactivate(self, app, container):
        """Deactivate plugin"""
        self.logger.info("Plugin deactivated")

# Load plugin
app.plugins.load(MyPlugin())
```

### Custom Serializers

```python
from covet.serialization import Serializer

class CustomJSONSerializer(Serializer):
    media_type = "application/json"
    
    def serialize(self, data: Any) -> bytes:
        """Custom serialization logic"""
        return json.dumps(data, cls=CustomEncoder).encode()
    
    def deserialize(self, data: bytes) -> Any:
        """Custom deserialization logic"""
        return json.loads(data.decode())

# Register serializer
app.serializers.register(CustomJSONSerializer())
```

---

## 🎯 Best Practices

### Error Handling

```python
from covet.exceptions import HTTPException, CovetPyError

class UserNotFoundError(CovetPyError):
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User {user_id} not found",
            error_code="USER_NOT_FOUND",
            context={"user_id": user_id}
        )

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "context": exc.context
        }
    )

@get("/users/{user_id}")
async def get_user(user_id: int):
    user = await User.get(user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return user
```

### Validation

```python
from pydantic import BaseModel, validator, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=13, le=120)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
    
    @validator('password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

@post("/users")
async def create_user(user: UserCreate):
    """Automatic validation before this function runs"""
    return await User.create(**user.dict())
```

---

This completes the comprehensive API reference for CovetPy. Each section provides practical examples and covers the most common use cases you'll encounter when building high-performance applications.

**For more detailed information, visit our [complete documentation](https://docs.covetpy.dev) or explore the [interactive examples](https://examples.covetpy.dev).**