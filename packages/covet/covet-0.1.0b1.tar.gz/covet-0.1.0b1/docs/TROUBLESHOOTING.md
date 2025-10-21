# CovetPy Troubleshooting Guide

**Version:** 0.2.0-sprint1
**Last Updated:** 2025-10-11

This guide covers common issues and their solutions when deploying and running CovetPy applications in production.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Server Won't Start](#server-wont-start)
3. [Database Connection Problems](#database-connection-problems)
4. [Performance Issues](#performance-issues)
5. [Memory Problems](#memory-problems)
6. [WebSocket Issues](#websocket-issues)
7. [Security Problems](#security-problems)
8. [Deployment Issues](#deployment-issues)
9. [Common Error Messages](#common-error-messages)
10. [Debugging Tips](#debugging-tips)

---

## Installation Issues

### Problem: pip install fails with build errors

**Symptoms:**
```
ERROR: Failed building wheel for covetpy
ERROR: Could not build wheels for covetpy
```

**Solutions:**

1. **Install build dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y python3-dev build-essential libssl-dev libffi-dev

   # CentOS/RHEL
   sudo dnf install -y python3-devel gcc openssl-devel libffi-devel
   ```

2. **Upgrade pip and setuptools:**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

3. **Use specific Python version:**
   ```bash
   python3.11 -m pip install covetpy
   ```

---

### Problem: Module not found after installation

**Symptoms:**
```python
ModuleNotFoundError: No module named 'covet'
```

**Solutions:**

1. **Verify installation:**
   ```bash
   pip list | grep covet
   pip show covetpy
   ```

2. **Check Python path:**
   ```bash
   python -c "import sys; print('\n'.join(sys.path))"
   ```

3. **Reinstall in correct environment:**
   ```bash
   # Activate virtual environment first
   source venv/bin/activate
   pip install covetpy
   ```

---

## Server Won't Start

### Problem: Address already in use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

1. **Find and kill process using port:**
   ```bash
   # Find process
   sudo lsof -i :8000

   # Kill process
   sudo kill -9 $(sudo lsof -t -i:8000)
   ```

2. **Use different port:**
   ```bash
   uvicorn app.main:app --port 8001
   ```

3. **Check systemd service:**
   ```bash
   sudo systemctl status covet
   sudo systemctl stop covet
   ```

---

### Problem: Permission denied binding to port

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use port > 1024 (non-privileged):**
   ```bash
   uvicorn app.main:app --port 8000
   ```

2. **Or run with sudo (not recommended):**
   ```bash
   sudo uvicorn app.main:app --port 80
   ```

3. **Use capabilities (recommended):**
   ```bash
   sudo setcap CAP_NET_BIND_SERVICE=+eip /usr/bin/python3.11
   ```

---

### Problem: Module import errors on startup

**Symptoms:**
```
ImportError: cannot import name 'CovetPy' from 'covet'
AttributeError: module 'covet' has no attribute 'CovetPy'
```

**Solutions:**

1. **Check Python version (requires 3.9+):**
   ```bash
   python --version
   ```

2. **Verify all dependencies installed:**
   ```bash
   pip install -r requirements-prod.txt
   ```

3. **Check for conflicting packages:**
   ```bash
   pip list | grep -E "covet|fastapi|flask"
   ```

4. **Clear Python cache:**
   ```bash
   find . -type d -name "__pycache__" -exec rm -r {} +
   find . -name "*.pyc" -delete
   ```

---

## Database Connection Problems

### Problem: Cannot connect to PostgreSQL

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
sqlalchemy.exc.OperationalError: connection refused
```

**Solutions:**

1. **Check PostgreSQL is running:**
   ```bash
   sudo systemctl status postgresql
   sudo systemctl start postgresql
   ```

2. **Verify connection settings:**
   ```bash
   psql -U covet_app -d covet_production -h localhost
   ```

3. **Check pg_hba.conf permissions:**
   ```bash
   sudo nano /etc/postgresql/14/main/pg_hba.conf
   ```

   Add:
   ```
   host    covet_production    covet_app    127.0.0.1/32    md5
   ```

4. **Check PostgreSQL is listening:**
   ```bash
   sudo nano /etc/postgresql/14/main/postgresql.conf
   ```

   Verify:
   ```
   listen_addresses = 'localhost'
   port = 5432
   ```

5. **Restart PostgreSQL:**
   ```bash
   sudo systemctl restart postgresql
   ```

---

### Problem: Too many database connections

**Symptoms:**
```
psycopg2.OperationalError: FATAL:  sorry, too many clients already
sqlalchemy.exc.OperationalError: connection pool exhausted
```

**Solutions:**

1. **Check active connections:**
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   SELECT * FROM pg_stat_activity WHERE datname = 'covet_production';
   ```

2. **Kill idle connections:**
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname = 'covet_production'
   AND state = 'idle'
   AND state_change < now() - interval '10 minutes';
   ```

3. **Increase PostgreSQL max_connections:**
   ```bash
   sudo nano /etc/postgresql/14/main/postgresql.conf
   ```

   Change:
   ```
   max_connections = 200
   ```

4. **Adjust application pool size:**
   ```bash
   # In /etc/covet/production.env
   DATABASE_POOL_SIZE=20
   DATABASE_MAX_OVERFLOW=10
   DATABASE_POOL_RECYCLE=3600
   ```

5. **Restart services:**
   ```bash
   sudo systemctl restart postgresql
   sudo systemctl restart covet
   ```

---

### Problem: Database migration fails

**Symptoms:**
```
alembic.util.exc.CommandError: Can't locate revision
sqlalchemy.exc.ProgrammingError: relation does not exist
```

**Solutions:**

1. **Check migration history:**
   ```bash
   covet migrate history
   alembic history
   ```

2. **Check current revision:**
   ```bash
   covet migrate current
   alembic current
   ```

3. **Manually fix revision:**
   ```bash
   # Stamp current version
   covet migrate stamp head

   # Or specific revision
   covet migrate stamp abc123
   ```

4. **Reset and re-run migrations:**
   ```bash
   # CAUTION: This drops all tables!
   covet migrate downgrade base
   covet migrate upgrade head
   ```

5. **Check database permissions:**
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE covet_production TO covet_app;
   GRANT ALL ON SCHEMA public TO covet_app;
   ```

---

## Performance Issues

### Problem: Slow response times

**Symptoms:**
- API responses taking > 1 second
- High latency in logs
- Timeouts from clients

**Diagnostics:**

1. **Check application metrics:**
   ```bash
   curl http://localhost:8000/metrics
   ```

2. **Monitor database queries:**
   ```sql
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   ```

3. **Check slow query log:**
   ```bash
   sudo tail -f /var/log/postgresql/postgresql-14-main.log
   ```

**Solutions:**

1. **Enable database query logging:**
   ```ini
   # postgresql.conf
   log_min_duration_statement = 1000  # Log queries > 1 second
   ```

2. **Add database indexes:**
   ```sql
   CREATE INDEX idx_posts_published ON posts(published, created_at);
   CREATE INDEX idx_users_email ON users(email);
   ```

3. **Enable Redis caching:**
   ```bash
   # /etc/covet/production.env
   CACHE_ENABLED=true
   REDIS_URL=redis://localhost:6379/0
   CACHE_DEFAULT_TTL=300
   ```

4. **Optimize worker count:**
   ```bash
   # /etc/systemd/system/covet.service
   # Workers = (2 x CPU cores) + 1
   ExecStart=/opt/covet/venv/bin/uvicorn app.main:app --workers 9
   ```

5. **Use connection pooling:**
   ```bash
   DATABASE_POOL_SIZE=20
   DATABASE_MAX_OVERFLOW=10
   DATABASE_POOL_PRE_PING=true
   ```

---

### Problem: High CPU usage

**Symptoms:**
- Server CPU at 100%
- Application becomes unresponsive
- Slow response times

**Diagnostics:**

1. **Check process CPU:**
   ```bash
   top -c
   ps aux | grep python | sort -nrk 3
   ```

2. **Profile Python application:**
   ```bash
   # Install py-spy
   pip install py-spy

   # Profile running process
   sudo py-spy top --pid $(pgrep -f uvicorn)

   # Generate flamegraph
   sudo py-spy record -o profile.svg --pid $(pgrep -f uvicorn)
   ```

3. **Check for infinite loops:**
   ```bash
   # View stack trace
   sudo py-spy dump --pid $(pgrep -f uvicorn)
   ```

**Solutions:**

1. **Identify slow endpoints:**
   ```bash
   # Check access logs for slow requests
   awk '$NF > 1' /var/log/nginx/covet_access.log | tail -20
   ```

2. **Optimize database queries:**
   ```python
   # Use select_related for foreign keys
   users = await User.objects.select_related('profile').all()

   # Use prefetch_related for many-to-many
   posts = await Post.objects.prefetch_related('tags').all()
   ```

3. **Limit worker count:**
   ```bash
   # Don't exceed CPU cores * 2
   ExecStart=/opt/covet/venv/bin/uvicorn app.main:app --workers 8
   ```

4. **Add rate limiting:**
   ```bash
   RATE_LIMIT_ENABLED=true
   RATE_LIMIT_PER_MINUTE=60
   ```

---

## Memory Problems

### Problem: Out of memory errors

**Symptoms:**
```
MemoryError: Unable to allocate memory
Killed (Out of memory)
```

**Diagnostics:**

1. **Check memory usage:**
   ```bash
   free -h
   ps aux --sort=-%mem | head -10
   ```

2. **Monitor memory over time:**
   ```bash
   # Install monitoring
   pip install memory-profiler

   # Profile specific function
   @profile
   def my_function():
       pass

   python -m memory_profiler script.py
   ```

**Solutions:**

1. **Increase system memory** (if possible)

2. **Reduce worker count:**
   ```bash
   # /etc/systemd/system/covet.service
   ExecStart=/opt/covet/venv/bin/uvicorn app.main:app --workers 2
   ```

3. **Reduce database pool size:**
   ```bash
   DATABASE_POOL_SIZE=10
   DATABASE_MAX_OVERFLOW=5
   ```

4. **Enable swap memory:**
   ```bash
   # Create 2GB swap
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile

   # Make permanent
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

5. **Add memory limits to systemd:**
   ```ini
   [Service]
   MemoryMax=1G
   MemoryHigh=900M
   ```

---

### Problem: Memory leaks

**Symptoms:**
- Memory usage grows over time
- Application becomes slower
- Eventually crashes with OOM

**Diagnostics:**

1. **Track memory over time:**
   ```bash
   while true; do
     ps aux | grep uvicorn | awk '{print $6}'
     sleep 60
   done >> memory_usage.log
   ```

2. **Use memory profiler:**
   ```python
   from pympler import tracker

   memory_tracker = tracker.SummaryTracker()

   # At end of request
   memory_tracker.print_diff()
   ```

**Solutions:**

1. **Restart workers periodically:**
   ```ini
   # /etc/systemd/system/covet.service
   ExecStart=/opt/covet/venv/bin/gunicorn app.main:app \
       --worker-class uvicorn.workers.UvicornWorker \
       --max-requests 1000 \
       --max-requests-jitter 100
   ```

2. **Close database connections explicitly:**
   ```python
   try:
       # Database operations
       pass
   finally:
       await db.close()
   ```

3. **Clear cache periodically:**
   ```python
   # Clear old cache entries
   await cache.clear_expired()
   ```

---

## WebSocket Issues

### Problem: WebSocket connections fail

**Symptoms:**
```
WebSocket connection failed
Error during WebSocket handshake
```

**Diagnostics:**

1. **Test WebSocket directly:**
   ```bash
   # Install wscat
   npm install -g wscat

   # Test connection
   wscat -c ws://localhost:8000/ws
   ```

2. **Check Nginx configuration:**
   ```bash
   sudo nginx -t
   sudo tail -f /var/log/nginx/error.log
   ```

**Solutions:**

1. **Configure Nginx for WebSocket:**
   ```nginx
   location /ws {
       proxy_pass http://covet_backend;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_set_header Host $host;

       # Increase timeouts
       proxy_read_timeout 3600s;
       proxy_send_timeout 3600s;
   }
   ```

2. **Check firewall allows WebSocket:**
   ```bash
   sudo ufw allow 8000/tcp
   ```

3. **Test without reverse proxy:**
   ```bash
   # Connect directly to application
   wscat -c ws://localhost:8000/ws
   ```

---

### Problem: WebSocket disconnects frequently

**Symptoms:**
- Connections drop after few minutes
- Clients reconnect constantly

**Solutions:**

1. **Implement ping/pong:**
   ```python
   # Server sends ping every 30 seconds
   await websocket.send_json({"type": "ping"})
   ```

2. **Increase timeout:**
   ```nginx
   # Nginx
   proxy_read_timeout 3600s;
   ```

3. **Configure keep-alive:**
   ```python
   # Client-side
   ws.addEventListener('close', () => {
       setTimeout(reconnect, 5000)
   })
   ```

---

## Security Problems

### Problem: CORS errors in browser

**Symptoms:**
```
Access to fetch blocked by CORS policy
No 'Access-Control-Allow-Origin' header
```

**Solutions:**

1. **Configure CORS middleware:**
   ```python
   from covet.middleware import CORSMiddleware

   app.middleware(CORSMiddleware, {
       'allow_origins': ['https://yourdomain.com'],
       'allow_methods': ['GET', 'POST', 'PUT', 'DELETE'],
       'allow_headers': ['*'],
       'allow_credentials': True
   })
   ```

2. **Or configure in Nginx:**
   ```nginx
   location /api/ {
       add_header Access-Control-Allow-Origin 'https://yourdomain.com' always;
       add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS' always;
       add_header Access-Control-Allow-Headers 'Authorization, Content-Type' always;

       if ($request_method = 'OPTIONS') {
           return 204;
       }
   }
   ```

---

### Problem: JWT token validation fails

**Symptoms:**
```
401 Unauthorized
Invalid token
Token has expired
```

**Solutions:**

1. **Check token expiration:**
   ```python
   import jwt
   from datetime import datetime

   try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
       print(f"Expires: {datetime.fromtimestamp(payload['exp'])}")
   except jwt.ExpiredSignatureError:
       print("Token has expired")
   except jwt.InvalidTokenError:
       print("Invalid token")
   ```

2. **Verify secret key matches:**
   ```bash
   # Check environment variable
   echo $JWT_SECRET_KEY

   # Check in code
   python -c "from app.config import JWT_SECRET_KEY; print(JWT_SECRET_KEY)"
   ```

3. **Increase token expiration:**
   ```bash
   # /etc/covet/production.env
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

---

## Deployment Issues

### Problem: Systemd service fails to start

**Symptoms:**
```
Job for covet.service failed
Process exited with code 1
```

**Diagnostics:**

1. **Check service status:**
   ```bash
   sudo systemctl status covet
   sudo journalctl -u covet -n 50 --no-pager
   ```

2. **Test command manually:**
   ```bash
   sudo -u covet /opt/covet/venv/bin/uvicorn app.main:app
   ```

**Solutions:**

1. **Check permissions:**
   ```bash
   sudo chown -R covet:covet /opt/covet
   sudo chmod -R 755 /opt/covet
   ```

2. **Check environment file:**
   ```bash
   sudo cat /etc/covet/production.env
   sudo chmod 600 /etc/covet/production.env
   ```

3. **Check working directory:**
   ```ini
   [Service]
   WorkingDirectory=/opt/covet/app
   ```

4. **Test with verbose logging:**
   ```ini
   [Service]
   ExecStart=/opt/covet/venv/bin/uvicorn app.main:app --log-level debug
   ```

---

### Problem: 502 Bad Gateway from Nginx

**Symptoms:**
- Nginx returns 502 error
- "upstream prematurely closed connection"

**Diagnostics:**

1. **Check Nginx error log:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. **Check backend is running:**
   ```bash
   sudo systemctl status covet
   curl http://localhost:8000/health
   ```

**Solutions:**

1. **Restart backend service:**
   ```bash
   sudo systemctl restart covet
   ```

2. **Check upstream configuration:**
   ```nginx
   upstream covet_backend {
       server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
   }
   ```

3. **Increase timeouts:**
   ```nginx
   proxy_connect_timeout 60s;
   proxy_send_timeout 60s;
   proxy_read_timeout 60s;
   ```

4. **Test Nginx config:**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

## Common Error Messages

### Error: "Event loop is closed"

**Cause:** Trying to use closed asyncio event loop

**Solution:**
```python
# Don't manually close event loop
# Let uvicorn/gunicorn handle it

# If using custom async code:
import asyncio

async def main():
    # Your async code
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Error: "Database is locked" (SQLite)

**Cause:** Multiple processes accessing SQLite

**Solution:**
```python
# Use PostgreSQL or MySQL for production
DATABASE_URL = "postgresql://user:pass@localhost/db"

# Or increase SQLite timeout
DATABASE_TIMEOUT = 30
```

---

### Error: "Too many open files"

**Cause:** File descriptor limit reached

**Solution:**
```bash
# Check current limit
ulimit -n

# Increase limit
sudo nano /etc/security/limits.conf

# Add:
covet soft nofile 65536
covet hard nofile 65536

# For systemd service:
[Service]
LimitNOFILE=65536
```

---

## Debugging Tips

### Enable Debug Mode

```bash
# /etc/covet/production.env
DEBUG=true
LOG_LEVEL=DEBUG
```

**Warning:** Never enable DEBUG in production!

---

### View Detailed Logs

```bash
# Application logs
sudo journalctl -u covet -f -o json-pretty

# With specific time range
sudo journalctl -u covet --since "10 minutes ago"

# With priority filter
sudo journalctl -u covet --priority=err

# Export to file
sudo journalctl -u covet --since today > debug.log
```

---

### Interactive Python Debugging

```python
# Add to code
import pdb; pdb.set_trace()

# Or use better debugger
import ipdb; ipdb.set_trace()

# Remote debugging
import remote_pdb; remote_pdb.set_trace()
```

---

### Request Tracing

```python
# Add middleware to log all requests
class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import time
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        logger.info(f"{request.method} {request.url} - {response.status_code} - {duration:.3f}s")

        return response

app.middleware(RequestLogMiddleware)
```

---

### Database Query Debugging

```python
# Enable SQL logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or in database URL
DATABASE_URL = "postgresql://user:pass@localhost/db?echo=true"
```

---

## Getting Help

If you can't resolve the issue:

1. **Check Documentation:**
   - https://docs.covetpy.com
   - GitHub Wiki

2. **Search GitHub Issues:**
   - https://github.com/covetpy/covetpy/issues

3. **Ask the Community:**
   - GitHub Discussions
   - Stack Overflow (tag: covetpy)
   - Discord Server

4. **File a Bug Report:**
   - Include error messages
   - Provide minimal reproducible example
   - Include environment details (OS, Python version, dependencies)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-11
