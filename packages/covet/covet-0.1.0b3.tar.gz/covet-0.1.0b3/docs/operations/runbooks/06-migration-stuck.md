# Runbook: Database Migration Stuck

## Alert Details
- **Alert Name:** `MigrationStuck`
- **Severity:** HIGH
- **Threshold:** Migration running > 30 minutes
- **SLA:** 1 hour to resolve

## Symptoms
- Migration job running for > 30 minutes
- Application deployment blocked
- Database locked by migration
- Users unable to access features

## Investigation
```bash
# Check running migrations
curl 'http://localhost:9090/api/v1/query?query=covet_migration_running_total'

# Check database locks
docker exec postgres psql -U covetpy -c "
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE query LIKE '%ALTER TABLE%' OR query LIKE '%CREATE INDEX%';"

# Check long-running transactions
docker exec postgres psql -U covetpy -c "
SELECT pid, now() - query_start AS duration, state, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;"
```

## Resolution

### Option 1: Wait (if acceptable)
```bash
# Monitor progress
watch -n 30 'docker logs covetpy-app --tail 50 | grep migration'
```

### Option 2: Cancel Migration
```bash
# Find migration PID
docker exec postgres psql -U covetpy -c "
SELECT pid FROM pg_stat_activity
WHERE query LIKE '%migration%' AND state = 'active';"

# Kill the migration (carefully!)
docker exec postgres psql -U covetpy -c "SELECT pg_cancel_backend(PID_HERE);"

# Rollback application deployment
kubectl rollout undo deployment/covetpy-app
```

### Option 3: Optimize and Retry
```bash
# Create index concurrently instead
docker exec postgres psql -U covetpy -c "
CREATE INDEX CONCURRENTLY idx_name ON table(column);"

# Use smaller batch sizes for data migrations
```

## Prevention
- Test migrations on production-sized data
- Use CONCURRENTLY for index creation
- Break large migrations into smaller steps
- Schedule migrations during low-traffic windows

## Verification
```bash
# Verify migration completed
docker exec covetpy-app python manage.py migrate --check

# Verify application healthy
curl http://localhost:8000/health
```
