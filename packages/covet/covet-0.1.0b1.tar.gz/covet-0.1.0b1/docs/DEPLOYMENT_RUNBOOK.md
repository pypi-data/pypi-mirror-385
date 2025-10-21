# CovetPy Production Deployment Runbook

## Overview

This runbook provides comprehensive guidance for deploying, operating, and troubleshooting the CovetPy web framework in production environments. It covers all aspects from initial setup to incident response.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Deployment Procedures](#deployment-procedures)
4. [Monitoring and Alerts](#monitoring-and-alerts)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Incident Response](#incident-response)
7. [Maintenance Procedures](#maintenance-procedures)
8. [Security Operations](#security-operations)
9. [Backup and Recovery](#backup-and-recovery)
10. [Emergency Procedures](#emergency-procedures)

## Prerequisites

### Required Tools

- **kubectl** (v1.28+) - Kubernetes command-line tool
- **aws-cli** (v2.0+) - AWS command-line interface
- **terraform** (v1.5+) - Infrastructure as Code tool
- **docker** (v20.0+) - Container runtime
- **helm** (v3.0+) - Kubernetes package manager
- **jq** (v1.6+) - JSON processor
- **curl** - HTTP client for testing

### Required Access

- **AWS Console** - Admin access to production AWS account
- **Kubernetes Cluster** - Admin access to production EKS cluster
- **GitHub** - Admin access to CovetPy repository
- **Monitoring** - Access to Grafana and Prometheus dashboards
- **Alerting** - Access to PagerDuty/Slack for incident management

### Environment Variables

```bash
# AWS Configuration
export AWS_PROFILE=covetpy-production
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=123456789012

# Kubernetes Configuration
export KUBECONFIG=/path/to/production-kubeconfig
export KUBECTL_CONTEXT=covetpy-production

# Application Configuration
export ENVIRONMENT=production
export NAMESPACE=covetpy-production
export IMAGE_TAG=latest
```

## Initial Setup

### 1. Infrastructure Deployment

#### Deploy with Terraform

```bash
# Navigate to infrastructure directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="environment=production" -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Save outputs
terraform output > ../outputs.json
```

#### Verify Infrastructure

```bash
# Check EKS cluster
aws eks describe-cluster --name covet-cluster

# Check RDS cluster
aws rds describe-db-clusters --db-cluster-identifier covet-aurora

# Check ElastiCache
aws elasticache describe-replication-groups --replication-group-id covet-redis
```

### 2. Kubernetes Setup

#### Install Required Operators

```bash
# External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets-system \
  --create-namespace

# Cert-Manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Prometheus Stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

#### Apply Kubernetes Manifests

```bash
# Create namespace
kubectl apply -f infrastructure/kubernetes/production/namespace.yaml

# Apply secrets management
kubectl apply -f infrastructure/security/secret-management.yml

# Apply application manifests
kubectl apply -f infrastructure/kubernetes/production/
```

### 3. Application Deployment

#### Build and Push Images

```bash
# Build production image
docker build -f Dockerfile.production -t ghcr.io/yourorg/covetpy:latest .

# Push to registry
docker push ghcr.io/yourorg/covetpy:latest
```

#### Deploy Application

```bash
# Deploy application
kubectl apply -f infrastructure/kubernetes/production/deployment.yaml

# Wait for rollout
kubectl rollout status deployment/covetpy-app -n covetpy-production

# Verify pods are running
kubectl get pods -n covetpy-production
```

## Deployment Procedures

### Standard Deployment

#### 1. Pre-deployment Checklist

- [ ] All tests pass in CI/CD pipeline
- [ ] Security scans completed successfully
- [ ] Database migrations prepared (if any)
- [ ] Backup taken
- [ ] Monitoring alerts configured
- [ ] Rollback plan prepared

#### 2. Deployment Steps

```bash
# 1. Create backup
./scripts/database-migration.sh --dry-run

# 2. Update image tag
kubectl set image deployment/covetpy-app \
  covetpy=ghcr.io/yourorg/covetpy:${NEW_TAG} \
  -n covetpy-production

# 3. Monitor rollout
kubectl rollout status deployment/covetpy-app \
  -n covetpy-production --timeout=600s

# 4. Run health checks
./scripts/health-check.sh

# 5. Verify functionality
./scripts/smoke-tests.sh
```

#### 3. Post-deployment Verification

```bash
# Check application health
curl -f https://api.yourdomain.com/health/ready

# Check database connectivity
curl -f https://api.yourdomain.com/health/database

# Check cache connectivity
curl -f https://api.yourdomain.com/health/cache

# Monitor error rates
kubectl logs -f deployment/covetpy-app -n covetpy-production
```

### Blue-Green Deployment

#### Using Argo Rollouts

```bash
# Create rollout
kubectl apply -f infrastructure/kubernetes/production/rollout.yaml

# Monitor rollout
kubectl argo rollouts get rollout covetpy-app-rollout \
  -n covetpy-production --watch

# Promote after validation
kubectl argo rollouts promote covetpy-app-rollout \
  -n covetpy-production
```

### Database Migrations

#### Safe Migration Process

```bash
# 1. Create backup
./scripts/database-migration.sh --environment production

# 2. Run migrations
./scripts/database-migration.sh \
  --environment production \
  --target latest

# 3. Verify data integrity
./scripts/verify-migration.sh
```

## Monitoring and Alerts

### Key Metrics Dashboard

#### Application Metrics
- **Request Rate**: HTTP requests per second
- **Error Rate**: 4xx/5xx errors percentage
- **Response Time**: P95 response time
- **Availability**: Uptime percentage

#### Infrastructure Metrics
- **CPU Usage**: Pod and node CPU utilization
- **Memory Usage**: Pod and node memory utilization
- **Disk Usage**: Storage utilization
- **Network I/O**: Network traffic patterns

#### Database Metrics
- **Connection Pool**: Active connections
- **Query Performance**: Slow query count
- **Replication Lag**: Primary-replica lag
- **Backup Status**: Backup success/failure

### Critical Alerts

#### Application Alerts
- **Service Down**: Application pods not responding
- **High Error Rate**: >5% error rate for 5 minutes
- **High Response Time**: P95 > 2 seconds for 5 minutes
- **Memory Leak**: Memory usage increasing consistently

#### Infrastructure Alerts
- **Node Not Ready**: Kubernetes node not ready
- **Pod Crash Loop**: Pod restarting frequently
- **Disk Space Low**: <10% disk space remaining
- **Certificate Expiry**: SSL certificates expiring in 7 days

#### Database Alerts
- **Database Down**: Database not responding
- **High Connections**: >80% of max connections
- **Replication Lag**: >30 seconds lag
- **Backup Failure**: Daily backup failed

### Alert Response Times

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| Critical | 15 minutes | Page on-call engineer |
| High | 1 hour | Slack notification |
| Medium | 4 hours | Email notification |
| Low | Next business day | Ticket creation |

## Troubleshooting Guide

### Common Issues

#### Application Won't Start

**Symptoms:**
- Pods in `CrashLoopBackOff` state
- Container exits immediately
- Health checks failing

**Investigation Steps:**
```bash
# Check pod status
kubectl get pods -n covetpy-production

# Check logs
kubectl logs deployment/covetpy-app -n covetpy-production --tail=100

# Check events
kubectl get events -n covetpy-production --sort-by='.lastTimestamp'

# Check resources
kubectl describe pod <pod-name> -n covetpy-production
```

**Common Causes:**
- Configuration errors
- Missing secrets
- Database connectivity issues
- Resource limits too low

#### Database Connection Issues

**Symptoms:**
- Connection timeout errors
- Authentication failures
- Slow query performance

**Investigation Steps:**
```bash
# Check database status
aws rds describe-db-clusters --db-cluster-identifier covet-aurora

# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx

# Test connectivity from pod
kubectl run debug --image=postgres:15 --rm -it -- \
  psql postgresql://user:pass@host:5432/db

# Check connection pool
kubectl logs deployment/covetpy-app -n covetpy-production | grep "connection"
```

#### High Memory Usage

**Symptoms:**
- Pods being killed by OOMKiller
- Memory usage steadily increasing
- Performance degradation

**Investigation Steps:**
```bash
# Check memory usage
kubectl top pods -n covetpy-production

# Check memory limits
kubectl get pods -n covetpy-production -o yaml | grep -A2 -B2 memory

# Enable memory profiling
kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
  curl localhost:8000/debug/pprof/heap
```

#### SSL Certificate Issues

**Symptoms:**
- Certificate expiry warnings
- HTTPS connection failures
- Certificate validation errors

**Investigation Steps:**
```bash
# Check certificate expiry
openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com | \
  openssl x509 -noout -dates

# Check cert-manager status
kubectl get certificates -n covetpy-production

# Check certificate renewal
kubectl describe certificate covetpy-tls -n covetpy-production
```

### Performance Issues

#### High Response Times

**Investigation Steps:**
```bash
# Check application metrics
curl https://api.yourdomain.com/metrics

# Check database performance
aws rds describe-db-cluster-performance-insights

# Profile application
kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
  curl localhost:8000/debug/pprof/profile
```

**Common Solutions:**
- Scale horizontally (add more pods)
- Optimize database queries
- Add caching layers
- Review resource limits

#### Database Performance

**Investigation Steps:**
```bash
# Check slow queries
aws rds describe-db-log-files --db-instance-identifier covet-aurora-1

# Check connection metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBClusterIdentifier,Value=covet-aurora
```

## Incident Response

### Incident Severity Levels

#### P0 - Critical
- Complete service outage
- Data loss or corruption
- Security breach

#### P1 - High
- Significant service degradation
- Feature unavailable
- Performance severely impacted

#### P2 - Medium
- Minor service degradation
- Non-critical feature affected
- Workaround available

#### P3 - Low
- Cosmetic issues
- Documentation problems
- Enhancement requests

### Incident Response Process

#### 1. Initial Response (0-15 minutes)

```bash
# Acknowledge alert
# Update incident status page
# Form incident response team
# Begin investigation

# Quick health check
./scripts/health-check.sh

# Check system status
kubectl get pods,svc,ingress -n covetpy-production
```

#### 2. Investigation (15-30 minutes)

```bash
# Gather logs
kubectl logs deployment/covetpy-app -n covetpy-production --since=1h > incident-logs.txt

# Check metrics
# Review recent changes
# Identify root cause
```

#### 3. Mitigation (30-60 minutes)

```bash
# Implement immediate fix or rollback
kubectl rollout undo deployment/covetpy-app -n covetpy-production

# Scale if needed
kubectl scale deployment/covetpy-app --replicas=10 -n covetpy-production

# Apply hotfix if available
kubectl set image deployment/covetpy-app covetpy=ghcr.io/yourorg/covetpy:hotfix
```

#### 4. Recovery Verification

```bash
# Verify service recovery
./scripts/smoke-tests.sh

# Monitor metrics
# Update stakeholders
# Document timeline
```

### Communication Templates

#### Initial Incident Report
```
🚨 INCIDENT ALERT 🚨
Severity: P1
Service: CovetPy API
Issue: High error rates detected
Started: 2024-01-15 14:30 UTC
Team: On-call engineer investigating
Updates: Every 15 minutes until resolved
```

#### Resolution Notice
```
✅ INCIDENT RESOLVED ✅
Severity: P1
Service: CovetPy API
Resolution: Database connection pool increased
Duration: 45 minutes
Root Cause: Connection pool exhaustion during traffic spike
Next Steps: Post-incident review scheduled
```

## Maintenance Procedures

### Scheduled Maintenance

#### Monthly Maintenance Window
- **Schedule**: First Sunday of each month, 2:00-6:00 AM UTC
- **Duration**: 4 hours maximum
- **Approval**: Requires stakeholder approval 48 hours prior

#### Pre-maintenance Checklist
- [ ] Maintenance window scheduled and communicated
- [ ] Backup completed successfully
- [ ] Rollback plan prepared
- [ ] Team members identified and available
- [ ] Status page updated

#### Maintenance Tasks

```bash
# 1. Update system packages
kubectl set image daemonset/node-updater updater=latest -n kube-system

# 2. Rotate secrets
./scripts/secret-rotation.sh --type all --environment production

# 3. Update certificates
kubectl apply -f infrastructure/security/certificates.yml

# 4. Database maintenance
./scripts/database-maintenance.sh

# 5. Clean up old resources
kubectl delete pods --field-selector=status.phase=Succeeded -n covetpy-production
```

### Kubernetes Cluster Maintenance

#### Node Pool Updates

```bash
# Update node pool configuration
aws eks update-nodegroup-config \
  --cluster-name covet-cluster \
  --nodegroup-name general \
  --scaling-config minSize=3,maxSize=12,desiredSize=6

# Update node AMI
aws eks update-nodegroup-version \
  --cluster-name covet-cluster \
  --nodegroup-name general
```

#### Cluster Version Upgrade

```bash
# 1. Check compatibility
kubectl version

# 2. Update control plane
aws eks update-cluster-version \
  --name covet-cluster \
  --kubernetes-version 1.29

# 3. Update node groups
aws eks update-nodegroup-version \
  --cluster-name covet-cluster \
  --nodegroup-name general
```

## Security Operations

### Security Monitoring

#### Security Metrics
- **Failed login attempts**: Authentication failures
- **API abuse**: Unusual request patterns
- **Certificate status**: SSL certificate health
- **Secret rotation**: Secret age and rotation status

#### Security Scanning

```bash
# Container vulnerability scanning
trivy image ghcr.io/yourorg/covetpy:latest

# Secret scanning
./scripts/secret-scan.sh

# Dependency scanning
safety check -r requirements.txt
```

### Access Management

#### Emergency Access

```bash
# Break-glass access to production
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/EmergencyAccess \
  --role-session-name emergency-$(date +%s)

# Temporary kubectl access
kubectl auth can-i "*" "*" --as=system:admin
```

#### Access Review

```bash
# List all service accounts
kubectl get serviceaccounts --all-namespaces

# Review RBAC permissions
kubectl get clusterrolebindings -o wide

# Check AWS IAM roles
aws iam list-roles --query 'Roles[?contains(RoleName, `covet`)]'
```

## Backup and Recovery

### Backup Verification

```bash
# Check automated backup status
aws backup list-backup-jobs \
  --by-backup-vault-name covet-backup-vault

# Verify S3 backup storage
aws s3 ls s3://covet-database-backups/ --recursive

# Test backup restoration (non-production)
./scripts/test-restore.sh --environment staging
```

### Disaster Recovery

#### RTO/RPO Targets
- **RTO (Recovery Time Objective)**: 15 minutes
- **RPO (Recovery Point Objective)**: 5 minutes

#### DR Procedure

```bash
# 1. Activate DR region
terraform apply -var="enable_dr=true"

# 2. Restore from backup
./scripts/disaster-recovery.sh --activate

# 3. Update DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch file://dr-dns-change.json

# 4. Verify service in DR region
curl -f https://api-dr.yourdomain.com/health
```

## Emergency Procedures

### Complete Service Outage

#### Immediate Actions (0-5 minutes)
1. **Acknowledge** the outage
2. **Activate** incident response team
3. **Update** status page
4. **Begin** investigation

#### Investigation Commands
```bash
# Check all pods
kubectl get pods --all-namespaces | grep -v Running

# Check cluster nodes
kubectl get nodes

# Check ingress
kubectl get ingress -n covetpy-production

# Check external dependencies
dig api.yourdomain.com
curl -I https://api.yourdomain.com
```

### Database Emergency

#### Database Failover
```bash
# Check primary instance
aws rds describe-db-clusters --db-cluster-identifier covet-aurora

# Failover to replica
aws rds failover-db-cluster \
  --db-cluster-identifier covet-aurora \
  --target-db-instance-identifier covet-aurora-replica-1
```

### Security Incident

#### Immediate Response
```bash
# Isolate affected pods
kubectl patch deployment covetpy-app -p '{"spec":{"replicas":0}}' -n covetpy-production

# Check for unauthorized access
kubectl get events --field-selector reason=FailedMount -n covetpy-production

# Rotate all secrets
./scripts/secret-rotation.sh --type all --force
```

### Contact Information

#### On-Call Rotation
- **Primary**: +1-555-0101 (PagerDuty)
- **Secondary**: +1-555-0102 (PagerDuty)
- **Escalation**: Engineering Manager

#### External Contacts
- **AWS Support**: Enterprise Support Case
- **DNS Provider**: Support ticket system
- **Security Team**: security@yourdomain.com

### Additional Resources

#### Documentation Links
- [Architecture Diagram](./ARCHITECTURE.md)
- [API Documentation](./API_REFERENCE.md)
- [Configuration Guide](./CONFIGURATION.md)
- [Troubleshooting FAQ](./TROUBLESHOOTING_FAQ.md)

#### Monitoring Dashboards
- [Application Dashboard](https://grafana.yourdomain.com/d/app/covetpy)
- [Infrastructure Dashboard](https://grafana.yourdomain.com/d/infra/kubernetes)
- [Database Dashboard](https://grafana.yourdomain.com/d/db/postgresql)

#### Status Pages
- [Public Status](https://status.yourdomain.com)
- [Internal Status](https://internal-status.yourdomain.com)

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Next Review**: 2024-04-15  
**Owner**: DevOps Team