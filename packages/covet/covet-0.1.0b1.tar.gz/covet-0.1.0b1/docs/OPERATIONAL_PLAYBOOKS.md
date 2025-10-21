# CovetPy Operational Playbooks

## Overview

This document contains detailed operational playbooks for common scenarios and incidents that may occur in the CovetPy production environment. Each playbook provides step-by-step procedures to diagnose, mitigate, and resolve issues quickly.

## Table of Contents

1. [Application Issues](#application-issues)
2. [Database Problems](#database-problems)
3. [Infrastructure Incidents](#infrastructure-incidents)
4. [Security Incidents](#security-incidents)
5. [Performance Issues](#performance-issues)
6. [Monitoring and Alerting](#monitoring-and-alerting)
7. [Deployment Issues](#deployment-issues)
8. [Network Problems](#network-problems)

## Application Issues

### Playbook: Application Pods Crash Looping

#### Symptoms
- Pods in `CrashLoopBackOff` state
- Application unavailable or intermittent
- High restart count on pods

#### Investigation Steps

1. **Check Pod Status**
   ```bash
   kubectl get pods -n covetpy-production
   kubectl describe pod <pod-name> -n covetpy-production
   ```

2. **Check Recent Logs**
   ```bash
   kubectl logs <pod-name> -n covetpy-production --previous
   kubectl logs <pod-name> -n covetpy-production --tail=100
   ```

3. **Check Resource Constraints**
   ```bash
   kubectl top pods -n covetpy-production
   kubectl describe nodes | grep -A 5 "Resource Requests"
   ```

4. **Check Configuration**
   ```bash
   kubectl get configmap -n covetpy-production
   kubectl get secrets -n covetpy-production
   ```

#### Common Causes and Solutions

| Cause | Symptoms | Solution |
|-------|----------|----------|
| Out of Memory | OOMKilled events | Increase memory limits |
| Missing Secrets | Auth errors in logs | Check External Secrets sync |
| Database Connection | Connection timeout | Verify database connectivity |
| Configuration Error | Startup failures | Review ConfigMap values |

#### Resolution Steps

1. **Immediate Mitigation**
   ```bash
   # Scale to healthy replicas only
   kubectl scale deployment covetpy-app --replicas=0 -n covetpy-production
   kubectl scale deployment covetpy-app --replicas=1 -n covetpy-production
   ```

2. **Fix Root Cause**
   ```bash
   # Update resource limits
   kubectl patch deployment covetpy-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"covetpy","resources":{"limits":{"memory":"4Gi"}}}]}}}}' -n covetpy-production
   
   # Update configuration
   kubectl edit configmap covetpy-config -n covetpy-production
   ```

3. **Verify Resolution**
   ```bash
   kubectl rollout status deployment/covetpy-app -n covetpy-production
   curl -f https://api.yourdomain.com/health/ready
   ```

#### Prevention
- Set appropriate resource requests and limits
- Implement comprehensive health checks
- Monitor pod restart rates
- Regular configuration reviews

---

### Playbook: High Error Rate (5xx Errors)

#### Symptoms
- High 5xx error rate in application logs
- Users reporting service errors
- Prometheus alerts firing

#### Investigation Steps

1. **Check Error Rate**
   ```bash
   # Check Prometheus metrics
   curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~'5..'}[5m])"
   
   # Check application logs
   kubectl logs deployment/covetpy-app -n covetpy-production | grep -i error | tail -20
   ```

2. **Check Dependencies**
   ```bash
   # Database connectivity
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "SELECT 1"
   
   # Redis connectivity
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     redis-cli -h $REDIS_HOST ping
   ```

3. **Check Resource Utilization**
   ```bash
   kubectl top pods -n covetpy-production
   kubectl describe hpa covetpy-app -n covetpy-production
   ```

#### Resolution Steps

1. **Scale if Resource Constrained**
   ```bash
   kubectl scale deployment covetpy-app --replicas=10 -n covetpy-production
   ```

2. **Restart Unhealthy Pods**
   ```bash
   kubectl delete pods -l app=covetpy,unhealthy=true -n covetpy-production
   ```

3. **Check and Fix Database Issues**
   ```bash
   # Check database performance
   aws rds describe-db-cluster-performance-insights --db-cluster-identifier covet-aurora
   
   # Check connection count
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity"
   ```

#### Follow-up Actions
- Review error patterns in logs
- Check for code deployment correlation
- Update resource limits if needed
- Implement circuit breakers for external dependencies

---

## Database Problems

### Playbook: Database Connection Pool Exhaustion

#### Symptoms
- Connection timeout errors
- "too many connections" errors
- Application unable to connect to database

#### Investigation Steps

1. **Check Connection Count**
   ```bash
   # From application pod
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     SELECT count(*) as total_connections,
            sum(case when state = 'active' then 1 else 0 end) as active_connections,
            sum(case when state = 'idle' then 1 else 0 end) as idle_connections
     FROM pg_stat_activity WHERE datname = 'covetpy'"
   
   # Check max connections
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "SHOW max_connections"
   ```

2. **Check Long Running Queries**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     SELECT pid, usename, application_name, state, 
            now() - query_start as duration, query
     FROM pg_stat_activity 
     WHERE state != 'idle' 
     ORDER BY duration DESC 
     LIMIT 10"
   ```

3. **Check Application Pool Settings**
   ```bash
   kubectl logs deployment/covetpy-app -n covetpy-production | grep -i "connection pool"
   ```

#### Resolution Steps

1. **Immediate Relief**
   ```bash
   # Kill long-running idle connections
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     SELECT pg_terminate_backend(pid)
     FROM pg_stat_activity
     WHERE state = 'idle'
     AND now() - state_change > interval '1 hour'"
   ```

2. **Scale Down Application Temporarily**
   ```bash
   kubectl scale deployment covetpy-app --replicas=2 -n covetpy-production
   ```

3. **Update Database Parameters**
   ```bash
   # Increase max_connections if needed
   aws rds modify-db-cluster-parameter-group \
     --db-cluster-parameter-group-name covet-aurora-params \
     --parameters ParameterName=max_connections,ParameterValue=200,ApplyMethod=immediate
   ```

4. **Optimize Application Connection Pool**
   ```bash
   kubectl patch configmap covetpy-config -n covetpy-production --patch '
   data:
     DB_POOL_SIZE: "10"
     DB_POOL_TIMEOUT: "30"
     DB_POOL_MAX_OVERFLOW: "5"'
   
   kubectl rollout restart deployment/covetpy-app -n covetpy-production
   ```

#### Prevention
- Monitor connection usage patterns
- Implement connection pool monitoring
- Set appropriate pool sizes based on load
- Regular query performance reviews

---

### Playbook: Database High CPU Usage

#### Symptoms
- Database CPU utilization > 80%
- Slow query performance
- Application timeout errors

#### Investigation Steps

1. **Check CPU Metrics**
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/RDS \
     --metric-name CPUUtilization \
     --dimensions Name=DBClusterIdentifier,Value=covet-aurora \
     --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 300 \
     --statistics Average
   ```

2. **Identify Expensive Queries**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     SELECT query, calls, total_time, mean_time, rows
     FROM pg_stat_statements
     ORDER BY total_time DESC
     LIMIT 10"
   ```

3. **Check for Lock Contention**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     SELECT blocked_locks.pid AS blocked_pid,
            blocked_activity.usename AS blocked_user,
            blocking_locks.pid AS blocking_pid,
            blocking_activity.usename AS blocking_user,
            blocked_activity.query AS blocked_statement,
            blocking_activity.query AS current_statement_in_blocking_process
     FROM pg_catalog.pg_locks blocked_locks
     JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
     JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
     JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
     WHERE NOT blocked_locks.granted"
   ```

#### Resolution Steps

1. **Scale Database if Possible**
   ```bash
   # Scale Aurora Serverless v2
   aws rds modify-current-db-cluster \
     --db-cluster-identifier covet-aurora \
     --serverless-v2-scaling-configuration MinCapacity=2,MaxCapacity=8 \
     --apply-immediately
   ```

2. **Optimize Problematic Queries**
   ```bash
   # Add missing indexes
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     CREATE INDEX CONCURRENTLY idx_users_email ON users(email);"
   ```

3. **Enable Read Replica Routing**
   ```bash
   kubectl patch configmap covetpy-config -n covetpy-production --patch '
   data:
     DATABASE_READ_REPLICA_URL: "postgresql://readonly:pass@aurora-reader:5432/covetpy"'
   
   kubectl rollout restart deployment/covetpy-app -n covetpy-production
   ```

#### Follow-up Actions
- Review and optimize slow queries
- Implement query result caching
- Consider database schema optimizations
- Set up automated performance monitoring

---

## Infrastructure Incidents

### Playbook: Kubernetes Node Not Ready

#### Symptoms
- Node shows `NotReady` status
- Pods being evicted from node
- Cluster capacity reduced

#### Investigation Steps

1. **Check Node Status**
   ```bash
   kubectl get nodes
   kubectl describe node <node-name>
   ```

2. **Check Node Resources**
   ```bash
   kubectl top nodes
   kubectl describe node <node-name> | grep -A 10 "Resource Requests"
   ```

3. **Check Node Logs**
   ```bash
   # SSH to node (if accessible)
   ssh ec2-user@<node-ip>
   sudo journalctl -u kubelet --since="1 hour ago"
   
   # Check system resources
   df -h
   free -h
   top
   ```

4. **Check AWS Instance Status**
   ```bash
   aws ec2 describe-instance-status --instance-ids <instance-id>
   aws ec2 describe-instances --instance-ids <instance-id>
   ```

#### Resolution Steps

1. **Cordon Node to Prevent New Pods**
   ```bash
   kubectl cordon <node-name>
   ```

2. **Drain Node Safely**
   ```bash
   kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --force
   ```

3. **Restart Kubelet (if accessible)**
   ```bash
   ssh ec2-user@<node-ip>
   sudo systemctl restart kubelet
   sudo systemctl status kubelet
   ```

4. **Replace Node if Unrecoverable**
   ```bash
   # Terminate instance (ASG will replace)
   aws ec2 terminate-instances --instance-ids <instance-id>
   
   # Or force node group refresh
   aws eks update-nodegroup-version \
     --cluster-name covet-cluster \
     --nodegroup-name general \
     --force
   ```

5. **Uncordon When Ready**
   ```bash
   kubectl uncordon <node-name>
   ```

#### Prevention
- Monitor node resource usage
- Set up node problem detector
- Regular node health checks
- Automated node replacement policies

---

### Playbook: Storage Full on Nodes

#### Symptoms
- Pods failing with disk pressure
- Node marked as `DiskPressure`
- Application unable to write files

#### Investigation Steps

1. **Check Node Disk Usage**
   ```bash
   kubectl describe node <node-name> | grep -i "disk"
   kubectl get events --field-selector reason=DiskPressure
   ```

2. **Identify Space Usage**
   ```bash
   # Check from node
   ssh ec2-user@<node-ip>
   sudo df -h
   sudo du -sh /var/lib/docker/
   sudo du -sh /var/lib/kubelet/
   sudo docker system df
   ```

3. **Check Pod Disk Usage**
   ```bash
   kubectl exec -it <pod-name> -n covetpy-production -- df -h
   kubectl exec -it <pod-name> -n covetpy-production -- du -sh /tmp /var/log
   ```

#### Resolution Steps

1. **Clean Docker Resources**
   ```bash
   ssh ec2-user@<node-ip>
   sudo docker system prune -f
   sudo docker volume prune -f
   sudo docker image prune -a -f
   ```

2. **Clean Kubernetes Resources**
   ```bash
   ssh ec2-user@<node-ip>
   sudo crictl rmi --prune
   sudo journalctl --vacuum-time=1d
   ```

3. **Clean Application Logs**
   ```bash
   # Rotate logs
   kubectl exec -it <pod-name> -n covetpy-production -- \
     find /var/log -name "*.log" -mtime +1 -delete
   ```

4. **Scale or Migrate Workloads**
   ```bash
   kubectl cordon <node-name>
   kubectl drain <node-name> --ignore-daemonsets
   ```

5. **Increase EBS Volume Size if Needed**
   ```bash
   aws ec2 describe-volumes --volume-ids <volume-id>
   aws ec2 modify-volume --volume-id <volume-id> --size 200
   
   # Extend filesystem from node
   sudo resize2fs /dev/nvme0n1p1
   ```

#### Prevention
- Set up disk usage monitoring
- Implement log rotation policies
- Regular cleanup of unused images
- Monitor application disk usage

---

## Security Incidents

### Playbook: Suspicious Authentication Activity

#### Symptoms
- Multiple failed login attempts
- Unusual login patterns
- Security monitoring alerts

#### Investigation Steps

1. **Check Authentication Logs**
   ```bash
   kubectl logs deployment/covetpy-app -n covetpy-production | grep -i "auth\|login"
   
   # Check failed authentication attempts
   kubectl logs deployment/covetpy-app -n covetpy-production | \
     grep "authentication failed" | tail -20
   ```

2. **Check Source IPs**
   ```bash
   # Analyze access logs
   aws s3 cp s3://covet-alb-logs/AWSLogs/ . --recursive
   grep "authentication" *.log | awk '{print $3}' | sort | uniq -c | sort -nr
   ```

3. **Check for Compromised Accounts**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     SELECT username, last_login, login_count, failed_attempts
     FROM users 
     WHERE failed_attempts > 10 OR last_login > now() - interval '1 hour'
     ORDER BY failed_attempts DESC"
   ```

4. **Check System Access**
   ```bash
   # Check kubectl access logs
   kubectl get events --all-namespaces | grep -i "authentication\|unauthorized"
   
   # Check AWS CloudTrail
   aws logs filter-log-events \
     --log-group-name CloudTrail/covetpy \
     --start-time $(date -d '1 hour ago' +%s)000 \
     --filter-pattern '{ ($.errorCode = "*UnauthorizedOperation") || ($.errorCode = "AccessDenied*") }'
   ```

#### Response Steps

1. **Block Suspicious IPs**
   ```bash
   # Update ALB security group
   aws ec2 authorize-security-group-ingress \
     --group-id sg-xxxxxxxx \
     --protocol tcp \
     --port 80 \
     --source-group sg-xxxxxxxx
   
   # Or use WAF rules
   aws wafv2 update-rule-group \
     --scope REGIONAL \
     --id <rule-group-id> \
     --rules file://block-ips.json
   ```

2. **Disable Compromised Accounts**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     UPDATE users SET is_active = false 
     WHERE username IN ('compromised_user1', 'compromised_user2')"
   ```

3. **Rotate Affected Secrets**
   ```bash
   ./scripts/secret-rotation.sh --type jwt --force
   ./scripts/secret-rotation.sh --type api-keys --force
   ```

4. **Increase Monitoring**
   ```bash
   # Enable debug logging temporarily
   kubectl patch configmap covetpy-config -n covetpy-production --patch '
   data:
     LOG_LEVEL: "DEBUG"
     SECURITY_MONITORING: "enabled"'
   
   kubectl rollout restart deployment/covetpy-app -n covetpy-production
   ```

#### Follow-up Actions
- Conduct security review
- Update authentication policies
- Implement additional monitoring
- User communication if needed

---

### Playbook: Certificate Expiry

#### Symptoms
- SSL certificate expiry warnings
- Browser certificate errors
- API clients failing with SSL errors

#### Investigation Steps

1. **Check Certificate Status**
   ```bash
   # Check current certificate
   openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com | \
     openssl x509 -noout -dates
   
   # Check all certificates
   kubectl get certificates -n covetpy-production
   kubectl describe certificate covetpy-tls -n covetpy-production
   ```

2. **Check Cert-Manager Status**
   ```bash
   kubectl get certificaterequests -n covetpy-production
   kubectl get orders -n covetpy-production
   kubectl logs -n cert-manager deployment/cert-manager
   ```

3. **Check DNS Records**
   ```bash
   dig _acme-challenge.api.yourdomain.com TXT
   nslookup api.yourdomain.com
   ```

#### Resolution Steps

1. **Force Certificate Renewal**
   ```bash
   # Delete certificate to trigger renewal
   kubectl delete certificate covetpy-tls -n covetpy-production
   
   # Or force renewal
   kubectl annotate certificate covetpy-tls -n covetpy-production \
     cert-manager.io/issue-temporary-certificate="true"
   ```

2. **Check Cluster Issuer**
   ```bash
   kubectl get clusterissuer letsencrypt-production -o yaml
   kubectl describe clusterissuer letsencrypt-production
   ```

3. **Manual Certificate Request**
   ```bash
   # Create new certificate request
   cat <<EOF | kubectl apply -f -
   apiVersion: cert-manager.io/v1
   kind: Certificate
   metadata:
     name: covetpy-tls-manual
     namespace: covetpy-production
   spec:
     secretName: covetpy-tls-manual
     issuerRef:
       name: letsencrypt-production
       kind: ClusterIssuer
     dnsNames:
     - api.yourdomain.com
     - yourdomain.com
   EOF
   ```

4. **Update Ingress if Needed**
   ```bash
   kubectl patch ingress covetpy-ingress -n covetpy-production --patch '
   spec:
     tls:
     - hosts:
       - api.yourdomain.com
       secretName: covetpy-tls-manual'
   ```

#### Prevention
- Set up certificate expiry monitoring
- Automate certificate renewal
- Test certificate renewal process
- Monitor cert-manager logs

---

## Performance Issues

### Playbook: High Response Times

#### Symptoms
- API response times > 2 seconds
- User complaints about slow performance
- Timeout errors in logs

#### Investigation Steps

1. **Check Response Time Metrics**
   ```bash
   # Query Prometheus for response times
   curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
   
   # Check application metrics
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     curl localhost:9090/metrics | grep http_request_duration
   ```

2. **Check Resource Utilization**
   ```bash
   kubectl top pods -n covetpy-production
   kubectl describe hpa covetpy-app -n covetpy-production
   ```

3. **Check Database Performance**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "
     SELECT query, calls, total_time, mean_time
     FROM pg_stat_statements
     WHERE mean_time > 1000
     ORDER BY mean_time DESC
     LIMIT 10"
   ```

4. **Check Cache Hit Rates**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     redis-cli -h $REDIS_HOST info stats | grep keyspace
   ```

#### Resolution Steps

1. **Scale Application Horizontally**
   ```bash
   kubectl scale deployment covetpy-app --replicas=10 -n covetpy-production
   ```

2. **Optimize Database Queries**
   ```bash
   # Enable query logging temporarily
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "SET log_statement = 'all'"
   
   # Add missing indexes
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     psql $DATABASE_URL -c "CREATE INDEX CONCURRENTLY idx_performance ON table_name(column_name)"
   ```

3. **Increase Cache Usage**
   ```bash
   kubectl patch configmap covetpy-config -n covetpy-production --patch '
   data:
     CACHE_TTL: "3600"
     CACHE_ENABLED: "true"'
   
   kubectl rollout restart deployment/covetpy-app -n covetpy-production
   ```

4. **Enable Application Profiling**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     curl localhost:8000/debug/pprof/profile?seconds=30 > profile.pprof
   ```

#### Follow-up Actions
- Analyze performance profile
- Implement code optimizations
- Review database query patterns
- Consider CDN for static content

---

### Playbook: Memory Leak Detection

#### Symptoms
- Steadily increasing memory usage
- Pods being killed by OOM killer
- Performance degradation over time

#### Investigation Steps

1. **Monitor Memory Trends**
   ```bash
   # Check memory usage over time
   kubectl top pods -n covetpy-production --sort-by=memory
   
   # Get detailed memory info
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     cat /proc/meminfo
   ```

2. **Generate Memory Profile**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     curl localhost:8000/debug/pprof/heap > heap.pprof
   
   # Download and analyze with go tool pprof
   go tool pprof heap.pprof
   ```

3. **Check for Memory Intensive Operations**
   ```bash
   kubectl logs deployment/covetpy-app -n covetpy-production | \
     grep -i "memory\|allocation\|gc"
   ```

4. **Monitor Garbage Collection**
   ```bash
   kubectl exec -it deployment/covetpy-app -n covetpy-production -- \
     curl localhost:9090/metrics | grep gc_
   ```

#### Resolution Steps

1. **Immediate Relief**
   ```bash
   # Restart pods with memory issues
   kubectl delete pods -l app=covetpy -n covetpy-production
   ```

2. **Increase Memory Limits Temporarily**
   ```bash
   kubectl patch deployment covetpy-app -n covetpy-production --patch '
   spec:
     template:
       spec:
         containers:
         - name: covetpy
           resources:
             limits:
               memory: "8Gi"'
   ```

3. **Enable Memory Debugging**
   ```bash
   kubectl patch configmap covetpy-config -n covetpy-production --patch '
   data:
     MEMORY_PROFILING: "enabled"
     GC_DEBUG: "true"'
   
   kubectl rollout restart deployment/covetpy-app -n covetpy-production
   ```

4. **Implement Circuit Breakers**
   ```bash
   kubectl patch configmap covetpy-config -n covetpy-production --patch '
   data:
     MAX_CONCURRENT_REQUESTS: "1000"
     REQUEST_TIMEOUT: "30"'
   ```

#### Follow-up Actions
- Code review for memory leaks
- Implement memory monitoring
- Optimize data structures
- Regular memory profiling

---

## Monitoring and Alerting

### Playbook: Prometheus Down

#### Symptoms
- No metrics data in Grafana
- Prometheus alerts not firing
- Monitoring dashboard empty

#### Investigation Steps

1. **Check Prometheus Pod Status**
   ```bash
   kubectl get pods -n monitoring | grep prometheus
   kubectl describe pod prometheus-server-xxx -n monitoring
   ```

2. **Check Prometheus Logs**
   ```bash
   kubectl logs prometheus-server-xxx -n monitoring --tail=100
   ```

3. **Check Storage Issues**
   ```bash
   kubectl describe pvc prometheus-server -n monitoring
   kubectl get pv | grep prometheus
   ```

4. **Check Configuration**
   ```bash
   kubectl get configmap prometheus-server -n monitoring -o yaml
   ```

#### Resolution Steps

1. **Restart Prometheus**
   ```bash
   kubectl delete pod prometheus-server-xxx -n monitoring
   ```

2. **Check and Fix Storage**
   ```bash
   # If PVC is full, increase size
   kubectl patch pvc prometheus-server -n monitoring --patch '
   spec:
     resources:
       requests:
         storage: 200Gi'
   ```

3. **Validate Configuration**
   ```bash
   # Check config syntax
   kubectl exec -it prometheus-server-xxx -n monitoring -- \
     promtool check config /etc/config/prometheus.yml
   ```

4. **Restore from Backup if Needed**
   ```bash
   # If data corruption, restore from backup
   kubectl scale deployment prometheus-server --replicas=0 -n monitoring
   # Restore data from S3 backup
   kubectl scale deployment prometheus-server --replicas=1 -n monitoring
   ```

#### Prevention
- Monitor Prometheus storage usage
- Regular configuration validation
- Automated backup of Prometheus data
- Set up Prometheus HA

---

### Playbook: Alert Fatigue - Too Many Alerts

#### Symptoms
- Constant alert notifications
- Important alerts being ignored
- Team alert burnout

#### Investigation Steps

1. **Analyze Alert Frequency**
   ```bash
   # Check AlertManager metrics
   curl -s "http://alertmanager:9093/api/v1/alerts" | jq '.data[] | .labels.alertname' | sort | uniq -c | sort -nr
   ```

2. **Review Alert History**
   ```bash
   # Check alert firing patterns
   kubectl logs alertmanager-xxx -n monitoring | grep -i "firing\|resolved"
   ```

3. **Check Alert Rules**
   ```bash
   kubectl get prometheusrules -n monitoring -o yaml | grep -A 5 -B 5 "alert:"
   ```

#### Resolution Steps

1. **Adjust Alert Thresholds**
   ```bash
   # Update alert rules
   kubectl patch prometheusrule application-alerts -n monitoring --patch '
   spec:
     groups:
     - name: app-alerts
       rules:
       - alert: HighErrorRate
         expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1  # Increase threshold
         for: 10m  # Increase duration'
   ```

2. **Implement Alert Grouping**
   ```bash
   # Update AlertManager config
   kubectl patch configmap alertmanager -n monitoring --patch '
   data:
     alertmanager.yml: |
       route:
         group_by: ["alertname", "cluster", "service"]
         group_wait: 30s
         group_interval: 5m
         repeat_interval: 24h'
   ```

3. **Set Up Alert Inhibition**
   ```bash
   # Add inhibition rules
   kubectl patch configmap alertmanager -n monitoring --patch '
   data:
     alertmanager.yml: |
       inhibit_rules:
       - source_match:
           alertname: NodeDown
         target_match:
           alertname: PodCrashLooping
         equal: ["node"]'
   ```

4. **Implement Alert Routing**
   ```bash
   # Route different severity levels
   kubectl patch configmap alertmanager -n monitoring --patch '
   data:
     alertmanager.yml: |
       route:
         routes:
         - match:
             severity: critical
           receiver: pagerduty
         - match:
             severity: warning
           receiver: slack
         - match:
             severity: info
           receiver: email'
   ```

#### Prevention
- Regular alert rule review
- Implement alert SLOs
- Alert rule testing
- Team alert guidelines

---

## Deployment Issues

### Playbook: Deployment Rollout Stuck

#### Symptoms
- Deployment stuck in progress
- New pods not coming up
- Rolling update not completing

#### Investigation Steps

1. **Check Deployment Status**
   ```bash
   kubectl rollout status deployment/covetpy-app -n covetpy-production
   kubectl describe deployment covetpy-app -n covetpy-production
   ```

2. **Check ReplicaSet Status**
   ```bash
   kubectl get rs -n covetpy-production
   kubectl describe rs <new-replicaset> -n covetpy-production
   ```

3. **Check Pod Events**
   ```bash
   kubectl get events -n covetpy-production --sort-by='.lastTimestamp' | grep -i error
   kubectl describe pods -l app=covetpy -n covetpy-production
   ```

4. **Check Resource Availability**
   ```bash
   kubectl describe nodes | grep -A 5 "Resource Requests"
   kubectl top nodes
   ```

#### Resolution Steps

1. **Check for Resource Constraints**
   ```bash
   # Scale down other workloads if needed
   kubectl scale deployment non-critical-app --replicas=0 -n covetpy-production
   ```

2. **Rollback if Necessary**
   ```bash
   # Rollback to previous version
   kubectl rollout undo deployment/covetpy-app -n covetpy-production
   
   # Check rollback status
   kubectl rollout status deployment/covetpy-app -n covetpy-production
   ```

3. **Force Rollout if Safe**
   ```bash
   # Delete stuck pods to force recreation
   kubectl delete pods -l app=covetpy,version=old -n covetpy-production
   ```

4. **Adjust Deployment Strategy**
   ```bash
   # Update rolling update strategy
   kubectl patch deployment covetpy-app -n covetpy-production --patch '
   spec:
     strategy:
       rollingUpdate:
         maxSurge: 1
         maxUnavailable: 0'
   ```

#### Prevention
- Implement deployment health checks
- Use deployment strategies appropriate for workload
- Monitor resource usage during deployments
- Test deployments in staging first

---

### Playbook: Image Pull Errors

#### Symptoms
- Pods stuck in `ImagePullBackOff`
- "Failed to pull image" errors
- New deployments failing

#### Investigation Steps

1. **Check Pod Status and Events**
   ```bash
   kubectl get pods -n covetpy-production | grep ImagePull
   kubectl describe pod <pod-name> -n covetpy-production
   ```

2. **Check Image Existence**
   ```bash
   # Verify image exists
   docker pull ghcr.io/yourorg/covetpy:latest
   
   # Check registry authentication
   kubectl get secrets -n covetpy-production | grep regcred
   ```

3. **Check Node Connectivity**
   ```bash
   # Test from node
   ssh ec2-user@<node-ip>
   sudo docker pull ghcr.io/yourorg/covetpy:latest
   ```

4. **Check Registry Status**
   ```bash
   curl -I https://ghcr.io/v2/
   ```

#### Resolution Steps

1. **Update Image Pull Secrets**
   ```bash
   # Create new registry secret
   kubectl create secret docker-registry regcred \
     --docker-server=ghcr.io \
     --docker-username=yourorg \
     --docker-password=$GITHUB_TOKEN \
     -n covetpy-production
   
   # Update deployment to use secret
   kubectl patch deployment covetpy-app -n covetpy-production --patch '
   spec:
     template:
       spec:
         imagePullSecrets:
         - name: regcred'
   ```

2. **Fix Image Tag**
   ```bash
   # Use specific tag instead of latest
   kubectl set image deployment/covetpy-app \
     covetpy=ghcr.io/yourorg/covetpy:v1.2.3 \
     -n covetpy-production
   ```

3. **Use Public Mirror if Available**
   ```bash
   # Temporarily use public image
   kubectl set image deployment/covetpy-app \
     covetpy=docker.io/yourorg/covetpy:v1.2.3 \
     -n covetpy-production
   ```

4. **Clean Up Failed Pods**
   ```bash
   kubectl delete pods -l app=covetpy --field-selector=status.phase=Failed -n covetpy-production
   ```

#### Prevention
- Use specific image tags, not latest
- Monitor registry health
- Implement image caching
- Test image pulls in CI/CD

---

## Network Problems

### Playbook: Ingress Not Reachable

#### Symptoms
- External users cannot reach application
- DNS resolution issues
- Load balancer health checks failing

#### Investigation Steps

1. **Check Ingress Status**
   ```bash
   kubectl get ingress -n covetpy-production
   kubectl describe ingress covetpy-ingress -n covetpy-production
   ```

2. **Check Load Balancer**
   ```bash
   # Get ALB DNS name
   kubectl get ingress covetpy-ingress -n covetpy-production -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
   
   # Test ALB directly
   curl -I http://<alb-dns-name>
   ```

3. **Check Target Groups**
   ```bash
   aws elbv2 describe-target-groups
   aws elbv2 describe-target-health --target-group-arn <target-group-arn>
   ```

4. **Check DNS Records**
   ```bash
   dig api.yourdomain.com
   nslookup api.yourdomain.com
   ```

#### Resolution Steps

1. **Check Service Endpoints**
   ```bash
   kubectl get endpoints covetpy-app -n covetpy-production
   kubectl describe service covetpy-app -n covetpy-production
   ```

2. **Verify Pod Health**
   ```bash
   kubectl get pods -l app=covetpy -n covetpy-production
   curl -f <pod-ip>:8000/health/ready
   ```

3. **Update DNS Records**
   ```bash
   # Update Route53 if needed
   aws route53 change-resource-record-sets \
     --hosted-zone-id Z123456789 \
     --change-batch file://dns-update.json
   ```

4. **Restart Ingress Controller**
   ```bash
   kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx
   ```

5. **Check Security Groups**
   ```bash
   # Verify ALB security group allows traffic
   aws ec2 describe-security-groups --group-ids sg-xxxxxxxx
   ```

#### Prevention
- Monitor ingress controller health
- Automate DNS health checks
- Regular load balancer target health monitoring
- Test external connectivity in CI/CD

---

This completes the comprehensive operational playbooks for CovetPy. Each playbook provides step-by-step procedures for diagnosing and resolving common production issues, helping ensure rapid incident response and system reliability.