# Fix Test 3 - Proposal Created ✅

## Proposal: fix-postgres-test-failures-3

**Status**: ✅ Created and Validated  
**Location**: `openspec/changes/fix-postgres-test-failures-3/`

## Summary

Created a comprehensive OpenSpec proposal to fix the remaining 45 failing/erroring tests in the main integration test suite after the PostgreSQL migration.

## Problem

After migrating from SQLite to PostgreSQL:
- **17 tests FAILED** - ValueError exceptions from PostgreSQL adapter
- **28 tests ERRORED** - `logged_client` fixture fails with 500 status during setup
- **Root cause**: PostgreSQL requires explicit `with db.connection():` contexts for query execution

## Solution

The proposal includes:

### 1. Core Strategy
- Wrap all database operations in tests with `with db.connection():` contexts
- Fix the critical `logged_client` fixture that blocks 28 tests
- Update test utilities (`create_test_user`, `create_test_post`)
- Ensure model validators work within connection contexts

### 2. Implementation Plan (10 phases, 50 tasks)
1. ✅ Fix Database Connection Context Management
2. ✅ Fix logged_client Fixture (priority - unblocks 28 tests)
3. ✅ Fix Test Utility Functions
4. ✅ Fix Model Validation Queries
5. ✅ Fix Test Setup and Teardown
6. ✅ Fix Query Execution Failures (17 tests)
7. ✅ Fix Authentication Flow Tests
8. ✅ Fix API Endpoint Tests (logged_client dependent)
9. ✅ Testing and Validation
10. ✅ Documentation

### 3. Technical Design
- **Connection Context Helper**: Create `ensure_db_connection()` utility
- **Pattern**: Explicit `with db.connection():` wrapping
- **Priority**: Fix logged_client first (highest impact)
- **Migration**: Phase-based rollout (fixtures → utilities → tests)

## Files Created

```
openspec/changes/fix-postgres-test-failures-3/
├── proposal.md         ✅ Why, what, impact
├── tasks.md           ✅ 50 implementation tasks
├── design.md          ✅ Technical decisions and patterns
└── specs/
    └── testing/
        └── spec.md    ✅ Updated requirements
```

## Validation

```bash
$ openspec validate fix-postgres-test-failures-3 --strict
Change 'fix-postgres-test-failures-3' is valid ✅
```

## Current Test Status

**Before Fix**:
- ✅ 38 passed
- ❌ 17 failed
- ❌ 28 errors
- Total: 38/55 passing (69%)

**After Fix (Expected)**:
- ✅ 55 passed
- ✅ 0 failed
- ✅ 0 errors
- Total: 55/55 passing (100%)

## Key Technical Decisions

### Decision 1: Explicit Connection Contexts
Use `with db.connection():` wrapping instead of auto-connecting decorators or monkey-patching.

**Why**: Clear, explicit, matches Emmett patterns, no magic behavior.

### Decision 2: Fix Logged Client First
Prioritize the `logged_client` fixture since 28 tests depend on it.

**Why**: Highest impact - unblocks majority of failing tests.

### Decision 3: Connection Context Helper
Create `ensure_db_connection()` helper to handle nested contexts safely.

**Why**: Provides consistent pattern, handles edge cases, cleaner test code.

## Example Pattern

**Before (SQLite - works but shouldn't)**:
```python
def create_test_user():
    user = User.create(email="test@example.com", password="test123")
    return user.id
```

**After (PostgreSQL - correct)**:
```python
def create_test_user():
    with db.connection():
        user = User.create(email="test@example.com", password="test123")
        return user.id
```

## Next Steps

### To Review Proposal
```bash
cd /Users/ed.sharood2/code/pybase
openspec show fix-postgres-test-failures-3
```

### To Start Implementation
```bash
# 1. Review the proposal
cat openspec/changes/fix-postgres-test-failures-3/proposal.md

# 2. Review technical design
cat openspec/changes/fix-postgres-test-failures-3/design.md

# 3. Review implementation tasks
cat openspec/changes/fix-postgres-test-failures-3/tasks.md

# 4. Begin implementation
# Follow the task order in tasks.md
```

### To Test Progress
```bash
# Run tests in Docker (assumes container is running)
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/tests.py -v

# Run with verbose output to see specific failures
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/tests.py -vv

# Run specific test to debug
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/tests.py -k test_login -vv
```

## Related Proposals

1. **fix-postgres-test-failures** - Addresses main `tests.py` database context issues (no tasks defined yet)
2. **fix-postgres-test-failures-2** - Addresses OAuth and roles test failures (31 tasks)
3. **fix-postgres-test-failures-3** - This proposal - main integration test suite (50 tasks)

## Success Criteria

- ✅ `logged_client` fixture succeeds (status 200)
- ✅ All 28 fixture setup errors resolved
- ✅ All 17 query execution failures resolved
- ✅ 55/55 tests passing in tests.py
- ✅ Zero ValueError exceptions from PostgreSQL adapter
- ✅ Test runtime < 15 seconds
- ✅ No connection leaks or warnings

## Documentation Updates Needed

After implementation:
1. PostgreSQL connection context requirements for tests
2. Examples of proper database operation wrapping
3. Test writing guide with PostgreSQL patterns
4. Common pitfalls and solutions

---

**Proposal Status**: ✅ READY FOR REVIEW  
**OpenSpec Validation**: ✅ PASSED  
**Date Created**: October 13, 2025

