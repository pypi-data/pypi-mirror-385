# CovetPy Authentication - Quick Reference

## Installation

No additional dependencies required. JWT and password hashing are built-in.

## 5-Minute Setup

```python
from covet import Covet
from covet.auth import Auth, login_required, hash_password, verify_password

app = Covet()
auth = Auth(app, secret_key='your-secret-key-change-in-production')

# In-memory user storage (use database in production)
users = {}

@app.route('/register', methods=['POST'])
async def register(request):
    data = await request.json()
    username = data['username']
    password = data['password']

    # Hash password
    users[username] = {
        'password_hash': hash_password(password),
        'roles': ['user']
    }

    return {'message': 'User registered'}, 201

@app.route('/login', methods=['POST'])
async def login(request):
    data = await request.json()
    username = data['username']
    password = data['password']

    user = users.get(username)
    if not user or not verify_password(password, user['password_hash']):
        return {'error': 'Invalid credentials'}, 401

    token = auth.create_token(user_id=username, roles=user['roles'])
    return {'token': token}

@app.route('/protected')
@login_required
async def protected(request):
    return {'user': request.user_id, 'message': 'Access granted'}

@app.route('/admin')
@login_required
@auth.roles_required('admin')
async def admin_only(request):
    return {'message': 'Admin access'}

if __name__ == '__main__':
    app.run()
```

## Common Patterns

### User Registration with Validation

```python
from covet.auth import check_password_strength, hash_password

@app.route('/register', methods=['POST'])
async def register(request):
    data = await request.json()

    # Validate password strength
    is_strong, issues = check_password_strength(data['password'])
    if not is_strong:
        return {'error': 'Weak password', 'issues': issues}, 400

    # Hash and store
    user = User(
        username=data['username'],
        password_hash=hash_password(data['password'])
    )
    db.save(user)

    return {'message': 'Registered successfully'}, 201
```

### Login with Token Refresh

```python
@app.route('/login', methods=['POST'])
async def login(request):
    # ... verify credentials ...

    access_token = auth.create_token(user_id=user.id, roles=user.roles)
    refresh_token = auth.create_refresh_token(user_id=user.id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': 1800  # 30 minutes
    }

@app.route('/refresh', methods=['POST'])
async def refresh(request):
    data = await request.json()
    refresh_token = data['refresh_token']

    try:
        new_access_token = auth.refresh_access_token(refresh_token)
        return {'access_token': new_access_token}
    except Exception as e:
        return {'error': 'Invalid refresh token'}, 401
```

### Logout (Token Revocation)

```python
@app.route('/logout', methods=['POST'])
@login_required
async def logout(request):
    from covet.auth.decorators import extract_token_from_request

    token = extract_token_from_request(request)
    auth.revoke_token(token)

    return {'message': 'Logged out'}
```

### Protected Routes

```python
# Basic authentication
@app.route('/profile')
@login_required
async def profile(request):
    return {
        'user_id': request.user_id,
        'username': request.username,
        'roles': request.roles
    }

# Role-based access
@app.route('/admin/users')
@login_required
@auth.roles_required('admin')
async def admin_users(request):
    return {'users': get_all_users()}

# Permission-based access
@app.route('/users/<user_id>/delete', methods=['DELETE'])
@login_required
@auth.permission_required('users.delete')
async def delete_user(request, user_id):
    User.delete(user_id)
    return {'message': 'User deleted'}

# Multiple roles (must have ALL)
@auth.roles_required('moderator', 'verified')
async def moderate_content(request):
    pass

# Any permission (OR logic)
@auth.permission_required('edit', 'delete', require_all=False)
async def manage_content(request):
    pass
```

### Optional Authentication

```python
@app.route('/content')
@login_required(optional=True)
async def content(request):
    if request.user_id:
        # Authenticated user - personalized content
        return {'content': get_user_content(request.user_id)}
    else:
        # Guest user - generic content
        return {'content': get_public_content()}
```

## Configuration Options

```python
auth = Auth(
    app,
    secret_key='64-char-random-string-here',  # REQUIRED
    algorithm='HS256',                         # HS256, HS512, RS256, RS512
    access_token_expire_minutes=30,            # Short-lived
    refresh_token_expire_days=30               # Long-lived
)
```

## Password Utilities

```python
from covet.auth import (
    hash_password,
    verify_password,
    check_password_strength,
    generate_secure_password
)

# Hash password
hashed = hash_password('SecurePass123!')

# Verify password
is_valid = verify_password('SecurePass123!', hashed)

# Check strength
is_strong, issues = check_password_strength('weak')
# Returns: (False, ['Too short', 'No uppercase', ...])

# Generate secure password
password = generate_secure_password(16)
# Returns: 'aB3$xY9!mK2#pL7@'
```

## Token Claims

### Standard Claims

Automatically included:
- `sub`: User ID (subject)
- `iat`: Issued at timestamp
- `exp`: Expiration timestamp
- `nbf`: Not before timestamp
- `iss`: Issuer (default: 'covet-app')
- `aud`: Audience (default: 'covet-api')
- `jti`: JWT ID (for revocation)
- `token_type`: 'access' or 'refresh'

### Custom Claims

```python
token = auth.create_token(
    user_id='123',
    username='john',          # Optional
    roles=['user', 'admin'],  # Optional
    # Custom claims:
    organization='acme-corp',
    subscription='premium',
    features=['api', 'analytics']
)

# Access in protected routes
@login_required
async def premium_feature(request):
    if request.user.get('subscription') != 'premium':
        return {'error': 'Premium required'}, 402
```

## Token Extraction

Tokens are automatically extracted from (in order):

1. **Authorization header** (recommended):
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJh...
   ```

2. **X-API-Token header**:
   ```
   X-API-Token: eyJ0eXAiOiJKV1QiLCJh...
   ```

3. **Query parameter** (not recommended):
   ```
   GET /api/data?token=eyJ0eXAiOiJKV1QiLCJh...
   ```

4. **Cookie**:
   ```
   Cookie: access_token=eyJ0eXAiOiJKV1QiLCJh...
   ```

## Error Handling

```python
from covet.auth.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
    AuthException
)

@app.route('/protected')
async def protected(request):
    from covet.auth.decorators import extract_token_from_request

    token = extract_token_from_request(request)
    if not token:
        return {'error': 'No token provided'}, 401

    try:
        payload = auth.verify_token(token)
        return {'user_id': payload['sub']}
    except TokenExpiredError:
        return {'error': 'Token expired'}, 401
    except TokenInvalidError as e:
        return {'error': f'Invalid token: {e}'}, 401
```

## Testing

### Unit Tests

```python
import pytest
from covet.auth import Auth, hash_password, verify_password

def test_password_hashing():
    password = 'SecurePass123!'
    hashed = hash_password(password)

    assert verify_password(password, hashed)
    assert not verify_password('wrong', hashed)

def test_token_creation():
    auth = Auth(secret_key='test-key-12345')

    token = auth.create_token(user_id='123', username='test')
    payload = auth.verify_token(token)

    assert payload['sub'] == '123'
    assert payload['username'] == 'test'

def test_token_revocation():
    auth = Auth(secret_key='test-key-12345')

    token = auth.create_token(user_id='123')
    auth.revoke_token(token)

    with pytest.raises(Exception):
        auth.verify_token(token)
```

### Integration Tests

```python
from covet.testing import TestClient

def test_login_flow():
    client = TestClient(app)

    # Register
    response = client.post('/register', json={
        'username': 'test',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 201

    # Login
    response = client.post('/login', json={
        'username': 'test',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 200
    token = response.json()['token']

    # Access protected route
    response = client.get(
        '/protected',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
```

## Security Checklist

### Development
- [ ] Use auto-generated secret key (it will warn)
- [ ] Test with HTTP (not HTTPS)
- [ ] Store tokens in memory/sessionStorage

### Production
- [ ] Use strong SECRET_KEY from environment
- [ ] Enforce HTTPS everywhere
- [ ] Short token expiration (15-30 min)
- [ ] Implement token refresh
- [ ] Add rate limiting on auth endpoints
- [ ] Use HttpOnly cookies for refresh tokens
- [ ] Validate password strength
- [ ] Log authentication events
- [ ] Monitor for suspicious activity
- [ ] Regular security audits

## Environment Variables

```bash
# .env file
SECRET_KEY=your-64-character-random-string-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
JWT_ALGORITHM=HS256
JWT_ISSUER=your-app-name
JWT_AUDIENCE=your-api-name
```

```python
import os
from covet.auth import Auth

auth = Auth(
    app,
    secret_key=os.environ['SECRET_KEY'],
    algorithm=os.environ.get('JWT_ALGORITHM', 'HS256'),
    access_token_expire_minutes=int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 30)),
    refresh_token_expire_days=int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS', 30))
)
```

## Common Issues

### "No token provided" Error
- Check Authorization header format: `Bearer <token>`
- Verify token is being sent from client
- Check CORS settings allow Authorization header

### "Token expired" Error
- Implement token refresh flow
- Adjust token expiration time
- Clear old tokens from client storage

### "Invalid token" Error
- Verify SECRET_KEY matches between creation and verification
- Check algorithm matches (HS256 vs RS256)
- Ensure token hasn't been tampered with

### Decorator not working
- Ensure `@login_required` is AFTER route decorator
- Check token is in correct format
- Verify auth instance is configured

## Examples

Full examples available in:
- `examples/auth_example.py` - Complete authentication system
- `examples/auth/simple_auth_test.py` - Unit tests
- `docs/AUTH_INTEGRATION_GUIDE.md` - Detailed guide

## API Summary

| Function | Purpose | Example |
|----------|---------|---------|
| `Auth()` | Create auth instance | `auth = Auth(app, secret_key='key')` |
| `create_token()` | Create JWT token | `token = auth.create_token(user_id='123')` |
| `verify_token()` | Verify JWT token | `payload = auth.verify_token(token)` |
| `create_refresh_token()` | Create refresh token | `refresh = auth.create_refresh_token('123')` |
| `refresh_access_token()` | Refresh access token | `new = auth.refresh_access_token(refresh)` |
| `revoke_token()` | Revoke token | `auth.revoke_token(token)` |
| `hash_password()` | Hash password | `hashed = auth.hash_password(pwd)` |
| `verify_password()` | Verify password | `valid = auth.verify_password(pwd, hash)` |
| `@login_required` | Require auth | `@login_required` |
| `@roles_required()` | Require roles | `@auth.roles_required('admin')` |
| `@permission_required()` | Require permissions | `@auth.permission_required('delete')` |

## Next Steps

1. Run the example: `python examples/auth_example.py`
2. Test with curl or Postman
3. Read full guide: `docs/AUTH_INTEGRATION_GUIDE.md`
4. Integrate into your app
5. Deploy to production with proper security

## Support

- Documentation: `/docs/AUTH_INTEGRATION_GUIDE.md`
- Examples: `/examples/auth_example.py`
- Tests: `/examples/auth/simple_auth_test.py`
