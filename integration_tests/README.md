# Test Suite

## 🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨

### ⚠️ ZERO-TOLERANCE POLICY ⚠️

**USING MOCKS, STUBS, OR TEST DOUBLES IS ILLEGAL IN THIS REPOSITORY**

This is a **ZERO-TOLERANCE POLICY**:
- ❌ **FORBIDDEN**: `unittest.mock`, `Mock()`, `MagicMock()`, `patch()`
- ❌ **FORBIDDEN**: `pytest-mock`, `mocker` fixture
- ❌ **FORBIDDEN**: Any mocking, stubbing, or test double libraries
- ❌ **FORBIDDEN**: Fake in-memory databases or fake HTTP responses
- ❌ **FORBIDDEN**: Simulated external services or APIs

### ✅ ONLY REAL INTEGRATION TESTS ARE ALLOWED

- ✅ Real database operations with actual SQL
- ✅ Real HTTP requests through test client
- ✅ Real browser interactions with Chrome DevTools MCP
- ✅ Real external service calls (or skip tests if unavailable)

**If you write a test with mocks, the test is INVALID and must be rewritten.**

---

## Test Files

All test files in this directory follow the no-mocking policy and contain only real integration tests.

### Main Test Suite

- **`tests.py`** - Main integration tests for Bloggy application
  - REST API endpoints
  - Authentication flows
  - Database operations
  - Valkey cache integration
  - Prometheus metrics
  - Post/Comment lifecycle
  - Session management

### Role-Based Access Control Tests

- **`test_roles.py`** - Role system validation tests
  - Model imports
  - Decorator imports
  - Seeder imports
  - User model extensions

- **`test_roles_integration.py`** - Real RBAC integration tests
  - Role creation and retrieval (real database)
  - Permission management (real database)
  - User-role assignments (real database)
  - Ownership-based permissions (real database)

### OAuth Social Login Tests

- **`test_oauth_real.py`** - Real OAuth integration tests
  - Token encryption/decryption (real Fernet)
  - PKCE generation and validation (real cryptography)
  - State parameter security (real randomness)
  - OAuth account management (real database)
  - OAuth token storage (real database)

### Auto UI Generation Tests

- **`test_auto_ui.py`** - Auto UI generator tests
  - UI mapping loading
  - Route generation
  - Form generation
  - Permission checking
  - Template rendering

### Chrome Browser Integration Tests

- **`chrome_integration_tests.py`** - Chrome DevTools MCP integration tests
  - Page loading verification
  - Navigation elements
  - Responsive design testing
  - Console error checking
  - Network request validation
  - Performance metrics

- **`test_ui_chrome_real.py`** - Real Chrome UI tests
  - Homepage testing
  - Authentication flows
  - Performance monitoring
  - Visual regression testing

---

## Running Tests

### Using Docker (Recommended)

```bash
# Run all tests
docker compose -f docker/docker-compose.yaml exec runtime pytest tests/

# Run specific test file
docker compose -f docker/docker-compose.yaml exec runtime pytest tests/tests.py -v

# Run with coverage
docker compose -f docker/docker-compose.yaml exec runtime pytest tests/ --cov=app --cov-report=html
```

### Using Local Environment

```bash
# Run all tests
./run_tests.sh

# Run specific test file
cd runtime && uv run pytest ../tests/tests.py -v

# Run with coverage
./run_tests.sh --coverage
```

### Chrome Integration Tests

Chrome tests require Chrome DevTools MCP to be available:

```bash
# Enable Chrome MCP
export HAS_CHROME_MCP=true

# Run Chrome tests
pytest tests/chrome_integration_tests.py -v -s
pytest tests/test_ui_chrome_real.py -v -s
```

---

## Test Coverage Goals

- **95%+ line coverage** - All code paths tested with real requests
- **90%+ branch coverage** - All conditionals tested with real data
- **100% endpoint coverage** - Every route tested with real HTTP
- **100% database operations** - Every CRUD operation tested for real

---

## Why No Mocking?

### Mocking Creates False Confidence

- ✗ Mocked tests pass but real code fails
- ✗ Mocks don't catch integration issues
- ✗ Mocks don't test actual database behavior
- ✗ Mocks don't test real serialization/deserialization
- ✗ Mocks don't test real error handling
- ✗ Mocks become outdated when implementation changes

### Integration Tests Provide Real Confidence

- ✓ Tests fail when real code has bugs
- ✓ Tests catch integration issues between components
- ✓ Tests verify actual database behavior and constraints
- ✓ Tests verify real API contracts
- ✓ Tests verify real error handling
- ✓ Tests verify actual user experience

---

## What to Test

### ✅ DO Test (Integration Level)

- **Complete HTTP request/response cycles**
  - Route handlers with real requests
  - Form submissions with real validation
  - API endpoints with real serialization
  - Redirects and status codes

- **Real Database Operations**
  - Create: Insert records and verify in database
  - Read: Query records and verify results
  - Update: Modify records and verify changes
  - Delete: Remove records and verify deletion
  - Relationships: Test joins and foreign keys
  - Constraints: Test uniqueness, required fields

- **Real Authentication Flows**
  - Login with real password hashing
  - Session creation and persistence
  - Authorization checks with real permissions
  - CSRF token generation and validation

- **Real UI Interactions**
  - Page navigation in real browser
  - Form filling with real input
  - Button clicks with real events
  - JavaScript execution
  - CSS rendering and layout
  - Network requests from browser

### ❌ DON'T Test (Use Integration, Not Mocks)

- **Isolated function logic** → Test via real HTTP endpoint instead
- **Database queries in isolation** → Test via complete route handlers
- **Template rendering alone** → Test by requesting page and verifying HTML
- **Form validation alone** → Test by submitting real forms

---

## Test Data Management

All tests use real database operations with proper cleanup:

```python
# ✅ CORRECT - Real test data with cleanup
@pytest.fixture()
def test_posts():
    """Create real test posts in database"""
    posts = []
    with db.connection():
        for i in range(3):
            post = Post.create(
                title=f'Test Post {i}',
                text=f'Test content {i}',
                user=1
            )
            posts.append(post)
    
    yield posts
    
    # Real cleanup
    with db.connection():
        for post in posts:
            post.delete_record()
```

---

## Enforcement

**Any test using mocks will be rejected in code review and must be rewritten as a real integration test.**

**Speed is NEVER a reason to use mocks. Mocking is ILLEGAL regardless of test performance.**

If tests become slow:
- ✅ Use module-scoped fixtures for expensive setup
- ✅ Use function-scoped fixtures for test-specific data
- ✅ Parallelize with pytest-xdist if needed
- ✅ Optimize database operations (bulk creates)
- ✅ Use transaction rollbacks for faster cleanup
- ❌ **ILLEGAL** to switch to mocking to make tests faster

---

## Additional Resources

- [Main README](../README.md)
- [AGENTS.md](../AGENTS.md) - Full testing philosophy
- [Emmett Documentation](../emmett_documentation/)
- [UI Testing Guide](../documentation/README_UI_TESTING.md)
- [Chrome Testing Guide](../documentation/README_CHROME_TESTING.md)

