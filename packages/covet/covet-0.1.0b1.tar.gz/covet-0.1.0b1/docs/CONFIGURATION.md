# CovetPy Configuration Reference

**Version:** 0.2.0-sprint1
**Last Updated:** 2025-10-11

Complete reference for all configuration options in CovetPy applications.

## Table of Contents

1. [Configuration Files](#configuration-files)
2. [Environment Variables](#environment-variables)
3. [Application Settings](#application-settings)
4. [Database Configuration](#database-configuration)
5. [Security Settings](#security-settings)
6. [Performance Tuning](#performance-tuning)
7. [Logging Configuration](#logging-configuration)
8. [Monitoring & Metrics](#monitoring--metrics)
9. [Feature Flags](#feature-flags)
10. [Third-Party Integrations](#third-party-integrations)

---

## Configuration Files

### Configuration Hierarchy

CovetPy loads configuration in the following order (later values override earlier):

1. **Default values** (hardcoded in application)
2. **Configuration file** (`config.py` or `config.yaml`)
3. **Environment-specific config** (`production.env`, `development.env`)
4. **Environment variables** (OS environment)
5. **Command-line arguments** (if applicable)

### Environment File Location

```bash
# Production
/etc/covet/production.env

# Development
.env or .env.development

# Testing
.env.test
```

### Loading Configuration

```python
from covet.config import Config, load_config

# Method 1: Load from environment file
config = load_config('/etc/covet/production.env')

# Method 2: Create config object
config = Config(
    DEBUG=False,
    SECRET_KEY='your-secret-key',
    DATABASE_URL='postgresql://user:pass@localhost/db'
)

# Method 3: Load from dict
config = Config.from_dict({
    'DEBUG': False,
    'SECRET_KEY': 'your-secret-key'
})
```

---

## Environment Variables

### Application Settings

#### ENVIRONMENT
- **Type:** string
- **Default:** `"development"`
- **Options:** `development`, `production`, `testing`, `staging`
- **Description:** Application environment

```bash
ENVIRONMENT=production
```

#### DEBUG
- **Type:** boolean
- **Default:** `false`
- **Description:** Enable debug mode (NEVER enable in production)

```bash
DEBUG=false
```

**Warning:** Setting `DEBUG=true` in production:
- Exposes sensitive information
- Disables security features
- Reduces performance
- Shows stack traces to users

#### APP_NAME
- **Type:** string
- **Default:** `"CovetPy"`
- **Description:** Application name for logging and monitoring

```bash
APP_NAME="My Application"
```

#### HOST
- **Type:** string
- **Default:** `"127.0.0.1"`
- **Description:** Host to bind server to

```bash
HOST=0.0.0.0  # Listen on all interfaces
```

#### PORT
- **Type:** integer
- **Default:** `8000`
- **Range:** `1-65535`
- **Description:** Port to bind server to

```bash
PORT=8000
```

#### WORKERS
- **Type:** integer
- **Default:** `4`
- **Recommended:** `(2 * CPU_CORES) + 1`
- **Description:** Number of worker processes

```bash
WORKERS=9  # For 4 CPU cores
```

---

### Security Settings

#### SECRET_KEY
- **Type:** string
- **Required:** Yes
- **Min Length:** 32 characters
- **Description:** Secret key for cryptographic operations

```bash
SECRET_KEY=your-secret-key-here-minimum-32-characters
```

**Generate secure key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### JWT_SECRET_KEY
- **Type:** string
- **Required:** Yes (if using JWT)
- **Min Length:** 32 characters
- **Description:** Secret key for JWT tokens

```bash
JWT_SECRET_KEY=your-jwt-secret-here-different-from-secret-key
```

#### JWT_ALGORITHM
- **Type:** string
- **Default:** `"HS256"`
- **Options:** `HS256`, `HS384`, `HS512`, `RS256`, `RS384`, `RS512`
- **Description:** JWT signing algorithm

```bash
JWT_ALGORITHM=HS256
```

#### JWT_ACCESS_TOKEN_EXPIRE_MINUTES
- **Type:** integer
- **Default:** `30`
- **Range:** `1-1440` (1 day)
- **Description:** Access token expiration in minutes

```bash
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### JWT_REFRESH_TOKEN_EXPIRE_DAYS
- **Type:** integer
- **Default:** `7`
- **Range:** `1-90`
- **Description:** Refresh token expiration in days

```bash
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### ALLOWED_HOSTS
- **Type:** comma-separated list
- **Default:** `"*"` (allow all)
- **Description:** Allowed host headers

```bash
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

#### CORS_ORIGINS
- **Type:** comma-separated list
- **Default:** `"*"` (allow all)
- **Description:** Allowed CORS origins

```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### CORS_ALLOW_CREDENTIALS
- **Type:** boolean
- **Default:** `false`
- **Description:** Allow credentials in CORS requests

```bash
CORS_ALLOW_CREDENTIALS=true
```

---

### Database Configuration

#### DATABASE_URL
- **Type:** string (connection URI)
- **Required:** Yes
- **Format:** `dialect://username:password@host:port/database`
- **Description:** Database connection URL

```bash
# PostgreSQL
DATABASE_URL=postgresql://covet_app:password@localhost:5432/covet_production

# MySQL
DATABASE_URL=mysql://covet_app:password@localhost:3306/covet_production

# SQLite (dev only)
DATABASE_URL=sqlite:///./covet.db
```

#### DATABASE_POOL_SIZE
- **Type:** integer
- **Default:** `20`
- **Range:** `5-100`
- **Description:** Database connection pool size

```bash
DATABASE_POOL_SIZE=20
```

#### DATABASE_MAX_OVERFLOW
- **Type:** integer
- **Default:** `10`
- **Range:** `0-50`
- **Description:** Maximum overflow connections beyond pool size

```bash
DATABASE_MAX_OVERFLOW=10
```

#### DATABASE_POOL_TIMEOUT
- **Type:** integer (seconds)
- **Default:** `30`
- **Range:** `10-300`
- **Description:** Timeout waiting for connection from pool

```bash
DATABASE_POOL_TIMEOUT=30
```

#### DATABASE_POOL_RECYCLE
- **Type:** integer (seconds)
- **Default:** `3600` (1 hour)
- **Range:** `300-7200`
- **Description:** Recycle connections after N seconds

```bash
DATABASE_POOL_RECYCLE=3600
```

#### DATABASE_ECHO
- **Type:** boolean
- **Default:** `false`
- **Description:** Log all SQL statements

```bash
DATABASE_ECHO=false  # Enable for debugging
```

#### DATABASE_POOL_PRE_PING
- **Type:** boolean
- **Default:** `true`
- **Description:** Test connections before using

```bash
DATABASE_POOL_PRE_PING=true
```

---

### Redis Configuration

#### REDIS_URL
- **Type:** string (connection URI)
- **Default:** `None`
- **Format:** `redis://[:password@]host:port[/db]`
- **Description:** Redis connection URL

```bash
REDIS_URL=redis://localhost:6379/0
# With password
REDIS_URL=redis://:password@localhost:6379/0
```

#### REDIS_PASSWORD
- **Type:** string
- **Default:** `None`
- **Description:** Redis password (alternative to URL)

```bash
REDIS_PASSWORD=your-redis-password
```

#### REDIS_DB
- **Type:** integer
- **Default:** `0`
- **Range:** `0-15`
- **Description:** Redis database number

```bash
REDIS_DB=0
```

#### REDIS_MAX_CONNECTIONS
- **Type:** integer
- **Default:** `50`
- **Range:** `10-1000`
- **Description:** Maximum Redis connections

```bash
REDIS_MAX_CONNECTIONS=50
```

#### CACHE_ENABLED
- **Type:** boolean
- **Default:** `false`
- **Description:** Enable caching

```bash
CACHE_ENABLED=true
```

#### CACHE_DEFAULT_TTL
- **Type:** integer (seconds)
- **Default:** `300` (5 minutes)
- **Range:** `60-3600`
- **Description:** Default cache TTL

```bash
CACHE_DEFAULT_TTL=300
```

---

### Performance Settings

#### MAX_UPLOAD_SIZE
- **Type:** integer (bytes)
- **Default:** `10485760` (10MB)
- **Range:** `1048576-104857600` (1MB-100MB)
- **Description:** Maximum file upload size

```bash
MAX_UPLOAD_SIZE=10485760  # 10MB
```

#### UPLOAD_DIR
- **Type:** string (path)
- **Default:** `./uploads`
- **Description:** Upload directory path

```bash
UPLOAD_DIR=/opt/covet/uploads
```

#### ALLOWED_UPLOAD_EXTENSIONS
- **Type:** comma-separated list
- **Default:** `jpg,jpeg,png,gif,pdf`
- **Description:** Allowed file extensions

```bash
ALLOWED_UPLOAD_EXTENSIONS=jpg,jpeg,png,gif,pdf,txt,doc,docx
```

#### RATE_LIMIT_ENABLED
- **Type:** boolean
- **Default:** `true`
- **Description:** Enable rate limiting

```bash
RATE_LIMIT_ENABLED=true
```

#### RATE_LIMIT_PER_MINUTE
- **Type:** integer
- **Default:** `60`
- **Range:** `1-1000`
- **Description:** Requests per minute per IP

```bash
RATE_LIMIT_PER_MINUTE=60
```

#### RATE_LIMIT_PER_HOUR
- **Type:** integer
- **Default:** `1000`
- **Range:** `100-100000`
- **Description:** Requests per hour per IP

```bash
RATE_LIMIT_PER_HOUR=1000
```

---

### Session Configuration

#### SESSION_BACKEND
- **Type:** string
- **Default:** `"memory"`
- **Options:** `memory`, `redis`, `database`
- **Description:** Session storage backend

```bash
SESSION_BACKEND=redis
```

#### SESSION_COOKIE_NAME
- **Type:** string
- **Default:** `"covet_session"`
- **Description:** Session cookie name

```bash
SESSION_COOKIE_NAME=covet_session
```

#### SESSION_COOKIE_SECURE
- **Type:** boolean
- **Default:** `true`
- **Description:** Secure flag on session cookie

```bash
SESSION_COOKIE_SECURE=true
```

#### SESSION_COOKIE_HTTPONLY
- **Type:** boolean
- **Default:** `true`
- **Description:** HTTP-only flag on session cookie

```bash
SESSION_COOKIE_HTTPONLY=true
```

#### SESSION_COOKIE_SAMESITE
- **Type:** string
- **Default:** `"lax"`
- **Options:** `strict`, `lax`, `none`
- **Description:** SameSite attribute on session cookie

```bash
SESSION_COOKIE_SAMESITE=lax
```

#### SESSION_MAX_AGE
- **Type:** integer (seconds)
- **Default:** `86400` (24 hours)
- **Range:** `3600-604800` (1 hour - 7 days)
- **Description:** Session expiration time

```bash
SESSION_MAX_AGE=86400
```

---

### Logging Configuration

#### LOG_LEVEL
- **Type:** string
- **Default:** `"INFO"`
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Description:** Logging level

```bash
LOG_LEVEL=INFO
```

#### LOG_FORMAT
- **Type:** string
- **Default:** `"text"`
- **Options:** `text`, `json`
- **Description:** Log format

```bash
LOG_FORMAT=json
```

#### LOG_FILE
- **Type:** string (path)
- **Default:** `None` (stdout only)
- **Description:** Log file path

```bash
LOG_FILE=/var/log/covet/app.log
```

#### ACCESS_LOG
- **Type:** string (path)
- **Default:** `None`
- **Description:** Access log file path

```bash
ACCESS_LOG=/var/log/covet/access.log
```

#### ERROR_LOG
- **Type:** string (path)
- **Default:** `None`
- **Description:** Error log file path

```bash
ERROR_LOG=/var/log/covet/error.log
```

#### LOG_ROTATION_ENABLED
- **Type:** boolean
- **Default:** `true`
- **Description:** Enable log rotation

```bash
LOG_ROTATION_ENABLED=true
```

#### LOG_MAX_SIZE
- **Type:** integer (MB)
- **Default:** `100`
- **Range:** `10-1000`
- **Description:** Maximum log file size before rotation

```bash
LOG_MAX_SIZE=100
```

#### LOG_BACKUP_COUNT
- **Type:** integer
- **Default:** `10`
- **Range:** `1-100`
- **Description:** Number of backup log files to keep

```bash
LOG_BACKUP_COUNT=10
```

---

### Monitoring & Metrics

#### PROMETHEUS_ENABLED
- **Type:** boolean
- **Default:** `true`
- **Description:** Enable Prometheus metrics

```bash
PROMETHEUS_ENABLED=true
```

#### PROMETHEUS_PORT
- **Type:** integer
- **Default:** `9090`
- **Range:** `1024-65535`
- **Description:** Prometheus metrics port

```bash
PROMETHEUS_PORT=9090
```

#### HEALTH_CHECK_PATH
- **Type:** string
- **Default:** `"/health"`
- **Description:** Health check endpoint path

```bash
HEALTH_CHECK_PATH=/health
```

#### METRICS_PATH
- **Type:** string
- **Default:** `"/metrics"`
- **Description:** Metrics endpoint path

```bash
METRICS_PATH=/metrics
```

#### SENTRY_DSN
- **Type:** string
- **Default:** `None`
- **Description:** Sentry error tracking DSN

```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

#### SENTRY_ENVIRONMENT
- **Type:** string
- **Default:** `None`
- **Description:** Sentry environment tag

```bash
SENTRY_ENVIRONMENT=production
```

#### SENTRY_TRACES_SAMPLE_RATE
- **Type:** float
- **Default:** `0.1`
- **Range:** `0.0-1.0`
- **Description:** Sentry trace sampling rate

```bash
SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

### Backup Configuration

#### BACKUP_ENABLED
- **Type:** boolean
- **Default:** `false`
- **Description:** Enable automatic backups

```bash
BACKUP_ENABLED=true
```

#### BACKUP_DIR
- **Type:** string (path)
- **Default:** `./backups`
- **Description:** Backup directory path

```bash
BACKUP_DIR=/opt/covet/backups
```

#### BACKUP_RETENTION_DAYS
- **Type:** integer
- **Default:** `30`
- **Range:** `1-365`
- **Description:** Days to retain backups

```bash
BACKUP_RETENTION_DAYS=30
```

#### BACKUP_SCHEDULE
- **Type:** string (cron format)
- **Default:** `"0 2 * * *"` (daily at 2 AM)
- **Description:** Backup schedule

```bash
BACKUP_SCHEDULE="0 2 * * *"
```

---

### Email Configuration

#### SMTP_HOST
- **Type:** string
- **Default:** `None`
- **Description:** SMTP server host

```bash
SMTP_HOST=smtp.gmail.com
```

#### SMTP_PORT
- **Type:** integer
- **Default:** `587`
- **Options:** `25`, `465`, `587`
- **Description:** SMTP server port

```bash
SMTP_PORT=587
```

#### SMTP_USER
- **Type:** string
- **Default:** `None`
- **Description:** SMTP username

```bash
SMTP_USER=your-email@gmail.com
```

#### SMTP_PASSWORD
- **Type:** string
- **Default:** `None`
- **Description:** SMTP password

```bash
SMTP_PASSWORD=your-app-password
```

#### SMTP_FROM
- **Type:** string (email)
- **Default:** `None`
- **Description:** From email address

```bash
SMTP_FROM=noreply@yourdomain.com
```

#### SMTP_TLS
- **Type:** boolean
- **Default:** `true`
- **Description:** Use TLS for SMTP

```bash
SMTP_TLS=true
```

---

### Feature Flags

#### ENABLE_API_DOCS
- **Type:** boolean
- **Default:** `false`
- **Description:** Enable API documentation endpoints

```bash
ENABLE_API_DOCS=false  # Disable in production
```

#### ENABLE_GRAPHQL_PLAYGROUND
- **Type:** boolean
- **Default:** `false`
- **Description:** Enable GraphQL Playground

```bash
ENABLE_GRAPHQL_PLAYGROUND=false  # Disable in production
```

#### ENABLE_DEBUG_TOOLBAR
- **Type:** boolean
- **Default:** `false`
- **Description:** Enable debug toolbar

```bash
ENABLE_DEBUG_TOOLBAR=false  # Disable in production
```

#### ENABLE_WEBSOCKETS
- **Type:** boolean
- **Default:** `true`
- **Description:** Enable WebSocket support

```bash
ENABLE_WEBSOCKETS=true
```

#### ENABLE_RATE_LIMITING
- **Type:** boolean
- **Default:** `true`
- **Description:** Enable rate limiting

```bash
ENABLE_RATE_LIMITING=true
```

---

## Configuration Examples

### Development Configuration

```bash
# .env.development

ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database (SQLite for local dev)
DATABASE_URL=sqlite:///./dev.db

# Simple secret keys (dev only!)
SECRET_KEY=dev-secret-key-not-for-production
JWT_SECRET_KEY=dev-jwt-secret-key

# Allow all CORS
CORS_ORIGINS=*

# Enable dev features
ENABLE_API_DOCS=true
ENABLE_GRAPHQL_PLAYGROUND=true
ENABLE_DEBUG_TOOLBAR=true
```

### Production Configuration

```bash
# /etc/covet/production.env

# Application
ENVIRONMENT=production
DEBUG=false
APP_NAME=CovetPy Production
HOST=0.0.0.0
PORT=8000
WORKERS=9

# Security
SECRET_KEY=super-secure-random-string-32-chars-minimum
JWT_SECRET_KEY=another-secure-random-string-different
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# Database
DATABASE_URL=postgresql://covet_app:secure_password@localhost:5432/covet_production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=300

# Session
SESSION_BACKEND=redis
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax
SESSION_MAX_AGE=86400

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/covet/app.log
ACCESS_LOG=/var/log/covet/access.log
ERROR_LOG=/var/log/covet/error.log

# Monitoring
PROMETHEUS_ENABLED=true
HEALTH_CHECK_PATH=/health
METRICS_PATH=/metrics

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Backups
BACKUP_ENABLED=true
BACKUP_DIR=/opt/covet/backups
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"

# Feature Flags
ENABLE_API_DOCS=false
ENABLE_GRAPHQL_PLAYGROUND=false
ENABLE_DEBUG_TOOLBAR=false
```

### Testing Configuration

```bash
# .env.test

ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=WARNING

# In-memory database for tests
DATABASE_URL=sqlite:///:memory:

# Test secret keys
SECRET_KEY=test-secret-key
JWT_SECRET_KEY=test-jwt-secret-key

# Disable external services
CACHE_ENABLED=false
REDIS_URL=

# Fast tests
SESSION_BACKEND=memory
```

---

## Validation

### Configuration Validation Script

```python
#!/usr/bin/env python3
"""Validate CovetPy configuration."""

import os
import sys
from urllib.parse import urlparse

def validate_config():
    """Validate all configuration settings."""
    errors = []
    warnings = []

    # Check required variables
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
    ]

    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required variable: {var}")

    # Check SECRET_KEY length
    secret_key = os.getenv('SECRET_KEY', '')
    if len(secret_key) < 32:
        errors.append("SECRET_KEY must be at least 32 characters")

    # Check DEBUG in production
    if os.getenv('ENVIRONMENT') == 'production' and os.getenv('DEBUG', '').lower() == 'true':
        errors.append("DEBUG must be false in production!")

    # Validate DATABASE_URL format
    db_url = os.getenv('DATABASE_URL', '')
    try:
        parsed = urlparse(db_url)
        if not parsed.scheme:
            errors.append("Invalid DATABASE_URL format")
        elif parsed.scheme == 'sqlite' and os.getenv('ENVIRONMENT') == 'production':
            warnings.append("SQLite not recommended for production")
    except Exception as e:
        errors.append(f"Invalid DATABASE_URL: {e}")

    # Check numeric ranges
    try:
        workers = int(os.getenv('WORKERS', 4))
        if workers < 1 or workers > 32:
            warnings.append(f"WORKERS={workers} may not be optimal")
    except ValueError:
        errors.append("WORKERS must be an integer")

    # Print results
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  ❌ {error}")

    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

    if not errors and not warnings:
        print("✅ Configuration is valid")
        return 0

    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(validate_config())
```

**Usage:**
```bash
# Load environment and validate
set -a
source /etc/covet/production.env
set +a
python validate_config.py
```

---

## Best Practices

1. **Never commit secrets to git**
   - Use `.env` files (add to `.gitignore`)
   - Use environment variables
   - Use secret management tools

2. **Use strong secret keys**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Separate configs per environment**
   - `production.env`
   - `development.env`
   - `testing.env`

4. **Validate configuration on startup**
   - Check required variables
   - Validate formats
   - Test database connection

5. **Document environment variables**
   - Provide example `.env.example`
   - Document in README
   - Include in deployment guide

6. **Use type hints**
   ```python
   from typing import Optional
   from pydantic import BaseSettings

   class Config(BaseSettings):
       DEBUG: bool = False
       DATABASE_URL: str
       REDIS_URL: Optional[str] = None
   ```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-11
