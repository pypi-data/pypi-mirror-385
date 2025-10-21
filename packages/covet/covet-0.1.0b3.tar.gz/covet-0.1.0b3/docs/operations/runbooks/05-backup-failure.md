# Runbook: Backup Failure

## Alert Details
- **Alert Name:** `BackupFailed`
- **Severity:** CRITICAL
- **Threshold:** No successful backup in 24 hours
- **SLA:** 2 hours to resolve

## Symptoms
- Last successful backup > 24 hours ago
- Backup jobs failing
- Data at risk in case of disaster

## Investigation
```bash
# Check last backup timestamp
curl 'http://localhost:9090/api/v1/query?query=covet_backup_last_success_timestamp'

# Check backup logs
docker logs covetpy-backup --tail 100

# Verify backup directory
ls -lh /backups/ | tail -20

# Check disk space on backup location
df -h /backups
```

## Resolution

### 1. Identify Failure Cause
```bash
# Common causes:
# - Disk full
# - Permission errors
# - Database connection issues
# - Network issues to backup storage

# Check backup script
cat /scripts/backup.sh
```

### 2. Manual Backup (Immediate)
```bash
# Create immediate backup
timestamp=$(date +%Y%m%d_%H%M%S)
docker exec postgres pg_dump -U covetpy covetpy_dev | gzip > /backups/manual_backup_${timestamp}.sql.gz

# Verify backup
gunzip -t /backups/manual_backup_${timestamp}.sql.gz
```

### 3. Fix Automated Backup
```bash
# Restart backup service
docker restart covetpy-backup

# Test backup script
docker exec covetpy-backup /scripts/backup.sh

# Check cron schedule
docker exec covetpy-backup crontab -l
```

## Verification
```bash
# Verify new backup created
ls -lht /backups/ | head -5

# Test restore (in test environment)
gunzip < /backups/latest.sql.gz | docker exec -i postgres psql -U covetpy test_db
```

## Prevention
- Monitor backup job health
- Alert on backup failures immediately
- Test restore procedures quarterly
- Maintain off-site backup copies

## Escalation
If unable to create backup after 2 hours, escalate to Database team.
Contact: `dba@covetpy.io`, Slack: `#database-team`
