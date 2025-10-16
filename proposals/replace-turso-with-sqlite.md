# OpenSpec Change Proposal: Replace Turso with SQLite

## Summary

This proposal outlines the complete replacement of the Turso database system with standard SQLite throughout the entire codebase. The change will simplify the database architecture, reduce dependencies, and eliminate the complexity of maintaining compatibility with both Turso and SQLite.

## Current State Analysis

### Database Files
- **Current primary database**: `/runtime/databases/bloggy.turso.db`
- **21 files** contain references to Turso or `bloggy.turso.db`
- **Only 1 actual database file** exists: `runtime/databases/bloggy.turso.db`

### Key Components Using Turso

1. **DatabaseManager** (`runtime/database_manager.py`):
   - Imports `turso` package (with fallback)
   - Uses `TursoDatabaseAdapter` class
   - Configures SQLite compatibility mode for Turso

2. **Application Configuration** (`runtime/app.py`):
   - Default `DATABASE_URL`: `'sqlite://runtime/databases/bloggy.turso.db'`
   - Comments reference "Turso implementation"

3. **Environment Variables**:
   - `DATABASE_URL` defaults to Turso database
   - `TURSO_DATABASE_URL` support in multiple files
   - Test configurations use Turso database

4. **Documentation and Configuration**:
   - `CLAUDE.md` references "Local Turso Database"
   - Docker and setup scripts reference Turso
   - Multiple test files reference Turso functionality

## Proposed Changes

### 1. Database File Consolidation

**Action**: Replace all database files with single SQLite database
```
New location: /runtime/databases/main.db
Remove: /runtime/databases/bloggy.turso.db
```

### 2. DatabaseManager Simplification

**Action**: Remove Turso-specific code and use native SQLite

**Changes to `runtime/database_manager.py`**:
- Remove `turso` package import and `TURSO_AVAILABLE` check
- Remove `TursoDatabaseAdapter` class
- Simplify `initialize()` method to use SQLite directly
- Update `is_turso()` method to return `False`
- Update all references from "Turso-compatible" to "SQLite"

**Simplified implementation**:
```python
def initialize(self, app: Any, database_url: Optional[str] = None) -> Database:
    if database_url is None:
        database_url = os.environ.get(
            'DATABASE_URL',
            'sqlite://runtime/databases/main.db'
        )

    app.config.db.uri = database_url
    app.config.db.adapter = 'sqlite'
    app.config.db.database = database_url.replace('sqlite://', '')

    self._db = Database(app)
    self._initialized = True
    return self._db
```

### 3. Application Configuration Updates

**Changes to `runtime/app.py`**:
```python
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'sqlite://runtime/databases/main.db'  # Updated default
)
```

### 4. Environment Variable Simplification

**Actions**:
- Remove all `TURSO_DATABASE_URL` references
- Update `DATABASE_URL` defaults to point to `main.db`
- Remove Turso-specific environment variable handling

### 5. Test Configuration Updates

**Files to update**:
- `integration_tests/conftest.py`
- `run_tests_host.sh`
- `tests/test_*.py` files

**Changes**:
- Replace all `bloggy.turso.db` references with `main.db`
- Remove Turso-specific test cases
- Update test database URLs

### 6. Documentation Updates

**Files to update**:
- `CLAUDE.md`
- `docker/RUNTIME_SETUP.md`
- `setup/setup.sh`
- All markdown documentation

**Changes**:
- Replace "Local Turso Database" with "Local SQLite Database"
- Update file paths from `bloggy.turso.db` to `main.db`
- Remove Turso-specific setup instructions

### 7. Docker Configuration

**Changes to `docker/docker-compose.yaml`**:
```yaml
environment:
  - DATABASE_URL=sqlite://runtime/databases/main.db
  # Remove TURSO_DATABASE_URL line
```

### 8. Setup Scripts

**Files to update**:
- `setup/setup.sh`
- `setup/setup_host.sh`
- `run_bloggy_host.sh`

**Changes**:
- Replace all `bloggy.turso.db` references with `main.db`
- Remove Turso-specific setup code
- Update database creation commands

## Implementation Plan

### Phase 1: Database File Migration
1. Create new `/runtime/databases/main.db`
2. Migrate data from existing `bloggy.turso.db` if needed
3. Update all database file references

### Phase 2: Code Simplification
1. Update `DatabaseManager` class
2. Remove Turso-specific imports and classes
3. Update application configuration
4. Simplify database initialization logic

### Phase 3: Configuration Updates
1. Update environment variables
2. Modify Docker configuration
3. Update setup scripts
4. Refresh test configurations

### Phase 4: Documentation and Cleanup
1. Update all documentation
2. Remove Turso-specific files
3. Archive Turso integration documentation
4. Update CLAUDE.md instructions

## Benefits

1. **Simplified Architecture**: Removes database abstraction layer
2. **Reduced Dependencies**: No longer requires `turso` package
3. **Easier Maintenance**: Single database system to support
4. **Better Performance**: Direct SQLite access without compatibility layer
5. **Clearer Documentation**: Simplified setup and configuration instructions
6. **Reduced Complexity**: Eliminates dual database system support

## Risk Assessment

**Low Risk Changes**:
- Database file rename (SQLite is compatible)
- Configuration string updates
- Documentation changes

**Medium Risk Changes**:
- DatabaseManager refactoring
- Environment variable removal
- Test configuration updates

**Mitigation Strategies**:
- Backup existing database before migration
- Run comprehensive tests after each phase
- Maintain backward compatibility where possible during transition

## Files Requiring Changes

1. **Core Application**:
   - `runtime/database_manager.py`
   - `runtime/app.py`

2. **Configuration**:
   - `docker/docker-compose.yaml`
   - `setup/setup.sh`
   - `setup/setup_host.sh`
   - `run_bloggy_host.sh`

3. **Testing**:
   - `integration_tests/conftest.py`
   - `run_tests_host.sh`
   - All test files with Turso references

4. **Documentation**:
   - `CLAUDE.md`
   - `docker/RUNTIME_SETUP.md`
   - All markdown files referencing Turso

## Success Criteria

1. ✅ Application starts successfully with SQLite database
2. ✅ All existing functionality works without modification
3. ✅ All tests pass with new database configuration
4. ✅ Documentation accurately reflects the simplified setup
5. ✅ No Turso references remain in codebase
6. ✅ Single database file (`main.db`) contains all data

## Conclusion

This change simplifies the database architecture by removing the unnecessary Turso compatibility layer while maintaining all existing functionality. The migration is straightforward since Turso uses SQLite-compatible storage, and the benefits include reduced complexity, better performance, and easier maintenance.