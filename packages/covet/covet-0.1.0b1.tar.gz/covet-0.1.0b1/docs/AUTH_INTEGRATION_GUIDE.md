# CovetPy Authentication Integration Guide

## Overview

The CovetPy authentication system provides a Flask-like API for securing your web applications with JWT tokens and secure password hashing. This guide covers the new simplified API designed for easy integration.

## Quick Start

### Basic Setup

```python
from covet import Covet
from covet.auth import Auth, login_required

# Create app
app = Covet()

# Setup authentication
auth = Auth(app, secret_key='your-secret-key-here')

@app.route('/login', methods=['POST'])
async def login(request):
    data = await request.json()

    # Verify credentials (implement your logic)
    if verify_user_credentials(data['username'], data['password']):
        token = auth.create_token(user_id=data['username'])
        return {'token': token}

    return {'error': 'Invalid credentials'}, 401

@app.route('/protected')
@login_required
async def protected_route(request):
    # User info automatically available
    return {
        'user_id': request.user_id,
        'username': request.username,
        'message': 'Access granted'
    }

if __name__ == '__main__':
    app.run()
```

## Security Architecture

### Threat Model

The authentication system is designed to protect against:

1. **Password Attacks**
   - Brute force: Scrypt hashing with high work factor
   - Rainbow tables: Unique salt per password
   - Timing attacks: Constant-time comparison

2. **Token Attacks**
   - Token theft: Short expiration, HTTPS only
   - Token manipulation: Cryptographic signature
   - Replay attacks: Token blacklist on logout
   - Session hijacking: Include user context in token

3. **Application Attacks**
   - XSS: Token in Authorization header (not cookies)
   - CSRF: Not vulnerable (stateless tokens)
   - SQL Injection: Parameterized queries (separate concern)

### Security Best Practices

#### 1. Secret Key Management

**CRITICAL**: Never hardcode secret keys in production.

```python
import os

# Development
if os.environ.get('ENV') == 'development':
    SECRET_KEY = 'dev-key-change-in-production'
else:
    # Production - load from environment or secrets manager
    SECRET_KEY = os.environ['SECRET_KEY']
    if not SECRET_KEY or len(SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters")

auth = Auth(app, secret_key=SECRET_KEY)
```

**Recommendations:**
- Use at least 64 random characters for HS256
- Use RSA 2048-bit keys for RS256 (multi-service architectures)
- Rotate keys every 90 days
- Store in environment variables or AWS Secrets Manager/HashiCorp Vault
- Never commit keys to version control

#### 2. Password Security

```python
from covet.auth import hash_password, verify_password, check_password_strength

# Registration
password = request.form['password']

# Validate strength
is_strong, issues = check_password_strength(password)
if not is_strong:
    return {'error': 'Weak password', 'issues': issues}, 400

# Hash password (Scrypt with secure defaults)
password_hash = hash_password(password)

# Store password_hash in database (never store plain text)
user = User(username=username, password_hash=password_hash)
db.save(user)

# Login
if verify_password(input_password, user.password_hash):
    # Password correct - create token
    token = auth.create_token(user_id=user.id)
```

**Security Features:**
- Scrypt algorithm (OWASP recommended)
- Work factor: N=2^14 (configurable)
- Automatic salt generation (32 bytes)
- Constant-time comparison
- Protection against GPU attacks

#### 3. Token Security

```python
# Short-lived access tokens
auth = Auth(
    app,
    secret_key=SECRET_KEY,
    access_token_expire_minutes=15,  # Short expiration
    refresh_token_expire_days=30      # Long-lived refresh
)

# Include relevant claims
token = auth.create_token(
    user_id=user.id,
    username=user.username,
    roles=user.roles,
    permissions=user.permissions
)

# Always verify on protected routes
@login_required
async def protected(request):
    # Token automatically verified
    # User context injected
    pass
```

**Token Lifecycle:**
1. **Login**: Issue access + refresh token
2. **API Calls**: Use access token in Authorization header
3. **Token Expires**: Use refresh token to get new access token
4. **Logout**: Revoke both tokens

#### 4. HTTPS Enforcement

```python
# Production configuration
if not os.environ.get('ENV') == 'development':
    # Enforce HTTPS
    @app.before_request
    def enforce_https(request):
        if not request.is_secure:
            return Response(
                content={'error': 'HTTPS required'},
                status_code=403
            )
```

**CRITICAL**: Always use HTTPS in production. JWT tokens are bearer tokens - anyone with the token can use it.

## API Reference

### Auth Class

```python
auth = Auth(
    app=None,                           # Covet app instance
    secret_key='your-secret-key',       # JWT signing key
    algorithm='HS256',                  # HS256, HS512, RS256, RS512
    access_token_expire_minutes=30,     # Access token TTL
    refresh_token_expire_days=30        # Refresh token TTL
)
```

#### Methods

**`create_token(user_id, username=None, roles=None, **claims) -> str`**

Create JWT access token.

```python
token = auth.create_token(
    user_id='123',
    username='john',
    roles=['user', 'admin'],
    permissions=['read:users', 'write:posts']
)
```

**`verify_token(token: str) -> dict`**

Verify and decode token.

```python
try:
    payload = auth.verify_token(token)
    user_id = payload['sub']
    roles = payload['roles']
except TokenExpiredError:
    # Handle expiration
    pass
except TokenInvalidError:
    # Handle invalid token
    pass
```

**`create_refresh_token(user_id: str) -> str`**

Create long-lived refresh token.

```python
refresh_token = auth.create_refresh_token(user_id='123')
# Store securely (httpOnly cookie or secure storage)
```

**`refresh_access_token(refresh_token: str) -> str`**

Create new access token from refresh token.

```python
try:
    new_access_token = auth.refresh_access_token(refresh_token)
except TokenExpiredError:
    # Refresh token expired - require re-login
    pass
```

**`revoke_token(token: str)`**

Revoke token (logout).

```python
auth.revoke_token(access_token)
auth.revoke_token(refresh_token)
```

**`hash_password(password: str) -> str`**

Hash password securely.

```python
hashed = auth.hash_password('SecurePass123!')
# Store in database
```

**`verify_password(password: str, password_hash: str) -> bool`**

Verify password against hash.

```python
if auth.verify_password(input_password, stored_hash):
    # Password correct
    pass
```

### Decorators

#### `@login_required`

Require valid JWT token.

```python
@app.route('/protected')
@login_required
async def protected(request):
    # Token verified automatically
    user_id = request.user_id
    username = request.username
    roles = request.roles
    return {'message': f'Hello {username}'}
```

**Optional Authentication:**

```python
@app.route('/optional')
@login_required(optional=True)
async def optional_auth(request):
    if request.user_id:
        return {'message': f'Hello {request.username}'}
    return {'message': 'Hello guest'}
```

#### `@roles_required(*roles)`

Require specific roles.

```python
@app.route('/admin')
@login_required
@auth.roles_required('admin')
async def admin_only(request):
    return {'message': 'Admin access'}

# Multiple roles (user must have ALL)
@auth.roles_required('moderator', 'verified')
async def moderator_only(request):
    return {'message': 'Moderator access'}
```

#### `@permission_required(*permissions, require_all=True)`

Require specific permissions.

```python
@app.route('/users/delete')
@login_required
@auth.permission_required('users.delete')
async def delete_user(request):
    # Has users.delete permission
    pass

# Any permission (OR logic)
@auth.permission_required('content.edit', 'content.delete', require_all=False)
async def moderate_content(request):
    # Has EITHER content.edit OR content.delete
    pass
```

## Complete Example

See `examples/auth_example.py` for a complete working example with:
- User registration
- Login/logout
- Protected routes
- Role-based access
- Password validation
- Token refresh

Run the example:

```bash
python examples/auth_example.py
```

Test with curl:

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "SecurePass123!"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "SecurePass123!"}'

# Access protected route
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Token Management Best Practices

### Access Token Storage

**Frontend (Browser):**

1. **Memory (Recommended)**: Store in JavaScript variable
   - Pros: Not accessible to XSS
   - Cons: Lost on page refresh (use refresh token)

2. **SessionStorage**: Page session only
   - Pros: Cleared on tab close
   - Cons: Vulnerable to XSS

3. **LocalStorage**: Persistent
   - Pros: Survives page refresh
   - Cons: Vulnerable to XSS, never expires

**Never use cookies for access tokens** (vulnerable to CSRF).

### Refresh Token Storage

**Options:**

1. **HttpOnly Cookie** (Recommended):
```python
@app.route('/auth/login', methods=['POST'])
async def login(request):
    # ... authentication logic ...

    response = Response(content={'access_token': access_token})
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,      # Not accessible to JavaScript
        secure=True,        # HTTPS only
        samesite='strict',  # CSRF protection
        max_age=30*24*3600  # 30 days
    )
    return response
```

2. **Secure Storage** (Mobile):
   - iOS: Keychain
   - Android: EncryptedSharedPreferences

### Token Rotation Strategy

```python
@app.route('/auth/refresh', methods=['POST'])
async def refresh(request):
    refresh_token = request.cookies.get('refresh_token')

    try:
        # Create new access token
        new_access_token = auth.refresh_access_token(refresh_token)

        # Optional: Rotate refresh token for maximum security
        payload = auth.verify_token(refresh_token)
        new_refresh_token = auth.create_refresh_token(payload['sub'])

        # Revoke old refresh token
        auth.revoke_token(refresh_token)

        response = Response(content={'access_token': new_access_token})
        response.set_cookie('refresh_token', new_refresh_token, ...)
        return response

    except TokenExpiredError:
        return Response(
            content={'error': 'Refresh token expired. Please login.'},
            status_code=401
        )
```

## Production Deployment Checklist

- [ ] Use environment variables for SECRET_KEY
- [ ] Enable HTTPS (use TLS 1.3)
- [ ] Set secure token expiration times
- [ ] Implement rate limiting on auth endpoints
- [ ] Add logging for authentication events
- [ ] Enable CORS with strict origins
- [ ] Use strong password requirements
- [ ] Implement account lockout after failed attempts
- [ ] Add 2FA for sensitive operations
- [ ] Monitor for suspicious authentication patterns
- [ ] Regular security audits
- [ ] Key rotation schedule
- [ ] Backup authentication data
- [ ] Disaster recovery plan

## Advanced Topics

### Using RS256 (Asymmetric Keys)

For multi-service architectures:

```python
from covet.auth.jwt import generate_rsa_keypair

# Generate keys
private_key, public_key = generate_rsa_keypair(key_size=2048)

# Save keys securely
with open('private.pem', 'w') as f:
    f.write(private_key)
with open('public.pem', 'w') as f:
    f.write(public_key)

# Use in Auth
auth = Auth(
    app,
    secret_key=private_key,
    algorithm='RS256'
)
```

**Benefits:**
- Public key can be shared with other services
- Services can verify tokens without secret key
- More secure for distributed systems

### Integration with Existing Auth Systems

```python
@auth.user_loader
def load_user(user_id):
    """Load user from database."""
    return User.query.get(user_id)

@app.route('/protected')
@login_required
async def protected(request):
    # Load full user object
    user = auth.load_user(request.user_id)
    return {'user': user.to_dict()}
```

### Custom Claims

```python
token = auth.create_token(
    user_id='123',
    username='john',
    # Custom claims
    organization_id='org-456',
    subscription_tier='premium',
    features=['analytics', 'api_access']
)

@login_required
async def premium_feature(request):
    if request.user.get('subscription_tier') != 'premium':
        return Response(
            content={'error': 'Premium subscription required'},
            status_code=402
        )
    # Premium feature logic
```

## Troubleshooting

### Common Issues

**1. Token Verification Fails**

```python
# Check token format
if not token.startswith('eyJ'):
    # Not a valid JWT

# Check expiration
try:
    payload = auth.verify_token(token)
except TokenExpiredError:
    # Token expired - refresh it
    pass

# Check algorithm mismatch
# Ensure auth.algorithm matches token algorithm
```

**2. User Context Not Available**

```python
# Ensure @login_required decorator is used
@app.route('/protected')
@login_required  # REQUIRED
async def protected(request):
    # Now request.user_id is available
    pass
```

**3. Token Not Found**

```python
# Check Authorization header format
# Correct: "Bearer eyJ..."
# Wrong: "eyJ..." or "Token eyJ..."

# Check header name
# Use: "Authorization"
# Not: "X-Auth-Token" (unless configured)
```

## Security Considerations Summary

### DO ✓

- Use strong secret keys (64+ characters)
- Store keys in environment variables
- Use HTTPS in production
- Short access token expiration (15-30 min)
- Implement token refresh
- Revoke tokens on logout
- Validate password strength
- Use Scrypt for password hashing
- Implement rate limiting
- Log authentication events

### DON'T ✗

- Hardcode secret keys
- Use weak passwords
- Store tokens in localStorage (if avoidable)
- Use long-lived access tokens
- Skip token verification
- Store passwords in plain text
- Use MD5 or SHA1 for passwords
- Allow unlimited login attempts
- Ignore security updates
- Share tokens between users

## Support

For issues or questions:
- GitHub: https://github.com/covetpy/covetpy
- Documentation: https://docs.covetpy.dev
- Security issues: security@covetpy.dev

## License

MIT License - see LICENSE file for details.
