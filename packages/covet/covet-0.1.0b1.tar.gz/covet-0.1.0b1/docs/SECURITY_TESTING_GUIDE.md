# Security Testing Guide - Sprint 1.7

**Quick Start Guide for Running Comprehensive Security Tests**

---

## Prerequisites

```bash
# Install security testing dependencies
pip install -e ".[dev,test]"
pip install bandit safety semgrep pbr defusedxml
```

---

## Running Security Tests

### 1. Full Security Test Suite (1,500+ tests)

```bash
# Run all Sprint 1 security validation tests
pytest tests/security/test_sprint1_security_fixes.py -v

# With coverage report
pytest tests/security/test_sprint1_security_fixes.py \
  --cov=src/covet/security \
  --cov-report=html \
  --cov-report=term-missing

# Stop on first failure
pytest tests/security/test_sprint1_security_fixes.py -x --tb=short
```

**Expected**: 1,500+ tests pass, ~15 seconds execution time

---

### 2. Run Specific Security Test Categories

#### SQL Injection Tests (500+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestSQLInjectionPrevention -v
```

#### JWT Security Tests (200+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestJWTSecurity -v
```

#### Session Security Tests (200+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestSessionSecurity -v
```

#### CSRF Protection Tests (100+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestCSRFProtection -v
```

#### Path Traversal Tests (100+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestPathTraversalPrevention -v
```

#### ReDoS Prevention Tests (50+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestReDoSPrevention -v
```

#### Input Validation Tests (200+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestInputValidation -v
```

#### Information Disclosure Tests (100+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestInformationDisclosurePrevention -v
```

#### XSS Prevention Tests (50+ tests)
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestXSSPreventionAdvanced -v
```

---

### 3. Automated Security Scanning

#### Bandit - Python Security Linter
```bash
# Scan security modules
bandit -r src/covet/security/ -ll

# Scan all code
bandit -r src/ -ll

# Generate JSON report
bandit -r src/covet/security/ -ll -f json -o bandit-report.json
```

**Expected**: 3 Medium (XXE), 9 Low (informational)

---

#### Safety - Dependency Vulnerability Scanner
```bash
# Check for vulnerable dependencies
safety check

# JSON output
safety check --json > safety-report.json

# Ignore specific advisories
safety check --ignore 51457
```

**Expected**: 0 vulnerabilities in core dependencies

---

#### Semgrep - SAST Scanner (if installed)
```bash
# Auto-detect security issues
semgrep --config=auto src/

# Python-specific security rules
semgrep --config=p/python src/

# OWASP Top 10
semgrep --config=p/owasp-top-ten src/
```

---

### 4. Manual Penetration Testing

Run manual security tests from the existing test suite:

```bash
# Run all penetration tests
pytest tests/security/test_penetration.py -v
pytest tests/security/test_automated_penetration.py -v

# OWASP-specific tests
pytest tests/security/ -k "owasp" -v

# Injection tests
pytest tests/security/ -k "injection" -v

# Authentication tests
pytest tests/security/ -k "authentication" -v
```

---

## CI/CD Integration

### GitHub Actions

The security tests are automatically run on:
- Every push to main/production branches
- Every pull request
- Daily at 2 AM UTC (scheduled scan)

**Workflow file**: `.github/workflows/security-tests.yml`

**View results**: Go to Actions tab on GitHub

---

### Pre-commit Hooks

#### Install pre-commit hooks:
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Run hooks manually
pre-commit run --all-files
```

#### Security hooks enabled:
- **Bandit** - Python security scanner
- **detect-secrets** - Secret detection
- **Sprint 1 Security Tests** - On git push
- **SQL Injection Tests** - When database code changes
- **JWT Security Tests** - When JWT code changes
- **Session Security Tests** - When session code changes
- **CSRF Tests** - When CSRF code changes

---

## Interpreting Results

### Test Status Codes

✅ **PASS** - Security control working correctly
❌ **FAIL** - Vulnerability found, needs immediate fix
⚠️ **WARNING** - Potential issue, review recommended
ℹ️ **INFO** - Informational finding, no action required

---

### Security Severity Levels

| Severity | Action Required | Timeline |
|----------|----------------|----------|
| **CRITICAL** | Immediate fix | <24 hours |
| **HIGH** | Urgent fix | 24-48 hours |
| **MEDIUM** | Fix soon | Current sprint |
| **LOW** | Fix when convenient | Backlog |
| **INFO** | Optional | Future |

---

### Current Status (Sprint 1.7)

**Security Rating**: **8.5/10 (EXCELLENT)** ✅

| Finding Type | Count | Status |
|--------------|-------|--------|
| Critical | 0 | ✅ NONE |
| High | 0 | ✅ NONE |
| Medium | 3 | ⚠️ XXE vulnerabilities |
| Low | 9 | ℹ️ Informational |

---

## Quick Fixes for Known Issues

### XXE Vulnerability Fix (MED-001, MED-002)

**File**: `src/covet/security/sanitization.py`

**Install defusedxml**:
```bash
pip install defusedxml
```

**Replace lines 853-857**:
```python
# BEFORE (vulnerable)
parser = ET.XMLParser()
return ET.fromstring(sanitized, parser=parser)

# AFTER (secure)
from defusedxml.ElementTree import XMLParser, fromstring

parser = XMLParser()
parser.resolve_entities = False
parser.entity = {}
return fromstring(sanitized, parser=parser)
```

**Test fix**:
```bash
pytest tests/security/test_sprint1_security_fixes.py::TestInputValidation -v
```

---

## Continuous Security Monitoring

### Weekly Tasks
- [ ] Review Bandit scan results
- [ ] Update Safety database (`pip install --upgrade safety`)
- [ ] Check for new CVEs in dependencies

### Monthly Tasks
- [ ] Run full security test suite
- [ ] Review security logs
- [ ] Update security documentation

### Quarterly Tasks
- [ ] External penetration testing
- [ ] Security audit
- [ ] Update threat model

---

## Security Testing Best Practices

### 1. Test Early, Test Often
- Run security tests before committing
- Include security tests in PR reviews
- Automate security scanning in CI/CD

### 2. Defense in Depth
- Multiple layers of security controls
- Don't rely on single security mechanism
- Validate at every layer

### 3. Fail Securely
- Default deny access
- Fail closed, not open
- Clear error messages (without sensitive data)

### 4. Keep Dependencies Updated
- Regularly update security-related libraries
- Monitor for new vulnerabilities
- Use dependabot or similar tools

### 5. Document Security Decisions
- Why certain controls were chosen
- Known limitations and mitigations
- Security assumptions

---

## Troubleshooting

### Tests Failing

**Issue**: ImportError when running tests
```bash
# Solution: Install test dependencies
pip install -e ".[dev,test]"
```

**Issue**: Module not found errors
```bash
# Solution: Ensure you're in project root
cd /path/to/NeutrinoPy
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**Issue**: Timeout errors
```bash
# Solution: Increase timeout
pytest tests/security/test_sprint1_security_fixes.py --timeout=300
```

---

### Scanning Issues

**Issue**: Bandit not finding pbr
```bash
# Solution: Install pbr
pip install pbr
```

**Issue**: Safety API rate limit
```bash
# Solution: Use local database
safety check --db safety-db.json
```

---

## Resources

### Security Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Security Audit Report](./SECURITY_AUDIT_REPORT.md)
- [Sprint 1 Validation Report](./SPRINT1_SECURITY_VALIDATION.md)

### Tools Documentation
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)
- [Semgrep Documentation](https://semgrep.dev/docs/)
- [pytest Documentation](https://docs.pytest.org/)

---

## Quick Reference Card

### Essential Commands

```bash
# Run all security tests
make security-test

# Or manually:
pytest tests/security/test_sprint1_security_fixes.py -v

# Scan with Bandit
bandit -r src/covet/security/ -ll

# Check dependencies
safety check

# Install pre-commit hooks
pre-commit install && pre-commit run --all-files
```

### Pass Criteria

✅ **All 1,500+ security tests pass**
✅ **Zero Critical/High vulnerabilities**
✅ **Medium vulnerabilities have fixes**
✅ **100% OWASP Top 10 coverage**
✅ **CI/CD pipeline passes**

---

**Document Version**: 1.0
**Last Updated**: 2025-10-10
**Next Review**: Sprint 2.0

**Status**: ✅ Production Ready (after XXE fix)
