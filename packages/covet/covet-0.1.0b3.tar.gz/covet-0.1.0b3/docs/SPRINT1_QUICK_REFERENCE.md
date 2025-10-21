# Sprint 1.6 Quick Reference Guide

## Error Handling Security - Quick Start

### Environment Configuration

```bash
# Production (default - most secure)
export COVET_ENV=production

# Development (detailed errors)
export COVET_ENV=development
```

### Key Files Created

1. **`src/covet/security/error_security.py`** - Main security module
   - Environment-aware error responses
   - Sanitization utilities
   - Error rate limiting
   - Security headers

2. **`src/covet/security/auth_security.py`** - Authentication security
   - Constant-time comparisons
   - Timing attack prevention
   - Auth rate limiting
   - Error normalization

3. **`src/tests/security/test_error_security.py`** - Comprehensive tests
   - 48 security test cases
   - All passing ✅

### Key Functions

#### Sanitization
```python
from covet.security.error_security import (
    sanitize_path,               # Remove absolute paths
    sanitize_sql_query,          # Mask SQL parameters
    sanitize_connection_string,  # Remove credentials
    sanitize_stack_trace,        # Clean stack traces
    sanitize_exception_context,  # Remove sensitive data
)

# Example
path = "/home/user/secret/app.py"
safe_path = sanitize_path(path)  # -> "<project>/app.py"

conn = "postgresql://user:pass@host/db"
safe_conn = sanitize_connection_string(conn)  # -> "postgresql://<user>:<redacted>@host/db"
```

#### Secure Error Responses
```python
from covet.security.error_security import create_secure_error_response

try:
    raise ValueError("Database error with credentials")
except Exception as e:
    response = create_secure_error_response(e)
    # Production: {"error": "An internal error occurred", "error_id": "ERR-...", "timestamp": "..."}
    # Development: Includes sanitized details
```

#### Timing Attack Prevention
```python
from covet.security.auth_security import (
    constant_time_compare,    # Use instead of ==
    add_auth_timing_jitter,   # Add random delay
    normalize_auth_error,     # Generic error messages
)

# WRONG - Timing attack vulnerable
if password == stored_password:
    return True

# CORRECT - Constant time
if constant_time_compare(password, stored_password):
    add_auth_timing_jitter()  # Add random delay
    return True
```

#### Rate Limiting
```python
from covet.security.error_security import get_error_rate_limiter
from covet.security.auth_security import get_auth_rate_limiter

# Error rate limiting (10 errors/minute)
error_limiter = get_error_rate_limiter()
is_limited, retry_after = error_limiter.is_rate_limited(client_ip)

# Auth rate limiting (5 attempts, 15 min lockout)
auth_limiter = get_auth_rate_limiter()
is_locked, seconds = auth_limiter.is_locked_out(username)
```

### Security Headers

Automatically applied to all error responses:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'none'
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer
```

### Error Response Format

**Production:**
```json
{
  "error": "An internal error occurred",
  "error_id": "ERR-a3f2b1c0d4e5f6a7",
  "timestamp": "2025-10-10T12:34:56Z"
}
```

**Development:**
```json
{
  "error": "An internal error occurred",
  "error_id": "ERR-a3f2b1c0d4e5f6a7",
  "timestamp": "2025-10-10T12:34:56Z",
  "details": "ValueError: Invalid input",
  "error_type": "ValueError",
  "stack_trace": "<sanitized stack trace>"
}
```

### Best Practices

✅ **DO:**
- Use `constant_time_compare()` for passwords/tokens
- Add timing jitter after authentication checks
- Use generic error messages ("Invalid credentials")
- Log full details server-side with error IDs
- Set `COVET_ENV=production` in production

❌ **DON'T:**
- Use `==` for password comparison
- Return different errors for "user not found" vs "wrong password"
- Include stack traces in production
- Expose database connection strings
- Skip timing jitter on auth operations

### Testing

```bash
# Run security tests
python -m pytest src/tests/security/test_error_security.py -v

# Test specific function
python -c "
import sys
sys.path.insert(0, 'src')
from covet.security.error_security import sanitize_path
print(sanitize_path('/home/user/secret.py'))
"
```

### Common Attack Scenarios Prevented

| Attack | Before | After |
|--------|--------|-------|
| **Database Credential Extraction** | Connection strings in errors | ✅ Credentials redacted |
| **User Enumeration** | Different error messages | ✅ Generic "Invalid credentials" |
| **File System Mapping** | Full paths in stack traces | ✅ Paths sanitized |
| **Timing Attacks** | Variable response times | ✅ Constant-time + jitter |
| **Brute Force** | Unlimited attempts | ✅ Rate limiting + lockout |
| **Error Reconnaissance** | Unlimited errors | ✅ 10 errors/min limit |

### Error Correlation

Server logs contain full details with error ID:
```
[ERR-a3f2b1c0d4e5f6a7] ValueError: Database connection failed
Stack trace:
  File "<project>/database.py", line 42, in connect
    ...
```

Client receives only error ID:
```json
{"error_id": "ERR-a3f2b1c0d4e5f6a7"}
```

Use error ID to correlate client issues with server logs.

### Configuration Options

```python
# Custom error rate limiter
from covet.security.error_security import ErrorRateLimiter

limiter = ErrorRateLimiter(
    window_seconds=60,           # 1 minute window
    max_errors=10,               # Max 10 errors
    block_duration_seconds=300   # Block for 5 minutes
)

# Custom auth rate limiter
from covet.security.auth_security import AuthRateLimiter

auth_limiter = AuthRateLimiter(
    max_attempts=5,              # Max 5 failed attempts
    window_seconds=300,          # In 5 minute window
    lockout_duration=900         # Lock out for 15 minutes
)
```

### Monitoring Queries

```sql
-- Find IPs with excessive errors
SELECT client_ip, COUNT(*) as error_count
FROM error_logs
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY client_ip
HAVING COUNT(*) > 50;

-- Find locked out users
SELECT username, locked_until
FROM auth_lockouts
WHERE locked_until > NOW();

-- Error rate trends
SELECT DATE_TRUNC('hour', timestamp) as hour,
       COUNT(*) as error_count
FROM error_logs
GROUP BY hour
ORDER BY hour DESC;
```

---

**Quick Status Check:**
```bash
# Verify production mode
python -c "
import os, sys
sys.path.insert(0, 'src')
os.environ['COVET_ENV'] = 'production'
from covet.security.error_security import get_security_config
c = get_security_config()
print(f'Production: {c.is_production}')
print(f'Sanitize paths: {c.sanitize_paths}')
print(f'Remove traces: {c.remove_stack_traces}')
"
```

**Expected output:**
```
Production: True
Sanitize paths: True
Remove traces: True
```

---

**For full details, see:** `docs/SPRINT1_ERROR_HANDLING_FIXES.md`
