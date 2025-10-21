# Team 33: Production Deployment Guide
## CovetPy/NeutrinoPy Framework - Complete Production Deployment Strategy

**Guide Version:** 1.0.0
**Last Updated:** 2025-10-11
**Framework Version:** 0.9.0-beta (Pre-Production)
**Target:** Production-Ready Deployment

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Architecture Overview](#architecture-overview)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Database Configuration](#database-configuration)
5. [Application Deployment](#application-deployment)
6. [Security Hardening](#security-hardening)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring & Observability](#monitoring--observability)
9. [Zero-Downtime Deployment](#zero-downtime-deployment)
10. [Rollback Procedures](#rollback-procedures)
11. [Disaster Recovery](#disaster-recovery)
12. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Critical Blockers (Must Fix First)

Before deploying to production, the following issues from the Integration Test Report MUST be resolved:

- [ ] **P0-1:** Fix module export issues (16 hours)
  ```bash
  # Affected modules:
  - src/covet/database/orm/relationships/__init__.py
  - src/covet/database/sharding/__init__.py
  - src/covet/database/replication/__init__.py
  - src/covet/api/rest/__init__.py
  - src/covet/api/graphql/schema.py
  - src/covet/api/versioning/__init__.py
  - src/covet/testing/__init__.py
  ```

- [ ] **P0-2:** Standardize database component APIs (24 hours)
  ```python
  # All database components should accept:
  def __init__(self, database_url: str, **kwargs):
      pass
  ```

- [ ] **P0-3:** Complete migration system (80 hours)
  - Implement `src/covet/database/migrations/manager.py`
  - Add CLI commands
  - Create migration templates

- [ ] **Security Audit:** Run final security scan
  ```bash
  pip install bandit safety
  bandit -r src/covet/
  safety check
  ```

- [ ] **Performance Testing:** Complete load tests
  ```bash
  pip install locust
  locust -f tests/performance/load_test.py
  ```

- [ ] **Documentation Review:** Verify all examples work

### Environment Checklist

- [ ] Production environment variables configured
- [ ] SSL certificates obtained and installed
- [ ] Database backups configured
- [ ] Monitoring tools set up
- [ ] Log aggregation configured
- [ ] CDN configured (if needed)
- [ ] DNS records updated
- [ ] Firewall rules configured
- [ ] Load balancer configured
- [ ] Health check endpoints tested

---

## Architecture Overview

### Recommended Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    CDN / Edge Network                        │
│                  (CloudFlare / Fastly)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Load Balancer (HAProxy/nginx)              │
│              SSL Termination & Rate Limiting                 │
└─────┬──────────────┬──────────────┬──────────────┬──────────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ CovetPy  │  │ CovetPy  │  │ CovetPy  │  │ CovetPy  │
│ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker 4 │
│ (uvicorn)│  │ (uvicorn)│  │ (uvicorn)│  │ (uvicorn)│
└─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘
      │              │              │              │
      └──────────────┴──────────────┴──────────────┘
                     │
      ┌──────────────┼──────────────┬──────────────┐
      │              │              │              │
      ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│PostgreSQL│  │  Redis   │  │ Message  │  │  S3/GCS  │
│ Primary  │  │  Cache   │  │  Queue   │  │  Storage │
└─────┬────┘  └──────────┘  └──────────┘  └──────────┘
      │
      ▼
┌──────────┐
│PostgreSQL│
│ Replica  │
└──────────┘
```

### Scaling Strategies

#### Horizontal Scaling (Recommended)
- **Workers:** 2-4 workers per CPU core
- **Instances:** Start with 4, scale to 20+ based on load
- **Database:** Master-replica setup with read replicas
- **Cache:** Redis Cluster for distributed caching

#### Vertical Scaling
- **CPU:** 8-32 cores per instance
- **RAM:** 16-64 GB per instance
- **Database:** 32-128 GB RAM, SSD storage

---

## Infrastructure Setup

### Option 1: Docker + Kubernetes (Recommended)

#### 1. Build Production Docker Image

```dockerfile
# File: Dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY src/ ./src/
COPY setup.py ./

# Install application
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 covetpy && \
    chown -R covetpy:covetpy /app

USER covetpy

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and push:
```bash
# Build
docker build -t covetpy:latest -t covetpy:v1.0.0 .

# Test locally
docker run -p 8000:8000 covetpy:latest

# Push to registry
docker tag covetpy:latest registry.example.com/covetpy:latest
docker push registry.example.com/covetpy:latest
```

#### 2. Kubernetes Deployment

```yaml
# File: k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covetpy-app
  namespace: production
  labels:
    app: covetpy
    version: v1.0.0
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: covetpy
  template:
    metadata:
      labels:
        app: covetpy
        version: v1.0.0
    spec:
      containers:
      - name: covetpy
        image: registry.example.com/covetpy:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: secret-key
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
---
apiVersion: v1
kind: Service
metadata:
  name: covetpy-service
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: covetpy
  ports:
  - port: 80
    targetPort: 8000
    name: http
  - port: 443
    targetPort: 8000
    name: https
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: covetpy-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: covetpy-app
  minReplicas: 4
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### 3. Secrets Management

```yaml
# File: k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: covetpy-secrets
  namespace: production
type: Opaque
stringData:
  database-url: "postgresql://user:password@postgres:5432/covetpy_prod"
  redis-url: "redis://redis:6379/0"
  secret-key: "your-secret-key-change-this-in-production"
  jwt-secret: "your-jwt-secret-change-this-too"
```

Apply Kubernetes resources:
```bash
# Create namespace
kubectl create namespace production

# Apply secrets (use sealed-secrets or Vault in real production)
kubectl apply -f k8s/secrets.yaml

# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -n production
kubectl logs -f deployment/covetpy-app -n production
```

---

### Option 2: Traditional VPS/VM Deployment

#### 1. Server Setup (Ubuntu 22.04 LTS)

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.10+
sudo apt-get install -y python3.10 python3.10-dev python3-pip

# Install system dependencies
sudo apt-get install -y \
    nginx \
    postgresql-14 \
    redis-server \
    supervisor \
    certbot \
    python3-certbot-nginx

# Install application
cd /opt
sudo git clone https://github.com/yourorg/covetpy.git
cd covetpy
sudo pip3 install -e .
```

#### 2. Systemd Service

```ini
# File: /etc/systemd/system/covetpy.service
[Unit]
Description=CovetPy Web Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=covetpy
Group=covetpy
WorkingDirectory=/opt/covetpy
Environment="PATH=/opt/covetpy/venv/bin"
Environment="DATABASE_URL=postgresql://user:pass@localhost/covetpy_prod"
Environment="REDIS_URL=redis://localhost:6379/0"
ExecStart=/opt/covetpy/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable covetpy
sudo systemctl start covetpy
sudo systemctl status covetpy
```

#### 3. Nginx Reverse Proxy

```nginx
# File: /etc/nginx/sites-available/covetpy
upstream covetpy_backend {
    server 127.0.0.1:8000 fail_timeout=0;
    # Add more workers if using multiple processes
    # server 127.0.0.1:8001 fail_timeout=0;
    # server 127.0.0.1:8002 fail_timeout=0;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
    listen 80;
    server_name api.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate Limiting
    limit_req zone=api_limit burst=20 nodelay;
    limit_conn conn_limit 10;

    # Client body size limit
    client_max_body_size 10M;

    # Logging
    access_log /var/log/nginx/covetpy_access.log;
    error_log /var/log/nginx/covetpy_error.log;

    # Static files (if any)
    location /static/ {
        alias /opt/covetpy/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check (bypass rate limiting)
    location /health {
        limit_req off;
        limit_conn off;
        proxy_pass http://covetpy_backend;
        access_log off;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://covetpy_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # API endpoints
    location / {
        proxy_pass http://covetpy_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/covetpy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Database Configuration

### PostgreSQL Production Setup

#### 1. Initial Database Setup

```bash
# Connect to PostgreSQL
sudo -u postgres psql

-- Create production database and user
CREATE DATABASE covetpy_prod;
CREATE USER covetpy_user WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE covetpy_prod TO covetpy_user;

-- Connect to database
\c covetpy_prod

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";  -- For query analysis

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO covetpy_user;
```

#### 2. PostgreSQL Configuration (`/etc/postgresql/14/main/postgresql.conf`)

```ini
# Memory Settings
shared_buffers = 4GB                    # 25% of total RAM
effective_cache_size = 12GB             # 75% of total RAM
maintenance_work_mem = 1GB
work_mem = 16MB

# Checkpoint Settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Connection Settings
max_connections = 200
superuser_reserved_connections = 3

# Query Planning
random_page_cost = 1.1  # For SSD storage
effective_io_concurrency = 200

# Write Ahead Log (WAL)
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'ddl'
log_duration = off
log_min_duration_statement = 1000  # Log queries taking >1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

#### 3. Connection Pool Configuration

```python
# File: src/config/database.py
from covet.database.core.connection_pool import ConnectionPool

# Production connection pool settings
pool = ConnectionPool(
    database_url=os.getenv("DATABASE_URL"),
    min_connections=10,
    max_connections=50,
    max_idle_time=300,  # 5 minutes
    max_lifetime=1800,  # 30 minutes
    connection_timeout=10,
    command_timeout=30,
    ssl_mode="require",  # Always use SSL in production
    application_name="covetpy_production"
)
```

#### 4. Read Replica Setup

```python
# File: src/config/database.py
from covet.database.replication.router import ReplicationRouter

# Configure master and replicas
db_router = ReplicationRouter(
    master_url=os.getenv("DATABASE_URL"),
    replica_urls=[
        os.getenv("DATABASE_REPLICA_1_URL"),
        os.getenv("DATABASE_REPLICA_2_URL"),
    ],
    read_preference="replica_preferred",  # Use replicas for reads when available
    health_check_interval=30
)
```

#### 5. Database Backup Strategy

```bash
# Daily automated backups
# File: /etc/cron.daily/covetpy-backup
#!/bin/bash
BACKUP_DIR="/var/backups/covetpy"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/covetpy_prod_$DATE.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -U covetpy_user -h localhost covetpy_prod | gzip > $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://your-backup-bucket/database/

# Keep only last 30 days locally
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Log completion
echo "Backup completed: $BACKUP_FILE"
```

Make executable:
```bash
sudo chmod +x /etc/cron.daily/covetpy-backup
```

---

## Application Deployment

### Environment Variables (Production)

```bash
# File: /opt/covetpy/.env.production
# NEVER commit this file to version control!

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-long-random-secret-key-minimum-32-characters
API_VERSION=v1.0.0

# Database
DATABASE_URL=postgresql://covetpy_user:password@postgres-primary:5432/covetpy_prod
DATABASE_REPLICA_1_URL=postgresql://covetpy_user:password@postgres-replica1:5432/covetpy_prod
DATABASE_REPLICA_2_URL=postgresql://covetpy_user:password@postgres-replica2:5432/covetpy_prod
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis-primary:6379/0
REDIS_CACHE_URL=redis://redis-cache:6379/1
REDIS_SESSION_URL=redis://redis-session:6379/2

# Security
JWT_SECRET_KEY=different-secret-for-jwt-tokens-minimum-64-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://example.com,https://app.example.com
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=5000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/covetpy/app.log

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Email (for notifications)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
ADMIN_EMAIL=admin@example.com

# Storage
S3_BUCKET=your-production-bucket
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# CDN
CDN_URL=https://cdn.example.com
STATIC_URL=https://cdn.example.com/static/
```

---

## Security Hardening

### 1. Application Security Configuration

```python
# File: src/main.py
from covet import CovetPy
from covet.security import configure_basic_security
from covet.security.headers import SecurityHeadersMiddleware
from covet.security.csrf import CSRFMiddleware
from covet.security.rate_limiting import RateLimitMiddleware
from covet.middleware import CORSMiddleware

app = CovetPy()

# Basic security (auth, CSRF, headers, rate limiting)
auth = configure_basic_security(app, secret_key=os.getenv("SECRET_KEY"))

# Additional security layers
app.middleware(SecurityHeadersMiddleware(
    csp="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    hsts_max_age=31536000,
    hsts_include_subdomains=True,
    hsts_preload=True,
    frame_options="DENY",
    content_type_options="nosniff",
    xss_protection="1; mode=block",
    referrer_policy="strict-origin-when-cross-origin"
))

# CORS for specific origins only
app.middleware(CORSMiddleware(
    allowed_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allowed_headers=["*"],
    allow_credentials=True,
    max_age=3600
))

# Rate limiting
app.middleware(RateLimitMiddleware(
    rate="100/minute",
    burst=20,
    per_ip=True,
    redis_url=os.getenv("REDIS_URL")
))
```

### 2. Firewall Configuration (UFW)

```bash
# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (from specific IPs only)
sudo ufw allow from 1.2.3.4 to any port 22

# HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# PostgreSQL (internal network only)
sudo ufw allow from 10.0.0.0/8 to any port 5432

# Redis (internal network only)
sudo ufw allow from 10.0.0.0/8 to any port 6379

# Enable firewall
sudo ufw enable
sudo ufw status verbose
```

### 3. SSL/TLS Configuration

```bash
# Obtain Let's Encrypt certificate
sudo certbot --nginx -d api.example.com -d www.api.example.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run

# Test SSL configuration
curl https://www.ssllabs.com/ssltest/analyze.html?d=api.example.com
```

---

## Performance Optimization

### 1. Application-Level Optimization

```python
# File: src/config/performance.py
from covet.cache import RedisCache
from covet.database.query_builder.cache import QueryCache

# Configure caching
cache = RedisCache(
    url=os.getenv("REDIS_CACHE_URL"),
    default_ttl=300,
    namespace="covetpy"
)

# Query caching
query_cache = QueryCache(
    backend=cache,
    enabled=True,
    default_ttl=60
)

# Response caching decorator
from functools import wraps

def cache_response(ttl=60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"response:{func.__name__}:{args}:{kwargs}"
            cached = await cache.get(cache_key)
            if cached:
                return cached

            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
```

### 2. Database Performance

```python
# File: src/models/base.py
from covet.database.orm import Model

class User(Model):
    # Add indexes for frequently queried fields
    class Meta:
        indexes = [
            ("email",),  # Single column index
            ("created_at", "status"),  # Composite index
        ]

    @classmethod
    async def get_active_users(cls):
        # Use select_related to avoid N+1 queries
        return await cls.objects.select_related("profile", "permissions").filter(
            status="active"
        ).all()
```

### 3. Connection Pooling Best Practices

```python
# Optimal pool sizing formula:
# connections = ((core_count * 2) + effective_spindle_count)
# For 8 cores + SSD: (8 * 2) + 1 = 17 connections per instance
# With 4 instances: 17 * 4 = 68 total connections
# Set max_connections = 100 in PostgreSQL (with buffer)

pool_config = {
    "min_connections": 10,
    "max_connections": 50,
    "max_idle_time": 300,
    "max_lifetime": 1800,
}
```

---

## Monitoring & Observability

### 1. Application Metrics (Prometheus)

```python
# File: src/middleware/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Define metrics
request_count = Counter(
    "covetpy_requests_total",
    "Total request count",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "covetpy_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"]
)

active_connections = Gauge(
    "covetpy_active_connections",
    "Number of active connections"
)

# Metrics endpoint
@app.route("/metrics")
async def metrics(request):
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### 2. Logging Configuration

```python
# File: src/config/logging.py
import logging
import logging.handlers
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logging
def setup_logging():
    logger = logging.getLogger("covetpy")
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        "/var/log/covetpy/app.log",
        maxBytes=100*1024*1024,  # 100MB
        backupCount=10
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    return logger
```

### 3. Health Check Endpoints

```python
# File: src/routes/health.py
from covet import CovetPy
from covet.health import HealthCheck

app = CovetPy()
health = HealthCheck()

@app.route("/health")
async def health_check(request):
    """Basic liveness check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.route("/health/ready")
async def readiness_check(request):
    """Readiness check - verify dependencies"""
    checks = {
        "database": await health.check_database(),
        "redis": await health.check_redis(),
        "external_api": await health.check_external_service(),
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }, status_code

@app.route("/health/startup")
async def startup_check(request):
    """Startup check - verify initialization"""
    return {
        "status": "started",
        "version": app.version,
        "timestamp": datetime.now().isoformat()
    }
```

### 4. Error Tracking (Sentry)

```python
# File: src/main.py
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,
    send_default_pii=False,  # Don't send PII
    before_send=filter_sensitive_data,
)

# Wrap app with Sentry middleware
app = SentryAsgiMiddleware(app)

def filter_sensitive_data(event, hint):
    """Remove sensitive data before sending to Sentry"""
    if "request" in event:
        if "headers" in event["request"]:
            # Remove authorization headers
            event["request"]["headers"].pop("authorization", None)
            event["request"]["headers"].pop("cookie", None)
    return event
```

---

## Zero-Downtime Deployment

### Strategy 1: Rolling Update (Kubernetes)

```bash
# Update image
kubectl set image deployment/covetpy-app covetpy=registry.example.com/covetpy:v1.1.0 -n production

# Watch rollout
kubectl rollout status deployment/covetpy-app -n production

# If issues arise, rollback
kubectl rollout undo deployment/covetpy-app -n production
```

The Kubernetes deployment configured earlier automatically handles zero-downtime with:
- `maxUnavailable: 0` - No pods terminated until new ones ready
- `maxSurge: 1` - One extra pod during update
- Readiness probes - Traffic only to ready pods
- `preStop` lifecycle hook - Graceful shutdown

### Strategy 2: Blue-Green Deployment

```bash
# Deploy new version (green) alongside old (blue)
kubectl apply -f k8s/deployment-green.yaml

# Test green deployment
kubectl run test-pod --rm -it --image=curlimages/curl -- \
  curl http://covetpy-service-green/health

# Switch traffic to green
kubectl patch service covetpy-service -p '{"spec":{"selector":{"version":"v1.1.0"}}}'

# Monitor for issues
# If problems, switch back to blue
kubectl patch service covetpy-service -p '{"spec":{"selector":{"version":"v1.0.0"}}}'

# Once confident, remove blue deployment
kubectl delete deployment covetpy-app-blue -n production
```

### Strategy 3: Canary Deployment

```yaml
# 10% traffic to new version, 90% to old
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: covetpy-canary
spec:
  hosts:
  - covetpy-service
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: covetpy-service
        subset: v1.1.0
  - route:
    - destination:
        host: covetpy-service
        subset: v1.0.0
      weight: 90
    - destination:
        host: covetpy-service
        subset: v1.1.0
      weight: 10
```

### Deployment Checklist

**Pre-Deployment:**
- [ ] Run full test suite
- [ ] Update changelog
- [ ] Tag release in git
- [ ] Build and push Docker image
- [ ] Run security scan on image
- [ ] Backup production database
- [ ] Notify team in Slack

**During Deployment:**
- [ ] Deploy to staging first
- [ ] Smoke test staging
- [ ] Deploy to production
- [ ] Monitor error rates
- [ ] Monitor response times
- [ ] Monitor CPU/memory
- [ ] Check logs for errors

**Post-Deployment:**
- [ ] Verify all health checks pass
- [ ] Run smoke tests on production
- [ ] Monitor for 30 minutes
- [ ] Update documentation
- [ ] Notify team of completion

---

## Rollback Procedures

### Immediate Rollback (Emergency)

```bash
# Kubernetes
kubectl rollout undo deployment/covetpy-app -n production
kubectl rollout status deployment/covetpy-app -n production

# Verify rollback
kubectl get pods -n production
kubectl logs -f deployment/covetpy-app -n production

# Traditional deployment
sudo systemctl stop covetpy
cd /opt/covetpy
git checkout v1.0.0  # Previous version
sudo systemctl start covetpy
sudo systemctl status covetpy
```

### Database Rollback

```bash
# Restore from backup
# 1. Stop application
kubectl scale deployment covetpy-app --replicas=0 -n production

# 2. Restore database
pg_restore -U covetpy_user -d covetpy_prod /var/backups/covetpy/backup_before_deploy.sql

# 3. Restart application with old version
kubectl rollout undo deployment/covetpy-app -n production
kubectl scale deployment covetpy-app --replicas=4 -n production
```

### Rollback Decision Matrix

| Severity | Condition | Action | Approval |
|----------|-----------|--------|----------|
| P0 | Service down | Immediate rollback | Any engineer |
| P1 | Major functionality broken | Rollback within 15 min | On-call lead |
| P2 | Minor issues, workaround exists | Hotfix or rollback within 1 hour | Team lead |
| P3 | Cosmetic issues | Fix in next release | Product owner |

---

## Disaster Recovery

### Backup Strategy

**RPO (Recovery Point Objective):** 1 hour
**RTO (Recovery Time Objective):** 4 hours

#### 1. Database Backups

```bash
# Continuous archiving (WAL)
# In postgresql.conf:
archive_mode = on
archive_command = 'aws s3 cp %p s3://your-backup-bucket/wal/%f'

# Daily full backups
0 2 * * * pg_basebackup -U postgres -D /var/backups/pg_backup -Ft -z -P

# Hourly incremental backups (via WAL archiving)
# Automatic with archive_command
```

#### 2. Disaster Recovery Runbook

**Scenario: Complete Database Loss**

1. **Assess Damage**
   ```bash
   # Check what's available
   aws s3 ls s3://your-backup-bucket/database/
   aws s3 ls s3://your-backup-bucket/wal/
   ```

2. **Restore Latest Backup**
   ```bash
   # Download latest base backup
   aws s3 cp s3://your-backup-bucket/database/latest.tar.gz /tmp/

   # Extract
   sudo -u postgres tar xzf /tmp/latest.tar.gz -C /var/lib/postgresql/14/main/

   # Download WAL files for point-in-time recovery
   aws s3 sync s3://your-backup-bucket/wal/ /var/lib/postgresql/14/main/pg_wal/
   ```

3. **Configure Recovery**
   ```bash
   # Create recovery.conf
   sudo -u postgres cat > /var/lib/postgresql/14/main/recovery.conf << EOF
   restore_command = 'cp /var/lib/postgresql/14/main/pg_wal/%f %p'
   recovery_target_time = '2025-10-11 14:00:00'
   EOF
   ```

4. **Start Recovery**
   ```bash
   sudo systemctl start postgresql
   # Monitor logs
   sudo tail -f /var/log/postgresql/postgresql-14-main.log
   ```

5. **Verify and Resume Service**
   ```bash
   # Connect and verify data
   sudo -u postgres psql covetpy_prod -c "SELECT COUNT(*) FROM users;"

   # Resume application
   kubectl scale deployment covetpy-app --replicas=4 -n production
   ```

**Scenario: Complete Infrastructure Loss**

1. **Spin up new infrastructure** (Infrastructure as Code)
   ```bash
   terraform apply -var-file=production.tfvars
   ```

2. **Deploy application**
   ```bash
   kubectl apply -f k8s/
   ```

3. **Restore databases** (as above)

4. **Update DNS** (5-minute TTL for fast failover)
   ```bash
   aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch file://dns-failover.json
   ```

5. **Verify and monitor**

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: High Database Connection Count

**Symptoms:**
- Error: "FATAL: sorry, too many clients already"
- Slow query performance

**Diagnosis:**
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
```

**Solution:**
```python
# Reduce connection pool size per instance
# If you have 4 instances with max_connections=50 each:
# Total: 200 connections
# Ensure PostgreSQL max_connections > 200
# Set in postgresql.conf: max_connections = 300
```

#### Issue 2: High Memory Usage

**Symptoms:**
- OOMKilled pods in Kubernetes
- Slow performance
- Swap usage increasing

**Diagnosis:**
```bash
# Check memory usage
kubectl top pods -n production
free -h

# Check for memory leaks
python -m memray run --live-remote src/main.py
```

**Solution:**
```yaml
# Increase memory limits in deployment
resources:
  limits:
    memory: "4Gi"  # Increased from 2Gi

# Or reduce worker count
CMD ["uvicorn", "src.main:app", "--workers", "2"]  # Reduced from 4
```

#### Issue 3: Slow API Response Times

**Symptoms:**
- Response times > 1 second
- Timeout errors

**Diagnosis:**
```python
# Enable query logging
import logging
logging.getLogger("covet.database").setLevel(logging.DEBUG)

# Check slow queries in PostgreSQL
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Solution:**
```python
# Add missing indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);

# Enable query caching
from covet.database.query_builder.cache import QueryCache
cache = QueryCache(enabled=True, default_ttl=60)

# Use select_related to avoid N+1 queries
users = await User.objects.select_related("profile").all()
```

#### Issue 4: WebSocket Disconnections

**Symptoms:**
- Clients frequently disconnecting
- "Connection reset by peer" errors

**Diagnosis:**
```bash
# Check nginx timeout settings
grep timeout /etc/nginx/sites-enabled/covetpy

# Check application logs
kubectl logs -f deployment/covetpy-app -n production | grep websocket
```

**Solution:**
```nginx
# Increase nginx timeouts for WebSocket
proxy_read_timeout 86400;  # 24 hours
proxy_send_timeout 86400;

# Add ping/pong in application
from covet.websocket import WebSocketEndpoint

class MyEndpoint(WebSocketEndpoint):
    async def on_connect(self, ws):
        await ws.accept()
        # Start ping task
        asyncio.create_task(self.ping_loop(ws))

    async def ping_loop(self, ws):
        while True:
            await asyncio.sleep(30)
            await ws.send_json({"type": "ping"})
```

#### Issue 5: Database Connection Timeout

**Symptoms:**
- "could not connect to server: Connection timed out"
- Applications can't reach database

**Diagnosis:**
```bash
# Test connection
psql -h postgres-host -U covetpy_user -d covetpy_prod

# Check firewall
sudo ufw status
telnet postgres-host 5432

# Check PostgreSQL is listening
sudo netstat -plnt | grep 5432
```

**Solution:**
```bash
# Update postgresql.conf
listen_addresses = '*'  # Or specific IPs

# Update pg_hba.conf
host covetpy_prod covetpy_user 10.0.0.0/8 md5

# Restart PostgreSQL
sudo systemctl restart postgresql

# Update firewall
sudo ufw allow from 10.0.0.0/8 to any port 5432
```

### Monitoring Dashboard Metrics

**Key Metrics to Monitor:**

1. **Application Metrics**
   - Request rate (req/s)
   - Response time (p50, p95, p99)
   - Error rate (%)
   - Active connections
   - Queue depth

2. **Database Metrics**
   - Connection count
   - Query rate
   - Slow query count
   - Cache hit ratio
   - Replication lag
   - Transaction rate

3. **Infrastructure Metrics**
   - CPU usage (%)
   - Memory usage (%)
   - Disk I/O
   - Network I/O
   - Pod restarts
   - Node health

4. **Business Metrics**
   - Active users
   - API calls per customer
   - Failed authentications
   - Data processed

---

## Appendix: Quick Reference

### Essential Commands

```bash
# Application
kubectl get pods -n production
kubectl logs -f deployment/covetpy-app -n production
kubectl exec -it <pod-name> -n production -- /bin/bash

# Database
sudo -u postgres psql covetpy_prod
\dt                    # List tables
\d+ table_name         # Describe table
SELECT pg_size_pretty(pg_database_size('covetpy_prod'));  # Database size

# Nginx
sudo nginx -t          # Test configuration
sudo systemctl reload nginx  # Reload without downtime
sudo tail -f /var/log/nginx/covetpy_access.log

# Redis
redis-cli
INFO                   # Server info
DBSIZE                 # Key count
KEYS pattern*          # Find keys (use SCAN in production)

# System
htop                   # Resource usage
df -h                  # Disk usage
free -h                # Memory usage
netstat -tulpn         # Network connections
```

### Performance Tuning Checklist

- [ ] Database indexes on all foreign keys
- [ ] Connection pooling configured
- [ ] Query caching enabled
- [ ] Redis caching for expensive operations
- [ ] CDN for static assets
- [ ] gzip compression enabled
- [ ] HTTP/2 enabled
- [ ] Database query optimization
- [ ] N+1 query detection enabled
- [ ] Async operations for I/O
- [ ] Worker count optimized
- [ ] Memory limits appropriate
- [ ] CPU limits appropriate

### Security Checklist

- [ ] All secrets in environment variables
- [ ] No hardcoded credentials
- [ ] SSL/TLS everywhere
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] CSRF protection enabled
- [ ] Rate limiting active
- [ ] Input validation on all endpoints
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] Authentication required
- [ ] Authorization checks
- [ ] Audit logging enabled
- [ ] Regular security updates
- [ ] Dependency vulnerability scanning
- [ ] Firewall rules tight
- [ ] Database encrypted at rest
- [ ] Backups encrypted
- [ ] Secrets rotation schedule

---

## Conclusion

This production deployment guide provides comprehensive instructions for deploying CovetPy in a secure, scalable, and maintainable way.

**Key Takeaways:**

1. **Fix P0 issues first** - Module exports and API consistency
2. **Security is paramount** - Multiple layers of protection
3. **Monitor everything** - Metrics, logs, traces
4. **Plan for failure** - Backups, rollbacks, disaster recovery
5. **Automate deployment** - CI/CD, infrastructure as code
6. **Test thoroughly** - Staging environment mirrors production

**Estimated Time to Production:**
- **With P0 fixes:** 2-3 weeks
- **Without P0 fixes:** Not recommended

For questions or issues, refer to:
- Integration Test Report: `docs/TEAM33_INTEGRATION_TEST_REPORT.md`
- Security Guide: `docs/archive/SECURITY_GUIDE.md`
- API Documentation: `docs/archive/API_REFERENCE.md`

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-11
**Guide Status:** COMPLETE
**Lines in Guide:** 1,847

---

**END OF PRODUCTION DEPLOYMENT GUIDE**
