# CovetPy Security Guide

## Overview

This guide provides comprehensive documentation for implementing authentication and authorization in CovetPy applications. All security modules follow industry best practices and OWASP guidelines.

**Last Updated:** 2025-10-12
**Security Status:** All critical vulnerabilities patched

## Recent Security Enhancements

### Critical Fixes (2025-10-12)

**RCE Vulnerability Patched:**
- **Issue:** Unsafe pickle deserialization in session storage (CRITICAL)
- **Fix:** Replaced pickle with HMAC-signed JSON serialization
- **Impact:** Remote code execution vulnerability eliminated
- **Status:** PATCHED ✓

**SQL Injection Prevention Enhanced:**
- **Issue:** Multiple SQL injection vectors identified
- **Fix:** All database queries now use parameterized statements
- **Impact:** SQL injection vulnerabilities eliminated
- **Status:** PATCHED ✓

**Weak Hash Usage Fixed:**
- **Issue:** MD5 used without security flag (HIGH severity)
- **Fix:** Added `usedforsecurity=False` flag for non-cryptographic uses
- **Impact:** Compliance with security best practices
- **Status:** PATCHED ✓

**Current Security Status:**
- HIGH severity issues: 0
- MEDIUM severity issues: 175 (non-blocking)
- LOW severity issues: 1,521 (informational)

## Table of Contents

1. [SQL Injection Prevention](#sql-injection-prevention)
2. [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
3. [Rate Limiting](#rate-limiting)
4. [Password Security](#password-security)
5. [Session Management](#session-management)
6. [JWT Authentication](#jwt-authentication)
7. [Security Best Practices](#security-best-practices)
8. [Production Deployment](#production-deployment)

---

## SQL Injection Prevention

### Overview

All database queries in CovetPy use parameterized statements to prevent SQL injection attacks. This is enforced at the framework level.

### Safe Query Patterns

**ORM Queries (Always Safe):**
```python
# ✅ SAFE - ORM automatically parameterizes
users = await User.objects.filter(username=user_input).all()

# ✅ SAFE - Even with complex conditions
users = await User.objects.filter(
    username=user_input,
    age__gte=min_age,
    email__icontains=search_term
).all()

# ✅ SAFE - Updates are parameterized
await User.objects.filter(id=user_id).update(status=new_status)
```

**Raw SQL Queries (Use Parameterization):**
```python
# ✅ SAFE - Parameterized query
users = await User.objects.raw(
    "SELECT * FROM users WHERE username = %s AND age > %s",
    [user_input, min_age]
)

# ✅ SAFE - Direct adapter queries
from covet.database.orm.adapter_registry import get_adapter

adapter = get_adapter('default')
result = await adapter.execute(
    "SELECT * FROM users WHERE email = %s",
    [email_input]
)
```

### UNSAFE Patterns (Never Do This)

```python
# ❌ UNSAFE - String interpolation
query = f"SELECT * FROM users WHERE username = '{user_input}'"
await adapter.execute(query)

# ❌ UNSAFE - String concatenation
query = "SELECT * FROM users WHERE username = '" + user_input + "'"
await adapter.execute(query)

# ❌ UNSAFE - Unvalidated table/column names
table_name = user_input
await adapter.execute(f"SELECT * FROM {table_name}")
```

### Identifier Validation

When you must use dynamic identifiers (table/column names), validate them:

```python
from covet.database.security import validate_identifier

# ✅ SAFE - Validated identifier
table_name = validate_identifier(user_input, allowed=['users', 'posts', 'comments'])
query = f"SELECT * FROM {table_name} WHERE id = %s"
await adapter.execute(query, [record_id])

# Validate column names
column = validate_identifier(sort_by, allowed=['created_at', 'username', 'email'])
query = f"SELECT * FROM users ORDER BY {column}"
await adapter.execute(query)
```

### Security Testing

Test your application for SQL injection:

```bash
# Run security tests
pytest tests/security/test_sql_injection.py -v

# Run Bandit security scanner
bandit -r src/ -lll
```

---

## Multi-Factor Authentication (MFA)

### Overview

CovetPy provides production-ready MFA with TOTP (Time-based One-Time Password) support, compatible with Google Authenticator, Authy, and other authenticator apps.

### Quick Start

```python
from src.covet.security.mfa import MFAManager, TOTPSecret

# Initialize MFA manager
mfa = MFAManager(
    issuer="MyApp",
    totp_digits=6,
    totp_interval=30,
    max_failed_attempts=5,
    lockout_duration=300  # 5 minutes
)

# Start enrollment for a user
uri, secret = mfa.start_enrollment(
    user_id="user123",
    account_name="user@example.com"
)

# Generate QR code for user to scan
qr_code_image = mfa.generate_qr_code(uri)

# User scans QR code and enters first token
user_token = "123456"  # From authenticator app

# Complete enrollment
backup_codes = mfa.complete_enrollment("user123", user_token)

# IMPORTANT: Display backup codes to user (one-time only!)
# Store these securely - user needs them for account recovery
print("Save these backup codes:")
for code in backup_codes:
    print(f"  {code}")
```

### Verification Flow

```python
# During login, after password verification
if mfa.is_enrolled(user_id):
    # Request MFA token from user
    mfa_token = request.form.get("mfa_token")

    # Verify TOTP token
    if mfa.verify_totp(user_id, mfa_token):
        # MFA verification successful
        create_session(user_id)
    else:
        # Failed MFA - check if using backup code
        if mfa.verify_backup_code(user_id, mfa_token):
            # Backup code valid - warn user to regenerate
            create_session(user_id)
            flash("You used a backup code. Please regenerate them.")
        else:
            # MFA failed
            return error("Invalid MFA code")
```

### Backup Codes Management

```python
# Check backup code status
status = mfa.get_backup_codes_status(user_id)
print(f"Remaining codes: {status['remaining']}/{status['total']}")

if status['depleted'] or status['remaining'] < 3:
    # Regenerate backup codes
    new_codes = mfa.regenerate_backup_codes(user_id)
    # Display to user
```

### Security Features

- **Lockout Protection**: Automatically locks account after N failed attempts
- **Time Windows**: Accepts tokens within ±30 seconds to account for clock drift
- **Backup Codes**: Single-use recovery codes (hashed before storage)
- **QR Code Generation**: Secure QR codes for easy setup

### Best Practices

1. **Always provide backup codes** during enrollment
2. **Store MFA secrets encrypted** in your database
3. **Use HTTPS** for all MFA operations
4. **Implement rate limiting** on MFA endpoints
5. **Log MFA events** for security auditing
6. **Allow MFA reset** only through secure account recovery

---

## Rate Limiting

### Overview

Protect your API from abuse with flexible rate limiting supporting multiple algorithms and distributed backends.

### Algorithms

1. **Sliding Window** (Recommended): Most accurate, prevents boundary bursts
2. **Token Bucket**: Allows controlled bursts while maintaining average rate
3. **Fixed Window**: Simple and efficient (but allows boundary bursts)

### Quick Start

```python
from src.covet.security.rate_limiting import (
    RateLimitManager,
    RateLimitConfig,
    RateLimitAlgorithm,
    RateLimitScope
)

# Initialize manager
rate_limiter = RateLimitManager(
    redis_url="redis://localhost:6379",  # Optional: for distributed systems
    enable_redis=True
)

# Add rate limit policies
rate_limiter.add_limit(
    "api",
    RateLimitConfig(
        limit=100,  # 100 requests
        window=60,  # per 60 seconds
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        scope=RateLimitScope.IP
    ),
    use_redis=True  # Use Redis for distributed rate limiting
)

rate_limiter.add_limit(
    "login",
    RateLimitConfig(
        limit=5,
        window=300,  # 5 attempts per 5 minutes
        scope=RateLimitScope.USER
    )
)
```

### Usage in Endpoints

```python
# In your route handler
async def api_endpoint(request):
    # Get client identifier (IP, user ID, or API key)
    identifier = request.client.host

    # Check rate limit
    result = await rate_limiter.check("api", identifier)

    if not result.allowed:
        # Rate limit exceeded
        return JSONResponse(
            {
                "error": "rate_limit_exceeded",
                "retry_after": result.retry_after,
                "limit": result.limit,
                "reset_time": result.reset_time
            },
            status_code=429,
            headers={
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": str(result.remaining),
                "X-RateLimit-Reset": str(int(result.reset_time)),
                "Retry-After": str(result.retry_after)
            }
        )

    # Process request normally
    return handle_request(request)
```

### Per-User Rate Limiting

```python
# Different limits for authenticated users
async def protected_endpoint(request):
    user_id = request.state.user_id

    result = await rate_limiter.check("authenticated_api", user_id)

    if not result.allowed:
        return rate_limit_error(result)

    # Continue...
```

### Middleware Integration

```python
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter, policy="api"):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.policy = policy

    async def dispatch(self, request, call_next):
        # Get identifier
        identifier = request.client.host

        # Check limit
        result = await self.rate_limiter.check(self.policy, identifier)

        if not result.allowed:
            return JSONResponse(
                {"error": "Rate limit exceeded"},
                status_code=429,
                headers={
                    "Retry-After": str(result.retry_after)
                }
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)

        return response
```

### Redis Configuration (Distributed Systems)

```python
# For production distributed systems
rate_limiter = RateLimitManager(
    redis_url="redis://redis-cluster:6379/0",
    enable_redis=True
)

# All rate limit checks will be synchronized across servers
```

### Advanced: Custom Policies

```python
# API tier-based limits
FREE_TIER = RateLimitConfig(limit=100, window=3600)  # 100/hour
PRO_TIER = RateLimitConfig(limit=10000, window=3600)  # 10k/hour
ENTERPRISE = RateLimitConfig(limit=1000000, window=3600)  # 1M/hour

rate_limiter.add_limit("free_tier", FREE_TIER)
rate_limiter.add_limit("pro_tier", PRO_TIER)
rate_limiter.add_limit("enterprise", ENTERPRISE)

# Apply based on user tier
async def api_call(request):
    user = request.state.user
    tier = get_user_tier(user.id)

    result = await rate_limiter.check(tier, user.id)
    # ...
```

---

## Password Security

### Overview

Comprehensive password security with complexity validation, breach detection, and account lockout.

### Password Hashing

```python
from src.covet.security.password_security import (
    PasswordHasher,
    HashAlgorithm
)

# Use Argon2id (OWASP recommended)
hasher = PasswordHasher(
    algorithm=HashAlgorithm.ARGON2ID,
    argon2_time_cost=2,
    argon2_memory_cost=65536,  # 64 MB
    argon2_parallelism=4
)

# Hash password
password_hash = hasher.hash("user_password")

# Verify password (constant-time comparison)
is_valid = hasher.verify("user_password", password_hash)

# Check if hash needs rehashing (after config changes)
if hasher.needs_rehash(password_hash):
    new_hash = hasher.hash(user_password)
    update_user_password_hash(user_id, new_hash)
```

### Password Validation

```python
from src.covet.security.password_security import (
    PasswordValidator,
    PasswordPolicy
)

# Define password policy
policy = PasswordPolicy(
    min_length=12,
    max_length=128,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True,
    max_repeating_chars=3,
    max_sequential_chars=3,
    check_common_passwords=True,
    check_breach_database=True  # HaveIBeenPwned API
)

validator = PasswordValidator(policy)

# Validate password
result = validator.validate(
    password="UserPassword123!",
    username="johndoe"  # Check similarity
)

if not result.valid:
    # Show errors to user
    for error in result.errors:
        print(f"❌ {error}")

    # Show warnings (non-blocking)
    for warning in result.warnings:
        print(f"⚠️  {warning}")

    # Show suggestions
    for suggestion in result.suggestions:
        print(f"💡 {suggestion}")
else:
    # Password meets requirements
    print(f"✅ Password strength: {result.strength.value}")
    print(f"   Score: {result.score}/100")

    if result.breach_detected:
        print(f"⚠️  This password was found in {result.breach_count:,} data breaches!")
```

### Account Lockout

```python
from src.covet.security.password_security import AccountLockoutManager

# Initialize lockout manager
lockout = AccountLockoutManager(
    max_attempts=5,
    lockout_duration=900,  # 15 minutes
    attempt_window=300,  # 5 minutes
    progressive_delay=True  # Exponential backoff
)

# During login
def login(username, password):
    # Check if locked
    if lockout.is_locked(username):
        return error("Account temporarily locked. Try again later.")

    # Verify password
    user = get_user(username)
    if not user or not verify_password(password, user.password_hash):
        # Record failed attempt
        is_locked, retry_after = lockout.record_attempt(
            username,
            success=False,
            ip_address=request.client.host
        )

        if is_locked:
            return error(f"Account locked for {retry_after} seconds")
        elif retry_after:
            # Progressive delay
            sleep(retry_after)

        return error("Invalid credentials")

    # Success - reset lockout
    lockout.record_attempt(username, success=True)

    return create_session(user)
```

### Breach Detection (HaveIBeenPwned)

The password validator automatically checks passwords against the HaveIBeenPwned database using **k-anonymity** (only first 5 characters of SHA-1 hash are sent):

```python
# Check during password change
result = validator.validate(new_password, check_breach=True)

if result.breach_detected:
    return error(
        f"This password has been exposed in {result.breach_count:,} data breaches. "
        "Please choose a different password."
    )
```

---

## Session Management

### Overview

Secure session management with fixation prevention, strict validation, and automatic expiration.

### Configuration

```python
from src.covet.security.session_security import (
    SessionManager,
    SessionConfig,
    SessionStore
)

# Configure sessions
config = SessionConfig(
    idle_timeout=1800,  # 30 minutes
    max_lifetime=28800,  # 8 hours
    sliding_expiration=True,
    regenerate_on_login=True,  # Prevent fixation
    bind_ip_address=True,
    bind_user_agent=True,
    strict_validation=True,
    max_concurrent_sessions=5
)

# Initialize manager
session_manager = SessionManager(
    config=config,
    use_redis=True,  # For distributed systems
    redis_url="redis://localhost:6379"
)
```

### Creating Sessions

```python
# After successful login
async def login(request):
    # Authenticate user
    user = authenticate(username, password)

    # Create session
    session = await session_manager.create_session(
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        initial_data={
            "username": user.username,
            "roles": user.roles
        }
    )

    # Set session cookie
    response = JSONResponse({"success": True})
    response.set_cookie(
        "session_id",
        session.session_id,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",
        max_age=config.max_lifetime
    )

    return response
```

### Validating Sessions

```python
# In middleware or route handler
async def get_current_session(request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        return None

    # Validate session
    session = await session_manager.get_session(
        session_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    if not session:
        # Invalid, expired, or suspicious
        return None

    return session

# Use in route
async def protected_route(request):
    session = await get_current_session(request)

    if not session:
        return redirect("/login")

    # Access session data
    user_id = session.user_id
    username = session.data.get("username")

    # Continue...
```

### Session Regeneration (Fixation Prevention)

```python
# Regenerate session ID after privilege elevation
async def after_password_change(request):
    old_session_id = request.cookies.get("session_id")

    # Regenerate session ID
    new_session = await session_manager.regenerate_session_id(old_session_id)

    # Update cookie
    response = JSONResponse({"success": True})
    response.set_cookie("session_id", new_session.session_id, ...)

    return response
```

### Logout

```python
# Single session logout
async def logout(request):
    session_id = request.cookies.get("session_id")

    await session_manager.revoke_session(session_id)

    response = redirect("/")
    response.delete_cookie("session_id")
    return response

# Logout all sessions (after password change)
async def logout_all_sessions(user_id):
    count = await session_manager.revoke_all_user_sessions(user_id)
    print(f"Revoked {count} sessions")
```

### Session Monitoring

```python
# Get all active sessions for user
async def list_active_sessions(user_id):
    sessions = await session_manager.get_user_sessions(user_id)

    return [
        {
            "session_id": s.session_id[:16] + "...",
            "created": s.metadata.created_at,
            "last_activity": s.metadata.last_activity,
            "ip_address": s.metadata.ip_address,
            "user_agent": s.metadata.user_agent
        }
        for s in sessions
    ]
```

---

## JWT Authentication

### Overview

JWT authentication is implemented with support for multiple algorithms and secure token management.

### Configuration

**Important:** Always use enums for algorithm selection, not strings.

```python
from covet.security.jwt_auth import (
    JWTAuthenticator,
    JWTConfig,
    JWTAlgorithm  # Use enum, not string!
)

# ✅ CORRECT - Use enum
config = JWTConfig(
    secret_key='YOUR_SECRET_KEY_MINIMUM_32_CHARS',
    algorithm=JWTAlgorithm.HS256,  # Use enum
    access_token_expire_minutes=15,
    refresh_token_expire_days=7,
    issuer="MyApp",
    audience="myapp-api"
)

# ❌ INCORRECT - Don't use string
config = JWTConfig(
    secret_key='secret',
    algorithm='HS256',  # Wrong!
    ...
)
```

### Algorithm Selection

| Algorithm | Use Case | Key Type |
|-----------|----------|----------|
| HS256 | Simple apps, internal APIs | Shared secret (32+ chars) |
| RS256 | Public APIs, microservices | RSA key pair (recommended) |
| ES256 | High performance, mobile | ECDSA key pair |

**Production Recommendation:** Use RS256 with RSA keys for better security.

### Creating Tokens

```python
auth = JWTAuthenticator(config)

# Create access and refresh tokens
tokens = auth.create_token_pair(
    subject="user123",
    roles=["user", "premium"],
    permissions=["read:posts", "write:posts"]
)

# Access the tokens
access_token = tokens.access_token
refresh_token = tokens.refresh_token

# Return to client
return JSONResponse({
    'access_token': access_token,
    'refresh_token': refresh_token,
    'token_type': 'Bearer',
    'expires_in': 900  # 15 minutes
})
```

### Verifying Tokens

```python
# In your authentication middleware
async def authenticate_request(request):
    # Extract token from header
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        raise Unauthorized('Missing or invalid token')

    token = auth_header.split(' ')[1]

    # Verify token
    try:
        claims = auth.verify_token(token)

        # Token is valid - extract user info
        user_id = claims.get('sub')
        roles = claims.get('roles', [])
        permissions = claims.get('permissions', [])

        # Attach to request
        request.state.user_id = user_id
        request.state.roles = roles
        request.state.permissions = permissions

    except JWTExpiredError:
        raise Unauthorized('Token expired')
    except JWTInvalidError:
        raise Unauthorized('Invalid token')
```

### Token Refresh

```python
# Endpoint for refreshing tokens
@app.route('/auth/refresh', methods=['POST'])
async def refresh_token(request):
    data = json.loads(request.body)
    refresh_token = data.get('refresh_token')

    try:
        # Verify refresh token
        claims = auth.verify_token(refresh_token, token_type='refresh')

        # Create new access token
        new_access_token = auth.create_access_token(
            subject=claims['sub'],
            roles=claims.get('roles', []),
            permissions=claims.get('permissions', [])
        )

        return JSONResponse({
            'access_token': new_access_token,
            'token_type': 'Bearer'
        })

    except JWTExpiredError:
        return JSONResponse({'error': 'Refresh token expired'}, status=401)
```

### Best Practices

1. **Use Strong Secret Keys:**
   ```python
   import secrets
   secret_key = secrets.token_urlsafe(64)  # 64 bytes = 512 bits
   ```

2. **Short Access Token Lifetime:**
   ```python
   access_token_expire_minutes=15  # 15 minutes max
   ```

3. **Longer Refresh Token Lifetime:**
   ```python
   refresh_token_expire_days=7  # 7 days typical
   ```

4. **Store Refresh Tokens Securely:**
   ```python
   # Store refresh token hash in database
   import hashlib
   token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
   await store_refresh_token(user_id, token_hash)
   ```

5. **Implement Token Revocation:**
   ```python
   # Blacklist for revoked tokens
   revoked_tokens = set()

   async def revoke_token(token):
       revoked_tokens.add(token)

   async def is_token_revoked(token):
       return token in revoked_tokens
   ```

---

## Security Best Practices

### 1. Defense in Depth

Use multiple security layers:

```python
async def secure_api_endpoint(request):
    # Layer 1: Rate limiting
    if not await check_rate_limit(request):
        return rate_limit_error()

    # Layer 2: Authentication
    session = await get_current_session(request)
    if not session:
        return unauthorized_error()

    # Layer 3: MFA verification (for sensitive operations)
    if requires_mfa and not session.data.get("mfa_verified"):
        return require_mfa_error()

    # Layer 4: Authorization
    if not has_permission(session.user_id, "write:data"):
        return forbidden_error()

    # Layer 5: Input validation
    data = validate_input(request.json())

    # Process request
    return handle_request(data)
```

### 2. Secure Configuration

```python
# Use environment variables for secrets
import os

# NEVER hardcode secrets
JWT_SECRET = os.environ["JWT_SECRET_KEY"]
DB_PASSWORD = os.environ["DATABASE_PASSWORD"]
REDIS_URL = os.environ["REDIS_URL"]

# Use strong random secrets
import secrets
SESSION_SECRET = secrets.token_urlsafe(64)
```

### 3. HTTPS Only

```python
# In production, enforce HTTPS
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)

# Set secure cookie flags
response.set_cookie(
    "session_id",
    session_id,
    secure=True,  # HTTPS only
    httponly=True,  # No JavaScript access
    samesite="strict"  # CSRF protection
)
```

### 4. Security Headers

```python
from src.covet.security.headers import SecurityHeadersMiddleware

app.add_middleware(
    SecurityHeadersMiddleware,
    csp="default-src 'self'",
    hsts=True,
    frame_deny=True
)
```

### 5. Audit Logging

```python
import logging

security_logger = logging.getLogger("security")

# Log security events
security_logger.info(f"Login successful: user={user_id}, ip={ip}")
security_logger.warning(f"Failed login: user={user_id}, ip={ip}")
security_logger.error(f"MFA locked: user={user_id}")
security_logger.critical(f"Breach attempt detected: ip={ip}")
```

---

## Production Deployment

### Redis Setup

For production, use Redis for distributed rate limiting and sessions:

```bash
# Install Redis
apt-get install redis-server

# Configure Redis for security
redis-cli CONFIG SET requirepass "your-strong-password"

# Enable persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### Database Schema

Store security data in your database:

```sql
-- User authentication
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret_encrypted TEXT,
    backup_codes_encrypted TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Session storage (if not using Redis)
CREATE TABLE sessions (
    session_id VARCHAR(128) PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);

-- Audit log
CREATE TABLE security_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(50),
    user_id UUID REFERENCES users(id),
    ip_address INET,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
);
```

### Monitoring

```python
# Track security metrics
from prometheus_client import Counter, Histogram

login_attempts = Counter("login_attempts_total", "Total login attempts", ["status"])
mfa_verifications = Counter("mfa_verifications_total", "MFA verifications", ["status"])
rate_limit_hits = Counter("rate_limit_hits_total", "Rate limit violations")
password_resets = Counter("password_resets_total", "Password resets")

# Use in code
login_attempts.labels(status="success").inc()
mfa_verifications.labels(status="failed").inc()
```

### Environment Variables

```bash
# .env file
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://:password@localhost:6379/0
MFA_ISSUER=YourAppName
RATE_LIMIT_ENABLED=true
PASSWORD_MIN_LENGTH=12
SESSION_MAX_LIFETIME=28800
```

---

## Testing

Run the comprehensive security test suite:

```bash
# All security tests
pytest tests/security/test_auth_comprehensive.py -v

# Specific test categories
pytest tests/security/test_auth_comprehensive.py -k "mfa" -v
pytest tests/security/test_auth_comprehensive.py -k "password" -v
pytest tests/security/test_auth_comprehensive.py -k "session" -v
pytest tests/security/test_auth_comprehensive.py -k "rate_limit" -v

# Integration tests
pytest tests/security/test_auth_comprehensive.py::TestSecurityIntegration -v
```

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)
- [HaveIBeenPwned API](https://haveibeenpwned.com/API/v3)

---

## Support

For security issues, please email security@covetpy.dev or open a confidential security advisory on GitHub.

**DO NOT** open public issues for security vulnerabilities.
