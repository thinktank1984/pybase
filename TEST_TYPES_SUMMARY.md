# Integration Test Types in pybase

## Summary

Total test files: **11**
Total test functions: **170+**
Total test classes: **18+**

---

## Test Files (Alphabetically)

### 1. `test_auth_comprehensive.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Functions:** 17  
**Purpose:** Comprehensive authentication testing
- Advanced authentication scenarios
- Edge cases and security testing
- Session management

### 2. `test_auto_ui.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Classes:** 5  
**Test Count:** 14 tests  
**Purpose:** Auto UI generation system
- UI mapping loader
- Auto UI generator
- Component configuration
- Field type detection
- Permission checking
- Route registration

### 3. `test_base_model.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Functions:** Unknown  
**Purpose:** Base model functionality testing
- Model inheritance
- Common model methods
- Base model utilities

### 4. `test_model_utils.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Functions:** 30  
**Purpose:** Model utility functions
- Helper functions
- Model transformations
- Data processing utilities

### 5. `test_oauth_real.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Classes:** 7  
**Test Count:** 23 tests  
**Purpose:** OAuth social login integration (NO MOCKING)
- Token encryption/decryption with real Fernet
- PKCE generation and validation
- State parameter security
- OAuth database operations
- Provider configuration (Google, GitHub, Microsoft, Facebook)
- Security validations

**Test Classes:**
- `TestRealTokenEncryption`
- `TestRealPKCEGeneration`
- `TestRealStateGeneration`
- `TestRealOAuthDatabaseOperations`
- `TestRealOAuthSecurity`
- `TestRealOAuthManager`
- `TestRealProviderConfiguration`

### 6. `test_oauth_real_user.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Classes:** 2  
**Purpose:** OAuth testing with real user account (ed.s.sharood@gmail.com)
- Real user OAuth flows
- Account linking
- Token management

### 7. `test_roles.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Functions:** 5  
**Purpose:** Basic role system tests
- Role creation
- Role assignment
- Basic permission checks

### 8. `test_roles_integration.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Functions:** 19  
**Test Count:** 19 tests  
**Purpose:** Role-Based Access Control (RBAC) integration (NO MOCKING)
- Role creation and retrieval
- Permission management
- User role assignments
- Multiple roles per user
- Permission inheritance
- Admin bypass
- Ownership-based permissions
- Moderator capabilities
- Seeded data verification

### 9. `test_roles_rest_api.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Functions:** 17  
**Purpose:** REST API for roles and permissions
- Role CRUD operations via API
- Permission API endpoints
- User-role API operations
- API authentication/authorization

### 10. `test_ui_chrome_real.py` ⚠️
**Status:** ⚠️ Active but requires Playwright (included in `./run_tests.sh --separate`)  
**Test Classes:** 4  
**Test Count:** 13 tests  
**Purpose:** Real Chrome browser UI testing
- Homepage rendering
- Navigation testing
- Responsive layouts
- Authentication pages
- Performance testing
- Console error checking
- Network request monitoring
- Visual regression testing

**Test Classes:**
- `TestHomepage`
- `TestAuthentication`
- `TestPerformance`
- `TestVisualRegression`

**Requirements:** Playwright browsers must be installed

### 11. `tests.py` ✅
**Status:** ✅ Active (included in `./run_tests.sh --separate`)  
**Test Functions:** 81  
**Test Count:** 83 tests  
**Purpose:** Main comprehensive integration tests
- Database operations (create, read, update, delete)
- Authentication & authorization
- Admin access control
- API endpoints (posts, comments, users)
- OpenAPI/Swagger documentation
- Form validation
- Valkey cache integration
- Prometheus metrics
- Error handling
- Session management
- CSRF protection
- Web page rendering

---

## Active Test Suites (./run_tests.sh --separate)

The following 11 test suites are actively run by `./run_tests.sh --separate`:

| # | Test File | Tests | Status | Time |
|---|-----------|-------|--------|------|
| 1 | `tests.py` | 83 | ✅ Passing | ~3s |
| 2 | `test_oauth_real.py` | 23 | ✅ Passing | ~0.1s |
| 3 | `test_roles_integration.py` | 19 | ✅ Passing | ~0.2s |
| 4 | `test_auto_ui.py` | 14 | ✅ Passing | ~0.06s |
| 5 | `test_ui_chrome_real.py` | 13 | ⚠️ Needs Playwright | ~1s |
| 6 | `test_auth_comprehensive.py` | 17 | 🆕 Included | - |
| 7 | `test_model_utils.py` | 30 | 🆕 Included | - |
| 8 | `test_roles_rest_api.py` | 17 | 🆕 Included | - |
| 9 | `test_roles.py` | 5 | 🆕 Included | - |
| 10 | `test_oauth_real_user.py` | ? | 🆕 Included | - |
| 11 | `test_base_model.py` | ? | 🆕 Included | - |

**Total Active Tests:** 220+ tests  
**Currently Passing:** 139 tests (from first 4 suites)

---

## Test Categories

### Database & ORM
- `tests.py` - Main database operations
- `test_base_model.py` - Base model functionality
- `test_model_utils.py` - Model utilities

### Authentication & Authorization
- `tests.py` - Basic auth flows
- `test_auth_comprehensive.py` - Advanced auth scenarios
- `test_oauth_real.py` - OAuth social login
- `test_oauth_real_user.py` - Real user OAuth flows

### Role-Based Access Control (RBAC)
- `test_roles.py` - Basic role tests
- `test_roles_integration.py` - RBAC integration
- `test_roles_rest_api.py` - Role API endpoints

### API & REST
- `tests.py` - Main API endpoints
- `test_roles_rest_api.py` - Role API

### UI & Frontend
- `test_ui_chrome_real.py` - Browser-based UI tests
- `test_auto_ui.py` - Auto UI generation

### Caching & Performance
- `tests.py` - Valkey cache & Prometheus metrics

---

## Running Tests

### Run All Tests Separately (with individual output files)
```bash
./run_tests.sh --separate
```

### Run All Tests Together
```bash
./run_tests.sh --app
```

### Run Individual Test Suite
```bash
# Main tests
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/tests.py -v

# OAuth tests
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_oauth_real.py -v

# Role tests
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_roles_integration.py -v

# Auto UI tests
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_auto_ui.py -v

# Chrome UI tests (requires Playwright)
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_ui_chrome_real.py -v

# Auth comprehensive
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_auth_comprehensive.py -v

# Model utils
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_model_utils.py -v

# Roles REST API
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_roles_rest_api.py -v

# Base roles
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_roles.py -v

# OAuth real user
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_oauth_real_user.py -v

# Base model
docker compose -f docker/docker-compose.yaml exec runtime pytest /app/integration_tests/test_base_model.py -v
```

---

## Test Coverage by Feature

| Feature | Test Files | Test Count |
|---------|-----------|-----------|
| **Database/ORM** | tests.py, test_base_model.py, test_model_utils.py | ~110+ |
| **Authentication** | tests.py, test_auth_comprehensive.py, test_oauth_real.py | ~120+ |
| **Authorization/RBAC** | test_roles.py, test_roles_integration.py, test_roles_rest_api.py | ~40+ |
| **API/REST** | tests.py, test_roles_rest_api.py | ~100+ |
| **UI/Frontend** | test_ui_chrome_real.py, test_auto_ui.py | ~27 |
| **Caching** | tests.py | ~15 |
| **Monitoring** | tests.py | ~10 |

---

## Repository Policy: NO MOCKING

🚨 **All tests follow strict NO MOCKING policy**

- ❌ No `unittest.mock`, `pytest-mock`, or test doubles
- ✅ Real database operations only
- ✅ Real HTTP requests through test client
- ✅ Real browser interactions (Chrome DevTools)
- ✅ Real encryption/decryption operations
- ✅ Tests fail (don't skip) if dependencies unavailable

See: `documentation/NO_MOCKING_ENFORCEMENT.md`

