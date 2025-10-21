# Runbook: High Query Latency

## Alert Details
- **Alert Name:** `DatabaseHighQueryLatency`
- **Severity:** HIGH
- **Threshold:** P95 latency > 500ms for 5 minutes
- **SLA:** 10 minutes to acknowledge, 30 minutes to mitigate

## Symptoms
- Slow page loads and API responses
- Database query P95 latency > 500ms
- Increased user complaints
- Request timeouts

## Investigation
```bash
# Check current latency
curl 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(covet_db_query_duration_seconds_bucket[5m]))'

# Identify slow queries
docker exec covetpy-app python -c "
from covet.database.monitoring.query_monitor import get_query_monitor
print(get_query_monitor().get_top_slow_queries(limit=10))
"

# Check database load
docker exec postgres psql -U covetpy -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

## Resolution
1. **Identify slow queries** from monitoring
2. **Add missing indexes**
   ```sql
   CREATE INDEX CONCURRENTLY idx_name ON table(column);
   ```
3. **Optimize queries** - Use EXPLAIN ANALYZE
4. **Scale read replicas** if read-heavy
5. **Enable query caching** for frequent queries

## Verification
```bash
# Verify latency improved
curl 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(covet_db_query_duration_seconds_bucket[5m]))'
# Should be < 500ms
```

## References
- [Query Performance Dashboard](http://localhost:3000/d/covetpy-query-perf)
