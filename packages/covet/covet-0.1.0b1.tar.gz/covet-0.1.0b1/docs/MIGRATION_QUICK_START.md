# CovetPy Migrations - Quick Start Guide

## Installation

```bash
cd /path/to/NeutrinoPy
pip install -e .
```

## 5-Minute Setup

### 1. Configure Database

Create `covet.config.py`:

```python
DATABASE = {
    "engine": "sqlite",
    "database": "myapp.db",
}
```

### 2. Define Models

Create `models.py`:

```python
from covet.orm.models import Model
from covet.orm.fields import AutoField, CharField

class User(Model):
    id = AutoField()
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=100)

    class Meta:
        table_name = "users"
```

### 3. Generate Migration

```bash
python covet-cli.py makemigrations
```

### 4. Apply Migration

```bash
python covet-cli.py migrate
```

### 5. Verify

```bash
python covet-cli.py showmigrations
```

## Common Commands

```bash
# Generate migrations from model changes
python covet-cli.py makemigrations

# Generate with custom name
python covet-cli.py makemigrations --name create_users

# Apply all pending migrations
python covet-cli.py migrate

# Apply without confirmation
python covet-cli.py migrate --yes

# Show migration status
python covet-cli.py showmigrations

# Rollback last migration
python covet-cli.py rollback

# Rollback without confirmation
python covet-cli.py rollback --yes
```

## Programmatic Usage

```python
from covet.orm.connection import ConnectionConfig, register_database
from covet.orm.migrations import Migration, MigrationRunner
from covet.orm.fields import AutoField, CharField

# Setup
config = ConnectionConfig(engine="sqlite", database="app.db")
register_database("default", config)

# Create migration
migration = Migration("add_users", "default")
migration.create_table("users", {
    "id": AutoField(),
    "username": CharField(max_length=50),
})

# Apply
runner = MigrationRunner("default")
runner.apply_migration(migration)
```

## Database Configuration Examples

### SQLite
```python
DATABASE = {
    "engine": "sqlite",
    "database": "myapp.db",
}
```

### PostgreSQL
```python
DATABASE = {
    "engine": "postgresql",
    "database": "myapp",
    "host": "localhost",
    "port": 5432,
    "username": "postgres",
    "password": "secret",
}
```

### MySQL
```python
DATABASE = {
    "engine": "mysql",
    "database": "myapp",
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "secret",
}
```

## Migration Operations Cheat Sheet

```python
# Create table
migration.create_table("users", {
    "id": AutoField(),
    "name": CharField(max_length=100),
})

# Drop table
migration.drop_table("users")

# Add column
migration.add_column("users", "age", IntegerField(null=True))

# Drop column
migration.drop_column("users", "age")

# Rename table
migration.rename_table("users", "accounts")

# Rename column
migration.rename_column("users", "name", "full_name")

# Create index
migration.create_index("idx_username", "users", ["username"], unique=True)

# Drop index
migration.drop_index("idx_username", "users")

# Add foreign key
migration.add_foreign_key(
    "posts", "user_id", "users", "id",
    on_delete="CASCADE"
)

# Custom SQL
migration.run_sql(
    "ALTER TABLE users ADD COLUMN custom TEXT",
    "ALTER TABLE users DROP COLUMN custom"
)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No models found | Import models, ensure they inherit from Model |
| Database error | Check covet.config.py, verify credentials |
| Migration failed | Run `rollback`, fix issue, try again |
| File not found | Check migrations directory exists |

## Project Structure

```
myproject/
├── covet.config.py      # Database config
├── models.py            # Model definitions
├── migrations/          # Migration files
│   ├── 20240101_120000_initial.py
│   └── 20240101_130000_add_users.py
└── covet-cli.py        # CLI tool (copy from NeutrinoPy)
```

## Next Steps

1. Read full documentation: `examples/migrations/README.md`
2. Review examples: `examples/migrations/models.py`
3. Run tests: `python examples/migrations/test_migrations.py`
4. Check implementation: `docs/MIGRATION_SYSTEM_IMPLEMENTATION.md`

## Support

- Documentation: `/docs/MIGRATION_SYSTEM_IMPLEMENTATION.md`
- Examples: `/examples/migrations/`
- Issues: Report via GitHub

---

**Happy Migrating!** 🚀
