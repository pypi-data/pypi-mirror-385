# CovetPy Database Monitoring Guide

Complete guide to monitoring and observability for CovetPy database operations.

## Table of Contents

1. [Overview](#overview)
2. [Query Monitoring](#query-monitoring)
3. [Connection Pool Monitoring](#connection-pool-monitoring)
4. [Integration](#integration)
5. [Alerting](#alerting)
6. [Best Practices](#best-practices)

---

## Overview

CovetPy provides production-grade monitoring for database operations with:

- **Query Performance Tracking**: Identify slow queries and optimization opportunities
- **Connection Pool Monitoring**: Track pool health and prevent exhaustion
- **Real-time Metrics**: Live dashboards and statistics
- **Alerting**: Multiple alert channels for proactive issue detection
- **Historical Analysis**: Trend analysis and performance insights

---

## Query Monitoring

### Quick Start

```python
from covet.database.monitoring import QueryMonitor

# Initialize query monitor
monitor = QueryMonitor(
    slow_query_threshold_ms=1000.0,  # Alert on queries > 1s
    enable_alerting=True,
    enable_logging=True
)

await monitor.start()

# Track a query
await monitor.track_query(
    sql="SELECT * FROM users WHERE id = ?",
    duration_ms=1500.5,
    success=True,
    parameters={'id': 123}
)

# Get slow queries
slow_queries = monitor.get_slow_queries(threshold_ms=500)
for query in slow_queries:
    print(f"Slow query: {query.duration_ms}ms - {query.query[:100]}")

# Get statistics
stats = monitor.get_query_stats(order_by='avg_duration', limit=10)
for stat in stats:
    print(f"{stat.query_pattern[:50]} - Avg: {stat.avg_duration_ms}ms")
```

### Configuration

```python
monitor = QueryMonitor(
    slow_query_threshold_ms=1000.0,     # Slow query threshold
    enable_alerting=True,                # Enable alerts
    enable_logging=True,                 # Log slow queries
    max_history_size=10000,              # Max query history
    stats_retention_hours=24,            # How long to keep stats
)
```

### Query Statistics

The monitor provides comprehensive statistics per query pattern:

```python
stats = monitor.get_query_stats()

for stat in stats:
    print(f"Query: {stat.query_pattern[:100]}")
    print(f"  Executions: {stat.execution_count}")
    print(f"  Avg Duration: {stat.avg_duration_ms:.2f}ms")
    print(f"  Median Duration: {stat.median_duration_ms:.2f}ms")
    print(f"  P95 Duration: {stat.p95_duration_ms:.2f}ms")
    print(f"  P99 Duration: {stat.p99_duration_ms:.2f}ms")
    print(f"  Error Rate: {stat.error_rate:.2f}%")
```

### Performance Reports

Generate text-based performance reports:

```python
report = monitor.generate_report()
print(report)
```

Output:
```
================================================================================
QUERY PERFORMANCE REPORT
================================================================================

OVERALL METRICS:
  Total Queries: 1,234
  Slow Queries: 45 (3.65%)
  Errors: 12 (0.97%)
  Unique Patterns: 67
  Threshold: 1000ms

TOP 5 SLOWEST QUERIES (by avg duration):
  1. SELECT * FROM orders WHERE user_id = ? AND status IN (...)...
     Avg: 2,345.67ms, P95: 3,456.78ms, Executions: 123
  ...
```

### Alert Handlers

Add custom alert handlers for slow queries:

```python
async def webhook_alert(alert: SlowQueryAlert):
    """Send alert to webhook."""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        await session.post(
            'https://alerts.example.com/webhook',
            json=alert.to_dict()
        )

def log_alert(alert: SlowQueryAlert):
    """Log alert to file."""
    with open('slow_queries.log', 'a') as f:
        f.write(f"{alert.timestamp}: {alert.query[:100]} - {alert.duration_ms}ms\n")

monitor.add_alert_handler(webhook_alert)
monitor.add_alert_handler(log_alert)
```

---

## Connection Pool Monitoring

### Quick Start

```python
from covet.database.monitoring import ConnectionPoolMonitor

# Initialize pool monitor
pool_monitor = ConnectionPoolMonitor(
    pool_size=20,
    health_check_interval=60,  # Health check every 60s
    exhaustion_threshold=0.9,   # Alert at 90% utilization
)

await pool_monitor.start()

# Record pool operations
pool_monitor.record_checkout()  # Connection checked out
pool_monitor.record_wait_time(150.5)  # Waited 150.5ms
pool_monitor.record_checkin()  # Connection returned

# Get current snapshot
snapshot = pool_monitor.get_current_snapshot()
print(f"Pool Utilization: {snapshot.utilization_percent:.1f}%")
print(f"Active: {snapshot.active_connections}/{snapshot.pool_size}")
print(f"Waiting: {snapshot.waiting_count}")

# Display dashboard
print(pool_monitor.generate_dashboard())
```

### Configuration

```python
pool_monitor = ConnectionPoolMonitor(
    pool_size=20,                    # Maximum pool size
    health_check_interval=60,        # Seconds between health checks
    snapshot_history_size=1000,      # Historical snapshots to keep
    exhaustion_threshold=0.9,        # Utilization % for alerts (0-1)
    high_wait_time_ms=1000.0,       # Wait time threshold for alerts
    enable_alerting=True,            # Enable alerts
)
```

### Health Checks

Set up automated health checks:

```python
async def db_health_check():
    """Check database connectivity."""
    try:
        # Ping database
        async with db.session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception:
        return False

pool_monitor.set_health_check_callback(db_health_check)
```

### Dashboard

The pool monitor provides a real-time text-based dashboard:

```python
dashboard = pool_monitor.generate_dashboard()
print(dashboard)
```

Output:
```
================================================================================
CONNECTION POOL DASHBOARD
================================================================================

STATUS: 🟢 HEALTHY

CURRENT STATE:
  Pool Size: 20
  Active: 8
  Idle: 12
  Waiting: 0
  Utilization: [████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 40.0%

PERFORMANCE:
  Avg Wait Time: 25.50ms
  Checkouts: 1,234
  Checkins: 1,234
  Timeouts: 0 (0.00%)
  Errors: 2 (0.16%)

STATISTICS:
  Peak Active: 15
  Peak Waiting: 3
  Health Checks: 98.5% success

RECENT HEALTH CHECKS:
  ✓ 14:32:15 - 12.50ms
  ✓ 14:31:15 - 11.25ms
  ✓ 14:30:15 - 13.75ms

TREND ANALYSIS (last 5 min):
  Utilization: → Stable
  Wait Time: ↘ Decreasing (5.0ms)

================================================================================
```

### Metrics

Get detailed pool metrics:

```python
metrics = pool_monitor.get_metrics()
print(f"Total Checkouts: {metrics.total_checkouts}")
print(f"Avg Wait Time: {metrics.avg_wait_time_ms:.2f}ms")
print(f"Timeout Rate: {metrics.timeout_rate:.2f}%")
print(f"Health Check Success: {metrics.health_check_success_rate:.1f}%")
```

### Alert Handlers

Add custom pool alert handlers:

```python
async def pool_alert_handler(alert_type: str, data: dict):
    """Handle pool alerts."""
    if alert_type == 'pool_exhaustion':
        # Pool is near exhaustion
        utilization = data['utilization_percent']
        print(f"ALERT: Pool at {utilization:.1f}% capacity!")

    elif alert_type == 'high_wait_time':
        wait_time = data['wait_time_ms']
        print(f"ALERT: High wait time: {wait_time:.0f}ms")

    elif alert_type == 'connection_timeout':
        print("ALERT: Connection timeout!")

    elif alert_type == 'health_check_failed':
        print(f"ALERT: Health check failed: {data}")

pool_monitor.add_alert_handler(pool_alert_handler)
```

---

## Integration

### Integrate with DatabaseSystem

```python
from covet.database import DatabaseSystem
from covet.database.monitoring import QueryMonitor, ConnectionPoolMonitor

# Initialize monitoring
query_monitor = await initialize_query_monitor(slow_query_threshold_ms=1000)
pool_monitor = await initialize_pool_monitor(pool_size=20)

# Initialize database system
db_system = DatabaseSystem()
await db_system.initialize({
    'databases': {
        'primary': {
            'host': 'localhost',
            'port': 5432,
            'database': 'myapp',
            'db_type': 'postgresql'
        }
    },
    'enable_monitoring': True,
    'connection_pool_size': 20,
})

# Hook into database operations
original_execute = db_system.execute_raw_query

async def monitored_execute(query, parameters=None, database='default'):
    """Wrap query execution with monitoring."""
    start_time = time.time()

    try:
        result = await original_execute(query, parameters, database)
        duration_ms = (time.time() - start_time) * 1000

        await query_monitor.track_query(
            sql=query,
            duration_ms=duration_ms,
            success=True
        )

        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        await query_monitor.track_query(
            sql=query,
            duration_ms=duration_ms,
            success=False,
            error=str(e)
        )

        raise

db_system.execute_raw_query = monitored_execute
```

### Integrate with Connection Pool

```python
class MonitoredConnectionPool:
    """Connection pool with monitoring."""

    def __init__(self, pool_size=20):
        self.pool = ConnectionPool(pool_size)
        self.monitor = ConnectionPoolMonitor(pool_size=pool_size)

    async def checkout(self):
        """Checkout connection with monitoring."""
        start_time = time.time()

        try:
            conn = await self.pool.checkout()
            wait_time_ms = (time.time() - start_time) * 1000

            self.monitor.record_checkout()
            self.monitor.record_wait_time(wait_time_ms)

            return conn

        except TimeoutError:
            self.monitor.record_timeout()
            raise

        except Exception as e:
            self.monitor.record_error(str(e))
            raise

    async def checkin(self, conn):
        """Return connection with monitoring."""
        await self.pool.checkin(conn)
        self.monitor.record_checkin()
```

---

## Alerting

### Email Alerts

```python
import smtplib
from email.message import EmailMessage

async def email_alert_handler(alert: SlowQueryAlert):
    """Send email alert for slow queries."""
    msg = EmailMessage()
    msg['Subject'] = f'Slow Query Alert: {alert.duration_ms:.0f}ms'
    msg['From'] = 'alerts@example.com'
    msg['To'] = 'dba@example.com'

    msg.set_content(f"""
    Slow query detected:

    Duration: {alert.duration_ms:.2f}ms
    Threshold: {alert.threshold_ms:.2f}ms
    Severity: {alert._get_severity()}
    Query: {alert.query[:500]}
    Timestamp: {alert.timestamp}
    """)

    # Send email
    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)

query_monitor.add_alert_handler(email_alert_handler)
```

### Webhook Alerts

```python
async def webhook_alert_handler(alert: SlowQueryAlert):
    """Send alert to monitoring service."""
    import aiohttp

    async with aiohttp.ClientSession() as session:
        await session.post(
            'https://monitoring.example.com/api/alerts',
            json={
                'type': 'slow_query',
                'severity': alert._get_severity(),
                'duration_ms': alert.duration_ms,
                'query': alert.query[:200],
                'timestamp': alert.timestamp.isoformat(),
            },
            headers={'Authorization': 'Bearer YOUR_API_KEY'}
        )

query_monitor.add_alert_handler(webhook_alert_handler)
```

### Slack Alerts

```python
async def slack_alert_handler(alert: SlowQueryAlert):
    """Send alert to Slack."""
    import aiohttp

    webhook_url = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

    severity_emoji = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🔵',
    }

    emoji = severity_emoji.get(alert._get_severity(), '⚪')

    message = {
        'text': f'{emoji} Slow Query Alert',
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Slow Query Detected*\n'
                            f'Duration: *{alert.duration_ms:.0f}ms*\n'
                            f'Severity: `{alert._get_severity()}`'
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'```{alert.query[:300]}```'
                }
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json=message)

query_monitor.add_alert_handler(slack_alert_handler)
```

---

## Best Practices

### 1. Set Appropriate Thresholds

```python
# Development
query_monitor = QueryMonitor(slow_query_threshold_ms=500)

# Production
query_monitor = QueryMonitor(slow_query_threshold_ms=1000)

# Critical systems
query_monitor = QueryMonitor(slow_query_threshold_ms=100)
```

### 2. Monitor Pool Utilization

```python
# Alert at 80% for warning, 90% for critical
pool_monitor = ConnectionPoolMonitor(
    pool_size=20,
    exhaustion_threshold=0.8,
)

# Monitor continuously
async def monitor_loop():
    while True:
        await asyncio.sleep(10)
        snapshot = pool_monitor.get_current_snapshot()

        if snapshot.utilization_percent > 80:
            logger.warning(f"High pool utilization: {snapshot.utilization_percent}%")
```

### 3. Regular Performance Reviews

```python
# Generate daily reports
async def daily_report():
    """Generate and email daily performance report."""
    report = query_monitor.generate_report()

    # Email to team
    await send_email(
        to='team@example.com',
        subject='Daily Database Performance Report',
        body=report
    )

# Schedule daily at midnight
scheduler.schedule(daily_report, cron='0 0 * * *')
```

### 4. Implement Query Caching

```python
# Cache frequently executed queries
slow_queries = monitor.get_slow_queries()
frequent_queries = monitor.get_most_frequent_queries()

# Identify candidates for caching
for query in frequent_queries:
    if query['execution_count'] > 1000:
        print(f"Cache candidate: {query['query_pattern'][:100]}")
```

### 5. Optimize Based on Metrics

```python
# Find optimization opportunities
stats = query_monitor.get_query_stats(order_by='avg_duration')

for stat in stats[:10]:  # Top 10 slowest
    print(f"\nOptimization Target:")
    print(f"  Query: {stat.query_pattern[:100]}")
    print(f"  Avg Duration: {stat.avg_duration_ms:.2f}ms")
    print(f"  Executions: {stat.execution_count}")
    print(f"  Total Time: {stat.total_duration_ms:.0f}ms")

    # Optimization suggestions
    if 'SELECT *' in stat.query_pattern:
        print("  → Consider selecting specific columns")
    if 'WHERE' not in stat.query_pattern and stat.execution_count > 100:
        print("  → Add indexes or filtering")
```

### 6. Cleanup and Retention

```python
# Configure appropriate retention
query_monitor = QueryMonitor(
    stats_retention_hours=24,  # Keep stats for 24 hours
    max_history_size=10000,    # Limit history size
)

# Manual cleanup if needed
query_monitor.clear_history()
```

---

## Troubleshooting

### High Memory Usage

If monitoring consumes too much memory:

```python
# Reduce history size
query_monitor = QueryMonitor(
    max_history_size=1000,      # Reduce from 10000
    stats_retention_hours=12,   # Reduce from 24
)

# Limit duration tracking
# (keeps only last 100 durations per query pattern)
```

### Missing Metrics

Ensure monitors are started:

```python
await query_monitor.start()
await pool_monitor.start()
```

### Alert Flood

Implement rate limiting:

```python
class RateLimitedAlertHandler:
    def __init__(self, handler, max_per_minute=10):
        self.handler = handler
        self.max_per_minute = max_per_minute
        self.recent_alerts = []

    async def __call__(self, alert):
        now = time.time()

        # Remove old alerts
        self.recent_alerts = [
            t for t in self.recent_alerts
            if now - t < 60
        ]

        # Check rate limit
        if len(self.recent_alerts) < self.max_per_minute:
            self.recent_alerts.append(now)
            await self.handler(alert)
        else:
            logger.warning("Alert rate limit exceeded")

# Use rate-limited handler
limited_handler = RateLimitedAlertHandler(email_alert_handler)
query_monitor.add_alert_handler(limited_handler)
```

---

## Summary

CovetPy's monitoring system provides production-grade observability with:

- Comprehensive query performance tracking
- Real-time connection pool monitoring
- Flexible alerting system
- Historical analysis and reporting
- Easy integration with existing code

For more information, see:
- [Database System Guide](./DATABASE_SYSTEM_GUIDE.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)
- [API Reference](./API_REFERENCE.md)
