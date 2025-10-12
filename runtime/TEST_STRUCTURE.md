# Bloggy Test Structure

## Test Organization

All tests are located in the `runtime/` directory alongside the application code.

### Active Test Files

```
runtime/
├── tests.py              # Main integration tests (pytest)
├── ui_tests.py           # UI integration tests (pytest)
└── test_ui_chrome.py     # Chrome DevTools tests (MCP-based)
```

## Test File Descriptions

### 1. `tests.py` - Main Integration Tests

**Purpose:** Comprehensive integration tests for all application features

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

**Current Status:** 29 tests implemented
- 3 basic app tests
- 15 Valkey cache tests  
- 11 Prometheus metrics tests

**Target:** 97 tests (100% endpoint coverage)

**Running:**
```bash
# Via test runner script
./run_tests.sh --app -v

# Directly in Docker
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -v

# With coverage
docker compose -f docker/docker-compose.yaml exec runtime \
    pytest tests.py --cov=app --cov-report=html --cov-report=term-missing
```

**Philosophy:** NO MOCKING
- Real database operations (SQLite)
- Real HTTP requests (Emmett test client)
- Real authentication and sessions
- Real form submissions with CSRF tokens
- Real validation and error handling

---

### 2. `ui_tests.py` - UI Integration Tests

**Purpose:** Test user interface and frontend interactions

**Test Categories:**
- Template rendering
- Form elements and validation
- Static file serving (CSS, JS)
- Tailwind CSS integration
- Layout and component structure

**Running:**
```bash
# Via test runner script
./run_tests.sh --ui -v

# Directly in Docker
docker compose -f docker/docker-compose.yaml exec runtime pytest ui_tests.py -v
```

---

### 3. `test_ui_chrome.py` - Chrome DevTools Tests

**Purpose:** Real browser testing using MCP Chrome DevTools integration

**Test Categories:**
- Browser navigation and page loading
- DOM structure and element interaction
- Form filling and submission
- JavaScript execution
- Network request monitoring
- Console error detection
- Screenshot capture
- Responsive design testing

**Running:**
```bash
# Via test runner script
./run_tests.sh --chrome

# Directly in Docker
docker compose -f docker/docker-compose.yaml exec runtime \
    python test_ui_chrome.py
```

**Requirements:**
- Chrome browser must be running
- MCP Chrome DevTools server connected
- Application running on http://localhost:8081

**Tools Used:**
- `mcp_chrome-devtools_navigate_page()` - Navigate to URLs
- `mcp_chrome-devtools_take_snapshot()` - Get DOM snapshot with UIDs
- `mcp_chrome-devtools_click()` - Click elements
- `mcp_chrome-devtools_fill()` - Fill form fields
- `mcp_chrome-devtools_take_screenshot()` - Capture screenshots
- `mcp_chrome-devtools_list_network_requests()` - Monitor network
- `mcp_chrome-devtools_list_console_messages()` - Check console

---

## Test Runner Script

### `run_tests.sh` - Unified Test Runner

**Usage:**
```bash
# Run all tests (app + UI + Chrome)
./run_tests.sh

# Run specific test suites
./run_tests.sh --app              # Integration tests only
./run_tests.sh --ui               # UI tests only
./run_tests.sh --chrome           # Chrome tests only

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
```

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

**DON'T:**
- ❌ Mock database calls
- ❌ Mock HTTP requests
- ❌ Mock external services
- ❌ Use test doubles or stubs
- ❌ Skip cleanup in fixtures
- ❌ Test in isolation without integration

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

### Current Coverage
- **Tests Implemented:** 29/97 (30%)
- **Endpoint Coverage:** ~20%
- **Line Coverage:** ~40-45%

### Target Coverage
- **Tests:** 97 tests (100% endpoint coverage)
- **Pass Rate:** 90%+ (87+ passing tests)
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

## Continuous Integration

### Running in CI/CD

```bash
# CI script example
docker compose -f docker/docker-compose.yaml up runtime -d
docker compose -f docker/docker-compose.yaml exec runtime \
    pytest tests.py --cov=app --cov-report=xml --cov-report=term
docker compose -f docker/docker-compose.yaml down
```

### Coverage Requirements

Set minimum coverage in CI:
```bash
pytest tests.py --cov=app --cov-fail-under=70
```

---

## Troubleshooting

### Common Issues

**Issue: "File or directory not found: runtime/tests.py"**
- **Solution:** Run from project root, not from runtime/

**Issue: "Session context errors"**
- **Solution:** Use factory fixtures, not module-scoped fixtures with session

**Issue: "Database already exists"**
- **Solution:** Delete database before tests: `rm runtime/databases/bloggy.db`

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

## Next Steps

See `COMPLETION_PLAN.md` for the roadmap to achieve 100% integration test coverage.

**Summary:**
1. ✅ Test infrastructure complete
2. 🔄 Restore 68 additional integration tests (in progress)
3. ⏳ Achieve 90%+ pass rate
4. ⏳ Reach 70-75% line coverage
5. ⏳ Document all test scenarios

**Estimated Time:** 9-14 hours of focused work

---

**Status:** 📋 Structure Documented  
**Last Updated:** 2025-10-12  
**Test Files:** 3 active files, 0 duplicates

