# Runbook: High Memory Usage

## Alert Details
- **Alert Name:** `HighMemoryUsage`
- **Severity:** HIGH
- **Threshold:** Memory usage > 90% for 5 minutes
- **SLA:** 15 minutes to mitigate

## Symptoms
- System memory usage > 90%
- OOM killer activated
- Application slowness
- Swap usage increasing

## Investigation
```bash
# Check memory usage
free -h

# Top memory consumers
ps aux --sort=-%mem | head -20

# Check for memory leaks
docker stats covetpy-app

# Python memory profiling
docker exec covetpy-app python -c "
import psutil
process = psutil.Process()
print(f'RSS: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'VMS: {process.memory_info().vms / 1024 / 1024:.2f} MB')
"
```

## Resolution
1. **Restart leaking service**
   ```bash
   docker restart covetpy-app
   ```

2. **Reduce cache size**
   ```bash
   docker exec redis redis-cli FLUSHDB
   ```

3. **Tune application memory settings**
   ```python
   # Reduce worker count
   WORKERS = 2  # Was 4

   # Enable garbage collection tuning
   import gc
   gc.set_threshold(700, 10, 10)
   ```

4. **Scale horizontally** if sustained high usage

## Prevention
- Implement memory monitoring
- Set max memory limits in Docker
- Use memory profiling in development

## Verification
```bash
free -h | grep Mem  # Should show > 20% available
```
