# CovetPy Monitoring - Quick Start Guide

## 5-Minute Setup

### 1. Start Monitoring Stack

```bash
cd /Users/vipin/Downloads/NeutrinoPy

# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose -f docker-compose.monitoring.yml ps
```

### 2. Verify Services Running

```bash
# Check all services are up
docker-compose -f docker-compose.monitoring.yml ps

# Should show:
# ✅ covetpy-prometheus   - Up
# ✅ covetpy-grafana      - Up
# ✅ covetpy-alertmanager - Up
# ✅ covetpy-postgres     - Up
# ✅ covetpy-redis        - Up
# ✅ postgres-exporter    - Up
# ✅ redis-exporter       - Up
# ✅ node-exporter        - Up
```

### 3. Access Dashboards

Open in your browser:

- **Grafana:** http://localhost:3000
  - Username: `admin`
  - Password: `admin`
  - Navigate to Dashboards → CovetPy folder
  - 8 dashboards available

- **Prometheus:** http://localhost:9090
  - Query metrics: `covet_db_connections_active`
  - View targets: Status → Targets
  - View alerts: Alerts

- **AlertManager:** http://localhost:9093
  - View active alerts
  - Silence alerts
  - Test notifications

### 4. Verify Metrics Collection

```bash
# Check metrics endpoint
curl http://localhost:9090/metrics | grep covet_

# Should return 38+ metrics like:
# covet_db_connections_active
# covet_system_cpu_usage_percent
# covet_http_requests_total
# etc.

# Query Prometheus
curl 'http://localhost:9090/api/v1/query?query=up' | jq

# Check health endpoints
curl http://localhost:8000/health | jq
curl http://localhost:8000/health/ready | jq
```

### 5. View Dashboards

In Grafana (http://localhost:3000):

1. **Login:** admin/admin (change password when prompted)
2. **Navigate:** Dashboards → Browse → CovetPy folder
3. **Open:** Any of the 8 dashboards
4. **Explore:** Click on graphs to drill down

**Recommended First Dashboards:**
- **System Health:** Overall system status
- **Database Connection Pool:** Database performance
- **Business Metrics:** Application usage

### 6. Test Alerting (Optional)

```bash
# Send test alert to AlertManager
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning",
      "instance": "localhost"
    },
    "annotations": {
      "summary": "Test Alert from Quick Start",
      "description": "This is a test alert to verify notification delivery"
    }
  }]'

# Check alert in AlertManager UI
open http://localhost:9093

# Check email in Mailhog (test email system)
open http://localhost:8025
```

## Common Commands

### Service Management

```bash
# Start monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Stop monitoring
docker-compose -f docker-compose.monitoring.yml down

# Restart specific service
docker-compose -f docker-compose.monitoring.yml restart grafana

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
docker-compose -f docker-compose.monitoring.yml logs -f grafana
docker-compose -f docker-compose.monitoring.yml logs -f alertmanager
```

### Monitoring Commands

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Query metrics
curl 'http://localhost:9090/api/v1/query?query=covet_db_connections_active' | jq

# Check alert rules
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].name'

# Check health
curl http://localhost:8000/health | jq '.status'
```

### Troubleshooting

```bash
# If Grafana shows "no data":
# 1. Check Prometheus is scraping
curl http://localhost:9090/api/v1/targets | jq

# 2. Check datasource in Grafana
curl -u admin:admin http://localhost:3000/api/datasources | jq

# 3. Test query manually
curl 'http://localhost:9090/api/v1/query?query=up'

# If alerts not firing:
# 1. Check alert rules loaded
curl http://localhost:9090/api/v1/rules

# 2. Check AlertManager status
curl http://localhost:9093/api/v2/status

# 3. View AlertManager logs
docker logs covetpy-alertmanager
```

## What's Included

### Dashboards (8)
1. Database Connection Pool - Monitor pool health, leaks, wait times
2. Query Performance - Track query latency, slow queries, errors
3. Security Metrics - Authentication, rate limits, suspicious activity
4. System Health - CPU, memory, disk, load average
5. Cache Performance - Hit rates, evictions, memory usage
6. Business Metrics - Request counts, top endpoints, success rates
7. Backup Status - Last backup time, size, success rate
8. Migration Status - Pending/running migrations, success rate

### Metrics (38+)
- Database: 10 metrics (connections, queries, performance)
- System: 8 metrics (CPU, memory, disk, network)
- HTTP: 6 metrics (requests, latency, errors)
- Cache: 5 metrics (hits, misses, memory)
- Health: 3 metrics (status checks)
- Backup/Migration: 6 metrics (status, duration)

### Alerts (25+)
- Critical: 8 alerts (pool exhausted, disk full, service down, etc.)
- High: 10 alerts (high latency, memory, errors, etc.)
- Medium: 5 alerts (auth failures, rate limits, etc.)
- Low: 2 alerts (informational)

### Runbooks (8)
Operational procedures in `/docs/operations/runbooks/`:
1. Database Connection Pool Exhausted
2. High Query Latency
3. Disk Space Critical
4. High Memory Usage
5. Backup Failure
6. Migration Stuck
7. High Error Rate
8. Authentication Failure Spike

## Next Steps

1. **Customize Alerts:**
   - Edit `/infrastructure/monitoring/rules/covetpy_alerts.yml`
   - Adjust thresholds for your environment
   - Add alert notification emails/Slack webhooks

2. **Configure Notifications:**
   - Edit `/infrastructure/monitoring/alertmanager.yml`
   - Set Slack webhook URL
   - Set PagerDuty routing keys
   - Configure email addresses

3. **Review Dashboards:**
   - Customize panels for your metrics
   - Add business-specific metrics
   - Create team-specific dashboards

4. **Production Deployment:**
   - Change default passwords
   - Enable HTTPS
   - Configure persistent volumes
   - Set up backups
   - Review security checklist

## Documentation

- **Complete Guide:** `/infrastructure/monitoring/README.md`
- **Completion Report:** `/docs/TEAM_11_COMPLETION_REPORT.md`
- **Runbooks:** `/docs/operations/runbooks/*.md`
- **Test Suite:** `/tests/monitoring/*.py`

## Support

- **Issues:** Check logs, review troubleshooting section
- **Documentation:** See `/infrastructure/monitoring/README.md`
- **Tests:** Run `pytest tests/monitoring/ -v`

## Summary

You now have:
✅ Prometheus collecting 38+ metrics every 15 seconds
✅ Grafana with 8 production dashboards
✅ AlertManager with 25+ alert rules
✅ Real health checks (database, Redis, disk, memory)
✅ 8 operational runbooks
✅ 60+ integration tests
✅ Complete documentation

**Time to value:** 5 minutes to full observability!

---

**Happy Monitoring! 🎯📊🚀**
