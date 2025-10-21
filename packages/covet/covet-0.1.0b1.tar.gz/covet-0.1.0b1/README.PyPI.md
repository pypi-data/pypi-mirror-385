# CovetPy - High-Performance Python Web Framework

[![Python versions](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)]()
[![Status](https://img.shields.io/badge/status-BETA-orange)]()

**CovetPy** is a high-performance Python web framework with Rust-optimized components, designed for building modern async applications with exceptional speed and developer experience.

---

## 🚀 Key Features

### Performance
- **Rust-Optimized Routing:** 10-13% performance improvement over pure Python
- **Async/Await First:** Built on ASGI 3.0 for maximum concurrency
- **Zero-Copy Operations:** Efficient memory usage with Rust extensions
- **Production-Ready:** Battle-tested components for high-traffic applications

### Full-Stack Capabilities
- **REST API:** Fast HTTP request/response handling with Pydantic validation
- **GraphQL:** Powered by Strawberry GraphQL for modern API development
- **WebSocket:** Real-time bidirectional communication with room management
- **Database ORM:** Full-featured ORM with migrations for PostgreSQL, MySQL, SQLite
- **Authentication:** JWT tokens, password hashing, MFA support
- **Caching:** Redis and in-memory caching for optimal performance

### Developer Experience
- **Type-Safe:** Comprehensive type hints for excellent IDE support
- **Modern Python:** Uses latest Python 3.9+ features
- **Clean API:** Intuitive, Flask-inspired interface
- **Well-Documented:** Extensive documentation and examples

---

## 📦 Installation

### Quick Install

```bash
# Minimal installation
pip install covet
```

## ⚡ Quick Start

### Hello World (30 seconds)

```python
from covet import CovetPy

# Create application
app = CovetPy()

# Define routes
@app.route("/")
async def hello(request):
    return {"message": "Hello, CovetPy!"}

@app.route("/users/{user_id}")
async def get_user(request, user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}

# Run server
if __name__ == "__main__":
    app.run()  # Runs on http://localhost:8000
```

### Database Integration

```python
from covet.database import DatabaseManager, PostgreSQLAdapter
from covet.database.orm import Model, Field

# Setup database
adapter = PostgreSQLAdapter(
    host='localhost',
    database='myapp',
    user='postgres',
    password='secret'
)
db = DatabaseManager(adapter)
await db.connect()

# Define models
class User(Model):
    __tablename__ = 'users'

    id = Field(int, primary_key=True, auto_increment=True)
    email = Field(str, unique=True, max_length=255)
    name = Field(str, max_length=100)
    created_at = Field('datetime', auto_now_add=True)

# Use ORM
user = await User.create(
    email='alice@example.com',
    name='Alice'
)

# Query
all_users = await User.all()
alice = await User.get(email='alice@example.com')
```

### REST API with Validation

```python
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

@app.route("/api/users", methods=["POST"])
async def create_user(request):
    data = await request.json()

    # Validate with Pydantic
    user_data = CreateUserRequest(**data)

    # Save to database
    user = await User.create(**user_data.dict())

    return {"id": user.id, "email": user.email}
```

### JWT Authentication

```python
from covet.security.jwt_auth import JWTAuthenticator, JWTConfig, TokenType

# Setup JWT
jwt_config = JWTConfig(
    secret_key='your-secret-key-min-32-chars',
    algorithm='HS256',
    access_token_expire_minutes=30
)
jwt_auth = JWTAuthenticator(jwt_config)

# Login endpoint
@app.route("/login", methods=["POST"])
async def login(request):
    data = await request.json()

    # Verify credentials (your logic)
    user_id = "user_123"

    # Create access token
    token = jwt_auth.create_token(user_id, TokenType.ACCESS)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# Protected route
@app.route("/profile")
async def profile(request):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]

    claims = jwt_auth.verify_token(token)
    user_id = claims['sub']

    return {"user_id": user_id}
```

### WebSocket Real-Time Communication

```python
from covet.websocket import WebSocketManager

ws_manager = WebSocketManager()

@app.websocket("/ws/chat/{room_id}")
async def chat_room(websocket, room_id: str):
    await ws_manager.connect(websocket, room_id)

    try:
        while True:
            message = await websocket.receive_json()
            await ws_manager.broadcast(room_id, message)
    except:
        await ws_manager.disconnect(websocket, room_id)
```

### GraphQL API

```python
from covet.api.graphql import GraphQLHandler
import strawberry

@strawberry.type
class User:
    id: int
    name: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        return [
            User(id=1, name="Alice", email="alice@example.com"),
            User(id=2, name="Bob", email="bob@example.com")
        ]

schema = strawberry.Schema(query=Query)

@app.route("/graphql", methods=["POST", "GET"])
async def graphql_endpoint(request):
    handler = GraphQLHandler(schema)
    return await handler.handle(request)
```

---

## 🎯 Performance

### Rust-Optimized Components

CovetPy includes Rust-optimized components that deliver measurable performance improvements:

**Benchmark Results:**
- Pure Python: 1,395 requests/sec
- Rust-Optimized: 1,576 requests/sec
- **Improvement: +13% throughput**

The Rust optimization is **enabled by default** - you get the performance boost automatically!

```python
from covet.core.fast_processor import ASGIApplication

# Rust optimization enabled by default
app = ASGIApplication()  # 13% faster

# Or disable for debugging
app = ASGIApplication(enable_rust=False)
```

---

## 🔧 System Requirements

- **Python:** 3.9, 3.10, 3.11, or 3.12
- **Operating Systems:** Linux, macOS, Windows
- **RAM:** Minimum 512MB, recommended 2GB
- **Disk:** 200MB for package + dependencies

---

## 📚 Feature Matrix

| Feature | Included | Install Extra |
|---------|----------|---------------|
| Core HTTP/ASGI | ✅ Always | - |
| Routing & Middleware | ✅ Always | - |
| Database (SQLite) | ✅ Always | - |
| PostgreSQL Support | ⚙️ Optional | `[database]` |
| MySQL Support | ⚙️ Optional | `[database]` |
| ORM with Migrations | ⚙️ Optional | `[orm]` |
| JWT Authentication | ⚙️ Optional | `[security]` |
| Password Hashing | ⚙️ Optional | `[security]` |
| MFA/TOTP | ⚙️ Optional | `[security]` |
| REST API | ⚙️ Optional | `[web]` |
| GraphQL | ⚙️ Optional | `[graphql]` |
| WebSocket | ✅ Always | - |
| Caching (Redis) | ⚙️ Optional | `[production]` |
| Monitoring | ⚙️ Optional | `[monitoring]` |
| Rust Optimization | ✅ Always | - |

---

## 🚀 Production Deployment

### Running with Uvicorn

```bash
# Install production dependencies
pip install covet[production]

# Run with Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn + Uvicorn workers
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Database Examples

**SQLite (Zero Configuration):**
```python
from covet.database import SQLiteAdapter

adapter = SQLiteAdapter(database_path='app.db')
```

**PostgreSQL:**
```python
from covet.database import PostgreSQLAdapter

adapter = PostgreSQLAdapter(
    host='localhost',
    port=5432,
    database='myapp',
    user='postgres',
    password='secret'
)
```

**MySQL:**
```python
from covet.database import MySQLAdapter

adapter = MySQLAdapter(
    host='localhost',
    port=3306,
    database='myapp',
    user='root',
    password='secret'
)
```

---

## ⚙️ Configuration

### Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
JWT_SECRET = os.getenv('JWT_SECRET_KEY')
REDIS_URL = os.getenv('REDIS_URL')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

### Application Configuration

```python
from covet import CovetPy
from covet.config import Config

config = Config(
    debug=False,
    host='0.0.0.0',
    port=8000,
    database_url='postgresql://user:pass@localhost/myapp',
    jwt_secret='your-secret-key',
    redis_url='redis://localhost:6379/0'
)

app = CovetPy(config=config)
```

---

## 🔒 Security Features

- **JWT Authentication:** Secure token-based auth with expiration
- **Password Hashing:** Bcrypt-based secure password storage
- **MFA/TOTP:** Two-factor authentication support
- **Input Validation:** Pydantic-powered request validation
- **CORS Middleware:** Configurable cross-origin resource sharing
- **Rate Limiting:** Protect against abuse and DDoS
- **SQL Injection Protection:** Parameterized queries
- **XSS Protection:** HTML sanitization

---

## 📊 Monitoring & Observability

```python
from covet.monitoring import MetricsCollector
from covet.monitoring.prometheus_exporter import PrometheusExporter

# Setup metrics
metrics = MetricsCollector()
exporter = PrometheusExporter(metrics)

# Metrics endpoint
@app.route("/metrics")
async def metrics_endpoint(request):
    return exporter.export()
```

---

## 🐛 Troubleshooting

### Common Issues

**Import Error:**
```bash
# Solution: Install package
pip install covet[full]
```

**Database Connection Error:**
```python
# Check connection parameters
adapter = PostgreSQLAdapter(
    host='localhost',  # Correct host?
    port=5432,        # Correct port?
    database='myapp', # Database exists?
    user='postgres',  # Valid user?
    password='secret' # Correct password?
)
```

**Rust Extensions Not Loading:**
```python
# Fallback to pure Python (works fine, slightly slower)
from covet import CovetPy
app = CovetPy()  # Automatically falls back if Rust unavailable
```

---

## 📄 License

**Proprietary License**

Copyright © 2025 Vipin Kumar. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 👤 Author

**Vipin Kumar**
- Email: vpnkumar.kumar1@gmail.com
- Website: https://covetpy.dev
- Documentation: https://github.com/vipin08/Covet-doc

---

## 🎯 Use Cases

**Perfect For:**
- High-performance REST APIs
- Real-time applications with WebSockets
- GraphQL backends
- Microservices architecture
- Full-stack web applications
- Data-intensive applications
- Enterprise backends

**Key Benefits:**
- Fast development with intuitive API
- Production-ready performance
- Comprehensive feature set
- Type-safe development
- Flexible deployment options

---

## 🚀 Get Started Now

```bash
# Install CovetPy
pip install covet[full]

# Create your first app
cat > app.py <<EOF
from covet import CovetPy

app = CovetPy()

@app.route("/")
async def hello(request):
    return {"message": "Hello, CovetPy!"}

if __name__ == "__main__":
    app.run()
EOF

# Run it
python app.py
```

Visit http://localhost:8000 and start building!

---

**CovetPy - Build fast, scalable Python applications with Rust-powered performance.**

**Version:** 0.1.0b1 (Beta)
**Status:** Production-Ready Core, Beta Features
