# CovetPy Database Sharding Guide

## Table of Contents

1. [Introduction](#introduction)
2. [When to Use Sharding](#when-to-use-sharding)
3. [Architecture Overview](#architecture-overview)
4. [Sharding Strategies](#sharding-strategies)
5. [Quick Start](#quick-start)
6. [Shard Key Selection](#shard-key-selection)
7. [Production Deployment](#production-deployment)
8. [Monitoring and Operations](#monitoring-and-operations)
9. [Rebalancing](#rebalancing)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [Performance Tuning](#performance-tuning)

---

## Introduction

CovetPy's database sharding system provides production-grade horizontal scaling for databases that have outgrown single-server capacity. It implements proven sharding patterns used by companies like Amazon (DynamoDB), LinkedIn, and Twitter.

### What is Database Sharding?

Sharding is a method of distributing data across multiple database servers (shards). Each shard contains a subset of the total data, allowing you to:

- **Scale horizontally**: Add more servers instead of upgrading one server
- **Improve performance**: Distribute load across multiple databases
- **Increase capacity**: Store more data than fits on a single server
- **Enhance availability**: Isolate failures to specific shards

### Key Features

- **Multiple sharding strategies**: Hash, range, consistent hash, geographic
- **Zero-downtime rebalancing**: Add/remove shards without service interruption
- **Automatic failover**: Health monitoring with automatic replica switching
- **Query routing**: Intelligent routing to single or multiple shards
- **Connection pooling**: Per-shard connection management
- **Production monitoring**: Prometheus metrics, health checks, alerting

---

## When to Use Sharding

### You SHOULD Consider Sharding When:

1. **Database size** exceeds 1TB or approaching hardware limits
2. **Query load** exceeds 10,000 QPS on a single database
3. **Write throughput** is bottlenecked by single-server I/O
4. **Geographic distribution** requires data locality (e.g., GDPR)
5. **Cost optimization**: Horizontal scaling is cheaper than vertical
6. **Future growth** will exceed single-server capacity within 12 months

### You Should NOT Use Sharding If:

1. **Database is small**: < 100GB can usually scale vertically
2. **Read-heavy workload**: Consider read replicas instead
3. **Complex joins**: Sharding makes cross-shard joins expensive
4. **Development complexity**: Adds operational overhead
5. **Query patterns unclear**: Optimize queries first

### Alternatives to Consider First:

1. **Vertical scaling**: Upgrade server hardware (RAM, CPU, SSD)
2. **Read replicas**: Distribute read traffic across replicas
3. **Caching**: Redis/Memcached for frequently accessed data
4. **Query optimization**: Indexes, query rewriting, EXPLAIN ANALYZE
5. **Connection pooling**: PgBouncer, ProxySQL
6. **Table partitioning**: PostgreSQL declarative partitioning

---

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                     Application Layer                    │
└─────────────────────┬───────────────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │     ShardRouter         │  ← Query routing & aggregation
         │  - Single-shard routing │
         │  - Scatter-gather       │
         │  - Result aggregation   │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │    ShardManager         │  ← Central coordinator
         │  - Health monitoring    │
         │  - Connection pooling   │
         │  - Failover logic       │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   ShardingStrategy      │  ← Routing algorithm
         │  - Hash                 │
         │  - Range                │
         │  - Consistent Hash      │
         │  - Geographic           │
         └────────────┬────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
┌─────▼────┐    ┌────▼────┐    ┌────▼─────┐
│  Shard 1  │    │ Shard 2 │    │  Shard 3 │
│ (Primary) │    │(Primary)│    │(Primary) │
│  + Replicas│    │+Replicas│    │+Replicas│
└──────────┘    └─────────┘    └──────────┘
```

### Component Responsibilities

#### **ShardRouter**
- Routes queries to appropriate shard(s)
- Handles single-shard and scatter-gather patterns
- Aggregates results from multiple shards
- Manages query timeouts and retries

#### **ShardManager**
- Maintains shard registry and metadata
- Monitors shard health with automatic failover
- Manages connection pools per shard
- Coordinates topology changes (add/remove shards)

#### **ShardingStrategy**
- Determines which shard stores which data
- Implements routing algorithms (hash, range, etc.)
- Handles shard rebalancing calculations

#### **ShardRebalancer**
- Orchestrates zero-downtime data migration
- Implements live migration and gradual transition
- Validates data consistency after migration
- Provides rollback capabilities

---

## Sharding Strategies

### 1. Hash-Based Sharding (Recommended for Most Use Cases)

**How it works**: Hash the shard key (e.g., user_id) and use modulo to select shard.

```python
from covet.database.sharding import ShardManager, HashStrategy, ShardInfo

# Define shards
shards = [
    ShardInfo('shard1', 'db1.example.com', 5432, 'app_db'),
    ShardInfo('shard2', 'db2.example.com', 5432, 'app_db'),
    ShardInfo('shard3', 'db3.example.com', 5432, 'app_db'),
]

# Create hash strategy
strategy = HashStrategy(shard_key='user_id', shards=shards)

# Initialize manager
manager = ShardManager(strategy=strategy)
await manager.initialize()

# Route query
shard = manager.get_shard_for_write(routing_key=12345)
print(f"User 12345 is on {shard.shard_id}")
```

**Pros:**
- Even distribution across shards
- Simple and predictable
- Good performance (O(1) lookup)

**Cons:**
- Adding/removing shards requires rebalancing
- Range queries span all shards
- No data locality

**Best for:** User data, session data, general-purpose sharding

---

### 2. Range-Based Sharding

**How it works**: Assign key ranges to specific shards.

```python
from covet.database.sharding import RangeStrategy

ranges = {
    'shard1': (0, 1000000),           # Users 0-1M
    'shard2': (1000001, 2000000),     # Users 1M-2M
    'shard3': (2000001, None),        # Users 2M+
}

strategy = RangeStrategy(
    shard_key='user_id',
    shards=shards,
    ranges=ranges
)
```

**Pros:**
- Efficient range queries (SELECT ... WHERE user_id BETWEEN x AND y)
- Easy to add new shards (append new range)
- Good for time-series data

**Cons:**
- Hot spots if data distribution is uneven
- Requires careful capacity planning
- Newer ranges may get more writes

**Best for:** Time-series data, chronological data, append-mostly workloads

---

### 3. Consistent Hashing

**How it works**: Virtual nodes on a hash ring for minimal rebalancing.

```python
from covet.database.sharding import ConsistentHashStrategy

strategy = ConsistentHashStrategy(
    shard_key='user_id',
    shards=shards,
    virtual_nodes_per_shard=150  # More = better distribution
)
```

**Pros:**
- Minimal data movement when adding/removing shards (only K/N keys move)
- Supports weighted sharding (higher capacity servers get more data)
- Good distribution with virtual nodes

**Cons:**
- More complex than simple hash
- Slight overhead from virtual node lookup
- Range queries still span all shards

**Best for:** Dynamic clusters, frequent topology changes, weighted sharding

---

### 4. Geographic Sharding

**How it works**: Route data based on geographic region.

```python
from covet.database.sharding import GeographicStrategy

# Shards must have 'region' set
shards = [
    ShardInfo('us-east', 'us-east.db.com', 5432, 'app', region='us-east-1'),
    ShardInfo('us-west', 'us-west.db.com', 5432, 'app', region='us-west-2'),
    ShardInfo('eu-west', 'eu-west.db.com', 5432, 'app', region='eu-west-1'),
]

strategy = GeographicStrategy(
    shard_key='region',
    shards=shards,
    default_region='us-east-1'
)
```

**Pros:**
- Data locality (low latency for regional users)
- Compliance with data residency laws (GDPR, etc.)
- Can isolate regional failures

**Cons:**
- Uneven distribution if users are geographically concentrated
- Cross-region queries are expensive
- Requires region information for routing

**Best for:** Global applications, regulatory compliance, data residency requirements

---

## Quick Start

### Basic Setup (5 minutes)

```python
import asyncio
from covet.database.sharding import (
    ShardManager,
    ShardRouter,
    ShardInfo,
    HashStrategy,
)

async def main():
    # Step 1: Define your shards
    shards = [
        ShardInfo(
            shard_id='shard1',
            host='localhost',
            port=5432,
            database='app_shard1',
            metadata={
                'user': 'postgres',
                'password': 'secret',
                'adapter_type': 'postgresql',
            }
        ),
        ShardInfo(
            shard_id='shard2',
            host='localhost',
            port=5433,
            database='app_shard2',
            metadata={
                'user': 'postgres',
                'password': 'secret',
                'adapter_type': 'postgresql',
            }
        ),
    ]

    # Step 2: Choose sharding strategy
    strategy = HashStrategy(shard_key='user_id', shards=shards)

    # Step 3: Initialize manager
    manager = ShardManager(strategy=strategy)
    await manager.initialize()

    # Step 4: Create router
    router = ShardRouter(manager)

    # Step 5: Execute queries
    # Single-shard query (fast)
    result = await router.execute(
        "SELECT * FROM users WHERE user_id = $1",
        params=(12345,),
        routing_key=12345  # Routes to correct shard
    )
    print(f"Found user: {result.rows}")

    # Multi-shard query (scatter-gather)
    result = await router.scatter_gather(
        "SELECT COUNT(*) as count FROM users WHERE is_active = $1",
        params=(True,),
        aggregation_func=lambda results: {
            'total': sum(r.rows[0]['count'] for r in results if r.success)
        }
    )
    print(f"Total active users: {result.rows[0]['total']}")

    # Cleanup
    await manager.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
```

### Complete Example with Error Handling

```python
from covet.database.sharding import ShardManager, ShardRouter, ShardInfo, HashStrategy

class UserService:
    """Example service using sharding."""

    def __init__(self, shards: list[ShardInfo]):
        self.strategy = HashStrategy(shard_key='user_id', shards=shards)
        self.manager = ShardManager(
            strategy=self.strategy,
            health_check_interval=30,        # Check health every 30s
            max_consecutive_failures=3,      # Mark unhealthy after 3 failures
            enable_auto_failover=True,       # Auto-switch to replicas
        )
        self.router = ShardRouter(
            shard_manager=self.manager,
            query_timeout=5.0,               # 5 second timeout
        )

    async def initialize(self):
        """Initialize sharding system."""
        await self.manager.initialize()
        print("Sharding system initialized")

    async def shutdown(self):
        """Shutdown sharding system."""
        await self.manager.shutdown()
        print("Sharding system shut down")

    async def get_user(self, user_id: int) -> dict:
        """Get user by ID (single-shard query)."""
        result = await self.router.execute(
            "SELECT * FROM users WHERE user_id = $1",
            params=(user_id,),
            routing_key=user_id,
            read_only=True,  # Prefer read replicas
        )

        if not result.success:
            raise Exception(f"Query failed: {result.error_message}")

        return result.rows[0] if result.rows else None

    async def create_user(self, user_id: int, name: str, email: str) -> bool:
        """Create new user (single-shard write)."""
        result = await self.router.execute(
            "INSERT INTO users (user_id, name, email) VALUES ($1, $2, $3)",
            params=(user_id, name, email),
            routing_key=user_id,  # Routes to correct shard
        )

        return result.success

    async def count_active_users(self) -> int:
        """Count active users across all shards (scatter-gather)."""
        result = await self.router.scatter_gather(
            "SELECT COUNT(*) as count FROM users WHERE is_active = $1",
            params=(True,),
            aggregation_func=lambda results: {
                'total': sum(
                    r.rows[0]['count']
                    for r in results
                    if r.success and r.rows
                )
            }
        )

        if not result.success:
            raise Exception(f"Count failed: {result.error_message}")

        return result.rows[0]['total']

    async def get_cluster_health(self) -> dict:
        """Get cluster health status."""
        return self.manager.get_cluster_status()
```

---

## Shard Key Selection

### Critical Decision: Choosing the Right Shard Key

The shard key determines how data is distributed. **Choose carefully - changing it later requires complete rebalancing**.

### Good Shard Keys

✅ **High Cardinality**: Many distinct values
```python
# Good: user_id (millions of unique values)
shard_key = 'user_id'

# Bad: country_code (only ~200 values)
shard_key = 'country_code'  # Don't do this!
```

✅ **Even Distribution**: Values spread evenly
```python
# Good: UUID, auto-increment IDs, hashed values
shard_key = 'user_id'  # Sequential IDs work with hash strategy

# Bad: Timestamp (creates hot spots for recent data)
shard_key = 'created_at'  # Avoid for hash sharding
```

✅ **Query Pattern Friendly**: Used in WHERE clauses
```python
# Good: Most queries filter by user_id
shard_key = 'user_id'
# Queries like: SELECT * FROM orders WHERE user_id = ?

# Bad: Rarely used in queries
shard_key = 'updated_at'
# Forces scatter-gather for: SELECT * FROM orders WHERE user_id = ?
```

✅ **Immutable**: Never changes
```python
# Good: user_id (never changes)
shard_key = 'user_id'

# Bad: email (users can change email)
shard_key = 'email'  # Changing email requires moving data
```

### Common Shard Key Patterns

#### **1. User ID (Most Common)**
```python
shard_key = 'user_id'
```
- **Use when**: Multi-tenant, user-based data
- **Pros**: Even distribution, high cardinality
- **Cons**: Cross-user queries are expensive

#### **2. Tenant ID (SaaS Applications)**
```python
shard_key = 'tenant_id'
```
- **Use when**: B2B SaaS, multi-tenant
- **Pros**: Data isolation, tenant-level queries fast
- **Cons**: Uneven distribution if tenant sizes vary

#### **3. Composite Key**
```python
# Hash combination of fields
shard_key = 'user_id'  # Primary
# But also store: tenant_id for filtering
```
- **Use when**: Need isolation + performance
- **Implementation**: Hash on user_id, filter by tenant_id within shard

#### **4. Geographic Key**
```python
shard_key = 'region'
```
- **Use when**: Global application, data residency
- **Pros**: Low latency, compliance
- **Cons**: Uneven distribution

### Anti-Patterns to Avoid

❌ **Low Cardinality Keys**
```python
# Bad: Only a few distinct values
shard_key = 'status'  # active/inactive
shard_key = 'category'  # 10 categories
```

❌ **Timestamp Keys (with Hash Strategy)**
```python
# Bad: Recent data creates hot spots
shard_key = 'created_at'  # All new writes go to one shard
```

❌ **Mutable Keys**
```python
# Bad: Data moves when key changes
shard_key = 'email'  # Users change emails
shard_key = 'username'  # Users change usernames
```

❌ **Nullable Keys**
```python
# Bad: NULL values can't be routed
shard_key = 'optional_field'  # Some rows have NULL
```

---

## Production Deployment

### Pre-Deployment Checklist

#### **1. Capacity Planning**

Calculate required capacity:

```
Total DB Size: 2TB
Number of Shards: 8
Per-Shard Size: 2TB / 8 = 250GB

With 3x growth buffer: 250GB * 3 = 750GB per shard
Hardware: 1TB SSD per shard (comfortable headroom)
```

#### **2. Shard Configuration**

```python
# Production shard configuration
shards = [
    ShardInfo(
        shard_id='prod-shard-01',
        host='db-shard-01.prod.internal',
        port=5432,
        database='app_production',
        weight=1.0,
        region='us-east-1',
        metadata={
            'user': 'app_user',
            'password': os.environ['DB_PASSWORD'],  # From secrets
            'adapter_type': 'postgresql',
            'pool_size': 20,
            'ssl': 'require',
        },
        tags={
            'env': 'production',
            'az': 'us-east-1a',
        }
    ),
    # ... more shards
]
```

#### **3. Connection Pooling**

```python
manager = ShardManager(
    strategy=strategy,
    connection_pool_size=20,      # 20 connections per shard
    connection_timeout=5.0,       # 5s connection timeout
    health_check_interval=30,     # Check every 30s
)
```

**Pool sizing formula**:
```
connections_per_shard = (max_app_instances * connections_per_instance) / num_shards

Example:
  10 app servers * 50 connections = 500 total
  500 / 10 shards = 50 connections per shard
  Set pool_size = 50-60 (with buffer)
```

#### **4. Monitoring Setup**

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
shard_queries = Counter('shard_queries_total', 'Total queries', ['shard', 'type'])
shard_latency = Histogram('shard_query_duration_seconds', 'Query latency', ['shard'])
shard_health = Gauge('shard_healthy', 'Shard health status', ['shard'])

# Instrument your code
async def execute_query(shard_id, query):
    with shard_latency.labels(shard=shard_id).time():
        result = await router.execute(query, routing_key=key)
        shard_queries.labels(shard=shard_id, type='success').inc()
        return result
```

#### **5. Schema Deployment**

Deploy schema to all shards:

```python
async def deploy_schema_to_all_shards(manager: ShardManager, migration_sql: str):
    """Deploy schema changes to all shards."""
    router = ShardRouter(manager)

    # Execute on all shards in parallel
    result = await router.execute_on_all_shards(migration_sql)

    if not result.success:
        raise Exception(f"Schema deployment failed: {result.error_message}")

    print(f"Schema deployed to {len(result.shard_results)} shards")
    return result

# Example usage
migration = """
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
"""

await deploy_schema_to_all_shards(manager, migration)
```

### Deployment Strategies

#### **Strategy 1: Greenfield Deployment (New Application)**

1. **Setup shards**: Provision databases
2. **Deploy schema**: Create tables on all shards
3. **Deploy application**: Connect to sharding layer
4. **Verify**: Test with synthetic traffic
5. **Go live**: Route production traffic

#### **Strategy 2: Migration from Single Database**

1. **Setup sharding infrastructure**: Don't route traffic yet
2. **Dual-write phase**: Write to both old DB and shards
3. **Backfill data**: Copy historical data to shards
4. **Verify consistency**: Compare old DB vs shards
5. **Switch reads**: Route reads to shards
6. **Verify performance**: Monitor for issues
7. **Stop dual-writes**: Write only to shards
8. **Decommission old DB**: After monitoring period

```python
# Dual-write implementation
async def create_user_dual_write(user_id, name, email):
    # Write to shards (new system)
    await sharded_service.create_user(user_id, name, email)

    # Also write to old DB (for safety)
    await old_db.execute(
        "INSERT INTO users (user_id, name, email) VALUES ($1, $2, $3)",
        (user_id, name, email)
    )
```

---

## Monitoring and Operations

### Health Monitoring

ShardManager automatically monitors shard health:

```python
# Get cluster health
status = manager.get_cluster_status()
print(f"Healthy shards: {status['healthy_shards']}/{status['total_shards']}")
print(f"Error rate: {status['error_rate'] * 100:.2f}%")

# Get specific shard status
shard_status = manager.get_shard_status('shard1')
print(f"Health: {shard_status['health']['is_healthy']}")
print(f"Latency: {shard_status['health']['average_latency_ms']:.2f}ms")
print(f"Connections: {shard_status['health']['connection_count']}")
```

### Prometheus Metrics

Export metrics for monitoring:

```python
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # Get sharding metrics
    cluster_status = manager.get_cluster_status()
    router_stats = router.get_statistics()

    # Update Prometheus gauges
    cluster_health_gauge.set(cluster_status['healthy_shards'])
    query_rate_gauge.set(router_stats['total_queries'])

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### Key Metrics to Monitor

1. **Shard Health**: Percentage of healthy shards
2. **Query Latency**: P50, P95, P99 per shard
3. **Error Rate**: Failed queries per shard
4. **Connection Pool**: Utilization per shard
5. **Data Distribution**: Keys per shard (balance)
6. **Rebalancing Progress**: When active

### Alerting Rules

```yaml
# Example Prometheus alerting rules
groups:
  - name: sharding
    rules:
      - alert: ShardUnhealthy
        expr: shard_healthy == 0
        for: 5m
        annotations:
          summary: "Shard {{ $labels.shard }} is unhealthy"

      - alert: HighShardLatency
        expr: shard_query_duration_seconds{quantile="0.95"} > 0.5
        for: 10m
        annotations:
          summary: "High latency on shard {{ $labels.shard }}"

      - alert: UnbalancedShards
        expr: stddev(keys_per_shard) / avg(keys_per_shard) > 0.2
        for: 1h
        annotations:
          summary: "Shards are unbalanced (>20% deviation)"
```

---

## Rebalancing

### When to Rebalance

- **Adding shards**: When capacity reached 70-80%
- **Removing shards**: Decommissioning or consolidation
- **Rebalancing load**: If distribution becomes uneven

### Zero-Downtime Rebalancing

```python
from covet.database.sharding import ShardRebalancer, RebalanceStrategy

# Create rebalancer
rebalancer = ShardRebalancer(
    shard_manager=manager,
    router=router,
    batch_size=1000,              # Rows per batch
    throttle_ms=10,               # Throttle between batches
    max_parallel_tasks=5,         # Parallel migration tasks
    enable_validation=True,       # Verify data consistency
)

# Add new shard
new_shard = ShardInfo('shard4', 'db4.example.com', 5432, 'app_db')
manager.add_shard(new_shard)

# Create rebalancing job
job = await rebalancer.create_rebalance_job(
    table_name='users',
    shard_key='user_id',
    strategy=RebalanceStrategy.LIVE_MIGRATION
)

# Execute rebalancing
success = await rebalancer.execute_job(job.job_id)

if success:
    print(f"Rebalancing completed: {job.total_migrated} rows migrated")
else:
    print(f"Rebalancing failed: {job.error_message}")
    # Rollback if needed
    await rebalancer.rollback_job(job.job_id)
```

### Monitoring Rebalancing

```python
# Monitor progress
while True:
    status = rebalancer.get_job_status(job.job_id)

    print(f"Progress: {status['progress_percent']:.1f}%")
    print(f"Rows migrated: {status['total_migrated']}/{status['total_rows']}")
    print(f"Duration: {status['duration_seconds']:.0f}s")

    if status['status'] in ['completed', 'failed']:
        break

    await asyncio.sleep(10)
```

---

## Troubleshooting

### Common Issues

#### **Issue 1: Uneven Distribution**

**Symptoms**: Some shards have much more data than others

**Diagnosis**:
```python
# Check distribution
distribution = manager.strategy.get_distribution(sample_keys)
for shard_id, count in distribution.items():
    print(f"{shard_id}: {count} keys ({count/total*100:.1f}%)")
```

**Solutions**:
- Increase virtual nodes (consistent hashing)
- Review shard key selection
- Consider rebalancing

#### **Issue 2: High Query Latency**

**Symptoms**: Slow queries, timeouts

**Diagnosis**:
```python
# Check shard health
for shard_id, health in manager.shard_health.items():
    print(f"{shard_id}: {health.average_latency_ms:.2f}ms latency")
    print(f"  Connections: {health.connection_count}")
    print(f"  Error rate: {health.error_rate * 100:.1f}%")
```

**Solutions**:
- Increase connection pool size
- Check database performance (indexes, query plans)
- Consider read replicas for read-heavy workloads
- Review query patterns (avoid scatter-gather if possible)

#### **Issue 3: Shard Marked Unhealthy**

**Symptoms**: Automatic failover, queries failing

**Diagnosis**:
```python
# Check shard health details
health = manager.shard_health['shard1']
print(f"Healthy: {health.is_healthy}")
print(f"Consecutive failures: {health.consecutive_failures}")
print(f"Last error: {health.last_error}")
```

**Solutions**:
- Check database server status
- Verify network connectivity
- Review database logs
- Check connection pool exhaustion

#### **Issue 4: Cross-Shard Queries Too Slow**

**Symptoms**: Scatter-gather queries taking too long

**Solutions**:
- Cache aggregated results
- Pre-compute aggregations (materialized views)
- Increase parallel shard limit
- Consider denormalizing data

---

## Best Practices

### Development

1. **Always specify routing_key** for single-shard queries
2. **Minimize cross-shard queries** (expensive)
3. **Use transactions within single shard** only
4. **Test with multiple shards** in development
5. **Monitor query patterns** to optimize shard key

### Schema Design

1. **Include shard key** in all table WHERE clauses
2. **Denormalize when necessary** to avoid joins
3. **Use same shard key** across related tables
4. **Avoid foreign keys** across shards
5. **Design for eventual consistency** in cross-shard scenarios

### Operations

1. **Monitor shard health** continuously
2. **Set up alerting** for unhealthy shards
3. **Plan capacity** for 2-3x growth
4. **Test failover** regularly
5. **Document runbooks** for common issues

### Performance

1. **Use connection pooling** (avoid connection churn)
2. **Batch operations** when possible
3. **Use read replicas** for read-heavy workloads
4. **Cache frequently accessed data**
5. **Profile and optimize** slow queries

---

## Performance Tuning

### Tuning Connection Pools

```python
# Adjust based on workload
manager = ShardManager(
    strategy=strategy,
    connection_pool_size=50,      # Start with app_servers * 5
    connection_timeout=5.0,       # Fail fast
)

# Monitor pool utilization
stats = await adapter.get_pool_stats()
print(f"Pool usage: {stats['used']}/{stats['size']} ({stats['used']/stats['size']*100:.0f}%)")

# If consistently >80%, increase pool size
# If consistently <20%, decrease to save resources
```

### Tuning Query Timeouts

```python
# Per-query timeout
result = await router.execute(
    query=long_running_query,
    routing_key=key,
    timeout=30.0,  # 30 seconds for this query
)

# Global timeout
router = ShardRouter(
    shard_manager=manager,
    query_timeout=10.0,  # Default 10s
)
```

### Tuning Rebalancing

```python
rebalancer = ShardRebalancer(
    shard_manager=manager,
    router=router,
    batch_size=5000,       # Larger batches = faster but more load
    throttle_ms=5,         # Lower throttle = faster but more load
    max_parallel_tasks=10, # More parallel = faster but more connections
)
```

### Caching Strategies

```python
from functools import lru_cache
import time

class CachedShardRouter:
    """Router with result caching."""

    def __init__(self, router: ShardRouter):
        self.router = router
        self.cache = {}
        self.cache_ttl = 60  # 60 seconds

    async def execute_cached(self, query: str, routing_key: int):
        """Execute with caching."""
        cache_key = f"{query}:{routing_key}"

        # Check cache
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return result  # Cache hit

        # Cache miss - execute query
        result = await self.router.execute(query, routing_key=routing_key)

        # Store in cache
        self.cache[cache_key] = (result, time.time())

        return result
```

---

## Appendix

### Glossary

- **Shard**: A single database server containing a subset of data
- **Shard Key**: The field used to determine which shard stores data
- **Routing**: Process of determining which shard to query
- **Scatter-Gather**: Querying all shards and combining results
- **Rebalancing**: Moving data between shards when topology changes
- **Virtual Node**: Logical node in consistent hash ring
- **Hot Spot**: Shard receiving disproportionate load

### Further Reading

- [Amazon DynamoDB Paper](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html)
- [Consistent Hashing and Random Trees (Karger et al.)](https://dl.acm.org/doi/10.1145/258533.258660)
- [Sharding Pinterest](https://medium.com/pinterest-engineering/sharding-pinterest-how-we-scaled-our-mysql-fleet-3f341e96ca6f)
- [Instagram Sharding](https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c)

### Quick Reference

```python
# Import everything
from covet.database.sharding import (
    ShardManager,
    ShardRouter,
    ShardInfo,
    HashStrategy,
    RangeStrategy,
    ConsistentHashStrategy,
    GeographicStrategy,
    ShardRebalancer,
    RebalanceStrategy,
)

# Basic workflow
shards = [ShardInfo(...), ShardInfo(...)]
strategy = HashStrategy('user_id', shards)
manager = ShardManager(strategy)
await manager.initialize()

router = ShardRouter(manager)
result = await router.execute(query, routing_key=key)

await manager.shutdown()
```

---

**Need Help?**

- GitHub Issues: https://github.com/your-org/covetpy/issues
- Documentation: https://covetpy.readthedocs.io
- Discord: https://discord.gg/covetpy

