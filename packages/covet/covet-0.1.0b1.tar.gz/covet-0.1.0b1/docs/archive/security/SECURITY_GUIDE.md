# CovetPy Security Guide

## Quick Start

### Basic Security Setup

```python
from covet import Covet
from covet.security import SecurityManager, SecurityConfig, JWTConfig

# Create app with security
app = Covet()

# Configure security
security_config = SecurityConfig(
    jwt=JWTConfig(
        algorithm="EdDSA",
        expiration=3600,
        issuer="my-app",
    ),
    force_https=True,
    debug=False,
)

# Initialize security manager
security = SecurityManager(security_config)

# Apply security middleware
from covet.security.middleware import SecurityMiddleware
app.add_middleware(SecurityMiddleware(security))

# Protected endpoint
@app.api('/protected')
@app.require_auth()
async def protected_endpoint(request):
    user = request.user  # Available after authentication
    return {"message": f"Hello {user.username}"}

if __name__ == "__main__":
    app.run()
```

## Authentication

### JWT Authentication

#### Configuration
```python
from covet.security import JWTConfig

jwt_config = JWTConfig(
    algorithm="EdDSA",  # Ed25519 for best security and performance
    expiration=3600,    # 1 hour
    refresh_expiration=86400,  # 24 hours for refresh tokens
    issuer="my-application",
    audience=["api-users"],
    allow_refresh=True,
    blacklist_enabled=True,
)
```

#### Usage
```python
from covet.security import AuthRequest

# Authenticate with JWT
auth_request = AuthRequest.jwt(token="eyJ0eXAiOiJKV1QiLCJhbGciOiJFZERTQSJ9...")
result = await security.authenticate(auth_request)

if result.user:
    print(f"Authenticated user: {result.user.username}")
else:
    print("Authentication failed")

# Generate token for user
user = User(id="123", username="john_doe")
token = await security.auth.generate_token(user)
```

### OAuth2 Authentication

```python
from covet.security import OAuth2Config, AuthRequest

oauth2_config = OAuth2Config(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://yourapp.com/callback",
    scope=["openid", "profile", "email"],
    provider="google",  # or "github", "microsoft", etc.
)

# Handle OAuth2 callback
@app.api('/auth/callback')
async def oauth_callback(request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    
    auth_request = AuthRequest.oauth2(code=code, state=state)
    result = await security.authenticate(auth_request)
    
    if result.user:
        # Create session or return JWT
        session = await security.create_session(result.user)
        return {"token": result.token, "session_id": session.id}
    else:
        return {"error": "Authentication failed"}, 401
```

### API Key Authentication

```python
from covet.security import APIKeyConfig, AuthRequest

# Configure API key authentication
api_key_config = APIKeyConfig(
    header_name="X-API-Key",  # or "Authorization"
    prefix="Bearer",  # optional prefix
    algorithm="SHA256",  # hashing algorithm
)

# Authenticate with API key
api_key = request.headers.get("X-API-Key")
auth_request = AuthRequest.api_key(key=api_key)
result = await security.authenticate(auth_request)
```

### Multi-Factor Authentication (MFA)

```python
from covet.security import MFAConfig, AuthRequest

mfa_config = MFAConfig(
    totp_enabled=True,
    sms_enabled=True,
    backup_codes_count=10,
    require_mfa_for_admin=True,
)

# Two-step authentication process
# Step 1: Primary authentication
primary_auth = AuthRequest.credentials(username="john", password="secret")
primary_result = await security.authenticate(primary_auth)

if primary_result.mfa_required:
    # Step 2: MFA authentication
    mfa_code = "123456"  # From TOTP app or SMS
    mfa_auth = AuthRequest.mfa(
        primary_token=primary_result.token,
        mfa_code=mfa_code
    )
    final_result = await security.authenticate(mfa_auth)
```

## Authorization

### Role-Based Access Control (RBAC)

```python
from covet.security import Permission, Role, AuthzContext

# Define permissions
create_post = Permission("posts", "create")
read_post = Permission("posts", "read")
delete_post = Permission("posts", "delete")

# Create roles
editor_role = Role("editor", "Content Editor")
editor_role.add_permission(create_post)
editor_role.add_permission(read_post)

admin_role = Role("admin", "Administrator")
admin_role.add_permission(create_post)
admin_role.add_permission(read_post)
admin_role.add_permission(delete_post)

# Store roles in authorization manager
await security.authz.create_role(editor_role)
await security.authz.create_role(admin_role)

# Check authorization
@app.api('/posts', methods=['POST'])
@app.require_auth()
@app.require_permission("posts", "create")
async def create_post_endpoint(request):
    # This endpoint requires authentication and "posts:create" permission
    return {"message": "Post created"}

# Manual authorization check
context = AuthzContext(
    user_id=user.id,
    roles=user.roles,
    attributes={"department": "marketing"}
)

result = await security.authorize(context, create_post)
if result.is_allowed():
    # User can create posts
    pass
else:
    # Access denied
    return {"error": "Access denied"}, 403
```

### Attribute-Based Access Control (ABAC)

```python
from covet.security import AuthzContext, Permission

# Complex authorization with attributes
context = AuthzContext(user_id="user123")
context.add_attribute("department", "finance")
context.add_attribute("clearance_level", "confidential")
context.add_attribute("location", "headquarters")
context.add_request_context("ip_address", "192.168.1.1")
context.add_request_context("time_of_day", "business_hours")
context.add_environment("system_mode", "normal")

# Define permission with constraints
sensitive_data_permission = Permission("financial_data", "read") \
    .with_constraint("clearance_level:confidential") \
    .with_constraint("location:headquarters") \
    .with_constraint("business_hours_only")

result = await security.authorize(context, sensitive_data_permission)
```

### Custom Authorization Policies

```python
from covet.security.authz.policy import PolicyEngine, Policy

# Define custom policy
policy_code = """
def evaluate(context, permission):
    # Custom business logic
    if permission.resource == "sensitive_data":
        if context.attributes.get("clearance_level") != "top_secret":
            return AuthzDecision.Deny, "Insufficient clearance level"
        
        if context.request_context.get("location") not in ["secure_facility"]:
            return AuthzDecision.Deny, "Access only allowed from secure facility"
    
    return AuthzDecision.Allow, "Policy approved"
"""

policy = Policy("sensitive_data_policy", policy_code, priority=100)
await security.authz.policy.add_policy(policy)
```

## Input Validation

### Basic Validation

```python
from covet.security import ValidationRule, ValidationType

# Define validation rules
validation_rules = [
    ValidationRule("email", "email", ValidationType.Email).required(),
    ValidationRule("password", "password", ValidationType.String(
        min_length=8,
        max_length=128,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+"
    )).required(),
    ValidationRule("age", "age", ValidationType.Number(
        min_value=18,
        max_value=120,
        integer_only=True
    )).required(),
    ValidationRule("website", "website", ValidationType.Url),
    ValidationRule("content", "content", ValidationType.XssSafe).required(),
]

# Validate input data
@app.api('/register', methods=['POST'])
async def register_user(request):
    data = await request.json()
    
    # Validate input
    result = await security.validate_input(data, validation_rules)
    
    if not result.is_valid():
        return {
            "error": "Validation failed",
            "details": result.error_messages()
        }, 400
    
    # Process valid data
    user = create_user(data)
    return {"message": "User created successfully"}
```

### Custom Validation

```python
from covet.security import ValidationRule, ValidationType

# Custom regex validation
custom_rule = ValidationRule(
    "product_code",
    "product_code",
    ValidationType.Custom(pattern=r"^PROD-[A-Z]{3}-\d{6}$")
).required().with_error_message("Invalid product code format")

# SQL injection protection
sql_safe_rule = ValidationRule(
    "search_query",
    "search_query",
    ValidationType.SqlSafe
).with_error_message("Potentially dangerous SQL detected")

# Command injection protection
command_safe_rule = ValidationRule(
    "filename",
    "filename",
    ValidationType.CommandSafe
).with_error_message("Invalid filename characters")
```

### Input Sanitization

```python
from covet.security import SanitizationOptions

# Basic sanitization
user_input = "<script>alert('xss')</script>Hello World & Co."
clean_input = await security.sanitize_input(user_input)
# Result: "Hello World &amp; Co."

# Custom sanitization options
sanitization_options = SanitizationOptions(
    strip_html=True,
    encode_html=True,
    remove_sql_injection=True,
    remove_scripts=True,
    normalize_whitespace=True,
    to_lowercase=False,
    trim=True,
)

clean_input = await security.sanitize_input(user_input, sanitization_options)
```

## Rate Limiting

### Basic Rate Limiting

```python
from covet.security import RateLimitConfig, RateLimitKey

# Configure rate limiting
rate_limit_config = RateLimitConfig(
    default_rpm=60,      # 60 requests per minute
    default_rph=1000,    # 1000 requests per hour
    default_burst=10,    # Allow burst of 10 requests
    ddos_protection=True,
    ddos_threshold=1000, # DDoS threshold
    whitelist=["127.0.0.1", "::1"],  # Localhost whitelist
)

# Check rate limit
@app.api('/api/data')
async def get_data(request):
    # Rate limit by IP address
    client_ip = request.client.host
    rate_key = RateLimitKey.from_ip(client_ip)
    
    status = await security.check_rate_limit(rate_key)
    
    if not status.allowed:
        return {
            "error": "Rate limit exceeded",
            "retry_after": status.retry_after.total_seconds()
        }, 429
    
    # Add rate limit headers
    response_headers = {
        "X-RateLimit-Limit": str(status.limit),
        "X-RateLimit-Remaining": str(status.remaining),
        "X-RateLimit-Reset": str(int(status.reset_time.timestamp())),
    }
    
    return {"data": "some data"}, 200, response_headers
```

### Advanced Rate Limiting

```python
from covet.security import RateLimitRule, RateLimitKey

# Custom rate limiting rules
premium_rule = RateLimitRule(
    key_pattern="apikey:premium*",
    requests_per_minute=500,
    requests_per_hour=10000,
    burst_size=50,
).with_priority(100)

admin_rule = RateLimitRule(
    key_pattern="user:admin*",
    requests_per_minute=1000,
    requests_per_hour=50000,
    burst_size=100,
).with_priority(200)

# Add custom rules
await security.rate_limiter.add_rule(premium_rule)
await security.rate_limiter.add_rule(admin_rule)

# Rate limit by user ID
@app.api('/user/profile')
@app.require_auth()
async def get_user_profile(request):
    rate_key = RateLimitKey.from_user_id(request.user.id)
    status = await security.check_rate_limit(rate_key)
    
    if not status.allowed:
        return {"error": "User rate limit exceeded"}, 429
    
    return {"profile": request.user.profile}

# Rate limit by API key
@app.api('/api/premium-data')
async def get_premium_data(request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return {"error": "API key required"}, 401
    
    rate_key = RateLimitKey.from_api_key(api_key)
    status = await security.check_rate_limit(rate_key)
    
    if not status.allowed:
        return {"error": "API key rate limit exceeded"}, 429
    
    return {"premium_data": "secret data"}
```

## Session Management

### Basic Session Management

```python
from covet.security import SessionConfig

session_config = SessionConfig(
    expiration=3600,     # 1 hour
    max_sessions=5,      # Max concurrent sessions per user
    secure_cookies=True, # HTTPS only
    http_only=True,      # No JavaScript access
    same_site="Strict",  # CSRF protection
)

# Create session
@app.api('/login', methods=['POST'])
async def login(request):
    data = await request.json()
    
    # Authenticate user
    auth_request = AuthRequest.credentials(
        username=data['username'],
        password=data['password']
    )
    result = await security.authenticate(auth_request)
    
    if result.user:
        # Create session
        session = await security.create_session(result.user, {
            "ip_address": request.client.host,
            "user_agent": request.headers.get("User-Agent"),
            "login_time": datetime.utcnow().isoformat(),
        })
        
        # Set session cookie
        response_headers = {
            "Set-Cookie": f"session_id={session.id}; HttpOnly; Secure; SameSite=Strict"
        }
        
        return {"message": "Login successful"}, 200, response_headers
    else:
        return {"error": "Invalid credentials"}, 401

# Use session
@app.api('/dashboard')
async def dashboard(request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return {"error": "No session"}, 401
    
    session = await security.get_session(session_id)
    if not session or session.is_expired():
        return {"error": "Session expired"}, 401
    
    # Update session activity
    await security.session_manager.update_activity(session_id)
    
    return {"dashboard": "data", "user": session.user}

# Logout
@app.api('/logout', methods=['POST'])
async def logout(request):
    session_id = request.cookies.get("session_id")
    if session_id:
        await security.destroy_session(session_id)
    
    response_headers = {
        "Set-Cookie": "session_id=; expires=Thu, 01 Jan 1970 00:00:00 GMT"
    }
    
    return {"message": "Logged out"}, 200, response_headers
```

## Cryptographic Operations

### Encryption and Decryption

```python
# Encrypt sensitive data
sensitive_data = b"confidential information"
encryption_result = await security.encrypt(sensitive_data)

# Store encrypted data (encryption_result contains ciphertext, nonce, key_id)
store_in_database({
    "ciphertext": encryption_result.ciphertext.hex(),
    "nonce": encryption_result.nonce.hex(),
    "algorithm": encryption_result.algorithm,
    "key_id": encryption_result.key_id,
})

# Decrypt data
retrieved_data = get_from_database()
encryption_result = EncryptionResult(
    ciphertext=bytes.fromhex(retrieved_data["ciphertext"]),
    nonce=bytes.fromhex(retrieved_data["nonce"]),
    algorithm=retrieved_data["algorithm"],
    key_id=retrieved_data["key_id"],
)

decrypted_data = await security.decrypt(encryption_result)
```

### Password Hashing

```python
# Hash password during registration
@app.api('/register', methods=['POST'])
async def register(request):
    data = await request.json()
    
    # Hash password
    password_hash = await security.hash_password(data['password'])
    
    # Store user with hashed password
    user = User(
        username=data['username'],
        password_hash=password_hash,
    )
    store_user(user)
    
    return {"message": "User registered"}

# Verify password during login
@app.api('/login', methods=['POST'])
async def login(request):
    data = await request.json()
    
    # Get user from database
    user = get_user_by_username(data['username'])
    if not user:
        return {"error": "Invalid credentials"}, 401
    
    # Verify password
    is_valid = await security.verify_password(data['password'], user.password_hash)
    
    if is_valid:
        # Create session or return token
        token = await security.auth.generate_token(user)
        return {"token": token}
    else:
        return {"error": "Invalid credentials"}, 401
```

## Security Headers

### Automatic Headers

```python
from covet.security import HeadersManager, CORSConfig, CSPConfig

# Configure CORS
cors_config = CORSConfig(
    allow_origins=["https://myapp.com", "https://app.mycompany.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    allow_credentials=True,
    max_age=86400,  # 24 hours
)

# Configure Content Security Policy
csp_config = CSPConfig(
    default_src=["'self'"],
    script_src=["'self'", "'unsafe-inline'", "https://cdn.mycompany.com"],
    style_src=["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    img_src=["'self'", "data:", "https://images.mycompany.com"],
    font_src=["'self'", "https://fonts.gstatic.com"],
    connect_src=["'self'", "https://api.mycompany.com"],
    frame_ancestors=["'none'"],
    base_uri=["'self'"],
    form_action=["'self'"],
)

# Headers are automatically applied by SecurityMiddleware
headers_manager = HeadersManager(
    cors_config=cors_config,
    csp_config=csp_config,
    security_headers=True,
)

# Manual header application
@app.api('/custom-headers')
async def custom_headers_endpoint(request):
    data = {"message": "Custom headers applied"}
    
    # Get security headers
    security_headers = headers_manager.get_security_headers(
        request_headers=dict(request.headers)
    )
    
    return data, 200, security_headers
```

## Secrets Management

### Basic Secrets

```python
from covet.security import SecretsManager

# Store secrets
await security.secrets_manager.store_secret("database_url", "postgresql://...")
await security.secrets_manager.store_secret("api_key", "sk-1234567890")

# Retrieve secrets
database_url = await security.secrets_manager.get_secret("database_url")
api_key = await security.secrets_manager.get_secret("api_key")

# Use in application
import asyncpg

async def get_database_connection():
    db_url = await security.secrets_manager.get_secret("database_url")
    return await asyncpg.connect(db_url)
```

### Secret Rotation

```python
# Automatic secret rotation
@app.api('/admin/rotate-secrets', methods=['POST'])
@app.require_auth()
@app.require_permission("admin", "manage_secrets")
async def rotate_secrets(request):
    data = await request.json()
    secret_name = data.get('secret_name')
    
    if secret_name:
        # Rotate specific secret
        new_secret = await security.secrets_manager.rotate_secret(secret_name)
        return {"message": f"Secret '{secret_name}' rotated", "new_version": new_secret.version}
    else:
        # Rotate all eligible secrets
        rotated_secrets = await security.secrets_manager.rotate_all_secrets()
        return {"message": f"Rotated {len(rotated_secrets)} secrets"}
```

## Audit Logging

### Security Event Logging

```python
from covet.security import AuditLevel

# Manual audit logging
await security.audit_logger.log_security_event(
    event_type="sensitive_data_access",
    severity=AuditLevel.INFO,
    user_id=request.user.id,
    session_id=session.id,
    ip_address=request.client.host,
    user_agent=request.headers.get("User-Agent"),
    details={
        "resource": "financial_reports",
        "action": "download",
        "file_name": "q4_2023_report.pdf",
        "file_size": 2048576,
    }
)

# Authentication events (automatically logged)
await security.audit_logger.log_auth_event(
    event_type="login_attempt",
    user_id=user.id,
    success=True,
    ip_address=request.client.host,
    details={
        "method": "password",
        "user_agent": request.headers.get("User-Agent"),
        "location": get_location_from_ip(request.client.host),
    }
)
```

### Query Audit Logs

```python
# Search audit logs
@app.api('/admin/audit-logs')
@app.require_auth()
@app.require_permission("admin", "view_audit_logs")
async def get_audit_logs(request):
    filters = {
        "start_date": request.query_params.get("start_date"),
        "end_date": request.query_params.get("end_date"),
        "user_id": request.query_params.get("user_id"),
        "event_type": request.query_params.get("event_type"),
        "severity": request.query_params.get("severity"),
    }
    
    logs = await security.audit_logger.query_logs(filters)
    
    return {
        "logs": [log.to_dict() for log in logs],
        "total": len(logs),
    }
```

## Middleware Integration

### Automatic Security

```python
from covet.security.middleware import (
    SecurityMiddleware,
    AuthMiddleware,
    RateLimitMiddleware,
    ValidationMiddleware,
    HeadersMiddleware,
)

app = CovetPy()

# Apply all security middleware
app.add_middleware(SecurityMiddleware(
    security_manager=security,
    enable_auth=True,
    enable_rate_limiting=True,
    enable_validation=True,
    enable_headers=True,
    enable_audit_logging=True,
))

# Or apply individual middleware
app.add_middleware(AuthMiddleware(security.auth))
app.add_middleware(RateLimitMiddleware(security.rate_limiter))
app.add_middleware(ValidationMiddleware(security.validator))
app.add_middleware(HeadersMiddleware(security.headers_manager))

# Endpoints automatically protected
@app.api('/protected-endpoint')
async def protected(request):
    # Authentication, rate limiting, validation, and headers
    # are automatically handled by middleware
    return {"message": "This endpoint is fully protected"}
```

### Custom Middleware

```python
from covet.middleware import BaseMiddleware

class CustomSecurityMiddleware(BaseMiddleware):
    def __init__(self, security_manager):
        self.security = security_manager
    
    async def __call__(self, request, call_next):
        # Pre-request security checks
        await self.check_request_security(request)
        
        # Process request
        response = await call_next(request)
        
        # Post-request security actions
        await self.log_response_security(request, response)
        
        return response
    
    async def check_request_security(self, request):
        # Custom security logic
        if request.path.startswith('/admin/'):
            # Additional security for admin endpoints
            await self.verify_admin_access(request)
    
    async def verify_admin_access(self, request):
        # Implement custom admin verification
        pass
    
    async def log_response_security(self, request, response):
        # Log security-relevant response information
        pass
```

## Testing Security

### Security Test Suite

```python
from covet.security.testing import SecurityTestSuite
import pytest

@pytest.fixture
async def security_manager():
    config = SecurityConfig(debug=True)  # Enable debug mode for testing
    manager = SecurityManager(config)
    await manager.initialize()
    return manager

@pytest.fixture
async def security_test_suite(security_manager):
    return SecurityTestSuite(security_manager)

class TestSecurity:
    async def test_authentication(self, security_test_suite):
        # Test all authentication methods
        results = await security_test_suite.test_authentication()
        assert all(result.passed for result in results)
    
    async def test_authorization(self, security_test_suite):
        # Test RBAC and ABAC
        results = await security_test_suite.test_authorization()
        assert all(result.passed for result in results)
    
    async def test_input_validation(self, security_test_suite):
        # Test against common attack vectors
        results = await security_test_suite.test_input_validation()
        assert all(result.passed for result in results)
    
    async def test_rate_limiting(self, security_test_suite):
        # Test rate limiting effectiveness
        results = await security_test_suite.test_rate_limiting()
        assert all(result.passed for result in results)
    
    async def test_cryptography(self, security_test_suite):
        # Test cryptographic operations
        results = await security_test_suite.test_cryptography()
        assert all(result.passed for result in results)
```

### Penetration Testing

```python
from covet.security.testing import PenetrationTester

async def run_security_assessment():
    pentest = PenetrationTester(security_manager)
    
    # Run comprehensive security assessment
    results = await pentest.run_comprehensive_test()
    
    # Generate security report
    report = pentest.generate_report(results)
    
    # Save report
    with open("security_assessment_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return results
```

## Deployment Security

### Production Configuration

```python
# Production security configuration
production_config = SecurityConfig(
    jwt=JWTConfig(
        algorithm="EdDSA",
        expiration=900,  # 15 minutes (shorter for production)
        refresh_expiration=86400,  # 24 hours
        issuer="production-app",
        blacklist_enabled=True,
    ),
    rate_limit=RateLimitConfig(
        default_rpm=60,  # Conservative limits
        ddos_protection=True,
        ddos_threshold=100,
        ddos_ban_duration=3600,  # 1 hour ban
    ),
    cors=CORSConfig(
        allow_origins=["https://myapp.com"],  # Specific origins only
        allow_credentials=True,
    ),
    session=SessionConfig(
        expiration=1800,  # 30 minutes
        max_sessions=3,   # Limit concurrent sessions
        secure_cookies=True,
        http_only=True,
        same_site="Strict",
    ),
    secrets=SecretConfig(
        provider="aws_secrets_manager",  # Use AWS Secrets Manager
        auto_rotation=True,
        rotation_interval=2592000,  # 30 days
    ),
    audit=AuditConfig(
        level=AuditLevel.INFO,
        storage="s3",  # Store in AWS S3
        retention_days=365,  # 1 year retention
        real_time_alerts=True,
    ),
    force_https=True,
    debug=False,
)

# Initialize for production
security = SecurityManager(production_config)
await security.initialize()
```

### Health Monitoring

```python
@app.api('/health/security')
async def security_health_check():
    health = await security.health_check()
    
    status_code = 200 if health["overall"] else 503
    
    return {
        "security_health": health,
        "timestamp": datetime.utcnow().isoformat(),
    }, status_code
```

This comprehensive guide covers all major aspects of the CovetPy security framework. For additional examples and advanced configurations, refer to the API documentation and the security architecture document.