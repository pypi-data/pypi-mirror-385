# CovetPy Framework - Getting Started Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Your First API](#your-first-api)
4. [Database Integration](#database-integration)
5. [Authentication](#authentication)
6. [Deployment](#deployment)
7. [Tutorials](#tutorials)
8. [Common Patterns](#common-patterns)

## Installation

### Requirements

- Python 3.8 or higher
- pip or conda
- (Optional) Rust toolchain for custom extensions

### Install from PyPI

```bash
# Basic installation
pip install covetpy

# With all optional dependencies
pip install "covetpy[all]"

# Specific extras
pip install "covetpy[postgres,redis,aws]"
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/covetpy/covetpy.git
cd covetpy

# Install in development mode
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Check version
covet --version

# Run development server
covet dev

# View available commands
covet --help
```

## Quick Start

### Hello World

Create a file named `app.py`:

```python
from covet import CovetPy

app = CovetPy()

@app.get("/")
async def hello():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()
```

Run the application:

```bash
python app.py
# Or use the CLI
covet run app:app
```

Visit http://localhost:8000 to see your API in action!

### Interactive API Documentation

CovetPy automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## Your First API

### Building a TODO API

Let's build a complete TODO API with CRUD operations:

```python
from covet import CovetPy, Request, Response
from covet.orm import Model, fields
from covet.validation import BaseModel
from typing import List, Optional
from datetime import datetime

app = CovetPy()

# Database model
class Todo(Model):
    id = fields.Integer(primary_key=True)
    title = fields.String(max_length=200)
    description = fields.Text(nullable=True)
    completed = fields.Boolean(default=False)
    created_at = fields.DateTime(auto_now_add=True)
    updated_at = fields.DateTime(auto_now=True)

# Pydantic models for validation
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

# Routes
@app.get("/todos", response_model=List[TodoResponse])
async def list_todos(
    limit: int = 10,
    offset: int = 0,
    completed: Optional[bool] = None
):
    """List all todos with pagination and filtering"""
    query = Todo.query()
    
    if completed is not None:
        query = query.filter(completed=completed)
    
    todos = await query.offset(offset).limit(limit).all()
    return todos

@app.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(todo: TodoCreate):
    """Create a new todo"""
    new_todo = Todo(**todo.dict())
    await new_todo.save()
    return new_todo

@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    """Get a specific todo by ID"""
    todo = await Todo.get(id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update a todo"""
    todo = await Todo.get(id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    for field, value in todo_update.dict(exclude_unset=True).items():
        setattr(todo, field, value)
    
    await todo.save()
    return todo

@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: int):
    """Delete a todo"""
    todo = await Todo.get(id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    await todo.delete()
    return Response(status_code=204)

# Run migrations on startup
@app.on_event("startup")
async def startup():
    await app.db.create_tables()

if __name__ == "__main__":
    app.run(debug=True)
```

### Testing the API

```bash
# Create a todo
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn CovetPy", "description": "Build amazing APIs"}'

# List todos
curl http://localhost:8000/todos

# Get specific todo
curl http://localhost:8000/todos/1

# Update todo
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete todo
curl -X DELETE http://localhost:8000/todos/1
```

## Database Integration

### PostgreSQL Setup

```python
from covet import CovetPy
from covet.db import Database

app = CovetPy()

# Configure database
app.config.database_url = "postgresql://user:pass@localhost/mydb"

# Or use environment variable
# export DATABASE_URL=postgresql://user:pass@localhost/mydb

# Initialize database
@app.on_event("startup")
async def init_db():
    await app.db.connect()
    # Create tables if they don't exist
    await app.db.create_tables()

@app.on_event("shutdown")
async def close_db():
    await app.db.disconnect()
```

### Model Relationships

```python
from covet.orm import Model, fields

class User(Model):
    id = fields.Integer(primary_key=True)
    username = fields.String(unique=True, max_length=50)
    email = fields.String(unique=True, max_length=255)
    posts = fields.OneToMany("Post", back_populates="author")

class Post(Model):
    id = fields.Integer(primary_key=True)
    title = fields.String(max_length=200)
    content = fields.Text()
    author_id = fields.Integer(foreign_key="users.id")
    author = fields.ManyToOne("User", back_populates="posts")
    tags = fields.ManyToMany("Tag", through="post_tags")

class Tag(Model):
    id = fields.Integer(primary_key=True)
    name = fields.String(unique=True, max_length=50)
    posts = fields.ManyToMany("Post", through="post_tags")

# Usage example
@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int):
    user = await User.get(id=user_id).prefetch_related("posts")
    if not user:
        raise HTTPException(404, "User not found")
    
    return {
        "user": user.username,
        "posts": [
            {"id": p.id, "title": p.title}
            for p in user.posts
        ]
    }
```

### Migrations

```bash
# Create a new migration
covet makemigration --name add_user_table

# Apply migrations
covet migrate

# Rollback migration
covet migrate --rollback

# View migration history
covet showmigrations
```

## Authentication

### JWT Authentication

```python
from covet import CovetPy, Security
from covet.auth import JWTAuth, get_current_user
from datetime import timedelta

app = CovetPy()

# Configure JWT
jwt_auth = JWTAuth(
    secret_key="your-secret-key",
    algorithm="HS256",
    expire_minutes=30
)

# User model
class User(Model):
    id = fields.Integer(primary_key=True)
    username = fields.String(unique=True)
    password_hash = fields.String()
    is_active = fields.Boolean(default=True)

# Login endpoint
@app.post("/auth/login")
async def login(username: str, password: str):
    user = await User.get(username=username)
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    
    # Create JWT token
    token = jwt_auth.create_token(
        data={"sub": user.id, "username": user.username}
    )
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

# Protected endpoint
@app.get("/auth/me")
async def get_current_user_info(
    current_user: User = Security(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username
    }

# Role-based access
@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    if "admin" not in current_user.roles:
        raise HTTPException(403, "Insufficient permissions")
    
    user = await User.get(id=user_id)
    await user.delete()
    return {"message": "User deleted"}
```

### OAuth2 Integration

```python
from covet.auth.oauth2 import OAuth2Provider

# Configure OAuth2 providers
oauth2 = OAuth2Provider(app)

oauth2.register(
    "google",
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    client_kwargs={"scope": "openid email profile"}
)

@app.get("/auth/google")
async def google_login():
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth2.google.authorize_redirect(redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth2.google.authorize_access_token()
    user_info = await oauth2.google.get("userinfo")
    
    # Create or update user
    user = await User.get_or_create(
        email=user_info["email"],
        defaults={"username": user_info["name"]}
    )
    
    # Create session
    jwt_token = jwt_auth.create_token(data={"sub": user.id})
    
    return {"access_token": jwt_token}
```

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the application
CMD ["covet", "run", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://db/myapp \
  myapp:latest
```

### Production Configuration

```python
# production.py
from covet import CovetPy
from covet.config import ProductionConfig

class MyProductionConfig(ProductionConfig):
    # Security
    SECRET_KEY = env("SECRET_KEY")
    ALLOWED_HOSTS = env("ALLOWED_HOSTS", cast=list)
    
    # Database
    DATABASE_URL = env("DATABASE_URL")
    DATABASE_POOL_SIZE = 50
    
    # Performance
    WORKERS = env("WORKERS", default=4, cast=int)
    WORKER_CONNECTIONS = 1000
    
    # Monitoring
    SENTRY_DSN = env("SENTRY_DSN", default=None)
    PROMETHEUS_ENABLED = True

app = CovetPy(config=MyProductionConfig)

# Production middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CompressionMiddleware)
app.add_middleware(PrometheusMiddleware)

# Health checks
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    try:
        await app.db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        return {"status": "not ready"}, 503
```

### Deployment Script

```bash
#!/bin/bash
# deploy.sh

# Build and push Docker image
docker build -t myapp:latest .
docker tag myapp:latest registry.example.com/myapp:latest
docker push registry.example.com/myapp:latest

# Deploy to Kubernetes
kubectl apply -f k8s/
kubectl rollout status deployment/myapp

# Run migrations
kubectl exec -it deployment/myapp -- covet migrate

# Verify deployment
curl https://api.example.com/health
```

## Tutorials

### Tutorial 1: Building a Blog API

```python
# Complete blog API with posts, comments, and categories
# See tutorials/blog_api.py for full implementation

from covet import CovetPy
from datetime import datetime

app = CovetPy()

# Models
class Category(Model):
    id = fields.Integer(primary_key=True)
    name = fields.String(unique=True)
    slug = fields.String(unique=True)

class Post(Model):
    id = fields.Integer(primary_key=True)
    title = fields.String(max_length=200)
    slug = fields.String(unique=True)
    content = fields.Text()
    published = fields.Boolean(default=False)
    category_id = fields.Integer(foreign_key="categories.id")
    author_id = fields.Integer(foreign_key="users.id")
    created_at = fields.DateTime(auto_now_add=True)
    
    category = fields.ManyToOne("Category")
    author = fields.ManyToOne("User")
    comments = fields.OneToMany("Comment")

# API endpoints
@app.get("/posts", response_model=List[PostResponse])
async def list_posts(
    category: Optional[str] = None,
    published: bool = True,
    limit: int = 10,
    offset: int = 0
):
    query = Post.query().filter(published=published)
    
    if category:
        query = query.join(Category).filter(Category.slug == category)
    
    posts = await query.order_by("-created_at")\
        .offset(offset).limit(limit).all()
    
    return posts

@app.get("/posts/{slug}")
async def get_post(slug: str):
    post = await Post.get(slug=slug, published=True)\
        .prefetch_related("author", "category", "comments")
    
    if not post:
        raise HTTPException(404, "Post not found")
    
    return post
```

### Tutorial 2: Real-time Chat Application

```python
# WebSocket-based chat application
# See tutorials/chat_app.py for full implementation

from covet import CovetPy, WebSocket
from covet.pubsub import RedisPubSub

app = CovetPy()
pubsub = RedisPubSub("redis://localhost")

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
    
    async def disconnect(self, websocket: WebSocket, room: str):
        self.active_connections[room].remove(websocket)
        if not self.active_connections[room]:
            del self.active_connections[room]
    
    async def broadcast(self, message: str, room: str):
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    
    # Subscribe to room messages
    await pubsub.subscribe(f"chat:{room}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Broadcast to room
            await pubsub.publish(f"chat:{room}", {
                "message": data,
                "room": room,
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        await manager.disconnect(websocket, room)
        await pubsub.unsubscribe(f"chat:{room}")
```

### Tutorial 3: File Upload Service

```python
# File upload with streaming and progress tracking
# See tutorials/file_upload.py for full implementation

from covet import CovetPy, UploadFile, File
from covet.responses import StreamingResponse
import aiofiles

app = CovetPy()

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    chunk_size: int = 1024 * 1024  # 1MB chunks
):
    """Upload file with streaming"""
    file_id = generate_file_id()
    file_path = f"uploads/{file_id}_{file.filename}"
    
    async with aiofiles.open(file_path, "wb") as f:
        total_size = 0
        async for chunk in file.stream(chunk_size):
            await f.write(chunk)
            total_size += len(chunk)
            
            # Update progress
            await pubsub.publish(f"upload:{file_id}", {
                "progress": total_size,
                "filename": file.filename
            })
    
    return {
        "file_id": file_id,
        "filename": file.filename,
        "size": total_size
    }

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """Stream file download"""
    file_path = get_file_path(file_id)
    
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    
    async def stream_file():
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(1024 * 1024):
                yield chunk
    
    return StreamingResponse(
        stream_file(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
```

## Common Patterns

### Dependency Injection

```python
from covet import Depends

# Database session dependency
async def get_db():
    async with app.db.session() as session:
        yield session

# Current user dependency
async def get_current_user(
    token: str = Header(..., alias="Authorization"),
    db = Depends(get_db)
):
    user_id = jwt_auth.decode_token(token)["sub"]
    user = await db.get(User, user_id)
    
    if not user:
        raise HTTPException(401, "Invalid token")
    
    return user

# Use in endpoint
@app.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    return {"user": current_user.username}
```

### Background Tasks

```python
from covet import BackgroundTasks

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    # Return immediately
    background_tasks.add_task(send_email, email)
    return {"message": "Notification will be sent"}

async def send_email(email: str):
    """This runs in the background"""
    await asyncio.sleep(1)  # Simulate email sending
    print(f"Email sent to {email}")
```

### Caching

```python
from covet.cache import cache, Cache
from datetime import timedelta

# Configure cache
cache.init(
    backend="redis://localhost",
    default_ttl=timedelta(minutes=5)
)

# Cache decorator
@cache(ttl=timedelta(hours=1))
async def expensive_operation(param: str):
    await asyncio.sleep(5)  # Simulate expensive operation
    return f"Result for {param}"

# Manual cache usage
@app.get("/data/{key}")
async def get_data(key: str):
    # Try cache first
    cached = await cache.get(f"data:{key}")
    if cached:
        return cached
    
    # Compute and cache
    result = await compute_data(key)
    await cache.set(f"data:{key}", result, ttl=300)
    
    return result
```

### Rate Limiting

```python
from covet.ratelimit import RateLimiter

# Configure rate limiter
rate_limiter = RateLimiter(
    backend="redis://localhost",
    default_limit="100/hour"
)

# Apply to endpoint
@app.get("/api/search")
@rate_limiter.limit("10/minute")
async def search(q: str):
    results = await perform_search(q)
    return results

# Custom rate limit key
@app.post("/api/expensive")
@rate_limiter.limit(
    "5/hour",
    key_func=lambda request: request.client.host
)
async def expensive_operation(data: dict):
    result = await process_data(data)
    return result
```

### Error Handling

```python
from covet.exceptions import HTTPException, ValidationError

# Custom exception handler
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors()
        }
    )

# Global error handler
@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    
    if app.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc),
                "type": type(exc).__name__
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

## Next Steps

1. **Explore the API Reference**: Deep dive into all available features
2. **Check out Examples**: See real-world applications built with CovetPy
3. **Join the Community**: Get help and share your projects
4. **Contribute**: Help make CovetPy even better

### Resources

- [API Reference](/docs/api)
- [Examples Repository](https://github.com/covet-framework/examples)
- [Community Discord](https://discord.gg/covet)
- [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/covet)

Happy coding with CovetPy! 🚀