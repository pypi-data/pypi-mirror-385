# Running CovetPy Tests

Complete guide to running the CovetPy test suite with real database integration.

---

## Quick Start

### 1. Install Dependencies

```bash
# Install all test dependencies
pip install -e ".[test]"

# Or install with full feature set including databases
pip install -e ".[full]"

# Install database drivers for integration tests
pip install asyncpg aiomysql redis
```

### 2. Start Test Databases

```bash
# Start PostgreSQL, MySQL, and Redis in Docker
docker-compose -f docker-compose.test.yml up -d

# Verify databases are running
docker-compose -f docker-compose.test.yml ps

# Check database health
docker-compose -f docker-compose.test.yml logs postgres-test
docker-compose -f docker-compose.test.yml logs mysql-test
docker-compose -f docker-compose.test.yml logs redis-test
```

### 3. Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/covet --cov-report=html --cov-report=term-missing

# Run specific test categories
pytest tests/ -m unit              # Unit tests only
pytest tests/ -m integration       # Integration tests only
pytest tests/ -m "not slow"        # Skip slow tests
pytest tests/ -m "performance"     # Performance tests only
```

---

## Test Database Configuration

### Connection Details

**PostgreSQL:**
- Host: localhost
- Port: 5433 (non-standard to avoid conflicts)
- Database: covet_test
- User: test
- Password: test_password_123

**MySQL:**
- Host: localhost
- Port: 3307 (non-standard to avoid conflicts)
- Database: covet_test
- User: test
- Password: test_password_123
- Root Password: root_password_456

**Redis:**
- Host: localhost
- Port: 6380 (non-standard to avoid conflicts)
- DB: 0

### Environment Variables

Override defaults with environment variables:

```bash
# PostgreSQL
export POSTGRES_TEST_HOST=localhost
export POSTGRES_TEST_PORT=5433
export POSTGRES_TEST_USER=test
export POSTGRES_TEST_PASSWORD=test_password_123
export POSTGRES_TEST_DB=covet_test

# MySQL
export MYSQL_TEST_HOST=localhost
export MYSQL_TEST_PORT=3307
export MYSQL_TEST_USER=test
export MYSQL_TEST_PASSWORD=test_password_123
export MYSQL_TEST_DB=covet_test

# Redis
export REDIS_TEST_HOST=localhost
export REDIS_TEST_PORT=6380
```

---

## Test Categories

### Unit Tests
```bash
pytest tests/unit/ -v
```
- No external dependencies
- Fast execution
- Test individual functions and classes
- Mock external services

### Integration Tests
```bash
pytest tests/integration/ -v
```
- Require real databases
- Test component interactions
- Verify database queries
- Test API endpoints

### End-to-End Tests
```bash
pytest tests/e2e/ -v
```
- Full user workflows
- Complete request/response cycles
- Real database transactions
- WebSocket connections

### Performance Tests
```bash
pytest tests/performance/ -v --benchmark-only
```
- Benchmark critical paths
- Load testing
- Throughput measurement
- Response time analysis

### Security Tests
```bash
pytest tests/security/ -v
```
- Authentication tests
- Authorization tests
- SQL injection prevention
- XSS prevention
- CSRF protection

---

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: covet_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test_password_123
        ports:
          - 5433:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      mysql:
        image: mysql:8.0
        env:
          MYSQL_DATABASE: covet_test
          MYSQL_USER: test
          MYSQL_PASSWORD: test_password_123
          MYSQL_ROOT_PASSWORD: root_password_456
        ports:
          - 3307:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

      redis:
        image: redis:7-alpine
        ports:
          - 6380:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -e ".[full]"
          pip install asyncpg aiomysql redis pytest-cov

      - name: Run tests
        env:
          POSTGRES_TEST_PORT: 5433
          MYSQL_TEST_PORT: 3307
          REDIS_TEST_PORT: 6380
        run: |
          pytest tests/ -v --cov=src/covet --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Coverage Reports

### Generate HTML Report

```bash
pytest tests/ --cov=src/covet --cov-report=html
open tests/reports/coverage/index.html
```

### Generate Terminal Report

```bash
pytest tests/ --cov=src/covet --cov-report=term-missing
```

### Generate XML Report (for CI)

```bash
pytest tests/ --cov=src/covet --cov-report=xml
```

### Coverage Thresholds

Minimum coverage targets:
- Overall: ≥85%
- Core framework: ≥90%
- Security: ≥95%
- Database: ≥85%
- API: ≥80%

---

## Debugging Tests

### Run Single Test

```bash
pytest tests/unit/test_core_routing.py::test_route_matching -v
```

### Run with Debug Output

```bash
pytest tests/ -v -s --log-cli-level=DEBUG
```

### Run with PDB Debugger

```bash
pytest tests/ --pdb
```

### Run Failed Tests Only

```bash
# Run tests, then re-run only failures
pytest tests/
pytest tests/ --lf  # --last-failed
```

---

## Performance Testing

### Benchmark Tests

```bash
# Run benchmarks
pytest tests/performance/ --benchmark-only

# Generate benchmark report
pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json

# Compare benchmarks
pytest tests/performance/ --benchmark-compare=baseline.json
```

### Load Testing

```bash
# Run load tests
pytest tests/load/ -v

# High concurrency load test
pytest tests/load/test_high_concurrency_load.py -v
```

---

## Troubleshooting

### Tests Can't Connect to Database

```bash
# Check database containers are running
docker-compose -f docker-compose.test.yml ps

# Check database logs
docker-compose -f docker-compose.test.yml logs postgres-test

# Restart databases
docker-compose -f docker-compose.test.yml restart
```

### Port Conflicts

```bash
# Check what's using the ports
lsof -i :5433  # PostgreSQL
lsof -i :3307  # MySQL
lsof -i :6380  # Redis

# Kill processes or change ports in docker-compose.test.yml
```

### Import Errors

```bash
# Reinstall package in development mode
pip install -e .

# Check Python path
python -c "import sys; print('\\n'.join(sys.path))"

# Verify imports
python -c "from covet.core.routing import CovetRouter"
```

### Slow Tests

```bash
# Show slowest 10 tests
pytest tests/ --durations=10

# Skip slow tests
pytest tests/ -m "not slow"

# Run tests in parallel
pip install pytest-xdist
pytest tests/ -n auto
```

---

## Test Markers

Available test markers:

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.e2e            # End-to-end test
@pytest.mark.performance    # Performance test
@pytest.mark.security       # Security test
@pytest.mark.slow           # Slow test (>5s)
@pytest.mark.real_backend   # Requires real backend
@pytest.mark.database       # Requires database
@pytest.mark.websocket      # WebSocket test
@pytest.mark.benchmark      # Benchmark test
```

Usage:

```bash
# Run only unit tests
pytest tests/ -m unit

# Run integration and e2e tests
pytest tests/ -m "integration or e2e"

# Run everything except slow tests
pytest tests/ -m "not slow"
```

---

## Test Fixtures

Available fixtures (defined in `tests/conftest.py`):

### Database Fixtures

- `postgres_pool` - PostgreSQL connection pool (session scope)
- `postgres_conn` - PostgreSQL connection (function scope, auto-rollback)
- `mysql_pool` - MySQL connection pool (session scope)
- `mysql_conn` - MySQL connection (function scope, auto-rollback)
- `redis_client` - Redis client (session scope)

### Utility Fixtures

- `test_user_data` - Sample user dictionary
- `test_api_key` - Sample API key string
- `test_jwt_secret` - JWT secret for testing
- `benchmark_config` - Performance test configuration

### Example Usage

```python
import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_crud(postgres_conn):
    """Test user CRUD operations with real database."""
    # Create user
    user_id = await postgres_conn.fetchval(
        "INSERT INTO users (username, email) VALUES ($1, $2) RETURNING id",
        "testuser", "test@example.com"
    )

    # Read user
    user = await postgres_conn.fetchrow(
        "SELECT * FROM users WHERE id = $1", user_id
    )

    assert user['username'] == "testuser"
    # Transaction auto-rolls back after test
```

---

## Maintenance

### Clean Test Databases

```bash
# Stop and remove containers
docker-compose -f docker-compose.test.yml down

# Remove volumes (if using persistent storage)
docker-compose -f docker-compose.test.yml down -v

# Restart fresh
docker-compose -f docker-compose.test.yml up -d
```

### Update Test Dependencies

```bash
# Update all dependencies
pip install --upgrade -e ".[test]"

# Update specific package
pip install --upgrade pytest pytest-asyncio
```

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## Getting Help

If tests are failing:

1. Check this documentation first
2. Review test logs: `pytest tests/ -v -s`
3. Check database logs: `docker-compose -f docker-compose.test.yml logs`
4. Review the Test Infrastructure Audit: `docs/TEST_INFRASTRUCTURE_AUDIT.md`
5. Contact the Test Infrastructure Team
