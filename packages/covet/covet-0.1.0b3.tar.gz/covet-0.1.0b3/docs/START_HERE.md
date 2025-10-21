# Start Here - CovetPy Documentation Guide

**Welcome to CovetPy!** This guide will help you navigate the documentation and get started quickly.

## Important: Read This First

CovetPy is an **educational framework** in beta. The documentation has been recently updated to fix critical mismatches between docs and implementation. **Always use the verified working examples**.

---

## Quick Navigation

### For New Users

1. **[Working Examples](examples/)** ⭐ START HERE
   - All examples tested and verified to work
   - Copy-paste ready code
   - Best way to learn the framework

2. **[Common Mistakes Guide](troubleshooting/COMMON_MISTAKES.md)** ⚠️ READ THIS
   - Avoid common pitfalls
   - Shows wrong vs. correct APIs
   - Saves you hours of debugging

3. **[README.md](../README.md)**
   - Project overview
   - Feature status
   - Honest limitations

---

## Documentation Quick Start

### Step 1: Run a Working Example (5 minutes)

```bash
cd /path/to/NeutrinoPy

# Run hello world
python docs/examples/01_hello_world.py

# Run database example
python docs/examples/02_database_example.py

# Run JWT example
python docs/examples/03_jwt_auth_example.py
```

### Step 2: Read Common Mistakes (10 minutes)

Open [docs/troubleshooting/COMMON_MISTAKES.md](troubleshooting/COMMON_MISTAKES.md)

Key things to know:
- Use `CovetPy`, not `Application`
- Use `JWTAlgorithm.HS256` enum, not string `'HS256'`
- Database uses adapter pattern: `DatabaseManager(SQLiteAdapter(...))`
- JWT parameter is `extra_claims`, not `custom_claims`

### Step 3: Build Something (30 minutes)

Use [docs/examples/05_full_integration_example.py](examples/05_full_integration_example.py) as a template.

It shows a complete working application with:
- SQLite database
- REST API endpoints
- JWT authentication
- User registration/login

---

## Documentation Structure

### ✅ Reliable Documentation (Use These)

| Document | Purpose | Status |
|----------|---------|--------|
| [examples/](examples/) | **Working code** | ✅ TESTED |
| [troubleshooting/COMMON_MISTAKES.md](troubleshooting/COMMON_MISTAKES.md) | **Avoid pitfalls** | ✅ ACCURATE |
| [DOCUMENTATION_FIXES_SUMMARY.md](DOCUMENTATION_FIXES_SUMMARY.md) | **What was fixed** | ✅ CURRENT |
| [README.md](../README.md) | **Project overview** | ✅ UPDATED |

### ⚠️ Mixed Reliability (Use with Caution)

| Document | Purpose | Warning |
|----------|---------|---------|
| [archive/GETTING_STARTED.md](archive/GETTING_STARTED.md) | Tutorial | ⚠️ Needs updating, may have wrong APIs |
| [archive/quickstart.md](archive/quickstart.md) | Quick start | ⚠️ Some examples incorrect |
| [archive/API_REFERENCE.md](archive/API_REFERENCE.md) | API docs | ⚠️ Some APIs shown don't exist |

**Recommendation**: Prefer `docs/examples/` over archived docs until they're updated.

---

## Finding What You Need

### I want to...

#### Learn CovetPy basics
→ Start with [examples/01_hello_world.py](examples/01_hello_world.py)

#### Use the database
→ See [examples/02_database_example.py](examples/02_database_example.py)
→ Read [Common Mistakes - Database API](troubleshooting/COMMON_MISTAKES.md#2-database-api-differences)

#### Implement authentication
→ See [examples/03_jwt_auth_example.py](examples/03_jwt_auth_example.py)
→ Read [Common Mistakes - JWT Enums](troubleshooting/COMMON_MISTAKES.md#3-jwt-authentication-enums)

#### Build a REST API
→ See [examples/04_rest_api_example.py](examples/04_rest_api_example.py)

#### See a complete application
→ See [examples/05_full_integration_example.py](examples/05_full_integration_example.py)

#### Understand what was fixed
→ Read [DOCUMENTATION_FIXES_SUMMARY.md](DOCUMENTATION_FIXES_SUMMARY.md)

#### Know what works and what doesn't
→ Read [README.md - Features](../README.md#-features-honest-status)
→ Read [FEATURE_STATUS.md](../FEATURE_STATUS.md)

#### Deploy to production
→ **DON'T** - CovetPy is educational, not production-ready
→ Use FastAPI, Flask, or Django instead

---

## Common Questions

### Q: Why do the examples in archived docs not work?

**A**: The archived docs were written before the implementation stabilized. Some show idealized APIs that were never implemented. Always use `docs/examples/` which have been tested.

### Q: Which APIs are safe to use?

**A**: See `docs/examples/` for safe, tested APIs. Key working components:
- Basic HTTP/ASGI (CovetPy application)
- SQLite database operations (DatabaseManager + SQLiteAdapter)
- JWT authentication (with correct enums)
- REST API framework (with Pydantic)
- Query builder
- Basic cache

### Q: What doesn't work?

**A**: See [README.md - What's Broken](../README.md#-whats-broken-or-missing-60-of-framework):
- PostgreSQL/MySQL adapters (empty stubs)
- GraphQL engine (2% complete)
- Advanced ORM features (select_related, etc.)
- Production monitoring
- And more - read the honest assessment

### Q: Can I use this in production?

**A**: **NO**. CovetPy is educational. For production, use:
- **FastAPI** - Modern, fast, production-ready
- **Flask** - Simple, stable, battle-tested
- **Django** - Full-featured, comprehensive

### Q: How do I report a documentation issue?

**A**:
1. Check if it's in [COMMON_MISTAKES.md](troubleshooting/COMMON_MISTAKES.md)
2. Check if example in `docs/examples/` works
3. If still an issue, open a GitHub issue with:
   - What the docs say
   - What actually happens
   - Error message
   - Example code

---

## Learning Path

### Beginner (1-2 hours)

1. Read [README.md](../README.md) - Understand what CovetPy is
2. Run [examples/01_hello_world.py](examples/01_hello_world.py) - See it work
3. Run [examples/02_database_example.py](examples/02_database_example.py) - Database basics
4. Read [COMMON_MISTAKES.md](troubleshooting/COMMON_MISTAKES.md) - Avoid pitfalls

### Intermediate (2-4 hours)

5. Study [examples/03_jwt_auth_example.py](examples/03_jwt_auth_example.py) - Authentication
6. Study [examples/04_rest_api_example.py](examples/04_rest_api_example.py) - REST API
7. Build a simple CRUD API using these as templates

### Advanced (4+ hours)

8. Study [examples/05_full_integration_example.py](examples/05_full_integration_example.py) - Full stack
9. Build your own application
10. Read source code in `src/covet/` to understand internals
11. Contribute improvements or fixes

---

## Contributing to Documentation

Found a mistake? Want to improve docs?

### Quick Fixes
- Fix typos, broken links, formatting
- Update examples with better comments
- Add missing edge cases

### Major Contributions
- Write new tested examples
- Create tutorials
- Improve common mistakes guide
- Auto-generate API documentation

**Process**:
1. Test your changes (especially code examples)
2. Follow existing doc style
3. Submit pull request
4. Update DOCUMENTATION_FIXES_SUMMARY.md if major change

---

## Documentation Status

**Last Major Update**: 2025-10-12

**What's Current**:
- ✅ Working examples (all 5 tested)
- ✅ Common mistakes guide
- ✅ README.md
- ✅ Documentation fixes summary

**What Needs Updating**:
- ⏳ Archive docs (GETTING_STARTED.md, quickstart.md, etc.)
- ⏳ API reference (needs auto-generation)
- ⏳ Tutorials (need rewrite with correct APIs)
- ⏳ Deployment guides (need verification)

---

## Getting Help

### Self-Service
1. Check [examples/](examples/) - Working code
2. Check [troubleshooting/COMMON_MISTAKES.md](troubleshooting/COMMON_MISTAKES.md) - Common issues
3. Check [README.md](../README.md) - Feature status
4. Read source code - The implementation is the truth

### Community
- GitHub Issues - Bug reports
- GitHub Discussions - Questions
- Stack Overflow - Tag: `covetpy`

### Remember
CovetPy is **educational**. For production support, use established frameworks.

---

## Final Checklist

Before you start coding with CovetPy:

- [ ] Read [README.md](../README.md) - Know what you're getting into
- [ ] Run [examples/01_hello_world.py](examples/01_hello_world.py) - Verify it works
- [ ] Read [COMMON_MISTAKES.md](troubleshooting/COMMON_MISTAKES.md) - Save yourself time
- [ ] Accept this is educational, not production-ready
- [ ] Have fun learning how frameworks work internally!

---

**Happy learning!** 🎓

For questions: See [DOCUMENTATION_FIXES_SUMMARY.md](DOCUMENTATION_FIXES_SUMMARY.md)

---

**Version**: CovetPy 0.9.0-beta
**Status**: Documentation UPDATED (2025-10-12)
**Examples**: 5/5 tested and working
