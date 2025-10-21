# Getting Started with CovetPy

**Last Updated:** 2025-10-10
**Difficulty:** Beginner
**Time Required:** 30 minutes

Welcome to CovetPy! This tutorial will get you up and running with your first CovetPy application in under 30 minutes.

## Table of Contents

- [What is CovetPy?](#what-is-covetpy)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Hello World](#hello-world)
- [Understanding the Basics](#understanding-the-basics)
- [Building a REST API](#building-a-rest-api)
- [Testing Your API](#testing-your-api)
- [Next Steps](#next-steps)

## What is CovetPy?

CovetPy is a modern, async-first Python web framework that provides:

- **High Performance**: Built on ASGI with async/await support
- **Enterprise Features**: ORM, caching, sessions, security
- **Production Ready**: Used in real-world applications
- **Developer Friendly**: Clean API inspired by Django and FastAPI
- **Fully Featured**: REST APIs, GraphQL, WebSockets, and more

## Prerequisites

Before starting, ensure you have:

- **Python 3.8+** installed
- Basic Python knowledge (functions, classes, async/await)
- A text editor or IDE (VS Code, PyCharm, etc.)
- Terminal/command line access

Check your Python version:

```bash
python --version  # Should show 3.8 or higher
```

## Installation

### Step 1: Create a Project Directory

```bash
mkdir my-covetpy-app
cd my-covetpy-app
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install CovetPy

```bash
# Install core framework
pip install covetpy

# Or with server support for development
pip install covetpy[server]

# Or with all features
pip install covetpy[full]
```

### Step 4: Verify Installation

```bash
python -c "import covet; print('CovetPy installed successfully!')"
```

## Hello World

Let's create your first CovetPy application!

### Create app.py

Create a file named `app.py`:

```python
from covet import CovetPy

# Create application instance
app = CovetPy()

# Define a route
@app.get("/")
async def hello():
    """Simple hello world endpoint."""
    return {"message": "Hello, CovetPy!"}

# Run the application
if __name__ == "__main__":
    # Built-in development server
    app.run(host="127.0.0.1", port=8000)
```

### Run Your Application

```bash
python app.py
```

You should see:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Test Your Application

Open your browser and visit: http://127.0.0.1:8000

You should see:

```json
{"message": "Hello, CovetPy!"}
```

Or use curl:

```bash
curl http://127.0.0.1:8000
```

Congratulations! You've created your first CovetPy application! 🎉

## Understanding the Basics

Let's break down what we just did:

### Application Instance

```python
from covet import CovetPy

app = CovetPy()
```

- `CovetPy()` creates an ASGI application instance
- The app handles HTTP requests, routing, middleware, and more
- You can customize it with configuration options

### Route Decorators

```python
@app.get("/")
async def hello():
    return {"message": "Hello, CovetPy!"}
```

- `@app.get("/")` registers a GET endpoint at the root path
- The function is `async` for better concurrency
- Return values are automatically converted to JSON

### HTTP Methods

CovetPy supports all standard HTTP methods:

```python
@app.get("/")      # GET requests
async def get_item():
    return {"method": "GET"}

@app.post("/")     # POST requests
async def create_item():
    return {"method": "POST"}

@app.put("/")      # PUT requests
async def update_item():
    return {"method": "PUT"}

@app.delete("/")   # DELETE requests
async def delete_item():
    return {"method": "DELETE"}

@app.patch("/")    # PATCH requests
async def patch_item():
    return {"method": "PATCH"}
```

### Path Parameters

Capture values from URLs:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID."""
    return {
        "user_id": user_id,
        "name": f"User {user_id}"
    }

# Test: http://127.0.0.1:8000/users/123
# Returns: {"user_id": 123, "name": "User 123"}
```

Type hints (`user_id: int`) automatically validate and convert parameters.

### Query Parameters

Access URL query strings:

```python
@app.get("/search")
async def search(request):
    """Search with query parameters."""
    query = request.query_params.get('q', '')
    limit = int(request.query_params.get('limit', 10))

    return {
        "query": query,
        "limit": limit,
        "results": []  # Your search logic here
    }

# Test: http://127.0.0.1:8000/search?q=python&limit=5
# Returns: {"query": "python", "limit": 5, "results": []}
```

### Request Object

Access the full request object:

```python
@app.post("/data")
async def receive_data(request):
    """Receive JSON data."""
    # Parse JSON body
    data = await request.json()

    # Access headers
    content_type = request.headers.get('Content-Type')

    # Access method
    method = request.method

    return {
        "received": data,
        "content_type": content_type,
        "method": method
    }
```

## Building a REST API

Let's build a simple Todo API with CRUD operations.

### Complete Todo API

Create `todo_app.py`:

```python
from covet import CovetPy
from typing import List, Optional
from dataclasses import dataclass, asdict
import json

# Create app
app = CovetPy()

# In-memory storage (replace with database in production)
todos = {}
todo_id_counter = 1

@dataclass
class Todo:
    """Todo item model."""
    id: int
    title: str
    completed: bool = False
    description: Optional[str] = None

# GET /todos - List all todos
@app.get("/todos")
async def list_todos():
    """Get all todos."""
    return {
        "todos": [asdict(todo) for todo in todos.values()],
        "count": len(todos)
    }

# POST /todos - Create a todo
@app.post("/todos")
async def create_todo(request):
    """Create a new todo."""
    global todo_id_counter

    # Parse request body
    data = await request.json()

    # Create todo
    todo = Todo(
        id=todo_id_counter,
        title=data.get('title'),
        description=data.get('description'),
        completed=data.get('completed', False)
    )

    # Store todo
    todos[todo_id_counter] = todo
    todo_id_counter += 1

    return {
        "message": "Todo created",
        "todo": asdict(todo)
    }

# GET /todos/{todo_id} - Get a specific todo
@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    """Get todo by ID."""
    if todo_id not in todos:
        return {
            "error": "Todo not found",
            "status": 404
        }, 404

    return {"todo": asdict(todos[todo_id])}

# PUT /todos/{todo_id} - Update a todo
@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, request):
    """Update a todo."""
    if todo_id not in todos:
        return {"error": "Todo not found"}, 404

    # Parse update data
    data = await request.json()

    # Update todo
    todo = todos[todo_id]
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']

    return {
        "message": "Todo updated",
        "todo": asdict(todo)
    }

# DELETE /todos/{todo_id} - Delete a todo
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a todo."""
    if todo_id not in todos:
        return {"error": "Todo not found"}, 404

    deleted_todo = todos.pop(todo_id)

    return {
        "message": "Todo deleted",
        "todo": asdict(deleted_todo)
    }

# Additional endpoints
@app.get("/todos/completed")
async def list_completed_todos():
    """Get all completed todos."""
    completed = [
        asdict(todo) for todo in todos.values()
        if todo.completed
    ]
    return {
        "todos": completed,
        "count": len(completed)
    }

@app.post("/todos/{todo_id}/complete")
async def complete_todo(todo_id: int):
    """Mark a todo as completed."""
    if todo_id not in todos:
        return {"error": "Todo not found"}, 404

    todos[todo_id].completed = True

    return {
        "message": "Todo marked as completed",
        "todo": asdict(todos[todo_id])
    }

# Run app
if __name__ == "__main__":
    print("Starting Todo API...")
    print("API Documentation:")
    print("  GET    /todos           - List all todos")
    print("  POST   /todos           - Create a todo")
    print("  GET    /todos/{id}      - Get a todo")
    print("  PUT    /todos/{id}      - Update a todo")
    print("  DELETE /todos/{id}      - Delete a todo")
    print("  GET    /todos/completed - List completed todos")
    print("  POST   /todos/{id}/complete - Complete a todo")
    print("\nServer running on http://127.0.0.1:8000")

    app.run(host="127.0.0.1", port=8000)
```

## Testing Your API

### Using curl

#### Create a todo:

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn CovetPy", "description": "Complete the getting started tutorial"}'
```

Response:
```json
{
  "message": "Todo created",
  "todo": {
    "id": 1,
    "title": "Learn CovetPy",
    "completed": false,
    "description": "Complete the getting started tutorial"
  }
}
```

#### List todos:

```bash
curl http://127.0.0.1:8000/todos
```

#### Get a specific todo:

```bash
curl http://127.0.0.1:8000/todos/1
```

#### Update a todo:

```bash
curl -X PUT http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

#### Delete a todo:

```bash
curl -X DELETE http://127.0.0.1:8000/todos/1
```

### Using Python requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Create a todo
response = requests.post(
    f"{BASE_URL}/todos",
    json={
        "title": "Learn CovetPy",
        "description": "Complete tutorial"
    }
)
print(response.json())

# List todos
response = requests.get(f"{BASE_URL}/todos")
print(response.json())

# Get a todo
response = requests.get(f"{BASE_URL}/todos/1")
print(response.json())

# Update a todo
response = requests.put(
    f"{BASE_URL}/todos/1",
    json={"completed": True}
)
print(response.json())

# Delete a todo
response = requests.delete(f"{BASE_URL}/todos/1")
print(response.json())
```

### Using httpie

```bash
# Install httpie
pip install httpie

# Create a todo
http POST http://127.0.0.1:8000/todos title="Learn CovetPy"

# List todos
http GET http://127.0.0.1:8000/todos

# Update a todo
http PUT http://127.0.0.1:8000/todos/1 completed=true

# Delete a todo
http DELETE http://127.0.0.1:8000/todos/1
```

## Next Steps

Congratulations! You've completed the CovetPy getting started tutorial. Here's what to explore next:

### 1. Database Integration (ORM Tutorial)

Learn how to use CovetPy's ORM for database operations:

```python
from covet.orm import Model, Field

class Todo(Model):
    title = Field.CharField(max_length=200)
    completed = Field.BooleanField(default=False)
    description = Field.TextField(blank=True)

# Create
todo = await Todo.objects.create(
    title="Learn ORM",
    description="Complete ORM tutorial"
)

# Query
todos = await Todo.objects.filter(completed=False).all()
```

Read: [ORM Tutorial](./02-orm-guide.md)

### 2. Caching

Add caching to improve performance:

```python
from covet.cache import cache_result

@cache_result(ttl=300)
async def get_todos():
    return await Todo.objects.all()
```

Read: [Caching Guide](./03-caching-guide.md)

### 3. Authentication & Security

Add user authentication and security:

```python
from covet.security import SimpleAuth, require_auth

auth = SimpleAuth("your-secret-key")

@app.get("/protected")
@require_auth(auth)
async def protected_route(request):
    return {"user": request.user.username}
```

Read: [Security Guide](./04-security-guide.md)

### 4. GraphQL API

Build a GraphQL API:

```python
from covet.api.graphql import GraphQLApp

graphql_app = GraphQLApp(schema)
app.mount("/graphql", graphql_app)
```

Read: [GraphQL Tutorial](./05-graphql-guide.md)

### 5. WebSockets

Add real-time functionality:

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    await websocket.send_json({"message": "Connected"})
```

### 6. Production Deployment

Deploy your application:

```bash
# Using Gunicorn + Uvicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t my-app .
docker run -p 8000:8000 my-app
```

Read: [Deployment Guides](../deployment/docker.md)

## Troubleshooting

### Port Already in Use

```bash
# Error: Address already in use
# Solution: Use a different port
app.run(host="127.0.0.1", port=8001)
```

### Module Not Found

```bash
# Error: ModuleNotFoundError: No module named 'covet'
# Solution: Make sure virtual environment is activated and CovetPy is installed
pip install covetpy
```

### Async/Await Errors

```bash
# Error: RuntimeError: This event loop is already running
# Solution: Use async functions consistently
# Don't mix sync and async incorrectly
```

### JSON Serialization Errors

```python
# Error: Object of type datetime is not JSON serializable
# Solution: Convert to string or use custom serializer

from datetime import datetime

@app.get("/time")
async def get_time():
    return {
        "time": datetime.now().isoformat()  # Convert to string
    }
```

## Tips & Best Practices

### 1. Use Async/Await Consistently

```python
# GOOD: Consistent async
@app.get("/data")
async def get_data():
    data = await fetch_from_db()
    return data

# AVOID: Mixing sync in async
@app.get("/data")
async def get_data():
    data = sync_blocking_call()  # Blocks event loop!
    return data
```

### 2. Handle Errors Gracefully

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        user = await User.objects.get(id=user_id)
        return {"user": user.to_dict()}
    except User.DoesNotExist:
        return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": "Internal server error"}, 500
```

### 3. Use Type Hints

```python
from typing import Optional

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    """Type hints help with validation and documentation."""
    user = await fetch_user(user_id)
    return {"user": user}
```

### 4. Organize Your Code

```python
# project/
# ├── app.py           # Main application
# ├── models.py        # Database models
# ├── routes/          # Route handlers
# │   ├── __init__.py
# │   ├── users.py
# │   └── todos.py
# ├── services/        # Business logic
# │   └── todo_service.py
# └── config.py        # Configuration
```

### 5. Use Environment Variables

```python
import os

# config.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

# app.py
from config import DATABASE_URL, SECRET_KEY, DEBUG

app = CovetPy(debug=DEBUG)
```

### 6. Add Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/data")
async def get_data():
    logger.info("Fetching data...")
    data = await fetch_data()
    logger.info(f"Fetched {len(data)} items")
    return {"data": data}
```

## Resources

### Documentation
- [API Reference](../api/orm.md)
- [ORM Guide](./02-orm-guide.md)
- [Caching Guide](./03-caching-guide.md)
- [Security Guide](./04-security-guide.md)
- [Deployment Guides](../deployment/docker.md)

### Example Applications
- [Blog API Example](../../examples/blog_api/)
- [E-commerce API Example](../../examples/ecommerce_api/)
- [Real-time Chat Example](../../examples/realtime_chat/)

### Community
- GitHub: https://github.com/covetpy/covetpy
- Documentation: https://docs.covetpy.com
- Issues: https://github.com/covetpy/covetpy/issues

## Summary

In this tutorial, you learned:

- ✅ How to install CovetPy
- ✅ Creating your first application
- ✅ Defining routes with decorators
- ✅ Handling path and query parameters
- ✅ Building a complete REST API
- ✅ Testing your API with curl and Python

You're now ready to build production-grade APIs with CovetPy!

Happy coding! 🚀
