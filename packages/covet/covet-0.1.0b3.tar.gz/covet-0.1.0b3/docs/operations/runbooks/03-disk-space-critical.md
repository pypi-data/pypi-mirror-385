# Runbook: Disk Space Critical

## Alert Details
- **Alert Name:** `DiskSpaceLow`
- **Severity:** CRITICAL
- **Threshold:** Disk usage > 90%
- **SLA:** Immediate action required

## Symptoms
- Disk space > 90% full
- Application unable to write logs
- Database writes failing
- Potential data loss risk

## Investigation
```bash
# Check disk usage
df -h /

# Find large directories
du -sh /* | sort -hr | head -20

# Check large files
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -hr | head -20

# Check log sizes
du -sh /var/log/*
```

## Immediate Actions
```bash
# 1. Rotate logs immediately
docker exec covetpy-app logrotate -f /etc/logrotate.conf

# 2. Clean Docker artifacts
docker system prune -af --volumes

# 3. Clean old backups
find /backups -name "*.sql.gz" -mtime +30 -delete

# 4. Clean temporary files
rm -rf /tmp/*
```

## Long-term Solutions
1. **Implement log rotation**
   ```yaml
   # /etc/logrotate.d/covetpy
   /var/log/covetpy/*.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

2. **Set up automated cleanup**
3. **Monitor disk growth trends**
4. **Increase disk capacity** if persistent

## Verification
```bash
df -h /  # Should show > 20% free space
```

## Escalation
If disk > 95% after cleanup, escalate to Infrastructure team immediately.
