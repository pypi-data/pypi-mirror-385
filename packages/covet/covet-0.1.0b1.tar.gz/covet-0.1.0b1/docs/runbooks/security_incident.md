# Security Incident Response Runbook

## Purpose
This runbook provides step-by-step procedures for responding to security incidents detected by CovetPy.

## Severity Levels
- **CRITICAL**: Active exploitation, data breach, system compromise
- **HIGH**: Attempted exploitation, privilege escalation
- **MEDIUM**: Suspicious activity, policy violations
- **LOW**: Information gathering, reconnaissance

## Incident Response Procedure

### 1. Detection & Alert (0-5 minutes)
**Actions:**
1. Receive alert from CovetPy Security Monitoring
2. Verify alert authenticity
3. Check IDS dashboard for context
4. Assign incident ID and severity

**Commands:**
```python
from covet.security.monitoring import IDS, IncidentResponseAutomation

# Check recent detections
ids = IDS()
stats = await ids.get_statistics()

# Create incident
ir = IncidentResponseAutomation()
incident = await ir.create_incident(
    title="Security Alert Investigation",
    description="Investigating alert XYZ",
    severity=IncidentSeverity.HIGH
)
```

### 2. Containment (5-15 minutes)
**Actions:**
1. Review automated containment actions
2. Block malicious IPs if not auto-blocked
3. Suspend compromised accounts
4. Isolate affected systems

**Commands:**
```python
# Block IP
from covet.security.monitoring import ThreatIntelligence

threat_intel = ThreatIntelligence()
await threat_intel.block_ip(
    ip="198.51.100.1",
    reason="Active SQL injection attack",
    permanent=False
)

# Review forensic evidence
from covet.security.monitoring import ForensicsCollector

forensics = ForensicsCollector()
analysis = await forensics.analyze_attack_trace("198.51.100.1")
```

### 3. Investigation (15-60 minutes)
**Actions:**
1. Collect all available evidence
2. Review audit logs
3. Analyze attack patterns
4. Determine scope and impact

**Commands:**
```python
# Query audit logs
from covet.security.monitoring import AuditLogger, EventType

audit = AuditLogger()
events = await audit.query(
    event_type=EventType.SQL_INJECTION_ATTEMPT,
    ip_address="198.51.100.1"
)

# Generate forensic report
report = await forensics.generate_forensic_report(incident.incident_id)
```

### 4. Eradication (1-4 hours)
**Actions:**
1. Remove malware/backdoors
2. Patch vulnerabilities
3. Reset compromised credentials
4. Update security rules

### 5. Recovery (4-24 hours)
**Actions:**
1. Restore from clean backups if needed
2. Monitor for reinfection
3. Gradually restore services
4. Verify system integrity

### 6. Post-Incident (1-7 days)
**Actions:**
1. Generate incident report
2. Document lessons learned
3. Update security policies
4. Conduct team review

**Commands:**
```python
# Generate final incident report
final_report = await ir.generate_report(incident.incident_id)

# Update incident status
await ir.update_incident_status(
    incident.incident_id,
    IncidentStatus.CLOSED,
    notes="Investigation complete. Attack contained and system secured."
)
```

## Common Incident Types

### SQL Injection Attack
**Indicators:**
- SQL keywords in request parameters
- Union-based injection patterns
- High number of database errors

**Response:**
1. Block attacker IP immediately
2. Review database access logs
3. Check for data exfiltration
4. Patch vulnerable endpoints

### Brute Force Attack
**Indicators:**
- High volume of failed login attempts
- Multiple accounts targeted from same IP
- Distributed attack patterns

**Response:**
1. Implement temporary account lockouts
2. Enable MFA for affected accounts
3. Block source IPs
4. Review successful logins for compromise

### DDoS Attack
**Indicators:**
- Sudden traffic spike
- High request rate from multiple IPs
- Service degradation

**Response:**
1. Enable rate limiting
2. Activate DDoS mitigation service
3. Scale infrastructure if possible
4. Block malicious traffic patterns

## Escalation Path
1. **On-call Engineer** (0-15 min): Initial triage and containment
2. **Security Team Lead** (15-60 min): Investigation and coordination
3. **CISO** (1-4 hours): Major incidents, data breaches
4. **Executive Team** (4+ hours): Public disclosure, legal matters

## Communication Templates

### Internal Alert
```
SECURITY INCIDENT: [SEVERITY]
Incident ID: [INC-YYYYMMDD-XXXX]
Type: [Attack Type]
Status: [DETECTED/INVESTIGATING/CONTAINED]
Impact: [Description]
Actions Taken: [List]
Next Steps: [List]
```

### Customer Notification (if required)
```
Subject: Security Incident Notification

We detected and contained a security incident on [DATE].
- What happened: [Brief description]
- What data was affected: [Scope]
- What we've done: [Actions]
- What you should do: [Recommendations]

We take security seriously and are committed to protecting your data.
```

## Tools & Resources
- **IDS Dashboard**: http://grafana.example.com/security-overview
- **Audit Logs**: /var/log/covet/security/audit.log
- **Incident Tracker**: https://jira.example.com/security-incidents
- **Escalation Contacts**: security-team@example.com

## Review & Updates
This runbook should be reviewed quarterly and updated after each major incident.

**Last Updated**: 2025-10-11
**Next Review**: 2026-01-11
