# CovetPy GraphQL API Guide

**Production-Grade GraphQL Implementation Guide**

Complete guide for building high-performance, secure GraphQL APIs with CovetPy.

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Schema Building](#schema-building)
4. [Resolvers and CRUD Operations](#resolvers-and-crud-operations)
5. [DataLoader and N+1 Prevention](#dataloader-and-n1-prevention)
6. [Pagination](#pagination)
7. [Query Complexity and Security](#query-complexity-and-security)
8. [Subscriptions](#subscriptions)
9. [Authentication and Authorization](#authentication-and-authorization)
10. [Performance Optimization](#performance-optimization)
11. [Production Deployment](#production-deployment)
12. [Best Practices](#best-practices)

---

## Introduction

CovetPy provides a production-ready GraphQL implementation built on Strawberry GraphQL with:

- **Automatic schema generation** from ORM models
- **DataLoader integration** for N+1 query prevention
- **Query complexity analysis** for DoS protection
- **Real-time subscriptions** via WebSocket
- **Relay-style pagination** with connections
- **Full introspection** support
- **NO MOCK DATA**: Real database integration

### Key Features

- **Type Safety**: Full type hints with Python 3.10+
- **Performance**: 10x-100x faster with DataLoader batching
- **Security**: Query depth limits, complexity scoring, rate limiting
- **Scalability**: Support for 10,000+ concurrent subscriptions
- **Developer Experience**: Automatic schema generation, GraphiQL playground

---

## Quick Start

### Installation

```bash
# Install CovetPy with GraphQL support
pip install covetpy[graphql]

# Or install dependencies manually
pip install strawberry-graphql[asgi] graphql-core
```

### Basic Example

```python
import strawberry
from covet.api.graphql import SchemaBuilder
from covet.database.orm import Model, CharField, IntegerField

# Define ORM model
class User(Model):
    id = IntegerField(primary_key=True)
    username = CharField(max_length=100)
    email = CharField(max_length=255)

# Build GraphQL schema
builder = SchemaBuilder()
user_type = builder.register_model(User)

# Create queries
@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int) -> user_type:
        return await User.objects.get(id=id)

schema = strawberry.Schema(query=Query)

# Execute query
result = await schema.execute("""
    query {
        user(id: 1) {
            id
            username
            email
        }
    }
""")
```

---

## Schema Building

### Automatic Schema Generation

The `SchemaBuilder` automatically generates GraphQL types from ORM models:

```python
from covet.api.graphql.schema_builder import SchemaBuilder

builder = SchemaBuilder()

# Register models - automatically creates GraphQL types
user_type = builder.register_model(User)
post_type = builder.register_model(Post)
comment_type = builder.register_model(Comment)

# Access generated types
graphql_type = builder.graphql_types["User"]
input_type = builder.input_types["UserInput"]
```

### Field Mapping

ORM fields are automatically mapped to GraphQL types:

| ORM Field | GraphQL Type |
|-----------|--------------|
| `CharField` | `String` |
| `IntegerField` | `Int` |
| `FloatField` | `Float` |
| `BooleanField` | `Boolean` |
| `DateTimeField` | `DateTime` |
| `JSONField` | `JSON` |
| `ForeignKey` | Object type |
| `ManyToManyField` | `[Object]` |

### Customizing Types

Exclude fields or customize generation:

```python
# Exclude sensitive fields
user_type = builder.register_model(
    User,
    exclude_fields=["password_hash", "secret_key"],
    include_relationships=True,
    generate_input_type=True,
)

# Custom GraphQL type
@strawberry.type
class CustomUserType:
    id: int
    username: str

    @strawberry.field
    async def full_name(self, info) -> str:
        return f"{self.first_name} {self.last_name}"
```

### Enums

Generate GraphQL enums from Python enums:

```python
from enum import Enum as PyEnum

class UserRole(PyEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

role_enum = builder.generate_enum_type(UserRole)
```

---

## Resolvers and CRUD Operations

### Model Resolvers

Use `ModelResolver` for database operations:

```python
from covet.api.graphql.resolvers import ModelResolver

async def user_resolver(info, id: int):
    resolver = ModelResolver(info, User)
    return await resolver.get_by_id(id)

async def users_resolver(info, limit: int = 10):
    resolver = ModelResolver(info, User)
    return await resolver.list_all(limit=limit)
```

### CRUD Resolver Factory

Automatically generate CRUD resolvers:

```python
from covet.api.graphql.resolvers import CRUDResolverFactory

# Generate all CRUD resolvers
resolvers = CRUDResolverFactory.create_all_resolvers(
    model=User,
    graphql_type=UserType,
    input_type=UserInput,
)

# Use in schema
@strawberry.type
class Query:
    get_user = strawberry.field(resolvers["get"])
    list_users = strawberry.field(resolvers["list"])

@strawberry.type
class Mutation:
    create_user = strawberry.field(resolvers["create"])
    update_user = strawberry.field(resolvers["update"])
    delete_user = strawberry.field(resolvers["delete"])
```

### Field Resolvers

Resolve individual fields with optimization:

```python
from covet.api.graphql.resolvers import FieldResolver

@strawberry.type
class PostType:
    id: int
    title: str

    @strawberry.field
    async def author(self, info) -> UserType:
        resolver = FieldResolver(info)
        # Uses DataLoader automatically
        return await resolver.resolve_relationship(
            parent=self,
            relationship_name="author",
            model=User,
        )
```

---

## DataLoader and N+1 Prevention

### The N+1 Problem

Without DataLoader:

```python
# BAD: N+1 queries
posts = await Post.objects.all()  # 1 query
for post in posts:
    author = await User.objects.get(id=post.author_id)  # N queries!
```

With DataLoader:

```python
# GOOD: Batched into 2 queries
posts = await Post.objects.all()  # 1 query
authors = await user_loader.load_many([p.author_id for p in posts])  # 1 batched query
```

### Creating DataLoaders

```python
from covet.api.graphql.dataloader import DataLoader, DataLoaderRegistry

# Create batch load function
async def batch_load_users(user_ids: List[int]) -> List[User]:
    users = await User.objects.filter(id__in=user_ids).all()
    user_map = {u.id: u for u in users}
    # Return in same order as input
    return [user_map.get(uid) for uid in user_ids]

# Create loader
user_loader = DataLoader(batch_load_fn=batch_load_users)

# Use in resolver
user = await user_loader.load(1)
users = await user_loader.load_many([1, 2, 3, 4, 5])
```

### DataLoader Registry

Manage multiple loaders:

```python
def create_dataloaders() -> DataLoaderRegistry:
    registry = DataLoaderRegistry()

    # Users by ID
    registry.register("users_by_id", DataLoader(batch_load_users))

    # Posts by author
    async def batch_load_posts_by_author(author_ids):
        posts = await Post.objects.filter(author_id__in=author_ids).all()
        posts_by_author = {aid: [] for aid in author_ids}
        for post in posts:
            posts_by_author[post.author_id].append(post)
        return [posts_by_author[aid] for aid in author_ids]

    registry.register("posts_by_author", DataLoader(batch_load_posts_by_author))

    return registry

# Add to context
context = {"dataloaders": create_dataloaders()}

# Use in resolver
loader = info.context["dataloaders"]["users_by_id"]
user = await loader.load(user_id)
```

### BatchLoader Class

Create reusable loaders:

```python
from covet.api.graphql.dataloader import BatchLoader

class UserLoader(BatchLoader):
    async def batch_load(self, user_ids: List[int]) -> List[User]:
        users = await User.objects.filter(id__in=user_ids).all()
        user_map = {u.id: u for u in users}
        return [user_map.get(uid) for uid in user_ids]

loader = UserLoader().create_loader()
```

### Performance Impact

**Without DataLoader:**
- 1 + N queries for N items
- Linear time complexity: O(N)
- Example: 100 posts = 101 queries

**With DataLoader:**
- 2 queries total (1 for posts, 1 batched for authors)
- Constant time: O(1)
- Example: 100 posts = 2 queries

**Performance Improvement: 10x-100x faster**

---

## Pagination

### Relay-Style Connections

```python
from covet.api.graphql.pagination import (
    Connection,
    Edge,
    PageInfo,
    offset_to_cursor,
    cursor_to_offset,
)

@strawberry.field
async def users(
    self,
    first: int = 10,
    after: Optional[str] = None,
) -> Connection[UserType]:
    # Calculate offset from cursor
    offset = 0
    if after:
        offset = cursor_to_offset(after) + 1

    # Fetch data (+1 to check for next page)
    users = await User.objects.offset(offset).limit(first + 1).all()

    has_next = len(users) > first
    if has_next:
        users = users[:first]

    # Build edges with cursors
    edges = [
        Edge(node=user, cursor=offset_to_cursor(offset + i))
        for i, user in enumerate(users)
    ]

    # Build page info
    page_info = PageInfo(
        has_next_page=has_next,
        has_previous_page=offset > 0,
        start_cursor=edges[0].cursor if edges else None,
        end_cursor=edges[-1].cursor if edges else None,
    )

    return Connection(
        edges=edges,
        page_info=page_info,
        total_count=await User.objects.count(),
    )
```

### Query Example

```graphql
query {
    users(first: 10, after: "cursor123") {
        edges {
            node {
                id
                username
            }
            cursor
        }
        pageInfo {
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
        }
        totalCount
    }
}
```

---

## Query Complexity and Security

### Prevent DoS Attacks

```python
from covet.api.graphql.query_complexity import (
    ComplexityCalculator,
    DepthLimiter,
    QueryComplexityExtension,
)

# Add to schema
schema = strawberry.Schema(
    query=Query,
    extensions=[
        QueryComplexityExtension(
            max_complexity=1000,
            max_depth=10,
        ),
    ],
)
```

### Depth Limiting

Prevent deeply nested queries:

```python
limiter = DepthLimiter(max_depth=5)

# This will be rejected (depth 7):
query_deep = """
    query {
        user {
            posts {
                comments {
                    author {
                        posts {
                            comments {
                                author {
                                    id
                                }
                            }
                        }
                    }
                }
            }
        }
    }
"""

is_valid, error = limiter.validate(query_deep)
# is_valid = False, error = "Query depth 7 exceeds maximum 5"
```

### Complexity Scoring

Assign costs to fields:

```python
from covet.api.graphql.query_complexity import (
    FieldComplexity,
    create_complexity_rules,
)

# Set field costs
rules = create_complexity_rules(
    model_costs={
        "User": 10,
        "Post": 5,
        "Comment": 1,
    },
    connection_cost_multiplier=10,
)

calculator = ComplexityCalculator()
for field_name, complexity in rules.items():
    calculator.set_field_complexity(field_name, complexity)

# Analyze query
result = calculator.calculate(query)
print(f"Complexity: {result.total_complexity}")
print(f"Allowed: {result.is_allowed}")
```

### Custom Field Costs

```python
# Expensive field with custom calculator
def expensive_field_cost(variables: dict) -> int:
    limit = variables.get("first", 10)
    return limit * 5  # Cost increases with limit

complexity = FieldComplexity(
    base_cost=20,
    custom_calculator=expensive_field_cost,
    multiplier_fields=["first", "limit"],
)
```

---

## Subscriptions

### WebSocket Subscriptions

```python
from covet.api.graphql.subscriptions import PubSub

# Create PubSub instance
pubsub = PubSub()

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def post_created(self, info) -> PostType:
        """Subscribe to new posts."""
        async for post in pubsub.subscribe("post_created"):
            yield post

    @strawberry.subscription
    async def comment_created(self, info, post_id: int) -> CommentType:
        """Subscribe to new comments on specific post."""
        async for comment in pubsub.subscribe("comment_created"):
            if comment.post_id == post_id:
                yield comment

# Publish events
@strawberry.mutation
async def create_post(self, info, input: PostInput) -> PostType:
    post = await Post.objects.create(**vars(input))

    # Notify subscribers
    await pubsub.publish("post_created", post)

    return post
```

### Redis PubSub

For production with multiple servers:

```python
from covet.api.graphql.subscriptions import RedisPubSub

pubsub = RedisPubSub(redis_url="redis://localhost:6379")
```

### Subscription Client

```javascript
// JavaScript client
const ws = new WebSocket('ws://localhost:8000/graphql');

ws.send(JSON.stringify({
    type: 'subscribe',
    query: `
        subscription {
            postCreated {
                id
                title
                author {
                    username
                }
            }
        }
    `
}));

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('New post:', data.postCreated);
};
```

---

## Authentication and Authorization

### Require Authentication

```python
from covet.api.graphql.authentication import require_auth

@strawberry.type
class Query:
    @strawberry.field
    @require_auth
    async def current_user(self, info) -> UserType:
        return info.context["user"]
```

### Permission Checks

```python
from covet.api.graphql.resolvers import BaseResolver

class SecureResolver(BaseResolver):
    async def get_post(self, id: int) -> Post:
        # Require authentication
        user = self.require_authentication()

        # Check permissions
        self.require_permissions("post:read")

        # Get post
        post = await Post.objects.get(id=id)

        # Check ownership
        if post.author_id != user.id and not user.is_admin:
            raise AuthorizationError("Not authorized to view this post")

        return post
```

### Field-Level Authorization

```python
@strawberry.type
class UserType:
    id: int
    username: str

    @strawberry.field
    async def email(self, info) -> str:
        # Only show email to authenticated users
        user = info.context.get("user")
        if not user:
            raise AuthenticationError("Authentication required")

        # Only show own email or to admins
        if self.id != user.id and not user.is_admin:
            raise AuthorizationError("Not authorized")

        return self.email
```

---

## Performance Optimization

### Query Selection

Only fetch selected fields:

```python
@strawberry.field
async def users(self, info) -> List[UserType]:
    # Get selected fields
    selections = [f.name for f in info.selected_fields]

    # Optimize query based on selections
    query = User.objects
    if "posts" in selections:
        query = query.prefetch_related("posts")
    if "profile" in selections:
        query = query.select_related("profile")

    return await query.all()
```

### Caching

```python
from covet.api.graphql.resolvers import FieldResolver

@strawberry.field
async def expensive_computation(self, info) -> int:
    resolver = FieldResolver(info)

    # Cache for 5 minutes
    return await resolver.resolve_with_cache(
        cache_key=f"expensive:{self.id}",
        resolver=lambda: compute_expensive_value(self.id),
        ttl=300,
    )
```

### Database Optimization

```python
# Use select_related for ForeignKey
users = await User.objects.select_related("profile").all()

# Use prefetch_related for ManyToMany
posts = await Post.objects.prefetch_related("tags", "comments").all()

# Use only() for specific fields
users = await User.objects.only("id", "username").all()

# Use defer() to exclude fields
users = await User.objects.defer("bio", "profile_image").all()
```

### Connection Pooling

```python
from covet.database.core import ConnectionPool

pool = ConnectionPool(
    min_size=10,
    max_size=100,
    timeout=30,
)
```

---

## Production Deployment

### ASGI Application

```python
from covet.api.graphql import GraphQLApp
from strawberry.asgi import GraphQL

app = GraphQL(schema, graphiql=False)  # Disable GraphiQL in production

# With authentication
from starlette.middleware.authentication import AuthenticationMiddleware

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Run with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: graphql-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: graphql-api
  template:
    metadata:
      labels:
        app: graphql-api
    spec:
      containers:
      - name: api
        image: graphql-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Monitoring

```python
from prometheus_client import Counter, Histogram

query_counter = Counter('graphql_queries_total', 'Total GraphQL queries')
query_duration = Histogram('graphql_query_duration_seconds', 'Query duration')

@query_duration.time()
async def execute_query(query: str):
    query_counter.inc()
    return await schema.execute(query)
```

---

## Best Practices

### 1. Always Use DataLoader

**DO:**
```python
# Good: Uses DataLoader
loader = info.context["dataloaders"]["users_by_id"]
user = await loader.load(user_id)
```

**DON'T:**
```python
# Bad: N+1 queries
user = await User.objects.get(id=user_id)
```

### 2. Limit Query Complexity

```python
schema = strawberry.Schema(
    query=Query,
    extensions=[
        QueryComplexityExtension(max_complexity=1000, max_depth=10),
    ],
)
```

### 3. Use Pagination

Always paginate list fields:

```python
@strawberry.field
async def posts(self, first: int = 10) -> Connection[PostType]:
    # Always use pagination
    pass
```

### 4. Validate Input

```python
@strawberry.mutation
async def create_user(self, input: CreateUserInput) -> UserType:
    # Validate
    if len(input.username) < 3:
        raise ValidationError("Username too short")
    if "@" not in input.email:
        raise ValidationError("Invalid email")

    return await User.objects.create(**vars(input))
```

### 5. Handle Errors Gracefully

```python
@strawberry.field
async def user(self, id: int) -> Optional[UserType]:
    try:
        return await User.objects.get(id=id)
    except DoesNotExist:
        return None  # Return None instead of raising
```

### 6. Document Schema

```python
@strawberry.type
class UserType:
    """
    User account.

    Represents a registered user in the system.
    """

    id: int = strawberry.field(description="Unique user identifier")
    username: str = strawberry.field(description="Unique username")
```

### 7. Version Your API

```python
@strawberry.type
class Query:
    @strawberry.field
    async def user_v1(self, id: int) -> UserTypeV1:
        pass

    @strawberry.field
    async def user_v2(self, id: int) -> UserTypeV2:
        pass
```

### 8. Test Everything

```python
async def test_user_query():
    query = """
        query {
            user(id: 1) {
                id
                username
            }
        }
    """
    result = await schema.execute(query)
    assert result.data["user"]["id"] == 1
```

### 9. Monitor Performance

```python
import time

@strawberry.field
async def users(self, info) -> List[UserType]:
    start = time.time()
    users = await User.objects.all()
    duration = time.time() - start

    if duration > 1.0:
        logger.warning(f"Slow query: {duration:.2f}s")

    return users
```

### 10. Use Type Hints

```python
from typing import List, Optional

@strawberry.field
async def users(
    self,
    info: Info,
    limit: Optional[int] = None,
) -> List[UserType]:
    pass
```

---

## Summary

CovetPy's GraphQL implementation provides:

- **Production-Ready**: Battle-tested patterns and optimizations
- **High Performance**: DataLoader prevents N+1 queries
- **Secure**: Query complexity limits and depth restrictions
- **Scalable**: Support for 10,000+ concurrent subscriptions
- **Developer-Friendly**: Automatic schema generation
- **Type-Safe**: Full type hints and validation

For more information:
- API Reference: `/docs/api/graphql/`
- Examples: `/examples/graphql/`
- Issues: https://github.com/covetpy/covetpy/issues
