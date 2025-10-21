# Installation Guide

**CovetPy Version:** 0.9.0-beta
**Status:** Educational/Beta - NOT for production
**Last Updated:** October 11, 2025

---

## ⚠️ Before You Install

**CovetPy is NOT production-ready.** This is an educational framework for learning:
- ASGI application architecture
- Async/await patterns in Python
- Basic ORM implementation
- Web framework internals

**For production applications, use:**
- **FastAPI** - https://fastapi.tiangolo.com/
- **Flask** - https://flask.palletsprojects.com/
- **Django** - https://www.djangoproject.com/

---

## Requirements

### System Requirements
- **Python:** 3.9 or higher
- **Operating System:** Any (Windows, macOS, Linux)
- **Database:** SQLite 3.35+ (included with Python)

### NOT Supported
- Python 3.8 or lower
- PostgreSQL (adapter is empty stub)
- MySQL (adapter is empty stub)
- MongoDB (not implemented)

---

## Installation from Source

CovetPy is **not published to PyPI**. You must install from source.

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourorg/covetpy.git
cd covetpy
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3.9 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Step 3: Install CovetPy

```bash
# Basic installation (core only)
pip install -e .

# With development tools (recommended for learning)
pip install -e ".[dev]"

# With documentation tools
pip install -e ".[docs]"

# With testing tools
pip install -e ".[test]"
```

### Step 4: Verify Installation

```bash
# Check installation
python -c "from covet import CovetPy; print('✅ CovetPy installed successfully')"

# Check version
python -c "from covet import __version__; print(f'Version: {__version__}')"
```

Expected output:
```
✅ CovetPy installed successfully
Version: 0.9.0-beta
```

---

## Optional Dependencies

### For Development

```bash
pip install -e ".[dev]"
```

Includes:
- pytest - Testing framework
- pytest-asyncio - Async test support
- pytest-cov - Coverage reporting
- pytest-mock - Mocking support
- black - Code formatting
- ruff - Linting
- mypy - Type checking
- httpx - HTTP client for testing

### For Documentation

```bash
pip install -e ".[docs]"
```

Includes:
- mkdocs - Documentation generator
- mkdocs-material - Material theme
- mkdocstrings - API documentation

### For Testing Only

```bash
pip install -e ".[test]"
```

Includes:
- pytest and related tools
- httpx for integration tests

---

## Database Setup

### SQLite (Only Supported Database)

CovetPy only works with SQLite. No setup required - SQLite is included with Python.

```python
from covet.database.simple_orm import Model, CharField

class User(Model):
    name = CharField(max_length=100)

# SQLite database is created automatically
```

### PostgreSQL (NOT SUPPORTED)

The PostgreSQL adapter is an **empty stub** (6 lines of code). Do not attempt to use it.

**Alternative:** Use `asyncpg` directly or SQLAlchemy

### MySQL (NOT SUPPORTED)

The MySQL adapter is an **empty stub** (6 lines of code). Do not attempt to use it.

**Alternative:** Use `aiomysql` directly or SQLAlchemy

---

## Configuration

### Minimal Configuration

No configuration required for basic usage:

```python
from covet import CovetPy

app = CovetPy()

@app.route("/")
async def hello(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()  # Requires uvicorn: pip install uvicorn
```

### Running the Application

#### Option 1: Using Built-in Runner

```bash
# Install uvicorn first
pip install uvicorn

# Run the application
python your_app.py
```

#### Option 2: Using uvicorn Directly

```bash
# Install uvicorn
pip install uvicorn[standard]

# Run with uvicorn
uvicorn your_app:app --reload
```

Access at: http://127.0.0.1:8000

---

## Troubleshooting

### Common Issues

#### 1. Import Error: No module named 'covet'

**Problem:** CovetPy not installed or wrong virtual environment

**Solution:**
```bash
# Ensure you're in the correct virtual environment
source venv/bin/activate

# Install in editable mode
pip install -e .

# Verify installation
pip list | grep covet
```

#### 2. Import Error: cannot import name 'X'

**Problem:** Trying to import features that don't exist

**Common examples:**
- `from covet.database.factory import ...` - Module doesn't exist
- `from covet.database.adapters.base import BaseAdapter` - Class incomplete
- `from covet.security.jwt_auth import create_token_pair` - Function doesn't exist

**Solution:** Only use documented, working features (see README.md)

#### 3. Database Connection Error (PostgreSQL/MySQL)

**Problem:** Trying to use PostgreSQL or MySQL

**Solution:** Use SQLite only. PostgreSQL/MySQL adapters are empty stubs.

```python
# ❌ This will NOT work
from covet.database.adapters.postgresql import PostgreSQLAdapter

# ✅ This works (SQLite only)
from covet.database.simple_orm import Model
```

#### 4. uvicorn Not Found

**Problem:** uvicorn not installed

**Solution:**
```bash
pip install uvicorn[standard]
```

#### 5. Test Failures (80.5% failure rate)

**Problem:** Most tests are written for features that don't exist

**Solution:** This is expected. Only test the 40% that works:
```bash
# Test only working components
pytest tests/core/  # HTTP/ASGI tests (if they exist)
```

---

## Development Setup

For contributors and learners:

### 1. Clone and Install

```bash
git clone https://github.com/yourorg/covetpy.git
cd covetpy
python3.9 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 2. Install Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

### 3. Run Tests

```bash
# Run all tests (expect ~80% failure)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/covet --cov-report=html

# Run specific tests
pytest tests/core/ -v
```

### 4. Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

---

## Uninstallation

```bash
# If installed with pip install -e .
pip uninstall covetpy

# Remove virtual environment
deactivate
rm -rf venv/

# Remove cloned repository
cd ..
rm -rf covetpy/
```

---

## Next Steps

After installation:

1. **Read Documentation**
   - [README.md](../README.md) - Project overview
   - [BETA_LIMITATIONS.md](../BETA_LIMITATIONS.md) - What's NOT ready

2. **Try Examples**
   - Start with simple HTTP/ASGI examples
   - Try the simple ORM with SQLite
   - Experiment with routing

3. **Learn**
   - Read the source code (it's educational)
   - Understand ASGI application architecture
   - Learn async/await patterns

4. **For Production**
   - Migrate to FastAPI: https://fastapi.tiangolo.com/
   - Or Flask: https://flask.palletsprojects.com/
   - Or Django: https://www.djangoproject.com/

---

## Support

### For Installation Issues

- **GitHub Issues:** https://github.com/yourorg/covetpy/issues
- **GitHub Discussions:** https://github.com/yourorg/covetpy/discussions

### For Production Support

**CovetPy has no production support.** Use established frameworks:
- FastAPI Community: https://fastapi.tiangolo.com/
- Flask Community: https://flask.palletsprojects.com/
- Django Community: https://www.djangoproject.com/

---

## Summary

✅ **Installation:**
```bash
git clone https://github.com/yourorg/covetpy.git
cd covetpy
pip install -e ".[dev]"
```

✅ **Verify:**
```bash
python -c "from covet import CovetPy; print('✅ Installed')"
```

✅ **Use:**
- For learning only
- SQLite database only
- Basic HTTP/ASGI features only

❌ **Do NOT Use:**
- In production
- With PostgreSQL/MySQL
- For security-sensitive applications
- With sensitive data

---

**For production applications, use FastAPI, Flask, or Django.**
