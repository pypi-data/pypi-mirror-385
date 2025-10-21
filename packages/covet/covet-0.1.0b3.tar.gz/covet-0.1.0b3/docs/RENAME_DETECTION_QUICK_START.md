# Column Rename Detection - Quick Start Guide

## What is This?

A system that **prevents data loss** when you rename columns in your database models by intelligently detecting renames instead of generating destructive DROP + ADD operations.

---

## The Problem

```python
# You rename a column in your model
class User(Model):
    # name = StringField()        # Old
    username = StringField()      # New

# Old system generates:
DROP COLUMN name;              # ⚠️ DATA LOST!
ADD COLUMN username;           # Empty column

# New system generates:
RENAME COLUMN name TO username;  # ✅ Data preserved!
```

---

## Quick Start (3 steps)

### 1. Enable Rename Detection (Default: Enabled)

```python
from src.covet.database.migrations.diff_engine import DiffEngine

# Basic usage (rename detection is ON by default)
diff_engine = DiffEngine()

# Explicit configuration
diff_engine = DiffEngine(
    detect_renames=True,              # Enable detection
    rename_similarity_threshold=0.80  # 80% similarity required (default)
)
```

### 2. Run Your Migration

```python
operations = diff_engine.compare_schemas(model_schemas, db_schemas)

# Operations will contain RENAME_COLUMN instead of DROP + ADD
for op in operations:
    print(f"{op.operation_type}: {op.table_name}")
```

### 3. Generate SQL

```python
from src.covet.database.migrations.generator import MigrationGenerator

generator = MigrationGenerator(dialect='postgresql')
migration = generator.generate_migration(
    operations=operations,
    migration_name='0001_rename_columns',
    app_name='myapp'
)

# SQL will use RENAME syntax (data-preserving)
# PostgreSQL: ALTER TABLE users RENAME COLUMN name TO username;
# MySQL:      ALTER TABLE users CHANGE name username VARCHAR(100);
# SQLite:     ALTER TABLE users RENAME COLUMN name TO username;
```

---

## Configuration Presets

### Conservative (Production)
```python
from src.covet.database.migrations.config import get_conservative_config

config = get_conservative_config()
# - 90% similarity threshold
# - Requires exact type match
# - Maximum safety, fewer detections
```

### Balanced (Default)
```python
from src.covet.database.migrations.config import get_balanced_config

config = get_balanced_config()
# - 80% similarity threshold
# - Flexible type matching
# - Good for most cases
```

### Aggressive (Development)
```python
from src.covet.database.migrations.config import get_aggressive_config

config = get_aggressive_config()
# - 70% similarity threshold
# - Maximum detection
# - More false positives possible
```

---

## Common Scenarios

### Scenario 1: Simple Rename
```python
# name → username
# Similarity: 57%
# Detected: ✅ YES (with default 80%? No, need 50%)

diff_engine = DiffEngine(rename_similarity_threshold=0.50)
```

### Scenario 2: Adding Prefix/Suffix
```python
# email → email_address
# Similarity: 38%
# Detected: ❌ NO (below 80% threshold)

# Solution: Lower threshold or manual override
diff_engine = DiffEngine(rename_similarity_threshold=0.35)
# OR
diff_engine.add_manual_rename('users', 'email', 'email_address')
```

### Scenario 3: Abbreviation to Full Word
```python
# fname → first_name
# Similarity: 60%
# Detected: ✅ YES (with 60% threshold)

diff_engine = DiffEngine(rename_similarity_threshold=0.60)
```

### Scenario 4: Low Similarity (Manual Override)
```python
# desc → description
# Similarity: 33%
# Detected: ❌ NO (too low)

# Solution: Manual specification
diff_engine = DiffEngine()
diff_engine.add_manual_rename('products', 'desc', 'description')
```

---

## Environment Variables

```bash
# Enable/disable detection
export COVET_DETECT_RENAMES=true

# Set similarity threshold (0.0 to 1.0)
export COVET_RENAME_THRESHOLD=0.80

# Require exact type match
export COVET_RENAME_REQUIRE_TYPE_MATCH=false

# Maximum length difference ratio
export COVET_RENAME_MAX_LENGTH_DIFF=0.5
```

---

## How to Disable

```python
# If you want the old behavior (not recommended)
diff_engine = DiffEngine(detect_renames=False)

# This will generate DROP + ADD (data loss!)
```

---

## Similarity Examples

| Old Name | New Name | Similarity | Default Threshold | Detected? |
|----------|----------|------------|-------------------|-----------|
| name | username | 57% | 80% | ❌ No (need 50%) |
| email | email_address | 38% | 80% | ❌ No (need 35%) |
| fname | first_name | 60% | 80% | ❌ No (need 60%) |
| status | state | 33% | 80% | ❌ No (manual) |
| id | user_id | 29% | 80% | ❌ No (manual) |
| created | created_at | 75% | 80% | ❌ No (need 70%) |

**Recommendation**: Use default 80% threshold with manual overrides for edge cases.

---

## Troubleshooting

### Problem: Rename not detected

**Solution 1**: Lower threshold
```python
diff_engine = DiffEngine(rename_similarity_threshold=0.60)
```

**Solution 2**: Manual override
```python
diff_engine.add_manual_rename('table', 'old_name', 'new_name')
```

### Problem: False positive (unrelated columns detected as rename)

**Solution**: Increase threshold
```python
diff_engine = DiffEngine(rename_similarity_threshold=0.90)
```

### Problem: Type mismatch (INTEGER → VARCHAR)

**Solution**: This is intentional - different types should not be renamed
```python
# If you really want to force it (not recommended):
diff_engine.add_manual_rename('table', 'old_name', 'new_name')
```

---

## Best Practices

### ✅ DO:
- Use default settings for most cases
- Use manual overrides for low-similarity renames
- Test migrations in development first
- Review generated SQL before applying

### ❌ DON'T:
- Set threshold too low (<50%) - more false positives
- Disable rename detection unless necessary
- Ignore type compatibility warnings
- Skip testing on production data copies

---

## Testing

Run the test suite:
```bash
pytest tests/database/migrations/test_rename_detection.py -v
```

Expected: 29 tests pass ✅

---

## Getting Help

### Documentation:
- Full report: `SPRINT_2_RENAME_DETECTION_COMPLETE.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md`
- Code: `src/covet/database/migrations/rename_detection.py`

### Support:
- Check test suite for examples
- Review configuration options
- Consult documentation comments in code

---

## Summary

**What It Does**: Detects column renames to prevent data loss

**How It Works**: Levenshtein distance + type compatibility + confidence scoring

**Default Behavior**: Enabled with 80% threshold

**When to Use**: Always (unless you specifically need old behavior)

**Configuration**: Environment variables or code

**Databases**: PostgreSQL, MySQL, SQLite

**Status**: Production Ready ✅

---

**Quick Start Complete!**

For detailed documentation, see: `SPRINT_2_RENAME_DETECTION_COMPLETE.md`
