# Integration Tests

This directory contains all integration tests for the pybase project.

## 🚨 CRITICAL POLICY: NO MOCKING ALLOWED

**⚠️ USING MOCKS, STUBS, OR TEST DOUBLES IS ILLEGAL IN THIS REPOSITORY ⚠️**

All tests in this directory must follow the ZERO-TOLERANCE NO MOCKING POLICY:

- ❌ **FORBIDDEN**: `unittest.mock`, `Mock()`, `MagicMock()`, `patch()`
- ❌ **FORBIDDEN**: `pytest-mock`, `mocker` fixture  
- ❌ **FORBIDDEN**: Any mocking, stubbing, or test double libraries
- ✅ **REQUIRED**: Real database operations with actual SQL
- ✅ **REQUIRED**: Real HTTP requests through test client
- ✅ **REQUIRED**: Real integration tests only

## Validation

This directory includes `validate_no_mocking.py` to enforce the NO MOCKING policy.

**Run validation:**
```bash
# From integration_tests/ directory
python3 validate_no_mocking.py

# From project root
python3 integration_tests/validate_no_mocking.py

# Strict mode (exits with error if violations found)
python3 integration_tests/validate_no_mocking.py --strict
```

**Current status:**
```
Files checked: 9
✅ NO VIOLATIONS FOUND
```

## Test Files

### Core Integration Tests
- **`tests.py`** (1,635 lines) - Main application integration tests
  - User authentication and authorization
  - Post and comment CRUD operations
  - API endpoint testing
  - Database operations
  
- **`conftest.py`** (85 lines) - Pytest configuration and fixtures
  - Database setup and teardown
  - Test client fixtures
  - Shared test utilities

### OAuth Social Login Tests
- **`test_oauth_real_user.py`** (419 lines) - OAuth tests with real user (ed.s.sharood@gmail.com)
  - Real database operations
  - Token encryption/decryption
  - Multiple provider support
  - Account linking
  
- **`test_oauth_real.py`** (614 lines) - Core OAuth functionality tests
  - PKCE generation and validation
  - State parameter security
  - Token management
  - Security features

- **`oauth_test_config.yaml`** (106 lines) - OAuth test configuration
  - Test user credentials
  - Provider settings

### Role-Based Access Control Tests
- **`test_roles_integration.py`** (587 lines) - RBAC integration tests
  - Role creation and management
  - Permission assignment
  - Access control validation
  
- **`test_roles.py`** (188 lines) - Role system tests
  - Role hierarchy
  - Permission checks
  - User role assignment

### Auto UI Generation Tests
- **`test_auto_ui.py`** (313 lines) - Automatic UI generation tests
  - Form generation from models
  - CRUD interface generation
  - UI component validation

### Chrome DevTools UI Tests
- **`test_ui_chrome_real.py`** (251 lines) - Real browser UI tests
  - Real Chrome browser interactions
  - Page navigation and forms
  - Visual testing
  
- **`chrome_integration_tests.py`** (426 lines) - Chrome DevTools integration
  - Browser automation with MCP
  - Screenshot capture
  - DOM validation

### Validation Script
- **`validate_no_mocking.py`** - NO MOCKING policy validator
  - Scans all test files for mocking violations
  - Enforces zero-tolerance policy
  - Used in CI/CD and pre-commit hooks

## Running Tests

### All Tests
```bash
# From project root
./run_tests.sh

# Or with Docker (recommended)
docker compose -f docker/docker-compose.yaml exec runtime \
  pytest /app/integration_tests/ -v
```

### Specific Test Files
```bash
# OAuth tests
pytest integration_tests/test_oauth_real_user.py -v

# Role tests
pytest integration_tests/test_roles_integration.py -v

# UI tests (requires Chrome MCP)
HAS_CHROME_MCP=true pytest integration_tests/test_ui_chrome_real.py -v

# Core tests
pytest integration_tests/tests.py -v
```

### With Coverage
```bash
pytest integration_tests/ --cov=runtime --cov-report=term-missing
```

## Test Statistics

- **Total test files:** 9
- **Total lines of test code:** ~5,500 lines
- **Mocking violations:** 0 ✅
- **Policy compliance:** 100% ✅

## Key Features

### Real Integration Testing
All tests use real operations:
- ✅ Real PostgreSQL database with actual SQL
- ✅ Real HTTP requests via test client
- ✅ Real encryption with Fernet
- ✅ Real browser with Chrome DevTools MCP
- ✅ Real OAuth flows (when configured)

### Comprehensive Coverage
- User authentication and sessions
- CRUD operations (create, read, update, delete)
- API endpoints with validation
- Role-based access control
- OAuth social login
- Auto UI generation
- Browser UI interactions

### Repository Policy Compliance
- Zero mocking - all tests use real operations
- Enforced via `validate_no_mocking.py`
- Pre-commit hooks prevent mocking
- CI/CD validation blocks PRs with mocks

## Configuration Files

- **`oauth_test_config.yaml`** - OAuth test user and provider configuration
- **`conftest.py`** - Pytest fixtures and test setup
- **`pytest.ini`** - Pytest configuration (in runtime/)

## Documentation

- **`../documentation/OAUTH_TESTING_GUIDE.md`** - Complete OAuth testing guide
- **`../documentation/OAUTH_QUICK_START.md`** - 5-minute OAuth quick start
- **`../documentation/NO_MOCKING_ENFORCEMENT.md`** - Policy enforcement guide
- **`../documentation/README_UI_TESTING.md`** - UI testing guide
- **`../documentation/CHROME_TESTING_GUIDE.md`** - Chrome DevTools guide
- **`../AGENTS.md`** - Repository policy and agent instructions

## Support

### Validate NO MOCKING Policy
```bash
cd integration_tests
python3 validate_no_mocking.py
```

### Check Logs
```bash
docker compose -f docker/docker-compose.yaml logs runtime
```

### Run Specific Test
```bash
pytest integration_tests/tests.py::test_user_login -v
```

### Debug Test
```bash
pytest integration_tests/tests.py::test_user_login -v -s  # Show print statements
```

## Contributing

When adding new tests:

1. **Follow NO MOCKING policy** - Use real operations only
2. **Run validator** - `python3 validate_no_mocking.py`
3. **Test your tests** - Ensure they pass
4. **Add documentation** - Update this README if needed
5. **Check coverage** - Run with `--cov` flag

**Remember:** Mocking is ILLEGAL. Tests must use real database, real HTTP, real everything!

## Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `pytest integration_tests/ -v` |
| Run OAuth tests | `pytest integration_tests/test_oauth_real_user.py -v` |
| Run with coverage | `pytest integration_tests/ --cov=runtime` |
| Validate no mocking | `python3 integration_tests/validate_no_mocking.py` |
| Run in Docker | `docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/ -v` |
| Check logs | `docker compose -f docker/docker-compose.yaml logs runtime` |

## Test User Information

For OAuth testing, we use:
- **Name:** Ed
- **Email:** ed.s.sharood@gmail.com

See `oauth_test_config.yaml` for full configuration.

---

**All tests in this directory are REAL integration tests with ZERO mocking.**
