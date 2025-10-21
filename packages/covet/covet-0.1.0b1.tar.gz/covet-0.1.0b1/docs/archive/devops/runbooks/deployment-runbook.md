# Deployment Runbook

## Overview

This runbook covers all deployment procedures for CovetPy, from development to production environments. It includes standard deployments, rollbacks, emergency procedures, and troubleshooting guides.

## Deployment Environments

### Environment Overview

| Environment | Purpose | URL | Auto-Deploy | Approval Required |
|-------------|---------|-----|-------------|-------------------|
| **Development** | Feature development | https://dev.covet.example.com | Yes (feature branches) | No |
| **Staging** | Integration testing | https://staging.covet.example.com | Yes (main branch) | No |
| **Production** | Live service | https://covet.example.com | Yes (tags) | Yes |

### Environment Configuration

```yaml
# deployment-environments.yml
environments:
  development:
    cluster: "covet-dev-cluster"
    namespace: "covet-dev"
    replicas: 1
    resources:
      requests:
        cpu: "100m"
        memory: "256Mi"
    database: "covet_dev"
    
  staging:
    cluster: "covet-staging-cluster"
    namespace: "covet-staging"
    replicas: 2
    resources:
      requests:
        cpu: "200m"
        memory: "512Mi"
    database: "covet_staging"
    
  production:
    cluster: "covet-prod-cluster"
    namespace: "covet"
    replicas: 5
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
    database: "covet_prod"
```

## Standard Deployment Process

### Pre-Deployment Checklist

#### Development Team
- [ ] Code review completed and approved
- [ ] All tests passing (unit, integration, end-to-end)
- [ ] Security scans passed
- [ ] Performance tests passed
- [ ] Documentation updated
- [ ] Database migrations tested (if applicable)

#### SRE Team
- [ ] Infrastructure capacity checked
- [ ] Monitoring and alerts configured
- [ ] Rollback plan prepared
- [ ] Deployment window scheduled
- [ ] Stakeholders notified

### Deployment Steps

#### 1. Preparation Phase
```bash
# Verify deployment readiness
./scripts/pre-deployment-check.sh

# Check cluster health
kubectl cluster-info
kubectl get nodes -o wide
kubectl top nodes

# Verify previous deployment is stable
kubectl rollout status deployment/covet-app -n covet

# Check resource availability
kubectl describe hpa covet-hpa -n covet
```

#### 2. Deployment Execution

##### Automated Deployment (GitOps)
```bash
# Tag for production deployment
git tag -a v1.2.3 -m "Release v1.2.3: Add new user management features"
git push origin v1.2.3

# Monitor deployment progress
kubectl get deployment covet-app -n covet -w

# Watch pods rolling update
kubectl get pods -n covet -l app=covet -w
```

##### Manual Deployment (Emergency)
```bash
# Build and push image
docker build -t ghcr.io/covet/covet:v1.2.3 .
docker push ghcr.io/covet/covet:v1.2.3

# Update deployment
kubectl set image deployment/covet-app \
  covet=ghcr.io/covet/covet:v1.2.3 \
  -n covet

# Monitor rollout
kubectl rollout status deployment/covet-app -n covet --timeout=600s
```

#### 3. Post-Deployment Verification

##### Health Checks
```bash
# Application health check
curl -f https://covet.example.com/health

# Detailed service status
curl -s https://covet.example.com/health | jq .

# Database connectivity
kubectl exec -it deployment/covet-app -n covet -- \
  python -c "from covet.database import check_connection; print(check_connection())"

# External dependencies
curl -f https://covet.example.com/health/dependencies
```

##### Performance Verification
```bash
# Response time check
time curl -s https://covet.example.com/api/v1/users > /dev/null

# Load test (light)
hey -n 100 -c 10 https://covet.example.com/health

# Memory usage check
kubectl top pods -n covet -l app=covet
```

##### Functional Testing
```bash
# Run smoke tests
pytest tests/smoke/ -v --env=production

# API endpoint verification
./scripts/api-verification.sh

# User journey tests
./scripts/user-journey-tests.sh
```

## Blue-Green Deployment

### Overview
Blue-green deployment minimizes downtime and risk by running two identical production environments.

### Procedure

#### 1. Prepare Green Environment
```bash
# Create green deployment
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covet-app-green
  namespace: covet
spec:
  replicas: 5
  selector:
    matchLabels:
      app: covet
      version: green
  template:
    metadata:
      labels:
        app: covet
        version: green
    spec:
      containers:
      - name: covet
        image: ghcr.io/covet/covet:v1.2.3
        # ... rest of container spec
EOF

# Wait for green deployment to be ready
kubectl rollout status deployment/covet-app-green -n covet
```

#### 2. Test Green Environment
```bash
# Create temporary service for testing
kubectl expose deployment covet-app-green \
  --name=covet-green-test \
  --port=80 \
  --target-port=8000 \
  -n covet

# Port forward for testing
kubectl port-forward svc/covet-green-test 8080:80 -n covet &

# Run tests against green environment
curl -f http://localhost:8080/health
pytest tests/smoke/ --base-url=http://localhost:8080

# Clean up test service
kubectl delete svc covet-green-test -n covet
```

#### 3. Switch Traffic to Green
```bash
# Update service selector to green
kubectl patch service covet-service -n covet \
  --patch '{"spec":{"selector":{"version":"green"}}}'

# Verify traffic switch
kubectl get endpoints covet-service -n covet
```

#### 4. Monitor and Cleanup
```bash
# Monitor green environment
watch kubectl get pods -n covet -l version=green

# After successful verification, cleanup blue
kubectl delete deployment covet-app-blue -n covet

# Rename green to primary
kubectl patch deployment covet-app-green -n covet \
  --patch '{"metadata":{"name":"covet-app"}}'
```

## Canary Deployment

### Overview
Canary deployment gradually shifts traffic to the new version while monitoring key metrics.

### Procedure

#### 1. Deploy Canary Version
```bash
# Deploy canary with minimal replicas
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: covet-app-canary
  namespace: covet
spec:
  replicas: 1
  selector:
    matchLabels:
      app: covet
      version: canary
  template:
    metadata:
      labels:
        app: covet
        version: canary
    spec:
      containers:
      - name: covet
        image: ghcr.io/covet/covet:v1.2.3
        # ... rest of container spec
EOF
```

#### 2. Configure Traffic Split (Istio)
```yaml
# traffic-split.yml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: covet-canary
  namespace: covet
spec:
  hosts:
  - covet.example.com
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: covet-service
        subset: canary
  - route:
    - destination:
        host: covet-service
        subset: stable
      weight: 95
    - destination:
        host: covet-service
        subset: canary
      weight: 5
```

#### 3. Monitor Canary Metrics
```bash
# Monitor error rates
kubectl exec -it deployment/prometheus -n monitoring -- \
  promtool query instant 'rate(http_requests_total{version="canary",code=~"5.."}[5m])'

# Monitor response times
kubectl exec -it deployment/prometheus -n monitoring -- \
  promtool query instant 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{version="canary"}[5m]))'

# Monitor business metrics
curl -s https://covet.example.com/metrics | grep -E "(canary|version)"
```

#### 4. Gradual Traffic Increase
```bash
# Increase to 10%
kubectl patch virtualservice covet-canary -n covet \
  --patch '{"spec":{"http":[{"route":[{"destination":{"subset":"stable"},"weight":90},{"destination":{"subset":"canary"},"weight":10}]}]}}'

# Increase to 50%
kubectl patch virtualservice covet-canary -n covet \
  --patch '{"spec":{"http":[{"route":[{"destination":{"subset":"stable"},"weight":50},{"destination":{"subset":"canary"},"weight":50}]}]}}'

# Full cutover (100%)
kubectl patch virtualservice covet-canary -n covet \
  --patch '{"spec":{"http":[{"route":[{"destination":{"subset":"canary"},"weight":100}]}]}}'
```

## Rollback Procedures

### Automatic Rollback Triggers
```yaml
# rollback-policy.yml
rollback_triggers:
  error_rate: "> 5% for 2 minutes"
  response_time: "p95 > 1000ms for 5 minutes"
  availability: "< 99% for 1 minute"
  health_check_failures: "> 50% for 30 seconds"
```

### Manual Rollback

#### Quick Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/covet-app -n covet

# Monitor rollback progress
kubectl rollout status deployment/covet-app -n covet

# Verify rollback success
kubectl get deployment covet-app -n covet -o wide
```

#### Rollback to Specific Version
```bash
# List deployment history
kubectl rollout history deployment/covet-app -n covet

# Rollback to specific revision
kubectl rollout undo deployment/covet-app -n covet --to-revision=3

# Verify specific version
kubectl describe deployment covet-app -n covet | grep Image
```

#### Database Rollback
```bash
# For schema changes, use migration rollback
kubectl exec -it deployment/covet-app -n covet -- \
  python manage.py migrate app_name migration_name

# For data corruption, restore from backup
aws rds restore-db-cluster-from-snapshot \
  --db-cluster-identifier covet-aurora-restored \
  --snapshot-identifier covet-aurora-snapshot-$(date +%Y%m%d)

# Update application to use restored database
kubectl patch configmap covet-config -n covet \
  --patch '{"data":{"DB_HOST":"covet-aurora-restored.cluster-xyz.us-east-1.rds.amazonaws.com"}}'
```

## Database Migrations

### Pre-Migration Checklist
- [ ] Backup database
- [ ] Test migration on staging
- [ ] Verify rollback procedure
- [ ] Check migration duration
- [ ] Plan maintenance window (if needed)

### Migration Procedure

#### Safe Migrations (No Downtime)
```bash
# Additive schema changes (new columns, tables, indexes)
kubectl exec -it deployment/covet-app -n covet -- \
  python manage.py migrate --plan

# Execute migration
kubectl exec -it deployment/covet-app -n covet -- \
  python manage.py migrate

# Verify migration
kubectl exec -it deployment/covet-app -n covet -- \
  python manage.py showmigrations
```

#### Breaking Migrations (Maintenance Window)
```bash
# 1. Scale down to single replica
kubectl scale deployment covet-app --replicas=1 -n covet

# 2. Enable maintenance mode
kubectl patch configmap covet-config -n covet \
  --patch '{"data":{"MAINTENANCE_MODE":"true"}}'

# 3. Execute migration
kubectl exec -it deployment/covet-app -n covet -- \
  python manage.py migrate

# 4. Disable maintenance mode
kubectl patch configmap covet-config -n covet \
  --patch '{"data":{"MAINTENANCE_MODE":"false"}}'

# 5. Scale back up
kubectl scale deployment covet-app --replicas=5 -n covet
```

## Emergency Procedures

### Emergency Hotfix Deployment
```bash
# 1. Create emergency branch
git checkout -b emergency/critical-security-fix

# 2. Apply fix and test
# ... make changes ...
pytest tests/ -x

# 3. Fast-track review (if possible)
git commit -m "EMERGENCY: Fix critical security vulnerability"
git push origin emergency/critical-security-fix

# 4. Emergency deployment bypass (if needed)
docker build -t ghcr.io/covet/covet:emergency-$(date +%s) .
docker push ghcr.io/covet/covet:emergency-$(date +%s)

kubectl set image deployment/covet-app \
  covet=ghcr.io/covet/covet:emergency-$(date +%s) \
  -n covet

# 5. Monitor closely
kubectl logs -f deployment/covet-app -n covet
```

### Service Degradation Response
```bash
# 1. Reduce non-essential features
kubectl patch configmap covet-config -n covet \
  --patch '{"data":{"FEATURE_FLAG_ANALYTICS":"false","FEATURE_FLAG_RECOMMENDATIONS":"false"}}'

# 2. Scale down resource-intensive services
kubectl scale deployment covet-worker --replicas=2 -n covet

# 3. Enable circuit breakers
kubectl patch configmap covet-config -n covet \
  --patch '{"data":{"CIRCUIT_BREAKER_ENABLED":"true"}}'

# 4. Implement rate limiting
kubectl apply -f configs/emergency-rate-limiting.yml
```

## Monitoring and Alerts

### Deployment-Specific Alerts
```yaml
# deployment-alerts.yml
groups:
  - name: deployment-alerts
    rules:
      - alert: DeploymentInProgress
        expr: kube_deployment_status_replicas != kube_deployment_status_ready_replicas
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Deployment {{ $labels.deployment }} has been in progress for over 10 minutes"
          
      - alert: DeploymentFailed
        expr: kube_deployment_status_condition{condition="Progressing",status="false"} == 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Deployment {{ $labels.deployment }} has failed"
          
      - alert: HighErrorRateAfterDeployment
        expr: rate(http_requests_total{code=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected after deployment"
```

### Key Metrics to Monitor
```bash
# Error rate
rate(http_requests_total{code=~"5.."}[5m]) / rate(http_requests_total[5m])

# Response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Throughput
rate(http_requests_total[5m])

# Pod restart rate
rate(kube_pod_container_status_restarts_total[5m])

# Resource utilization
rate(container_cpu_usage_seconds_total[5m])
container_memory_usage_bytes / container_spec_memory_limit_bytes
```

## Troubleshooting

### Common Deployment Issues

#### Pods Not Starting
```bash
# Check pod status
kubectl describe pods -n covet -l app=covet

# Check events
kubectl get events -n covet --sort-by='.lastTimestamp'

# Check resource constraints
kubectl top nodes
kubectl describe nodes | grep -A 10 "Allocated resources"

# Check image pull issues
kubectl describe pod <pod-name> -n covet | grep -A 10 "Events"
```

#### Image Pull Errors
```bash
# Verify image exists
docker pull ghcr.io/covet/covet:v1.2.3

# Check registry credentials
kubectl get secret regcred -n covet -o yaml

# Test image pull from cluster
kubectl run test-pod --image=ghcr.io/covet/covet:v1.2.3 --rm -it -- /bin/bash
```

#### Configuration Issues
```bash
# Check ConfigMap
kubectl get configmap covet-config -n covet -o yaml

# Check Secrets
kubectl get secret covet-secrets -n covet -o yaml

# Verify environment variables in pod
kubectl exec -it deployment/covet-app -n covet -- env | grep COVET
```

#### Health Check Failures
```bash
# Check health endpoint directly
kubectl exec -it deployment/covet-app -n covet -- \
  curl localhost:8000/health

# Check application logs
kubectl logs deployment/covet-app -n covet --tail=100

# Test database connectivity
kubectl exec -it deployment/covet-app -n covet -- \
  python -c "import psycopg2; print('DB connection OK')"
```

### Performance Issues

#### Slow Startup
```bash
# Check resource limits
kubectl describe pod <pod-name> -n covet | grep -A 10 "Limits"

# Increase startup probe delay
kubectl patch deployment covet-app -n covet \
  --patch '{"spec":{"template":{"spec":{"containers":[{"name":"covet","startupProbe":{"initialDelaySeconds":60}}]}}}}'

# Check for expensive initialization
kubectl logs deployment/covet-app -n covet | grep -i "startup\|init"
```

#### Memory Leaks
```bash
# Monitor memory usage over time
kubectl top pods -n covet -l app=covet --sort-by=memory

# Check for memory limits
kubectl describe deployment covet-app -n covet | grep -A 5 "Limits"

# Enable memory profiling (if available)
kubectl patch configmap covet-config -n covet \
  --patch '{"data":{"MEMORY_PROFILING":"true"}}'
```

## Documentation and Knowledge Base

### Deployment Records
- Maintain deployment log with timestamps, versions, and changes
- Document any manual interventions required
- Track deployment duration and issues encountered

### Runbook Updates
- Update this runbook after each incident or process change
- Review quarterly with the team
- Version control all deployment scripts and configurations

### Team Knowledge Sharing
- Regular deployment post-mortems
- Knowledge transfer sessions for new team members
- Cross-training on deployment procedures

## Tools and Scripts

### Deployment Scripts
```bash
# /scripts/deploy.sh - Main deployment script
#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "Deploying version $VERSION to $ENVIRONMENT"

# Pre-deployment checks
./scripts/pre-deployment-check.sh $ENVIRONMENT

# Deploy
kubectl set image deployment/covet-app \
  covet=ghcr.io/covet/covet:$VERSION \
  -n covet-$ENVIRONMENT

# Wait for rollout
kubectl rollout status deployment/covet-app -n covet-$ENVIRONMENT

# Post-deployment verification
./scripts/post-deployment-check.sh $ENVIRONMENT

echo "Deployment completed successfully"
```

### Monitoring Scripts
```bash
# /scripts/deployment-health-check.sh
#!/bin/bash

NAMESPACE=${1:-covet}

echo "Checking deployment health in namespace: $NAMESPACE"

# Check deployment status
kubectl get deployment -n $NAMESPACE

# Check pod health
kubectl get pods -n $NAMESPACE -l app=covet

# Run health check
kubectl exec -it deployment/covet-app -n $NAMESPACE -- \
  curl -f localhost:8000/health || echo "Health check failed"

# Check recent logs for errors
kubectl logs deployment/covet-app -n $NAMESPACE --tail=50 | grep -i error || echo "No errors found"

echo "Health check completed"
```

## Contact Information

**Deployment Team Lead**: [Name] - [Contact]
**SRE On-Call**: [PagerDuty rotation]
**Emergency Escalation**: [Manager contact]

**Last Updated**: 2024-01-15
**Next Review**: 2024-04-15

---

*This runbook should be accessible to all team members and updated regularly based on lessons learned and process improvements.*