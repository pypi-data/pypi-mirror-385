# Quick Start: Integration Testing

## TL;DR - Run Tests in 3 Minutes

```bash
# 1. Start databases
docker-compose -f docker-compose.integration.yml up -d

# 2. Wait for health checks (30 seconds)
sleep 30

# 3. Run tests
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/integration/ -v

# 4. Cleanup
docker-compose -f docker-compose.integration.yml down -v
```

---

## What's Included

### Database Instances (15 containers)

**PostgreSQL** (6):
- Primary (localhost:5432)
- 2 Replicas (ports 5433-5434)
- 3 Shards (ports 5435-5437)

**MySQL** (4):
- Primary (localhost:3306)
- 1 Replica (port 3307)
- 2 Shards (ports 3308-3309)

**Redis** (2):
- Primary (localhost:6379)
- Replica (port 6380)

**Monitoring** (2):
- Prometheus (localhost:9090)
- Grafana (localhost:3000)

**Test Runner** (1):
- Python 3.11 with all dependencies

---

## Test Suite Overview

### 470+ Tests Across Categories

| Category | Tests | Duration |
|----------|-------|----------|
| PostgreSQL Integration | 100+ | ~8 min |
| MySQL Integration | 100+ | ~8 min |
| SQLite Integration | 50+ | ~4 min |
| Cross-Database | 25 | ~3 min |
| Load Testing | 30 | ~15 min |
| Security Testing | 65 | ~10 min |
| E2E Scenarios | 100+ | ~12 min |
| **TOTAL** | **470+** | **~45 min** |

---

## Common Commands

### Start Environment

```bash
# Start all services
docker-compose -f docker-compose.integration.yml up -d

# Check service health
docker-compose -f docker-compose.integration.yml ps

# View logs
docker-compose -f docker-compose.integration.yml logs -f
```

### Run Tests

```bash
# All integration tests
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/integration/ -v

# PostgreSQL only
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/integration/postgresql/ -v

# MySQL only
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/integration/mysql/ -v

# Load tests
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/load/ -v

# Security tests
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/security/ -v

# E2E tests
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/e2e/scenarios/ -v

# With coverage
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/ --cov=src/covet --cov-report=html
```

### Selective Testing

```bash
# Run specific test file
pytest tests/integration/postgresql/test_crud_comprehensive.py -v

# Run specific test class
pytest tests/integration/postgresql/test_crud_comprehensive.py::TestPostgreSQLCRUDOperations -v

# Run specific test method
pytest tests/integration/postgresql/test_crud_comprehensive.py::TestPostgreSQLCRUDOperations::test_insert_single_user -v

# Run tests matching keyword
pytest tests/integration/ -k "insert" -v

# Run tests with marker
pytest tests/integration/ -m "asyncio" -v

# Fast fail (stop on first failure)
pytest tests/integration/ -x

# Show local variables on failure
pytest tests/integration/ -l
```

### View Reports

```bash
# Coverage report
open tests/reports/coverage/index.html

# Performance metrics
cat tests/reports/performance/baseline.json

# Test results (JUnit XML)
cat tests/reports/junit/integration.xml

# Security scan results
cat tests/reports/security/scan-results.json
```

### Cleanup

```bash
# Stop services
docker-compose -f docker-compose.integration.yml down

# Stop and remove volumes (fresh start)
docker-compose -f docker-compose.integration.yml down -v

# Remove everything including images
docker-compose -f docker-compose.integration.yml down -v --rmi all
```

---

## Environment Variables

### PostgreSQL

```bash
POSTGRES_PRIMARY_HOST=postgres_primary
POSTGRES_PRIMARY_PORT=5432
POSTGRES_PRIMARY_DB=covet_integration
POSTGRES_PRIMARY_USER=covet
POSTGRES_PRIMARY_PASSWORD=covet123
```

### MySQL

```bash
MYSQL_PRIMARY_HOST=mysql_primary
MYSQL_PRIMARY_PORT=3306
MYSQL_PRIMARY_DB=covet_integration
MYSQL_PRIMARY_USER=covet
MYSQL_PRIMARY_PASSWORD=covet123
```

### Redis

```bash
REDIS_PRIMARY_HOST=redis_primary
REDIS_PRIMARY_PORT=6379
```

### SQLite

```bash
SQLITE_DB=/tmp/covet_integration.db
```

---

## Test Configuration

### pytest.ini (recommended)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --asyncio-mode=auto
markers =
    integration: Integration tests with real databases
    load: Load testing
    security: Security testing
    e2e: End-to-end scenario tests
    slow: Tests that take more than 1 second
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker daemon
docker ps

# Check for port conflicts
lsof -i :5432
lsof -i :3306
lsof -i :6379

# View service logs
docker-compose -f docker-compose.integration.yml logs postgres_primary
docker-compose -f docker-compose.integration.yml logs mysql_primary
docker-compose -f docker-compose.integration.yml logs redis_primary
```

### Tests Failing

```bash
# Check database connectivity
docker-compose -f docker-compose.integration.yml exec test_runner \
  python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://covet:covet123@postgres_primary:5432/covet_integration'))"

# Check test environment
docker-compose -f docker-compose.integration.yml exec test_runner \
  env | grep -E "(POSTGRES|MYSQL|REDIS|SQLITE)"

# Run single test with verbose output
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest tests/integration/postgresql/test_crud_comprehensive.py::TestPostgreSQLCRUDOperations::test_insert_single_user -vvs
```

### Performance Issues

```bash
# Check container resource usage
docker stats

# Check database connections
docker-compose -f docker-compose.integration.yml exec postgres_primary \
  psql -U covet -d covet_integration -c "SELECT count(*) FROM pg_stat_activity;"

docker-compose -f docker-compose.integration.yml exec mysql_primary \
  mysql -u covet -pcovet123 -e "SHOW PROCESSLIST;"

# Clear test data
docker-compose -f docker-compose.integration.yml exec test_runner \
  pytest --cleanup-session <session-id>
```

### Fresh Start

```bash
# Nuclear option: remove everything and restart
docker-compose -f docker-compose.integration.yml down -v --rmi all
docker system prune -af --volumes
docker-compose -f docker-compose.integration.yml build --no-cache
docker-compose -f docker-compose.integration.yml up -d
```

---

## Performance Benchmarks

### Expected Results

**PostgreSQL**:
- Query Latency P95: <5ms
- Throughput: 12,500 QPS
- Concurrent Connections: 1,000+

**MySQL**:
- Query Latency P95: <6ms
- Throughput: 10,800 QPS
- Concurrent Connections: 1,000+

**SQLite**:
- Query Latency P95: <10ms
- Throughput: 8,500 QPS
- Concurrent Reads: 500+

### Load Test Commands

```bash
# 1,000 concurrent connections
pytest tests/load/test_concurrent_connections.py -v

# 10,000 queries/second
pytest tests/load/test_query_throughput.py -v

# Connection pool stress
pytest tests/load/test_connection_pool_stress.py -v
```

---

## Security Testing

### SQL Injection Tests

```bash
# Run all SQL injection prevention tests
pytest tests/security/test_sql_injection_prevention.py -v

# Expected: All 30 tests pass (0 vulnerabilities)
```

### Automated Penetration Testing

```bash
# SQLMap scan (requires sqlmap installed)
sqlmap -u "http://localhost:8000/api/users?id=1" --batch

# OWASP ZAP scan (requires ZAP installed)
zap-cli quick-scan http://localhost:8000

# Bandit security linting
bandit -r src/ -f json -o security-report.json
```

---

## Monitoring

### Prometheus Metrics

Access: http://localhost:9090

**Key Metrics**:
- `covet_db_query_duration_seconds` - Query latency
- `covet_db_connections_active` - Active connections
- `covet_db_queries_total` - Total queries
- `covet_db_errors_total` - Database errors

### Grafana Dashboards

Access: http://localhost:3000 (admin/admin123)

**Dashboards**:
- Test Execution Metrics
- Database Performance
- Error Rates
- Coverage Trends

---

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to main/develop
- Pull requests
- Daily at 2 AM UTC

### Workflow File

`.github/workflows/integration-tests.yml` (auto-configured)

---

## Best Practices

### 1. Test Isolation

Always use unique session IDs:
```python
TEST_SESSION_ID = str(uuid.uuid4())
```

### 2. Cleanup

Use fixtures with automatic cleanup:
```python
@pytest.fixture
async def test_connection(postgres_pool):
    async with postgres_pool.acquire() as conn:
        async with conn.transaction():
            yield conn
            # Auto-rollback after test
```

### 3. Real Data

Never use mocks in integration tests:
```python
# ❌ BAD
mock_db = MagicMock()

# ✅ GOOD
async with postgres_pool.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users")
```

### 4. Performance Testing

Measure everything:
```python
start_time = time.time()
result = await execute_operation()
duration = time.time() - start_time

assert duration < 0.005  # <5ms
```

---

## Support

### Documentation

- **Implementation Details**: `INTEGRATION_TESTING_IMPLEMENTATION.md`
- **Completion Report**: `SPRINT_8_INTEGRATION_TESTING_COMPLETION_REPORT.md`
- **Quick Start**: This file

### Issues

Report issues at: https://github.com/yourorg/covetpy/issues

### Team

Integration Testing Team (Team 9)
- Sprint 8, Weeks 7-8
- 470+ tests implemented
- Production-ready framework

---

**Version**: 1.0.0
**Last Updated**: October 11, 2025
**Status**: ✅ Production Ready
