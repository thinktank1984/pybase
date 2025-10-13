# PostgreSQL Test Fixes Summary

## Completed Fixes

### 1. ✅ OAuth Test SQL Syntax (COMPLETE)
**Files Modified:**
- `integration_tests/test_oauth_real_user.py`

**Changes:**
- Replaced all SQLite `?` placeholders with PostgreSQL `%s` placeholders
- Added proper type casting with `int()` for foreign key comparisons
- Quoted `"user"` column name to avoid PostgreSQL keyword conflicts

**Status:** All SQL syntax fixes applied successfully. OAuth tests now pass (except for expected failures due to missing tokens).

### 2. ✅ Roles REST API SQL Syntax (COMPLETE)
**Files Modified:**
- `integration_tests/test_roles_rest_api.py`

**Changes:**
- Replaced SQLite `?` placeholders with PostgreSQL `%s` placeholders in cleanup code
- Added proper integer type casting for user IDs

**Status:** SQL syntax fixes complete.

### 3. ✅ Roles Integration Migration Handling (COMPLETE)
**Files Modified:**
- `integration_tests/test_roles_integration.py`

**Changes:**
- Removed SQLite-specific database dropping code
- Updated fixture to rely on conftest.py session-level PostgreSQL setup
- Added table existence checks instead of dropping/recreating
- Quoted `"user"` column names in cleanup SQL to avoid keyword conflicts

**Status:** Migration handling updated for PostgreSQL.

### 4. ✅ Database Connection Context (COMPLETE)
**Files Modified:**
- `runtime/models/utils.py`
- `runtime/models/role/model.py`
- `runtime/models/permission/model.py`

**Changes:**
- Updated `get_db()` to use `getattr()` instead of cached import
- Added `with db.connection():` context to all model class methods:
  - `Role.get_by_name()`
  - `Role.get_all()`
  - `Role.get_permissions()`
  - `Permission.get_by_name()`
  - `Permission.get_by_resource()`
  - `Permission.get_all()`

**Status:** All model methods now properly use PostgreSQL connection contexts.

## Remaining Issue

### pyDAL Query Returns Empty Results

**Symptom:**
- Raw SQL: `SELECT name FROM roles` returns `['admin', 'author', 'moderator', 'viewer']` ✓
- pyDAL ORM: `db(db.roles.name == 'admin').select()` returns `[]` ✗

**Investigation:**
- Database URI is correct (`bloggy_test`)
- Table exists and has data (confirmed via raw SQL)
- Connection context is present
- Query object is created correctly

**Root Cause:**
The `db.roles` pyDAL Table object is not properly synced with the PostgreSQL table structure after migrations run. This is likely because:
1. conftest.py creates a new Database instance
2. It calls `define_models()` which creates table definitions in memory
3. Migrations create the actual PostgreSQL tables
4. But the pyDAL Table objects don't reflect the actual table structure

**Possible Solutions:**
1. Call a table metadata refresh/sync after migrations
2. Recreate the Database instance after migrations complete
3. Use a different approach for test database initialization
4. Investigate pyDAL's table discovery mechanism for PostgreSQL

**Workaround:**
Tests can use raw SQL queries with `db.executesql()` which work correctly. The ORM layer issue only affects model class methods that use pyDAL queries.

## Test Results Summary

### test_oauth_real_user.py
- **Status:** 9 passing, 4 expected failures (missing OAuth tokens)
- **Fixes Applied:** ✅ Complete
- **Notes:** SQL syntax fixes successful, type casting working

### test_roles_rest_api.py  
- **Status:** SQL syntax fixes applied
- **Fixes Applied:** ✅ Complete
- **Notes:** Ready to test once roles_integration is fixed

### test_roles_integration.py
- **Status:** Blocked by pyDAL query issue
- **Fixes Applied:** ⚠️ Partial (SQL syntax fixed, but ORM queries failing)
- **Notes:** Needs pyDAL table metadata sync solution

## Recommendations

### Short Term
1. Continue investigating pyDAL PostgreSQL table initialization
2. Test if recreating Database instance after migrations helps
3. Consider using Emmett's built-in migration utilities instead of subprocess

### Long Term
1. Add PostgreSQL-specific notes to AGENTS.md about pyDAL requirements
2. Create helper utilities for test database management
3. Document the pyDAL table metadata refresh pattern

## Files Changed

### Test Files
- `integration_tests/test_oauth_real_user.py` - ✅ SQL syntax fixed
- `integration_tests/test_roles_integration.py` - ⚠️ SQL fixed, ORM blocked
- `integration_tests/test_roles_rest_api.py` - ✅ SQL syntax fixed

### Model Files
- `runtime/models/utils.py` - ✅ get_db() fixed
- `runtime/models/role/model.py` - ✅ Connection contexts added
- `runtime/models/permission/model.py` - ✅ Connection contexts added

### Test Infrastructure
- `integration_tests/conftest.py` - ⚠️ Needs pyDAL sync solution

## Commands for Testing

```bash
# Test OAuth (should pass)
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_oauth_real_user.py -v

# Test roles integration (blocked by pyDAL issue)
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_roles_integration.py -v

# Test roles REST API
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_roles_rest_api.py -v
```

## Key Learnings

1. **PostgreSQL requires explicit connection contexts** - Every pyDAL query must be within `with db.connection():`
2. **SQL placeholders differ** - PostgreSQL uses `%s`, SQLite uses `?`
3. **Reserved words must be quoted** - Column names like `user` need quotes: `"user"`
4. **Type casting is strict** - PostgreSQL won't auto-cast between types
5. **pyDAL table metadata** - Table definitions must be synced with actual database schema


