# CovetPy Compliance Quick Start Guide

## Installation

```bash
# Install required dependencies
pip install cryptography>=41.0.0 \
            argon2-cffi>=23.1.0 \
            python-ldap>=3.4.0 \
            PyJWT>=2.8.0
```

## Quick Start

### 1. Run Security Audit

```bash
# Full compliance audit
python scripts/security_audit.py --all

# Specific standards
python scripts/security_audit.py --pci-dss
python scripts/security_audit.py --hipaa
python scripts/security_audit.py --gdpr
python scripts/security_audit.py --soc2

# Generate JSON report
python scripts/security_audit.py --all --report-format json --output compliance.json
```

### 2. Initialize Encryption

```python
from covet.security.compliance import (
    KeyManagementService,
    DataEncryptionService
)

# Create key management service
kms = KeyManagementService()

# Generate encryption key (auto-rotates in 90 days)
key = kms.generate_key(key_id="app_data", expires_in_days=90)

# Create encryption service
encryption = DataEncryptionService(kms)

# Encrypt sensitive data
encrypted = encryption.encrypt_string(
    plaintext="Credit card: 4111-1111-1111-1111",
    key_id="app_data",
    associated_data="user_12345"
)

# Decrypt data
decrypted = encryption.decrypt_string(
    encrypted_json=encrypted,
    associated_data="user_12345"
)
```

### 3. Enable Audit Logging

```python
from covet.security.compliance import AuditLogger, AuditEventType

# Create audit logger (1-year retention for PCI DSS)
audit = AuditLogger(retention_days=365)

# Log events
audit.log(
    event_type=AuditEventType.DATA_READ,
    action="view_payment_card",
    result="success",
    user_id="user_123",
    ip_address="192.168.1.1",
    resource="cards/4111",
    cardholder_data_accessed=True
)

# Verify log integrity
assert audit.verify_integrity()
```

### 4. Configure Access Control

```python
from covet.security.compliance import (
    AccessControlManager,
    AccessPolicy,
    AccessAction,
    AccessDecision
)

# Create access control manager
acm = AccessControlManager(audit)

# Define policy
policy = AccessPolicy(
    policy_id="pci_data_access",
    name="PCI Cardholder Data Access",
    description="Restrict access to cardholder data",
    resource_pattern="cards/*",
    actions={AccessAction.READ},
    effect=AccessDecision.ALLOW,
    principals={"payment_processor_role"},
    conditions={"require_mfa": True}
)

acm.add_policy(policy)

# Check access
result = acm.check_access(
    principal="user_123",
    action=AccessAction.READ,
    resource="cards/4111",
    roles={"payment_processor_role"},
    context={"mfa_verified": True}
)

if result.decision == AccessDecision.ALLOW:
    # Grant access
    print("Access granted")
```

## Use Cases

### PCI DSS: Encrypt Credit Card Data

```python
from covet.security.compliance import (
    KeyManagementService,
    DataEncryptionService,
    AuditLogger,
    AuditEventType
)

# Setup
kms = KeyManagementService()
encryption = DataEncryptionService(kms)
audit = AuditLogger(retention_days=365)

# Generate PCI-specific key
pci_key = kms.generate_key(key_id="pci_cardholder_data")

# Encrypt credit card
card_number = "4111-1111-1111-1111"
encrypted_card = encryption.encrypt_string(
    plaintext=card_number,
    key_id="pci_cardholder_data",
    associated_data="merchant_id_456"
)

# Log access
audit.log(
    event_type=AuditEventType.SECURITY_ENCRYPTION,
    action="encrypt_card",
    result="success",
    user_id="system",
    resource="pci_cardholder_data",
    cardholder_data_accessed=True
)

# Store encrypted card in database
database.save(encrypted_card)
```

### HIPAA: Encrypt PHI

```python
from covet.security.compliance import (
    PHIEncryptionService,
    HIPAAAuditLogger,
    PHICategory
)

# Setup
phi_service = PHIEncryptionService(kms, encryption, audit)
hipaa_audit = HIPAAAuditLogger(audit)

# Encrypt patient diagnosis
encrypted_diagnosis = phi_service.encrypt_phi(
    data="Patient diagnosed with Type 2 Diabetes",
    patient_id="patient_12345",
    user_id="doctor_789",
    categories={PHICategory.DIAGNOSIS}
)

# Log PHI access
hipaa_audit.log_phi_access(
    user_id="doctor_789",
    patient_id="patient_12345",
    action="encrypt",
    phi_categories={PHICategory.DIAGNOSIS.value},
    success=True,
    purpose="treatment"
)

# Decrypt for authorized user
decrypted = phi_service.decrypt_phi(
    encrypted_data=encrypted_diagnosis,
    patient_id="patient_12345",
    user_id="doctor_789",
    purpose="treatment"
)
```

### GDPR: Handle User Data Request

```python
from covet.security.compliance import (
    DataPortabilityService,
    RightToDeletionService,
    ConsentManager,
    DataExportFormat,
    DeletionReason,
    ProcessingPurpose
)

# Setup
portability = DataPortabilityService()
deletion = RightToDeletionService()
consent = ConsentManager()

# Export user data (Article 20)
user_data = database.get_user_data("user_123")
exported_data = portability.export_user_data(
    user_data=user_data,
    format=DataExportFormat.JSON
)

# Send to user
send_email(user="user_123", attachment=exported_data)

# Delete user data (Article 17)
deletion_request = deletion.create_deletion_request(
    user_id="user_123",
    reason=DeletionReason.USER_REQUEST
)

deletion.process_deletion(
    request_id=deletion_request.request_id,
    data_sources=["database", "cache", "logs", "backups"]
)

# Verify deletion
verification = deletion.verify_deletion(
    request_id=deletion_request.request_id,
    data_sources=["database", "cache", "logs", "backups"]
)

# Manage consent (Articles 6 & 7)
consent.grant_consent(
    user_id="user_456",
    purpose=ProcessingPurpose.MARKETING,
    consent_text="I agree to receive promotional emails"
)

# Check before processing
if consent.check_consent("user_456", ProcessingPurpose.MARKETING):
    send_marketing_email("user_456")
```

### SOC 2: Monitor Security Events

```python
from covet.security.compliance import (
    SOC2Monitor,
    SOC2ControlFramework,
    SecurityEventSeverity,
    ControlStatus
)

# Setup monitoring
monitor = SOC2Monitor()
controls = SOC2ControlFramework()

# Log security event
event = monitor.log_event(
    event_type="unauthorized_access_attempt",
    severity=SecurityEventSeverity.HIGH,
    source="api_gateway",
    description="Failed authentication: 10 attempts in 1 minute",
    user_id="attacker_ip_1.2.3.4",
    attempts=10
)

# Create incident for critical events
if event.severity == SecurityEventSeverity.CRITICAL:
    incident = monitor.create_incident(
        description="Critical security event detected",
        severity=event.severity,
        affected_systems=["api_gateway", "auth_service"]
    )

# Assess controls
controls.assess_control(
    control_id="CC6.1",
    assessor="security_team",
    result=ControlStatus.OPERATING_EFFECTIVELY,
    findings=["MFA implemented and tested"],
    recommendations=[],
    evidence=["mfa_test_results.pdf"]
)

# Get compliance score
soc2_score = controls.get_compliance_score()
print(f"SOC 2 Compliance: {soc2_score:.1f}%")
```

## Configuration Examples

### Production Configuration

```python
# config.py
import os
from covet.security.compliance import (
    KeyManagementService,
    DataEncryptionService,
    AuditLogger,
    AccessControlManager,
)

# Environment-specific configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Key Management
KMS_CONFIG = {
    "master_key": os.getenv("KMS_MASTER_KEY"),
    "key_rotation_days": 90,
    "kdf": "scrypt"  # or "argon2id" for even better security
}

# Audit Logging
AUDIT_CONFIG = {
    "retention_days": 365 if ENVIRONMENT == "production" else 30,
    "enable_realtime": True,
    "enable_integrity_check": True
}

# Access Control
ACCESS_CONFIG = {
    "default_deny": True,
    "emergency_access_duration": 60,  # minutes
    "access_review_frequency": 90  # days
}

# Initialize services
kms = KeyManagementService(**KMS_CONFIG)
encryption = DataEncryptionService(kms)
audit = AuditLogger(**AUDIT_CONFIG)
access_control = AccessControlManager(audit)
```

## Compliance Checklist

### PCI DSS
- [ ] Encrypt all cardholder data at rest (AES-256)
- [ ] Log all access to cardholder data
- [ ] Implement strong access control (RBAC)
- [ ] Rotate encryption keys every 90 days
- [ ] Retain logs for minimum 1 year
- [ ] Verify log integrity daily
- [ ] Run quarterly security audits

### HIPAA
- [ ] Encrypt all PHI at rest and in transit
- [ ] Log all PHI access with user ID, timestamp, action
- [ ] Implement Business Associate Agreements
- [ ] Retain audit logs for 6 years
- [ ] Implement secure deletion procedures
- [ ] Conduct annual risk assessments
- [ ] Train workforce on HIPAA requirements

### GDPR
- [ ] Implement right to data portability
- [ ] Implement right to erasure
- [ ] Implement consent management
- [ ] Document data processing activities
- [ ] Implement privacy by design
- [ ] Conduct Data Protection Impact Assessments
- [ ] Appoint Data Protection Officer (if required)

### SOC 2
- [ ] Implement and test security controls
- [ ] Document control objectives
- [ ] Conduct control assessments
- [ ] Monitor security events
- [ ] Implement incident response procedures
- [ ] Conduct annual penetration tests
- [ ] Maintain audit trail for all changes

## Troubleshooting

### Encryption Issues

**Problem:** Key not found
```python
# Solution: Generate key first
kms.generate_key(key_id="missing_key")
```

**Problem:** Decryption fails
```python
# Solution: Verify associated data matches
encrypted = encryption.encrypt_string(
    plaintext="data",
    key_id="key1",
    associated_data="context1"  # Must match for decryption
)

decrypted = encryption.decrypt_string(
    encrypted_json=encrypted,
    associated_data="context1"  # Same context required
)
```

### Audit Log Issues

**Problem:** Log integrity check fails
```python
# Solution: Check for tampering
if not audit.verify_integrity():
    # Investigate potential breach
    alert_security_team()
```

### Access Control Issues

**Problem:** Access denied unexpectedly
```python
# Solution: Check policy evaluation
result = acm.check_access(user, action, resource, roles, context)
print(f"Decision: {result.decision}")
print(f"Reason: {result.reason}")
print(f"Matched policies: {result.matched_policies}")
```

## Performance Tips

1. **Key Caching:** Cache active keys to avoid repeated KMS calls
2. **Batch Operations:** Encrypt/decrypt multiple records in batch
3. **Async Logging:** Use async audit logging for high-throughput applications
4. **Policy Optimization:** Order policies by frequency of use

## Support

- Documentation: `/docs/`
- Security Issues: security@covetpy.com
- Bug Reports: https://github.com/covetpy/issues
- Security Advisory: https://github.com/covetpy/security-advisories

---

**Document Version:** 1.0.0
**Last Updated:** October 11, 2025
