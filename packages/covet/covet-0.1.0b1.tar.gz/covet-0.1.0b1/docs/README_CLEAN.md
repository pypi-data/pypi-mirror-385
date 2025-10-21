# CovetPy Framework (NeutrinoPy)

A lightweight Python web framework with Flask-like simplicity and Django-like ORM.

## Quick Start

```python
from covet import Covet
from covet.orm import Database, Model, CharField

app = Covet()
db = Database('app.db')

class User(Model):
    username = CharField(max_length=100)

@app.get('/')
async def home(request):
    return {'message': 'Hello World'}

@app.get('/users')
async def users(request):
    all_users = User.objects.all()
    return {'users': [u.username for u in all_users]}

app.run()
```

## Installation

```bash
# Development
git clone https://github.com/covetpy/covet
cd covet
pip install -e .

# Production (Coming Week 16)
pip install covet
```

## Features

- ✅ ASGI 3.0 compliant HTTP server
- ✅ Flask-like routing decorators
- ✅ Django-like ORM with relationships
- ✅ JWT authentication with bcrypt
- ✅ Middleware pipeline (CORS, Sessions, Auth)
- ✅ Database migrations
- ✅ SQLite, MySQL, PostgreSQL support

## Status

- **Version**: 0.1.0-alpha
- **Test Coverage**: 90%
- **Production Ready**: Alpha (use with caution)

## Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [API Reference](docs/API_DOCUMENTATION_GUIDE.md)
- [Database Guide](docs/DATABASE_QUICK_START.md)
- [Examples](examples/)

## Contributing

The framework is in alpha. Contributions welcome!

## License

MIT

---
Created by vipin08 - October 2025