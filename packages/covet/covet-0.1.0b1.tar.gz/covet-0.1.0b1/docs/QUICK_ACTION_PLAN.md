# Database Production Hardening - Quick Action Plan

**Current Status:** Connection Pool 82.6% Ready (19/23 tests passing)
**Target:** 100% Production-Ready in 2-3 weeks

---

## Week 2: Days 1-7 (Current Week)

### Day 1: Fix Connection Pool Tests (2 hours)
**Goal:** 100% test pass rate
```bash
# Fix these 4 failing tests:
pytest tests/database/test_connection_pool.py::TestBasicPoolOperations::test_connection_validation -v
pytest tests/database/test_connection_pool.py::TestBasicPoolOperations::test_pool_statistics_tracking -v
pytest tests/database/test_connection_pool.py::TestLeakDetectionAndRecovery::test_memory_leak_prevention -v
pytest tests/database/test_connection_pool.py::TestFailoverScenarios::test_connection_factory_failures -v
```

**Issues:**
- test_connection_validation: Timeout behavior needs adjustment
- test_pool_statistics_tracking: Counter off-by-one
- test_memory_leak_prevention: GC timing assertion
- test_connection_factory_failures: Retry counter assertion

### Day 2-3: MySQL Adapter Production Hardening (16 hours)
**File:** `src/covet/database/adapters/mysql.py`

**Tasks:**
1. Integrate ConnectionPool class
   ```python
   from covet.database.core.connection_pool import ConnectionPool, PoolConfig

   class MySQLAdapter:
       def __init__(self, config):
           pool_config = PoolConfig(min_size=10, max_size=100)
           self.pool = ConnectionPool(self._create_connection, pool_config)
   ```

2. Add retry logic with exponential backoff
   ```python
   async def execute_with_retry(self, query, params, max_retries=3):
       for attempt in range(max_retries):
           try:
               return await self.execute(query, params)
           except MySQLError as e:
               if attempt == max_retries - 1:
                   raise
               await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
   ```

3. Add query timeout handling
   ```python
   async def execute(self, query, params, timeout=30):
       return await asyncio.wait_for(
           self._execute_internal(query, params),
           timeout=timeout
       )
   ```

4. Add slow query logging
   ```python
   async def execute(self, query, params):
       start = time.time()
       result = await self._execute_internal(query, params)
       duration = time.time() - start

       if duration > 0.1:  # 100ms threshold
           logger.warning(f"Slow query: {duration:.3f}s - {query}")

       return result
   ```

5. Load test at 1,000 QPS
   ```bash
   # Create load test
   python benchmarks/mysql_load_test.py --qps 1000 --duration 60
   ```

### Day 4-5: ORM Performance Validation (16 hours)

**Create:** `benchmarks/orm_comparison.py`

```python
import time
import asyncio
from covet.database.orm import Model, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

class BenchmarkSuite:
    async def benchmark_simple_select(self):
        # CovetPy
        start = time.perf_counter()
        results = await User.filter(age__gte=18).all()
        covet_time = time.perf_counter() - start

        # SQLAlchemy
        start = time.perf_counter()
        results = await session.execute(select(User).where(User.age >= 18))
        sqlalchemy_time = time.perf_counter() - start

        print(f"CovetPy: {covet_time:.6f}s")
        print(f"SQLAlchemy: {sqlalchemy_time:.6f}s")
        print(f"Speedup: {sqlalchemy_time/covet_time:.2f}x")

    async def benchmark_bulk_insert(self, n=1000):
        # Test bulk insert performance
        pass

    async def benchmark_relationship_loading(self):
        # Test select_related vs N+1 queries
        pass
```

**Implement N+1 Prevention:**
```python
# In covet/database/orm/query.py

class QuerySet:
    def select_related(self, *relations):
        """Load foreign key relationships with JOINs."""
        self._select_related = relations
        return self

    def prefetch_related(self, *relations):
        """Load many-to-many relationships with separate query."""
        self._prefetch_related = relations
        return self

    async def all(self):
        if self._select_related:
            # Generate JOIN query
            query = self._build_join_query()
        elif self._prefetch_related:
            # Execute main query + prefetch queries
            results = await self._execute_main_query()
            await self._prefetch_relations(results)
        else:
            results = await self._execute_simple_query()

        return results
```

### Day 6-7: Backup System Foundation (16 hours)

**File:** `src/covet/database/backup/backup_manager.py`

**Fix imports and implement:**
```python
import asyncio
import gzip
import hashlib
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet

class BackupManager:
    def __init__(self, db_adapter, backup_dir="/backups"):
        self.db_adapter = db_adapter
        self.backup_dir = Path(backup_dir)
        self.encryption_key = self._load_encryption_key()

    async def create_backup(self, backup_type="full"):
        """Create database backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.sql.gz.enc"

        # 1. Export database
        sql_dump = await self._export_database()

        # 2. Compress
        compressed = gzip.compress(sql_dump.encode())

        # 3. Encrypt
        encrypted = self._encrypt_data(compressed)

        # 4. Write to file
        backup_file.write_bytes(encrypted)

        # 5. Verify backup
        is_valid = await self._verify_backup(backup_file)

        # 6. Log backup metadata
        metadata = {
            'timestamp': timestamp,
            'size': backup_file.stat().st_size,
            'checksum': hashlib.sha256(encrypted).hexdigest(),
            'verified': is_valid
        }

        return metadata

    async def restore_backup(self, backup_file):
        """Restore database from backup."""
        # 1. Read backup file
        encrypted = Path(backup_file).read_bytes()

        # 2. Decrypt
        compressed = self._decrypt_data(encrypted)

        # 3. Decompress
        sql_dump = gzip.decompress(compressed).decode()

        # 4. Execute SQL
        await self._import_database(sql_dump)

        # 5. Verify restoration
        is_valid = await self._verify_restoration()

        return is_valid

    async def schedule_automated_backups(self):
        """Schedule daily backups."""
        while True:
            # Run at 2 AM daily
            await asyncio.sleep(self._time_until_2am())
            await self.create_backup()
            await self._cleanup_old_backups(retention_days=30)
```

**Test backup/restore:**
```bash
# Create test script
python -c "
from covet.database.backup import BackupManager
import asyncio

async def test():
    manager = BackupManager(adapter, '/tmp/backups')

    # Create backup
    metadata = await manager.create_backup()
    print(f'Backup created: {metadata}')

    # Restore backup
    result = await manager.restore_backup(metadata['path'])
    print(f'Restore successful: {result}')

asyncio.run(test())
"
```

---

## Week 3: Days 8-14 (Next Week)

### Day 8-9: Slow Query Logging (16 hours)

**File:** `src/covet/database/monitoring/slow_query_logger.py`

```python
import time
import logging
from collections import defaultdict

class SlowQueryLogger:
    def __init__(self, threshold_ms=100):
        self.threshold_ms = threshold_ms
        self.slow_queries = []
        self.stats = defaultdict(lambda: {'count': 0, 'total_time': 0})

    async def log_query(self, query, params, execution_time_ms):
        if execution_time_ms > self.threshold_ms:
            # Get query plan
            query_plan = await self._get_query_plan(query)

            slow_query = {
                'query': query,
                'params': params,
                'execution_time': execution_time_ms,
                'query_plan': query_plan,
                'timestamp': datetime.now()
            }

            self.slow_queries.append(slow_query)
            self.stats[query]['count'] += 1
            self.stats[query]['total_time'] += execution_time_ms

            # Log warning
            logging.warning(
                f"Slow query detected: {execution_time_ms:.2f}ms\n"
                f"Query: {query}\n"
                f"Plan: {query_plan}"
            )

    def get_top_slow_queries(self, limit=10):
        """Get top 10 slowest queries."""
        return sorted(
            self.slow_queries,
            key=lambda x: x['execution_time'],
            reverse=True
        )[:limit]

    def get_most_frequent_slow_queries(self, limit=10):
        """Get most frequently slow queries."""
        return sorted(
            self.stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:limit]
```

**Integration:**
```python
# In database adapter
class DatabaseAdapter:
    def __init__(self, config):
        self.slow_query_logger = SlowQueryLogger(threshold_ms=100)

    async def execute(self, query, params):
        start = time.perf_counter()
        result = await self._execute_internal(query, params)
        duration_ms = (time.perf_counter() - start) * 1000

        await self.slow_query_logger.log_query(query, params, duration_ms)

        return result
```

### Day 10-11: Circuit Breaker Integration (16 hours)

**File:** `src/covet/database/adapters/circuit_breaker.py` (already exists)

**Integrate with adapters:**
```python
from covet.database.adapters.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

class DatabaseAdapter:
    def __init__(self, config):
        cb_config = CircuitBreakerConfig(
            failure_threshold=5,
            timeout=60.0,
            success_threshold=2
        )
        self.circuit_breaker = CircuitBreaker(cb_config)

    async def execute(self, query, params):
        # Check if circuit is open
        if not self.circuit_breaker.can_execute():
            raise CircuitOpenException("Database circuit breaker is OPEN")

        try:
            result = await self._execute_internal(query, params)
            self.circuit_breaker.record_success()
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
```

### Day 12-14: Load Testing Suite (24 hours)

**Create:** `tests/load/database_load_test.py`

```python
import asyncio
import time
from locust import User, task, between, events

class DatabaseLoadTest(User):
    wait_time = between(0.01, 0.1)  # 10-100ms between requests

    @task(80)
    async def read_operation(self):
        """80% read traffic."""
        start = time.perf_counter()
        result = await self.client.execute(
            "SELECT * FROM users WHERE age > 18 LIMIT 100"
        )
        duration = time.perf_counter() - start

        events.request.fire(
            request_type="SELECT",
            name="read_users",
            response_time=duration * 1000,  # ms
            response_length=len(result.rows),
            exception=None,
            context={}
        )

    @task(15)
    async def write_operation(self):
        """15% write traffic."""
        await self.client.execute(
            "INSERT INTO users (name, age) VALUES (%s, %s)",
            ("Test User", 25)
        )

    @task(5)
    async def complex_query(self):
        """5% complex queries."""
        await self.client.execute("""
            SELECT u.*, COUNT(p.id) as post_count
            FROM users u
            LEFT JOIN posts p ON p.user_id = u.id
            GROUP BY u.id
            HAVING post_count > 10
        """)

# Run load test
# locust -f tests/load/database_load_test.py --users 1000 --spawn-rate 100
```

**Automated load test script:**
```bash
#!/bin/bash
# tests/load/run_load_tests.sh

echo "Starting load tests..."

# Test 1: 1,000 QPS baseline
echo "Test 1: 1,000 QPS for 60 seconds"
locust -f database_load_test.py \
    --users 100 --spawn-rate 10 \
    --run-time 60s --headless \
    --csv results_1k_qps

# Test 2: 5,000 QPS stress test
echo "Test 2: 5,000 QPS for 60 seconds"
locust -f database_load_test.py \
    --users 500 --spawn-rate 50 \
    --run-time 60s --headless \
    --csv results_5k_qps

# Test 3: 10,000 QPS extreme test
echo "Test 3: 10,000 QPS for 60 seconds"
locust -f database_load_test.py \
    --users 1000 --spawn-rate 100 \
    --run-time 60s --headless \
    --csv results_10k_qps

echo "Load tests complete. Check results_*.csv"
```

---

## Week 4: Days 15-21 (Validation Week)

### Day 15-16: End-to-End Load Testing
- Run full application load test at 10,000 QPS
- Monitor database performance metrics
- Validate P95 latency < 10ms
- Check for memory leaks

### Day 17-18: Backup/Restore Validation
- Test backup creation
- Test backup restoration
- Verify data integrity
- Measure RTO (Recovery Time Objective)
- Test PITR (Point-in-Time Recovery)

### Day 19-20: Production Deployment Checklist
- [ ] All tests passing (100%)
- [ ] Load tests completed
- [ ] Backup/restore verified
- [ ] Monitoring dashboards created
- [ ] Runbooks documented
- [ ] Team trained
- [ ] SLA commitments defined

### Day 21: Final Sign-Off
- Review all metrics
- Validate production readiness
- Get sign-off from stakeholders
- Plan deployment strategy

---

## Quick Commands

### Run All Database Tests
```bash
pytest tests/database/ -v --tb=short
```

### Run Connection Pool Tests Only
```bash
pytest tests/database/test_connection_pool.py -v
```

### Run Load Tests
```bash
./tests/load/run_load_tests.sh
```

### Create Backup
```bash
python -m covet.database.backup create --type full
```

### Restore Backup
```bash
python -m covet.database.backup restore --file backup_20251013_143000.sql.gz.enc
```

### Run Benchmarks
```bash
python benchmarks/orm_comparison.py --iterations 1000
```

### Check Slow Queries
```bash
python -m covet.database.monitoring.slow_queries --top 10
```

---

## Success Metrics

### Week 2 Goals:
- [ ] Connection pool: 100% tests passing
- [ ] MySQL adapter: Production-ready
- [ ] ORM benchmarks: Completed and documented
- [ ] Backup system: Functional

### Week 3 Goals:
- [ ] N+1 prevention: Implemented
- [ ] Circuit breaker: Integrated
- [ ] Slow query logging: Working
- [ ] Load tests: 1K, 5K, 10K QPS validated

### Week 4 Goals:
- [ ] Full production readiness
- [ ] All documentation complete
- [ ] Team trained
- [ ] Deployment plan ready

---

## Priority Matrix

**DO FIRST (Critical + Urgent):**
1. Backup/restore system
2. ORM performance validation
3. N+1 query prevention

**DO NEXT (Critical + Less Urgent):**
1. MySQL adapter completion
2. Slow query logging
3. Load testing suite

**DO LATER (Important + Less Urgent):**
1. Circuit breaker integration
2. Migration rollback safety
3. Sharding validation

**DO EVENTUALLY (Nice to Have):**
1. Read replica support
2. Cross-region replication
3. Query complexity analysis

---

**Last Updated:** 2025-10-13
**Current Status:** Connection Pool 82.6% Ready
**Target:** 100% Production-Ready in 14-21 days
