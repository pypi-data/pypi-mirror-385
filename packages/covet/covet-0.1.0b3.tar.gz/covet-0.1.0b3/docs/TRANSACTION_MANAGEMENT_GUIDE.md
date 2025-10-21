# CovetPy Transaction Management Guide

**Version 1.0.0**
**Sprint 5 Implementation**

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Features](#core-features)
4. [Nested Transactions](#nested-transactions)
5. [Automatic Retry Logic](#automatic-retry-logic)
6. [Isolation Levels](#isolation-levels)
7. [Transaction Hooks](#transaction-hooks)
8. [Transaction Timeout](#transaction-timeout)
9. [Monitoring & Metrics](#monitoring--metrics)
10. [Dashboard](#dashboard)
11. [Best Practices](#best-practices)
12. [API Reference](#api-reference)
13. [Troubleshooting](#troubleshooting)

---

## Overview

CovetPy's Transaction Management System provides enterprise-grade transaction handling for database operations with comprehensive features for data integrity, concurrency control, and operational visibility.

### Key Features

- **Nested Transactions**: Support for 3+ levels of nesting using SAVEPOINT mechanism
- **Automatic Retry**: Exponential backoff retry logic for deadlock recovery
- **Isolation Levels**: Full support for READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE
- **Transaction Hooks**: Lifecycle hooks for custom behavior (pre/post commit/rollback)
- **Timeout Support**: Prevent long-running transactions with automatic timeout
- **Comprehensive Monitoring**: Real-time metrics and performance tracking
- **Real-time Dashboard**: Web-based visualization of transaction health
- **Multi-database Support**: Works with PostgreSQL, MySQL, SQLite

---

## Quick Start

### Installation

```python
from covet.database.transaction import TransactionManager, IsolationLevel
from covet.database.adapters.postgresql import PostgreSQLAdapter

# Initialize database adapter
adapter = PostgreSQLAdapter(
    host='localhost',
    port=5432,
    database='mydb',
    user='postgres',
    password='secret'
)

# Create transaction manager
manager = TransactionManager(adapter)
```

### Basic Transaction

```python
# Simple transaction with automatic commit/rollback
async with manager.atomic() as txn:
    await txn.connection.execute(
        "INSERT INTO users (name, email) VALUES ($1, $2)",
        ("Alice", "alice@example.com")
    )
    # Automatically commits on success
    # Automatically rolls back on exception
```

---

## Core Features

### 1. Basic Transaction Operations

#### Commit on Success

```python
async with manager.atomic() as txn:
    # Execute database operations
    await txn.connection.execute("INSERT INTO orders (user_id, amount) VALUES ($1, $2)", (1, 100))
    await txn.connection.execute("UPDATE accounts SET balance = balance - $1 WHERE id = $2", (100, 1))
    # Transaction commits automatically when context exits
```

#### Automatic Rollback on Error

```python
try:
    async with manager.atomic() as txn:
        await txn.connection.execute("INSERT INTO orders ...")
        raise ValueError("Payment validation failed")
        # Transaction will rollback automatically
except ValueError:
    print("Transaction rolled back")
```

### 2. Transaction State

```python
async with manager.atomic() as txn:
    print(f"State: {txn.state}")  # TransactionState.ACTIVE
    print(f"Duration: {txn.duration_ms}ms")  # Current duration
    print(f"Is nested: {txn.is_nested}")  # False for top-level
    print(f"Level: {txn.level}")  # 0 for top-level
```

---

## Nested Transactions

CovetPy supports **deep transaction nesting (3+ levels)** using database SAVEPOINT mechanism.

### Two-Level Nesting

```python
async with manager.atomic() as outer:
    # Outer transaction operations
    await outer.connection.execute("INSERT INTO orders (id, total) VALUES (1, 100)")

    async with manager.atomic() as inner:
        # Inner transaction operations
        await inner.connection.execute("INSERT INTO order_items (order_id, product_id) VALUES (1, 101)")
        # Inner transaction can rollback independently
```

### Three-Level Nesting (Meeting Requirements)

```python
async with manager.atomic() as level1:
    print(f"Level 1: {level1.level}")  # 0
    await level1.connection.execute("INSERT INTO organizations (name) VALUES ('Acme Corp')")

    async with manager.atomic() as level2:
        print(f"Level 2: {level2.level}")  # 1
        await level2.connection.execute("INSERT INTO departments (org_id, name) VALUES (1, 'Engineering')")

        async with manager.atomic() as level3:
            print(f"Level 3: {level3.level}")  # 2
            await level3.connection.execute("INSERT INTO teams (dept_id, name) VALUES (1, 'Backend')")

            # All three levels share the same connection
            assert level1.connection == level2.connection == level3.connection
```

### Nested Transaction Isolation

**Key Benefit**: Inner transaction rollback doesn't affect outer transaction.

```python
async with manager.atomic() as outer:
    await outer.connection.execute("INSERT INTO accounts (id, balance) VALUES (1, 1000)")

    # Try to process a payment
    try:
        async with manager.atomic() as inner:
            await inner.connection.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
            await inner.connection.execute("INSERT INTO payments (account_id, amount) VALUES (1, 100)")
            raise ValueError("Payment gateway error")  # Inner transaction rolls back
    except ValueError:
        pass

    # Outer transaction continues
    await outer.connection.execute("INSERT INTO audit_log (message) VALUES ('Payment failed')")
    # Outer transaction commits successfully
```

### Manual Savepoint Control

```python
async with manager.atomic() as txn:
    # Create manual savepoint
    sp1 = await txn.create_savepoint("before_update")

    await txn.connection.execute("UPDATE users SET balance = balance - 100 WHERE id = 1")

    # Rollback to savepoint if needed
    if some_condition:
        await txn.rollback_to_savepoint(sp1)

    # Or release savepoint to commit changes
    await txn.release_savepoint(sp1)
```

---

## Automatic Retry Logic

The `@retry` decorator provides automatic retry with exponential backoff for transient failures (e.g., deadlocks).

### Basic Retry

```python
@manager.retry(max_attempts=3)
async def transfer_funds(from_account: int, to_account: int, amount: float):
    async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
        # Debit source account
        await txn.connection.execute(
            "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
            (amount, from_account)
        )

        # Credit destination account
        await txn.connection.execute(
            "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
            (amount, to_account)
        )

# Call function - will retry on deadlock
await transfer_funds(1, 2, 100.0)
```

### Custom Retry Configuration

```python
@manager.retry(
    max_attempts=5,              # Try up to 5 times
    initial_delay=0.5,           # Start with 500ms delay
    backoff_multiplier=2.0,      # Double delay each retry
    exceptions=(DeadlockError, TimeoutError)  # Retry on these errors
)
async def complex_operation():
    async with manager.atomic() as txn:
        # Complex multi-table update
        pass
```

### Retry Behavior

- **Attempt 1**: Immediate execution
- **Attempt 2**: Wait 500ms (initial_delay)
- **Attempt 3**: Wait 1000ms (500ms × 2.0)
- **Attempt 4**: Wait 2000ms (1000ms × 2.0)
- **Attempt 5**: Wait 4000ms (2000ms × 2.0)

### Deadlock Detection

The retry system automatically detects deadlocks across different databases:

```python
# Automatically detected deadlock indicators:
# - PostgreSQL: "deadlock detected", "could not serialize access"
# - MySQL: "1213 Deadlock found", "lock wait timeout"
# - SQL Server: "Transaction was deadlocked"

@manager.retry(max_attempts=3)
async def concurrent_update():
    async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
        # This might deadlock with concurrent transactions
        await txn.connection.execute("UPDATE inventory SET quantity = quantity - 1 WHERE product_id = $1", (42,))
```

---

## Isolation Levels

CovetPy supports all standard SQL isolation levels.

### Isolation Level Overview

| Level | Dirty Reads | Non-repeatable Reads | Phantom Reads | Use Case |
|-------|-------------|---------------------|---------------|----------|
| READ UNCOMMITTED | Yes | Yes | Yes | Analytics (rarely used) |
| READ COMMITTED | No | Yes | Yes | Default for most apps |
| REPEATABLE READ | No | No | Yes | Financial transactions |
| SERIALIZABLE | No | No | No | Critical data integrity |

### Setting Isolation Level

```python
# READ COMMITTED (default)
async with manager.atomic(isolation=IsolationLevel.READ_COMMITTED) as txn:
    # Prevents dirty reads
    pass

# REPEATABLE READ
async with manager.atomic(isolation=IsolationLevel.REPEATABLE_READ) as txn:
    # Prevents dirty and non-repeatable reads
    pass

# SERIALIZABLE (highest isolation)
async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
    # Prevents all concurrency anomalies
    pass
```

### Real-World Example: Bank Transfer

```python
@manager.retry(max_attempts=3)
async def bank_transfer(from_account: int, to_account: int, amount: float):
    # Use SERIALIZABLE for financial transactions
    async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
        # Check source balance
        balance = await txn.connection.fetchval(
            "SELECT balance FROM accounts WHERE id = $1",
            (from_account,)
        )

        if balance < amount:
            raise ValueError("Insufficient funds")

        # Debit source
        await txn.connection.execute(
            "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
            (amount, from_account)
        )

        # Credit destination
        await txn.connection.execute(
            "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
            (amount, to_account)
        )

        # Log transaction
        await txn.connection.execute(
            "INSERT INTO transactions (from_account, to_account, amount) VALUES ($1, $2, $3)",
            (from_account, to_account, amount)
        )
```

---

## Transaction Hooks

Hooks allow custom behavior at specific points in the transaction lifecycle.

### Available Hooks

- **pre_commit**: Called before commit (use for validation)
- **post_commit**: Called after successful commit (use for notifications)
- **pre_rollback**: Called before rollback (use for cleanup)
- **post_rollback**: Called after rollback (use for error recovery)

### Example: Audit Logging

```python
async def log_commit(txn: Transaction):
    logger.info(f"Transaction {txn.transaction_id} committed (duration: {txn.duration_ms}ms)")

async def log_rollback(txn: Transaction):
    logger.error(f"Transaction {txn.transaction_id} rolled back")

hooks = TransactionHooks(
    post_commit=log_commit,
    post_rollback=log_rollback
)

async with manager.atomic(hooks=hooks) as txn:
    await txn.connection.execute("INSERT INTO orders ...")
```

### Example: Cache Invalidation

```python
async def invalidate_cache(txn: Transaction):
    """Invalidate cache after successful commit."""
    await cache.invalidate('users')

hooks = TransactionHooks(post_commit=invalidate_cache)

async with manager.atomic(hooks=hooks) as txn:
    await txn.connection.execute("UPDATE users SET name = $1 WHERE id = $2", ("Alice", 1))
    # Cache will be invalidated after commit
```

### Example: Pre-Commit Validation

```python
async def validate_before_commit(txn: Transaction):
    """Validate data before commit."""
    # Check business rules
    if not await check_business_rules(txn):
        raise ValueError("Business rule violation")

hooks = TransactionHooks(pre_commit=validate_before_commit)

async with manager.atomic(hooks=hooks) as txn:
    await txn.connection.execute("UPDATE accounts SET balance = $1 WHERE id = $2", (1000, 1))
    # Validation will run before commit
```

---

## Transaction Timeout

Prevent long-running transactions with automatic timeout.

### Setting Timeout

```python
# Transaction will rollback if it exceeds 30 seconds
async with manager.atomic(timeout=30.0) as txn:
    await txn.connection.execute("INSERT INTO large_table ...")
```

### Timeout with Retry

```python
@manager.retry(max_attempts=3)
async def long_operation():
    # Give each attempt 60 seconds
    async with manager.atomic(timeout=60.0) as txn:
        await txn.connection.execute("VACUUM ANALYZE")
```

### Global Timeout Configuration

```python
config = TransactionConfig(
    isolation_level=IsolationLevel.READ_COMMITTED,
    timeout=30.0,  # Default timeout for all transactions
)

manager = TransactionManager(adapter, default_config=config)
```

---

## Monitoring & Metrics

CovetPy provides comprehensive transaction monitoring.

### Getting Current Metrics

```python
metrics = manager.get_metrics()

print(f"Total transactions: {metrics['total_transactions']}")
print(f"Success rate: {metrics['success_rate']:.1f}%")
print(f"Average duration: {metrics['average_duration_ms']:.2f}ms")
print(f"Active transactions: {metrics['active_transactions']}")
print(f"Deadlocks: {metrics['deadlock_count']}")
print(f"Timeouts: {metrics['timeout_count']}")
```

### Getting Active Transactions

```python
active_txns = manager.get_active_transactions()

for txn in active_txns:
    print(f"Transaction {txn['transaction_id']}")
    print(f"  Level: {txn['level']}")
    print(f"  Duration: {txn['duration_ms']:.0f}ms")
    print(f"  Isolation: {txn['isolation']}")
    print(f"  State: {txn['state']}")
```

### Resetting Metrics

```python
# Reset all metrics to zero
manager.reset_metrics()
```

### Long-Running Transaction Detection

```python
# Configure threshold for long-running transactions
manager = TransactionManager(
    adapter,
    long_transaction_threshold=10.0  # Warn if transaction exceeds 10 seconds
)

# Long-running transactions will be logged as warnings
async with manager.atomic() as txn:
    await asyncio.sleep(15)  # This will trigger a warning
```

### Background Monitoring

```python
# Start background monitoring (logs metrics every 60 seconds)
await manager.start_monitoring(interval=60.0)

# ... application runs ...

# Stop monitoring when shutting down
await manager.stop_monitoring()
```

---

## Dashboard

CovetPy includes a real-time web dashboard for transaction monitoring.

### Starting the Dashboard

```python
from covet.database.transaction import TransactionDashboard

# Create dashboard
dashboard = TransactionDashboard(
    transaction_manager=manager,
    history_retention=3600,  # Keep 1 hour of history
    snapshot_interval=10.0,  # Take snapshot every 10 seconds
)

# Start monitoring
await dashboard.start()
```

### Viewing Dashboard HTML

```python
# Get dashboard HTML
html = dashboard.get_dashboard_html()

# Serve via web framework (e.g., Starlette, FastAPI)
@app.get("/transaction-dashboard")
async def transaction_dashboard():
    return HTMLResponse(dashboard.get_dashboard_html())
```

### Dashboard Features

- **Real-time Metrics**: Live transaction statistics
- **Health Status**: Overall system health score (0-100)
- **Active Transactions**: List of currently running transactions
- **Recent Alerts**: Warning and error alerts
- **Recommendations**: Automated performance recommendations

### Getting Historical Data

```python
# Get last 60 minutes of history
history = dashboard.get_history(minutes=60)

# Get last 100 snapshots
history = dashboard.get_history(limit=100)
```

### Getting Alerts

```python
# Get all alerts from last hour
alerts = dashboard.get_alerts(minutes=60)

# Get only critical alerts
alerts = dashboard.get_alerts(level=AlertLevel.CRITICAL)

# Get last 10 alerts
alerts = dashboard.get_alerts(limit=10)
```

### Performance Trends

```python
trends = dashboard.get_performance_trends(minutes=60)

print(f"Transaction count change: {trends['trends']['transaction_count_change']}")
print(f"Success rate change: {trends['trends']['success_rate_change']}")
print(f"Average duration change: {trends['trends']['average_duration_change']}")
```

### Health Status

```python
health = dashboard.get_health_status()

print(f"Status: {health['status']}")  # healthy, degraded, warning, critical
print(f"Health score: {health['health_score']}/100")
print(f"Issues: {health['issues']}")
print(f"Recommendations: {health['recommendations']}")
```

### Generating Reports

```python
# JSON report
json_report = dashboard.generate_report(format='json', include_history=True)

# CSV report
csv_report = dashboard.generate_report(format='csv', history_minutes=60)

# Save to file
with open('transaction_report.json', 'w') as f:
    f.write(json_report)
```

### Alert Thresholds

```python
# Customize alert thresholds
dashboard = TransactionDashboard(
    transaction_manager=manager,
    alert_thresholds={
        'max_active_transactions': 100,
        'max_transaction_duration_ms': 30000,  # 30 seconds
        'min_success_rate': 95.0,  # 95%
        'max_deadlock_count': 10,
        'max_timeout_count': 5,
    }
)
```

---

## Best Practices

### 1. Keep Transactions Short

```python
# GOOD: Short transaction
async with manager.atomic() as txn:
    await txn.connection.execute("UPDATE users SET last_login = NOW() WHERE id = $1", (user_id,))

# BAD: Long transaction with external API calls
async with manager.atomic() as txn:
    await txn.connection.execute("INSERT INTO orders ...")
    await send_email_notification()  # DON'T do this inside transaction
    await charge_credit_card()       # DON'T do this inside transaction
```

### 2. Use Appropriate Isolation Levels

```python
# READ COMMITTED for most operations
async with manager.atomic(isolation=IsolationLevel.READ_COMMITTED) as txn:
    await txn.connection.execute("INSERT INTO logs ...")

# SERIALIZABLE for critical financial transactions
async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
    # Money transfer logic
    pass
```

### 3. Always Use Retry for Deadlock-Prone Operations

```python
# GOOD: Retry wrapper for concurrent updates
@manager.retry(max_attempts=3)
async def update_inventory(product_id: int, quantity: int):
    async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
        await txn.connection.execute(
            "UPDATE inventory SET quantity = quantity - $1 WHERE product_id = $2",
            (quantity, product_id)
        )

# BAD: No retry for operation that might deadlock
async def update_inventory(product_id: int, quantity: int):
    async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
        await txn.connection.execute(...)  # Might fail on deadlock
```

### 4. Use Transaction Hooks for Side Effects

```python
# GOOD: Use post-commit hook for side effects
async def send_notification(txn: Transaction):
    await email_service.send("Transaction completed")

hooks = TransactionHooks(post_commit=send_notification)

async with manager.atomic(hooks=hooks) as txn:
    await txn.connection.execute("INSERT INTO orders ...")

# BAD: Side effects inside transaction
async with manager.atomic() as txn:
    await txn.connection.execute("INSERT INTO orders ...")
    await email_service.send("Transaction completed")  # DON'T do this
```

### 5. Set Timeouts for Long Operations

```python
# GOOD: Set timeout for potentially long operations
async with manager.atomic(timeout=60.0) as txn:
    await txn.connection.execute("DELETE FROM old_logs WHERE created_at < NOW() - INTERVAL '1 year'")

# BAD: No timeout for potentially long operation
async with manager.atomic() as txn:
    await txn.connection.execute("DELETE FROM old_logs ...")  # Might run forever
```

### 6. Monitor Transaction Metrics

```python
# Enable background monitoring
await manager.start_monitoring(interval=60.0)

# Start dashboard
dashboard = TransactionDashboard(manager)
await dashboard.start()

# Check metrics regularly
metrics = manager.get_metrics()
if metrics['success_rate'] < 95:
    logger.warning("Transaction success rate below 95%")
```

### 7. Use Nested Transactions for Complex Operations

```python
@manager.retry(max_attempts=3)
async def create_order_with_items(order_data: dict, items: list):
    async with manager.atomic() as order_txn:
        # Create order
        order_id = await order_txn.connection.fetchval(
            "INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING id",
            (order_data['user_id'], order_data['total'])
        )

        # Create order items (nested transaction)
        for item in items:
            try:
                async with manager.atomic() as item_txn:
                    await item_txn.connection.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity) VALUES ($1, $2, $3)",
                        (order_id, item['product_id'], item['quantity'])
                    )
            except Exception as e:
                logger.error(f"Failed to create item: {e}")
                # Continue with other items
```

---

## API Reference

### TransactionManager

#### Constructor

```python
TransactionManager(
    database_adapter: Any,
    default_config: Optional[TransactionConfig] = None,
    long_transaction_threshold: float = 10.0
)
```

#### Methods

- `atomic(isolation, timeout, read_only, hooks)`: Context manager for transactions
- `retry(max_attempts, backoff_multiplier, initial_delay, exceptions)`: Retry decorator
- `get_metrics()`: Get current transaction metrics
- `get_active_transactions()`: Get list of active transactions
- `reset_metrics()`: Reset all metrics to zero
- `start_monitoring(interval)`: Start background monitoring
- `stop_monitoring()`: Stop background monitoring

### Transaction

#### Properties

- `transaction_id`: Unique transaction identifier
- `state`: Current transaction state
- `level`: Nesting level (0 for top-level)
- `is_nested`: Boolean indicating if nested
- `is_active`: Boolean indicating if active
- `duration_ms`: Duration in milliseconds
- `connection`: Database connection object

#### Methods

- `create_savepoint(name)`: Create a savepoint
- `rollback_to_savepoint(name)`: Rollback to savepoint
- `release_savepoint(name)`: Release savepoint
- `commit()`: Commit transaction
- `rollback(error)`: Rollback transaction

### IsolationLevel

- `READ_UNCOMMITTED`
- `READ_COMMITTED`
- `REPEATABLE_READ`
- `SERIALIZABLE`

### TransactionConfig

```python
TransactionConfig(
    isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
    timeout: Optional[float] = None,
    read_only: bool = False,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_backoff_multiplier: float = 2.0,
    hooks: Optional[TransactionHooks] = None
)
```

### TransactionHooks

```python
TransactionHooks(
    pre_commit: Optional[Callable] = None,
    post_commit: Optional[Callable] = None,
    pre_rollback: Optional[Callable] = None,
    post_rollback: Optional[Callable] = None
)
```

### TransactionDashboard

#### Constructor

```python
TransactionDashboard(
    transaction_manager: TransactionManager,
    history_retention: int = 3600,
    snapshot_interval: float = 10.0,
    alert_thresholds: Optional[Dict[str, Any]] = None
)
```

#### Methods

- `start()`: Start dashboard monitoring
- `stop()`: Stop dashboard monitoring
- `get_current_metrics()`: Get current metrics
- `get_active_transactions()`: Get active transactions
- `get_history(minutes, limit)`: Get historical data
- `get_alerts(minutes, level, limit)`: Get alerts
- `get_performance_trends(minutes)`: Get performance trends
- `get_health_status()`: Get health status
- `generate_report(format, include_history, history_minutes)`: Generate report
- `get_dashboard_html()`: Get HTML dashboard

---

## Troubleshooting

### Issue: Deadlocks Occurring Frequently

**Symptoms**: High `deadlock_count` in metrics

**Solutions**:
1. Use `@retry` decorator with exponential backoff
2. Increase isolation level to `SERIALIZABLE` for critical sections
3. Review lock ordering in application code
4. Reduce transaction duration
5. Check dashboard recommendations

```python
# Add retry to deadlock-prone operations
@manager.retry(max_attempts=5)
async def concurrent_update():
    async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
        # Your code here
        pass
```

### Issue: High Transaction Latency

**Symptoms**: High `average_duration_ms` in metrics

**Solutions**:
1. Profile slow queries
2. Add database indexes
3. Reduce transaction scope
4. Use read-only transactions for queries
5. Check for N+1 query problems

```python
# Use read-only flag for queries
async with manager.atomic(read_only=True) as txn:
    # Query operations only
    pass
```

### Issue: Transaction Timeouts

**Symptoms**: High `timeout_count` in metrics

**Solutions**:
1. Increase timeout threshold
2. Optimize slow queries
3. Split long operations into smaller transactions
4. Use batch operations

```python
# Increase timeout for long operations
async with manager.atomic(timeout=120.0) as txn:
    # Long-running operation
    pass
```

### Issue: Low Success Rate

**Symptoms**: `success_rate` below 95%

**Solutions**:
1. Check application logs for errors
2. Review dashboard alerts
3. Verify database connectivity
4. Check for resource exhaustion
5. Add proper error handling

```python
# Get detailed error information
metrics = manager.get_metrics()
if metrics['success_rate'] < 95:
    alerts = dashboard.get_alerts(level=AlertLevel.ERROR)
    for alert in alerts:
        print(f"Error: {alert['message']}")
```

### Issue: Too Many Active Transactions

**Symptoms**: `active_transactions` constantly high

**Solutions**:
1. Reduce transaction duration
2. Increase connection pool size
3. Check for transaction leaks (not committing/rolling back)
4. Review application logic for blocking operations inside transactions

```python
# Monitor active transactions
active = manager.get_active_transactions()
for txn in active:
    if txn['duration_ms'] > 30000:
        print(f"Long-running transaction: {txn['transaction_id']}")
```

---

## Performance Tuning

### Connection Pool Configuration

```python
from covet.database.adapters.postgresql import PostgreSQLAdapter

adapter = PostgreSQLAdapter(
    host='localhost',
    database='mydb',
    min_pool_size=10,    # Minimum connections
    max_pool_size=50,    # Maximum connections
    command_timeout=60.0 # Command timeout
)
```

### Batch Operations

```python
# GOOD: Batch insert
async with manager.atomic() as txn:
    await txn.connection.executemany(
        "INSERT INTO users (name, email) VALUES ($1, $2)",
        [(f"User{i}", f"user{i}@example.com") for i in range(1000)]
    )

# BAD: Individual inserts
async with manager.atomic() as txn:
    for i in range(1000):
        await txn.connection.execute(
            "INSERT INTO users (name, email) VALUES ($1, $2)",
            (f"User{i}", f"user{i}@example.com")
        )
```

---

## Examples

### Complete E-commerce Order Processing

```python
@manager.retry(max_attempts=3)
async def process_order(user_id: int, cart_items: list, payment_info: dict):
    """
    Process an e-commerce order with full transaction management.
    """
    async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as order_txn:
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        # Create order
        order_id = await order_txn.connection.fetchval(
            "INSERT INTO orders (user_id, total, status) VALUES ($1, $2, 'pending') RETURNING id",
            (user_id, total)
        )

        # Add order items
        for item in cart_items:
            async with manager.atomic() as item_txn:
                # Check inventory
                available = await item_txn.connection.fetchval(
                    "SELECT quantity FROM inventory WHERE product_id = $1 FOR UPDATE",
                    (item['product_id'],)
                )

                if available < item['quantity']:
                    raise ValueError(f"Insufficient inventory for product {item['product_id']}")

                # Insert order item
                await item_txn.connection.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
                    (order_id, item['product_id'], item['quantity'], item['price'])
                )

                # Update inventory
                await item_txn.connection.execute(
                    "UPDATE inventory SET quantity = quantity - $1 WHERE product_id = $2",
                    (item['quantity'], item['product_id'])
                )

        # Update order status
        await order_txn.connection.execute(
            "UPDATE orders SET status = 'completed' WHERE id = $1",
            (order_id,)
        )

        return order_id

# Use with hooks for notifications
async def send_order_confirmation(txn: Transaction):
    # Send confirmation email after successful order
    pass

hooks = TransactionHooks(post_commit=send_order_confirmation)

order_id = await process_order(user_id=1, cart_items=cart, payment_info=payment)
```

---

## Sprint 5 Completion Summary

### Implemented Features ✓

1. **Nested Transactions (3+ levels deep)** ✓
   - SAVEPOINT mechanism
   - Automatic savepoint management
   - Manual savepoint control

2. **Automatic Retry Logic** ✓
   - @retry decorator
   - Exponential backoff
   - Configurable attempts and delays
   - Custom exception handling

3. **Transaction Features** ✓
   - All isolation levels (READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE)
   - Read-only transactions
   - Transaction hooks (pre/post commit/rollback)
   - Transaction timeout support

4. **Monitoring** ✓
   - Transaction duration tracking
   - Long-running transaction detection
   - Comprehensive metrics (count, success rate, duration)
   - Real-time dashboard with HTML visualization
   - Alert system
   - Performance trends
   - Health status monitoring

### Definition of Done ✓

- [x] Nested transactions work (3+ levels deep)
- [x] Automatic retry works on deadlocks
- [x] All isolation levels supported
- [x] Transaction metrics tracked
- [x] Comprehensive documentation with examples
- [x] Unit tests covering all features

---

**For support or questions, refer to the CovetPy documentation or contact the development team.**
