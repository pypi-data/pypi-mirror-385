# CovetPy v1.0 - Production Deployment Guide

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployments](#cloud-deployments)
  - [AWS](#aws-deployment)
  - [Azure](#azure-deployment)
  - [GCP](#gcp-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Overview

CovetPy v1.0 provides comprehensive deployment options for production environments:

- **Docker**: Containerized deployment with <200MB images
- **Kubernetes**: Full orchestration with auto-scaling
- **AWS**: ECS, EKS, and Lambda support
- **Azure**: ACI and AKS support
- **GCP**: Cloud Run and GKE support

## Quick Start

### Prerequisites

- Python 3.9+
- Docker (for containerized deployment)
- kubectl (for Kubernetes deployment)
- Cloud CLI tools (aws-cli, az, gcloud)

### Installation

```bash
# Install CovetPy with production dependencies
pip install covetpy[production]

# Or install with all features
pip install covetpy[full]
```

### Running Locally

```bash
# Basic development server
python -m covet serve

# Production server with workers
uvicorn covet.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker Deployment

### Build Production Image

```bash
# Build the Docker image
docker build -t covetpy:1.0.0 -f Dockerfile .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e COVET_ENV=production \
  -e SECRET_KEY=your-secret-key \
  covetpy:1.0.0
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# With monitoring stack
docker-compose --profile monitoring up -d

# View logs
docker-compose logs -f web

# Stop all services
docker-compose down
```

### Multi-Stage Build Benefits

- **Small Image Size**: <200MB final image
- **Security**: Non-root user, minimal dependencies
- **Performance**: Rust extensions included
- **Health Checks**: Built-in health monitoring

## Kubernetes Deployment

### Using kubectl

```bash
# Deploy to Kubernetes
kubectl apply -f deploy/k8s/

# Check deployment status
kubectl get pods -n covetpy-production
kubectl get svc -n covetpy-production

# View logs
kubectl logs -f deployment/covetpy-web -n covetpy-production

# Scale deployment
kubectl scale deployment covetpy-web --replicas=5 -n covetpy-production
```

### Using Kustomize

```bash
# Deploy to development
kubectl apply -k k8s/overlays/development/

# Deploy to staging
kubectl apply -k k8s/overlays/staging/

# Deploy to production
kubectl apply -k k8s/overlays/production/

# Verify deployment
kubectl get all -n covetpy-production
```

### Horizontal Pod Autoscaling

The HPA is configured to scale based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 80%)
- Custom metrics (requests/sec, response time)

```bash
# Check HPA status
kubectl get hpa -n covetpy-production

# Describe HPA
kubectl describe hpa covetpy-hpa -n covetpy-production
```

### Health Checks

CovetPy provides multiple health check endpoints:

- `/health` - Simple health check
- `/health/live` - Liveness probe (for K8s)
- `/health/ready` - Readiness probe (for K8s)
- `/health/detailed` - Comprehensive health status

## Cloud Deployments

### AWS Deployment

#### AWS ECS (Fargate)

```bash
# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://cloud/aws/ecs-task-definition.json

# Create or update service
aws ecs create-service \
  --cli-input-json file://cloud/aws/ecs-service.json

# Check service status
aws ecs describe-services \
  --cluster covetpy-production \
  --services covetpy-web
```

#### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster -f cloud/aws/eks-cluster.yaml

# Deploy application
kubectl apply -k k8s/overlays/production/

# Configure ALB ingress
kubectl apply -f cloud/aws/alb-ingress.yaml
```

#### AWS Lambda (Serverless)

```bash
# Install Serverless Framework
npm install -g serverless

# Deploy to Lambda
cd cloud/aws/
serverless deploy --stage production

# View logs
serverless logs -f api --tail
```

### Azure Deployment

#### Azure Container Instances (ACI)

```bash
# Create resource group
az group create --name covetpy-rg --location eastus

# Deploy container
az deployment group create \
  --resource-group covetpy-rg \
  --template-file cloud/azure/aci-deployment.json

# Check status
az container show \
  --resource-group covetpy-rg \
  --name covetpy-web
```

#### Azure Kubernetes Service (AKS)

```bash
# Create AKS cluster
az aks create \
  --resource-group covetpy-rg \
  --name covetpy-cluster \
  --node-count 3 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials \
  --resource-group covetpy-rg \
  --name covetpy-cluster

# Deploy application
kubectl apply -f cloud/azure/aks-deployment.yaml
```

### GCP Deployment

#### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy covetpy-web \
  --image gcr.io/PROJECT_ID/covetpy:1.0.0 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Or use YAML configuration
gcloud run services replace cloud/gcp/cloudrun-service.yaml
```

#### Google Kubernetes Engine (GKE)

```bash
# Create GKE cluster
gcloud container clusters create covetpy-cluster \
  --region us-central1 \
  --num-nodes 3

# Get credentials
gcloud container clusters get-credentials covetpy-cluster

# Deploy application
kubectl apply -k k8s/overlays/production/
```

## Configuration

### Environment Variables

CovetPy uses environment variables for configuration:

```bash
# Application
COVET_ENV=production
COVET_LOG_LEVEL=info
COVET_WORKERS=4
COVET_HOST=0.0.0.0
COVET_PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Cache
REDIS_URL=redis://redis:6379/0
CACHE_BACKEND=redis
CACHE_DEFAULT_TIMEOUT=300

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
CORS_ALLOWED_ORIGINS=https://example.com

# Monitoring
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc
METRICS_ENABLED=true
```

### Secrets Management

#### Kubernetes Secrets

```bash
# Create secret from literal
kubectl create secret generic covetpy-secrets \
  --from-literal=SECRET_KEY=your-secret \
  --from-literal=DATABASE_PASSWORD=db-pass \
  -n covetpy-production

# Create secret from file
kubectl create secret generic covetpy-secrets \
  --from-env-file=.env.production \
  -n covetpy-production
```

#### AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
  --name covetpy/secret-key \
  --secret-string "your-secret-key"

# Update task definition to use secret
# (Already configured in ecs-task-definition.json)
```

## Monitoring

### Prometheus Metrics

CovetPy exports comprehensive metrics at `/metrics`:

```bash
# Access metrics
curl http://localhost:9090/metrics

# Query with PromQL
curl -G http://prometheus:9090/api/v1/query \
  --data-urlencode 'query=covetpy_http_requests_total'
```

### Grafana Dashboards

Pre-built dashboards are available in `monitoring/grafana/dashboards/`:

1. Import dashboard JSON into Grafana
2. Configure Prometheus datasource
3. View real-time metrics

### Health Monitoring

```bash
# Check health
curl http://localhost:8000/health

# Liveness check
curl http://localhost:8000/health/live

# Readiness check
curl http://localhost:8000/health/ready

# Detailed health
curl http://localhost:8000/health/detailed
```

### Logging

CovetPy supports structured JSON logging:

```bash
# Configure logging
export LOG_FORMAT=json
export LOG_OUTPUT=stdout
export SENTRY_DSN=your-sentry-dsn

# View logs in Kubernetes
kubectl logs -f deployment/covetpy-web -n covetpy-production

# View logs in Docker
docker logs -f covetpy-web
```

## Troubleshooting

### Common Issues

#### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n covetpy-production

# Check events
kubectl get events -n covetpy-production --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n covetpy-production --previous
```

#### Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug \
  --image=postgres:16 \
  --restart=Never \
  -- psql -h postgres -U covetuser -d covetdb

# Check connection pool
curl http://localhost:8000/health/detailed | jq '.checks[] | select(.name=="database")'
```

#### High Memory Usage

```bash
# Check resource usage
kubectl top pods -n covetpy-production

# Adjust resource limits
kubectl set resources deployment covetpy-web \
  --limits=memory=2Gi \
  -n covetpy-production
```

#### Performance Issues

```bash
# Check metrics
curl http://localhost:9090/metrics | grep covetpy_http_request_duration

# Enable profiling
export COVET_PROFILING=true

# Check slow queries
kubectl logs deployment/covetpy-web -n covetpy-production | grep "slow_query"
```

### Debug Mode

```bash
# Enable debug logging
kubectl set env deployment/covetpy-web \
  COVET_LOG_LEVEL=debug \
  -n covetpy-production

# Watch logs
kubectl logs -f deployment/covetpy-web -n covetpy-production
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/covetpy-web -n covetpy-production

# Rollback to specific revision
kubectl rollout undo deployment/covetpy-web \
  --to-revision=2 \
  -n covetpy-production

# Check rollout history
kubectl rollout history deployment/covetpy-web -n covetpy-production
```

## Performance Tuning

### Worker Configuration

```bash
# Calculate workers
workers = (2 * cpu_cores) + 1

# Set workers
export COVET_WORKERS=9  # for 4 CPU cores
```

### Database Optimization

```bash
# Connection pool sizing
export DATABASE_POOL_SIZE=20
export DATABASE_MAX_OVERFLOW=40
export DATABASE_POOL_TIMEOUT=30
```

### Caching

```bash
# Enable caching
export CACHE_BACKEND=redis
export CACHE_DEFAULT_TIMEOUT=300
export CACHE_KEY_PREFIX=covetpy
```

## Security Checklist

- [ ] Secrets stored in secure vault
- [ ] HTTPS/TLS configured
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] CSRF protection enabled
- [ ] Input validation active
- [ ] SQL injection protection verified
- [ ] XSS protection enabled
- [ ] Regular security scans scheduled

## Support

For issues and questions:
- GitHub Issues: https://github.com/covetpy/covetpy/issues
- Documentation: https://covetpy.readthedocs.io
- Discord: https://discord.gg/covetpy

---

**CovetPy v1.0** - Production Deployment Guide

Last Updated: October 10, 2025
