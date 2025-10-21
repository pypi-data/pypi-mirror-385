# CovetPy Deployment Quick Start

**5-Minute Deployment Guide**

## Option 1: Docker Compose (Fastest)

```bash
# Clone repository
git clone https://github.com/covetpy/covetpy.git
cd covetpy

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f covetpy-app

# Access application
curl http://localhost:8000/health
```

**Deployed Services**:
- Application: http://localhost:8000
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000 (admin/admin)
- Jaeger: http://localhost:16686
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## Option 2: Kubernetes (Recommended for Production)

```bash
# Apply manifests
kubectl apply -f kubernetes/base/namespace.yaml
kubectl create secret generic covetpy-secrets --from-env-file=.env
kubectl apply -f kubernetes/base/

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s \
  deployment/covetpy-api -n covetpy

# Check status
kubectl get pods -n covetpy
kubectl logs -f deployment/covetpy-api -n covetpy

# Access application (port-forward for testing)
kubectl port-forward svc/covetpy-service 8000:8000 -n covetpy
curl http://localhost:8000/health
```

---

## Option 3: AWS (Production with Terraform)

```bash
# Configure AWS CLI
aws configure

# Initialize Terraform
cd terraform/aws
terraform init

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
region = "us-east-1"
environment = "production"
app_name = "covetpy"
domain_name = "api.covetpy.com"
EOF

# Deploy infrastructure
terraform plan
terraform apply

# Application will be available at your ALB DNS name
# Check outputs for URLs
terraform output alb_dns_name
```

---

## Quick Verification

```bash
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:9090/metrics

# Expected response
{
  "status": "healthy",
  "uptime_seconds": 123.45,
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"}
  }
}
```

---

## Next Steps

1. Configure monitoring alerts
2. Set up backup automation
3. Run load tests
4. Review security checklist
5. Configure CI/CD pipeline

See `/Users/vipin/Downloads/NeutrinoPy/SPRINT8_PRODUCTION_READY_COMPLETE.md` for full documentation.
