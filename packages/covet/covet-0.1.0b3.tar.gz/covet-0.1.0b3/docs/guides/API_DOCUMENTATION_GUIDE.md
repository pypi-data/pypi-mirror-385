# API Documentation Guide

**Complete guide to documenting APIs with CovetPy**

This guide covers everything you need to create production-grade API documentation using CovetPy's comprehensive documentation generation tools.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [OpenAPI Specification Generation](#openapi-specification-generation)
3. [Interactive Documentation (Swagger UI)](#interactive-documentation-swagger-ui)
4. [Beautiful Documentation (ReDoc)](#beautiful-documentation-redoc)
5. [Markdown Documentation](#markdown-documentation)
6. [Automatic Examples](#automatic-examples)
7. [Postman Collections](#postman-collections)
8. [Authentication Documentation](#authentication-documentation)
9. [Advanced Features](#advanced-features)
10. [Production Best Practices](#production-best-practices)

---

## Quick Start

Get started with API documentation in 5 minutes:

```python
from covet.api.docs import OpenAPIGenerator, SwaggerUI
from pydantic import BaseModel

# Define your models
class User(BaseModel):
    id: int
    name: str
    email: str

# Create documentation generator
generator = OpenAPIGenerator(
    title="My API",
    version="1.0.0",
    description="Production API"
)

# Add routes
generator.add_route(
    path="/users/{user_id}",
    method="GET",
    response_model=User,
    summary="Get user",
    tags=["Users"]
)

# Generate OpenAPI spec
spec = generator.generate_spec()

# Create Swagger UI
swagger = SwaggerUI()
html = swagger.get_html()

# Save documentation
generator.save_json("openapi.json")
with open("docs.html", "w") as f:
    f.write(html)
```

---

## OpenAPI Specification Generation

### Basic Setup

```python
from covet.api.docs import OpenAPIGenerator

generator = OpenAPIGenerator(
    title="My API",
    version="1.0.0",
    description="API description with Markdown support",
    contact={
        "name": "API Support",
        "email": "support@example.com",
        "url": "https://example.com/support"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0"
    },
    servers=[
        {"url": "https://api.example.com", "description": "Production"},
        {"url": "https://staging.example.com", "description": "Staging"}
    ]
)
```

### Adding Routes

#### Simple GET Endpoint

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(..., example=1, description="User ID")
    name: str = Field(..., example="John Doe")
    email: str = Field(..., example="john@example.com")

def get_user(user_id: int):
    """Get user by ID."""
    pass

generator.add_route(
    path="/users/{user_id}",
    method="GET",
    handler=get_user,
    response_model=User,
    summary="Get user",
    description="Retrieve user information by ID",
    tags=["Users"]
)
```

#### POST with Request Body

```python
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., format="email")
    password: str = Field(..., min_length=8)

def create_user(user: UserCreate):
    """Create a new user."""
    pass

generator.add_route(
    path="/users",
    method="POST",
    handler=create_user,
    request_model=UserCreate,
    response_model=User,
    summary="Create user",
    tags=["Users"],
    responses={
        400: {"description": "Invalid input"},
        409: {"description": "User already exists"}
    }
)
```

### Path and Query Parameters

Parameters are automatically extracted from:
- Path placeholders: `/users/{user_id}`
- Function signatures: `def list_users(page: int = 1, limit: int = 20)`

```python
def list_users(page: int = 1, limit: int = 20, search: Optional[str] = None):
    """
    List users with pagination and search.

    Args:
        page: Page number (1-indexed)
        limit: Items per page
        search: Optional search query
    """
    pass

generator.add_route(
    path="/users",
    method="GET",
    handler=list_users,
    summary="List users"
)
# Automatically generates:
# - query parameter 'page' (optional, default=1)
# - query parameter 'limit' (optional, default=20)
# - query parameter 'search' (optional)
```

### Manual Parameters

```python
from covet.api.docs import OpenAPIParameter, ParameterLocation

generator.add_route(
    path="/users",
    method="GET",
    parameters=[
        OpenAPIParameter(
            name="X-Request-ID",
            in_=ParameterLocation.HEADER,
            description="Unique request identifier",
            required=False,
            schema_={"type": "string", "format": "uuid"}
        )
    ]
)
```

---

## Interactive Documentation (Swagger UI)

### Basic Configuration

```python
from covet.api.docs import SwaggerUI, SwaggerUIConfig, SwaggerUITheme

swagger = SwaggerUI(
    config=SwaggerUIConfig(
        spec_url="/openapi.json",
        title="API Documentation",
        persist_authorization=True,  # Remember tokens between refreshes
        display_request_duration=True,  # Show request time
        try_it_out_enabled=True,  # Enable try-it-out by default
        theme=SwaggerUITheme.LIGHT
    )
)

html = swagger.get_html()
```

### Custom Branding

```python
config = SwaggerUIConfig(
    spec_url="/openapi.json",
    title="My Brand API",
    custom_css="""
        .swagger-ui .topbar { background-color: #2c3e50; }
        .swagger-ui .topbar .download-url-wrapper { display: none; }
    """,
    custom_favicon="https://example.com/favicon.ico"
)

swagger = SwaggerUI(config=config)
```

### OAuth2 Configuration

```python
config = SwaggerUIConfig(
    spec_url="/openapi.json",
    oauth2_redirect_url="https://api.example.com/docs/oauth2-redirect",
    persist_authorization=True
)

swagger = SwaggerUI(config=config)

# Also generate OAuth2 redirect page
redirect_html = swagger.get_oauth2_redirect_html()
with open("oauth2-redirect.html", "w") as f:
    f.write(redirect_html)
```

### ASGI Integration

```python
from covet.api.rest import RESTFramework

app = RESTFramework(
    title="My API",
    version="1.0.0",
    enable_docs=True,
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
    openapi_url="/openapi.json"
)

# Routes automatically generate OpenAPI spec
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    pass

# Visit http://localhost:8000/docs for Swagger UI
```

---

## Beautiful Documentation (ReDoc)

### Basic Configuration

```python
from covet.api.docs import ReDocUI, ReDocConfig, ReDocTheme

redoc = ReDocUI(
    config=ReDocConfig(
        spec_url="/openapi.json",
        title="API Documentation",
        theme=ReDocTheme.DARK,
        hide_download_button=False,
        expand_responses="200,201",  # Auto-expand success responses
        required_props_first=True,
        native_scrollbars=True
    )
)

html = redoc.get_html()
```

### Custom Theming

```python
config = ReDocConfig(
    spec_url="/openapi.json",
    title="My Brand API",
    theme=ReDocTheme.DARK,
    primary_color="#FF6B6B",
    text_color="#FFFFFF",
    background_color="#1A1A1A",
    logo_url="https://example.com/logo.png",
    logo_href="https://example.com"
)

redoc = ReDocUI(config=config)
```

### Standalone HTML

For offline documentation or CDN-free deployment:

```python
# Generate single HTML file with embedded spec
standalone = redoc.get_standalone_html(openapi_spec=spec)

with open("api-docs.html", "w") as f:
    f.write(standalone)
```

---

## Markdown Documentation

### Generate for MkDocs

```python
from covet.api.docs import MarkdownGenerator, MarkdownConfig, MarkdownFormat

markdown_gen = MarkdownGenerator(
    spec=openapi_spec,
    config=MarkdownConfig(
        format=MarkdownFormat.MKDOCS,
        languages=["curl", "python", "javascript"],
        include_toc=True,
        include_schemas=True,
        group_by_tags=True,
        base_url="https://api.example.com"
    )
)

# Single file
markdown = markdown_gen.generate()
with open("docs/api.md", "w") as f:
    f.write(markdown)
```

### Split by Tags

```python
config = MarkdownConfig(
    format=MarkdownFormat.MKDOCS,
    split_by_tags=True  # Create separate file per tag
)

markdown_gen = MarkdownGenerator(spec=spec, config=config)
files = markdown_gen.generate_files()

for filename, content in files.items():
    with open(f"docs/{filename}", "w") as f:
        f.write(content)

# Creates:
# - docs/index.md (overview)
# - docs/users.md (Users tag)
# - docs/authentication.md (Authentication tag)
# - docs/schemas.md (all schemas)
```

### Custom Code Examples

Generated code examples include:

**cURL:**
```bash
curl -X GET "https://api.example.com/users/123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Python:**
```python
import requests

url = "https://api.example.com/users/123"
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}

response = requests.get(url, headers=headers)
print(response.json())
```

**JavaScript:**
```javascript
const url = "https://api.example.com/users/123";
const headers = {
    "Authorization": "Bearer YOUR_TOKEN"
};

fetch(url, { method: "GET", headers })
    .then(response => response.json())
    .then(data => console.log(data));
```

---

## Automatic Examples

### Generate from Models

```python
from covet.api.docs import ExampleGenerator, ExampleConfig

generator = ExampleGenerator(
    config=ExampleConfig(
        use_realistic_data=True,
        include_optional_fields=True,
        array_min_items=2,
        array_max_items=4
    )
)

# Generate single example
example = generator.generate_example(UserCreate)
# {"username": "johndoe", "email": "john@example.com", "password": "secure123"}

# Generate multiple examples
examples = generator.generate_examples(UserCreate, count=3)
for ex in examples:
    print(ex.summary, ex.value)
```

### Automatic Field Recognition

The generator recognizes common field patterns:

```python
class Contact(BaseModel):
    email: str          # → "user@example.com"
    phone: str          # → "+1-555-123-4567"
    name: str           # → "John Doe"
    website: str        # → "https://example.com"
    address: str        # → "123 Main St"
    city: str           # → "New York"
    country: str        # → "USA"
```

### Respect Constraints

```python
class Product(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., ge=0.0, le=10000.0)
    quantity: int = Field(..., ge=1, le=1000)
    tags: List[str] = Field(..., min_items=1, max_items=5)

example = generator.generate_example(Product)
# All constraints are respected:
# - name length between 3-50 chars
# - price between 0-10000
# - quantity between 1-1000
# - tags array with 1-5 items
```

### Add to OpenAPI Operations

```python
generator.add_examples_to_operation(
    operation=operation_dict,
    request_model=UserCreate,
    response_model=UserResponse
)
# Automatically adds request and response examples to operation
```

---

## Postman Collections

### Generate Collection

```python
from covet.api.docs import PostmanCollection

collection = PostmanCollection(
    name="My API",
    openapi_spec=spec,
    base_url="https://api.example.com",
    description="Complete API collection"
)

# Generate collection JSON
collection_json = collection.generate()

with open("postman_collection.json", "w") as f:
    import json
    json.dump(collection_json, f, indent=2)
```

### Custom Authentication

```python
from covet.api.docs import PostmanAuth, PostmanAuthType

# Bearer token
auth = PostmanAuth(
    type=PostmanAuthType.BEARER,
    bearer=[
        {"key": "token", "value": "{{bearer_token}}", "type": "string"}
    ]
)

collection.set_auth(auth)

# API Key
auth = PostmanAuth(
    type=PostmanAuthType.API_KEY,
    apikey=[
        {"key": "key", "value": "X-API-Key", "type": "string"},
        {"key": "value", "value": "{{api_key}}", "type": "string"},
        {"key": "in", "value": "header", "type": "string"}
    ]
)
```

### Environment Variables

```python
# Add collection variables
collection.add_variable("base_url", "https://api.example.com")
collection.add_variable("api_key", "", "Your API key")

# Generate environment file
env = collection.generate_environment(
    "Production",
    additional_vars={
        "base_url": "https://api.example.com",
        "api_key": "your_production_key"
    }
)

with open("production.postman_environment.json", "w") as f:
    import json
    json.dump(env, f, indent=2)
```

---

## Authentication Documentation

### JWT Bearer Authentication

```python
from covet.api.docs import SecurityScheme, SecuritySchemeType

generator.add_security_scheme(
    "bearer_auth",
    SecurityScheme(
        type=SecuritySchemeType.HTTP,
        scheme="bearer",
        bearer_format="JWT",
        description="""
        JWT authentication via Bearer token.

        Obtain token from /auth/login endpoint and include in requests:
        ```
        Authorization: Bearer YOUR_TOKEN
        ```
        """
    )
)

# Apply globally
generator.set_global_security([{"bearer_auth": []}])

# Or per-endpoint
generator.add_route(
    path="/protected",
    method="GET",
    security=[{"bearer_auth": []}]
)
```

### API Key Authentication

```python
generator.add_security_scheme(
    "api_key",
    SecurityScheme(
        type=SecuritySchemeType.API_KEY,
        name="X-API-Key",
        in_="header",
        description="API key for authentication"
    )
)
```

### OAuth 2.0

```python
generator.add_security_scheme(
    "oauth2",
    SecurityScheme(
        type=SecuritySchemeType.OAUTH2,
        flows={
            "authorizationCode": {
                "authorizationUrl": "https://auth.example.com/authorize",
                "tokenUrl": "https://auth.example.com/token",
                "scopes": {
                    "read": "Read access to resources",
                    "write": "Write access to resources",
                    "admin": "Administrative access"
                }
            }
        },
        description="OAuth 2.0 authorization code flow"
    )
)
```

### Multiple Auth Methods

```python
# Support multiple authentication methods
generator.add_security_scheme("bearer", bearer_scheme)
generator.add_security_scheme("api_key", api_key_scheme)

# Endpoint supports either method
generator.add_route(
    path="/data",
    method="GET",
    security=[
        {"bearer": []},
        {"api_key": []}
    ]
)
```

---

## Advanced Features

### Custom Response Types

```python
class SuccessResponse(BaseModel):
    data: User
    message: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict

generator.add_route(
    path="/users/{user_id}",
    method="GET",
    response_model=SuccessResponse,
    responses={
        200: SuccessResponse,  # Success with data
        400: ErrorResponse,     # Bad request
        401: ErrorResponse,     # Unauthorized
        404: ErrorResponse,     # Not found
        500: ErrorResponse      # Server error
    }
)
```

### Webhooks (OpenAPI 3.1)

```python
generator.add_webhook(
    "user_created",
    {
        "post": {
            "summary": "User created webhook",
            "description": "Called when a new user is created",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/User"}
                    }
                }
            },
            "responses": {
                "200": {"description": "Webhook received"}
            }
        }
    }
)
```

### Deprecated Endpoints

```python
generator.add_route(
    path="/legacy/users",
    method="GET",
    deprecated=True,
    summary="List users (deprecated)",
    description="This endpoint is deprecated. Use /v2/users instead."
)
```

### Operation-Specific Servers

```python
generator.add_route(
    path="/data",
    method="GET",
    servers=[
        {"url": "https://data-api.example.com", "description": "Data API server"}
    ]
)
```

---

## Production Best Practices

### 1. Comprehensive Model Documentation

```python
class User(BaseModel):
    """
    User account model.

    Represents a registered user in the system with profile information
    and metadata.
    """
    id: int = Field(
        ...,
        example=123,
        description="Unique user identifier (auto-generated)"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        example="johndoe",
        description="Unique username (alphanumeric and underscore only)"
    )
    email: str = Field(
        ...,
        format="email",
        example="john@example.com",
        description="User's email address (must be unique)"
    )
    created_at: datetime = Field(
        ...,
        example="2025-01-01T00:00:00Z",
        description="Account creation timestamp (UTC)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "username": "johndoe",
                "email": "john@example.com",
                "created_at": "2025-01-01T00:00:00Z"
            }
        }
```

### 2. Detailed Operation Documentation

```python
def get_user(user_id: int) -> User:
    """
    Get user by ID.

    Retrieves detailed information about a specific user account.
    Requires authentication via Bearer token.

    Args:
        user_id: Unique user identifier

    Returns:
        User object with complete profile information

    Raises:
        401: Unauthorized - Invalid or missing authentication token
        403: Forbidden - Insufficient permissions to access user
        404: Not Found - User with specified ID does not exist
        500: Internal Server Error - Unexpected server error

    Example:
        GET /users/123
        Authorization: Bearer eyJhbGc...

        Response:
        {
            "id": 123,
            "username": "johndoe",
            "email": "john@example.com",
            "created_at": "2025-01-01T00:00:00Z"
        }
    """
    pass
```

### 3. Organize with Tags

```python
# Define tags upfront
generator.add_tag(
    "Users",
    "User account management - CRUD operations for user accounts"
)
generator.add_tag(
    "Authentication",
    "Authentication and token management"
)
generator.add_tag(
    "Admin",
    "Administrative operations (requires admin role)"
)

# Use consistently
generator.add_route(..., tags=["Users"])
generator.add_route(..., tags=["Users", "Admin"])  # Multiple tags
```

### 4. Version Your API

```python
generator = OpenAPIGenerator(
    title="My API",
    version="2.1.0",  # Semantic versioning
    servers=[
        {"url": "https://api.example.com/v2", "description": "Version 2"},
        {"url": "https://api.example.com/v1", "description": "Version 1 (deprecated)"}
    ]
)
```

### 5. Include Rate Limiting Info

```python
generator = OpenAPIGenerator(
    title="My API",
    version="1.0.0",
    description="""
# My API

## Rate Limits

- 100 requests per minute per IP address
- 1000 requests per hour per authenticated user
- Rate limit headers included in all responses:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Reset timestamp

## Error Codes

- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INVALID_TOKEN`: Authentication token invalid
- `VALIDATION_ERROR`: Request validation failed
    """
)
```

### 6. Document Error Responses

```python
class StandardError(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional context")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: str = Field(..., description="Unique request identifier")

# Use for all error responses
generator.add_route(
    path="/users",
    method="POST",
    responses={
        400: StandardError,
        401: StandardError,
        403: StandardError,
        409: StandardError,
        422: StandardError,
        500: StandardError
    }
)
```

### 7. Serve Multiple Documentation Formats

```python
from covet.api.rest import RESTFramework

app = RESTFramework(
    title="My API",
    version="1.0.0",
    enable_docs=True
)

# Serve at multiple endpoints
# /docs          → Swagger UI (interactive)
# /redoc         → ReDoc (beautiful)
# /openapi.json  → OpenAPI spec (machine-readable)
# /api.md        → Markdown (static site generators)
```

### 8. Validate Generated Specs

```python
import json

# Generate spec
spec = generator.generate_spec()

# Validate structure
assert "openapi" in spec
assert spec["openapi"] in ["3.0.3", "3.1.0"]
assert "paths" in spec
assert "components" in spec

# Validate with external tools
# Use: openapi-spec-validator, swagger-cli, redocly lint
```

### 9. Keep Documentation in Sync

```python
# Use CI/CD to regenerate docs automatically
# Example GitHub Actions workflow:

"""
name: Generate API Docs

on: [push]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate OpenAPI spec
        run: python scripts/generate_docs.py
      - name: Validate spec
        run: npx @redocly/cli lint openapi.json
      - name: Deploy docs
        run: ./deploy-docs.sh
"""
```

### 10. Performance Optimization

```python
# For large APIs with 100+ endpoints:
# - Use lazy loading in Swagger UI
# - Enable ReDoc lazy rendering
# - Split Markdown docs by tags
# - Cache generated specs

config = SwaggerUIConfig(
    spec_url="/openapi.json",
    lazy_rendering=True,  # Don't render all at once
    default_models_expand_depth=1  # Don't expand all models
)

redoc_config = ReDocConfig(
    spec_url="/openapi.json",
    lazy_rendering=True,  # Render on scroll
    schema_expansion_level=1  # Collapse schemas by default
)
```

---

## Complete Production Example

```python
"""
Production API Documentation Setup
"""

from covet.api.docs import (
    OpenAPIGenerator,
    SwaggerUI,
    SwaggerUIConfig,
    ReDocUI,
    ReDocConfig,
    MarkdownGenerator,
    MarkdownConfig,
    PostmanCollection,
    SecurityScheme,
    SecuritySchemeType,
)

def setup_documentation():
    """Setup complete API documentation."""

    # 1. Create generator with full info
    generator = OpenAPIGenerator(
        title="Production API",
        version="2.0.0",
        description=open("API_OVERVIEW.md").read(),
        contact={
            "name": "API Support",
            "email": "api-support@example.com",
            "url": "https://example.com/support"
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0"
        },
        servers=[
            {"url": "https://api.example.com/v2", "description": "Production"},
            {"url": "https://staging-api.example.com/v2", "description": "Staging"},
            {"url": "http://localhost:8000/v2", "description": "Local development"}
        ]
    )

    # 2. Configure security
    generator.add_security_scheme(
        "bearer_auth",
        SecurityScheme(
            type=SecuritySchemeType.HTTP,
            scheme="bearer",
            bearer_format="JWT",
            description="JWT Bearer token authentication"
        )
    )

    # 3. Define tags
    generator.add_tag("Users", "User management operations")
    generator.add_tag("Auth", "Authentication endpoints")
    generator.add_tag("Admin", "Administrative operations")

    # 4. Add all routes (from your application)
    # ... add_route calls ...

    # 5. Generate OpenAPI spec
    spec = generator.generate_spec()
    generator.save_json("docs/openapi.json", indent=2)
    generator.save_yaml("docs/openapi.yaml")

    # 6. Generate Swagger UI
    swagger = SwaggerUI(
        config=SwaggerUIConfig(
            spec_url="/openapi.json",
            title="Production API - Interactive Docs",
            persist_authorization=True
        )
    )
    with open("docs/swagger.html", "w") as f:
        f.write(swagger.get_html())

    # 7. Generate ReDoc
    redoc = ReDocUI(
        config=ReDocConfig(
            spec_url="/openapi.json",
            title="Production API - Documentation"
        )
    )
    with open("docs/redoc.html", "w") as f:
        f.write(redoc.get_html())

    # 8. Generate Markdown docs
    markdown_gen = MarkdownGenerator(
        spec=spec,
        config=MarkdownConfig(split_by_tags=True)
    )
    markdown_files = markdown_gen.generate_files()
    for filename, content in markdown_files.items():
        with open(f"docs/markdown/{filename}", "w") as f:
            f.write(content)

    # 9. Generate Postman collection
    postman = PostmanCollection(
        name="Production API",
        openapi_spec=spec,
        base_url="https://api.example.com/v2"
    )
    collection = postman.generate()
    with open("docs/postman_collection.json", "w") as f:
        json.dump(collection, f, indent=2)

    # 10. Generate environments
    for env_name, base_url in [
        ("Production", "https://api.example.com/v2"),
        ("Staging", "https://staging-api.example.com/v2"),
        ("Development", "http://localhost:8000/v2")
    ]:
        env = postman.generate_environment(
            env_name,
            {"base_url": base_url}
        )
        with open(f"docs/postman_{env_name.lower()}.json", "w") as f:
            json.dump(env, f, indent=2)

    print("✓ Documentation generated successfully!")
    print("  - OpenAPI spec: docs/openapi.json, docs/openapi.yaml")
    print("  - Swagger UI: docs/swagger.html")
    print("  - ReDoc: docs/redoc.html")
    print("  - Markdown: docs/markdown/*.md")
    print("  - Postman: docs/postman_*.json")

if __name__ == "__main__":
    setup_documentation()
```

---

## Resources

### OpenAPI Specification
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [OpenAPI Examples](https://github.com/OAI/OpenAPI-Specification/tree/main/examples)

### Tools
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [ReDoc](https://github.com/Redocly/redoc)
- [Postman](https://www.postman.com/)
- [MkDocs](https://www.mkdocs.org/)

### Validation
- [OpenAPI Validator](https://github.com/OpenAPITools/openapi-schema-validator)
- [Redocly CLI](https://redocly.com/docs/cli/)

---

## Support

For questions, issues, or contributions:
- GitHub: https://github.com/covetpy/covet
- Documentation: https://docs.covetpy.dev
- Discord: https://discord.gg/covetpy

---

**Generated with CovetPy v1.0.0**
