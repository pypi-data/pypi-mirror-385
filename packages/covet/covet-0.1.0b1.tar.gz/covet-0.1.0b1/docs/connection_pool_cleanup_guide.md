# CovetPy Connection Pool Cleanup System - Production Guide

## Overview

The CovetPy framework includes a comprehensive connection pool cleanup system designed by a Senior Database Administrator with 20 years of experience. This system provides enterprise-grade connection management with automatic leak detection, memory pressure monitoring, and graceful shutdown procedures.

## Key Features

### 1. Connection Leak Detection and Prevention
- **Automatic Detection**: Monitors connections checked out for extended periods
- **Stack Trace Capture**: Records checkout locations for debugging
- **Configurable Thresholds**: Customizable leak detection timeouts
- **Force Cleanup**: Automatic cleanup of leaked connections after timeout

### 2. Memory Pressure Monitoring
- **System Memory Monitoring**: Tracks system and process memory usage
- **Automatic Cleanup**: Removes idle connections under memory pressure
- **Configurable Thresholds**: Set memory pressure trigger points
- **Graceful Degradation**: Maintains minimum connections during cleanup

### 3. Health Monitoring and Recovery
- **Continuous Health Checks**: Regular validation of connection health
- **Automatic Recovery**: Self-healing capabilities for degraded pools
- **Comprehensive Metrics**: Detailed performance and health statistics
- **Alert Generation**: Proactive notifications for pool health issues

### 4. Graceful Shutdown Procedures
- **Signal Handling**: Responds to SIGTERM and SIGINT gracefully
- **Timeout Management**: Configurable shutdown timeouts
- **Resource Cleanup**: Ensures all connections are properly closed
- **Emergency Cleanup**: Fallback cleanup via atexit handlers

## Configuration Examples

### Development Environment

```python
from covet.database.core.database_base import EnhancedPoolConfig
from covet.database.core.comprehensive_pool_manager import (
    ComprehensivePoolManager, PoolManagerConfig, PoolType
)

# Development pool configuration - focus on debugging
dev_pool_config = EnhancedPoolConfig(
    min_connections=1,
    max_connections=5,
    max_idle_time=300.0,  # 5 minutes
    connection_timeout=30.0,
    
    # Aggressive leak detection for development
    max_checkout_time=60.0,  # 1 minute
    enable_leak_detection=True,
    leak_detection_interval=30.0,  # Check every 30 seconds
    
    # Detailed logging for debugging
    enable_detailed_metrics=True,
    enable_health_check_logging=True,
    enable_performance_logging=True,
    slow_operation_threshold=0.5,  # Log operations > 0.5 seconds
    
    # Conservative memory monitoring
    enable_memory_monitoring=True,
    memory_pressure_threshold=0.7,  # 70% threshold
)

# Development manager configuration
dev_manager_config = PoolManagerConfig(
    default_pool_type=PoolType.ENHANCED,
    enable_cross_pool_monitoring=True,
    monitoring_interval=60.0,  # Check every minute
    enable_automatic_recovery=True,
    recovery_check_interval=120.0,  # Recovery every 2 minutes
)
```

### Production Environment

```python
# Production pool configuration - focus on stability and performance
prod_pool_config = EnhancedPoolConfig(
    min_connections=5,
    max_connections=20,
    max_idle_time=600.0,  # 10 minutes
    connection_timeout=30.0,
    
    # Connection lifecycle management
    max_connection_lifetime=3600.0,  # 1 hour maximum lifetime
    max_checkout_time=300.0,  # 5 minutes maximum checkout
    connection_validation_interval=60.0,
    
    # Leak detection - less aggressive for production
    enable_leak_detection=True,
    leak_detection_interval=120.0,  # Check every 2 minutes
    max_leaked_connections=3,
    leak_cleanup_timeout=600.0,  # 10 minutes before force close
    
    # Memory pressure management
    enable_memory_monitoring=True,
    memory_pressure_threshold=0.85,  # 85% threshold
    memory_check_interval=300.0,  # Check every 5 minutes
    memory_cleanup_batch_size=2,
    
    # Error handling and recovery
    max_connection_errors=5,
    error_recovery_interval=300.0,
    enable_circuit_breaker=True,
    circuit_breaker_failure_threshold=3,
    circuit_breaker_recovery_timeout=60.0,
    
    # Performance optimization
    enable_connection_warming=True,
    warm_connections_count=3,
    enable_stale_connection_removal=True,
    stale_connection_threshold_multiplier=2.0,
    
    # Monitoring - reduced verbosity for production
    enable_detailed_metrics=True,
    enable_health_check_logging=False,
    enable_performance_logging=False,
    slow_operation_threshold=2.0,  # Log operations > 2 seconds
)

# Production manager configuration
prod_manager_config = PoolManagerConfig(
    default_pool_type=PoolType.ENHANCED,
    enable_cross_pool_monitoring=True,
    monitoring_interval=300.0,  # Check every 5 minutes
    enable_automatic_recovery=True,
    recovery_check_interval=600.0,  # Recovery every 10 minutes
    enable_pool_health_alerts=True,
    health_alert_threshold=0.7,  # Alert if less than 70% pools healthy
)
```

### High-Load Environment

```python
# High-load configuration - maximum performance and resilience
high_load_pool_config = EnhancedPoolConfig(
    min_connections=10,
    max_connections=50,
    max_idle_time=300.0,  # 5 minutes - shorter for high turnover
    connection_timeout=15.0,  # Faster timeout for high load
    
    # Aggressive connection management
    max_connection_lifetime=1800.0,  # 30 minutes maximum lifetime
    max_checkout_time=120.0,  # 2 minutes maximum checkout
    connection_validation_interval=30.0,  # Frequent validation
    
    # Proactive leak detection
    enable_leak_detection=True,
    leak_detection_interval=60.0,  # Check every minute
    max_leaked_connections=5,
    leak_cleanup_timeout=300.0,  # 5 minutes before force close
    
    # Aggressive memory management
    enable_memory_monitoring=True,
    memory_pressure_threshold=0.8,  # 80% threshold
    memory_check_interval=120.0,  # Check every 2 minutes
    memory_cleanup_batch_size=5,  # Larger cleanup batches
    
    # Circuit breaker for fault tolerance
    enable_circuit_breaker=True,
    circuit_breaker_failure_threshold=5,
    circuit_breaker_recovery_timeout=30.0,
    
    # Performance optimization
    enable_connection_warming=True,
    warm_connections_count=5,
    enable_stale_connection_removal=True,
    stale_connection_threshold_multiplier=1.5,  # More aggressive cleanup
    
    # Minimal logging overhead
    enable_detailed_metrics=True,
    enable_health_check_logging=False,
    enable_performance_logging=False,
    slow_operation_threshold=5.0,  # Only log very slow operations
)
```

## Database-Specific Configurations

### PostgreSQL Configuration

```python
from covet.database.adapters.postgresql import PostgreSQLAdapter

# PostgreSQL optimized configuration
postgresql_config = EnhancedPoolConfig(
    min_connections=3,
    max_connections=15,
    max_idle_time=600.0,
    
    # PostgreSQL-specific optimizations
    max_connection_lifetime=7200.0,  # 2 hours - PostgreSQL handles long connections well
    health_check_interval=60.0,
    connection_validation_interval=120.0,
    
    # PostgreSQL typically has lower memory pressure tolerance
    memory_pressure_threshold=0.9,  # 90% threshold
    
    # PostgreSQL connection setup can be expensive, so be conservative
    enable_connection_warming=True,
    warm_connections_count=2,
)
```

### MySQL Configuration

```python
from covet.database.adapters.mysql import MySQLAdapter

# MySQL optimized configuration
mysql_config = EnhancedPoolConfig(
    min_connections=2,
    max_connections=20,
    max_idle_time=300.0,  # MySQL times out idle connections
    
    # MySQL-specific optimizations
    max_connection_lifetime=1800.0,  # 30 minutes - MySQL default wait_timeout consideration
    health_check_interval=30.0,  # More frequent due to MySQL timeouts
    connection_validation_interval=60.0,
    
    # MySQL typically needs more aggressive cleanup
    enable_stale_connection_removal=True,
    stale_connection_threshold_multiplier=1.5,
)
```

### SQLite Configuration

```python
from covet.database.adapters.sqlite import SQLiteAdapter

# SQLite optimized configuration (single writer limitation)
sqlite_config = EnhancedPoolConfig(
    min_connections=1,
    max_connections=3,  # SQLite doesn't benefit from many connections
    max_idle_time=1800.0,  # 30 minutes - file-based, no server timeouts
    
    # SQLite-specific optimizations
    max_connection_lifetime=0,  # No lifetime limit for file-based DB
    health_check_interval=300.0,  # Less frequent health checks
    
    # SQLite has minimal memory pressure
    enable_memory_monitoring=False,  # Not as critical for file-based DB
    
    # Conservative settings for file-based database
    enable_connection_warming=False,
    enable_leak_detection=True,
    leak_detection_interval=300.0,  # Less frequent checks
)
```

### MongoDB Configuration

```python
from covet.database.adapters.mongodb import MongoDBAdapter

# MongoDB optimized configuration
mongodb_config = EnhancedPoolConfig(
    min_connections=5,
    max_connections=25,
    max_idle_time=900.0,  # 15 minutes - MongoDB maintains connection state
    
    # MongoDB-specific optimizations
    max_connection_lifetime=3600.0,  # 1 hour
    health_check_interval=120.0,
    
    # MongoDB can handle more connections efficiently
    memory_pressure_threshold=0.85,
    enable_connection_warming=True,
    warm_connections_count=3,
)
```

## Monitoring and Alerting Integration

### Prometheus Metrics Integration

```python
def setup_prometheus_metrics(pool_manager: ComprehensivePoolManager):
    """Setup Prometheus metrics for pool monitoring."""
    from prometheus_client import Gauge, Counter, Histogram
    
    # Define metrics
    pool_connections_total = Gauge('covet_pool_connections_total', 'Total connections', ['pool_name'])
    pool_connections_active = Gauge('covet_pool_connections_active', 'Active connections', ['pool_name'])
    pool_connections_leaked = Gauge('covet_pool_connections_leaked', 'Leaked connections', ['pool_name'])
    pool_response_time = Histogram('covet_pool_response_time_seconds', 'Response time', ['pool_name'])
    pool_cleanup_operations = Counter('covet_pool_cleanup_operations_total', 'Cleanup operations', ['pool_name'])
    
    def update_metrics():
        """Update Prometheus metrics from pool statistics."""
        stats = pool_manager.get_comprehensive_statistics()
        
        for pool_name, pool_stats in stats['pool_stats'].items():
            pool_connections_total.labels(pool_name=pool_name).set(
                pool_stats.get('total_connections', 0)
            )
            pool_connections_active.labels(pool_name=pool_name).set(
                pool_stats.get('checked_out_connections', 0)
            )
            pool_connections_leaked.labels(pool_name=pool_name).set(
                pool_stats.get('leaked_connections', 0)
            )
            
            # Update response time histogram
            response_times = pool_stats.get('response_times', {})
            if response_times.get('avg', 0) > 0:
                pool_response_time.labels(pool_name=pool_name).observe(
                    response_times['avg']
                )
    
    # Register callback to update metrics periodically
    pool_manager.register_cleanup_callback(update_metrics)
    
    return update_metrics
```

### Custom Health Check Integration

```python
def setup_custom_health_checks(pool_manager: ComprehensivePoolManager):
    """Setup custom health check integration."""
    
    def custom_health_check():
        """Custom health check function."""
        health_reports = pool_manager.get_all_health_reports()
        
        for pool_name, report in health_reports.items():
            if not report.is_healthy:
                # Send alert to monitoring system
                send_alert(f"Pool {pool_name} is unhealthy: {', '.join(report.issues)}")
            
            if report.leaked_connections > 5:
                # Critical alert for too many leaks
                send_critical_alert(f"Pool {pool_name} has {report.leaked_connections} leaked connections")
            
            if report.avg_response_time > 10.0:
                # Performance alert
                send_performance_alert(f"Pool {pool_name} has high response time: {report.avg_response_time:.2f}s")
    
    def send_alert(message: str):
        """Send alert to monitoring system."""
        # Implement your alerting logic here
        logger.warning(f"ALERT: {message}")
    
    def send_critical_alert(message: str):
        """Send critical alert to monitoring system."""
        # Implement your critical alerting logic here
        logger.error(f"CRITICAL ALERT: {message}")
    
    def send_performance_alert(message: str):
        """Send performance alert to monitoring system."""
        # Implement your performance alerting logic here
        logger.warning(f"PERFORMANCE ALERT: {message}")
    
    return custom_health_check
```

## Best Practices

### 1. Configuration Tuning

- **Start Conservative**: Begin with lower connection limits and gradually increase based on load testing
- **Monitor Memory**: Keep an eye on memory usage patterns and adjust thresholds accordingly
- **Test Leak Detection**: Regularly test leak detection by intentionally creating leaks in development
- **Validate Health Checks**: Ensure health check intervals balance detection speed with overhead

### 2. Production Deployment

- **Gradual Rollout**: Deploy enhanced pools gradually, starting with non-critical databases
- **Monitor Metrics**: Set up comprehensive monitoring before deploying to production
- **Test Recovery**: Regularly test automatic recovery procedures
- **Document Configuration**: Maintain clear documentation of pool configurations and their rationale

### 3. Troubleshooting

#### High Memory Usage
```python
# Check memory statistics
stats = pool_manager.get_comprehensive_statistics()
memory_info = stats['pool_stats']['your_pool_name'].get('memory_info', {})
print(f"Process memory: {memory_info.get('process_memory_mb', 0):.2f} MB")

# Force cleanup if needed
cleanup_result = pool_manager.force_cleanup_all_pools()
print(f"Cleanup removed {cleanup_result['total_connections_cleaned']} connections")
```

#### Connection Leaks
```python
# Get leaked connection information
leaked_info = pool.get_leaked_connections_info()
for leak in leaked_info:
    print(f"Leaked connection: {leak['thread_id']}, duration: {leak['checkout_duration']:.2f}s")
    print(f"Stack trace: {leak['stack_trace'][-3:]}")  # Last 3 stack frames
```

#### Pool Health Issues
```python
# Validate pool integrity
validation = pool_manager.validate_all_pools()
if not validation['overall_healthy']:
    print("Pool integrity issues detected:")
    for issue in validation['critical_issues']:
        print(f"  - {issue}")
```

### 4. Performance Optimization

- **Connection Warming**: Enable for databases with expensive connection setup (PostgreSQL, Oracle)
- **Batch Cleanup**: Use larger batch sizes for high-load environments
- **Circuit Breakers**: Enable for unstable network conditions
- **Health Check Intervals**: Balance detection speed with system overhead

## Conclusion

The CovetPy connection pool cleanup system provides enterprise-grade connection management with comprehensive monitoring, automatic recovery, and graceful shutdown procedures. By following the configuration examples and best practices in this guide, you can ensure optimal database performance and reliability in your production environment.

For additional support or custom configuration assistance, refer to the comprehensive demonstration script or contact the development team.