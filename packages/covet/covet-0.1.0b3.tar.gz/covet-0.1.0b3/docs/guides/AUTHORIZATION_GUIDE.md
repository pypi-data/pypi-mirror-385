# CovetPy Authorization System Guide

## Table of Contents

1. [Introduction](#introduction)
2. [RBAC vs ABAC](#rbac-vs-abac)
3. [Quick Start](#quick-start)
4. [RBAC Guide](#rbac-guide)
5. [ABAC Guide](#abac-guide)
6. [Policy Engine](#policy-engine)
7. [Decorators](#decorators)
8. [Middleware](#middleware)
9. [Multi-Tenant Authorization](#multi-tenant-authorization)
10. [Performance Optimization](#performance-optimization)
11. [Security Best Practices](#security-best-practices)
12. [Production Deployment](#production-deployment)

## Introduction

The CovetPy Authorization System provides production-ready authorization with both Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC). It's designed for high performance, scalability, and security.

### Key Features

- **Dual Authorization Models**: RBAC for simplicity, ABAC for complex scenarios
- **Unified Policy Engine**: Combine RBAC and ABAC with multiple strategies
- **High Performance**: <5ms cached authorization decisions, 100,000+ checks/sec
- **Complete Audit Trail**: Track all authorization decisions
- **Multi-Tenant Support**: Tenant isolation and hierarchical structures
- **Easy Integration**: Decorators, middleware, and programmatic APIs

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  (Routes, Controllers, Business Logic)                   │
└────────────────┬────────────────────────────────────────┘
                 │
       ┌─────────┴──────────┐
       │    Decorators      │  @require_permission()
       │    Middleware      │  @require_role()
       └─────────┬──────────┘  @require_policy()
                 │
┌────────────────┴────────────────────────────────────────┐
│         Policy Decision Point (PDP)                      │
│  ┌──────────────────┬───────────────────┐              │
│  │  RBAC Manager    │   ABAC Manager    │              │
│  │  (Roles/Perms)   │   (Policies)      │              │
│  └──────────────────┴───────────────────┘              │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│         Database Layer (ORM Integration)                 │
│  Roles | Permissions | Policies | Audit Logs            │
└─────────────────────────────────────────────────────────┘
```

## RBAC vs ABAC

### When to Use RBAC

Use RBAC when:
- Access control is based on user roles
- Permissions are relatively static
- Simple hierarchical permissions suffice
- Performance is critical (RBAC is faster)

**Example**: Blog system where admins can delete posts, editors can create/edit, users can comment.

### When to Use ABAC

Use ABAC when:
- Access control depends on multiple attributes
- Dynamic conditions are required (time, location, etc.)
- Ownership or relationship-based access
- Complex business rules

**Example**: Document management where users can edit documents they own, managers can edit department documents, and access is restricted during business hours.

### Hybrid Approach

Use both (recommended):
- RBAC for basic role-based permissions
- ABAC for complex scenarios and fine-grained control
- Policy engine to combine both strategies

## Quick Start

### Installation

```bash
pip install covetpy
```

### Basic RBAC Example

```python
from covet.security.authz import RBACManager, initialize_default_roles

# Initialize RBAC
rbac = RBACManager()
await initialize_default_roles(rbac)

# Create role
await rbac.create_role('editor', 'Content Editor', 'Can edit content')
await rbac.assign_permission_to_role('editor', 'posts:write')

# Assign role to user
await rbac.assign_role_to_user('user123', 'editor')

# Check permission
has_permission = await rbac.check_permission('user123', 'posts:write')
print(f"Can write posts: {has_permission}")  # True
```

### Basic ABAC Example

```python
from covet.security.authz import ABACManager, PolicyBuilder

# Initialize ABAC
abac = ABACManager()

# Create policy using builder
policy = (PolicyBuilder('read-own-documents')
    .allow()
    .when_subject(user_id='${resource.owner}')
    .when_resource(type='document')
    .for_actions(['read'])
    .build())

await abac.create_policy(**policy)

# Evaluate access
allowed, reason, policy_id = await abac.evaluate_access(
    subject={'user_id': 'user123'},
    resource={'type': 'document', 'owner': 'user123'},
    action='read'
)
print(f"Access: {'ALLOWED' if allowed else 'DENIED'}")
```

### Decorator Example

```python
from covet.security.authz import require_permission, require_role

@require_permission('posts:write')
async def create_post(request, title: str, content: str):
    # Only users with posts:write permission can access
    return {"id": 1, "title": title}

@require_role('admin', 'moderator')
async def delete_user(request, user_id: str):
    # Only admins or moderators can access
    return {"status": "deleted"}
```

## RBAC Guide

### Role Hierarchy

Create roles with parent-child relationships for inheritance:

```python
# Create parent role
await rbac.create_role('admin', 'Administrator', 'Full access', priority=100)
await rbac.assign_permission_to_role('admin', 'admin:*')

# Create child role (inherits admin permissions)
await rbac.create_role(
    'super_admin',
    'Super Administrator',
    'Ultimate access',
    parent_role='admin',
    priority=110
)
```

### Permission Wildcards

Use wildcards for flexible permission matching:

```python
# Grant all user permissions
await rbac.assign_permission_to_role('admin', 'users:*')

# Grant all read permissions
await rbac.assign_permission_to_role('viewer', '*:read')

# Grant specific resource permissions
await rbac.assign_permission_to_role('editor', 'posts:read:*')
```

### Scoped Permissions

Support global, organization, and project-level permissions:

```python
# Global permission
await rbac.assign_role_to_user('user123', 'admin', scope='global')

# Organization-level permission
await rbac.assign_role_to_user(
    'user456',
    'org_admin',
    scope='organization',
    scope_id='org_acme'
)

# Project-level permission
await rbac.assign_role_to_user(
    'user789',
    'project_lead',
    scope='project',
    scope_id='project_123'
)

# Check with scope
can_manage = await rbac.check_permission(
    'user456',
    'org:manage',
    scope='organization',
    scope_id='org_acme'
)
```

### Dynamic Role Evaluation

Roles and permissions are evaluated dynamically:

```python
# Get all user roles
roles = await rbac.get_user_roles('user123')

# Get all permissions (includes inherited)
permissions = await rbac.get_user_permissions('user123')

# Check multiple permissions
has_all = await rbac.check_all_permissions(
    'user123',
    ['posts:read', 'posts:write']
)

has_any = await rbac.check_any_permission(
    'user123',
    ['posts:delete', 'users:delete']
)
```

## ABAC Guide

### Policy Structure

ABAC policies consist of four attribute types:

```python
policy = {
    "name": "engineering-confidential-access",
    "effect": "allow",  # or "deny"
    "subject": {
        # User attributes
        "department": "engineering",
        "clearance_level": {"$gte": 3}
    },
    "resource": {
        # Resource attributes
        "type": "document",
        "classification": "confidential"
    },
    "action": ["read", "write"],
    "environment": {
        # Environmental attributes
        "time": {"$between": ["09:00", "17:00"]},
        "vpn_connected": True
    }
}
```

### Operators

ABAC supports rich comparison operators:

```python
{
    "$eq": value,           # Equal
    "$ne": value,           # Not equal
    "$gt": value,           # Greater than
    "$gte": value,          # Greater than or equal
    "$lt": value,           # Less than
    "$lte": value,          # Less than or equal
    "$in": [values],        # In list
    "$not_in": [values],    # Not in list
    "$contains": value,     # Contains (string/list)
    "$regex": pattern,      # Regex match
    "$between": [low, high],# Between two values
    "$exists": true/false   # Attribute exists
}
```

### Variable Substitution

Reference other attributes using `${path}` syntax:

```python
# Users can only read their own documents
policy = {
    "subject": {
        "user_id": "${resource.owner}"  # Match user_id to resource owner
    },
    "resource": {
        "type": "document"
    },
    "action": ["read"]
}

# Managers can access their department's resources
policy = {
    "subject": {
        "role": "manager",
        "department": "${resource.department}"
    },
    "resource": {
        "type": "report"
    },
    "action": ["read"]
}
```

### Policy Priority

Policies are evaluated in priority order (highest first). DENY policies should have higher priority:

```python
# High priority deny (evaluated first)
await abac.create_policy(
    name="deny-interns-classified",
    effect="deny",
    subject={"employee_type": "intern"},
    resource={"classification": "classified"},
    action=["read", "write"],
    priority=90  # High priority
)

# Lower priority allow
await abac.create_policy(
    name="allow-staff-internal",
    effect="allow",
    subject={"employee_type": "staff"},
    resource={"classification": "internal"},
    action=["read"],
    priority=50  # Lower priority
)
```

### PolicyBuilder

Use the fluent API for cleaner policy creation:

```python
from covet.security.authz import PolicyBuilder

policy = (PolicyBuilder("complex-access")
    .allow()
    .when_subject(
        department="engineering",
        clearance_level={"$gte": 3},
        employment_status="active"
    )
    .when_resource(
        type="design_document",
        status={"$not_in": ["archived", "deleted"]},
        shared=True
    )
    .for_actions(["read", "comment"])
    .when_environment(
        vpn_connected=True,
        business_hours=True
    )
    .with_description("Engineering access to shared design docs")
    .with_priority(55)
    .build())

await abac.create_policy(**policy)
```

## Policy Engine

The Policy Decision Point (PDP) combines RBAC and ABAC using various strategies.

### Decision Strategies

```python
from covet.security.authz import PolicyDecisionPoint, DecisionStrategy

# RBAC only
pdp = PolicyDecisionPoint(strategy=DecisionStrategy.RBAC_ONLY)

# ABAC only
pdp = PolicyDecisionPoint(strategy=DecisionStrategy.ABAC_ONLY)

# RBAC first, fallback to ABAC (recommended)
pdp = PolicyDecisionPoint(strategy=DecisionStrategy.RBAC_FIRST)

# ABAC first, fallback to RBAC
pdp = PolicyDecisionPoint(strategy=DecisionStrategy.ABAC_FIRST)

# Both must allow (most restrictive)
pdp = PolicyDecisionPoint(strategy=DecisionStrategy.BOTH_ALLOW)

# Either can allow (most permissive)
pdp = PolicyDecisionPoint(strategy=DecisionStrategy.EITHER_ALLOW)
```

### Authorization Decision

```python
decision = await pdp.evaluate(
    user_id='user123',
    resource_type='documents',
    resource_id='doc456',
    action='read',
    user_attributes={'department': 'engineering'},
    resource_attributes={'owner': 'user123'},
    environment_attributes={'vpn_connected': True}
)

if decision.allowed:
    print(f"Access granted: {decision.reason}")
    print(f"RBAC result: {decision.rbac_result}")
    print(f"ABAC result: {decision.abac_result}")
    print(f"Evaluation time: {decision.evaluation_time_ms}ms")
else:
    print(f"Access denied: {decision.reason}")
```

## Decorators

### @require_permission

Require specific permissions:

```python
from covet.security.authz import require_permission

# Single permission
@require_permission('posts:write')
async def create_post(request, title: str):
    ...

# Multiple permissions (all required)
@require_permission('posts:write', 'posts:publish', require_all=True)
async def publish_post(request, post_id: int):
    ...

# Multiple permissions (any required)
@require_permission('posts:delete', 'posts:moderate', require_all=False)
async def remove_post(request, post_id: int):
    ...
```

### @require_role

Require specific roles:

```python
from covet.security.authz import require_role

# Single role
@require_role('admin')
async def admin_dashboard(request):
    ...

# Multiple roles (any required)
@require_role('admin', 'moderator', require_all=False)
async def moderate_content(request, content_id: int):
    ...
```

### @require_policy

Use ABAC policies:

```python
from covet.security.authz import require_policy, DecisionStrategy

@require_policy('documents', 'read', strategy=DecisionStrategy.RBAC_FIRST)
async def get_document(request, doc_id: str):
    # Evaluated using RBAC first, then ABAC
    ...
```

### @require_ownership

Require resource ownership:

```python
from covet.security.authz import require_ownership

@require_ownership('document', owner_field='owner_id', allow_admin=True)
async def update_document(request, doc_id: str, owner_id: str):
    # Only document owner (or admin) can update
    ...
```

## Middleware

### AuthorizationMiddleware

Automatic route-level authorization:

```python
from covet.security.authz import AuthorizationMiddleware, DecisionStrategy

app = AuthorizationMiddleware(
    app,
    exempt_paths=['/health', '/metrics', '/docs'],
    exempt_patterns=[r'^/public/.*'],
    optional_paths=['/'],
    default_action='access',
    strategy=DecisionStrategy.RBAC_FIRST,
    enable_audit=True
)
```

The middleware:
- Extracts user from request scope (set by auth middleware)
- Determines resource type and action from path and HTTP method
- Evaluates authorization using PDP
- Returns 403 Forbidden if denied
- Injects authorization decision into request scope

### PermissionLoaderMiddleware

Load user permissions into request:

```python
from covet.security.authz import PermissionLoaderMiddleware

app = PermissionLoaderMiddleware(app)
```

Adds to request scope:
- `user['permissions']`: List of permissions
- `user['roles']`: List of role names
- `user['role_objects']`: Full role objects

## Multi-Tenant Authorization

### Tenant Isolation

Use scoped roles and permissions:

```python
# Create tenant-specific role
await rbac.create_role(
    f"tenant_admin_{tenant_id}",
    f"Tenant Admin - {tenant_name}",
    scope=PermissionScope.ORGANIZATION,
    priority=90
)

# Assign to user with scope
await rbac.assign_role_to_user(
    user_id,
    f"tenant_admin_{tenant_id}",
    scope=PermissionScope.ORGANIZATION,
    scope_id=tenant_id
)

# Check permission with scope
can_access = await rbac.check_permission(
    user_id,
    f"tenant:{tenant_id}:manage",
    scope=PermissionScope.ORGANIZATION,
    scope_id=tenant_id
)
```

### Multi-Tenant Users

Users can have different roles in different tenants:

```python
# Assign user to multiple tenants
await rbac.assign_role_to_user(
    "consultant@external.com",
    "tenant_user_acme",
    scope=PermissionScope.ORGANIZATION,
    scope_id="acme_corp"
)

await rbac.assign_role_to_user(
    "consultant@external.com",
    "tenant_admin_contoso",
    scope=PermissionScope.ORGANIZATION,
    scope_id="contoso_ltd"
)

# Get roles for specific tenant
acme_roles = await rbac.get_user_roles(
    "consultant@external.com",
    scope=PermissionScope.ORGANIZATION,
    scope_id="acme_corp"
)
```

### Hierarchical Tenants

Support parent-child tenant relationships:

```python
# Enterprise account (parent)
await rbac.create_role(
    "enterprise_admin",
    "Enterprise Admin",
    scope=PermissionScope.ORGANIZATION,
    priority=95
)

# Department roles (children)
await rbac.create_role(
    "dept_admin_engineering",
    "Engineering Admin",
    scope=PermissionScope.PROJECT,
    priority=70,
    parent_role="enterprise_admin"  # Inherits permissions
)
```

## Performance Optimization

### Caching

Authorization decisions are cached by default:

```python
# Configure cache TTL
pdp = PolicyDecisionPoint(
    enable_caching=True,
    cache_ttl=60  # Cache for 60 seconds
)

# Cache statistics
metrics = pdp.get_metrics()
print(f"Cache hit rate: {metrics['cache_stats']['hit_rate']}")
```

### Permission Registry Caching

The permission registry uses LRU caching:

```python
from covet.security.authz import PermissionRegistry

registry = PermissionRegistry(cache_size=10000)

# Check cache stats
stats = registry.get_stats()
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
```

### Database Optimization

- Use database indexes on frequently queried fields
- Enable connection pooling
- Batch permission checks when possible

```python
# Batch permission checks
permissions_to_check = ['posts:read', 'posts:write', 'posts:delete']
has_all = await rbac.check_all_permissions(user_id, permissions_to_check)
```

### Performance Targets

- Permission check (cached): <2ms
- Permission check (uncached): <10ms
- Policy evaluation: <10ms
- Support 100,000+ decisions/sec (cached)

## Security Best Practices

### 1. Principle of Least Privilege

Grant minimum necessary permissions:

```python
# Good: Specific permissions
await rbac.assign_permission_to_role('editor', 'posts:write')

# Bad: Overly broad permissions
await rbac.assign_permission_to_role('editor', '*')  # Too permissive!
```

### 2. Secure Defaults (Deny by Default)

Always deny unless explicitly allowed:

```python
# ABAC denies by default if no policy matches
# RBAC denies if user doesn't have permission

# Explicit deny for sensitive resources
await abac.create_policy(
    name="deny-classified-default",
    effect="deny",
    resource={"classification": "classified"},
    action=["*"],
    priority=100  # High priority
)
```

### 3. Audit Everything

Enable comprehensive audit logging:

```python
rbac = RBACManager(enable_audit=True)
abac = ABACManager(enable_audit=True)

# Query audit logs
from covet.security.authz.models import PermissionAuditLog

recent_denials = await PermissionAuditLog.objects.filter(
    decision='deny',
    created_at__gte=one_hour_ago
).all()
```

### 4. Regular Permission Reviews

Periodically review and revoke unused permissions:

```python
# Get all user roles
roles = await rbac.get_user_roles(user_id)

# Revoke expired or unnecessary roles
for role in roles:
    if should_revoke(role):
        await rbac.revoke_role_from_user(user_id, role.name)
```

### 5. Separation of Duties

Prevent conflicts of interest:

```python
# Don't allow users to approve their own requests
policy = (PolicyBuilder("no-self-approval")
    .deny()
    .when_subject(user_id="${resource.created_by}")
    .when_resource(type="approval_request")
    .for_actions(["approve"])
    .with_priority(95)
    .build())
```

### 6. Input Validation

Always validate user input in authorization checks:

```python
import re

def is_valid_permission(perm: str) -> bool:
    """Validate permission format."""
    return bool(re.match(r'^[a-z_]+:[a-z_]+(\:[a-z_]+)?$', perm))

# Use before checking
if is_valid_permission(permission):
    has_perm = await rbac.check_permission(user_id, permission)
```

## Production Deployment

### Database Setup

1. **Create tables** using migrations:

```python
# In your migration file
from covet.security.authz.models import (
    Permission,
    Role,
    RolePermission,
    UserRole,
    Policy,
    PermissionAuditLog,
)

# Tables will be created automatically by ORM
```

2. **Create indexes** for performance:

```sql
-- Index on user_id for fast user permission lookup
CREATE INDEX idx_user_roles_user_id ON authz_user_roles(user_id, is_active);

-- Index on role_id for fast role permission lookup
CREATE INDEX idx_role_permissions_role_id ON authz_role_permissions(role_id);

-- Index on audit logs for queries
CREATE INDEX idx_audit_user_time ON authz_audit_logs(user_id, created_at);
CREATE INDEX idx_audit_decision ON authz_audit_logs(decision, created_at);
```

### Configuration

```python
from covet.security.authz import (
    RBACManager,
    ABACManager,
    PolicyDecisionPoint,
    DecisionStrategy,
)

# Production configuration
rbac = RBACManager(
    enable_audit=True,
    cache_ttl=300  # 5 minutes
)

abac = ABACManager(
    enable_audit=True
)

pdp = PolicyDecisionPoint(
    rbac_manager=rbac,
    abac_manager=abac,
    strategy=DecisionStrategy.RBAC_FIRST,
    enable_caching=True,
    cache_ttl=60  # 1 minute
)
```

### Monitoring

Set up Prometheus metrics:

```python
from prometheus_client import Counter, Histogram

authz_decisions = Counter(
    'authz_decisions_total',
    'Total authorization decisions',
    ['result']
)

authz_duration = Histogram(
    'authz_decision_duration_seconds',
    'Authorization decision duration'
)

# In your authorization code
with authz_duration.time():
    decision = await pdp.evaluate(...)
    authz_decisions.labels(result='allow' if decision.allowed else 'deny').inc()
```

### High Availability

1. **Database replication** for read scalability
2. **Redis/Memcached** for distributed caching
3. **Load balancing** across multiple instances
4. **Connection pooling** for database connections

```python
# Use Redis for distributed cache (production)
import redis
from covet.database.cache import RedisCache

redis_client = redis.Redis(host='redis', port=6379)
cache = RedisCache(redis_client, ttl=300)
```

### Backup and Recovery

1. Regular database backups
2. Audit log archival
3. Permission configuration backup

```python
# Export roles and permissions
async def backup_authz_config():
    roles = await Role.objects.all()
    policies = await Policy.objects.all()

    backup = {
        'roles': [role.to_dict() for role in roles],
        'policies': [policy.to_dict() for policy in policies],
        'timestamp': datetime.utcnow().isoformat()
    }

    with open(f'authz_backup_{datetime.now().date()}.json', 'w') as f:
        json.dump(backup, f, indent=2)
```

---

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/covetpy/covetpy
- Documentation: https://docs.covetpy.dev/authorization
- Community: https://discord.gg/covetpy

## License

MIT License - see LICENSE file for details.
