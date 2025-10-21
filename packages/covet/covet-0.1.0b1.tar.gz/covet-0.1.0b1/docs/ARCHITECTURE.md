# CovetPy Framework Architecture
## Production-Grade Zero-Dependency Web Framework

**Version:** 0.3
**Last Updated:** 2025-10-10
**Status:** Sprint 3 - Refactored

---

## Table of Contents

1. [Overview](#1-overview)
2. [Application Architecture](#2-application-architecture)
3. [Module Organization](#3-module-organization)
4. [Request/Response Lifecycle](#4-requestresponse-lifecycle)
5. [Exception Handling](#5-exception-handling)
6. [Middleware Pipeline](#6-middleware-pipeline)
7. [Database Layer](#7-database-layer)
8. [Security Architecture](#8-security-architecture)
9. [Deployment Architecture](#9-deployment-architecture)

---

## 1. Overview

CovetPy is a high-performance, zero-dependency web framework for Python that provides:
- ASGI 3.0 compliance for production deployment
- Built-in security hardening
- Comprehensive middleware system
- Advanced routing with parameter extraction
- Real-time WebSocket support
- Enterprise-grade ORM

### 1.1 Design Principles

```
┌────────────────────────────────────────────────────┐
│ COVETPY DESIGN PRINCIPLES                          │
├────────────────────────────────────────────────────┤
│                                                    │
│ 1. Zero External Dependencies                     │
│    └─ Pure Python stdlib implementation           │
│                                                    │
│ 2. Security by Design                             │
│    └─ Built-in security hardening                 │
│                                                    │
│ 3. Performance First                              │
│    └─ Optimized request/response handling         │
│                                                    │
│ 4. Developer Experience                           │
│    └─ Intuitive API, clear documentation          │
│                                                    │
│ 5. Production Ready                               │
│    └─ Battle-tested, fully typed, comprehensive   │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 2. Application Architecture

### 2.1 Class Hierarchy (ADR-001)

```
┌─────────────────────────────────────────────────────────────────┐
│                     COVETPY APPLICATION CLASSES                 │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │  CovetApplication │  ◄── MAIN CLASS
                    └─────────────────┘
                            │
                            │ implements
                            ▼
                    ┌─────────────────┐
                    │   ASGI Protocol   │
                    └─────────────────┘
                            │
                            │ wrapped by
                            ▼
                    ┌─────────────────┐
                    │  CovetASGIApp    │  ◄── PRODUCTION
                    └─────────────────┘

                    ┌─────────────────┐
                    │      Covet       │  ◄── FACTORY
                    └─────────────────┘
                            │
                            │ creates
                            │
                            └──────────────► CovetApplication

                    ┌─────────────────┐
                    │    CovetApp      │  ◄── DEPRECATED
                    └─────────────────┘
                            │
                            │ alias to
                            └──────────────► CovetApplication
```

### 2.2 Application Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION LIFECYCLE                         │
└─────────────────────────────────────────────────────────────────┘

    START
      │
      ├─► 1. Create Application
      │        └─ Covet.create_app(...)
      │
      ├─► 2. Initialize
      │        ├─ Setup logging
      │        ├─ Configure container
      │        ├─ Apply middleware
      │        └─ Load plugins
      │
      ├─► 3. Startup Handlers
      │        └─ Run @app.on_event("startup")
      │
      ├─► 4. Serve Requests ◄──┐
      │        │                │
      │        ├─ Parse request │
      │        ├─ Route match   │ MAIN LOOP
      │        ├─ Middleware    │
      │        ├─ Handler       │
      │        └─ Response   ───┘
      │
      ├─► 5. Shutdown Signal
      │        └─ Ctrl+C or SIGTERM
      │
      ├─► 6. Shutdown Handlers
      │        └─ Run @app.on_event("shutdown")
      │
      └─► 7. Cleanup
               ├─ Close connections
               ├─ Dispose resources
               └─ Exit
```

---

## 3. Module Organization

### 3.1 Directory Structure

```
src/covet/
├── core/                       # Framework core
│   ├── __init__.py            # Public API exports
│   ├── app.py                 # Application factory
│   ├── app_pure.py            # CovetApplication class
│   ├── asgi_app.py            # ASGI 3.0 wrapper
│   ├── asgi.py                # ASGI utilities
│   ├── http.py                # HTTP primitives
│   ├── http_objects.py        # Request/Response (1,382 lines - needs refactor)
│   ├── http_server.py         # Production HTTP/1.1 server
│   ├── routing.py             # URL routing
│   ├── advanced_router.py     # Advanced routing features
│   ├── middleware.py          # Middleware system
│   ├── builtin_middleware.py  # Built-in middleware (1,096 lines - needs refactor)
│   ├── config.py              # Configuration
│   ├── container.py           # Dependency injection
│   ├── exceptions.py          # Exception hierarchy
│   ├── logging.py             # Structured logging
│   ├── plugins.py             # Plugin system
│   ├── validation.py          # Input validation
│   └── websocket.py           # WebSocket support
│
├── middleware/                 # Middleware implementations
│   ├── __init__.py
│   ├── core.py                # Middleware base classes
│   ├── cors.py                # CORS middleware
│   └── input_validation.py    # Validation middleware
│
├── auth/                       # Authentication & Authorization
│   ├── __init__.py
│   ├── auth.py                # Auth implementation
│   ├── jwt_auth.py            # JWT support
│   ├── oauth2.py              # OAuth2 support
│   ├── rbac.py                # Role-based access control
│   ├── two_factor.py          # 2FA support
│   ├── middleware.py          # Auth middleware
│   ├── security.py            # Security utilities
│   └── endpoints.py           # Auth endpoints
│
├── database/                   # Database layer
│   ├── __init__.py
│   ├── core/
│   │   ├── database_base.py   # Base classes
│   │   ├── connection_pool.py # Connection pooling
│   │   └── enhanced_connection_pool.py
│   ├── adapters/              # Database adapters
│   │   ├── base.py
│   │   ├── postgresql.py
│   │   ├── mysql.py
│   │   └── sqlite.py
│   ├── query_builder/         # Query builder
│   │   ├── builder.py
│   │   ├── conditions.py
│   │   ├── joins.py
│   │   ├── expressions.py
│   │   └── aggregates.py
│   ├── orm/                   # ORM implementation
│   │   ├── models.py
│   │   ├── fields.py
│   │   ├── query.py
│   │   ├── managers.py
│   │   └── connection.py
│   ├── migrations/            # Database migrations
│   │   └── advanced_migration.py
│   ├── sharding/              # Database sharding
│   │   └── shard_manager.py
│   └── transaction/           # Transaction management
│       └── advanced_transaction_manager.py
│
├── orm/                        # Legacy ORM (to be consolidated)
│   ├── __init__.py
│   ├── models.py
│   ├── fields.py
│   ├── query.py
│   ├── managers.py
│   ├── connection.py
│   ├── migrations.py
│   └── exceptions.py
│
├── templates/                  # Template engine
│   ├── __init__.py
│   ├── engine.py              # Template engine
│   ├── compiler.py            # Template compiler
│   ├── loader.py              # Template loader
│   ├── filters.py             # Template filters
│   ├── static.py              # Static file handling
│   └── examples.py            # Template examples
│
├── websocket/                  # WebSocket support
│   ├── __init__.py
│   ├── protocol.py            # WebSocket protocol
│   ├── connection.py          # Connection management
│   ├── routing.py             # WebSocket routing
│   ├── client.py              # WebSocket client
│   ├── security.py            # WebSocket security
│   ├── asgi.py                # ASGI WebSocket
│   └── examples.py            # WebSocket examples
│
├── security/                   # Security utilities
│   ├── __init__.py
│   ├── simple_auth.py         # Simple auth implementation
│   ├── jwt_auth.py            # JWT utilities
│   └── error_security.py      # Error sanitization
│
├── testing/                    # Testing utilities
│   └── client.py              # Test client
│
├── _rust/                      # Rust integration (optional)
│   └── __init__.py            # Python fallbacks
│
├── config.py                   # Global configuration
└── __init__.py                 # Package exports
```

### 3.2 Import Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMPORT DEPENDENCY GRAPH                      │
└─────────────────────────────────────────────────────────────────┘

Level 0 (No dependencies):
    ├── core.exceptions
    ├── core.config
    └── core.logging

Level 1 (Depends on Level 0):
    ├── core.http (→ exceptions)
    ├── core.container (→ config, exceptions)
    └── core.validation (→ exceptions)

Level 2 (Depends on Level 0-1):
    ├── core.routing (→ http, exceptions)
    ├── core.middleware (→ http, exceptions)
    └── auth (→ http, exceptions, validation)

Level 3 (Depends on Level 0-2):
    ├── core.app_pure (→ http, routing, middleware, config)
    ├── database (→ exceptions, validation)
    └── templates (→ exceptions)

Level 4 (Depends on Level 0-3):
    ├── core.asgi_app (→ app_pure, middleware)
    └── websocket (→ http, routing)

Level 5 (Public API):
    └── core.__init__ (→ all modules)
```

---

## 4. Request/Response Lifecycle

### 4.1 HTTP Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              HTTP REQUEST/RESPONSE LIFECYCLE                    │
└─────────────────────────────────────────────────────────────────┘

CLIENT REQUEST
      │
      ▼
┌─────────────────┐
│  ASGI Server    │  (uvicorn, hypercorn, daphne)
│  (uvicorn)      │
└─────────────────┘
      │
      │ ASGI protocol
      ▼
┌─────────────────┐
│ CovetASGIApp    │  ASGI 3.0 wrapper
│                 │  ├─ Lifespan management
│                 │  ├─ Request parsing
│                 │  └─ Response serialization
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Middleware      │  Request processing
│ Pipeline        │  ├─ CORS
│                 │  ├─ Authentication
│                 │  ├─ Rate limiting
│                 │  ├─ Request logging
│                 │  └─ Input validation
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Router          │  URL matching
│                 │  ├─ Static routes
│                 │  ├─ Parameterized routes
│                 │  └─ Regex routes
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Route Handler   │  Business logic
│                 │  ├─ Request processing
│                 │  ├─ Database queries
│                 │  └─ Response creation
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Response        │  Response processing
│ Middleware      │  ├─ Compression
│                 │  ├─ Response logging
│                 │  └─ Error handling
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ ASGI Response   │  ASGI serialization
│                 │  ├─ Headers
│                 │  ├─ Status code
│                 │  └─ Body
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ ASGI Server     │  HTTP serialization
└─────────────────┘
      │
      ▼
CLIENT RESPONSE
```

### 4.2 Request Object Structure

```python
class Request:
    """HTTP Request object"""

    # Request line
    method: str              # GET, POST, PUT, DELETE, etc.
    url: str                 # Full URL path
    path: str                # URL path
    query_string: str        # Query parameters

    # Headers
    headers: Dict[str, str]  # HTTP headers

    # Body
    _body: bytes            # Raw body
    _json: Optional[dict]   # Parsed JSON (lazy)
    _form: Optional[dict]   # Parsed form data (lazy)

    # Metadata
    remote_addr: str        # Client IP
    scheme: str             # http or https
    server_name: str        # Server hostname
    server_port: int        # Server port

    # Routing
    path_params: dict       # URL parameters

    # State
    state: dict             # Request-scoped state
```

### 4.3 Response Object Structure

```python
class Response:
    """HTTP Response object"""

    # Content
    content: Union[str, bytes, dict]
    _body_bytes: Optional[bytes]

    # Status
    status_code: int        # HTTP status code

    # Headers
    headers: Dict[str, str] # HTTP headers
    media_type: str         # Content-Type

    # Cookies
    cookies: Dict[str, Cookie]

    # Methods
    def set_cookie(...)     # Add cookie
    def get_content_bytes() # Get response body
```

---

## 5. Exception Handling

### 5.1 Exception Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXCEPTION HIERARCHY                          │
└─────────────────────────────────────────────────────────────────┘

Exception (Python builtin)
    │
    └─► CovetError (Base framework exception)
            │
            ├─► ConfigurationError
            │     └─ Used for: config file errors, env var issues
            │
            ├─► ContainerError
            │     └─ Used for: DI failures, circular dependencies
            │
            ├─► MiddlewareError
            │     └─ Used for: middleware initialization, execution
            │
            ├─► PluginError
            │     └─ Used for: plugin loading, initialization
            │
            ├─► ValidationError
            │     └─ Used for: input validation, data validation
            │
            ├─► AuthenticationError
            │     └─ Used for: login failures, token validation
            │
            ├─► AuthorizationError
            │     └─ Used for: permission denied, RBAC failures
            │
            ├─► DatabaseError
            │     └─ Used for: connection errors, query failures
            │
            ├─► NetworkError
            │     └─ Used for: HTTP request failures, timeouts
            │
            ├─► SerializationError
            │     └─ Used for: JSON parsing, data conversion
            │
            ├─► RateLimitError
            │     └─ Used for: rate limiting, throttling
            │
            ├─► ServiceUnavailableError
            │     └─ Used for: service downtime, dependencies
            │
            ├─► SecurityError
            │     └─ Used for: security violations, attacks
            │
            └─► HTTPException
                  └─ Used for: HTTP errors with status codes
```

### 5.2 Exception Context

```python
class CovetError(Exception):
    """
    All framework exceptions include:
    - message: Human-readable error message
    - error_code: Machine-readable error code
    - context: Additional context (sanitized in production)
    - cause: Original exception (for exception chaining)
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[dict] = None,
        cause: Optional[Exception] = None,
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert to API response with security sanitization.
        - Removes sensitive data (passwords, tokens, PII)
        - Sanitizes stack traces
        - Respects production environment
        """
```

### 5.3 Security Hardening

```
┌─────────────────────────────────────────────────────────────────┐
│               EXCEPTION SECURITY FEATURES                       │
└─────────────────────────────────────────────────────────────────┘

1. Context Sanitization
   ├─ Remove passwords
   ├─ Remove API keys
   ├─ Remove tokens
   ├─ Remove PII
   └─ Hash sensitive data

2. Stack Trace Sanitization
   ├─ Remove absolute paths (production)
   ├─ Remove environment variables
   ├─ Remove source code snippets
   └─ Limit stack depth

3. Environment-Aware
   ├─ Development: Full context + stack traces
   ├─ Staging: Sanitized context + limited traces
   └─ Production: Minimal context, no traces

4. Secure Logging
   ├─ Log to secure location
   ├─ Include correlation IDs
   ├─ Separate security events
   └─ Audit trail for compliance
```

---

## 6. Middleware Pipeline

### 6.1 Middleware Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   MIDDLEWARE PIPELINE                           │
└─────────────────────────────────────────────────────────────────┘

Request →
    │
    ├─► [1] ExceptionMiddleware
    │        └─ Catches all exceptions
    │        └─ Returns error response
    │
    ├─► [2] CORSMiddleware
    │        └─ Adds CORS headers
    │        └─ Handles preflight
    │
    ├─► [3] RequestLoggingMiddleware
    │        └─ Logs request start
    │        └─ Adds correlation ID
    │
    ├─► [4] AuthenticationMiddleware
    │        └─ Validates JWT token
    │        └─ Loads user context
    │
    ├─► [5] RateLimitMiddleware
    │        └─ Checks rate limits
    │        └─ Returns 429 if exceeded
    │
    ├─► [6] InputValidationMiddleware
    │        └─ Validates request data
    │        └─ Sanitizes input
    │
    ├─► [7] SessionMiddleware
    │        └─ Loads session data
    │        └─ Manages session lifecycle
    │
    └─► [Handler] Route Handler
             │
             └─► Response
                      │
    ┌─────────────────┘
    │
    ├─◄ [7] SessionMiddleware
    │        └─ Saves session data
    │
    ├─◄ [6] InputValidationMiddleware
    │        └─ (no response processing)
    │
    ├─◄ [5] RateLimitMiddleware
    │        └─ (no response processing)
    │
    ├─◄ [4] AuthenticationMiddleware
    │        └─ (no response processing)
    │
    ├─◄ [3] RequestLoggingMiddleware
    │        └─ Logs response
    │        └─ Records duration
    │
    ├─◄ [2] CORSMiddleware
    │        └─ Adds CORS headers
    │
    └─◄ [1] ExceptionMiddleware
             └─ (already caught exceptions)
                  │
                  └─► Response
```

### 6.2 Middleware Interface

```python
class Middleware:
    """Base middleware interface"""

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Process request and response.

        Args:
            request: HTTP request object
            call_next: Next middleware in chain

        Returns:
            HTTP response object
        """
        # Before request processing
        # Modify request, check conditions, etc.

        response = await call_next(request)

        # After request processing
        # Modify response, add headers, etc.

        return response
```

---

## 7. Database Layer

### 7.1 Database Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

Application Layer
      │
      ▼
┌─────────────────┐
│ ORM/Models      │  High-level API
│                 │  ├─ Model definitions
│                 │  ├─ Relationships
│                 │  └─ Validation
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Query Builder   │  SQL generation
│                 │  ├─ Fluent interface
│                 │  ├─ JOIN support
│                 │  └─ Aggregations
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Connection Pool │  Connection management
│                 │  ├─ Connection reuse
│                 │  ├─ Health checks
│                 │  └─ Load balancing
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Database Adapter│  Database-specific
│                 │  ├─ PostgreSQL
│                 │  ├─ MySQL
│                 │  └─ SQLite
└─────────────────┘
      │
      ▼
Database Server
```

---

## 8. Security Architecture

### 8.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                              │
└─────────────────────────────────────────────────────────────────┘

Layer 1: Input Validation
    ├─ SQL injection prevention
    ├─ XSS prevention
    ├─ Command injection prevention
    └─ Path traversal prevention

Layer 2: Authentication
    ├─ JWT token validation
    ├─ Password hashing (bcrypt/argon2)
    ├─ 2FA support
    └─ Session management

Layer 3: Authorization
    ├─ Role-based access control (RBAC)
    ├─ Permission checking
    ├─ Resource ownership
    └─ API key validation

Layer 4: Rate Limiting
    ├─ Token bucket
    ├─ Sliding window
    ├─ Fixed window
    └─ Per-user/IP limits

Layer 5: Error Handling
    ├─ Context sanitization
    ├─ Stack trace filtering
    ├─ Secure error messages
    └─ Audit logging
```

---

## 9. Deployment Architecture

### 9.1 Production Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                  PRODUCTION ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

Load Balancer (nginx/HAProxy)
      │
      ├─► ASGI Server 1 (uvicorn)
      │        └─► CovetASGIApp
      │
      ├─► ASGI Server 2 (uvicorn)
      │        └─► CovetASGIApp
      │
      └─► ASGI Server N (uvicorn)
               └─► CovetASGIApp

Database
      ├─► Primary (read/write)
      └─► Replicas (read-only)

Cache
      └─► Redis (session, rate limiting)

Monitoring
      ├─► Prometheus (metrics)
      ├─► Grafana (dashboards)
      └─► ELK Stack (logs)
```

### 9.2 Scaling Strategy

```
Horizontal Scaling:
    ├─ Multiple ASGI workers per server
    ├─ Multiple servers behind load balancer
    └─ Database read replicas

Vertical Scaling:
    ├─ Increase worker count
    ├─ Increase connection pool size
    └─ Optimize resource limits

Caching:
    ├─ Application-level caching
    ├─ Database query caching
    └─ CDN for static assets
```

---

## Appendix: Migration Guides

### A. Migrating from CovetApp to CovetApplication

```python
# OLD (deprecated)
from covet.core import CovetApp
app = CovetApp(title="My API")

# NEW (recommended)
from covet.core import CovetApplication
app = CovetApplication(title="My API")

# OR use factory
from covet.core import Covet
app = Covet.create_app(title="My API")
```

### B. Exception Handling Migration

```python
# OLD (bare except)
try:
    result = risky_operation()
except:
    return error_response("Error", 500)

# NEW (specific exceptions)
try:
    result = risky_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    return error_response("Invalid input", 400)
except DatabaseError as e:
    logger.error(f"Database error: {e}", exc_info=True)
    return error_response("Database error", 500)
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-10
**Maintained By:** CovetPy Core Team
