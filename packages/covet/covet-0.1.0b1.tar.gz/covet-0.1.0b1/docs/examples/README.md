# CovetPy Working Examples

This directory contains **tested, working examples** that demonstrate the correct way to use CovetPy framework components. Every example in this directory has been verified to execute without errors.

## Important: These Examples Use the CORRECT APIs

The examples in this directory reflect the **actual implementation** of CovetPy, not idealized documentation. They are based on real working tests and have been verified to run successfully.

## Examples Overview

### 1. Hello World (`01_hello_world.py`)
**The simplest possible CovetPy application**

- Basic application setup
- Simple route definition
- Path parameters
- Running the development server

**Run it:**
```bash
python docs/examples/01_hello_world.py
```

**Visit:** http://localhost:8000/

---

### 2. Database Example (`02_database_example.py`)
**Complete SQLite database operations**

- Connecting to SQLite database
- Creating tables with foreign keys
- CRUD operations (Create, Read, Update, Delete)
- JOIN queries
- Aggregation queries
- Parameterized queries

**Run it:**
```bash
python docs/examples/02_database_example.py
```

**Creates:** `/tmp/covetpy_example.db`

---

### 3. JWT Authentication Example (`03_jwt_auth_example.py`)
**Token generation and verification**

**CRITICAL:** This example shows the CORRECT way to use JWT in CovetPy:
- Use `JWTAlgorithm.HS256` (enum), NOT `'HS256'` (string)
- Use `TokenType.ACCESS` (enum), NOT `'access'` (string)

Features demonstrated:
- JWT configuration with enums
- Access token generation
- Refresh token generation
- Token verification
- Custom claims (roles, permissions)

**Run it:**
```bash
python docs/examples/03_jwt_auth_example.py
```

---

### 4. REST API Example (`04_rest_api_example.py`)
**Request validation and routing**

- RESTFramework setup
- Pydantic models for validation
- Field constraints (min_length, max_length, ge, le)
- CRUD endpoints
- Error handling with NotFoundError

**Run it:**
```bash
python docs/examples/04_rest_api_example.py
```

---

### 5. Full Integration Example (`05_full_integration_example.py`)
**Complete application: Database + REST API + JWT**

This is a complete user registration and login system that combines all CovetPy components:
- SQLite database for user storage
- REST API for endpoints
- JWT authentication for security
- Request validation with Pydantic

Features:
- User registration with validation
- User login with authentication
- JWT token generation
- Password verification (simplified for demo)
- User listing

**Run it:**
```bash
python docs/examples/05_full_integration_example.py
```

**Creates:** `/tmp/covetpy_integration.db`

---

## Installation Requirements

All examples require:

```bash
# Basic installation
pip install uvicorn pydantic

# If running from source
cd /path/to/NeutrinoPy
pip install -e .
```

## Key Differences from Documentation

### WRONG (in old docs):
```python
from covet import Application  # Does NOT exist
app = Application()
```

### CORRECT (actual implementation):
```python
from covet import CovetPy
app = CovetPy()
```

---

### WRONG (in old docs):
```python
from covet.auth import JWTConfig
config = JWTConfig(algorithm='HS256')  # String NOT accepted
```

### CORRECT (actual implementation):
```python
from covet.security.jwt_auth import JWTConfig, JWTAlgorithm
config = JWTConfig(algorithm=JWTAlgorithm.HS256)  # Must use enum
```

---

### WRONG (in old docs):
```python
from covet.database import Database
db = Database(adapter='sqlite', database='app.db')
```

### CORRECT (actual implementation):
```python
from covet.database import DatabaseManager, SQLiteAdapter
adapter = SQLiteAdapter(database_path='app.db')
db = DatabaseManager(adapter)
```

---

## Testing the Examples

To test all examples at once:

```bash
# Run each example (they all output to /tmp/)
python docs/examples/01_hello_world.py &  # Runs server
python docs/examples/02_database_example.py
python docs/examples/03_jwt_auth_example.py
python docs/examples/04_rest_api_example.py
python docs/examples/05_full_integration_example.py
```

## Common Pitfalls

See `docs/troubleshooting/COMMON_MISTAKES.md` for detailed information about common mistakes when using CovetPy.

### Quick Reference:

1. **Class naming**: Use `CovetPy`, not `Application`
2. **JWT enums**: Use `JWTAlgorithm.HS256` and `TokenType.ACCESS`, not strings
3. **Database setup**: Use `DatabaseManager(adapter)`, not `Database(...)`
4. **Import paths**: Use full paths like `covet.security.jwt_auth`, not short paths

## Contributing Examples

If you create a new working example:

1. Test it thoroughly
2. Add detailed comments
3. Follow the naming convention: `##_descriptive_name.py`
4. Update this README
5. Add it to the troubleshooting guide if it addresses a common mistake

## Support

If an example doesn't work for you:

1. Check your CovetPy version: `python -c "import covet; print(covet.__version__)"`
2. Verify Python version: `python --version` (needs 3.9+)
3. Check dependencies: `pip list | grep -E "(pydantic|uvicorn)"`
4. Open an issue with the full error message

## License

These examples are part of the CovetPy project and are released under the MIT License.
