# Runbook: High HTTP Error Rate

## Alert Details
- **Alert Name:** `HighHTTPErrorRate`
- **Severity:** HIGH
- **Threshold:** 5xx error rate > 1% for 3 minutes
- **SLA:** 5 minutes to acknowledge, 20 minutes to mitigate

## Symptoms
- HTTP 5xx error rate > 1%
- User complaints of errors
- Degraded service availability

## Investigation
```bash
# Check current error rate
curl 'http://localhost:9090/api/v1/query?query=sum(rate(covet_http_5xx_responses[5m]))/sum(rate(covet_http_requests_total[5m]))*100'

# Check which endpoints are failing
curl 'http://localhost:9090/api/v1/query?query=topk(10,sum(rate(covet_http_5xx_responses[5m]))by(endpoint))'

# Check application logs
docker logs covetpy-app --tail 200 | grep ERROR

# Check exception types
curl 'http://localhost:9090/api/v1/query?query=sum(rate(covet_http_exceptions_total[5m]))by(exception_type)'
```

## Resolution

### Immediate Actions
1. **Check recent deployments**
   ```bash
   # Rollback if recent deployment
   kubectl rollout undo deployment/covetpy-app
   ```

2. **Check dependencies**
   ```bash
   # Verify database
   curl http://localhost:8000/health | jq '.checks.database'

   # Verify Redis
   curl http://localhost:8000/health | jq '.checks.redis'
   ```

3. **Restart service** (if health checks failing)
   ```bash
   docker restart covetpy-app
   ```

### Root Cause Analysis
```bash
# Analyze error patterns
docker logs covetpy-app | grep -A 5 "500 Internal Server Error"

# Check for common errors
# - Database connection errors
# - Redis connection errors
# - Null pointer exceptions
# - Timeout errors
```

## Verification
```bash
# Verify error rate decreased
curl 'http://localhost:9090/api/v1/query?query=sum(rate(covet_http_5xx_responses[5m]))/sum(rate(covet_http_requests_total[5m]))*100'
# Should be < 0.1%
```

## Post-Incident
- Add tests to prevent regression
- Improve error handling in affected endpoints
- Add detailed logging for error scenarios

## References
- [HTTP Metrics Dashboard](http://localhost:3000/d/covetpy-http)
- [Application Logs](http://localhost:3000/explore)
