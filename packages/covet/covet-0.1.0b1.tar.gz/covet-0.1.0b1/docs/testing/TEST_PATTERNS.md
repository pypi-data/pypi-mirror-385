# CovetPy Test Patterns & Best Practices

## Quick Reference Guide for Writing Tests

### Test Structure (AAA Pattern)

```python
def test_feature_scenario_outcome():
    """Descriptive docstring explaining what this test verifies."""

    # ARRANGE - Setup test data and conditions
    user = {"username": "testuser", "email": "test@example.com"}
    hasher = PasswordHasher()

    # ACT - Execute the code being tested
    hashed_password = hasher.hash_password("secure123")
    is_valid = hasher.verify_password("secure123", hashed_password)

    # ASSERT - Verify the expected outcome
    assert hashed_password is not None
    assert is_valid is True
    assert hashed_password != "secure123"  # Password should be hashed
```

---

## Critical Rules

### ❌ NEVER DO THIS

```python
# WRONG: Returning boolean (test always passes)
def test_something():
    result = do_something()
    return result == expected  # ❌ ALWAYS PASSES

# WRONG: Using mock data in integration tests
def test_database_integration():
    mock_db = MagicMock()  # ❌ NOT A REAL DATABASE
    mock_db.query.return_value = [{"id": 1}]

# WRONG: No assertions
def test_create_user():
    user = create_user("test")
    # ❌ NO ASSERTION - What are we testing?
```

### ✅ ALWAYS DO THIS

```python
# CORRECT: Use assertions
def test_something():
    result = do_something()
    assert result == expected  # ✅ PROPER ASSERTION

# CORRECT: Use real database in integration tests
def test_database_integration(real_postgres_db):
    result = real_postgres_db.execute("SELECT * FROM users")  # ✅ REAL DB
    assert len(result) > 0

# CORRECT: Always assert
def test_create_user():
    user = create_user("test")
    assert user is not None  # ✅ CLEAR ASSERTION
    assert user["username"] == "test"
```

---

## Test Types

### 1. Unit Tests (Fast, Isolated)

**Purpose:** Test individual functions/methods in isolation
**Mocking:** Allowed for external dependencies
**Speed:** <1 second per test

```python
import pytest
from unittest.mock import Mock, patch

def test_calculate_total_with_valid_items():
    """Test total calculation with valid items."""
    # Arrange
    items = [
        {"price": 10.00, "quantity": 2},
        {"price": 5.00, "quantity": 3}
    ]

    # Act
    total = calculate_total(items)

    # Assert
    assert total == 35.00  # (10*2) + (5*3)

@pytest.mark.asyncio
async def test_async_function():
    """Test async functions with pytest-asyncio."""
    # Arrange
    user_id = 123

    # Act
    result = await fetch_user(user_id)

    # Assert
    assert result["id"] == user_id
```

### 2. Integration Tests (Real Backends)

**Purpose:** Test component interactions with real services
**Mocking:** NOT ALLOWED - Use real databases, APIs, etc.
**Speed:** 1-10 seconds per test

```python
import pytest

@pytest.mark.integration
def test_postgresql_connection_and_query(postgresql_container):
    """Test real PostgreSQL database connection."""
    # Arrange - Use real PostgreSQL from Docker
    db = PostgreSQLAdapter(postgresql_container.get_connection_url())

    # Act
    db.execute("CREATE TABLE users (id INT, name VARCHAR(100))")
    db.execute("INSERT INTO users VALUES (1, 'Test User')")
    result = db.query("SELECT * FROM users WHERE id = 1")

    # Assert
    assert len(result) == 1
    assert result[0]["name"] == "Test User"

    # Cleanup
    db.execute("DROP TABLE users")

@pytest.mark.integration
async def test_redis_caching_with_real_redis(redis_container):
    """Test caching with real Redis instance."""
    # Arrange
    cache = RedisCache(redis_container.get_connection_url())
    key = "test_key"
    value = {"data": "test_value"}

    # Act
    await cache.set(key, value, ttl=60)
    cached_value = await cache.get(key)

    # Assert
    assert cached_value == value
```

### 3. End-to-End Tests (Complete Workflows)

**Purpose:** Test complete user workflows through entire system
**Mocking:** NOT ALLOWED - Real application stack
**Speed:** 10-60 seconds per test

```python
import pytest
from covet.testing import TestClient

@pytest.mark.e2e
async def test_user_registration_login_crud_workflow(test_app):
    """Test complete user workflow: register → login → CRUD → logout."""
    client = TestClient(test_app)

    # Step 1: Register user
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    response = await client.post("/api/auth/register", json=register_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Step 2: Login
    login_data = {"username": "testuser", "password": "SecurePass123!"}
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Step 3: Create resource (authenticated)
    headers = {"Authorization": f"Bearer {token}"}
    resource_data = {"title": "Test Resource", "content": "Test content"}
    response = await client.post("/api/resources", json=resource_data, headers=headers)
    assert response.status_code == 201
    resource_id = response.json()["id"]

    # Step 4: Read resource
    response = await client.get(f"/api/resources/{resource_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Resource"

    # Step 5: Update resource
    update_data = {"title": "Updated Title"}
    response = await client.put(f"/api/resources/{resource_id}", json=update_data, headers=headers)
    assert response.status_code == 200

    # Step 6: Delete resource
    response = await client.delete(f"/api/resources/{resource_id}", headers=headers)
    assert response.status_code == 204

    # Step 7: Logout
    response = await client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200
```

---

## Fixtures & Setup

### Database Fixtures

```python
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.mysql import MySqlContainer

@pytest.fixture(scope="session")
def postgresql_container():
    """Provide PostgreSQL test database."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def mysql_container():
    """Provide MySQL test database."""
    with MySqlContainer("mysql:8.0") as mysql:
        yield mysql

@pytest.fixture
def db_connection(postgresql_container):
    """Provide database connection with cleanup."""
    conn = create_connection(postgresql_container.get_connection_url())
    yield conn
    conn.close()
```

### Application Fixtures

```python
@pytest.fixture
async def test_app():
    """Provide test application instance."""
    app = create_app(testing=True)
    await app.startup()
    yield app
    await app.shutdown()

@pytest.fixture
def authenticated_client(test_app):
    """Provide authenticated test client."""
    client = TestClient(test_app)
    # Create test user and authenticate
    token = create_test_user_and_get_token(client)
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

---

## Parametrized Tests

Test multiple scenarios with single test function:

```python
@pytest.mark.parametrize("password,expected_valid", [
    ("Secure123!", True),      # Valid password
    ("weak", False),            # Too short
    ("NoNumbers!", False),      # No numbers
    ("nonumbers123", False),    # No special chars
    ("", False),                # Empty
    ("a" * 1000, True),        # Very long but valid
])
def test_password_validation(password, expected_valid):
    """Test password validation with various inputs."""
    is_valid = validate_password(password)
    assert is_valid == expected_valid

@pytest.mark.parametrize("database", ["postgresql", "mysql", "sqlite"])
@pytest.mark.integration
def test_database_adapter_crud(database, get_db_container):
    """Test CRUD operations across different databases."""
    db = get_db_container(database)

    # Create
    result = db.execute("INSERT INTO users (name) VALUES (?)", ["Test User"])
    assert result.rowcount == 1

    # Read
    rows = db.query("SELECT * FROM users WHERE name = ?", ["Test User"])
    assert len(rows) == 1

    # Update
    db.execute("UPDATE users SET name = ? WHERE name = ?", ["Updated", "Test User"])

    # Delete
    db.execute("DELETE FROM users WHERE name = ?", ["Updated"])
```

---

## Testing Exceptions

```python
def test_invalid_input_raises_validation_error():
    """Test that invalid input raises ValidationError."""
    invalid_data = {"email": "not-an-email"}

    with pytest.raises(ValidationError) as exc_info:
        validate_user(invalid_data)

    assert "email" in str(exc_info.value)
    assert "invalid" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_async_exception_handling():
    """Test async exception handling."""
    with pytest.raises(AuthenticationError):
        await authenticate_user("invalid_token")
```

---

## Testing Async Code

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test async function with pytest-asyncio."""
    result = await async_operation()
    assert result is not None

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test multiple concurrent async operations."""
    tasks = [
        async_operation(1),
        async_operation(2),
        async_operation(3)
    ]
    results = await asyncio.gather(*tasks)
    assert len(results) == 3
    assert all(r is not None for r in results)
```

---

## Mocking (Unit Tests Only)

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock_dependency():
    """Test function with mocked external dependency."""
    # Create mock
    mock_api = Mock()
    mock_api.fetch_data.return_value = {"data": "test"}

    # Test function with mock
    result = process_data(mock_api)

    # Verify mock was called correctly
    mock_api.fetch_data.assert_called_once()
    assert result["data"] == "test"

@patch('module.external_api_call')
def test_with_patch(mock_api_call):
    """Test with patched function."""
    mock_api_call.return_value = {"status": "success"}

    result = function_that_calls_api()

    assert result["status"] == "success"
    mock_api_call.assert_called_once()
```

---

## Performance Testing

```python
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

def test_performance_benchmark(benchmark: BenchmarkFixture):
    """Benchmark function performance."""
    result = benchmark(expensive_operation, arg1, arg2)
    assert result is not None

def test_performance_threshold():
    """Test that operation completes within time limit."""
    import time
    start = time.time()

    result = expensive_operation()

    elapsed = time.time() - start
    assert elapsed < 1.0  # Must complete within 1 second
    assert result is not None
```

---

## Coverage Best Practices

### Check Coverage

```bash
# Run tests with coverage
pytest --cov=covet --cov-report=term-missing

# Generate HTML report
pytest --cov=covet --cov-report=html
open htmlcov/index.html

# Fail if below threshold
pytest --cov=covet --cov-fail-under=85
```

### Focus on Important Coverage

```python
# Test all code paths
def test_all_branches():
    """Test all conditional branches."""
    # Test if branch
    assert function(True) == "yes"

    # Test else branch
    assert function(False) == "no"

# Test edge cases
def test_edge_cases():
    """Test boundary conditions."""
    assert process_value(0) is not None      # Zero
    assert process_value(1) is not None      # Min
    assert process_value(999999) is not None # Max
    assert process_value(-1) is not None     # Negative
```

---

## Test Organization

```python
class TestUserAuthentication:
    """Group related tests in a class."""

    def test_login_success(self):
        """Test successful login."""
        assert login("user", "pass") is not None

    def test_login_invalid_password(self):
        """Test login with invalid password."""
        assert login("user", "wrong") is None

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user."""
        assert login("fake", "pass") is None

    @pytest.mark.slow
    def test_login_rate_limiting(self):
        """Test rate limiting on multiple failed attempts."""
        for _ in range(5):
            login("user", "wrong")

        with pytest.raises(RateLimitError):
            login("user", "wrong")
```

---

## Common Assertions

```python
# Equality
assert result == expected
assert result != unexpected

# Truth/Falsiness
assert result  # Truthy
assert not result  # Falsy
assert result is True
assert result is False
assert result is None

# Containment
assert item in collection
assert item not in collection
assert "substring" in string

# Type checking
assert isinstance(result, dict)
assert isinstance(result, list)
assert type(result) is str

# Comparisons
assert result > 0
assert result >= 10
assert result < 100
assert result <= 100

# Approximate equality (floats)
assert result == pytest.approx(3.14159, rel=1e-3)

# Collections
assert len(collection) == 5
assert len(collection) > 0
assert all(item > 0 for item in collection)
assert any(item > 10 for item in collection)
```

---

## Markers

```python
# Skip test
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

# Skip conditionally
@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_feature():
    pass

# Expected failure
@pytest.mark.xfail(reason="Known bug #123")
def test_known_issue():
    pass

# Custom markers
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.security
def test_something():
    pass

# Run specific markers
# pytest -m "slow"
# pytest -m "not slow"
# pytest -m "integration and not slow"
```

---

## Debugging Tests

```python
# Print debugging
def test_with_debug():
    result = complex_function()
    print(f"Result: {result}")  # Will show in pytest -s output
    assert result is not None

# Use pytest debugging
def test_with_breakpoint():
    result = complex_function()
    import pdb; pdb.set_trace()  # Debugger breakpoint
    assert result is not None

# Run single test
# pytest tests/test_file.py::test_function_name -v

# Run with print output
# pytest -s

# Run last failed tests
# pytest --lf

# Run failed first
# pytest --ff
```

---

## Anti-Patterns to Avoid

### ❌ Testing Implementation Details

```python
# BAD: Testing internal implementation
def test_internal_cache_structure():
    obj = MyClass()
    assert obj._internal_cache == {}  # Don't test private attributes

# GOOD: Testing behavior
def test_caching_behavior():
    obj = MyClass()
    obj.get_data()  # First call
    result = obj.get_data()  # Should use cache
    assert result is not None
```

### ❌ Fragile Tests

```python
# BAD: Depends on external state
def test_get_users():
    users = get_users()  # Depends on database state
    assert len(users) == 5  # Will break if data changes

# GOOD: Control test state
def test_get_users(clean_database):
    create_test_users(5)
    users = get_users()
    assert len(users) == 5
```

### ❌ Slow Unit Tests

```python
# BAD: Slow unit test
def test_user_creation():
    time.sleep(2)  # Unnecessary delay
    db.connect()  # Real database
    user = create_user()  # Complex setup

# GOOD: Fast unit test
def test_user_creation():
    user = create_user_object("test")  # In-memory object
    assert user.name == "test"
```

---

## Resources

- pytest documentation: https://docs.pytest.org/
- Real Python pytest guide: https://realpython.com/pytest-python-testing/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- testcontainers: https://testcontainers-python.readthedocs.io/

---

**Remember:**
- Unit tests = Fast & Isolated (mocks OK)
- Integration tests = Real backends (no mocks)
- E2E tests = Complete workflows (real everything)
- Always use assertions, never return booleans
- Descriptive test names explain what's being tested
- AAA pattern for clarity
