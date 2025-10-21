# CovetPy Version Upgrade Guide

**Version:** 0.2.0-sprint1
**Last Updated:** 2025-10-11

This guide covers upgrading between different versions of CovetPy, including breaking changes, deprecated features, and migration strategies.

## Table of Contents

1. [Upgrade Process](#upgrade-process)
2. [Version Compatibility](#version-compatibility)
3. [Breaking Changes by Version](#breaking-changes-by-version)
4. [Deprecation Timeline](#deprecation-timeline)
5. [Migration Strategies](#migration-strategies)
6. [Testing After Upgrade](#testing-after-upgrade)
7. [Rollback Procedures](#rollback-procedures)

---

## Upgrade Process

### General Upgrade Steps

1. **Review Release Notes**
   ```bash
   # View changelog
   curl https://github.com/covetpy/covetpy/releases/latest
   ```

2. **Backup Everything**
   ```bash
   # Backup database
   pg_dump -U covet_app covet_production > backup_$(date +%Y%m%d).sql

   # Backup application
   tar -czf /backups/app_$(date +%Y%m%d).tar.gz /opt/covet/
   ```

3. **Test in Staging**
   ```bash
   # Never upgrade production first!
   # Always test in staging environment
   ```

4. **Upgrade CovetPy**
   ```bash
   # Activate virtual environment
   source /opt/covet/venv/bin/activate

   # Upgrade package
   pip install --upgrade covetpy

   # Or specific version
   pip install covetpy==0.2.0
   ```

5. **Run Database Migrations**
   ```bash
   # Run migrations
   covet migrate

   # Or check what will run
   covet migrate --dry-run
   ```

6. **Update Configuration**
   ```bash
   # Review new configuration options
   cat /opt/covet/venv/lib/python3.11/site-packages/covet/config.py.example

   # Update your config
   nano /etc/covet/production.env
   ```

7. **Restart Services**
   ```bash
   sudo systemctl restart covet
   sudo systemctl status covet
   ```

8. **Verify Deployment**
   ```bash
   # Health check
   curl http://localhost:8000/health

   # Check logs
   sudo journalctl -u covet -n 50 --no-pager
   ```

---

## Version Compatibility

### Python Version Requirements

| CovetPy Version | Minimum Python | Recommended Python | Maximum Python |
|-----------------|----------------|-------------------|----------------|
| 0.1.x | 3.9 | 3.11 | 3.12 |
| 0.2.x | 3.9 | 3.11 | 3.12 |
| 0.3.x (planned) | 3.10 | 3.12 | 3.13 |

### Database Compatibility

| CovetPy Version | PostgreSQL | MySQL | SQLite |
|-----------------|------------|-------|--------|
| 0.1.x | 12+ | 8.0+ | 3.35+ |
| 0.2.x | 14+ | 8.0+ | 3.35+ |

### Dependency Compatibility

Check `requirements-prod.txt` for specific versions.

---

## Breaking Changes by Version

### Upgrading to 0.2.0 from 0.1.x

**Release Date:** 2025-10-11
**Risk Level:** Medium

#### Breaking Changes

1. **ASGI Application Initialization**
   ```python
   # Old (0.1.x)
   from covet import Covet
   app = Covet()

   # New (0.2.x)
   from covet import CovetPy
   app = CovetPy()
   ```

2. **Middleware Registration**
   ```python
   # Old (0.1.x)
   app.add_middleware(CORSMiddleware, allow_origins=['*'])

   # New (0.2.x)
   app.middleware(CORSMiddleware, allow_origins=['*'])
   ```

3. **Request Object Changes**
   ```python
   # Old (0.1.x)
   data = request.json()  # Sync method

   # New (0.2.x)
   data = await request.json()  # Async method
   ```

4. **Database Configuration**
   ```python
   # Old (0.1.x)
   DATABASE_URI = "..."

   # New (0.2.x)
   DATABASE_URL = "..."  # Renamed for consistency
   ```

#### Deprecated Features

- `Covet` class (use `CovetPy`)
- `app.add_middleware()` (use `app.middleware()`)
- Synchronous request methods (use async)

#### New Features

- ASGI 3.0 full compliance
- Improved WebSocket support
- Enhanced security features
- Better database connection pooling

#### Migration Steps

1. **Update imports:**
   ```bash
   # Find and replace in all files
   find ./app -name "*.py" -exec sed -i 's/from covet import Covet/from covet import CovetPy/g' {} +
   find ./app -name "*.py" -exec sed -i 's/app = Covet()/app = CovetPy()/g' {} +
   ```

2. **Update middleware:**
   ```bash
   find ./app -name "*.py" -exec sed -i 's/app.add_middleware(/app.middleware(/g' {} +
   ```

3. **Update request handlers:**
   ```python
   # Add async/await to all request.json() calls
   # Before:
   data = request.json()

   # After:
   data = await request.json()
   ```

4. **Update configuration:**
   ```bash
   # In /etc/covet/production.env
   # Rename DATABASE_URI to DATABASE_URL
   sed -i 's/DATABASE_URI=/DATABASE_URL=/g' /etc/covet/production.env
   ```

---

### Upgrading to 0.1.0 from Pre-release

**Release Date:** 2025-01-15
**Risk Level:** High

#### Breaking Changes

1. **ORM Model Definition**
   ```python
   # Old (pre-release)
   class User(BaseModel):
       name = StringField()

   # New (0.1.0)
   class User(Model):
       name = CharField(max_length=100)
   ```

2. **Query API**
   ```python
   # Old (pre-release)
   users = User.all()

   # New (0.1.0)
   users = await User.objects.all()
   ```

---

## Deprecation Timeline

### Currently Deprecated (Will be removed in 0.3.0)

| Feature | Deprecated In | Remove In | Alternative |
|---------|--------------|-----------|-------------|
| `Covet` class | 0.2.0 | 0.3.0 | Use `CovetPy` |
| `add_middleware()` | 0.2.0 | 0.3.0 | Use `middleware()` |
| Sync request methods | 0.2.0 | 0.3.0 | Use async methods |
| `DATABASE_URI` | 0.2.0 | 0.3.0 | Use `DATABASE_URL` |

### Planned Deprecations (0.3.0)

| Feature | Deprecate In | Remove In | Alternative |
|---------|-------------|-----------|-------------|
| Legacy routing | 0.3.0 | 0.4.0 | Use advanced router |
| Basic auth | 0.3.0 | 0.4.0 | Use JWT auth |

---

## Migration Strategies

### Blue-Green Deployment

For zero-downtime upgrades:

```bash
#!/bin/bash
# blue-green-upgrade.sh

# 1. Deploy new version to "green" environment
docker-compose -f docker-compose.green.yml up -d

# 2. Health check green environment
curl http://green.internal:8000/health

# 3. Switch traffic to green
kubectl patch service covet -p '{"spec":{"selector":{"version":"green"}}}'

# 4. Monitor for issues
sleep 60

# 5. If successful, shutdown blue
docker-compose -f docker-compose.blue.yml down

# 6. If issues, rollback
# kubectl patch service covet -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Rolling Update

For Kubernetes deployments:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covet-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero downtime
  template:
    spec:
      containers:
      - name: covet
        image: covetpy:0.2.0  # New version
```

```bash
# Apply rolling update
kubectl apply -f deployment.yaml

# Monitor rollout
kubectl rollout status deployment/covet-app

# Rollback if issues
kubectl rollout undo deployment/covet-app
```

### Canary Deployment

Gradual rollout:

```yaml
# Nginx traffic split
upstream covet_v1 {
    server v1.internal:8000;
}

upstream covet_v2 {
    server v2.internal:8000;
}

split_clients $remote_addr $backend {
    10% covet_v2;  # 10% to new version
    * covet_v1;    # 90% to old version
}

server {
    location / {
        proxy_pass http://$backend;
    }
}
```

---

## Testing After Upgrade

### Automated Tests

```bash
# Run full test suite
pytest tests/ -v

# Run specific test categories
pytest tests/integration/ -v
pytest tests/security/ -v
pytest tests/performance/ -v
```

### Manual Testing Checklist

#### 1. Core Functionality

- [ ] Application starts successfully
- [ ] Health endpoint responds: `/health`
- [ ] API endpoints return expected data
- [ ] WebSocket connections work
- [ ] Static files serve correctly

#### 2. Authentication

- [ ] User registration works
- [ ] Login succeeds with valid credentials
- [ ] Login fails with invalid credentials
- [ ] JWT tokens validate correctly
- [ ] Token refresh works
- [ ] Logout invalidates tokens

#### 3. Database Operations

- [ ] Read operations work
- [ ] Create operations work
- [ ] Update operations work
- [ ] Delete operations work
- [ ] Transactions commit/rollback correctly
- [ ] Connection pool operates normally

#### 4. Performance

- [ ] Response times within acceptable range
- [ ] No memory leaks (monitor over time)
- [ ] CPU usage normal
- [ ] Database connection count stable

#### 5. Security

- [ ] CORS headers present
- [ ] Security headers present
- [ ] Rate limiting active
- [ ] Input validation working
- [ ] SQL injection prevention active
- [ ] XSS prevention working

### Load Testing

```bash
# Install tools
sudo apt-get install apache2-utils

# Test with increasing load
ab -n 1000 -c 10 http://localhost:8000/api/health
ab -n 5000 -c 50 http://localhost:8000/api/users
ab -n 10000 -c 100 http://localhost:8000/api/posts

# Or use wrk
wrk -t4 -c100 -d30s http://localhost:8000/api/health
```

### Smoke Test Script

```bash
#!/bin/bash
# smoke-test.sh - Quick post-upgrade validation

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "Running smoke tests..."

# 1. Health check
echo -n "Health check... "
curl -f -s "${BASE_URL}/health" > /dev/null && echo "✓" || (echo "✗" && exit 1)

# 2. API root
echo -n "API root... "
curl -f -s "${BASE_URL}/api" > /dev/null && echo "✓" || (echo "✗" && exit 1)

# 3. Authentication
echo -n "Authentication... "
TOKEN=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"password"}' \
  | jq -r '.access_token')
[ -n "$TOKEN" ] && echo "✓" || (echo "✗" && exit 1)

# 4. Authenticated request
echo -n "Authenticated request... "
curl -f -s -H "Authorization: Bearer $TOKEN" \
  "${BASE_URL}/api/users/me" > /dev/null && echo "✓" || (echo "✗" && exit 1)

# 5. WebSocket
echo -n "WebSocket... "
wscat -c "${BASE_URL}/ws" -x '{"type":"ping"}' 2>&1 | grep -q "pong" && echo "✓" || echo "⚠ (optional)"

echo ""
echo "All smoke tests passed! ✓"
```

---

## Rollback Procedures

### Quick Rollback

If issues occur immediately after upgrade:

```bash
#!/bin/bash
# quick-rollback.sh

# 1. Stop new version
sudo systemctl stop covet

# 2. Restore previous version
pip install covetpy==0.1.9  # Previous version

# 3. Rollback database migrations
covet migrate rollback --to previous

# 4. Restart service
sudo systemctl start covet

# 5. Verify
curl http://localhost:8000/health
```

### Full Rollback with Database

```bash
#!/bin/bash
# full-rollback.sh

# 1. Stop application
sudo systemctl stop covet

# 2. Restore database backup
psql -U postgres -c "DROP DATABASE covet_production;"
psql -U postgres -c "CREATE DATABASE covet_production OWNER covet_app;"
psql -U covet_app covet_production < backup_20251011.sql

# 3. Restore application backup
rm -rf /opt/covet/app
tar -xzf /backups/app_20251011.tar.gz -C /opt/covet/

# 4. Restore virtual environment
rm -rf /opt/covet/venv
tar -xzf /backups/venv_20251011.tar.gz -C /opt/covet/

# 5. Restart service
sudo systemctl start covet

# 6. Verify
sleep 5
curl http://localhost:8000/health
```

### Docker Rollback

```bash
# Rollback to previous image
docker-compose down
docker-compose up -d covetpy:0.1.9

# Or with kubectl
kubectl rollout undo deployment/covet-app
kubectl rollout status deployment/covet-app
```

---

## Post-Upgrade Monitoring

Monitor these metrics closely for 24-48 hours after upgrade:

### Application Metrics

```bash
# Response times
curl http://localhost:8000/metrics | grep http_request_duration

# Error rates
curl http://localhost:8000/metrics | grep http_requests_total

# Active connections
curl http://localhost:8000/metrics | grep active_connections
```

### System Metrics

```bash
# CPU usage
top -bn1 | grep "Cpu(s)"

# Memory usage
free -h

# Disk I/O
iostat -x 1

# Network
iftop
```

### Database Metrics

```sql
-- Connection count
SELECT count(*) FROM pg_stat_activity WHERE datname = 'covet_production';

-- Slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Locks
SELECT * FROM pg_locks WHERE NOT granted;
```

---

## Troubleshooting Common Upgrade Issues

### Issue: Import errors after upgrade

**Symptom:**
```
ImportError: cannot import name 'Covet' from 'covet'
```

**Solution:**
```bash
# Clear Python cache
find /opt/covet -name "*.pyc" -delete
find /opt/covet -type d -name "__pycache__" -exec rm -r {} +

# Reinstall
pip install --force-reinstall --no-cache-dir covetpy
```

### Issue: Database migration fails

**Symptom:**
```
Error: Migration 0042_add_column conflicts with existing schema
```

**Solution:**
```bash
# Check current migration state
covet migrate status

# Show pending migrations
covet migrate show-pending

# Manual rollback if needed
covet migrate rollback --to 0041

# Re-run migrations
covet migrate
```

### Issue: Configuration not loading

**Symptom:**
```
KeyError: 'DATABASE_URL'
```

**Solution:**
```bash
# Check environment file
sudo cat /etc/covet/production.env | grep DATABASE

# Test configuration loading
python -c "from covet.config import load_config; print(load_config())"

# Restart with explicit config
sudo systemctl edit covet
# Add: EnvironmentFile=/etc/covet/production.env
```

---

## Support

If you encounter issues during upgrade:

1. **Check Documentation:**
   - Release notes
   - Changelog
   - Migration guide

2. **Search GitHub Issues:**
   - https://github.com/covetpy/covetpy/issues

3. **Ask for Help:**
   - GitHub Discussions
   - Discord server
   - Stack Overflow (tag: covetpy)

4. **File Bug Report:**
   - Include version numbers
   - Provide error messages
   - Share relevant configuration (redact secrets!)

---

## Best Practices

1. **Always test in staging first**
2. **Create backups before upgrading**
3. **Read release notes thoroughly**
4. **Monitor closely after upgrade**
5. **Have rollback plan ready**
6. **Upgrade during low-traffic period**
7. **Test rollback procedure before upgrading**

---

**Document Version:** 1.0
**Last Updated:** 2025-10-11
