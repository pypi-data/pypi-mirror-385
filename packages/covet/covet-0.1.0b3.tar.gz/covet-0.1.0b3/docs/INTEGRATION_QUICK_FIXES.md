# CovetPy Integration Quick Fixes

**Quick Reference for Fixing Import Errors**

---

## Fix #1: OAuth2Token Dataclass (15 minutes)

**File:** `src/covet/security/auth/oauth2_provider.py`

**Line:** 210-229

**Error:** `TypeError: non-default argument 'expires_at' follows default argument`

**Fix:**

```python
@dataclass
class OAuth2Token:
    """OAuth2 access token or refresh token."""

    token: str
    token_type: TokenType
    client_id: str
    user_id: Optional[str]
    scopes: Set[str]
    expires_at: datetime  # MOVE THIS BEFORE DEFAULTS

    # Token metadata (with defaults)
    issued_at: datetime = field(default_factory=datetime.utcnow)

    # Refresh token (only for access tokens)
    refresh_token: Optional[str] = None
    refresh_token_expires_at: Optional[datetime] = None

    # Revocation
    revoked: bool = False
    revoked_at: Optional[datetime] = None

    # Associated authorization code (for audit trail)
    authorization_code: Optional[str] = None

    # Additional claims (for JWT tokens)
    extra_claims: Dict[str, Any] = field(default_factory=dict)
```

**Test:**
```bash
python -c "from covet.security.auth import OAuth2Token; print('OK')"
```

---

## Fix #2: GraphQL Input Import (15 minutes)

**File:** `src/covet/api/graphql/schema.py`

**Line:** 54-60

**Error:** `ImportError: cannot import name 'input'`

**Fix (Option A - Add alias):**

```python
# Re-export Strawberry decorators with type aliases
ObjectType = strawberry.type
InputType = strawberry.input
InterfaceType = strawberry.interface
UnionType = strawberry.union
EnumType = strawberry.enum

# Aliases for consistency
graphql_type = strawberry.type
graphql_input = strawberry.input
graphql_interface = strawberry.interface
graphql_enum = strawberry.enum
graphql_scalar = strawberry.scalar
field = strawberry.field

# Direct exports for backward compatibility
enum = strawberry.enum
type_decorator = strawberry.type
input_decorator = strawberry.input
input = strawberry.input  # ADD THIS LINE
interface_decorator = strawberry.interface
scalar = strawberry.scalar
```

**Fix (Option B - Update import):**

```python
# File: src/covet/api/graphql/__init__.py
# Line 93, change from:
from .schema import input as graphql_input

# To:
from .schema import input_decorator as graphql_input
```

**Test:**
```bash
python -c "from covet.api.graphql import graphql_input; print('OK')"
```

---

## Fix #3: Application Module (30 minutes)

**File:** Create `src/covet/core/application.py`

**Error:** `ModuleNotFoundError: No module named 'covet.core.application'`

**Fix (Create new file):**

```python
"""
CovetPy Application Module

Provides aliases for backward compatibility and convenience imports.
"""

from .asgi_app import CovetASGIApp as CovetApplication
from .app_pure import Covet

__all__ = [
    "CovetApplication",
    "Covet",
]
```

**Alternative Fix (Remove import):**

```python
# File: src/covet/core/__init__.py
# Remove any lines importing from .application
# The exports are already available through other paths
```

**Test:**
```bash
python -c "from covet.core.application import Covet; print('OK')"
```

---

## Fix #4: Monitoring Tracing (30 minutes)

**File:** Create `src/covet/monitoring/tracing.py`

**Error:** `ModuleNotFoundError: No module named 'covet.monitoring.tracing'`

**Fix (Create stub):**

```python
"""
OpenTelemetry Tracing Integration

Stub implementation for distributed tracing.
Full implementation requires: opentelemetry-api, opentelemetry-sdk

TODO: Implement full OpenTelemetry integration
"""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


def configure_tracing(
    service_name: str = "covetpy",
    endpoint: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    Configure distributed tracing with OpenTelemetry.

    Args:
        service_name: Service name for tracing
        endpoint: OTLP endpoint URL
        **kwargs: Additional configuration options
    """
    logger.info(
        "Tracing configuration called (stub implementation). "
        "Install opentelemetry-api and opentelemetry-sdk for full support."
    )


def trace_middleware():
    """
    ASGI middleware for automatic request tracing.

    Returns:
        Middleware function that adds tracing to requests
    """
    async def middleware(scope, receive, send):
        # Pass-through middleware (no tracing yet)
        # TODO: Add OpenTelemetry span creation
        await send(scope)

    logger.info(
        "Trace middleware loaded (stub). "
        "Install OpenTelemetry packages for full tracing support."
    )

    return middleware


__all__ = [
    "configure_tracing",
    "trace_middleware",
]
```

**Test:**
```bash
python -c "from covet.monitoring import configure_tracing; print('OK')"
```

---

## Fix #5: DatabaseConfig Export (30 minutes)

**File:** `src/covet/database/__init__.py`

**Error:** `ImportError: cannot import name 'DatabaseConfig'`

**Fix:**

```python
"""
CovetPy Database Layer
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import json
import sqlite3

# Import core components
from .core import DatabaseConfig  # ADD THIS LINE

from .security import (
    InvalidIdentifierError,
    validate_table_name,
    validate_column_name,
)

# ... rest of file ...

__all__ = [
    # Core
    "DatabaseConfig",  # ADD THIS LINE
    # Security
    "InvalidIdentifierError",
    "validate_table_name",
    "validate_column_name",
    # Database
    "DatabaseAdapter",
    "DatabaseDialect",
    "DatabaseManager",
    "SQLiteAdapter",
    "create_database_manager",
    # Models
    "Model",
    # JSON utilities
    "json",
    "sqlite3",
    "security",
]
```

**Test:**
```bash
python -c "from covet.database import DatabaseConfig; print('OK')"
```

---

## Verification Script

**Create:** `verify_fixes.py`

```python
#!/usr/bin/env python3
"""Verify all integration fixes"""

import sys

def test_import(module_name, symbol=None):
    """Test importing a module or symbol."""
    try:
        if symbol:
            exec(f"from {module_name} import {symbol}")
            print(f"✅ {module_name}.{symbol}")
        else:
            exec(f"import {module_name}")
            print(f"✅ {module_name}")
        return True
    except Exception as e:
        print(f"❌ {module_name}{('.' + symbol) if symbol else ''}: {e}")
        return False

def main():
    print("Testing CovetPy Integration Fixes\n")

    results = []

    # Test Fix #1: OAuth2Token
    results.append(test_import("covet.security.auth", "OAuth2Token"))

    # Test Fix #2: GraphQL input
    results.append(test_import("covet.api.graphql", "graphql_input"))

    # Test Fix #3: Application module
    results.append(test_import("covet.core.application", "Covet"))

    # Test Fix #4: Monitoring tracing
    results.append(test_import("covet.monitoring", "configure_tracing"))

    # Test Fix #5: DatabaseConfig
    results.append(test_import("covet.database", "DatabaseConfig"))

    # Summary
    print(f"\n{'='*50}")
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} passed")

    if passed == total:
        print("✅ All fixes verified successfully!")
        return 0
    else:
        print("❌ Some fixes need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Run:**
```bash
python verify_fixes.py
```

---

## Expected Output After Fixes

```
Testing CovetPy Integration Fixes

✅ covet.security.auth.OAuth2Token
✅ covet.api.graphql.graphql_input
✅ covet.core.application.Covet
✅ covet.monitoring.configure_tracing
✅ covet.database.DatabaseConfig

==================================================
Results: 5/5 passed
✅ All fixes verified successfully!
```

---

## Checklist

- [ ] Fix #1: OAuth2Token dataclass (15 min)
- [ ] Fix #2: GraphQL input import (15 min)
- [ ] Fix #3: Application module (30 min)
- [ ] Fix #4: Monitoring tracing (30 min)
- [ ] Fix #5: DatabaseConfig export (30 min)
- [ ] Run verification script
- [ ] Run test suite: `pytest tests/`
- [ ] Commit changes

**Total Time:** 2 hours

---

## After Fixes

Run comprehensive tests:

```bash
# Import test
python -c "import covet; print('CovetPy imported successfully!')"

# Create app test
python -c "from covet import Covet; app = Covet(); print('App created!')"

# Full test suite
pytest tests/ -v

# Integration audit
python audit_comprehensive_integration.py
```

Expected result: **100/100 Integration Score**

---

**Need Help?**

See full documentation:
- `docs/AUDIT_INTEGRATION_ARCHITECTURE_DETAILED.md`
- `docs/INTEGRATION_AUDIT_EXECUTIVE_SUMMARY.md`
