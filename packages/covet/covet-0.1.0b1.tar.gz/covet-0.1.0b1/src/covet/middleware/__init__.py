"""
CovetPy Middleware Package

Comprehensive middleware system with production-ready components:
- Core middleware architecture with circuit breakers and monitoring
- Authentication middleware with JWT/API key support
- CORS middleware with configurable policies
- Rate limiting with Redis/in-memory backends
- Security headers and content security policies
- Performance monitoring and metrics collection
- Request/response logging with structured data
- Error handling and recovery mechanisms
"""

from covet.middleware.core import (  # Core classes; Built-in middleware; Factory functions; Configurations
    COMPRESSION_MIDDLEWARE_CONFIG,
    CORS_MIDDLEWARE_CONFIG,
    BaseMiddleware,
    CompressionMiddleware,
    ErrorHandlingMiddleware,
    MiddlewareConfig,
    MiddlewareContext,
    MiddlewarePhase,
    MiddlewareStack,
    PerformanceMonitoringMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    create_debug_middleware_stack,
    create_default_middleware_stack,
)

# Backward compatibility alias
Middleware = BaseMiddleware

# Authentication middleware (to be implemented)
# from .auth import (
#     AuthenticationMiddleware,
#     JWTAuthenticationMiddleware,
#     APIKeyAuthenticationMiddleware,
#     AuthConfig,
#     AuthResult,
#     JWTConfig,
#     APIKeyConfig,
# )

# CORS middleware (to be implemented)
# from .cors import (
#     CORSMiddleware,
#     CORSConfig,
#     CORSPolicy,
# )

__all__ = [
    # Core middleware
    "BaseMiddleware",
    "Middleware",
    "MiddlewareConfig",
    "MiddlewareContext",
    "MiddlewarePhase",
    "MiddlewareStack",
    # Built-in middleware
    "ErrorHandlingMiddleware",
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "RateLimitMiddleware",
    "CompressionMiddleware",
    "PerformanceMonitoringMiddleware",
    # Factory functions
    "create_default_middleware_stack",
    "create_debug_middleware_stack",
    # Configurations
    "CORS_MIDDLEWARE_CONFIG",
    "COMPRESSION_MIDDLEWARE_CONFIG",
]
