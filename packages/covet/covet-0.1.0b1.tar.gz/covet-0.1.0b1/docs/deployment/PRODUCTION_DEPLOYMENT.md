# CovetPy Production Deployment Guide

**Version:** 0.2.0-sprint1
**Last Updated:** 2025-10-11
**Status:** Production-Ready Educational Framework

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Systemd Service](#systemd-service)
5. [Nginx Reverse Proxy](#nginx-reverse-proxy)
6. [Docker Deployment](#docker-deployment)
7. [Kubernetes Deployment](#kubernetes-deployment)
8. [Post-Deployment Validation](#post-deployment-validation)
9. [Production Checklist](#production-checklist)

---

## Prerequisites

### System Requirements

**Minimum Requirements:**
- Python 3.9+ (3.11+ recommended for best performance)
- 2 CPU cores
- 4GB RAM
- 20GB disk space
- Linux-based OS (Ubuntu 20.04+, CentOS 8+, or Debian 11+)

**Recommended for Production:**
- Python 3.11 or 3.12
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD storage
- Ubuntu 22.04 LTS or Rocky Linux 9

### Database Requirements

CovetPy supports multiple database backends:

- **SQLite** (built-in, no setup needed - dev/testing only)
- **PostgreSQL 14+** (recommended for production)
- **MySQL 8.0+** / MariaDB 10.6+

### Optional Components

- **Redis 6.0+** - For caching and session storage
- **Nginx 1.18+** - Reverse proxy and load balancing
- **Certbot** - For SSL/TLS certificates (Let's Encrypt)

---

## Installation

### 1. System Package Installation

#### Ubuntu/Debian

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Install Redis (optional)
sudo apt-get install -y redis-server

# Install Nginx
sudo apt-get install -y nginx

# Install build tools
sudo apt-get install -y build-essential libssl-dev libffi-dev
```

#### CentOS/RHEL/Rocky Linux

```bash
# Update system
sudo dnf update -y

# Install Python 3.11
sudo dnf install -y python3.11 python3.11-devel python3.11-pip

# Install PostgreSQL
sudo dnf install -y postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Install Redis (optional)
sudo dnf install -y redis
sudo systemctl enable redis
sudo systemctl start redis

# Install Nginx
sudo dnf install -y nginx
sudo systemctl enable nginx

# Install build tools
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y openssl-devel libffi-devel
```

### 2. Create Application User

```bash
# Create dedicated user for application
sudo useradd -r -m -s /bin/bash covet
sudo usermod -aG sudo covet  # Optional: for management tasks

# Create application directories
sudo mkdir -p /opt/covet
sudo chown -R covet:covet /opt/covet
```

### 3. Application Setup

Switch to covet user:

```bash
sudo su - covet
cd /opt/covet
```

Create and activate virtual environment:

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 4. Install CovetPy

#### Option A: From PyPI (Recommended for Production)

```bash
# Core framework (zero dependencies)
pip install covetpy

# With production dependencies
pip install covetpy[production]

# Or full feature set
pip install covetpy[full]
```

#### Option B: From Source (For Development/Customization)

```bash
# Clone repository
git clone https://github.com/covetpy/covetpy.git
cd covetpy

# Install in editable mode with production dependencies
pip install -e .[production]
```

#### Option C: Specific Feature Sets

```bash
# Just ASGI server
pip install covetpy[server]

# With database support
pip install covetpy[database]

# With security enhancements
pip install covetpy[security]

# With monitoring
pip install covetpy[monitoring]
```

### 5. Database Setup

#### PostgreSQL (Recommended)

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb covet_production
createuser covet_app --pwprompt

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE covet_production TO covet_app;"
psql -c "ALTER DATABASE covet_production OWNER TO covet_app;"

# For PostgreSQL 15+, grant schema privileges
psql -d covet_production -c "GRANT ALL ON SCHEMA public TO covet_app;"
psql -d covet_production -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO covet_app;"
psql -d covet_production -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO covet_app;"

# Exit postgres user
exit
```

#### MySQL/MariaDB

```bash
# Login to MySQL
sudo mysql -u root -p

# Create database and user
CREATE DATABASE covet_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'covet_app'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON covet_production.* TO 'covet_app'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Run Database Migrations

```bash
# Activate virtual environment
source /opt/covet/venv/bin/activate

# Run migrations (if using CovetPy's migration system)
covet migrate

# Or using your application's migration command
python manage.py migrate
```

---

## Configuration

### 1. Environment Variables

Create `/etc/covet/production.env`:

```bash
sudo mkdir -p /etc/covet
sudo nano /etc/covet/production.env
```

**Production Configuration:**

```bash
# =============================================================================
# CovetPy Production Configuration
# =============================================================================

# Application Settings
# =============================================================================
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secret-key-here-minimum-32-characters-use-openssl-rand
APP_NAME=CovetPy Production

# Security Settings
# =============================================================================
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_32_CHARS_MINIMUM
JWT_SECRET_KEY=CHANGE_THIS_TO_ANOTHER_SECURE_RANDOM_STRING
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Allowed hosts (comma-separated)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# CORS Settings (if needed)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# Database Configuration
# =============================================================================
# PostgreSQL (Recommended)
DATABASE_URL=postgresql://covet_app:your_password@localhost:5432/covet_production

# MySQL Alternative
# DATABASE_URL=mysql://covet_app:your_password@localhost:3306/covet_production

# SQLite (Dev/Test Only)
# DATABASE_URL=sqlite:///./covet.db

# Database Pool Settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
DATABASE_ECHO=false

# Redis Configuration (Optional - for caching/sessions)
# =============================================================================
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=300

# Application Server Settings
# =============================================================================
HOST=0.0.0.0
PORT=8000
WORKERS=4  # 2-4 workers per CPU core
WORKER_CLASS=uvicorn.workers.UvicornWorker
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100
TIMEOUT=30
KEEPALIVE=5

# Logging Configuration
# =============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json  # json or text
LOG_FILE=/var/log/covet/app.log
ACCESS_LOG=/var/log/covet/access.log
ERROR_LOG=/var/log/covet/error.log

# Monitoring & Metrics
# =============================================================================
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
HEALTH_CHECK_PATH=/health
METRICS_PATH=/metrics

# Rate Limiting
# =============================================================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# File Upload Settings
# =============================================================================
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=/opt/covet/uploads
ALLOWED_UPLOAD_EXTENSIONS=jpg,jpeg,png,gif,pdf,txt

# Session Configuration
# =============================================================================
SESSION_BACKEND=redis  # redis, database, or memory
SESSION_COOKIE_NAME=covet_session
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax
SESSION_MAX_AGE=86400  # 24 hours

# Email Configuration (Optional)
# =============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com
SMTP_TLS=true

# Backup Configuration
# =============================================================================
BACKUP_ENABLED=true
BACKUP_DIR=/opt/covet/backups
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM

# Feature Flags
# =============================================================================
ENABLE_API_DOCS=false  # Disable in production
ENABLE_GRAPHQL_PLAYGROUND=false
ENABLE_DEBUG_TOOLBAR=false

# Third-Party Integrations (Optional)
# =============================================================================
# AWS_ACCESS_KEY_ID=your-aws-key
# AWS_SECRET_ACCESS_KEY=your-aws-secret
# AWS_REGION=us-east-1
# S3_BUCKET=your-bucket-name

# Sentry Error Tracking (Optional)
# SENTRY_DSN=https://your-sentry-dsn

# =============================================================================
# END OF CONFIGURATION
# =============================================================================
```

### 2. Generate Secret Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Set Proper Permissions

```bash
# Secure configuration file
sudo chmod 600 /etc/covet/production.env
sudo chown covet:covet /etc/covet/production.env

# Create log directory
sudo mkdir -p /var/log/covet
sudo chown -R covet:covet /var/log/covet
sudo chmod 755 /var/log/covet

# Create upload directory
sudo mkdir -p /opt/covet/uploads
sudo chown -R covet:covet /opt/covet/uploads
sudo chmod 755 /opt/covet/uploads

# Create backup directory
sudo mkdir -p /opt/covet/backups
sudo chown -R covet:covet /opt/covet/backups
sudo chmod 700 /opt/covet/backups
```

---

## Systemd Service

### 1. Create Systemd Service File

Create `/etc/systemd/system/covet.service`:

```bash
sudo nano /etc/systemd/system/covet.service
```

**Service Configuration:**

```ini
[Unit]
Description=CovetPy ASGI Application
Documentation=https://docs.covetpy.com
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=covet
Group=covet
WorkingDirectory=/opt/covet
Environment="PATH=/opt/covet/venv/bin"
EnvironmentFile=/etc/covet/production.env

# Production server with Uvicorn
ExecStart=/opt/covet/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log \
    --use-colors \
    --proxy-headers \
    --forwarded-allow-ips='*'

# Graceful restart
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

# Restart policy
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/covet/uploads /opt/covet/backups /var/log/covet

# Resource limits
LimitNOFILE=65536
LimitNPROC=512

# Standard output/error logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=covet

[Install]
WantedBy=multi-user.target
```

### 2. Alternative: Gunicorn with Uvicorn Workers

For better process management, use Gunicorn:

```ini
# Alternative ExecStart with Gunicorn
ExecStart=/opt/covet/venv/bin/gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keepalive 5 \
    --log-level info \
    --access-logfile /var/log/covet/access.log \
    --error-logfile /var/log/covet/error.log \
    --capture-output \
    --enable-stdio-inheritance
```

### 3. Start and Enable Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Start service
sudo systemctl start covet

# Enable service to start on boot
sudo systemctl enable covet

# Check status
sudo systemctl status covet

# View logs
sudo journalctl -u covet -f
```

### 4. Service Management Commands

```bash
# Start service
sudo systemctl start covet

# Stop service
sudo systemctl stop covet

# Restart service
sudo systemctl restart covet

# Reload service (graceful restart)
sudo systemctl reload covet

# Check status
sudo systemctl status covet

# View recent logs
sudo journalctl -u covet --since "10 minutes ago"

# Follow logs in real-time
sudo journalctl -u covet -f

# Check if service is enabled
sudo systemctl is-enabled covet
```

---

## Nginx Reverse Proxy

### 1. Create Nginx Configuration

Create `/etc/nginx/sites-available/covet`:

```bash
sudo nano /etc/nginx/sites-available/covet
```

**Nginx Configuration:**

```nginx
# Upstream configuration
upstream covet_backend {
    # Round-robin load balancing
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;

    # Add more servers for horizontal scaling
    # server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    # server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;

    # Keep connections alive
    keepalive 32;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;

    # SSL Settings (Modern Configuration)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Logs
    access_log /var/log/nginx/covet_access.log combined;
    error_log /var/log/nginx/covet_error.log warn;

    # General Settings
    client_max_body_size 10M;
    client_body_timeout 30s;
    client_header_timeout 30s;
    keepalive_timeout 65s;
    send_timeout 30s;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;

    # Static files (if serving directly from Nginx)
    location /static/ {
        alias /opt/covet/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location /media/ {
        alias /opt/covet/uploads/;
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }

    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://covet_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        access_log off;
    }

    # Authentication endpoints (strict rate limiting)
    location ~ ^/api/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;
        limit_conn conn_limit 10;

        proxy_pass http://covet_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # API endpoints (moderate rate limiting)
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 20;

        proxy_pass http://covet_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://covet_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 3600s;
        proxy_read_timeout 3600s;
    }

    # Default location (all other requests)
    location / {
        proxy_pass http://covet_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### 2. Enable Site and Test Configuration

```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/covet /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check Nginx status
sudo systemctl status nginx
```

### 3. Setup SSL Certificates with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Setup automatic renewal (if not already configured)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Docker Deployment

### 1. Dockerfile

Create `Dockerfile` in your project root:

```dockerfile
# Multi-stage build for optimal image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-prod.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements-prod.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN useradd -r -u 1000 covet

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/covet/.local

# Copy application code
COPY --chown=covet:covet . .

# Set PATH
ENV PATH=/home/covet/.local/bin:$PATH

# Switch to non-root user
USER covet

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # CovetPy Application
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: covet_app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://covet:password@db:5432/covet
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - LOG_LEVEL=INFO
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    networks:
      - covet_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL Database
  db:
    image: postgres:14-alpine
    container_name: covet_db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=covet
      - POSTGRES_USER=covet
      - POSTGRES_PASSWORD=password
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    networks:
      - covet_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U covet"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:6-alpine
    container_name: covet_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - covet_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx Reverse Proxy
  nginx:
    image: nginx:1.24-alpine
    container_name: covet_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
      - ./static:/var/www/static:ro
    depends_on:
      - app
    networks:
      - covet_network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  covet_network:
    driver: bridge
```

### 3. Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

---

## Kubernetes Deployment

### 1. Namespace

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: covet
  labels:
    name: covet
    environment: production
```

### 2. ConfigMap

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: covet-config
  namespace: covet
data:
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  DATABASE_POOL_SIZE: "20"
  WORKERS: "4"
```

### 3. Secrets

Create `k8s/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: covet-secrets
  namespace: covet
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key-here"
  JWT_SECRET_KEY: "your-jwt-secret-here"
  DATABASE_URL: "postgresql://user:password@postgres:5432/covet"
  REDIS_URL: "redis://redis:6379/0"
```

### 4. Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covet-app
  namespace: covet
  labels:
    app: covet
    tier: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: covet
      tier: backend
  template:
    metadata:
      labels:
        app: covet
        tier: backend
    spec:
      containers:
      - name: covet
        image: your-registry/covet:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        envFrom:
        - configMapRef:
            name: covet-config
        - secretRef:
            name: covet-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

### 5. Service

Create `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: covet-service
  namespace: covet
  labels:
    app: covet
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: covet
    tier: backend
```

### 6. Ingress

Create `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: covet-ingress
  namespace: covet
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
    secretName: covet-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: covet-service
            port:
              number: 80
```

### 7. Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get all -n covet

# View logs
kubectl logs -f deployment/covet-app -n covet

# Scale deployment
kubectl scale deployment covet-app --replicas=5 -n covet

# Check pod status
kubectl get pods -n covet -w
```

---

## Post-Deployment Validation

### 1. Health Check

```bash
# Check application health
curl https://yourdomain.com/health

# Expected response:
# {"status":"healthy","service":"CovetPy","version":"0.2.0"}
```

### 2. API Test

```bash
# Test API endpoint
curl https://yourdomain.com/api/users

# Test with authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://yourdomain.com/api/users/profile
```

### 3. WebSocket Test

```bash
# Install wscat
npm install -g wscat

# Test WebSocket connection
wscat -c wss://yourdomain.com/ws

# Send test message
> {"type":"ping"}
< {"type":"pong"}
```

### 4. Load Test

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 https://yourdomain.com/api/health

# Or use wrk
wrk -t4 -c100 -d30s https://yourdomain.com/api/health
```

### 5. Database Connection Test

```bash
# Connect to database
psql -h localhost -U covet_app -d covet_production

# Check tables
\dt

# Exit
\q
```

### 6. Check Logs

```bash
# Application logs
sudo journalctl -u covet -f

# Nginx access logs
sudo tail -f /var/log/nginx/covet_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/covet_error.log

# Application logs (if using file logging)
sudo tail -f /var/log/covet/app.log
```

---

## Production Checklist

### Security

- [ ] DEBUG mode is disabled (DEBUG=false)
- [ ] SECRET_KEY is generated and secure (32+ characters)
- [ ] JWT_SECRET_KEY is generated and different from SECRET_KEY
- [ ] Database password is strong and unique
- [ ] Redis password is set (if exposed)
- [ ] Environment variables are used for all secrets
- [ ] SSL/TLS certificates are installed and valid
- [ ] HTTPS is enforced (HTTP redirects to HTTPS)
- [ ] Security headers are configured in Nginx
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] File upload limits are set
- [ ] SQL injection protection is verified
- [ ] XSS protection is enabled
- [ ] CSRF protection is enabled

### Performance

- [ ] Database connection pooling is configured
- [ ] Redis caching is enabled and working
- [ ] Gzip compression is enabled
- [ ] Static files are served efficiently
- [ ] CDN is configured (optional)
- [ ] Database indexes are optimized
- [ ] Query performance is monitored
- [ ] Worker count is optimized (2-4 per CPU core)
- [ ] Keep-alive connections are enabled

### Monitoring

- [ ] Health check endpoint is working
- [ ] Prometheus metrics are enabled
- [ ] Application logs are centralized
- [ ] Error tracking is configured (Sentry, etc.)
- [ ] Uptime monitoring is set up
- [ ] Alerts are configured for critical issues
- [ ] Database performance is monitored
- [ ] Disk space monitoring is configured
- [ ] CPU and memory usage is monitored

### Backup & Recovery

- [ ] Database backups are scheduled
- [ ] Backup restoration is tested
- [ ] Point-in-time recovery is configured
- [ ] Application data backups are automated
- [ ] Backup retention policy is defined
- [ ] Disaster recovery plan is documented

### Operations

- [ ] Systemd service is enabled and running
- [ ] Service starts automatically on boot
- [ ] Graceful shutdown is configured
- [ ] Log rotation is configured
- [ ] Firewall rules are configured
- [ ] SSH access is secured (key-based only)
- [ ] Service account has minimal privileges
- [ ] Documentation is up to date

### Testing

- [ ] Smoke tests pass in production
- [ ] Load testing confirms performance requirements
- [ ] WebSocket connections work correctly
- [ ] API endpoints respond correctly
- [ ] Authentication flow works end-to-end
- [ ] Database migrations run successfully

---

## Next Steps

1. **Read the Operations Runbook**: `/docs/operations/RUNBOOK.md`
2. **Configure Monitoring**: `/docs/operations/MONITORING_GUIDE.md`
3. **Setup Backups**: `/docs/operations/BACKUP_GUIDE.md`
4. **Review Security Guide**: `/docs/SECURITY_GUIDE.md`
5. **API Documentation**: `/docs/api/README.md`
6. **Troubleshooting**: `/docs/TROUBLESHOOTING.md`

---

## Support

- **Documentation**: https://docs.covetpy.com
- **GitHub**: https://github.com/covetpy/covetpy
- **Issues**: https://github.com/covetpy/covetpy/issues
- **Community**: https://discord.gg/covetpy

---

**Note**: This is an educational framework. For production-critical applications, consider using battle-tested frameworks like FastAPI, Flask, or Django.
