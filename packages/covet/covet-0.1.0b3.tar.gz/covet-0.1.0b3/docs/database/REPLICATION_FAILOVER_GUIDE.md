# Read Replica Failover Guide

## Production Operations Manual for Database Replication and Failover

This guide provides comprehensive operational procedures for managing read replicas and handling failover scenarios in production environments.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Setup and Configuration](#setup-and-configuration)
3. [Health Monitoring](#health-monitoring)
4. [Failover Procedures](#failover-procedures)
5. [Recovery Procedures](#recovery-procedures)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Architecture Overview

### Components

The replication system consists of four main components:

1. **ReplicaManager**: Manages replica registration, health checking, and topology
2. **ReplicationRouter**: Handles automatic read/write splitting with consistency guarantees
3. **LagMonitor**: Monitors replication lag and generates alerts
4. **FailoverManager**: Handles automatic primary promotion and topology reconfiguration

### Topology

```
                    ┌─────────────────┐
                    │  Application    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Replication    │
                    │     Router      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼───────┐ ┌───▼──────┐ ┌─────▼────────┐
       │   Primary    │ │ Replica1 │ │  Replica2    │
       │ (us-east-1)  │ │(us-east)│ │  (us-west)   │
       └──────────────┘ └──────────┘ └──────────────┘
              │              │              │
              └──────────────┴──────────────┘
                      Replication
```

---

## Setup and Configuration

### Initial Setup

```python
from covet.database.replication import setup_replication, FailoverStrategy

# Configure replication
await setup_replication(
    primary={
        'host': 'primary.db.example.com',
        'port': 5432,
        'database': 'production',
        'user': 'app_user',
        'password': 'secure_password',
        'ssl': 'require'
    },
    replicas=[
        {
            'host': 'replica1.db.example.com',
            'port': 5432,
            'region': 'us-east-1a',
            'weight': 100,
            'max_lag_seconds': 5.0
        },
        {
            'host': 'replica2.db.example.com',
            'port': 5432,
            'region': 'us-west-2a',
            'weight': 80,
            'max_lag_seconds': 10.0
        }
    ],
    health_check_interval=10.0,
    max_lag_threshold=5.0,
    enable_auto_failover=True,
    failover_strategy=FailoverStrategy.SUPERVISED
)
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `health_check_interval` | 10.0 | Seconds between health checks |
| `max_lag_threshold` | 5.0 | Maximum acceptable lag (seconds) |
| `enable_auto_failover` | True | Enable automatic failover |
| `failover_strategy` | SUPERVISED | Failover strategy |
| `min_replicas_for_failover` | 1 | Minimum healthy replicas for failover |
| `read_after_write_window` | 5.0 | Consistency window (seconds) |

---

## Health Monitoring

### Monitoring Dashboard

```python
from covet.database.replication import get_replication_status

# Get comprehensive status
status = get_replication_status()

print(f"Replicas: {status['replica_manager']['metrics']['total_replicas']}")
print(f"Healthy: {status['replica_manager']['metrics']['healthy_replicas']}")
print(f"Replica Hit Rate: {status['router']['replica_hit_rate_percent']}%")
```

### Health Check Metrics

Monitor these key metrics:

1. **Replication Lag**: Time behind primary (target: < 5 seconds)
2. **Response Time**: Query response time (target: < 100ms)
3. **Connection Pool**: Available connections (target: > 20%)
4. **Replica Availability**: Percentage of healthy replicas (target: > 90%)

### Alert Thresholds

```python
from covet.database.replication import get_lag_monitor, AlertSeverity

lag_monitor = get_lag_monitor()

# Register alert handler
async def handle_alert(alert):
    if alert.severity == AlertSeverity.CRITICAL:
        # Page on-call engineer
        await notify_oncall(alert)
    elif alert.severity == AlertSeverity.ERROR:
        # Send high-priority alert
        await send_alert(alert)
    else:
        # Log warning
        logger.warning(f"Lag alert: {alert.message}")

lag_monitor.register_alert_callback(handle_alert)
```

---

## Failover Procedures

### Automatic Failover

The system automatically initiates failover when:

1. Primary fails 3 consecutive health checks (default: 15 seconds)
2. Primary becomes unreachable
3. Primary response time exceeds threshold

**Failover Process** (< 5 seconds):

1. **Detection** (1s): Detect primary failure
2. **Validation** (1s): Verify failover conditions
3. **Election** (1s): Select best replica
4. **Promotion** (2s): Promote replica to primary
5. **Reconfiguration** (<1s): Update topology

### Manual Failover

For planned maintenance:

```python
from covet.database.replication import get_failover_manager, FailoverReason

failover_mgr = get_failover_manager()

# Initiate planned failover
event = await failover_mgr.initiate_failover(
    reason=FailoverReason.PLANNED_MAINTENANCE,
    target_replica_id='replica1:5432/production',
    metadata={'planned_by': 'ops-team', 'ticket': 'MAINT-1234'}
)

print(f"Failover completed in {event.duration_seconds:.2f}s")
print(f"New primary: {event.new_primary_id}")
```

### Failover Validation

After failover, verify:

```bash
# 1. Check new primary accepts writes
psql -h replica1.db.example.com -c "SELECT pg_is_in_recovery();"
# Expected: f (false)

# 2. Verify replication from new primary
psql -h replica2.db.example.com -c "SELECT pg_is_in_recovery();"
# Expected: t (true)

# 3. Check application connectivity
curl http://app.example.com/health
# Expected: 200 OK
```

---

## Recovery Procedures

### Recovering Failed Primary

After the original primary is fixed:

```python
from covet.database.replication import get_replica_manager, ReplicaConfig, ReplicaRole

replica_mgr = get_replica_manager()

# Add old primary as replica
old_primary_config = ReplicaConfig(
    host='old-primary.db.example.com',
    port=5432,
    database='production',
    user='app_user',
    password='secure_password',
    role=ReplicaRole.REPLICA,
    region='us-east-1a'
)

# Register as replica
await replica_mgr.register_replica(old_primary_config)
```

### Replica Recovery

If a replica fails and recovers:

```python
# The system automatically:
# 1. Detects replica is back online
# 2. Checks replication lag
# 3. Re-adds to routing pool when lag < threshold
```

### Split-Brain Prevention

The system prevents split-brain by:

1. **Fencing**: Old primary is verified down before promotion
2. **Quorum**: Requires majority of replicas available
3. **Validation**: Multiple health checks before failover
4. **Timeout**: 2-second verification window

---

## Troubleshooting

### High Replication Lag

**Symptoms**: Replica lag > 10 seconds

**Causes**:
- High write load on primary
- Network latency
- Slow disk on replica
- Large transactions

**Resolution**:
```python
# 1. Check current lag
lag_monitor = get_lag_monitor()
stats = lag_monitor.get_lag_statistics('replica1:5432/production')
print(f"Mean lag: {stats.mean_lag:.2f}s")
print(f"P95 lag: {stats.p95_lag:.2f}s")

# 2. Temporarily remove from rotation
replica_mgr = get_replica_manager()
await replica_mgr.unregister_replica('replica1:5432/production', drain=True)

# 3. Investigate on replica
# Check disk I/O, network, locks, etc.

# 4. Re-add when resolved
await replica_mgr.register_replica(config)
```

### Replica Connection Failures

**Symptoms**: "No replica available" warnings

**Resolution**:
```python
# 1. Check replica status
status = get_replication_status()
for replica in status['replica_manager']['replicas']:
    print(f"{replica['id']}: {replica['status']}")

# 2. Force use of primary temporarily
from covet.database.orm import User

# Explicit primary routing
users = await User.objects.using('primary').all()
```

### Failover Not Triggering

**Symptoms**: Primary down but no failover

**Checks**:
```python
failover_mgr = get_failover_manager()
metrics = failover_mgr.get_metrics()

# Check failover is enabled
print(f"Strategy: {metrics['strategy']}")
print(f"Consecutive failures: {metrics['consecutive_primary_failures']}")

# Check minimum replicas
replica_mgr = get_replica_manager()
healthy = replica_mgr.get_metrics()['healthy_replicas']
min_required = failover_mgr.min_replicas_for_failover

if healthy < min_required:
    print(f"Insufficient replicas: {healthy} < {min_required}")
```

---

## Best Practices

### 1. Regular Testing

Test failover monthly:

```python
# Controlled failover test
event = await failover_mgr.initiate_failover(
    reason=FailoverReason.PLANNED_MAINTENANCE,
    metadata={'test': True}
)

# Validate failover time
assert event.duration_seconds < 5.0, "Failover too slow"
```

### 2. Monitoring Integration

```python
# Export metrics to Prometheus/Datadog
status = get_replication_status()

metrics.gauge('db.replicas.total', status['replica_manager']['metrics']['total_replicas'])
metrics.gauge('db.replicas.healthy', status['replica_manager']['metrics']['healthy_replicas'])
metrics.gauge('db.replica_hit_rate', status['router']['replica_hit_rate_percent'])
metrics.gauge('db.failover.count', status['failover_manager']['total_failovers'])
```

### 3. Geographic Distribution

- Place replicas in multiple availability zones
- Set appropriate weights for cross-region replicas
- Configure higher lag thresholds for distant replicas

### 4. Capacity Planning

- Size replica pools for N+2 redundancy
- Monitor connection pool utilization
- Scale replicas before hitting 80% capacity

### 5. Consistency Guarantees

```python
# Critical reads always from primary
critical_user = await User.objects.using('primary').get(id=admin_id)

# Read-after-write consistency
router = get_replication_router()
session_id = router.create_session()

# Write
async with router.route_query("INSERT ...", session=session_id) as adapter:
    await adapter.execute("INSERT INTO orders ...")

# Subsequent read sees write
async with router.route_query("SELECT ...", session=session_id) as adapter:
    order = await adapter.fetch_one("SELECT * FROM orders WHERE ...")
```

---

## Emergency Procedures

### Complete Cluster Failure

If all databases fail:

1. **Stop application traffic**: Return 503 Service Unavailable
2. **Restore from backup**: Use most recent point-in-time backup
3. **Verify data integrity**: Run consistency checks
4. **Gradually restore traffic**: Start with health checks only

### Data Corruption Detected

1. **Isolate affected database**: Remove from rotation immediately
2. **Assess scope**: Determine which data is corrupted
3. **Restore from backup**: Point-in-time recovery to before corruption
4. **Replay WAL**: Replay write-ahead logs if needed
5. **Verify**: Run comprehensive integrity checks

### Network Partition

If replica appears failed but is actually isolated:

1. **Verify network connectivity**: Ping, traceroute from multiple sources
2. **Check split-brain prevention**: Ensure old primary is fenced
3. **Manual intervention**: May need to manually demote old primary
4. **Resync replica**: Full resync may be required

---

## Maintenance Procedures

### Adding New Replica

```python
new_replica = ReplicaConfig(
    host='replica3.db.example.com',
    port=5432,
    database='production',
    user='app_user',
    password='secure_password',
    region='eu-west-1a',
    weight=100
)

replica_mgr = get_replica_manager()
await replica_mgr.register_replica(new_replica)
```

### Removing Replica

```python
# Graceful removal (drains connections)
await replica_mgr.unregister_replica(
    'replica3:5432/production',
    drain=True  # Wait for in-flight queries
)
```

### Upgrading Database Version

1. Upgrade replicas first (zero downtime)
2. Promote upgraded replica to primary
3. Upgrade old primary
4. Add back as replica

---

## Support and Escalation

### Log Collection

```bash
# Collect replication logs
python -c "
from covet.database.replication import get_replication_status
import json
status = get_replication_status()
print(json.dumps(status, indent=2))
" > replication-status.json

# Collect failover history
python -c "
from covet.database.replication import get_failover_manager
mgr = get_failover_manager()
history = mgr.get_failover_history(limit=10)
for event in history:
    print(event.to_dict())
" > failover-history.json
```

### Escalation Path

1. **Level 1**: Application logs and monitoring
2. **Level 2**: Database administrator
3. **Level 3**: Platform engineering on-call
4. **Level 4**: Vendor support (if applicable)

---

## Appendix: Configuration Reference

### Complete Configuration Example

```python
await setup_replication(
    # Primary Configuration
    primary={
        'host': 'primary.db.example.com',
        'port': 5432,
        'database': 'production',
        'user': 'app_user',
        'password': os.environ['DB_PASSWORD'],
        'ssl': 'require',
        'min_pool_size': 10,
        'max_pool_size': 50
    },

    # Replica Configuration
    replicas=[
        {
            'host': 'replica1.db.example.com',
            'port': 5432,
            'region': 'us-east-1a',
            'datacenter': 'aws-us-east',
            'weight': 100,
            'max_lag_seconds': 5.0,
            'min_pool_size': 5,
            'max_pool_size': 20
        },
        {
            'host': 'replica2.db.example.com',
            'port': 5432,
            'region': 'us-west-2a',
            'datacenter': 'aws-us-west',
            'weight': 80,  # Lower weight for cross-region
            'max_lag_seconds': 10.0,  # Higher lag tolerance
            'min_pool_size': 3,
            'max_pool_size': 15
        }
    ],

    # Health Monitoring
    health_check_interval=10.0,
    max_lag_threshold=5.0,
    lag_check_interval=5.0,
    auto_remediate=True,

    # Failover Configuration
    enable_auto_failover=True,
    failover_strategy=FailoverStrategy.SUPERVISED,
    min_replicas_for_failover=1,
    failover_timeout=30.0,
    consecutive_failures_threshold=3,

    # Routing Configuration
    default_read_preference=ReadPreference.REPLICA_PREFERRED,
    default_consistency=ConsistencyLevel.READ_AFTER_WRITE,
    read_after_write_window=5.0,

    # Advanced
    auto_discover=False,
    discovery_interval=60.0
)
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-11
**Maintained By**: Platform Engineering Team
