# Incident Response Runbook

## Emergency Contacts

### Primary On-Call Rotation
- **Primary**: [On-call engineer name/contact]
- **Secondary**: [Backup engineer name/contact]
- **Escalation Manager**: [Engineering manager name/contact]

### External Contacts
- **Cloud Provider Support**: [Support contact/case URL]
- **Security Team**: [Security team contact]
- **Legal/Compliance**: [Legal team contact for data breaches]

## Quick Response Procedures

### Immediate Actions (First 5 Minutes)

1. **Acknowledge the Alert**
   ```bash
   # Acknowledge in PagerDuty
   pd incident acknowledge <incident_id>
   
   # Join incident Slack channel
   # Channel: #incident-<timestamp>
   ```

2. **Initial Assessment**
   - Check service status dashboard
   - Verify monitoring systems are operational
   - Assess user impact scope

3. **Form Incident Response Team**
   ```
   /incident create "Brief description of issue"
   # This creates:
   # - Incident Slack channel
   # - Incident commander assignment
   # - Initial status page update
   ```

### Severity Classification

| Severity | Definition | Examples | Response Time |
|----------|------------|----------|---------------|
| **P0 - Critical** | Total service outage, data loss | API down, database corruption | Immediate |
| **P1 - High** | Major feature broken, security breach | Authentication failure, major performance degradation | 15 minutes |
| **P2 - Medium** | Minor feature impacted | Single endpoint slow, non-critical service down | 1 hour |
| **P3 - Low** | Cosmetic issue, monitoring alert | Dashboard display issue, warning thresholds | 4 hours |

## Common Incident Types and Responses

### 1. API Service Outage

#### Symptoms
- Health check endpoints returning 5xx errors
- High error rate in monitoring
- User reports of service unavailability

#### Immediate Actions
```bash
# Check pod status
kubectl get pods -n covet -l app=covet

# Check recent deployments
kubectl rollout history deployment/covet-app -n covet

# Check application logs
kubectl logs -n covet -l app=covet --tail=100 -f

# Check ingress and load balancer
kubectl describe ingress covet-ingress -n covet
kubectl get svc covet-service -n covet
```

#### Diagnosis Steps
1. **Check Infrastructure**
   ```bash
   # Verify nodes are healthy
   kubectl get nodes
   kubectl describe nodes | grep -i "condition\|taint"
   
   # Check cluster resources
   kubectl top nodes
   kubectl describe hpa covet-hpa -n covet
   ```

2. **Check Application Health**
   ```bash
   # Application-specific health checks
   curl -k https://api.covet.example.com/health
   curl -k https://api.covet.example.com/metrics
   
   # Database connectivity
   kubectl exec -it deployment/covet-app -n covet -- \
     python -c "import psycopg2; print('DB OK')"
   ```

3. **Check Dependencies**
   ```bash
   # Database status
   aws rds describe-db-cluster-snapshots --db-cluster-identifier covet-aurora
   
   # Redis status
   aws elasticache describe-replication-groups --replication-group-id covet-redis
   
   # External service dependencies
   curl -I https://external-api.example.com/health
   ```

#### Resolution Actions
1. **Quick Fixes**
   ```bash
   # Restart pods if unhealthy
   kubectl rollout restart deployment/covet-app -n covet
   
   # Scale up if resource constrained
   kubectl scale deployment covet-app --replicas=10 -n covet
   
   # Rollback recent deployment
   kubectl rollout undo deployment/covet-app -n covet
   ```

2. **Configuration Fixes**
   ```bash
   # Update configuration
   kubectl patch configmap covet-config -n covet --patch '{"data":{"key":"new-value"}}'
   
   # Update secrets
   kubectl patch secret covet-secrets -n covet --patch '{"data":{"key":"bmV3LXZhbHVl"}}'
   
   # Restart to pick up config changes
   kubectl rollout restart deployment/covet-app -n covet
   ```

### 2. Database Issues

#### High Connection Count
```sql
-- Check current connections
SELECT count(*) as connection_count 
FROM pg_stat_activity 
WHERE state = 'active';

-- Check long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Kill long-running queries if necessary
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '10 minutes'
AND state = 'active';
```

#### Slow Query Performance
```sql
-- Enable slow query logging temporarily
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1 second
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Reset query statistics
SELECT pg_stat_statements_reset();
```

#### Database Failover
```bash
# Manual RDS failover
aws rds failover-db-cluster \
  --db-cluster-identifier covet-aurora \
  --target-db-instance-identifier covet-aurora-replica-1

# Monitor failover progress
aws rds describe-db-clusters \
  --db-cluster-identifier covet-aurora \
  --query 'DBClusters[0].Status'

# Update application configuration with new endpoint
kubectl patch configmap covet-config -n covet \
  --patch '{"data":{"DB_HOST":"new-writer-endpoint"}}'

# Restart application to pick up new config
kubectl rollout restart deployment/covet-app -n covet
```

### 3. High Load/Performance Issues

#### CPU/Memory Pressure
```bash
# Check resource utilization
kubectl top pods -n covet
kubectl describe hpa covet-hpa -n covet

# Scale immediately if needed
kubectl scale deployment covet-app --replicas=20 -n covet

# Check for memory leaks
kubectl exec -it deployment/covet-app -n covet -- \
  python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

#### Network Issues
```bash
# Check network connectivity
kubectl exec -it deployment/covet-app -n covet -- \
  ping -c 3 google.com

# Check DNS resolution
kubectl exec -it deployment/covet-app -n covet -- \
  nslookup covet-service.covet.svc.cluster.local

# Check service mesh metrics (if using Istio)
kubectl exec -it deployment/covet-app -n covet -c istio-proxy -- \
  curl localhost:15000/stats | grep circuit_breaker
```

#### Queue Backlog
```bash
# Check Redis queue depth
kubectl exec -it deployment/redis -n covet -- \
  redis-cli llen task_queue

# Scale background workers
kubectl scale deployment covet-worker --replicas=10 -n covet

# Check worker health
kubectl logs -n covet -l app=covet-worker --tail=50
```

### 4. Security Incidents

#### Suspected Data Breach
1. **Immediate Containment**
   ```bash
   # Block all external traffic
   kubectl patch service covet-service -n covet \
     --patch '{"spec":{"type":"ClusterIP"}}'
   
   # Scale down to minimum
   kubectl scale deployment covet-app --replicas=1 -n covet
   
   # Enable audit logging
   kubectl patch configmap covet-config -n covet \
     --patch '{"data":{"AUDIT_LOG_LEVEL":"DEBUG"}}'
   ```

2. **Investigation**
   ```bash
   # Check access logs
   kubectl logs -n covet -l app=covet --since=1h | grep -E "(ERROR|WARN|security)"
   
   # Check authentication logs
   grep -i "authentication\|authorization" /var/log/auth.log
   
   # Network traffic analysis
   tcpdump -i any -w /tmp/capture.pcap port 443
   ```

3. **Evidence Preservation**
   ```bash
   # Create snapshots
   aws ec2 create-snapshot --volume-id vol-xyz --description "Incident evidence"
   
   # Export logs
   kubectl logs deployment/covet-app -n covet --since=24h > incident-logs.txt
   
   # Database dump for analysis
   pg_dump covet > incident-db-dump.sql
   ```

#### DDoS Attack
```bash
# Check ingress metrics
kubectl get ing covet-ingress -n covet -o yaml

# Enable rate limiting
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: rate-limit-filter
  namespace: covet
spec:
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      listener:
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.local_ratelimit
        typed_config:
          "@type": type.googleapis.com/udpa.type.v1.TypedStruct
          type_url: type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          value:
            stat_prefix: local_rate_limiter
            token_bucket:
              max_tokens: 100
              tokens_per_fill: 100
              fill_interval: 60s
EOF

# Block malicious IPs at ALB level
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:region:account:listener/app/covet-alb/xyz \
  --conditions Field=source-ip,Values=malicious.ip.address/32 \
  --priority 1 \
  --actions Type=fixed-response,FixedResponseConfig='{StatusCode=403,ContentType=text/plain,MessageBody=Blocked}'
```

## Escalation Procedures

### When to Escalate

1. **Automatic Escalation Triggers**
   - P0 incident not acknowledged within 5 minutes
   - P1 incident not resolved within 1 hour
   - Multiple services affected simultaneously
   - Security incident detected

2. **Manual Escalation Criteria**
   - Root cause unclear after initial investigation
   - Resolution requires architectural changes
   - Legal/compliance implications
   - Customer data potentially compromised

### Escalation Contacts

```yaml
escalation_matrix:
  engineering:
    level_1: "On-call engineer"
    level_2: "Senior engineer/Tech lead"
    level_3: "Engineering manager"
    level_4: "VP Engineering/CTO"
  
  security:
    level_1: "Security engineer"
    level_2: "Security team lead"
    level_3: "CISO"
  
  business:
    level_1: "Product manager"
    level_2: "VP Product"
    level_3: "CEO"
  
  external:
    legal: "Legal team"
    pr: "Public relations"
    customer_success: "Customer success manager"
```

## Communication Templates

### Internal Status Update
```
🔄 INCIDENT UPDATE - INC-2024-0115-001

Status: INVESTIGATING
Time: 2024-01-15 14:30 UTC
Duration: 25 minutes

Impact:
- API response times 3x normal
- 15% of requests timing out
- ~1000 users affected

Current Actions:
- Scaled app servers from 3 to 10 instances
- Investigating database query performance
- Monitoring resource utilization

Next Update: 15:00 UTC

IC: @john.doe
```

### Customer Communication
```
We're currently experiencing elevated response times with our API service. 
Some users may notice slower performance or occasional timeouts.

Our engineering team is actively working on a resolution. 

We'll provide another update within 30 minutes.

Status page: https://status.covet.example.com
```

### All-Clear Message
```
✅ INCIDENT RESOLVED - INC-2024-0115-001

Resolution Time: 2024-01-15 15:15 UTC
Total Duration: 45 minutes

Resolution:
- Identified slow database query causing connection pool exhaustion
- Applied query optimization and increased pool size
- All metrics returned to normal

Root Cause:
- Recent data growth triggered query performance regression
- Connection pool sizing inadequate for load

Follow-up:
- Post-incident review scheduled for 2024-01-16 10:00 UTC
- Database performance monitoring improvements in progress

Thank you for your patience.
```

## Post-Incident Checklist

### Immediate (Within 1 hour of resolution)
- [ ] Verify all systems are stable
- [ ] Update status page to "All Systems Operational"
- [ ] Send all-clear communication
- [ ] Document timeline in incident tracker
- [ ] Schedule post-incident review meeting

### Short-term (Within 24 hours)
- [ ] Collect all relevant logs and metrics
- [ ] Create initial incident report
- [ ] Identify immediate action items
- [ ] Update monitoring/alerting as needed
- [ ] Communicate with affected customers

### Long-term (Within 1 week)
- [ ] Complete post-incident review
- [ ] Document lessons learned
- [ ] Implement prevention measures
- [ ] Update runbooks based on learnings
- [ ] Share knowledge with broader team

## Tools and Resources

### Monitoring Dashboards
- **Service Overview**: https://grafana.covet.example.com/d/service-overview
- **Infrastructure**: https://grafana.covet.example.com/d/infrastructure
- **Database**: https://grafana.covet.example.com/d/database
- **Security**: https://grafana.covet.example.com/d/security

### Log Analysis
- **Application Logs**: https://kibana.covet.example.com
- **Infrastructure Logs**: CloudWatch Logs
- **Security Logs**: AWS CloudTrail

### Communication Channels
- **Incident Channel**: #incident-response
- **Engineering**: #engineering
- **Status Updates**: #status-updates
- **Customer Support**: #customer-support

### External Tools
- **Status Page**: https://status.covet.example.com
- **PagerDuty**: https://covet.pagerduty.com
- **AWS Console**: https://console.aws.amazon.com
- **Kubernetes Dashboard**: https://k8s.covet.example.com

## Emergency Procedures

### Complete Service Shutdown
```bash
# Emergency shutdown procedure
# Use only when directed by incident commander

# 1. Stop all traffic
kubectl patch service covet-service -n covet \
  --patch '{"spec":{"selector":{"app":"emergency-shutdown"}}}'

# 2. Scale down applications
kubectl scale deployment covet-app --replicas=0 -n covet
kubectl scale deployment covet-worker --replicas=0 -n covet

# 3. Update status page
curl -X POST https://api.statuspage.io/v1/pages/PAGE_ID/incidents \
  -H "Authorization: OAuth API_KEY" \
  -d 'incident[name]=Emergency Maintenance' \
  -d 'incident[status]=investigating' \
  -d 'incident[impact_override]=major' \
  -d 'incident[body]=Service temporarily unavailable due to emergency maintenance'

# 4. Notify stakeholders
echo "EMERGENCY: Service shutdown initiated at $(date)" | \
  slack chat send --channel "#incident-response" --text -
```

### Emergency Recovery
```bash
# Emergency recovery procedure

# 1. Restore from last known good state
kubectl apply -f emergency-backup/

# 2. Verify database integrity
kubectl exec -it deployment/covet-app -n covet -- \
  python manage.py check --database=default

# 3. Gradually restore traffic
kubectl scale deployment covet-app --replicas=1 -n covet
# Wait and monitor before scaling further

# 4. Monitor recovery
watch kubectl get pods -n covet
```

## Contact Information Update

**Last Updated**: 2024-01-15
**Next Review**: 2024-04-15

**Maintained by**: SRE Team
**Emergency Contact**: +1-555-SRE-HELP

---

*This runbook should be reviewed and updated quarterly or after any major incident. All team members should familiarize themselves with these procedures.*