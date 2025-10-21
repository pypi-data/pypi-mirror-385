# Contributing to CovetPy

Thank you for your interest in contributing to CovetPy! This document provides guidelines and instructions for contributing to this educational web framework project.

## Table of Contents

- [Project Philosophy](#project-philosophy)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)
- [Areas of Contribution](#areas-of-contribution)
- [Getting Help](#getting-help)

---

## Project Philosophy

CovetPy is an **educational framework** designed for learning web development concepts. When contributing, please keep these principles in mind:

### Core Values

1. **Educational Value First**: Code should be readable and teach concepts, not just work
2. **Honesty**: No exaggerated claims or fabricated features
3. **Clarity Over Cleverness**: Simple, understandable code over complex optimizations
4. **Real Over Mock**: Real implementations over mock/dummy data
5. **Quality Over Speed**: Well-tested, documented code over quick implementations

### Not a Production Framework

CovetPy is **NOT** trying to replace Django, FastAPI, or Flask for production use. It's a learning tool. Contributions should prioritize:
- Code clarity and documentation
- Educational examples
- Learning resources
- Understanding over performance

---

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

#### 1. Documentation Improvements
- Fix typos and grammatical errors
- Improve existing documentation clarity
- Add missing documentation
- Create tutorials and guides
- Add code examples
- Translate documentation

#### 2. Bug Fixes
- Fix identified bugs
- Improve error messages
- Fix edge cases
- Improve error handling

#### 3. Code Quality Improvements
- Add type hints
- Improve code comments
- Refactor complex code
- Remove code duplication
- Improve naming

#### 4. Testing
- Add missing tests
- Improve test coverage
- Fix failing tests
- Add integration tests
- Add performance tests

#### 5. Features
- Complete incomplete features (ORM, Query Builder, Migrations)
- Improve existing features
- Add requested features (see Issues)

**Note**: For new features, please open an issue first to discuss

#### 6. Examples and Tutorials
- Create example applications
- Write step-by-step tutorials
- Add educational code samples
- Create video tutorials

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- pip
- (Optional) PostgreSQL, MySQL, Redis for full testing

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/covetpy.git
cd covetpy

# Add upstream remote
git remote add upstream https://github.com/covetpy/covetpy.git
```

### 2. Install in Development Mode

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Or install all dependencies
pip install -e ".[full,dev]"
```

### 3. Verify Installation

```bash
# Run tests
pytest tests/ -v

# Run code quality checks
black src/ tests/ --check
ruff check src/ tests/
mypy src/

# Verify imports
python -c "import covet; print(covet.__version__)"
```

### 4. Set Up Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

---

## Coding Standards

### Python Style

We follow **PEP 8** with some modifications:

- **Line Length**: 88 characters (Black default)
- **Formatter**: Black (mandatory)
- **Linter**: Ruff (mandatory)
- **Type Checker**: mypy strict mode

### Code Formatting

**Before committing**, always run:

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type check
mypy src/
```

### Naming Conventions

```python
# Classes: PascalCase
class UserManager:
    pass

# Functions and methods: snake_case
def get_user_by_id(user_id: int):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_CONNECTIONS = 100

# Private methods: _leading_underscore
def _internal_method():
    pass

# Module names: lowercase
# database_adapter.py (not Database_Adapter.py or databaseAdapter.py)
```

### Type Hints

**All code must have type hints**:

```python
# Good
def process_data(data: dict[str, Any]) -> list[str]:
    return list(data.keys())

# Bad (missing type hints)
def process_data(data):
    return list(data.keys())
```

### Documentation

**All public APIs must have docstrings**:

```python
def validate_email(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid")
        False
    """
    # Implementation
    pass
```

### Comments

**Write educational comments**:

```python
# Good - explains WHY
# Use constant-time comparison to prevent timing attacks
if secrets.compare_digest(hash1, hash2):
    pass

# Bad - explains WHAT (obvious from code)
# Compare two hashes
if secrets.compare_digest(hash1, hash2):
    pass
```

### Error Handling

**Use specific exceptions**, never bare `except`:

```python
# Good
try:
    result = risky_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Invalid input: {e}")
    raise

# Bad
try:
    result = risky_operation()
except:
    pass
```

---

## Testing Requirements

### Test Coverage

- **Minimum coverage**: 80% for new code
- **Target coverage**: 85%+ overall
- **Security code**: 95%+ coverage

### Testing Tools

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src/covet --cov-report=html tests/

# Run specific test file
pytest tests/unit/test_security.py -v

# Run tests matching pattern
pytest -k "test_sql_injection"
```

### Writing Tests

**Follow the arrange-act-assert pattern**:

```python
def test_user_creation():
    # Arrange
    db = Database(":memory:")
    user_data = {"name": "Alice", "email": "alice@example.com"}

    # Act
    user = db.create_user(**user_data)

    # Assert
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.id is not None
```

### Test Categories

#### Unit Tests
- Test single functions/classes in isolation
- Use mocks sparingly
- Fast execution (<1s per test)

```python
def test_hash_password():
    password = "secure_password"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
```

#### Integration Tests
- Test multiple components together
- Use real databases (not mocks)
- Test actual interactions

```python
async def test_database_transaction(real_db):
    async with real_db.transaction():
        user = await real_db.create_user(name="Alice")
        assert user.id is not None
```

#### Security Tests
- Test all security features
- Test attack scenarios
- Test edge cases

```python
def test_sql_injection_prevention():
    malicious_input = "1 OR 1=1; DROP TABLE users--"
    with pytest.raises(ValidationError):
        db.execute_query(f"SELECT * FROM users WHERE id={malicious_input}")
```

### Test Requirements for Pull Requests

**Your PR must**:
- [ ] Include tests for all new code
- [ ] Pass all existing tests
- [ ] Achieve 80%+ coverage for new code
- [ ] Include security tests for security-related changes
- [ ] Include integration tests for database changes
- [ ] Not decrease overall test coverage

---

## Pull Request Process

### Before Creating a PR

1. **Check existing issues and PRs** - Avoid duplicate work
2. **Discuss major changes** - Open an issue first
3. **Update documentation** - Keep docs in sync with code
4. **Write tests** - Comprehensive test coverage
5. **Run all checks** - Tests, linting, type checking

### Creating a PR

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # Or for bugfixes
   git checkout -b fix/bug-description
   ```

2. **Make your changes**:
   ```bash
   # Edit files
   # Add tests
   # Update documentation
   ```

3. **Run checks locally**:
   ```bash
   # Format code
   black src/ tests/

   # Check linting
   ruff check src/ tests/

   # Type check
   mypy src/

   # Run tests
   pytest tests/ --cov=src/covet
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: Brief description

   - Detailed change 1
   - Detailed change 2
   - Fixes #123"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request on GitHub**:
   - Fill out the PR template completely
   - Reference related issues
   - Add screenshots for UI changes
   - Request review from maintainers

### PR Title Format

```
<type>: <brief description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- test: Adding or fixing tests
- refactor: Code refactoring
- perf: Performance improvement
- style: Code style changes (formatting, etc.)
- chore: Maintenance tasks

Examples:
- feat: Add JWT refresh token rotation
- fix: Prevent SQL injection in query builder
- docs: Add tutorial for database migrations
- test: Add security tests for CSRF protection
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Code quality improvement
- [ ] Test improvement

## Related Issues
Fixes #123
Related to #456

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] All tests passing
- [ ] Coverage maintained/increased

## Documentation
- [ ] Updated docstrings
- [ ] Updated README if needed
- [ ] Updated CHANGELOG if needed
- [ ] Added examples if needed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### PR Review Process

1. **Automated checks run**: CI/CD pipeline
2. **Code review**: At least one maintainer review
3. **Feedback addressed**: Make requested changes
4. **Approval**: Maintainer approval required
5. **Merge**: Squash and merge to main

### After PR is Merged

```bash
# Update your local repository
git checkout main
git pull upstream main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## Community Guidelines

### Code of Conduct

Please read and follow our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

### Communication

- **Be respectful and professional**
- **Assume positive intent**
- **Provide constructive feedback**
- **Help others learn** (remember, this is an educational project)
- **No discrimination or harassment**

### Review Guidelines

When reviewing PRs:

#### For Contributors
- **Be patient**: Reviews take time
- **Be receptive**: Reviewers are trying to help
- **Ask questions**: If feedback is unclear
- **Learn**: Reviews are learning opportunities

#### For Reviewers
- **Be kind**: Contributors are volunteering time
- **Be constructive**: Suggest improvements, don't just criticize
- **Be educational**: Explain WHY something should change
- **Be thorough**: Check code, tests, and documentation
- **Be timely**: Respond within a week if possible

---

## Areas of Contribution

### High Priority (Help Needed!)

#### 1. Complete ORM Implementation
**Status**: Field validation complete, Model class needs work

**What's Needed**:
- Model class CRUD operations
- Relationship management (ForeignKey, ManyToMany)
- Query generation from models
- Lazy loading and eager loading
- N+1 query prevention

**Skills**: Python, SQLAlchemy knowledge, testing

#### 2. Implement Query Builder
**Status**: Design complete, needs implementation

**What's Needed**:
- Django-style query API
- Q objects for complex queries
- F expressions
- Aggregation functions
- Subquery support

**Skills**: Python, Django/SQLAlchemy knowledge

#### 3. Implement Migration System
**Status**: Design complete, needs implementation

**What's Needed**:
- Schema change detection
- Migration generation
- Migration execution
- Rollback support

**Skills**: Python, database knowledge, Alembic knowledge

#### 4. Increase Test Coverage
**Current**: 10%
**Target**: 85%+

**What's Needed**:
- Fix 768 broken tests (return booleans)
- Write 5,000+ meaningful tests
- Integration tests with real backends
- End-to-end tests

**Skills**: Python, pytest, testing best practices

#### 5. Improve Documentation
**What's Needed**:
- API reference documentation
- Tutorial series (8+ tutorials)
- Example applications (5+ examples)
- Video tutorials
- Deployment guides

**Skills**: Writing, teaching, Python

#### 6. Performance Benchmarking
**What's Needed**:
- Comprehensive HTTP benchmarks
- Comparison with other frameworks
- Performance profiling
- Optimization recommendations

**Skills**: Python, performance testing, profiling

### Medium Priority

#### 7. Complete Print Statement Cleanup
**Status**: 178 print statements remain

**What's Needed**:
- Replace with proper logging
- Use appropriate log levels
- Add structured logging

**Skills**: Python, logging

#### 8. Fix Rust Extensions
**Status**: Code exists but not functional

**What's Needed**:
- Fix PyO3 bindings
- Implement JSON operations
- Implement JWT operations
- Add tests

**Skills**: Rust, Python, PyO3

### Areas Always Welcome

- **Documentation improvements**: Always appreciated
- **Bug fixes**: Check the issue tracker
- **Test improvements**: More tests always welcome
- **Code quality**: Refactoring, type hints, comments
- **Examples**: More educational examples

---

## Getting Help

### Questions?

- **GitHub Discussions**: For general questions
- **GitHub Issues**: For bugs and feature requests
- **Documentation**: Check existing docs first

### Resources

- [README.md](README.md): Project overview
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): Framework architecture
- [Sprint Reports](docs/): Detailed implementation reports
- [Test Patterns](tests/README.md): Testing guidelines

### Mentorship

We're happy to help new contributors:
- Comment on issues you're interested in
- Ask questions on GitHub Discussions
- Request code review guidance
- Pair programming sessions (if available)

---

## Recognition

### Contributors

All contributors will be:
- Listed in release notes
- Mentioned in CHANGELOG.md
- Credited in documentation they create
- Recognized in the README

### Significant Contributions

Major contributors may be invited to:
- Join the core team
- Become code reviewers
- Help with project governance

---

## License

By contributing to CovetPy, you agree that your contributions will be licensed under the MIT License, the same license as the project.

---

## Thank You!

Thank you for considering contributing to CovetPy! Whether you're fixing a typo, adding a test, or implementing a major feature, your contributions help make this educational framework better for everyone.

**Remember**: This is an educational project. The goal is to help people learn, so prioritize clarity and documentation over cleverness and optimization.

**Happy Contributing!**

The CovetPy Team

---

**Last Updated**: 2025-10-10
**Version**: 1.0.0

**Questions?** Open an issue or discussion on GitHub!
