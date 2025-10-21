# CovetPy Migration System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CovetPy Migration System                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│     CLI      │────────▶│  Migration   │────────▶│   Database   │
│   Commands   │         │    Engine    │         │   (Pg/My/Sq) │
└──────────────┘         └──────────────┘         └──────────────┘
      │                         │                         │
      │                         │                         │
      ▼                         ▼                         ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Migration   │         │    Schema    │         │  Migration   │
│    Files     │         │ Introspector │         │   Tracker    │
└──────────────┘         └──────────────┘         └──────────────┘
```

## Component Architecture

### 1. CLI Layer
```
┌─────────────────────────────────────────┐
│          CLI Commands                    │
├─────────────────────────────────────────┤
│  - makemigrations                        │
│  - migrate                               │
│  - rollback                              │
│  - showmigrations                        │
├─────────────────────────────────────────┤
│  Responsibilities:                       │
│  • Parse command-line arguments          │
│  • Load configuration                    │
│  • Discover models                       │
│  • Coordinate operations                 │
│  • Display user feedback                 │
└─────────────────────────────────────────┘
```

### 2. Core Engine
```
┌─────────────────────────────────────────┐
│        Migration Engine                  │
├─────────────────────────────────────────┤
│  Components:                             │
│  ┌─────────────────────────────────┐    │
│  │  SchemaIntrospector             │    │
│  │  • Read database schema         │    │
│  │  • Extract tables/columns       │    │
│  │  • Get indexes/constraints      │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  MigrationEngine                │    │
│  │  • Compare models vs DB         │    │
│  │  • Detect changes               │    │
│  │  • Generate operations          │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  MigrationRunner                │    │
│  │  • Execute operations           │    │
│  │  • Track history                │    │
│  │  • Handle rollbacks             │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 3. File Management
```
┌─────────────────────────────────────────┐
│      File Management Layer               │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │  MigrationWriter                │    │
│  │  • Generate Python code         │    │
│  │  • Create timestamped files     │    │
│  │  • Format operations            │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  MigrationLoader                │    │
│  │  • Discover migration files     │    │
│  │  • Load Python modules          │    │
│  │  • Execute upgrade functions    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 4. Operations
```
┌─────────────────────────────────────────┐
│      Migration Operations                │
├─────────────────────────────────────────┤
│  Table Operations:                       │
│  • CreateTable    • DropTable            │
│  • RenameTable                           │
│                                          │
│  Column Operations:                      │
│  • AddColumn      • DropColumn           │
│  • AlterColumn    • RenameColumn         │
│                                          │
│  Index Operations:                       │
│  • CreateIndex    • DropIndex            │
│                                          │
│  Constraint Operations:                  │
│  • AddForeignKey  • DropForeignKey       │
│                                          │
│  Custom Operations:                      │
│  • RunSQL                                │
└─────────────────────────────────────────┘
```

## Data Flow

### Migration Generation Flow
```
┌─────────────┐
│   Models    │
│ (Python)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  Migration  │────▶│   Schema    │
│   Engine    │     │Introspector │
└──────┬──────┘     └──────┬──────┘
       │                   │
       │◀──────────────────┘
       ▼
┌─────────────┐
│   Detect    │
│   Changes   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generate   │
│ Operations  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Migration  │
│   Writer    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Python File │
│ (.py)       │
└─────────────┘
```

### Migration Execution Flow
```
┌─────────────┐
│ Migration   │
│   Files     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Migration  │
│   Loader    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  Migration  │────▶│  Check      │
│   Runner    │     │  Applied    │
└──────┬──────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│  Execute    │
│ Operations  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   Update    │────▶│  Database   │
│  Tracker    │     │             │
└─────────────┘     └─────────────┘
```

## Database Schema

### Migration Tracking Table
```sql
CREATE TABLE covet_migrations (
    id          SERIAL/INT/INTEGER PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    app         VARCHAR(255) NOT NULL,
    applied_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum    VARCHAR(64) NOT NULL,
    UNIQUE(name, app)
);
```

## Class Hierarchy

```
MigrationOperation (ABC)
├── CreateTable
├── DropTable
├── AddColumn
├── DropColumn
├── AlterColumn
├── RenameTable
├── RenameColumn
├── CreateIndex
├── DropIndex
├── AddForeignKey
├── DropForeignKey
└── RunSQL

Migration
├── operations: List[MigrationOperation]
├── dependencies: List[str]
└── methods: execute(), rollback(), get_checksum()

SchemaIntrospector
├── get_tables()
├── get_columns()
├── get_indexes()
└── get_constraints()

MigrationEngine
├── detect_changes()
├── generate_migration()
├── _create_table_operations()
└── _detect_table_changes()

MigrationRunner
├── apply_migration()
├── rollback_migration()
├── apply_migrations()
├── get_applied_migrations()
└── show_migrations()

MigrationWriter
├── write_migration()
├── _generate_migration_code()
└── _operation_to_code()

MigrationLoader
├── load_migrations()
└── _load_migration_file()
```

## Interaction Patterns

### Pattern 1: Auto-Generation
```
User runs: covet makemigrations
    ↓
CLI discovers models
    ↓
MigrationEngine.detect_changes(models)
    ↓
SchemaIntrospector reads database
    ↓
Compare models vs database
    ↓
Generate operations list
    ↓
MigrationEngine.generate_migration()
    ↓
MigrationWriter.write_migration()
    ↓
Migration file created
```

### Pattern 2: Migration Application
```
User runs: covet migrate
    ↓
CLI loads configuration
    ↓
MigrationLoader.load_migrations()
    ↓
MigrationRunner checks applied
    ↓
Filter pending migrations
    ↓
Sort by dependencies
    ↓
For each migration:
    ↓
    Execute operations in transaction
    ↓
    Update tracking table
    ↓
All applied successfully
```

### Pattern 3: Rollback
```
User runs: covet rollback
    ↓
CLI loads configuration
    ↓
MigrationRunner.get_applied_migrations()
    ↓
Get last migration
    ↓
MigrationLoader.load_migration_file()
    ↓
Execute rollback operations (reversed)
    ↓
Remove from tracking table
    ↓
Rollback complete
```

## Database Adapter Pattern

```
┌────────────────────────────────────┐
│      Database Connection           │
└────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌────────┐         ┌────────┐
│  Sync  │         │ Async  │
│  Pool  │         │  Pool  │
└────┬───┘         └───┬────┘
     │                 │
     └────────┬────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│PostgreSQL│     │  MySQL   │     │  SQLite  │
└──────────┘     └──────────┘     └──────────┘
```

## Security Model

```
┌─────────────────────────────────────┐
│         Security Layers             │
├─────────────────────────────────────┤
│  1. Input Validation                │
│     • Sanitize table/column names   │
│     • Validate field types          │
│                                     │
│  2. SQL Injection Prevention        │
│     • Parameterized queries         │
│     • No string concatenation       │
│                                     │
│  3. Integrity Verification          │
│     • SHA-256 checksums             │
│     • Migration tracking            │
│                                     │
│  4. Transaction Safety              │
│     • Atomic operations             │
│     • Rollback on failure           │
│                                     │
│  5. Access Control                  │
│     • Database credentials          │
│     • File permissions              │
└─────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────┐
│  Operation  │
│   Starts    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Begin     │
│ Transaction │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   Execute   │────▶│   Success   │
│  Operation  │     └──────┬──────┘
└──────┬──────┘            │
       │                   ▼
       │            ┌─────────────┐
       │            │   Commit    │
       │            │ Transaction │
       │            └──────┬──────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│    Error    │     │   Update    │
│  Occurred   │     │   Tracker   │
└──────┬──────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│  Rollback   │
│ Transaction │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Log      │
│   Error     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Raise     │
│  Exception  │
└─────────────┘
```

## Configuration Hierarchy

```
┌─────────────────────────────────────┐
│      Configuration Sources          │
├─────────────────────────────────────┤
│  1. Environment Variables           │
│     DB_ENGINE, DB_NAME, etc.        │
│                                     │
│  2. Config File                     │
│     covet.config.py                 │
│                                     │
│  3. CLI Arguments                   │
│     --migrations-dir, etc.          │
│                                     │
│  4. Defaults                        │
│     sqlite, :memory:, etc.          │
└─────────────────────────────────────┘
      Priority: CLI > Config > Env > Default
```

## Extension Points

```
┌─────────────────────────────────────┐
│      Extension Mechanisms           │
├─────────────────────────────────────┤
│  1. Custom Operations               │
│     • Inherit MigrationOperation    │
│     • Implement execute/rollback    │
│                                     │
│  2. Custom Commands                 │
│     • Add to CLI module             │
│     • Register in main()            │
│                                     │
│  3. Database Adapters               │
│     • Extend SchemaIntrospector     │
│     • Add SQL generation logic      │
│                                     │
│  4. Hooks                           │
│     • Pre/post migration            │
│     • Custom validation             │
└─────────────────────────────────────┘
```

## Performance Considerations

```
┌─────────────────────────────────────┐
│      Performance Features           │
├─────────────────────────────────────┤
│  • Connection pooling               │
│  • Lazy model loading               │
│  • Efficient schema queries         │
│  • Batch operation execution        │
│  • Transaction-based commits        │
│  • Minimal database round-trips     │
└─────────────────────────────────────┘
```

---

**Architecture Design**: Production-Ready, Scalable, Maintainable
**Pattern**: Repository + Command + Strategy
**Status**: Fully Implemented ✅
