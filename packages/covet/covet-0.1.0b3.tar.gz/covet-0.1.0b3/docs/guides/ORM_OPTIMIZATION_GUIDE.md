# CovetPy ORM Query Optimization Guide

**Comprehensive guide to optimizing database queries using CovetPy's advanced optimization tools**

---

## Table of Contents

1. [Overview](#overview)
2. [Query Optimizer](#query-optimizer)
3. [EXPLAIN Analyzer](#explain-analyzer)
4. [Index Advisor](#index-advisor)
5. [Query Cache](#query-cache)
6. [Query Profiler](#query-profiler)
7. [Batch Operations](#batch-operations)
8. [Best Practices](#best-practices)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)

---

## Overview

CovetPy provides a comprehensive suite of query optimization tools designed for production environments:

- **Query Optimizer**: Analyzes and rewrites queries for better performance
- **EXPLAIN Analyzer**: Executes and analyzes database execution plans
- **Index Advisor**: Recommends indexes based on query patterns
- **Query Cache**: High-performance caching with Redis/Memory backends
- **Query Profiler**: Tracks performance metrics and detects N+1 queries
- **Batch Operations**: Optimized bulk insert/update/delete operations

### Performance Targets

- Query plan analysis: <10ms
- Bulk insert: 10,000+ rows/sec
- Cache hit rate: >80%
- Index suggestion accuracy: >90%

---

## Query Optimizer

The query optimizer analyzes SQL queries and applies various optimization techniques.

### Basic Usage

```python
from covet.database.orm.optimizer import QueryOptimizer, OptimizationLevel

# Initialize optimizer
optimizer = QueryOptimizer(
    database="postgresql",
    optimization_level=OptimizationLevel.MODERATE,
    cache_enabled=True,
)

# Analyze a query
analysis = optimizer.analyze_query(
    sql="SELECT * FROM users WHERE email = $1",
    params=["user@example.com"]
)

print(f"Complexity: {analysis.complexity.value}")
print(f"Estimated cost: {analysis.estimated_cost}")
print(f"Warnings: {analysis.warnings}")
```

### Optimization Levels

- **CONSERVATIVE**: Safe, minimal changes only
- **MODERATE**: Balanced approach (recommended)
- **AGGRESSIVE**: Maximum optimization (use with caution)

### Query Analysis

```python
# Detailed analysis
analysis = optimizer.analyze_query(sql, params)

print(f"Tables: {analysis.table_count}")
print(f"JOINs: {analysis.join_count}")
print(f"Subqueries: {analysis.subquery_count}")
print(f"Index usage: {analysis.index_usage}")
print(f"Missing indexes: {analysis.missing_indexes}")
```

### Query Optimization

```python
# Optimize query
result = optimizer.optimize_query(sql, params)

print(f"Optimizations applied: {result.optimizations_applied}")
print(f"Estimated improvement: {result.estimated_improvement}%")
print(f"Optimized SQL: {result.optimized_sql}")
```

### Optimization Techniques

1. **Redundant Clause Removal**: Removes duplicate WHERE conditions
2. **WHERE Simplification**: Eliminates tautologies (e.g., `1 = 1`)
3. **UNION Optimization**: Converts UNION to UNION ALL when safe
4. **Subquery Flattening**: Converts subqueries to JOINs
5. **JOIN Reordering**: Optimizes JOIN order based on table sizes
6. **LIMIT Push-down**: Pushes LIMIT into subqueries

### Recommendations

```python
# Get optimization recommendations
recommendations = optimizer.get_recommendations(sql)

for rec in recommendations:
    print(f"- {rec}")
```

---

## EXPLAIN Analyzer

Analyzes database execution plans to understand query performance.

### Basic Usage

```python
from covet.database.orm.explain import ExplainAnalyzer

# Initialize analyzer
analyzer = ExplainAnalyzer(database_adapter=adapter)

# Analyze query plan
plan = await analyzer.explain_query(
    sql="SELECT * FROM users WHERE email = $1",
    params=["user@example.com"]
)

print(f"Total cost: {plan.total_cost}")
print(f"Estimated rows: {plan.estimated_rows}")
print(f"Uses index: {plan.uses_index}")
```

### EXPLAIN ANALYZE

```python
# Execute query and get actual statistics
plan = await analyzer.explain_analyze(sql, params)

print(f"Actual execution time: {plan.execution_time}ms")
print(f"Actual rows: {plan.actual_rows}")
```

### Plan Visualization

```python
# Visualize execution plan
visualization = analyzer.visualize_plan(plan)
print(visualization)
```

### Detecting Performance Issues

```python
# Check for sequential scans
if plan.has_sequential_scan:
    print(f"WARNING: Sequential scans on: {plan.sequential_scans}")

# Check for missing indexes
if not plan.uses_index:
    print("WARNING: No indexes used")

# Analyze cost
if plan.total_cost > 1000:
    print(f"HIGH COST: {plan.total_cost}")
```

### Comparing Queries

```python
# Compare execution plans
queries = [
    ("original", "SELECT * FROM users WHERE email = $1", params),
    ("optimized", "SELECT id, email FROM users WHERE email = $1", params),
]

results = await analyzer.compare_queries(queries)

for name, plan in results.items():
    print(f"{name}: cost={plan.total_cost}")
```

---

## Index Advisor

Recommends indexes based on query workload analysis.

### Basic Usage

```python
from covet.database.orm.index_advisor import IndexAdvisor

# Initialize advisor
advisor = IndexAdvisor(database_adapter=adapter)

# Analyze workload
workload = [
    "SELECT * FROM users WHERE email = $1",
    "SELECT * FROM posts WHERE author_id = $1 AND published = true",
]

await advisor.analyze_workload(workload)

# Get recommendations
recommendations = await advisor.get_recommendations()

for rec in recommendations:
    print(f"Priority: {rec.priority.value}")
    print(f"Table: {rec.table_name}")
    print(f"Columns: {rec.column_names}")
    print(f"SQL: {rec.create_statement}")
    print(f"Estimated improvement: {rec.estimated_improvement}%")
```

### Missing Index Detection

```python
# Detect missing indexes
missing = await advisor.detect_missing_indexes()

for rec in missing:
    print(f"MISSING: {rec.create_statement}")
```

### Unused Index Detection

```python
# Detect unused indexes
unused = await advisor.detect_unused_indexes()

for index in unused:
    print(f"UNUSED: {index.index_name} on {index.table_name}")
    print(f"  Consider dropping to save space")
```

### Index Impact Estimation

```python
# Estimate impact of creating an index
impact = await advisor.estimate_index_impact(
    table_name="users",
    column_names=["email"]
)

print(f"Estimated size: {impact['estimated_size_mb']:.2f} MB")
print(f"Queries affected: {impact['affected_query_count']}")
print(f"Improvement: {impact['estimated_improvement']:.1f}%")
```

---

## Query Cache

High-performance caching layer with multiple backend support.

### Configuration

```python
from covet.database.orm.query_cache import QueryCache, CacheConfig

# Memory backend (single process)
config = CacheConfig(
    backend="memory",
    default_ttl=300,  # 5 minutes
    max_size=10000,
)

# Redis backend (distributed)
config = CacheConfig(
    backend="redis",
    redis_url="redis://localhost:6379/0",
    default_ttl=300,
)

cache = QueryCache(config)
```

### Manual Caching

```python
# Set value
await cache.set("user:123", user_data, ttl=60)

# Get value
user = await cache.get("user:123")

# Delete value
await cache.delete("user:123")

# Clear all
await cache.clear()
```

### Decorator Usage

```python
@cache.cached(ttl=300, invalidate_on=["User"])
async def get_user_by_email(email: str):
    return await User.objects.get(email=email)

# First call executes query
user1 = await get_user_by_email("test@example.com")

# Second call uses cache
user2 = await get_user_by_email("test@example.com")
```

### Cache Invalidation

```python
# Invalidate by model
await cache.invalidate_model("User")

# Invalidate specific key
await cache.delete("user:123")
```

### Cache Warming

```python
# Warm cache with common queries
queries = [
    ("active_users", lambda: User.objects.filter(is_active=True).all()),
    ("recent_posts", lambda: Post.objects.order_by("-created_at").limit(10).all()),
]

results = await cache.warm_cache(queries, concurrent=5)
```

### Cache Statistics

```python
stats = cache.get_statistics()

print(f"Hit rate: {stats['hit_rate']:.1f}%")
print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Avg latency: {stats['avg_latency_ms']:.2f}ms")
```

---

## Query Profiler

Tracks query performance and detects issues.

### Configuration

```python
from covet.database.orm.profiler import QueryProfiler, ProfilerConfig

config = ProfilerConfig(
    slow_query_threshold=100.0,  # 100ms
    enable_slow_query_logging=True,
    enable_n_plus_one_detection=True,
    enable_memory_tracking=True,
)

profiler = QueryProfiler(config)
```

### Profiling Queries

```python
# Synchronous context manager
with profiler.profile_query("get_user", sql="SELECT * FROM users WHERE id = $1"):
    # Execute query
    pass

# Asynchronous context manager
async with profiler.profile_query_async("get_users", sql="SELECT * FROM users"):
    users = await User.objects.all()
```

### Slow Query Detection

```python
# Get slow queries
slow_queries = profiler.get_slow_queries(limit=10)

for query in slow_queries:
    print(f"Query: {query.query_id}")
    print(f"Duration: {query.duration_ms:.2f}ms")
    print(f"SQL: {query.sql}")
```

### N+1 Query Detection

```python
# Detect N+1 patterns
patterns = profiler.detect_n_plus_one()

for pattern in patterns:
    print(f"Pattern: {pattern['query']}")
    print(f"Count: {pattern['count']}")
    print(f"Total time: {pattern['total_duration_ms']:.2f}ms")
    print("FIX: Use select_related() or prefetch_related()")
```

### Performance Baselines

```python
# Set baseline
profiler.set_baseline("SELECT * FROM users WHERE email = ?", 10.0)

# Detect regressions
regressions = profiler.detect_regressions(threshold_factor=1.5)

for reg in regressions:
    print(f"Query: {reg['query']}")
    print(f"Baseline: {reg['baseline_ms']:.2f}ms")
    print(f"Current: {reg['current_avg_ms']:.2f}ms")
    print(f"Slowdown: {reg['slowdown_factor']:.1f}x")
```

### Alerts

```python
# Add custom alert
profiler.add_alert(AlertLevel.WARNING, "High query rate detected")

# Get alerts
alerts = profiler.get_alerts(level=AlertLevel.ERROR)

for level, message, timestamp in alerts:
    print(f"[{level.value}] {message} at {timestamp}")
```

---

## Batch Operations

Optimized bulk operations for high-throughput scenarios.

### Configuration

```python
from covet.database.orm.batch_operations import (
    BatchOperations,
    BatchConfig,
    ConflictResolution,
)

config = BatchConfig(
    batch_size=1000,
    enable_progress_tracking=True,
    enable_auto_tuning=True,
)

batch_ops = BatchOperations(database_adapter=adapter, config=config)
```

### Bulk Insert

```python
# Prepare data
users = [
    {"username": f"user{i}", "email": f"user{i}@example.com"}
    for i in range(10000)
]

# Progress callback
def on_progress(current, total):
    print(f"Progress: {current}/{total} batches")

# Execute bulk insert
result = await batch_ops.bulk_insert(
    table="users",
    records=users,
    batch_size=1000,
    conflict_resolution=ConflictResolution.IGNORE,
    on_progress=on_progress,
)

print(f"Inserted {result.rows_affected} rows in {result.duration_seconds:.2f}s")
print(f"Throughput: {result.rows_per_second:.0f} rows/sec")
```

### Bulk Update

```python
# Prepare updates
updates = [
    {"id": i, "age": 25, "updated_at": datetime.now()}
    for i in range(1, 1001)
]

# Execute bulk update
result = await batch_ops.bulk_update(
    table="users",
    updates=updates,
    key_column="id",
    batch_size=500,
)

print(f"Updated {result.rows_affected} rows")
```

### Bulk Delete

```python
# Delete by IDs
user_ids = list(range(1, 1001))

result = await batch_ops.bulk_delete(
    table="users",
    key_column="id",
    key_values=user_ids,
    batch_size=500,
)

print(f"Deleted {result.rows_affected} rows")
```

---

## Best Practices

### 1. Query Optimization

- Always profile queries before optimizing
- Use EXPLAIN to understand execution plans
- Start with conservative optimization level
- Monitor impact after applying optimizations

### 2. Indexing Strategy

- Index columns used in WHERE, JOIN, ORDER BY
- Use composite indexes for multi-column queries
- Monitor index usage and drop unused indexes
- Consider partial indexes for PostgreSQL
- Balance query speed vs. write performance

### 3. Caching Strategy

- Cache frequently accessed, slowly changing data
- Use appropriate TTL values
- Implement cache warming for critical queries
- Monitor cache hit rates (target >80%)
- Invalidate caches on data changes

### 4. N+1 Query Prevention

- Always use `select_related()` for ForeignKey
- Always use `prefetch_related()` for ManyToMany
- Enable N+1 detection in development
- Profile application before production deployment

### 5. Batch Operations

- Use bulk operations for >100 rows
- Choose appropriate batch sizes (1000-5000)
- Implement progress tracking for long operations
- Use transactions appropriately
- Handle errors gracefully

---

## Performance Tuning

### Database Configuration

#### PostgreSQL

```sql
-- Increase shared_buffers (25% of RAM)
shared_buffers = 8GB

-- Increase work_mem for sorting
work_mem = 64MB

-- Enable parallel queries
max_parallel_workers_per_gather = 4

-- Increase maintenance_work_mem
maintenance_work_mem = 1GB
```

#### MySQL

```ini
[mysqld]
innodb_buffer_pool_size = 8G
innodb_log_file_size = 512M
max_connections = 500
query_cache_size = 256M
```

### Application Configuration

```python
# Connection pool size
DATABASE = {
    "min_connections": 10,
    "max_connections": 100,
    "timeout": 30,
}

# Cache configuration
CACHE = {
    "backend": "redis",
    "default_ttl": 300,
    "max_size": 10000,
}

# Profiler configuration
PROFILER = {
    "slow_query_threshold": 100,
    "enable_n_plus_one_detection": True,
}
```

---

## Troubleshooting

### Common Issues

#### High Query Latency

**Symptoms**: Queries taking >100ms

**Diagnosis**:
```python
# Run EXPLAIN
plan = await analyzer.explain_query(sql, params)
print(plan.sequential_scans)  # Check for seq scans

# Check indexes
recommendations = await advisor.get_recommendations()
```

**Solutions**:
- Add missing indexes
- Optimize query structure
- Use query caching
- Implement pagination

#### Low Cache Hit Rate

**Symptoms**: Cache hit rate <50%

**Diagnosis**:
```python
stats = cache.get_statistics()
print(f"Hit rate: {stats['hit_rate']:.1f}%")
```

**Solutions**:
- Increase cache size
- Adjust TTL values
- Implement cache warming
- Review invalidation strategy

#### N+1 Queries

**Symptoms**: Many repetitive queries

**Diagnosis**:
```python
patterns = profiler.detect_n_plus_one()
```

**Solutions**:
```python
# Instead of:
users = await User.objects.all()
for user in users:
    posts = await user.posts.all()  # N+1!

# Use:
users = await User.objects.prefetch_related('posts').all()
for user in users:
    posts = await user.posts.all()  # No extra queries
```

#### Slow Batch Operations

**Symptoms**: Throughput <1000 rows/sec

**Diagnosis**:
```python
stats = batch_ops.get_statistics()
print(f"Throughput: {stats['avg_throughput_rows_per_second']:.0f}")
```

**Solutions**:
- Increase batch size
- Use COPY protocol (PostgreSQL)
- Disable triggers temporarily
- Add indexes after bulk insert

---

## Production Deployment Checklist

- [ ] Enable query profiling
- [ ] Configure appropriate cache size and TTL
- [ ] Set up index monitoring
- [ ] Implement slow query alerting
- [ ] Configure connection pooling
- [ ] Set up performance baselines
- [ ] Enable N+1 detection in staging
- [ ] Review and apply index recommendations
- [ ] Configure backup and recovery
- [ ] Set up monitoring dashboards

---

## Additional Resources

- [CovetPy ORM Documentation](../orm/)
- [Database Performance Tuning](./PERFORMANCE_TUNING.md)
- [Caching Strategies](./CACHING_STRATEGIES.md)
- [Index Design Patterns](./INDEX_DESIGN.md)

---

**For production support, contact the CovetPy team or visit our GitHub repository.**
