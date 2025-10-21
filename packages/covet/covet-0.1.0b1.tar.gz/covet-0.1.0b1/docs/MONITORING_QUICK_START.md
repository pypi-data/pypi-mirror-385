# CovetPy Database Monitoring - Quick Start Guide

Get up and running with database monitoring in 5 minutes.

## Installation

```bash
pip install covetpy[database]
```

## Basic Setup (30 seconds)

```python
from covet.database.monitoring import QueryMonitor, ConnectionPoolMonitor

# Query monitoring
query_monitor = QueryMonitor(slow_query_threshold_ms=1000)
await query_monitor.start()

# Pool monitoring
pool_monitor = ConnectionPoolMonitor(pool_size=20)
await pool_monitor.start()
```

## Track Queries (Copy & Paste)

```python
import time

async def execute_with_monitoring(sql, params=None):
    """Execute query with automatic monitoring."""
    start = time.time()

    try:
        result = await db.execute(sql, params)
        duration_ms = (time.time() - start) * 1000

        await query_monitor.track_query(
            sql=sql,
            duration_ms=duration_ms,
            success=True,
            parameters=params
        )

        return result

    except Exception as e:
        duration_ms = (time.time() - start) * 1000

        await query_monitor.track_query(
            sql=sql,
            duration_ms=duration_ms,
            success=False,
            error=str(e)
        )

        raise
```

## Monitor Pool (Copy & Paste)

```python
class MonitoredPool:
    """Connection pool with monitoring."""

    def __init__(self, pool):
        self.pool = pool
        self.monitor = pool_monitor

    async def get_connection(self):
        start = time.time()

        conn = await self.pool.get()

        wait_time_ms = (time.time() - start) * 1000
        self.monitor.record_checkout()
        self.monitor.record_wait_time(wait_time_ms)

        return conn

    async def release(self, conn):
        await self.pool.release(conn)
        self.monitor.record_checkin()
```

## Get Insights (Run Anytime)

```python
# Slow queries
slow = query_monitor.get_slow_queries()
print(f"Found {len(slow)} slow queries")

# Top slowest
for query in query_monitor.get_top_slow_queries(limit=5):
    print(f"{query['avg_duration_ms']:.0f}ms: {query['query_pattern'][:80]}")

# Pool status
print(pool_monitor.generate_dashboard())

# Metrics
metrics = query_monitor.get_metrics()
print(f"Total queries: {metrics['total_queries']}")
print(f"Slow query rate: {metrics['slow_query_rate']:.2f}%")
```

## Add Alerts (Optional)

### Slack Alert

```python
async def slack_alert(alert):
    import aiohttp
    webhook = "YOUR_SLACK_WEBHOOK_URL"

    async with aiohttp.ClientSession() as session:
        await session.post(webhook, json={
            'text': f'Slow Query: {alert.duration_ms:.0f}ms'
        })

query_monitor.add_alert_handler(slack_alert)
```

### Email Alert

```python
def email_alert(alert):
    import smtplib
    from email.message import EmailMessage

    msg = EmailMessage()
    msg['Subject'] = f'Slow Query: {alert.duration_ms:.0f}ms'
    msg['From'] = 'alerts@yourapp.com'
    msg['To'] = 'team@yourapp.com'
    msg.set_content(alert.query[:200])

    with smtplib.SMTP('localhost') as smtp:
        smtp.send_message(msg)

query_monitor.add_alert_handler(email_alert)
```

## Production Checklist

- [ ] Set appropriate slow query threshold
- [ ] Configure alert handlers
- [ ] Set up health checks
- [ ] Configure log retention
- [ ] Test alerts
- [ ] Monitor the monitors

## Common Configurations

### Development
```python
QueryMonitor(slow_query_threshold_ms=500)
```

### Staging
```python
QueryMonitor(slow_query_threshold_ms=1000)
```

### Production
```python
QueryMonitor(
    slow_query_threshold_ms=1000,
    enable_alerting=True,
    stats_retention_hours=24
)
```

### High Traffic
```python
QueryMonitor(
    slow_query_threshold_ms=2000,
    max_history_size=50000,
    stats_retention_hours=72
)
```

## Useful Commands

```python
# Generate report
print(query_monitor.generate_report())

# Clear history
query_monitor.clear_history()

# Get error-prone queries
errors = query_monitor.get_error_prone_queries()

# Get frequent queries
frequent = query_monitor.get_most_frequent_queries()

# Pool dashboard
print(pool_monitor.generate_dashboard())

# Stop monitoring
await query_monitor.stop()
await pool_monitor.stop()
```

## Need More?

- Full Guide: [DATABASE_MONITORING_GUIDE.md](./DATABASE_MONITORING_GUIDE.md)
- API Reference: [monitoring/README.md](../src/covet/database/monitoring/README.md)
- Examples: [tests/integration/](../tests/integration/)

---

**You're all set!** Start monitoring and get insights into your database performance.
