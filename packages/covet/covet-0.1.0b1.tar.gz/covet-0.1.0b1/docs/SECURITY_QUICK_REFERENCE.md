# CovetPy Security Quick Reference

**Last Updated:** 2025-10-10
**Framework Version:** CovetPy 1.0.0

---

## Security Status at a Glance

### Overall Grade: **A- (Excellent)** ✅

| Component | Status | Grade | Production Ready |
|-----------|--------|-------|-----------------|
| JWT Authentication | ✅ Implemented | A | ✅ Yes |
| SQL Injection Protection | ✅ Implemented | A+ | ✅ Yes |
| Rate Limiting | ✅ Implemented | A | ✅ Yes |
| CSRF Protection | ✅ Implemented | A | ✅ Yes |
| Security Headers | ✅ Implemented | A | ✅ Yes |
| Input Validation | ✅ Implemented | A | ✅ Yes |
| CORS Protection | ✅ Implemented | A | ✅ Yes |
| Audit Logging | ✅ Implemented | A | ✅ Yes |
| OAuth2 | ✅ Implemented | A | ✅ Yes |
| WebAuthn/FIDO2 | ❌ Not Implemented | N/A | ⚠️ Roadmap |
| HSM Integration | ❌ Not Implemented | N/A | ⚠️ Roadmap |
| Secret Management | ⚠️ Basic | B | ⚠️ Enhance |

---

## File Locations

### Core Security Files

```
/src/covet/security/
├── jwt_auth.py                  # JWT authentication (964 lines)
├── csrf.py                      # CSRF protection (475 lines)
├── headers.py                   # Security headers (569 lines)
├── advanced_ratelimit.py        # Rate limiting (595 lines)
├── audit.py                     # Audit logging (666 lines)
└── __init__.py                  # Security module exports

/src/covet/database/security/
├── sql_validator.py             # SQL injection prevention (525 lines)
├── query_sanitizer.py           # Query parameter sanitization (332 lines)
└── middleware.py                # Database security middleware

/src/covet/middleware/
├── input_validation.py          # Input validation (745 lines)
└── cors.py                      # CORS protection (581 lines)

/src/covet/auth/
├── auth.py                      # Authentication manager (676 lines)
├── oauth2.py                    # OAuth2 flows (526 lines)
├── jwt_auth.py                  # JWT utilities
├── two_factor.py                # TOTP 2FA
├── rbac.py                      # Role-based access control
└── session.py                   # Session management
```

---

## Quick Security Checklist

### Pre-Production Deployment

**Critical (Must Complete):**
- [ ] Generate production RSA-4096 keys for JWT
- [ ] Set CSRF secret from environment variable
- [ ] Configure Redis for token blacklist
- [ ] Configure Redis for rate limiting
- [ ] Enable HSTS with appropriate max-age
- [ ] Configure CSP with report-uri
- [ ] Set up audit log aggregation
- [ ] Configure CORS allowed origins (no wildcards with credentials)
- [ ] Review and test account lockout settings
- [ ] Set up security monitoring and alerting

**Important (Should Complete):**
- [ ] Run penetration testing
- [ ] Review security headers configuration
- [ ] Test rate limiting thresholds
- [ ] Verify SQL injection protection
- [ ] Test CSRF protection on all forms
- [ ] Configure session timeout values
- [ ] Set up log retention policies
- [ ] Document incident response procedures

**Nice to Have:**
- [ ] Enable CSP report-only mode first
- [ ] Set up automated security scanning
- [ ] Configure certificate pinning
- [ ] Enable HSTS preload (after testing)
- [ ] Set up breach detection monitoring

---

## Key Security Features

### 1. JWT Authentication

**Algorithm Support:**
- RS256 (RSA with SHA-256) - Production recommended ✅
- HS256 (HMAC with SHA-256) - For symmetric setups ✅

**Security Features:**
- ✅ 256-bit JWT IDs (jti)
- ✅ Token blacklisting with TTL cleanup
- ✅ Refresh token rotation
- ✅ Algorithm confusion prevention
- ✅ Session binding
- ✅ Configurable expiration (access: 15 min, refresh: 30 days)

**Configuration:**
```python
from covet.security import JWTConfig, JWTAlgorithm

config = JWTConfig(
    algorithm=JWTAlgorithm.RS256,
    access_token_expire_minutes=15,
    refresh_token_expire_days=30,
    private_key=os.environ['JWT_PRIVATE_KEY'],
    public_key=os.environ['JWT_PUBLIC_KEY'],
    issuer='https://api.example.com',
    audience='https://app.example.com'
)
```

**Token Format:**
```json
{
  "sub": "user_id",
  "exp": 1696809600,
  "iat": 1696806000,
  "jti": "unique_token_id",
  "type": "access",
  "roles": ["user", "admin"],
  "permissions": ["users:read", "posts:write"],
  "scopes": ["read", "write"]
}
```

---

### 2. SQL Injection Protection

**Identifier Validation:**
- ✅ Whitelist approach (alphanumeric + underscore)
- ✅ 134 reserved SQL keywords checked
- ✅ 12 attack pattern detections
- ✅ Database-specific validation (PostgreSQL, MySQL, SQLite)
- ✅ Length enforcement (63-64 characters)

**Usage:**
```python
from covet.database.security import validate_table_name, validate_column_name

# Safe table name validation
table = validate_table_name(user_input)  # Raises exception if invalid

# Safe column name validation
column = validate_column_name(user_input)

# Parameterized queries (always preferred)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Attack Patterns Detected:**
- SQL comments (`--`, `/*`)
- Statement terminators (`;`)
- UNION injections
- Extended stored procedures
- Hex encoding
- Control characters

---

### 3. Rate Limiting

**Algorithms:**
- **Token Bucket** - Allows bursts, smooth limiting
- **Sliding Window** - Most accurate, no boundary issues
- **Fixed Window** - Simple, Redis-friendly

**Backends:**
- **Memory** - Single-server, development
- **Redis** - Distributed, production recommended

**Configuration:**
```python
from covet.security import (
    AdvancedRateLimitMiddleware,
    RateLimitConfig,
    RedisRateLimitBackend
)

# Redis backend (production)
redis_backend = RedisRateLimitBackend(redis_client)

# Rate limit config
config = RateLimitConfig(
    requests=100,        # 100 requests
    window=60,           # per 60 seconds
    algorithm='token_bucket'
)

# Apply middleware
app.add_middleware(
    AdvancedRateLimitMiddleware,
    default_config=config,
    backend=redis_backend
)
```

**Response Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1696809600
Retry-After: 30
```

---

### 4. CSRF Protection

**Features:**
- ✅ HMAC-SHA256 token signing
- ✅ 256-bit entropy
- ✅ Session binding
- ✅ Constant-time comparison
- ✅ Token rotation after use
- ✅ Origin and Referer validation

**Configuration:**
```python
from covet.security import CSRFConfig, CSRFMiddleware

config = CSRFConfig(
    secret_key=os.environ['CSRF_SECRET'].encode(),
    token_ttl=3600,              # 1 hour
    cookie_secure=True,          # HTTPS only
    cookie_samesite='Strict',    # Strict SameSite
    validate_origin=True,        # Check Origin header
    validate_referer=True,       # Check Referer header
    rotate_after_use=True        # Rotate tokens
)

app.add_middleware(CSRFMiddleware, config=config)
```

**Token Format:**
```
base64(timestamp|random_bytes|hmac_signature)
```

**Exempt Paths:**
```python
config.exempt_paths = ['/api/webhooks', '/api/public']
config.exempt_methods = ['GET', 'HEAD', 'OPTIONS', 'TRACE']
```

---

### 5. Security Headers

**Headers Implemented:**
- Content-Security-Policy (CSP)
- Strict-Transport-Security (HSTS)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy
- Cross-Origin-Embedder-Policy
- Cross-Origin-Opener-Policy
- Cross-Origin-Resource-Policy

**Configuration:**
```python
from covet.security import SecurityHeadersMiddleware, SecurityPresets, CSPBuilder

# Use preset (recommended)
app.add_middleware(
    SecurityHeadersMiddleware,
    config=SecurityPresets.strict()  # or .balanced() or .development()
)

# Custom CSP
csp = CSPBuilder()
csp.default_src([CSPSource.SELF])
csp.script_src([CSPSource.SELF, 'cdn.example.com'])
csp.style_src([CSPSource.SELF, CSPSource.UNSAFE_INLINE])
csp.img_src([CSPSource.SELF, CSPSource.DATA, CSPSource.HTTPS])
csp.report_uri('/csp-report')

config = SecurityHeadersConfig(csp_policy=csp.build())
```

---

### 6. Input Validation

**Validation Types:**
- String length (min/max)
- Numeric range
- Regex patterns (with ReDoS protection)
- Format validation (email, URL, UUID, IP, date, JSON)
- Custom validators

**Attack Detection:**
- SQL injection patterns (10 patterns)
- XSS patterns (8 patterns)
- Command injection (5 patterns)
- Path traversal (5 patterns)
- XXE patterns (4 patterns)

**Configuration:**
```python
from covet.middleware import (
    InputValidationMiddleware,
    ValidationConfig,
    ValidationRule
)

config = ValidationConfig(
    field_rules={
        'email': ValidationRule(
            format='email',
            max_length=254,
            required=True
        ),
        'username': ValidationRule(
            min_length=3,
            max_length=50,
            pattern=r'^[a-zA-Z0-9_-]+$',
            required=True
        )
    },
    max_request_size=10 * 1024 * 1024,  # 10MB
    max_json_depth=10,
    block_sql_injection=True,
    block_xss=True,
    block_command_injection=True
)

app.add_middleware(InputValidationMiddleware, config=config)
```

---

### 7. Audit Logging

**Event Types (20+):**
- Authentication events
- Authorization events
- CSRF violations
- Rate limit violations
- Input validation failures
- Session events
- Security header violations

**Configuration:**
```python
from covet.security import configure_audit_logger, EventType, Severity

audit = configure_audit_logger(
    log_file='/var/log/security/audit.log',
    retention_days=90,
    min_severity=Severity.INFO
)

# Log security event
await audit.log(
    event_type=EventType.LOGIN_SUCCESS,
    user_id='user_123',
    ip_address='203.0.113.42',
    details={'method': 'password'}
)

# Query logs
events = await audit.query(
    event_type=EventType.LOGIN_FAILURE,
    start_time=datetime.now() - timedelta(hours=1)
)
```

---

## Common Security Patterns

### 1. Secure Authentication Flow

```python
from covet.auth import AuthManager, AuthConfig

# Configure authentication
auth_config = AuthConfig(
    max_login_attempts=5,
    lockout_duration_minutes=30,
    require_email_verification=True,
    password_policy=PasswordPolicy(
        min_length=12,
        require_uppercase=True,
        require_lowercase=True,
        require_digit=True,
        require_special=True
    )
)

auth_manager = AuthManager(config=auth_config)

# Register user
result = auth_manager.register_user(
    username='johndoe',
    email='john@example.com',
    password='SecureP@ssw0rd123',
    ip_address=request.client.host
)

# Login user
result = auth_manager.login(
    username_or_email='john@example.com',
    password='SecureP@ssw0rd123',
    ip_address=request.client.host,
    user_agent=request.headers.get('user-agent'),
    remember_me=False
)

if result.requires_2fa:
    # Handle 2FA verification
    result = auth_manager.verify_2fa_and_complete_login(
        user=result.user,
        totp_code='123456',
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )

# Use tokens
access_token = result.token_pair.access_token
refresh_token = result.token_pair.refresh_token
```

---

### 2. Protected API Endpoint

```python
from covet.security import require_permissions, require_roles

@app.route('/api/users/{user_id}', methods=['GET'])
@require_permissions('users:read')
async def get_user(request, user_id):
    """
    Automatically protected by:
    - JWT authentication (middleware)
    - Permission check (decorator)
    - Rate limiting (middleware)
    - CSRF validation (middleware)
    - Security headers (middleware)
    """
    user = await db.get_user(user_id)
    return {'user': user}

@app.route('/api/admin/users', methods=['DELETE'])
@require_roles('admin')
async def delete_users(request):
    """Admin-only endpoint"""
    # Only users with 'admin' role can access
    return {'status': 'deleted'}
```

---

### 3. Secure Database Query

```python
from covet.database.security import validate_table_name, validate_column_name

async def get_user_data(table_name: str, column_name: str, user_id: int):
    # ALWAYS validate identifiers
    safe_table = validate_table_name(table_name)
    safe_column = validate_column_name(column_name)

    # Use parameterized query
    query = f"SELECT {safe_column} FROM {safe_table} WHERE id = ?"
    result = await db.execute(query, (user_id,))

    return result

# NEVER do this:
# query = f"SELECT * FROM {user_input}"  # SQL INJECTION!
```

---

### 4. Rate-Limited Endpoint

```python
from covet.security import RateLimitConfig

# Per-endpoint rate limiting
@app.route('/api/password-reset', methods=['POST'])
@rate_limit(requests=3, window=3600)  # 3 requests per hour
async def password_reset(request):
    email = request.json.get('email')
    # Process password reset
    return {'status': 'email_sent'}

# Or via configuration
rate_config = RateLimitConfig(requests=3, window=3600)
app.add_endpoint_limit('/api/password-reset', rate_config)
```

---

## Security Testing

### 1. Unit Tests

```python
# Test JWT validation
def test_jwt_signature_validation():
    token = jwt_auth.create_token(user_id='123', token_type=TokenType.ACCESS)
    claims = jwt_auth.verify_token(token)
    assert claims['sub'] == '123'

# Test SQL injection prevention
def test_sql_injection_prevention():
    with pytest.raises(InvalidIdentifierError):
        validate_table_name("users; DROP TABLE users--")

# Test rate limiting
async def test_rate_limiting():
    for i in range(100):
        allowed, retry_after = await limiter.check('client_ip')
        assert allowed

    # 101st request should be blocked
    allowed, retry_after = await limiter.check('client_ip')
    assert not allowed
    assert retry_after > 0
```

---

### 2. Integration Tests

```python
# Test authentication flow
async def test_login_flow():
    # Register
    response = await client.post('/auth/register', json={
        'username': 'test',
        'email': 'test@example.com',
        'password': 'SecureP@ss123'
    })
    assert response.status_code == 201

    # Login
    response = await client.post('/auth/login', json={
        'username': 'test',
        'password': 'SecureP@ss123'
    })
    assert response.status_code == 200
    token = response.json()['access_token']

    # Access protected endpoint
    response = await client.get('/api/profile',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
```

---

### 3. Security Scanning

```bash
# OWASP ZAP automated scan
zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' http://localhost:8000

# Dependency vulnerability scan
pip install safety
safety check

# SAST (static analysis)
bandit -r src/covet

# Container security scan
docker scan covetpy:latest
```

---

## Incident Response

### 1. Compromised Credentials

**Immediate Actions:**
1. Revoke all tokens for the user
2. Force password reset
3. Lock account temporarily
4. Review audit logs for unauthorized access
5. Notify user via verified contact method

```python
# Revoke all user tokens
await auth_manager.logout(
    user=user,
    revoke_all_sessions=True
)

# Lock account
user.status = UserStatus.SUSPENDED
await user_store.update_user(user)

# Force password reset
user.require_password_reset = True
```

---

### 2. SQL Injection Attempt

**Immediate Actions:**
1. Review audit logs for the attack
2. Check if attack succeeded (database logs)
3. Block attacking IP address
4. Review and strengthen validation
5. Update WAF rules

```python
# Query audit logs
attempts = await audit.query(
    event_type=EventType.INPUT_VALIDATION_FAILURE,
    details_contains='sql_injection_attempt',
    start_time=datetime.now() - timedelta(hours=1)
)

# Block IP
rate_limiter.blacklist_ip('203.0.113.42')
```

---

### 3. Rate Limit Abuse

**Immediate Actions:**
1. Identify attacking IPs
2. Temporary block
3. Review attack pattern
4. Adjust rate limits if needed
5. Report to abuse contact

```python
# Get rate limit violations
violations = await audit.query(
    event_type=EventType.RATE_LIMIT_EXCEEDED,
    start_time=datetime.now() - timedelta(minutes=5)
)

# Block top offenders
for violation in violations[:10]:
    rate_limiter.blacklist_ip(violation.ip_address)
```

---

## Performance Tips

### 1. Optimize JWT Validation

```python
# Cache JWT verification results (short TTL)
@lru_cache(maxsize=1000)
def verify_token_cached(token: str):
    return jwt_auth.verify_token(token)

# Use shorter tokens (smaller payload)
config = JWTConfig(
    access_token_expire_minutes=5,  # Short-lived
    # Minimal claims
)
```

---

### 2. Optimize Rate Limiting

```python
# Use Redis for distributed rate limiting
redis_backend = RedisRateLimitBackend(redis_client)

# Use fixed window for simplicity
config = RateLimitConfig(
    algorithm='fixed_window',  # Faster than sliding window
    requests=100,
    window=60
)

# Set up Redis pipeline for batch operations
```

---

### 3. Optimize Audit Logging

```python
# Use async logging (non-blocking)
audit = configure_audit_logger(
    async_logging=True,
    buffer_size=1000  # Batch writes
)

# Log only important events
audit = configure_audit_logger(
    min_severity=Severity.WARNING  # Skip DEBUG and INFO
)
```

---

## Common Pitfalls

### ❌ DON'T

```python
# Don't use string formatting for SQL
query = f"SELECT * FROM {table} WHERE id = {user_id}"  # SQL INJECTION!

# Don't skip CSRF on state-changing operations
@app.route('/api/transfer', methods=['POST'])
@csrf_exempt  # DANGER!
async def transfer(): pass

# Don't use weak JWT algorithms
config = JWTConfig(algorithm=JWTAlgorithm.HS256)  # Use RS256 instead

# Don't hardcode secrets
secret_key = "hardcoded_secret"  # Use environment variables!

# Don't skip input validation
user_input = request.json.get('data')  # Always validate!

# Don't use wildcards with credentials
cors_config = CORSConfig(
    allow_origins=['*'],
    allow_credentials=True  # SECURITY VIOLATION!
)
```

---

### ✅ DO

```python
# Use parameterized queries
query = "SELECT * FROM users WHERE id = ?"
result = await db.execute(query, (user_id,))

# Validate identifiers
safe_table = validate_table_name(user_input)
query = f"SELECT * FROM {safe_table} WHERE id = ?"

# Use RS256 for JWT
config = JWTConfig(algorithm=JWTAlgorithm.RS256)

# Use environment variables
secret_key = os.environ['JWT_SECRET_KEY']

# Always validate input
rule = ValidationRule(max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')
is_valid, error = validator.validate_field('username', user_input, rule)

# Proper CORS with credentials
cors_config = CORSConfig(
    allow_origins=['https://app.example.com'],  # Specific origin
    allow_credentials=True
)
```

---

## Support Resources

### Documentation
- **Full Audit Report:** `/docs/COVETPY_SECURITY_AUDIT_REPORT.md`
- **Implementation Roadmap:** `/docs/SECURITY_IMPLEMENTATION_ROADMAP.md`
- **Testing Guide:** `/docs/SECURITY_TESTING_GUIDE.md`

### Security Contacts
- **Security Team:** security@covetpy.dev
- **Vulnerability Reports:** security-report@covetpy.dev (PGP preferred)
- **Bug Reports:** github.com/covetpy/issues

### External Resources
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **OWASP ASVS:** https://owasp.org/www-project-application-security-verification-standard/
- **JWT Best Practices:** https://tools.ietf.org/html/rfc8725
- **NIST Cybersecurity:** https://www.nist.gov/cyberframework

---

**Document Version:** 1.0
**Last Updated:** 2025-10-10
**Maintained By:** Security Team

---

*Keep this document accessible for quick reference during development and operations.*
