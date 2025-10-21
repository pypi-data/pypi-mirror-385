# Migrating from Beta to v1.0

**Current Version:** 0.9.0-beta
**Target Version:** 1.0.0-stable (PLANNED - Not Yet Available)
**Status:** This guide describes future migration when v1.0 is released

---

## ⚠️ Important Notice

**CovetPy v1.0 does not exist yet.** This document describes the planned migration path IF the project decides to pursue production readiness.

**Current Recommendation:** Migrate to an established framework instead:
- **FastAPI** - https://fastapi.tiangolo.com/
- **Flask** - https://flask.palletsprojects.com/
- **Django** - https://www.djangoproject.com/

---

## Table of Contents

1. [Should You Wait for v1.0?](#should-you-wait-for-v10)
2. [What Will Change in v1.0](#what-will-change-in-v10)
3. [Migration Strategy](#migration-strategy)
4. [Breaking Changes](#breaking-changes)
5. [Alternative: Migrate to Established Frameworks](#alternative-migrate-to-established-frameworks)

---

## Should You Wait for v1.0?

### Decision Tree

**Are you using CovetPy in production?**
- ✅ **YES** → ⚠️ **MIGRATE IMMEDIATELY** to FastAPI/Flask/Django (see below)
  - CovetPy is NOT safe for production
  - Security vulnerabilities (SQL injection, broken auth)
  - Data loss risk (no transaction support)

**Are you using CovetPy for learning?**
- ✅ **YES** → Continue using for education
  - Core features (40%) work well for learning
  - Wait for v1.0 IF project continues
  - OR migrate to learn production frameworks

**Are you evaluating CovetPy for a future project?**
- ✅ **YES** → Use an established framework instead
  - v1.0 timeline uncertain (6-9 months minimum)
  - Competing with mature, proven frameworks
  - Higher risk, no community support yet

---

## What Will Change in v1.0

### IF the project pursues production readiness (Option A from BETA_LIMITATIONS.md):

### Phase 1: Security & Stability (Q4 2025)
**Version:** 1.0.0-alpha → 1.0.0-beta → 1.0.0

#### Security Fixes (CRITICAL)
- ✅ Fix SQL injection vulnerabilities
  - Replace f-string queries with parameterized queries
  - Add comprehensive input validation
  - **Breaking:** Query syntax may change
- ✅ Fix JWT authentication
  - Add expiration validation
  - Implement token revocation
  - Add refresh token support
  - **Breaking:** Authentication API will change
- ✅ Implement CSRF protection
  - Add CSRF middleware
  - Update form handling
  - **Breaking:** May require CSRF tokens in requests
- ✅ Add comprehensive RBAC
  - Role-based access control
  - Permission system
  - **Breaking:** New authorization API

#### Database Support
- ✅ PostgreSQL adapter (complete implementation)
  - Full async support
  - Connection pooling
  - Transaction support
  - **Breaking:** Configuration changes required
- ✅ MySQL adapter (complete implementation)
  - UTF8MB4 support
  - Connection pooling
  - **Breaking:** Configuration changes required
- ✅ Migration system
  - Schema migration support
  - Data migrations
  - Rollback support
  - **Breaking:** New migration commands

#### Testing
- ✅ 80%+ test coverage
  - All core features tested
  - Integration tests with real databases
  - Performance regression tests
  - **Breaking:** May discover bugs requiring API changes

### Phase 2: Enterprise Features (Q1 2026)
**Version:** 1.1.0

- ✅ Horizontal sharding
- ✅ Read replica support
- ✅ Advanced connection pooling
- **Breaking:** Database configuration changes

### Phase 3: Advanced Features (Q2 2026)
**Version:** 1.2.0

- ✅ Backup & recovery
- ✅ Point-in-Time Recovery (PITR)
- ✅ Monitoring integration
- **Breaking:** May require new configuration

### Phase 4: Full Feature Parity (Q3 2026)
**Version:** 2.0.0

- ✅ GraphQL engine (complete)
- ✅ REST API framework (complete)
- ✅ OpenAPI/Swagger generation
- **Breaking:** Major API changes

---

## Migration Strategy

### Step 1: Assess Your Usage

**Before migrating, determine:**

1. **What features are you using?**
   ```bash
   # Check your imports
   grep -r "from covet" your_project/
   grep -r "import covet" your_project/
   ```

2. **Are you using broken features?**
   - PostgreSQL/MySQL → ❌ Empty stubs (use SQLite or migrate)
   - JWT auth → ❌ Broken (implement custom auth)
   - GraphQL → ❌ Not implemented (use alternative)
   - Sharding → ❌ Not implemented (remove or mock)

3. **What's your data?**
   - SQLite → Can migrate to v1.0
   - PostgreSQL/MySQL → NOT CURRENTLY SUPPORTED
   - Sensitive data → ⚠️ **MIGRATE IMMEDIATELY**

### Step 2: Backup Everything

```bash
# Backup your database
sqlite3 your_database.db .dump > backup.sql

# Backup your code
git tag beta-backup-$(date +%Y%m%d)
git push --tags

# Backup your configuration
cp -r config/ config.backup/
```

### Step 3: Read the Changelog

When v1.0 is released, read:
- `CHANGELOG.md` - All changes
- `BREAKING_CHANGES.md` - Breaking changes
- `MIGRATION_GUIDE.md` - Detailed migration steps

### Step 4: Test in Staging

**DO NOT upgrade production directly.**

1. Create a staging environment
2. Install v1.0
3. Run your test suite
4. Manually test all features
5. Check for deprecation warnings
6. Fix all issues
7. Performance test
8. Security audit

### Step 5: Gradual Migration

```python
# Option A: Feature flag
if USE_V1_FEATURES:
    from covet.v1 import CovetPy
else:
    from covet import CovetPy  # Old beta

# Option B: Gradual route migration
# Migrate routes one at a time
@app.route("/new-endpoint")  # v1.0
async def new_endpoint():
    pass

@app_legacy.route("/old-endpoint")  # beta
async def old_endpoint():
    pass
```

---

## Breaking Changes

### Expected Breaking Changes (When v1.0 Releases)

#### 1. Database Configuration

**Beta (Current):**
```python
# Simple, no configuration needed
from covet.database.simple_orm import Model

class User(Model):
    name = CharField(max_length=100)
```

**v1.0 (Expected):**
```python
# Requires explicit database configuration
from covet.database import configure, Model

configure({
    'default': {
        'ENGINE': 'postgresql',
        'NAME': 'mydb',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
        'PORT': 5432,
    }
})

class User(Model):
    name = CharField(max_length=100)

    class Meta:
        database = 'default'
```

#### 2. Authentication API

**Beta (Current - BROKEN):**
```python
from covet.api.rest.auth import authenticate_user

# This is broken, don't use it
user = authenticate_user(token, secret)
```

**v1.0 (Expected):**
```python
from covet.security.auth import JWTAuthenticator

auth = JWTAuthenticator(
    secret_key=settings.SECRET_KEY,
    algorithm='RS256',  # More secure
    expiration=3600,    # 1 hour
)

# Validate token
user = await auth.authenticate(token)

# Refresh token
new_token = await auth.refresh(refresh_token)
```

#### 3. Query API

**Beta (Current):**
```python
# F-string queries (VULNERABLE)
users = User.objects.raw(f"SELECT * FROM users WHERE id = {user_id}")
```

**v1.0 (Expected):**
```python
# Parameterized queries only
users = User.objects.raw(
    "SELECT * FROM users WHERE id = %s",
    [user_id]
)

# Or use ORM
user = await User.objects.get(id=user_id)
```

#### 4. Middleware API

**Beta (Current):**
```python
from covet.middleware import RateLimitMiddleware

# Empty stub, doesn't work
app.add_middleware(RateLimitMiddleware)
```

**v1.0 (Expected):**
```python
from covet.middleware import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    rate="100/minute",
    key_func=lambda request: request.client.host,
    backend="redis://localhost:6379/0"
)
```

#### 5. Schema Validation

**Beta (Current):**
```python
# No validation
@app.post("/users")
async def create_user(request):
    data = await request.json()
    # No validation, security risk
    user = await User.objects.create(**data)
    return {"id": user.id}
```

**v1.0 (Expected):**
```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(ge=0, le=150)

@app.post("/users")
async def create_user(request: Request, data: UserCreate):
    # Validated automatically
    user = await User.objects.create(**data.dict())
    return {"id": user.id}
```

---

## Alternative: Migrate to Established Frameworks

### Recommended: Migrate to FastAPI

**Why FastAPI?**
- Similar async/await patterns
- Modern Python (3.9+)
- Excellent type hint support
- Auto-generated OpenAPI docs
- Production-ready
- Large community
- Excellent performance

**Migration effort:** 2-4 weeks

#### Step-by-Step: CovetPy to FastAPI

##### 1. Install FastAPI

```bash
pip install fastapi uvicorn[standard] sqlalchemy[asyncio] alembic
```

##### 2. Migrate Routes

**CovetPy (Beta):**
```python
from covet import CovetPy

app = CovetPy()

@app.route("/users/{user_id}", methods=["GET"])
async def get_user(request, user_id: int):
    return {"user_id": user_id}
```

**FastAPI:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

**Changes:**
- `CovetPy()` → `FastAPI()`
- `@app.route()` → `@app.get()` / `@app.post()` etc.
- No `request` parameter needed for simple cases
- Path parameters work similarly

##### 3. Migrate Database (ORM)

**CovetPy (Beta):**
```python
from covet.database.simple_orm import Model, CharField

class User(Model):
    name = CharField(max_length=100)
    email = CharField(max_length=255)

# Usage
user = await User.objects.create(name="Alice", email="alice@example.com")
users = await User.objects.filter(age__gte=18).all()
```

**FastAPI + SQLAlchemy:**
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255))

# Setup
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
async_session = sessionmaker(engine, class_=AsyncSession)

# Usage
async with async_session() as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    await session.commit()

    # Query
    from sqlalchemy import select
    result = await session.execute(select(User).where(User.age >= 18))
    users = result.scalars().all()
```

**Changes:**
- More verbose but more powerful
- Explicit session management
- Full transaction support
- Production-ready
- Multi-database support (PostgreSQL, MySQL, SQLite)

##### 4. Migrate Authentication

**CovetPy (Beta - BROKEN):**
```python
from covet.api.rest.auth import authenticate_user

# Don't use this - it's broken
```

**FastAPI + python-jose:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)

    # Get user from database
    user = await get_user_by_username(username)
    return user

# Protected route
@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

##### 5. Complete Migration Checklist

- [ ] Install FastAPI and dependencies
- [ ] Migrate all routes (change decorators)
- [ ] Migrate database models (to SQLAlchemy)
- [ ] Migrate authentication (to OAuth2/JWT)
- [ ] Add request validation (Pydantic models)
- [ ] Migrate middleware
- [ ] Update tests
- [ ] Add OpenAPI documentation
- [ ] Performance test
- [ ] Security audit
- [ ] Deploy to staging
- [ ] Deploy to production

---

### Alternative: Flask

**If you prefer simplicity over performance:**

```bash
pip install flask sqlalchemy
```

**Migration effort:** 3-5 weeks (sync vs async difference)

---

### Alternative: Django

**If you want a full framework:**

```bash
pip install django
```

**Migration effort:** 4-8 weeks (different architecture)

---

## Timeline & Expectations

### If v1.0 is Released

**Estimated Timeline:**
- **Q4 2025:** v1.0.0-alpha (testing)
- **Q1 2026:** v1.0.0-beta (feature complete)
- **Q2 2026:** v1.0.0 (stable release)

**What to expect:**
- Breaking changes to ALL APIs
- Database schema changes
- Configuration changes
- Migration scripts provided
- Comprehensive documentation
- Migration support

### If v1.0 is NOT Released

**Alternative paths:**
1. Project pivots to educational focus (most likely)
2. Project archived
3. Community fork

**Recommendation:** Don't wait. Migrate to established framework now.

---

## Getting Help

### When v1.0 is Released

- Read official migration guide
- Check GitHub Discussions
- Review example migrations
- Test in staging first

### Before v1.0

- Migrate to FastAPI/Flask/Django
- Use CovetPy for learning only
- Don't use in production

---

## Conclusion

**Current Recommendation:** **Do NOT wait for v1.0**

Instead:
1. **If in production:** Migrate to FastAPI immediately (2-4 weeks)
2. **If learning:** Continue with CovetPy or migrate to learn production framework
3. **If evaluating:** Choose FastAPI, Flask, or Django

When v1.0 is released:
1. Read the official migration guide
2. Test thoroughly in staging
3. Expect breaking changes
4. Budget 2-4 weeks for migration

---

**Document Status:** PLANNED (v1.0 doesn't exist yet)
**Last Updated:** October 11, 2025
**Next Update:** When v1.0 release date is announced
