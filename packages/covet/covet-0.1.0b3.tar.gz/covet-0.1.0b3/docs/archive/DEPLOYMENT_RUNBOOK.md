# CovetPy Deployment Runbook

This comprehensive runbook provides step-by-step instructions for deploying and managing CovetPy applications across different environments and cloud providers.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Cloud Provider Specific](#cloud-provider-specific)
5. [Monitoring Setup](#monitoring-setup)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedures](#rollback-procedures)
8. [Scaling Guidelines](#scaling-guidelines)

## Quick Start

### Prerequisites
```bash
# Install CovetPy
pip install covetpy

# Verify installation
covet --version
```

### Create New Project
```bash
# Create a new project
covet new myapp --template fastapi --database postgresql --auth jwt --docker --monitoring

# Navigate to project
cd myapp

# Start development server
covet run
```

Your application will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Metrics: `http://localhost:8000/metrics`

## Local Development

### Using Docker Compose

1. **Start all services:**
```bash
docker-compose up -d
```

This starts:
- CovetPy application (port 8000)
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Prometheus monitoring (port 9090)
- Grafana dashboards (port 3000)

2. **View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f covet-app
```

3. **Stop services:**
```bash
docker-compose down
```

### Manual Setup

1. **Set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start database (PostgreSQL example):**
```bash
# Using Docker
docker run -d \
  --name postgres \
  -e POSTGRES_DB=covetpy \
  -e POSTGRES_USER=covetpy \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine
```

4. **Run application:**
```bash
covet run --host 0.0.0.0 --port 8000 --reload
```

## Production Deployment

### Build Production Image

```bash
# Build production Docker image
docker build -f Dockerfile.production -t covetpy-app:latest .

# Test the image
docker run -p 8000:8000 --env-file .env.production covetpy-app:latest
```

### Environment Configuration

Create production environment file (`.env.production`):

```bash
# Application Settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secure-secret-key-change-this
LOG_LEVEL=info

# Database (use actual production values)
DATABASE_URL=postgresql://user:password@prod-db-host:5432/covetpy

# Cache
REDIS_URL=redis://prod-redis-host:6379/0

# Security
ALLOWED_HOSTS=["https://api.yourdomain.com", "https://yourdomain.com"]

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc

# Performance
WORKERS=4
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50
```

### Health Checks

Ensure these endpoints are accessible:

- **Liveness:** `GET /health/live` - Returns 200 if application is alive
- **Readiness:** `GET /health/ready` - Returns 200 if ready to serve traffic
- **Health:** `GET /health` - Detailed health information

### Load Balancer Configuration

Example NGINX configuration:

```nginx
upstream covetpy_app {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://covetpy_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        proxy_pass http://covetpy_app/health;
        access_log off;
    }
    
    location /metrics {
        proxy_pass http://covetpy_app/metrics;
        # Restrict access to internal networks
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;
    }
}
```

## Cloud Provider Specific

### AWS Deployment

1. **ECS with Fargate:**
```bash
# Build and push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
docker tag covetpy-app:latest <account>.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest
docker push <account>.dkr.ecr.us-west-2.amazonaws.com/covetpy-app:latest

# Deploy using task definition
aws ecs update-service --cluster covetpy-cluster --service covetpy-service --force-new-deployment
```

2. **EKS Deployment:**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s-manifests/
kubectl rollout status deployment/covetpy-app -n covetpy
```

### GCP Deployment

1. **Cloud Run:**
```bash
# Deploy to Cloud Run
gcloud run deploy covetpy-app \
  --image gcr.io/your-project/covetpy-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

2. **GKE Deployment:**
```bash
# Deploy to GKE
kubectl apply -f k8s-manifests/
kubectl rollout status deployment/covetpy-app
```

### Azure Deployment

1. **Container Instances:**
```bash
# Deploy to ACI
az container create \
  --resource-group covetpy-rg \
  --name covetpy-app \
  --image covetpyregistry.azurecr.io/covetpy-app:latest \
  --cpu 2 \
  --memory 4
```

2. **App Service:**
```bash
# Deploy to App Service
az webapp config container set \
  --name covetpy-webapp \
  --resource-group covetpy-rg \
  --docker-custom-image-name covetpyregistry.azurecr.io/covetpy-app:latest
```

## Monitoring Setup

### Prometheus Configuration

1. **Start monitoring stack:**
```bash
# Using docker-compose
docker-compose -f docker-compose.monitoring.yml up -d
```

2. **Access monitoring tools:**
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (admin/admin)
- AlertManager: `http://localhost:9093`

### Key Metrics to Monitor

- **Request Rate:** `rate(covetpy_http_requests_total[5m])`
- **Response Time:** `histogram_quantile(0.95, rate(covetpy_http_request_duration_seconds_bucket[5m]))`
- **Error Rate:** `rate(covetpy_http_requests_total{status_code=~"5.."}[5m])`
- **Database Queries:** `rate(covetpy_database_queries_total[5m])`
- **Cache Hit Ratio:** `covetpy_cache_hit_ratio`

### Alerting Rules

Key alerts configured:
- High error rate (>5% 5xx responses)
- High response time (>2s 95th percentile)
- Application down
- Database connection issues
- High resource usage

### Log Aggregation

Configure structured logging:

```python
# In your application
import structlog

logger = structlog.get_logger(__name__)
logger.info("User registration", user_id=123, email="user@example.com")
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Symptoms:**
- Container exits immediately
- Health checks fail
- Connection refused errors

**Diagnostics:**
```bash
# Check container logs
docker logs <container-id>

# Check health endpoint
curl -f http://localhost:8000/health

# Verify environment variables
docker exec <container-id> env | grep -E "(DATABASE|REDIS|SECRET)"
```

**Solutions:**
- Verify database connectivity
- Check environment variables
- Ensure required services are running
- Check file permissions

#### 2. High Response Times

**Symptoms:**
- Slow API responses
- Timeouts
- High CPU/memory usage

**Diagnostics:**
```bash
# Check metrics
curl http://localhost:8000/metrics | grep duration

# Profile the application
docker exec <container-id> python -m py_spy top --pid 1

# Check database performance
# Monitor slow query logs
```

**Solutions:**
- Scale horizontally (add more instances)
- Optimize database queries
- Implement caching
- Check for memory leaks

#### 3. Database Connection Issues

**Symptoms:**
- "Connection refused" errors
- Database health checks failing
- Transaction timeouts

**Diagnostics:**
```bash
# Test database connectivity
docker exec <container-id> python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('DATABASE_URL')
    print('Connected successfully')
    await conn.close()
asyncio.run(test())
"

# Check connection pool
curl http://localhost:8000/metrics | grep database_connections
```

**Solutions:**
- Verify database URL and credentials
- Check network connectivity
- Adjust connection pool settings
- Monitor database resource usage

#### 4. Memory Issues

**Symptoms:**
- Out of memory errors
- Container restarts
- Slow performance

**Diagnostics:**
```bash
# Check memory usage
docker stats <container-id>

# Memory profiling
docker exec <container-id> python -m memory_profiler your_script.py
```

**Solutions:**
- Increase memory limits
- Fix memory leaks
- Optimize data structures
- Implement pagination

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set environment variable
export DEBUG=true
export LOG_LEVEL=debug

# Restart application
covet run --reload
```

**Warning:** Never enable debug mode in production!

## Rollback Procedures

### Container-based Rollback

```bash
# Tag current version
docker tag covetpy-app:latest covetpy-app:rollback

# Roll back to previous version
docker pull covetpy-app:previous-version
docker tag covetpy-app:previous-version covetpy-app:latest

# Restart containers
docker-compose up -d covet-app
```

### Kubernetes Rollback

```bash
# Check rollout history
kubectl rollout history deployment/covetpy-app

# Rollback to previous version
kubectl rollout undo deployment/covetpy-app

# Rollback to specific revision
kubectl rollout undo deployment/covetpy-app --to-revision=2

# Check rollback status
kubectl rollout status deployment/covetpy-app
```

### Database Migration Rollback

```bash
# Check current migration
docker exec <container-id> alembic current

# Rollback migration
docker exec <container-id> alembic downgrade -1

# Rollback to specific revision
docker exec <container-id> alembic downgrade <revision-id>
```

## Scaling Guidelines

### Horizontal Scaling

#### Docker Compose
```bash
# Scale application instances
docker-compose up -d --scale covet-app=3
```

#### Kubernetes
```bash
# Scale deployment
kubectl scale deployment covetpy-app --replicas=5

# Horizontal Pod Autoscaler
kubectl autoscale deployment covetpy-app --cpu-percent=70 --min=2 --max=10
```

### Vertical Scaling

#### Adjust resource limits:

```yaml
# docker-compose.yml
services:
  covet-app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

#### Kubernetes:
```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Database Scaling

#### Read Replicas:
```bash
# Configure read-only database connections
DATABASE_READ_URL=postgresql://readonly-user:password@read-replica:5432/covetpy
```

#### Connection Pooling:
```python
# Adjust pool settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### Cache Scaling

#### Redis Cluster:
```bash
# Configure Redis cluster
REDIS_CLUSTER_NODES=redis-1:6379,redis-2:6379,redis-3:6379
```

### Load Testing

```bash
# Using k6
k6 run benchmarks/k6/covet-load-test.js

# Using locust
locust -f benchmarks/performance/locust-performance.py --host=http://localhost:8000
```

### Performance Targets

- **Response Time:** 95th percentile < 500ms
- **Throughput:** > 1000 requests/second
- **Error Rate:** < 0.1%
- **Availability:** > 99.9%

### Monitoring Scaling Events

```bash
# Monitor key metrics during scaling
watch -n 5 'curl -s http://localhost:8000/metrics | grep -E "(http_requests|memory|cpu)"'
```

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Validate all input data
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Implement proper authentication/authorization
- [ ] Keep dependencies updated
- [ ] Use security headers
- [ ] Regular security audits
- [ ] Monitor for suspicious activity
- [ ] Backup encryption keys

## Backup Procedures

### Database Backup
```bash
# PostgreSQL backup
pg_dump -h localhost -U covetpy -d covetpy > backup.sql

# Automated backup script
0 2 * * * /usr/local/bin/backup-database.sh
```

### Configuration Backup
```bash
# Backup configuration files
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env* docker-compose*.yml k8s-manifests/
```

## Disaster Recovery

### Recovery Time Objectives (RTO)
- **Critical systems:** 15 minutes
- **Non-critical systems:** 1 hour

### Recovery Point Objectives (RPO)
- **Database:** 5 minutes
- **Configuration:** 1 hour

### Recovery Procedures

1. **Assess the situation**
2. **Activate disaster recovery plan**
3. **Restore from backups**
4. **Verify system functionality**
5. **Update monitoring and alerting**
6. **Document lessons learned**

This runbook should be regularly updated and tested to ensure it remains accurate and effective.