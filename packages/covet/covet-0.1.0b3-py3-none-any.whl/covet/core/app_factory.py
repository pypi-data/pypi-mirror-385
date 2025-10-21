"""
Application Factory for CovetPy

Provides intelligent app creation that can use either:
1. Pure Python implementation (zero dependencies)
2. FastAPI-powered implementation (production performance)

The factory automatically selects the best implementation based on
available dependencies and user preferences.
"""

import os
from typing import Any, Optional, Type


def create_covet_app(
    backend: Optional[str] = None, use_fastapi: Optional[bool] = None, **kwargs
) -> Any:
    """
    Create a CovetPy application with the specified backend.

    Args:
        backend: Backend to use ("pure", "fastapi", or None for auto-detect)
        use_fastapi: Legacy parameter, True to use FastAPI backend
        **kwargs: Additional arguments passed to the app constructor

    Returns:
        CovetPy application instance

    The factory will:
    1. Use FastAPI if explicitly requested
    2. Use FastAPI if available and not explicitly disabled
    3. Fall back to pure Python implementation otherwise
    """
    # Determine backend preference
    if backend is None:
        if use_fastapi is not None:
            backend = "fastapi" if use_fastapi else "pure"
        else:
            # Check environment variable
            backend = os.environ.get("COVET_BACKEND", "auto")

    # Handle auto-detection
    if backend == "auto":
        try:
            import fastapi
            import uvicorn

            backend = "fastapi"
        except ImportError:
            backend = "pure"

    # Create the appropriate implementation
    if backend == "fastapi":
        try:
            from .fastapi_integration import CovetPyFastAPI

            return CovetPyFastAPI(**kwargs)
        except ImportError:
            # Provide helpful error message
            import warnings

            warnings.warn(
                "FastAPI backend requested but not available. "
                "Install with: pip install 'covet[web]' or pip install fastapi uvicorn\n"
                "Falling back to pure Python implementation.",
                RuntimeWarning,
            )
            backend = "pure"

    # Default to pure Python implementation
    if backend == "pure" or backend is None:
        # Import the CovetPy wrapper from main __init__
        import sys

        from .app_pure import CovetApplication

        parent = sys.modules[__name__.rsplit(".", 1)[0]]
        if hasattr(parent, "CovetPy"):
            # Use the wrapper class that provides the simple API
            return parent.CovetPy(**kwargs)
        else:
            # Direct app creation
            return CovetApplication(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}. Use 'pure' or 'fastapi'.")


# Convenience aliases
def create_pure_app(**kwargs) -> Any:
    """Create a pure Python CovetPy app (zero dependencies)."""
    return create_covet_app(backend="pure", **kwargs)


def create_fastapi_app(**kwargs) -> Any:
    """Create a FastAPI-powered CovetPy app (production performance)."""
    return create_covet_app(backend="fastapi", **kwargs)


# Export the factory and specific creators
__all__ = [
    "create_covet_app",
    "create_pure_app",
    "create_fastapi_app",
]
