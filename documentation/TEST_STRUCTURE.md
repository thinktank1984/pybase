# Bloggy Test Structure

## 🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨

**This repository ONLY allows REAL integration tests. Mock tests have been DELETED.**

## Test Organization

All tests are located in the `runtime/` directory alongside the application code.

### Active Test Files

```
runtime/
├── tests.py                      # Main integration tests (pytest) ✅
├── test_ui_chrome_real.py        # Real Chrome DevTools tests ✅
├── chrome_integration_tests.py   # Additional Chrome tests ✅
├── chrome_test_helpers.py        # Chrome testing helpers ✅
├── test_oauth_real.py            # OAuth integration tests ✅
├── test_roles_integration.py     # Role system integration tests ✅
└── test_auto_ui.py               # Auto-UI generation tests ✅
```

## Test File Descriptions

### 1. `tests.py` - Main Integration Tests ✅

**Purpose:** Comprehensive **REAL** integration tests for all application features

**Test Categories:**
- ✅ Basic application (login, admin access, empty db)
- ✅ REST API endpoints (Posts, Comments, Users)
- ✅ OpenAPI/Swagger documentation
- ✅ Authentication flows (login, logout, credentials)
- ✅ Post lifecycle (viewing, creating, forms)
- ✅ Comment functionality
- ✅ Authorization (admin-only routes)
- ✅ Database relationships (User/Post/Comment)
- ✅ Error handling and edge cases
- ✅ Session management and CSRF
- ✅ Valkey cache operations
- ✅ Prometheus metrics collection

**Running:**
```bash
# Via test runner script (Docker)
./run_tests.sh --app -v

# Directly in Docker
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -v

# With coverage
docker compose -f docker/docker-compose.yaml exec runtime \
    pytest tests.py --cov=app --cov-report=html --cov-report=term-missing
```

**Philosophy:** NO MOCKING (ILLEGAL)
- ✅ Real database operations (SQLite)
- ✅ Real HTTP requests (Emmett test client)
- ✅ Real authentication and sessions
- ✅ Real form submissions with CSRF tokens
- ✅ Real validation and error handling
- ❌ **FORBIDDEN:** Mocks, stubs, test doubles

---

### 2. `test_ui_chrome_real.py` - Real Chrome DevTools Tests ✅

**Purpose:** REAL browser testing using actual Chrome via MCP Chrome DevTools

**Test Categories:**
- Real browser navigation and page loading
- Real DOM structure and element interaction
- Real form filling and submission
- Real JavaScript execution
- Real network request monitoring
- Real console error detection
- Real screenshot capture
- Real responsive design testing

**Running:**
```bash
# Via test runner script with HAS_CHROME_MCP=true
HAS_CHROME_MCP=true ./run_tests.sh --chrome

# Directly (requires Chrome running)
export HAS_CHROME_MCP=true
cd runtime
pytest test_ui_chrome_real.py -v -s
```

**Requirements:**
- Chrome browser must be running on host
- MCP Chrome DevTools server connected
- Application running on http://localhost:8081
- Environment variable `HAS_CHROME_MCP=true`

**MCP Tools Used:**
- `mcp_chrome-devtools_navigate_page()` - Navigate to URLs
- `mcp_chrome-devtools_take_snapshot()` - Get DOM snapshot with UIDs
- `mcp_chrome-devtools_click()` - Click real elements
- `mcp_chrome-devtools_fill()` - Fill real form fields
- `mcp_chrome-devtools_take_screenshot()` - Capture real screenshots
- `mcp_chrome-devtools_list_network_requests()` - Monitor real network
- `mcp_chrome-devtools_list_console_messages()` - Check real console

**Status:** ✅ These are **REAL** tests that actually open Chrome and test the UI!

---

### 3. `chrome_integration_tests.py` - Additional Chrome Tests ✅

**Purpose:** More real Chrome integration tests for specific UI features

**Test Categories:**
- Accessibility testing
- Performance testing
- Cross-browser compatibility
- Visual regression testing

**Running:** Same as `test_ui_chrome_real.py` above

---

### 4. OAuth & Role System Tests ✅

- `test_oauth_real.py` - Real OAuth integration tests
- `test_roles_integration.py` - Real role system integration tests
- `test_auto_ui.py` - Real auto-UI generation tests

All follow the same **NO MOCKING** policy - only real database operations and HTTP requests.

---

## Test Runner Script

### `run_tests.sh` - Unified Test Runner

**Usage:**
```bash
# Run all tests (app + Chrome if HAS_CHROME_MCP=true)
./run_tests.sh

# Run specific test suites
./run_tests.sh --app              # Integration tests only
./run_tests.sh --chrome           # Chrome tests only (skipped if no HAS_CHROME_MCP)

# Run with options
./run_tests.sh --app -v           # Verbose output
./run_tests.sh --app -vv          # Very verbose output
./run_tests.sh --app -x           # Stop on first failure
./run_tests.sh --app --no-coverage  # Skip coverage report

# Run specific tests
./run_tests.sh --app -k test_api  # Tests matching "test_api"
./run_tests.sh --app -k prometheus  # Prometheus tests only

# Show slowest tests
./run_tests.sh --app --durations=10

# Advanced options
./run_tests.sh --app -vv -x -k test_login  # Debug specific test
./run_tests.sh --app --cov-min=70          # Require 70% coverage

# Run real Chrome tests
HAS_CHROME_MCP=true ./run_tests.sh --chrome
```

**Important Notes:**
- Mock tests have been **DELETED** from this repository
- Chrome tests are **SKIPPED** (not mocked) if prerequisites aren't met
- This follows the repository's strict **NO MOCKING** policy

---

## Test Development Guidelines

### Writing Integration Tests

**DO:**
- ✅ Use real database operations (`db.connection()`)
- ✅ Use real HTTP requests (`client.get()`, `logged_client.post()`)
- ✅ Verify actual database state after operations
- ✅ Test complete request/response cycles
- ✅ Use descriptive test names (`test_api_posts_create_authenticated`)
- ✅ Add docstrings to every test
- ✅ Clean up test data in fixtures
- ✅ Test both success and error cases

**DON'T (ILLEGAL):**
- ❌ **ILLEGAL:** Mock database calls
- ❌ **ILLEGAL:** Mock HTTP requests
- ❌ **ILLEGAL:** Mock external services
- ❌ **ILLEGAL:** Use test doubles or stubs
- ❌ **ILLEGAL:** Use unittest.mock, pytest-mock, or any mocking libraries
- ❌ **FORBIDDEN:** Create fake data that doesn't touch the database
- ❌ **FORBIDDEN:** Simulate browser interactions instead of using real Chrome

**If prerequisites aren't met, SKIP tests - don't mock them!**

### Fixture Pattern

**Use factory fixtures for dynamic data:**
```python
@pytest.fixture()
def create_test_post():
    """Factory fixture to create test posts on demand"""
    created_posts = []
    
    def _create_post(title='Test Post', text='Test content', user_id=1):
        with db.connection():
            post = Post.create(title=title, text=text, user=user_id)
            post_id = post.id
        created_posts.append(post_id)
        return post_id
    
    yield _create_post
    
    # Cleanup all created posts
    with db.connection():
        for post_id in created_posts:
            post = Post.get(post_id)
            if post:
                post.comments().delete()
                post.delete_record()
```

**Use in tests:**
```python
def test_view_single_post(client, create_test_post):
    """Test GET /post/<id> displays post"""
    post_id = create_test_post(title='Single Post', text='Single Content')
    
    r = client.get(f'/post/{post_id}')
    assert r.status == 200
    assert 'Single Post' in r.data
```

---

## Coverage Goals

### Target Coverage
- **Pass Rate:** 90%+ passing tests
- **Line Coverage:** 70-75%
- **Branch Coverage:** 65-70%
- **Endpoint Coverage:** 100% (all routes tested)

### Coverage Reporting
```bash
# Generate HTML coverage report
docker compose -f docker/docker-compose.yaml exec runtime \
    pytest tests.py --cov=app --cov-report=html --cov-report=term-missing

# Open report
open runtime/htmlcov/index.html
```

---

## Test Execution Environment

### Docker Environment (Recommended)

**Why Docker?**
- Consistent environment across all machines
- All dependencies pre-installed
- Isolated database for testing
- Matches production environment

**Setup:**
```bash
# Start application
docker compose -f docker/docker-compose.yaml up runtime -d

# Run tests
./run_tests.sh --app -v

# Stop application
docker compose -f docker/docker-compose.yaml down
```

### Local Environment (Fallback)

**Setup:**
```bash
cd runtime
uv run pytest tests.py -v
```

**Note:** Local environment may have dependency or configuration differences.

---

## Test Database

### Database Isolation

Tests use the same database as development but:
- ✅ Setup creates fresh migrations
- ✅ Setup creates admin user
- ✅ Each test cleans up its data
- ✅ Module-scoped fixtures ensure consistency

### Database Setup

```python
@pytest.fixture(scope='module', autouse=True)
def _prepare_db(request):
    """Setup test database with migrations and admin user"""
    with db.connection():
        migration = generate_runtime_migration(db)
        migration.up()
        setup_admin()
    
    yield
    
    with db.connection():
        User.all().delete()
        auth.delete_group('admin')
        migration.down()
```

---

## Troubleshooting

### Common Issues

**Issue: "Chrome tests skipped"**
- **Reason:** `HAS_CHROME_MCP` environment variable not set
- **Solution:** Export `HAS_CHROME_MCP=true` and ensure Chrome is running

**Issue: "Mock tests not found"**
- **Reason:** Mock tests have been DELETED per repository policy
- **Solution:** Use real integration tests instead

**Issue: "File or directory not found: runtime/tests.py"**
- **Solution:** Run from project root, not from runtime/

**Issue: "Session context errors"**
- **Solution:** Use factory fixtures, not module-scoped fixtures with session

**Issue: "Tests pass locally but fail in Docker"**
- **Solution:** Always use Docker for testing to ensure consistency

### Debug Commands

```bash
# Run single test with full output
./run_tests.sh --app -k test_login -vv

# Stop on first failure
./run_tests.sh --app -x

# Show test execution time
./run_tests.sh --app --durations=10

# Show all fixtures
docker compose -f docker/docker-compose.yaml exec runtime \
    pytest tests.py --fixtures
```

---

## Policy Enforcement

**🚨 Any pull request containing mock tests will be REJECTED 🚨**

- ❌ Tests using `unittest.mock`, `Mock()`, `MagicMock()`
- ❌ Tests using `pytest-mock` or `mocker` fixture
- ❌ Tests simulating database operations
- ❌ Tests simulating HTTP requests
- ❌ Tests simulating external services

**✅ Only REAL integration tests are accepted**

---

**Status:** 📋 No Mocking Policy Enforced  
**Last Updated:** 2025-10-12  
**Mock Tests:** DELETED (policy violation)
**Real Tests:** All active test files

