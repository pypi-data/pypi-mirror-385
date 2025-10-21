# Runbook: Database Connection Pool Exhausted

## Alert Details
- **Alert Name:** `DatabaseConnectionPoolExhausted`
- **Severity:** CRITICAL
- **SLA:** 5 minutes to acknowledge, 15 minutes to resolve

## Symptoms
- Database connection pool utilization > 95%
- Application unable to acquire database connections
- Increased request timeouts
- 503 Service Unavailable errors
- Queue of waiting requests growing

## Impact
- **User Impact:** HIGH - Users cannot access database-dependent features
- **Business Impact:** HIGH - Transaction processing stopped
- **Data Impact:** MEDIUM - No data loss, but operations blocked

## Root Causes
1. Connection leaks (connections not properly released)
2. Sudden traffic spike exceeding pool capacity
3. Slow queries holding connections too long
4. Pool configuration too small for workload
5. Database performance degradation

## Investigation Steps

### 1. Check Current Pool Status
```bash
# View Grafana dashboard
open http://localhost:3000/d/covetpy-db-pool

# Check metrics via Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=covet_db_connections_active'
curl -s 'http://localhost:9090/api/v1/query?query=covet_db_connections_idle'
curl -s 'http://localhost:9090/api/v1/query?query=covet_db_connections_leaked_total'
```

### 2. Identify Connection Leaks
```bash
# Check for leaked connections
docker exec covetpy-app python -c "
from covet.database.monitoring.pool_monitor import get_pool_monitor
monitor = get_pool_monitor()
print(monitor.generate_dashboard())
"

# Look for connections in 'idle in transaction' state
docker exec postgres psql -U covetpy -c "
SELECT pid, state, query_start, state_change
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND query_start < NOW() - INTERVAL '5 minutes'
ORDER BY query_start;"
```

### 3. Analyze Slow Queries
```bash
# Check for long-running queries
docker exec postgres psql -U covetpy -c "
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC
LIMIT 10;"
```

### 4. Review Recent Traffic
```bash
# Check request rate spike
curl -s 'http://localhost:9090/api/v1/query?query=rate(covet_http_requests_total[5m])'

# Check error rate
curl -s 'http://localhost:9090/api/v1/query?query=rate(covet_http_5xx_responses[5m])'
```

## Resolution Steps

### Immediate Actions (< 5 minutes)

#### Option 1: Restart Application (Fastest)
```bash
# Restart to release all connections
docker restart covetpy-app

# Wait for health checks
watch -n 2 'curl -s http://localhost:8000/health | jq .status'
```

#### Option 2: Kill Leaked Connections
```bash
# Terminate idle in transaction connections
docker exec postgres psql -U covetpy -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND query_start < NOW() - INTERVAL '5 minutes';"
```

#### Option 3: Increase Pool Size (Temporary)
```bash
# Edit environment variable
docker exec covetpy-app sh -c '
export DATABASE_POOL_SIZE=40
export DATABASE_MAX_OVERFLOW=20
kill -HUP 1  # Reload config
'
```

### Short-term Fixes (< 30 minutes)

#### Fix Connection Leaks in Code
```python
# Add connection timeout monitoring
from covet.database.monitoring import get_pool_monitor

monitor = get_pool_monitor()

# Set alert on high wait times
monitor.record_wait_time(wait_time_ms)
if wait_time_ms > 1000:
    logger.error("High connection wait time detected")
```

#### Optimize Slow Queries
```bash
# Identify top slow queries
docker exec covetpy-app python -c "
from covet.database.monitoring.query_monitor import get_query_monitor
monitor = get_query_monitor()
print(monitor.generate_report())
"

# Add indexes for slow queries
docker exec postgres psql -U covetpy -c "
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
"
```

### Long-term Solutions

1. **Implement Connection Pooling Best Practices**
   - Use context managers for all database operations
   - Set connection timeouts: `pool_timeout=30`
   - Enable pool pre-ping: `pool_pre_ping=True`
   - Configure pool recycling: `pool_recycle=3600`

2. **Add Monitoring and Alerts**
   - Alert on pool utilization > 80% (warning)
   - Alert on pool utilization > 90% (critical)
   - Dashboard for connection wait times
   - Track connection lease duration

3. **Optimize Database Configuration**
   ```sql
   -- Increase max connections
   ALTER SYSTEM SET max_connections = '200';

   -- Set idle connection timeout
   ALTER SYSTEM SET idle_in_transaction_session_timeout = '300000';  -- 5 min

   -- Reload configuration
   SELECT pg_reload_conf();
   ```

4. **Implement Circuit Breaker**
   ```python
   from covet.resilience import CircuitBreaker

   @CircuitBreaker(failure_threshold=5, recovery_timeout=60)
   async def database_operation():
       async with db_pool.acquire() as conn:
           return await conn.fetch(query)
   ```

## Verification

### Success Criteria
- Pool utilization < 70%
- Connection wait time < 100ms (P95)
- No connection timeouts in last 5 minutes
- No 503 errors
- Application responding normally

### Verification Commands
```bash
# Check pool metrics
curl -s 'http://localhost:9090/api/v1/query?query=(covet_db_connections_active/covet_db_connection_pool_size)*100'

# Verify health
curl http://localhost:8000/health | jq '.checks.connection_pool'

# Check error rate
curl -s 'http://localhost:9090/api/v1/query?query=rate(covet_http_5xx_responses[5m])' | jq '.data.result[0].value[1]'
```

## Post-Incident

### 1. Root Cause Analysis
- Review application logs for connection leak patterns
- Analyze slow query patterns
- Check for correlation with deployment or traffic changes

### 2. Documentation
- Document connection leak locations
- Update code patterns to prevent recurrence
- Share learnings with team

### 3. Preventive Measures
- Add unit tests for connection management
- Implement code review checklist for database operations
- Set up proactive alerts for early warning

## Escalation

### Level 1: On-Call Engineer (You)
- Follow this runbook
- Attempt immediate resolution

### Level 2: Database Team
Contact if:
- Pool exhaustion persists after restart
- Database server itself is slow
- Connection leak in database layer suspected

Slack: `#database-team`
Email: `dba@covetpy.io`

### Level 3: Engineering Lead
Contact if:
- Issue not resolved in 30 minutes
- Business-critical impact
- Multiple services affected

Phone: +1-XXX-XXX-XXXX
Slack: `@engineering-lead`

## References
- [Connection Pool Monitoring Dashboard](http://localhost:3000/d/covetpy-db-pool)
- [Database Performance Dashboard](http://localhost:3000/d/covetpy-query-perf)
- [CovetPy Database Documentation](../../../README.md)
- [PostgreSQL Connection Pooling Best Practices](https://www.postgresql.org/docs/current/runtime-config-connection.html)

## Change Log
- 2024-01-15: Initial version
- 2024-01-20: Added circuit breaker pattern
