# PostgreSQL Migration Proposal - Summary

## 📋 Overview

An OpenSpec change proposal has been created to replace SQLite with PostgreSQL as the primary database for the Bloggy application.

**Change ID**: `replace-sqlite-with-postgres`  
**Status**: ⏳ Awaiting Approval (0/28 tasks)  
**Type**: Breaking Change - Architecture Shift

## 🎯 Why This Change?

SQLite has limitations for production environments:
- ❌ Limited concurrent write performance (file-based locking)
- ❌ No client-server architecture for multi-instance deployments
- ❌ Weaker concurrency compared to PostgreSQL
- ❌ Not suitable for high-traffic applications

PostgreSQL provides:
- ✅ Robust ACID compliance
- ✅ Excellent concurrency and connection pooling
- ✅ Advanced indexing and full-text search
- ✅ Proven production scalability
- ✅ Already used by Bugsink in the Docker environment

## 📦 What's Included in the Proposal

The proposal includes **4 files** following OpenSpec conventions:

### 1. `proposal.md` - The "Why" and "What"
- Problem statement and motivation
- List of changes (marked breaking changes)
- Impact analysis (affected specs and code)
- Migration path overview

### 2. `tasks.md` - Implementation Checklist (28 tasks)
Organized into 6 sections:
1. **Docker Infrastructure** (5 tasks) - PostgreSQL service setup
2. **Database Configuration** (5 tasks) - Connection string and settings
3. **Migration Strategy** (5 tasks) - Data migration from SQLite
4. **Testing Updates** (5 tasks) - PostgreSQL test database
5. **Documentation** (5 tasks) - Update guides and instructions
6. **Cleanup** (3 tasks) - Remove SQLite artifacts

### 3. `design.md` - Technical Decisions
Covers 5 key decisions with rationale:
- **Decision 1**: PostgreSQL 16 (Alpine image)
- **Decision 2**: Environment variable configuration with fallback
- **Decision 3**: Connection pool size of 20 (up from 10)
- **Decision 4**: Separate test database with automatic cleanup
- **Decision 5**: Manual migration with documentation (no automated tool)

Also includes:
- Risks and mitigations
- Complete migration plan with rollback strategy
- Open questions and answers

### 4. Spec Deltas (2 files)
- `specs/database/spec.md` - **NEW CAPABILITY** with 9 requirements
  - PostgreSQL connection configuration
  - Connection pool management
  - Docker service setup
  - Error handling
  - Environment-specific configuration
  
- `specs/testing/spec.md` - **MODIFIED** existing testing spec
  - Updated for PostgreSQL test database
  - Connection pool settings for tests
  - Test isolation requirements

## 🔑 Key Technical Decisions

### PostgreSQL Configuration
```python
# Environment variable with fallback
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://bloggy:bloggy_password@postgres:5432/bloggy'
)
app.config.db.uri = DATABASE_URL

# PostgreSQL-optimized connection pool
app.config.db.pool_size = int(os.environ.get('DB_POOL_SIZE', '20'))
app.config.db.adapter_args = {
    'sslmode': 'prefer',  # Use SSL if available
}
```

### Docker Compose Service
```yaml
postgres:
  image: postgres:16-alpine
  container_name: postgres
  restart: unless-stopped
  environment:
    POSTGRES_DB: bloggy
    POSTGRES_USER: bloggy
    POSTGRES_PASSWORD: bloggy_password
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U bloggy"]
    interval: 5s
    timeout: 5s
    retries: 5
```

### Test Database
```python
# Separate test database
TEST_DATABASE_URL = os.environ.get(
    'TEST_DATABASE_URL',
    'postgresql://bloggy:bloggy_password@postgres:5432/bloggy_test'
)
```

## 🚨 Breaking Changes

1. **Database files** in `runtime/databases/` will no longer be used
2. **SQLite-specific SQL** queries must be replaced with PostgreSQL equivalents
3. **Development setup** requires Docker with PostgreSQL running
4. **Existing data** must be manually migrated or will be lost

## 📝 Implementation Steps (High-Level)

1. **Add PostgreSQL to Docker** - New service with health check
2. **Update app.py** - Change database URI and configuration
3. **Migrate data** - Export from SQLite, import to PostgreSQL (optional)
4. **Update tests** - Use PostgreSQL test database
5. **Update docs** - Reflect PostgreSQL in all documentation
6. **Cleanup** - Remove SQLite files and configuration

## ✅ Validation

The proposal has been validated with OpenSpec:
```bash
$ openspec validate replace-sqlite-with-postgres --strict
✓ Change 'replace-sqlite-with-postgres' is valid
```

All requirements have proper scenarios using the correct format (`#### Scenario:`).

## 📂 Proposal Location

```
openspec/changes/replace-sqlite-with-postgres/
├── proposal.md              # Why and what
├── tasks.md                 # 28 implementation tasks
├── design.md                # Technical decisions and migration plan
└── specs/
    ├── database/
    │   └── spec.md          # NEW: 9 requirements for PostgreSQL
    └── testing/
        └── spec.md          # MODIFIED: 3 requirements updated
```

## 🔄 Migration Path for Existing Data

### Option 1: Start Fresh (Recommended for Development)
1. Pull latest code
2. Start Docker Compose (PostgreSQL initializes)
3. Run migrations: `docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up`
4. Done! Clean slate with PostgreSQL

### Option 2: Migrate Existing Data
1. Backup SQLite: `cp runtime/databases/bloggy.db runtime/databases/bloggy.db.backup`
2. Export data from SQLite (custom script or SQL dump)
3. Start Docker Compose with PostgreSQL
4. Run migrations to create schema
5. Import data into PostgreSQL
6. Verify data integrity
7. Remove SQLite database files

### Rollback Plan
If anything goes wrong:
1. Stop Docker Compose
2. Restore previous version of code
3. Restore SQLite database from backup
4. Restart with SQLite

## 📊 Impact Analysis

### Affected Files
- `runtime/app.py` - Database configuration (lines 62-70)
- `docker/docker-compose.yaml` - Add PostgreSQL service
- `integration_tests/conftest.py` - Test database setup
- `documentation/AGENTS.md` - Database documentation
- `openspec/project.md` - Tech stack description

### Affected Capabilities
- **database** (NEW) - Database connection and configuration
- **testing** (MODIFIED) - Test database using PostgreSQL

## 🚀 Next Steps

### For Reviewers
1. Review `openspec/changes/replace-sqlite-with-postgres/proposal.md`
2. Review technical decisions in `design.md`
3. Check requirements in `specs/database/spec.md`
4. Approve or request changes

### For Implementation (After Approval)
1. Read all proposal files
2. Follow `tasks.md` checklist sequentially
3. Update each task status as you complete it
4. Run `openspec validate --strict` after implementation
5. Archive the change after successful deployment

## 📚 Related Documentation

- **OpenSpec Instructions**: `/openspec/AGENTS.md`
- **Project Context**: `/openspec/project.md`
- **Current Database Config**: `runtime/app.py` (lines 62-70)
- **Docker Compose**: `docker/docker-compose.yaml`

## ❓ Questions or Concerns?

The proposal includes an "Open Questions" section in `design.md` that addresses:
- Whether to provide automated data migration script (No - manual is sufficient)
- Connection pool configurability (Yes - via environment variable)
- SSL requirements for development (Use `sslmode=prefer`)

---

**Status**: 📋 Proposal Ready for Review  
**Validation**: ✅ Passed strict validation  
**Tasks**: 0/28 completed  
**Breaking**: Yes - Requires approval before implementation

