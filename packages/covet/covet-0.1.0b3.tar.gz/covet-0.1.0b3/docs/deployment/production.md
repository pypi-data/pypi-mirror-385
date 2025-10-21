# CovetPy Production Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2025-10-11

## Table of Contents

- [Overview](#overview)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [High Availability Setup](#high-availability-setup)
- [Monitoring Configuration](#monitoring-configuration)
- [Security Hardening](#security-hardening)
- [Performance Optimization](#performance-optimization)
- [Disaster Recovery](#disaster-recovery)

---

## Overview

This guide covers production deployment of CovetPy applications with Docker, Kubernetes, high availability, monitoring, and security best practices.

**Architecture:**
```
Load Balancer (nginx/HAProxy)
    ↓
CovetPy App Instances (3+)
    ↓
PostgreSQL Primary + Replicas
Redis Cluster
```

---

## Docker Deployment

### Dockerfile

```dockerfile
# Multi-stage build for optimal image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts are executable
RUN chmod +x /app/scripts/*.sh

# Create non-root user
RUN useradd -m -u 1000 covetpy && \
    chown -R covetpy:covetpy /app

USER covetpy

# Environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  # CovetPy application
  app:
    build: .
    container_name: covetpy-app
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:secret@db:5432/covetpy
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./static:/app/static
    networks:
      - covetpy-network

  # PostgreSQL database
  db:
    image: postgres:14-alpine
    container_name: covetpy-db
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=covetpy
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - covetpy-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    container_name: covetpy-redis
    restart: always
    command: redis-server --appendonly yes --requirepass secret
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - covetpy-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: covetpy-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./static:/var/www/static:ro
    depends_on:
      - app
    networks:
      - covetpy-network

volumes:
  postgres-data:
  redis-data:

networks:
  covetpy-network:
    driver: bridge
```

### Nginx Configuration

```nginx
# nginx.conf
upstream covetpy_backend {
    least_conn;
    server app:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API requests
    location / {
        proxy_pass http://covetpy_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check
    location /health {
        proxy_pass http://covetpy_backend/health;
        access_log off;
    }
}
```

### Deployment Commands

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Run migrations
docker-compose exec app python -m covet migration apply

# Scale application
docker-compose up -d --scale app=3

# Stop all services
docker-compose down

# Restart app only
docker-compose restart app
```

---

## Kubernetes Deployment

### Deployment Manifest

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covetpy-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: covetpy
  template:
    metadata:
      labels:
        app: covetpy
    spec:
      containers:
      - name: covetpy
        image: your-registry/covetpy:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: covetpy-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service and Ingress

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: covetpy-service
  namespace: production
spec:
  selector:
    app: covetpy
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: covetpy-ingress
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: covetpy-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: covetpy-service
            port:
              number: 80
```

### PostgreSQL StatefulSet

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: production
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        env:
        - name: POSTGRES_DB
          value: covetpy
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

### Deployment Commands

```bash
# Create namespace
kubectl create namespace production

# Create secrets
kubectl create secret generic covetpy-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=secret-key="your-secret-key" \
  -n production

# Deploy application
kubectl apply -f k8s/ -n production

# Check status
kubectl get pods -n production
kubectl get services -n production
kubectl get ingress -n production

# View logs
kubectl logs -f deployment/covetpy-app -n production

# Scale deployment
kubectl scale deployment covetpy-app --replicas=5 -n production

# Rolling update
kubectl set image deployment/covetpy-app covetpy=your-registry/covetpy:v2 -n production

# Rollback
kubectl rollout undo deployment/covetpy-app -n production
```

---

## High Availability Setup

### Multi-Region Architecture

```
Region A (Primary):
├── Load Balancer
├── CovetPy Instances (3+)
├── PostgreSQL Primary
└── Redis Primary

Region B (Secondary):
├── Load Balancer
├── CovetPy Instances (3+)
├── PostgreSQL Read Replica
└── Redis Replica

Global Load Balancer (Route53/Cloudflare)
```

### PostgreSQL Replication

**Primary Configuration:**
```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB
synchronous_commit = on
```

**Replica Configuration:**
```bash
# Create replica
pg_basebackup -h primary-host -D /var/lib/postgresql/data -U replicator -P -R

# standby.signal file automatically created
```

**Connection String (Read Replicas):**
```python
# config/database.py
PRIMARY = DatabaseConfig(
    host='primary.db.example.com',
    database='covetpy',
    pool_size=20
)

REPLICA = DatabaseConfig(
    host='replica.db.example.com',
    database='covetpy',
    pool_size=30  # More connections for reads
)

# Route reads to replica
@app.get('/api/posts/')
async def list_posts():
    # Use replica for read-only queries
    posts = await Post.objects.using('replica').all()
    return posts
```

### Redis Sentinel for HA

```yaml
# docker-compose-redis-ha.yaml
version: '3.8'

services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes

  redis-replica-1:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379

  redis-replica-2:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379

  redis-sentinel-1:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf

  redis-sentinel-2:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf

  redis-sentinel-3:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf
```

---

## Monitoring Configuration

### Prometheus + Grafana

```yaml
# docker-compose-monitoring.yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  grafana-data:
```

**Prometheus Configuration:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'covetpy'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
```

**Expose Metrics in CovetPy:**
```python
# app/main.py
from covet.metrics import metrics

app = Covet()

# Add metrics endpoint
@app.get('/metrics')
async def prometheus_metrics():
    """Expose Prometheus metrics."""
    return metrics.generate_latest()
```

---

## Security Hardening

### Security Checklist

- [ ] Use HTTPS only (TLS 1.2+)
- [ ] Set secure headers (CSP, HSTS, X-Frame-Options)
- [ ] Enable CORS only for trusted origins
- [ ] Use strong SECRET_KEY (32+ random bytes)
- [ ] Store secrets in environment variables or secret manager
- [ ] Enable rate limiting
- [ ] Validate all user input
- [ ] Use parameterized queries (prevent SQL injection)
- [ ] Enable CSRF protection
- [ ] Hash passwords with bcrypt
- [ ] Implement JWT token expiration
- [ ] Regular security updates
- [ ] Enable audit logging
- [ ] Restrict database user permissions
- [ ] Use network segmentation
- [ ] Enable firewall rules

### Example Security Configuration

```python
# config/security.py
from covet.security import SecurityConfig

SECURITY = SecurityConfig(
    # CORS
    cors_allowed_origins=[
        'https://example.com',
        'https://app.example.com'
    ],
    cors_allow_credentials=True,

    # Rate limiting
    rate_limit_enabled=True,
    rate_limit_requests=100,
    rate_limit_window=60,  # per minute

    # CSRF
    csrf_protection=True,
    csrf_cookie_secure=True,

    # Headers
    hsts_enabled=True,
    hsts_max_age=31536000,
    frame_options='DENY',
    content_type_options='nosniff',

    # JWT
    jwt_secret_key=os.getenv('JWT_SECRET_KEY'),
    jwt_algorithm='HS256',
    jwt_expiration=3600  # 1 hour
)
```

---

## Disaster Recovery

### Backup Strategy

**Automated Backups:**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
pg_dump -h localhost -U postgres covetpy | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/db_$DATE.sql.gz" s3://my-backups/postgresql/

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

# Cron: Run daily at 2 AM
# 0 2 * * * /path/to/backup.sh
```

**Restore:**
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

# Download from S3
aws s3 cp "s3://my-backups/postgresql/$BACKUP_FILE" ./

# Restore database
gunzip < "$BACKUP_FILE" | psql -h localhost -U postgres covetpy
```

### Disaster Recovery Plan

1. **Detect Failure** (automated monitoring)
2. **Failover to Replica** (automatic or manual)
3. **Investigate Root Cause**
4. **Restore Service**
5. **Post-Mortem Review**

**Automated Failover (PostgreSQL):**
```bash
# patroni.yml (HA tool for PostgreSQL)
scope: covetpy-cluster
name: node1

restapi:
  listen: 0.0.0.0:8008
  connect_address: node1:8008

postgresql:
  listen: 0.0.0.0:5432
  connect_address: node1:5432
  data_dir: /var/lib/postgresql/data

  authentication:
    replication:
      username: replicator
      password: secret

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
```

---

## Conclusion

Production deployment requires careful planning and ongoing maintenance. This guide provides a solid foundation, but adapt to your specific requirements.

**Key Takeaways:**
1. Use Docker/Kubernetes for consistency
2. Implement high availability (multiple instances, database replication)
3. Monitor everything (metrics, logs, health checks)
4. Harden security (HTTPS, rate limiting, input validation)
5. Automate backups and test recovery
6. Plan for scale (horizontal scaling, caching, CDN)

---

**Document Information:**
- Version: 1.0.0
- Last Updated: 2025-10-11
- Maintained by: CovetPy Team
