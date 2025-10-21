# CovetPy Authentication System Guide

## Table of Contents
1. [Overview](#overview)
2. [OAuth2 Authentication](#oauth2-authentication)
3. [SAML Integration](#saml-integration)
4. [LDAP/Active Directory](#ldap-active-directory)
5. [Multi-Factor Authentication](#multi-factor-authentication)
6. [Session Management](#session-management)
7. [Password Policy](#password-policy)
8. [Middleware Integration](#middleware-integration)
9. [Security Best Practices](#security-best-practices)
10. [Production Deployment](#production-deployment)

## Overview

CovetPy's authentication system provides enterprise-grade authentication with support for:

- **OAuth2 2.0** (RFC 6749, RFC 7636 PKCE, RFC 7662, RFC 7009)
- **SAML 2.0** Service Provider with SSO/SLO
- **LDAP/Active Directory** authentication with connection pooling
- **Multi-Factor Authentication** (TOTP, SMS, Email, Backup Codes)
- **Session Management** with Redis backend
- **Password Policy** enforcement with breach detection

### Key Features

- ✅ RFC-compliant implementations
- ✅ Production-ready security
- ✅ Horizontal scalability (Redis-backed)
- ✅ Comprehensive audit logging
- ✅ Rate limiting and abuse prevention
- ✅ Integration with all CovetPy APIs

---

## OAuth2 Authentication

### Quick Start

```python
from covet.security.auth.oauth2_provider import OAuth2Provider, OAuth2Config, GrantType

# Configure OAuth2
config = OAuth2Config(
    authorization_code_lifetime=600,    # 10 minutes
    access_token_lifetime=3600,         # 1 hour
    refresh_token_lifetime=2592000,     # 30 days
    require_pkce=True,                  # Require PKCE for public clients
    use_jwt_tokens=False,               # Use opaque tokens
)

# Initialize provider
oauth2 = OAuth2Provider(config)

# Register OAuth2 client
client = await oauth2.register_client(
    client_id="my_app",
    client_name="My Application",
    is_confidential=True,
    allowed_grant_types={GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN},
    redirect_uris=["https://myapp.com/callback"],
    allowed_scopes={"read", "write", "profile"},
    client_secret="your_secure_secret",
)
```

### Supported Flows

#### 1. Authorization Code Flow (Recommended)

Most secure flow for web applications.

```python
# Step 1: Validate authorization request
is_valid, error, _ = await oauth2.create_authorization_request(
    client_id="my_app",
    redirect_uri="https://myapp.com/callback",
    scope="read write",
)

# Step 2: User approves, create authorization code
auth_code = await oauth2.create_authorization_code(
    client_id="my_app",
    user_id="user123",
    redirect_uri="https://myapp.com/callback",
    scopes={"read", "write"},
)

# Step 3: Exchange code for token
token, error = await oauth2.exchange_authorization_code(
    client_id="my_app",
    client_secret="your_secure_secret",
    code=auth_code.code,
    redirect_uri="https://myapp.com/callback",
)
```

#### 2. Authorization Code with PKCE

For public clients (mobile apps, SPAs) that cannot securely store secrets.

```python
from covet.security.auth.oauth2_provider import PKCEChallenge, PKCEMethod

# Client generates PKCE challenge
pkce = PKCEChallenge.generate(PKCEMethod.S256)

# Create authorization code with PKCE
auth_code = await oauth2.create_authorization_code(
    client_id="mobile_app",
    user_id="user123",
    redirect_uri="myapp://callback",
    scopes={"read"},
    code_challenge=pkce.code_challenge,
    code_challenge_method=PKCEMethod.S256,
)

# Exchange code with verifier
token, error = await oauth2.exchange_authorization_code(
    client_id="mobile_app",
    client_secret=None,  # Public client
    code=auth_code.code,
    redirect_uri="myapp://callback",
    code_verifier=pkce.code_verifier,
)
```

#### 3. Client Credentials Flow

For service-to-service authentication.

```python
# Request token with client credentials
token, error = await oauth2.client_credentials_grant(
    client_id="service_app",
    client_secret="service_secret",
    scope="api:read api:write",
)
```

#### 4. Refresh Token Flow

Renew expired access tokens.

```python
# Use refresh token to get new access token
new_token, error = await oauth2.refresh_token_grant(
    client_id="my_app",
    client_secret="your_secure_secret",
    refresh_token=old_token.refresh_token,
)
```

### Token Validation

```python
# Validate access token
is_valid, token_obj = await oauth2.validate_token(access_token)

if is_valid:
    user_id = token_obj.user_id
    scopes = token_obj.scopes
    # Process request
```

### Token Introspection (RFC 7662)

```python
# Introspect token
introspection = await oauth2.introspect_token(
    token=access_token,
    client_id="resource_server",
    client_secret="resource_secret",
)

if introspection["active"]:
    print(f"Token belongs to: {introspection['username']}")
    print(f"Scopes: {introspection['scope']}")
```

### Token Revocation (RFC 7009)

```python
# Revoke token
success = await oauth2.revoke_token(
    token=access_token,
    client_id="my_app",
    client_secret="your_secure_secret",
)
```

---

## SAML Integration

### Service Provider Setup

```python
from covet.security.auth.saml_provider import SAMLProvider, SAMLConfig

# Configure SAML SP
config = SAMLConfig(
    sp_entity_id="https://myapp.com",
    idp_entity_id="https://idp.example.com",
    acs_url="https://myapp.com/auth/saml/acs",
    idp_sso_url="https://idp.example.com/sso",
    sp_private_key=open("sp-private-key.pem").read(),
    sp_certificate=open("sp-certificate.pem").read(),
    idp_certificate=open("idp-certificate.pem").read(),
    want_assertions_signed=True,
    sign_requests=True,
)

saml = SAMLProvider(config)
```

### SP-Initiated SSO

```python
# Step 1: Create authentication request
request_id, xml = saml.create_authn_request()

# Step 2: Redirect user to IdP
redirect_url = saml.build_authn_request_url(xml, relay_state="/dashboard")

# Step 3: Process SAML response (at ACS endpoint)
assertion, error = saml.parse_saml_response(saml_response)

if assertion and not error:
    user_id = assertion.subject
    attributes = assertion.attributes
    # Create session for user
```

### Generate SP Metadata

```python
# Generate metadata for IdP configuration
metadata_xml = saml.generate_sp_metadata()

# Save to file or serve via HTTP
with open("sp-metadata.xml", "w") as f:
    f.write(metadata_xml)
```

### Single Logout (SLO)

```python
# Initiate logout
request_id, xml = saml.create_logout_request(
    name_id=user_email,
    session_index=session_index,
)

# Redirect to IdP for logout
```

### IdP Configuration Examples

#### Okta
```yaml
Entity ID: https://myapp.com
ACS URL: https://myapp.com/auth/saml/acs
Name ID Format: EmailAddress
```

#### Azure AD
```yaml
Entity ID: https://myapp.com
Reply URL: https://myapp.com/auth/saml/acs
Sign on URL: https://myapp.com/login
```

---

## LDAP/Active Directory

### Basic Configuration

```python
from covet.security.auth.ldap_provider import LDAPProvider, LDAPConfig

# Configure LDAP
config = LDAPConfig(
    host="ldap.example.com",
    port=636,  # LDAPS
    use_ssl=True,
    base_dn="dc=example,dc=com",
    bind_dn="cn=admin,dc=example,dc=com",
    bind_password="admin_password",
    user_search_filter="(uid={username})",
    user_search_base="ou=users,dc=example,dc=com",
)

ldap = LDAPProvider(config)
```

### User Authentication

```python
# Authenticate user
user, error = await ldap.authenticate("john.doe", "password123")

if user:
    print(f"Authenticated: {user.full_name}")
    print(f"Email: {user.email}")
    print(f"Groups: {user.group_names}")
```

### Active Directory Configuration

```python
config = LDAPConfig(
    host="ad.example.com",
    port=636,
    use_ssl=True,
    base_dn="dc=example,dc=com",
    is_active_directory=True,  # Enable AD features
    ad_domain="EXAMPLE",
    user_search_filter="(sAMAccountName={username})",
    enable_nested_groups=True,  # Support nested groups
)
```

### Connection Pooling

```python
# Configure connection pool
config = LDAPConfig(
    # ... other settings
    pool_size=10,              # Max connections
    pool_keepalive=600,        # 10 minutes
    connect_timeout=10,
    receive_timeout=10,
)
```

---

## Multi-Factor Authentication

### TOTP (Time-Based OTP)

```python
from covet.security.auth.mfa_provider import MFAProvider, MFAConfig, MFAMethod

config = MFAConfig(
    totp_issuer="MyApp",
    totp_period=30,
    totp_digits=6,
)

mfa = MFAProvider(config)

# Enroll user in TOTP
secret, uri, qr_code = await mfa.enroll_totp(
    user_id="user123",
    account_name="user@example.com",
)

# Display QR code to user (they scan with authenticator app)

# Verify TOTP code
is_valid, error = await mfa.verify_mfa(
    user_id="user123",
    method=MFAMethod.TOTP,
    code="123456",
)
```

### SMS OTP

```python
# Send SMS OTP
success, error = await mfa.sms.generate_and_send(
    user_id="user123",
    phone_number="+1234567890",
)

# Verify SMS code
is_valid, error = await mfa.sms.verify("user123", "123456")
```

### Email OTP

```python
# Send email OTP
success, error = await mfa.email.generate_and_send(
    user_id="user123",
    email="user@example.com",
)

# Verify email code
is_valid, error = await mfa.email.verify("user123", "ABCD1234")
```

### Backup Codes

```python
# Generate backup codes
codes = mfa.backup_codes.generate_codes("user123")

# Display codes to user (they should save them)
for code in codes:
    print(code)  # e.g., "A3B4-C5D6"

# Verify backup code
is_valid, error = await mfa.backup_codes.verify_code("user123", "A3B4-C5D6")
```

### Device Trust

```python
# Trust device after MFA
device_id = await mfa.trust_device(
    user_id="user123",
    device_fingerprint="fingerprint_hash",
    device_name="Chrome on MacBook",
)

# Check if device is trusted
is_trusted = await mfa.is_device_trusted(
    user_id="user123",
    device_fingerprint="fingerprint_hash",
)
```

---

## Session Management

### Basic Session Management

```python
from covet.security.auth.session_manager import SessionManager, SessionConfig

config = SessionConfig(
    redis_url="redis://localhost:6379/0",
    session_lifetime=3600,        # 1 hour
    idle_timeout=1800,            # 30 minutes
    remember_me_enabled=True,
)

sessions = SessionManager(config)

# Create session
session = await sessions.create_session(
    user_id="user123",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    remember_me=False,
)

# Validate session
session = await sessions.get_session(
    session_id=session_id,
    ip_address=client_ip,
    user_agent=client_ua,
)
```

### Session Security Features

```python
config = SessionConfig(
    check_ip_address=True,         # Prevent hijacking
    check_user_agent=True,          # Detect session theft
    max_concurrent_sessions=5,      # Limit sessions per user
    regenerate_on_login=True,       # Prevent fixation
)
```

### Remember Me

```python
# Create session with remember-me
session = await sessions.create_session(
    user_id="user123",
    remember_me=True,  # Extended lifetime
)

# Login using remember token
new_session = await sessions.remember_me_login(remember_token)
```

### Session Regeneration

```python
# Regenerate session ID after privilege change
new_session = await sessions.regenerate_session_id(old_session_id)
```

---

## Password Policy

### Configuration

```python
from covet.security.auth.password_policy import PasswordPolicy, PasswordPolicyConfig

config = PasswordPolicyConfig(
    min_length=12,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True,
    min_entropy=40.0,
    breach_detection_enabled=True,  # Check Have I Been Pwned
    password_history_count=5,
    max_failed_attempts=5,
    lockout_duration=900,  # 15 minutes
)

policy = PasswordPolicy(config)
```

### Password Validation

```python
# Validate password
result = await policy.validate_password(
    password="UserPassword123!",
    username="john.doe",
    email="john@example.com",
)

if result.is_valid:
    print(f"Strength: {result.strength}")
    print(f"Score: {result.score}/100")
else:
    print("Errors:")
    for error in result.errors:
        print(f"  - {error}")
```

### Password Hashing

```python
# Hash password (Argon2id or PBKDF2)
password_hash = policy.hash_password("SecurePassword123!")

# Verify password
is_valid = policy.verify_password("SecurePassword123!", password_hash)
```

### Breach Detection

```python
# Check if password has been breached
is_breached, count = await policy.breach_detector.check_breach("password123")

if is_breached:
    print(f"Password found in {count} data breaches!")
```

---

## Middleware Integration

### Complete Authentication Middleware

```python
from covet.security.auth.middleware import AuthenticationMiddleware

# Initialize middleware with all providers
middleware = AuthenticationMiddleware(
    app,
    oauth2_provider=oauth2,
    saml_provider=saml,
    session_manager=sessions,
    mfa_provider=mfa,
    exempt_paths={"/health", "/login", "/register"},
    require_mfa_paths={"/admin/*", "/sensitive/*"},
)

# Use in ASGI application
app = middleware
```

### OAuth2 Middleware

```python
from covet.security.auth.middleware import OAuth2Middleware

middleware = OAuth2Middleware(
    app,
    provider=oauth2,
    exempt_paths={"/public/*"},
    required_scopes={
        "/api/users": ["users:read"],
        "/api/admin": ["admin:write"],
    },
)
```

### Session Middleware

```python
from covet.security.auth.middleware import SessionMiddleware

middleware = SessionMiddleware(
    app,
    session_manager=sessions,
    exempt_paths={"/login", "/register"},
)
```

---

## Security Best Practices

### 1. Token Security

- ✅ Use HTTPS only in production
- ✅ Set short token lifetimes (1 hour for access tokens)
- ✅ Implement token rotation for refresh tokens
- ✅ Use PKCE for public clients
- ✅ Validate redirect URIs strictly

### 2. Session Security

- ✅ Use secure cookies (HTTPOnly, Secure, SameSite)
- ✅ Regenerate session IDs after login
- ✅ Implement idle and absolute timeouts
- ✅ Validate IP address and User-Agent
- ✅ Use Redis for distributed sessions

### 3. Password Security

- ✅ Use Argon2id for password hashing
- ✅ Enforce strong password policies
- ✅ Check passwords against breach databases
- ✅ Implement account lockout
- ✅ Maintain password history

### 4. MFA Security

- ✅ Use TOTP with 30-second window
- ✅ Rate limit OTP verification attempts
- ✅ Implement backup codes
- ✅ Allow device trust for convenience
- ✅ Require MFA for sensitive operations

### 5. LDAP Security

- ✅ Use LDAPS (LDAP over TLS)
- ✅ Validate TLS certificates
- ✅ Sanitize inputs to prevent injection
- ✅ Use connection pooling
- ✅ Implement connection timeouts

---

## Production Deployment

### Prerequisites

```bash
# Install dependencies
pip install covetpy[auth]

# Or install specific dependencies
pip install PyJWT cryptography ldap3 redis qrcode httpx argon2-cffi
```

### Environment Configuration

```bash
# OAuth2
OAUTH2_ISSUER=https://auth.example.com
OAUTH2_ACCESS_TOKEN_LIFETIME=3600
OAUTH2_REFRESH_TOKEN_LIFETIME=2592000

# Redis
REDIS_URL=redis://redis:6379/0

# LDAP
LDAP_HOST=ldap.example.com
LDAP_PORT=636
LDAP_USE_SSL=true
LDAP_BASE_DN=dc=example,dc=com

# SAML
SAML_SP_ENTITY_ID=https://app.example.com
SAML_IDP_ENTITY_ID=https://idp.example.com
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth
        image: myapp/auth:latest
        env:
        - name: REDIS_URL
          value: redis://redis-service:6379/0
        ports:
        - containerPort: 8000
```

### Monitoring

```python
# Get statistics
oauth2_stats = oauth2._stats
session_stats = sessions.get_stats()
mfa_stats = mfa.get_stats()

# Log to monitoring system
logger.info("auth_stats", extra={
    "oauth2": oauth2_stats,
    "sessions": session_stats,
    "mfa": mfa_stats,
})
```

### Health Checks

```python
async def health_check():
    """Health check endpoint."""
    checks = {
        "oauth2": len(oauth2._clients) >= 0,
        "redis": await sessions.store._get_redis() is not None,
        "ldap": ldap._servers is not None,
    }

    return {
        "status": "healthy" if all(checks.values()) else "degraded",
        "checks": checks,
    }
```

---

## Performance Tuning

### OAuth2
- Token generation: <50ms
- Token validation: <5ms
- Use JWT for stateless validation

### Sessions
- Session validation: <5ms with Redis
- Use connection pooling
- Implement session caching

### Password Hashing
- Argon2: ~100-200ms (configurable)
- Adjust time_cost and memory_cost based on requirements

### LDAP
- Connection pooling: Reuse connections
- Caching: Cache user lookups for 5 minutes
- Timeout: Set appropriate timeouts

---

## Troubleshooting

### OAuth2 Issues

**Invalid client error**
- Verify client_id and client_secret
- Check client is registered
- Ensure grant type is allowed

**Invalid redirect_uri**
- Must exactly match registered URI
- Include protocol (https://)
- No wildcards allowed

### SAML Issues

**Signature validation failed**
- Verify IdP certificate is correct
- Check clock sync between SP and IdP
- Ensure assertions are signed

**Attribute mapping**
- Check IdP attribute names
- Configure attribute_map correctly

### LDAP Issues

**Connection timeout**
- Check LDAP server is reachable
- Verify port (389 for LDAP, 636 for LDAPS)
- Check firewall rules

**Authentication failed**
- Verify bind DN and password
- Check user search filter
- Ensure user exists in directory

---

## Support

For issues or questions:
- GitHub: https://github.com/covetpy/covetpy
- Documentation: https://docs.covetpy.dev
- Email: support@covetpy.dev

---

**Last Updated:** 2025-10-11
**Version:** 1.0.0
