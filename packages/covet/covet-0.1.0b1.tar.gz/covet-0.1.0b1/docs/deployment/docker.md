# Docker Deployment Guide

**Status: Educational Example - Not Production-Tested**

This guide shows how to containerize a CovetPy application using Docker. These are educational examples and have not been tested in production.

## Prerequisites

- Docker installed (https://docs.docker.com/get-docker/)
- Basic Docker knowledge
- A CovetPy application to deploy

## Basic Dockerfile

Create `Dockerfile` in your project root:

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Requirements File

Create `requirements.txt`:

```
# Core framework (install from source or PyPI when available)
covetpy[server]

# ASGI server
uvicorn[standard]==0.24.0

# Optional: Database
asyncpg==0.29.0  # PostgreSQL
aiomysql==0.2.0  # MySQL

# Optional: Caching
redis==5.0.1

# Optional: Production server
gunicorn==21.2.0
```

## Building and Running

### Build the Image

```bash
# Build image
docker build -t covetpy-app .

# Build with tag
docker build -t covetpy-app:v1.0.0 .
```

### Run the Container

```bash
# Basic run
docker run -p 8000:8000 covetpy-app

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/mydb \
  -e SECRET_KEY=your-secret-key \
  covetpy-app

# Run in detached mode
docker run -d -p 8000:8000 --name my-app covetpy-app

# View logs
docker logs -f my-app

# Stop container
docker stop my-app
```

## Docker Compose

For multi-container applications, create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-dev-secret-key}
    depends_on:
      - db
      - redis
    volumes:
      - ./:/app
    command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Using Docker Compose

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up --build
```

## Production Dockerfile

For production, use a multi-stage build:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run with gunicorn
CMD ["gunicorn", "app:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

## Environment Variables

Create `.env` file (DO NOT commit to version control):

```bash
# Application
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DATABASE_URL=postgresql://user:password@db:5432/database

# Redis
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET=another-secret-key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

Load in `docker-compose.yml`:

```yaml
services:
  web:
    env_file:
      - .env
```

## Health Check Endpoint

Add health check to your application:

```python
# app.py
from covet import CovetPy

app = CovetPy()

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/Kubernetes."""
    return {
        "status": "healthy",
        "service": "covetpy-app",
        "version": "1.0.0"
    }
```

## Volumes and Persistence

### Database Persistence

```yaml
services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
```

### Application Logs

```yaml
services:
  web:
    volumes:
      - ./logs:/app/logs
```

## Best Practices

### 1. Multi-Stage Builds

```dockerfile
# Reduce image size by using multi-stage builds
FROM python:3.11 as builder
# ... install dependencies

FROM python:3.11-slim
# ... copy only runtime dependencies
```

### 2. Layer Caching

```dockerfile
# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code last
COPY . .
```

### 3. Non-Root User

```dockerfile
# Always run as non-root user
RUN useradd -m appuser
USER appuser
```

### 4. Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8000/health || exit 1
```

### 5. Environment Variables

```dockerfile
# Use environment variables for configuration
ENV APP_ENV=production \
    LOG_LEVEL=info
```

## Limitations

**Important**: These Docker configurations are educational examples:

- Not tested under production load
- No comprehensive security hardening
- Basic monitoring and logging only
- Simplified health checks
- No advanced orchestration patterns

For production deployments:
- Use established deployment patterns
- Implement comprehensive monitoring
- Add proper security scanning
- Test thoroughly before deploying
- Consider managed services (AWS ECS, Google Cloud Run, etc.)

## See Also

- [Kubernetes Deployment](kubernetes.md)
- [AWS Deployment](aws.md)
- [Production Best Practices](production-checklist.md)
