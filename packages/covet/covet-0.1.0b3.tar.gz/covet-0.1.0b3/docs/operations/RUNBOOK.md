# CovetPy Operations Runbook

**Version:** 0.2.0-sprint1
**Last Updated:** 2025-10-11
**Audience:** DevOps, SRE, Operations Teams

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Monitoring & Alerting](#monitoring--alerting)
3. [Log Management](#log-management)
4. [Backup & Recovery](#backup--recovery)
5. [Scaling Operations](#scaling-operations)
6. [Security Operations](#security-operations)
7. [Performance Tuning](#performance-tuning)
8. [Common Procedures](#common-procedures)
9. [Emergency Procedures](#emergency-procedures)
10. [Maintenance Windows](#maintenance-windows)

---

## Daily Operations

### Morning Health Check

**Frequency:** Daily at 9:00 AM
**Duration:** 10-15 minutes
**Owner:** Operations Team

```bash
#!/bin/bash
# daily-health-check.sh

echo "=== CovetPy Daily Health Check ==="
echo "Date: $(date)"
echo ""

# 1. Service Status
echo "1. Service Status"
systemctl status covet --no-pager | grep "Active:"
echo ""

# 2. System Resources
echo "2. System Resources"
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
echo "Memory Usage:"
free -h | awk '/^Mem:/ {print $3 "/" $2}'
echo "Disk Usage:"
df -h | grep -E '^/dev/' | awk '{print $6 ": " $5}'
echo ""

# 3. Database Status
echo "3. Database Status"
systemctl status postgresql --no-pager | grep "Active:"
psql -U covet_app -d covet_production -c "SELECT pg_size_pretty(pg_database_size('covet_production')) AS size;" 2>/dev/null
echo ""

# 4. Redis Status
echo "4. Redis Status"
systemctl status redis --no-pager | grep "Active:"
redis-cli ping 2>/dev/null
echo ""

# 5. Recent Errors
echo "5. Recent Errors (Last Hour)"
journalctl -u covet --since "1 hour ago" | grep -i error | tail -10
echo ""

# 6. API Health Check
echo "6. API Health Check"
curl -s http://localhost:8000/health | jq .
echo ""

# 7. Active Connections
echo "7. Active Connections"
ss -s | grep -E "TCP:|ESTAB"
echo ""

echo "=== Health Check Complete ==="
```

### Daily Metrics Review

Check these metrics daily:

1. **Request Rate**: Should be within normal range
2. **Response Time**: P95 < 200ms, P99 < 500ms
3. **Error Rate**: < 1% of all requests
4. **Database Connections**: < 80% of pool size
5. **Redis Memory**: < 80% of max memory
6. **Disk Space**: > 20% free
7. **CPU Usage**: < 70% average
8. **Memory Usage**: < 80% total

---

## Monitoring & Alerting

### Prometheus Setup

**Installation:**

```bash
# Install Prometheus
sudo apt-get install -y prometheus

# Configure Prometheus
sudo nano /etc/prometheus/prometheus.yml
```

**Configuration:**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

rule_files:
  - "alerts.yml"

scrape_configs:
  # CovetPy Application
  - job_name: 'covet'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          environment: 'production'
          service: 'covet-app'
    metrics_path: '/metrics'

  # Node Exporter (System Metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  # Redis Exporter
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

**Alert Rules** (`/etc/prometheus/alerts.yml`):

```yaml
groups:
  - name: covet_alerts
    interval: 30s
    rules:
      # High Error Rate
      - alert: HighErrorRate
        expr: rate(covet_http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      # High Response Time
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(covet_http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "P95 response time is {{ $value }}s"

      # Service Down
      - alert: ServiceDown
        expr: up{job="covet"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "CovetPy service is down"
          description: "Service has been down for more than 1 minute"

      # High Memory Usage
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      # High Disk Usage
      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes{fstype!="tmpfs"} - node_filesystem_avail_bytes{fstype!="tmpfs"}) / node_filesystem_size_bytes{fstype!="tmpfs"} > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage"
          description: "Disk usage is {{ $value | humanizePercentage }}"

      # Database Connection Pool Exhausted
      - alert: DatabasePoolExhausted
        expr: covet_db_pool_connections_in_use / covet_db_pool_max_connections > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value | humanizePercentage }} of connections in use"
```

### Grafana Dashboards

**Installation:**

```bash
# Install Grafana
sudo apt-get install -y grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Access: http://localhost:3000
# Default credentials: admin/admin
```

**Dashboard Panels:**

1. **Request Rate** (Graph)
   - Query: `rate(covet_http_requests_total[5m])`

2. **Response Time** (Graph)
   - Query: `histogram_quantile(0.95, rate(covet_http_request_duration_seconds_bucket[5m]))`

3. **Error Rate** (Graph)
   - Query: `rate(covet_http_requests_total{status=~"5.."}[5m])`

4. **Active Connections** (Gauge)
   - Query: `covet_active_connections`

5. **Database Pool** (Gauge)
   - Query: `covet_db_pool_connections_in_use`

6. **CPU Usage** (Graph)
   - Query: `100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`

7. **Memory Usage** (Graph)
   - Query: `(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100`

### Alerting Channels

Configure Alertmanager (`/etc/prometheus/alertmanager.yml`):

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical'
    - match:
        severity: warning
      receiver: 'warning'

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@yourdomain.com'
        from: 'alerts@yourdomain.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@yourdomain.com'
        auth_password: 'your-app-password'

  - name: 'critical'
    email_configs:
      - to: 'oncall@yourdomain.com'
        from: 'alerts@yourdomain.com'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#critical-alerts'
        title: 'CRITICAL: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'warning'
    email_configs:
      - to: 'ops@yourdomain.com'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#ops-alerts'
```

---

## Log Management

### Log Locations

```bash
# Application Logs
/var/log/covet/app.log          # Application events
/var/log/covet/access.log       # HTTP access logs
/var/log/covet/error.log        # Error logs

# System Logs
journalctl -u covet             # Systemd journal

# Nginx Logs
/var/log/nginx/covet_access.log
/var/log/nginx/covet_error.log

# Database Logs
/var/log/postgresql/postgresql-14-main.log
```

### Log Rotation

Configure logrotate (`/etc/logrotate.d/covet`):

```bash
/var/log/covet/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 covet covet
    sharedscripts
    postrotate
        systemctl reload covet > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/covet*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### Centralized Logging with ELK Stack

**1. Install Elasticsearch:**

```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update
sudo apt-get install elasticsearch
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
```

**2. Install Logstash:**

```bash
sudo apt-get install logstash
```

Configure Logstash (`/etc/logstash/conf.d/covet.conf`):

```ruby
input {
  file {
    path => "/var/log/covet/*.log"
    type => "covet"
    codec => json
  }

  file {
    path => "/var/log/nginx/covet_access.log"
    type => "nginx-access"
  }
}

filter {
  if [type] == "covet" {
    json {
      source => "message"
    }
    date {
      match => ["timestamp", "ISO8601"]
    }
  }

  if [type] == "nginx-access" {
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}" }
    }
    date {
      match => ["timestamp", "dd/MMM/yyyy:HH:mm:ss Z"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "covet-%{+YYYY.MM.dd}"
  }
}
```

**3. Install Kibana:**

```bash
sudo apt-get install kibana
sudo systemctl enable kibana
sudo systemctl start kibana

# Access: http://localhost:5601
```

### Useful Log Commands

```bash
# View real-time logs
journalctl -u covet -f

# View logs from last hour
journalctl -u covet --since "1 hour ago"

# View error logs only
journalctl -u covet --priority=err

# Search logs for specific pattern
journalctl -u covet | grep -i "database"

# Export logs to file
journalctl -u covet --since today > /tmp/covet-logs-$(date +%Y%m%d).log

# View logs by time range
journalctl -u covet --since "2025-10-11 09:00:00" --until "2025-10-11 10:00:00"

# View last 100 lines
journalctl -u covet -n 100

# Follow Nginx access logs
tail -f /var/log/nginx/covet_access.log

# Count requests by status code
awk '{print $9}' /var/log/nginx/covet_access.log | sort | uniq -c | sort -rn
```

---

## Backup & Recovery

### Database Backup

**Daily Automated Backup Script** (`/opt/covet/scripts/backup-db.sh`):

```bash
#!/bin/bash
# Database backup script

# Configuration
BACKUP_DIR="/opt/covet/backups"
DB_NAME="covet_production"
DB_USER="covet_app"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/covet_db_$DATE.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
echo "Starting database backup..."
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Check if backup succeeded
if [ $? -eq 0 ]; then
    echo "Backup completed: $BACKUP_FILE"

    # Calculate size
    SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "Backup size: $SIZE"

    # Delete old backups
    find $BACKUP_DIR -name "covet_db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "Old backups cleaned up (retention: $RETENTION_DAYS days)"
else
    echo "Backup failed!"
    exit 1
fi
```

**Schedule with Cron:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/covet/scripts/backup-db.sh >> /var/log/covet/backup.log 2>&1
```

### Database Restoration

```bash
# Stop application
sudo systemctl stop covet

# Restore from backup
gunzip < /opt/covet/backups/covet_db_20251011_020000.sql.gz | psql -U covet_app -d covet_production

# Restart application
sudo systemctl start covet

# Verify restoration
psql -U covet_app -d covet_production -c "SELECT COUNT(*) FROM users;"
```

### Application Data Backup

```bash
#!/bin/bash
# Backup application data

BACKUP_DIR="/opt/covet/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/covet/uploads/

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/covet/

echo "Application data backup completed"
```

### Point-in-Time Recovery (PITR)

Enable PostgreSQL WAL archiving (`/etc/postgresql/14/main/postgresql.conf`):

```ini
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /opt/covet/backups/wal/%f && cp %p /opt/covet/backups/wal/%f'
archive_timeout = 300
max_wal_senders = 3
```

**Create PITR backup:**

```bash
# Create base backup
pg_basebackup -U covet_app -D /opt/covet/backups/pitr/$(date +%Y%m%d) -Fp -Xs -P

# WAL files are automatically archived
```

**Restore to point in time:**

```bash
# Stop PostgreSQL
sudo systemctl stop postgresql

# Restore base backup
rm -rf /var/lib/postgresql/14/main/*
cp -r /opt/covet/backups/pitr/20251011/* /var/lib/postgresql/14/main/

# Create recovery.conf
cat > /var/lib/postgresql/14/main/recovery.conf <<EOF
restore_command = 'cp /opt/covet/backups/wal/%f %p'
recovery_target_time = '2025-10-11 14:30:00'
EOF

# Start PostgreSQL (recovery will begin automatically)
sudo systemctl start postgresql
```

---

## Scaling Operations

### Vertical Scaling (Single Server)

**Increase Resources:**

```bash
# Check current limits
ulimit -n  # File descriptors
ulimit -u  # Max processes

# Increase limits (/etc/security/limits.conf)
covet soft nofile 65536
covet hard nofile 65536
covet soft nproc 32768
covet hard nproc 32768

# Increase worker count
sudo nano /etc/systemd/system/covet.service
# Change: --workers 8 (from 4)

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart covet
```

**Database Scaling:**

```bash
# Increase PostgreSQL connections
sudo nano /etc/postgresql/14/main/postgresql.conf

# Adjust settings
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 16MB

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Horizontal Scaling (Multiple Servers)

**1. Load Balancer Configuration:**

Update Nginx upstream (`/etc/nginx/sites-available/covet`):

```nginx
upstream covet_backend {
    least_conn;  # Or: ip_hash, round_robin

    server 10.0.1.10:8000 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 max_fails=3 fail_timeout=30s;

    keepalive 32;
}
```

**2. Session Persistence:**

Use Redis for session storage to enable sticky sessions:

```python
# Configuration
SESSION_BACKEND = "redis"
REDIS_URL = "redis://redis-cluster:6379/0"
```

**3. Database Read Replicas:**

```python
# Configure read replicas
DATABASE_WRITE_URL = "postgresql://master:5432/covet"
DATABASE_READ_URLS = [
    "postgresql://replica1:5432/covet",
    "postgresql://replica2:5432/covet",
]
```

### Auto-Scaling (Cloud)

**AWS Auto Scaling Group:**

```json
{
  "AutoScalingGroupName": "covet-asg",
  "MinSize": 2,
  "MaxSize": 10,
  "DesiredCapacity": 3,
  "HealthCheckType": "ELB",
  "HealthCheckGracePeriod": 300,
  "TargetGroupARNs": ["arn:aws:elasticloadbalancing:..."],
  "Tags": [
    {
      "Key": "Name",
      "Value": "covet-app-server"
    }
  ]
}
```

**Scaling Policies:**

```json
{
  "PolicyName": "scale-up-on-cpu",
  "AdjustmentType": "ChangeInCapacity",
  "ScalingAdjustment": 2,
  "Cooldown": 300,
  "MetricAggregationType": "Average",
  "TargetTrackingConfiguration": {
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 70.0
  }
}
```

---

## Security Operations

### SSL Certificate Renewal

```bash
# Check certificate expiry
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run

# Renew certificates (auto-scheduled)
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal
```

### Security Audits

**Daily Security Checks:**

```bash
#!/bin/bash
# security-audit.sh

echo "=== Security Audit ==="
echo "Date: $(date)"
echo ""

# 1. Check for failed login attempts
echo "1. Failed Login Attempts:"
journalctl -u covet --since today | grep -i "authentication failed" | wc -l

# 2. Check open ports
echo "2. Open Ports:"
ss -tunlp

# 3. Check firewall status
echo "3. Firewall Status:"
sudo ufw status

# 4. Check for unauthorized sudo usage
echo "4. Sudo Usage Today:"
journalctl _COMM=sudo --since today | wc -l

# 5. Check file permissions
echo "5. Critical File Permissions:"
ls -l /etc/covet/production.env
ls -l /opt/covet/backups/

# 6. Check for security updates
echo "6. Security Updates Available:"
apt list --upgradable 2>/dev/null | grep -i security | wc -l

echo ""
echo "=== Audit Complete ==="
```

### Vulnerability Scanning

```bash
# Install and run Lynis
sudo apt-get install lynis
sudo lynis audit system

# Scan for vulnerable packages
sudo apt-get install -y debsecan
debsecan --suite $(lsb_release -cs) --format detail

# Check Python dependencies for vulnerabilities
pip install safety
safety check --file requirements-prod.txt
```

---

## Performance Tuning

### Application Tuning

**Worker Optimization:**

```bash
# Calculate optimal workers: (2 x CPUs) + 1
WORKERS=$((2 * $(nproc) + 1))
echo "Recommended workers: $WORKERS"

# Update systemd service
sudo nano /etc/systemd/system/covet.service
# Update: --workers $WORKERS

sudo systemctl daemon-reload
sudo systemctl restart covet
```

**Connection Pool Tuning:**

```bash
# In /etc/covet/production.env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

### Database Tuning

**PostgreSQL Optimization:**

```ini
# /etc/postgresql/14/main/postgresql.conf

# Memory Configuration
shared_buffers = 4GB          # 25% of RAM
effective_cache_size = 12GB   # 75% of RAM
maintenance_work_mem = 1GB
work_mem = 16MB

# Query Planning
random_page_cost = 1.1        # For SSD
effective_io_concurrency = 200

# WAL Configuration
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
checkpoint_completion_target = 0.9

# Connection Configuration
max_connections = 200
```

**Index Optimization:**

```sql
-- Find missing indexes
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    most_common_vals
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY n_distinct DESC;

-- Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Redis Tuning

```bash
# /etc/redis/redis.conf

# Memory Management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 60
```

---

## Common Procedures

### Deploying Updates

```bash
#!/bin/bash
# deploy-update.sh

set -e

echo "Starting deployment..."

# 1. Backup current version
echo "Creating backup..."
sudo -u covet tar -czf /opt/covet/backups/app_$(date +%Y%m%d_%H%M%S).tar.gz /opt/covet/app/

# 2. Pull latest code
echo "Pulling latest code..."
cd /opt/covet/app
sudo -u covet git pull origin main

# 3. Install dependencies
echo "Installing dependencies..."
sudo -u covet /opt/covet/venv/bin/pip install -r requirements-prod.txt

# 4. Run migrations
echo "Running migrations..."
sudo -u covet /opt/covet/venv/bin/covet migrate

# 5. Collect static files
echo "Collecting static files..."
sudo -u covet /opt/covet/venv/bin/python manage.py collectstatic --noinput

# 6. Reload application
echo "Reloading application..."
sudo systemctl reload covet

# 7. Health check
echo "Performing health check..."
sleep 5
curl -f http://localhost:8000/health || {
    echo "Health check failed! Rolling back..."
    sudo systemctl restart covet
    exit 1
}

echo "Deployment completed successfully!"
```

### Rolling Back

```bash
#!/bin/bash
# rollback.sh

echo "Rolling back to previous version..."

# 1. Stop application
sudo systemctl stop covet

# 2. Restore previous version
LATEST_BACKUP=$(ls -t /opt/covet/backups/app_*.tar.gz | head -1)
echo "Restoring from: $LATEST_BACKUP"
sudo -u covet tar -xzf $LATEST_BACKUP -C /

# 3. Rollback database migrations (if needed)
# sudo -u covet /opt/covet/venv/bin/covet migrate rollback

# 4. Restart application
sudo systemctl start covet

# 5. Health check
sleep 5
curl -f http://localhost:8000/health && echo "Rollback successful!" || echo "Rollback failed!"
```

### Clearing Cache

```bash
# Clear Redis cache
redis-cli FLUSHDB

# Or with authentication
redis-cli -a your-password FLUSHDB

# Clear specific keys
redis-cli KEYS "covet:*" | xargs redis-cli DEL

# Clear application cache
curl -X POST http://localhost:8000/admin/cache/clear \
     -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Emergency Procedures

### Service is Down

```bash
# 1. Check service status
sudo systemctl status covet

# 2. View recent logs
sudo journalctl -u covet -n 100 --no-pager

# 3. Try to restart
sudo systemctl restart covet

# 4. If restart fails, check port conflict
sudo lsof -i :8000

# 5. Kill conflicting process if necessary
sudo kill -9 $(sudo lsof -t -i:8000)

# 6. Start service
sudo systemctl start covet

# 7. Escalate if not resolved
```

### High CPU Usage

```bash
# 1. Identify process
top -c

# 2. Check application threads
ps -eLf | grep covet

# 3. Generate stack trace (Python)
sudo py-spy top --pid $(pgrep -f "uvicorn")

# 4. Check for long-running queries
psql -U covet_app -d covet_production -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"

# 5. Terminate long-running queries if necessary
psql -U covet_app -d covet_production -c "SELECT pg_terminate_backend(pid);"
```

### Database Connection Issues

```bash
# 1. Check PostgreSQL status
sudo systemctl status postgresql

# 2. Check connection count
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 3. Kill idle connections
psql -U postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'covet_production'
AND state = 'idle'
AND state_change < now() - interval '10 minutes';"

# 4. Restart PostgreSQL if necessary
sudo systemctl restart postgresql
```

### Out of Disk Space

```bash
# 1. Check disk usage
df -h

# 2. Find large files
sudo du -ah / | sort -rh | head -20

# 3. Clear old logs
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.gz" -mtime +30 -delete

# 4. Clear old backups
sudo find /opt/covet/backups -name "*.gz" -mtime +30 -delete

# 5. Clear package cache
sudo apt-get clean

# 6. Restart services
sudo systemctl restart covet
```

---

## Maintenance Windows

### Scheduled Maintenance

**Monthly Maintenance Checklist:**

1. **System Updates** (2nd Saturday, 2:00 AM)
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   sudo apt-get autoremove -y
   sudo reboot
   ```

2. **Database Maintenance** (Every Sunday, 3:00 AM)
   ```sql
   -- Vacuum and analyze
   VACUUM ANALYZE;

   -- Reindex
   REINDEX DATABASE covet_production;

   -- Update statistics
   ANALYZE;
   ```

3. **Certificate Renewal** (Automated, 1st of month)
   ```bash
   sudo certbot renew
   ```

4. **Security Patches** (As needed, emergency window)
   ```bash
   sudo apt-get update
   sudo apt-get install --only-upgrade <package>
   ```

### Maintenance Window Communication

**Email Template:**

```
Subject: Scheduled Maintenance - CovetPy Service

Dear Users,

We will be performing scheduled maintenance on our CovetPy service:

Date: Saturday, October 14, 2025
Time: 2:00 AM - 4:00 AM UTC
Duration: Approximately 2 hours
Impact: Service will be unavailable during this time

Maintenance activities:
- System security updates
- Database optimization
- Performance improvements

We apologize for any inconvenience this may cause.

Best regards,
Operations Team
```

---

## Support Contacts

**On-Call Rotation:**
- Week 1: ops-team-1@yourdomain.com
- Week 2: ops-team-2@yourdomain.com

**Escalation Path:**
1. Level 1: Operations Team (ops@yourdomain.com)
2. Level 2: Senior SRE (sre-lead@yourdomain.com)
3. Level 3: Engineering Manager (eng-manager@yourdomain.com)

**Emergency Hotline:** +1-XXX-XXX-XXXX

---

**Document Version:** 1.0
**Last Reviewed:** 2025-10-11
**Next Review:** 2025-11-11
