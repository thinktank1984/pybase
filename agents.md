<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AGENTS.md - Critical Agent Instructions

This file provides guidance to AI agents (Claude Code, Gemini, etc.) when working with code in this repository.

---

## 🐳 CRITICAL: Docker is Always Running

**⚠️ DO NOT START OR STOP DOCKER CONTAINERS ⚠️**

This is a **CRITICAL RULE**:
- ❌ **NEVER** run `docker compose up` or `docker compose down`
- ❌ **NEVER** start or stop containers
- ❌ **NEVER** restart containers from the host

**✅ Docker containers are ALWAYS RUNNING:**
- ✅ The `runtime` container is always up
- ✅ The `postgres` container is always up
- ✅ All services are persistent

**✅ To restart code or services:**
- ✅ Connect to the container: `docker compose -f docker/docker-compose.yaml exec runtime bash`
- ✅ Restart processes inside the container
- ✅ Kill processes with `pkill` if needed
- ✅ Use `exec` commands to run operations inside running containers

**Example - Restarting the application:**
```bash
# WRONG - Do not restart container
docker compose -f docker/docker-compose.yaml restart runtime

# CORRECT - Connect and restart process inside container
docker compose -f docker/docker-compose.yaml exec runtime pkill -f "emmett serve"
# Process will auto-restart via entrypoint or supervisor
```

**Example - Running tests:**
```bash
# CORRECT - Use exec with running container
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/tests.py -v
```

**Why this matters:** Docker containers maintain persistent connections, database pools, and state. Restarting containers breaks these connections and wastes time.

---

## 🐘 CRITICAL: Never Drop the Database

**⚠️ DO NOT DROP OR RECREATE DATABASES ⚠️**

This is a **CRITICAL RULE**:
- ❌ **NEVER** run `DROP DATABASE` in test setup
- ❌ **NEVER** recreate databases between test runs
- ❌ **NEVER** terminate database connections to drop databases

**✅ Database is PERSISTENT:**
- ✅ The `bloggy_test` database persists between test runs
- ✅ Tables and schema persist (managed by migrations)
- ✅ Clean up test DATA, not the database itself

**✅ Correct approach:**
- ✅ Check if database exists, create only if missing
- ✅ Run migrations to ensure schema is up to date
- ✅ Clean up test data (DELETE rows) in teardown
- ✅ Preserve database structure and connections

**Example - Test Setup:**
```python
# WRONG - Dropping and recreating database
cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
cursor.execute(f"CREATE DATABASE {db_name}")

# CORRECT - Use existing database, create only if missing
cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
if not cursor.fetchone():
    cursor.execute(f"CREATE DATABASE {db_name}")
```

**Example - Test Teardown:**
```python
# WRONG - Dropping database
DROP DATABASE bloggy_test

# CORRECT - Clean up test data only
DELETE FROM users WHERE email LIKE '%@example.com%'
```

**Why this matters:** Persistent databases maintain connections, indexes, and state. Dropping databases breaks connections from the always-running Docker containers and wastes time recreating schema.

---

## 🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨

**⚠️ USING MOCKS, STUBS, OR TEST DOUBLES IS ILLEGAL IN THIS REPOSITORY ⚠️**

This is a **ZERO-TOLERANCE POLICY**:
- ❌ **FORBIDDEN**: `unittest.mock`, `Mock()`, `MagicMock()`, `patch()`
- ❌ **FORBIDDEN**: `pytest-mock`, `mocker` fixture
- ❌ **FORBIDDEN**: Any mocking, stubbing, or test double libraries
- ❌ **FORBIDDEN**: Fake in-memory databases or fake HTTP responses
- ❌ **FORBIDDEN**: Simulated external services or APIs

**✅ ONLY REAL INTEGRATION TESTS ARE ALLOWED:**
- ✅ Real database operations with actual SQL
- ✅ Real HTTP requests through test client
- ✅ Real browser interactions with Chrome DevTools MCP
- ✅ Real external service calls (or FAIL tests if unavailable)

**Why this matters:** Mocked tests pass but hide real bugs. Integration tests catch actual issues before production.

---

## 🚨 CRITICAL POLICY: NO SKIPPING TESTS ALLOWED 🚨

**⚠️ SKIPPING TESTS IS ILLEGAL IN THIS REPOSITORY ⚠️**

This is a **ZERO-TOLERANCE POLICY**:
- ❌ **FORBIDDEN**: `@pytest.mark.skip` or `@pytest.mark.skipif` decorators
- ❌ **FORBIDDEN**: `pytest.skip()` calls in tests or fixtures
- ❌ **FORBIDDEN**: Commenting out tests to avoid failures

**✅ TESTS MUST EITHER RUN OR FAIL:**
- ✅ Use `pytest.fail()` with clear error message if dependencies unavailable
- ✅ Configure Docker environment with all dependencies
- ✅ Tests either run successfully or fail with actionable message

**Example:**
```python
# ❌ WRONG - Skipping test (ILLEGAL)
@pytest.mark.skipif(not HAS_CHROME, reason="Chrome not available")
def test_ui():
    pass

# ✅ CORRECT - Failing with clear message
@pytest.fixture
def chrome():
    if not HAS_CHROME:
        pytest.fail("Chrome MCP not available. Configure Docker environment properly.")
    return get_chrome()
```

---

## 🚨 CRITICAL POLICY: NEVER DROP THE DATABASE 🚨

**⚠️ DROPPING THE DATABASE IS STRICTLY FORBIDDEN ⚠️**

This is a **ZERO-TOLERANCE POLICY**:
- ❌ **FORBIDDEN**: `DROP DATABASE` commands
- ❌ **FORBIDDEN**: `emmett migrations reset` or similar destructive operations
- ❌ **FORBIDDEN**: Deleting database files or volumes
- ❌ **FORBIDDEN**: Any operation that destroys existing data

**✅ SAFE DATABASE OPERATIONS:**
- ✅ Run migrations forward: `emmett migrations up`
- ✅ Create new tables via migrations
- ✅ Add columns via migrations
- ✅ Clean up test data in tests (DELETE records, not DROP tables)
- ✅ Truncate specific tables if needed (TRUNCATE, not DROP)

**Why this matters:** The database contains persistent state and production data. Dropping it causes irreversible data loss and breaks the development environment. Use migrations to evolve the schema forward.

---

## ⚡ Quick Summary

**This is an Emmett Framework application**

**DO:**
- ✅ Use Docker for running and testing (all dependencies pre-configured)
- ✅ Work with Emmett patterns (app.py, routes, ORM models)
- ✅ Reference Emmett documentation in `/emmett_documentation/`
- ✅ Write REAL integration tests with actual database changes
- ✅ Test real UI with Chrome DevTools MCP
- ✅ Build Tailwind CSS before running (`npm run build:css` in runtime/)
- ✅ Run type checking with `./run_type_check.sh` (Pyright)

**NEVER:**
- 🚫 Drop the database or run destructive database operations
- 🚫 Mock database calls, HTTP requests, or external services
- 🚫 Skip tests - they must either run or fail with clear messages
- 🚫 Use unittest.mock, pytest-mock, or any mocking libraries

---

## 📚 Emmett Framework Documentation

The `emmett_documentation/` directory contains comprehensive documentation for the Emmett web framework.

**Quick Reference**: See `emmett_documentation/documentation_summary.md` for a complete table of contents.

**Key areas**: ORM patterns, routing, authentication, forms, templates, WebSockets, caching, and deployment.

---

## Project Structure

```
runtime/                 # Main application directory
├── app.py              # Main Emmett application
├── models/             # ORM models
├── migrations/         # Database migrations
├── templates/          # Renoir templates
└── static/            # Static files (CSS, JS, images)

integration_tests/     # Integration tests (NO MOCKING)
├── conftest.py        # Test configuration and fixtures
├── tests.py           # Main application tests
└── test_*.py          # Specific test modules

documentation/         # Project documentation
docker/                # Docker configuration
emmett_documentation/  # Emmett framework docs
hooks/                 # Git hooks for code quality
setup/                 # Setup scripts
```

---

## Development Commands

### Using Docker (Recommended)

**⚠️ IMPORTANT: Always use Docker. It has all dependencies pre-configured.**

**📋 WORKFLOW: Check if Docker is Running First**

Before running Docker commands, check if containers are already running:

```bash
# Check if runtime container is running
docker compose -f docker/docker-compose.yaml ps runtime

# If runtime is NOT running, start it:
docker compose -f docker/docker-compose.yaml up runtime -d

# If runtime IS running, use exec commands directly
```

**Common Docker Commands:**

```bash
# Start the application (if not already running)
docker compose -f docker/docker-compose.yaml up runtime

# Run in detached mode (recommended for testing)
docker compose -f docker/docker-compose.yaml up runtime -d

# Run tests (ASSUMES Docker is already running - will fail if not)
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/ -v

# Run migrations (ASSUMES Docker is already running)
docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up

# View logs
docker compose -f docker/docker-compose.yaml logs -f runtime

# Stop containers
docker compose -f docker/docker-compose.yaml down
```

Application available at: **http://localhost:8081/**

### Local Development (Fallback Only)

```bash
# Run the application
./run_bloggy.sh

# Run tests
./run_tests.sh

# Database migrations
cd runtime && uv run emmett migrations up
```

---

## Git Hooks

Git hooks validate models before commits.

```bash
# Install git hooks (one-time setup)
./hooks/install.sh

# Validate models directly
cd runtime && python validate_models.py --all
```

**What the hook does:**
- ✅ Runs automatically on `git commit`
- ✅ Validates Emmett models for anti-patterns
- ✅ **Blocks commits** with model errors
- ✅ Allows commits with warnings

---

## Emmett Application Patterns

### Model Definition

```python
from emmett.orm import Model, Field

class Post(Model):
    title = Field.string()
    text = Field.text()
    author = Field.belongs_to('user')
    
    validation = {
        'title': {'presence': True, 'len': {'range': (3, 250)}},
        'text': {'presence': True}
    }
```

### Route Definition

```python
@app.route('/')
async def index():
    posts = Post.all().select()
    return {'posts': posts}
```

### Authentication

```python
from emmett.tools import requires

@app.route('/admin')
@requires(lambda: auth.user is not None, url('login'))
async def admin():
    return {}
```

---

## Type Checking

This project uses **Pyright** for static type checking.

```bash
# Run type checks
./run_type_check.sh

# Check specific files
./run_type_check.sh runtime/app.py runtime/models/
```

**Expected:** ~89 errors, ~150 warnings (mostly ORM-related, which is expected for pyDAL's dynamic features)

**Best practices:**
- Use `type: ignore[attr-defined]` for ORM field access
- Use `dict[str, Any]` for route return types
- Add type hints to new functions

---

## Testing

**⚠️ IMPORTANT: Always use Docker for testing to ensure consistent environment.**

**🔍 CHECK DOCKER STATUS BEFORE RUNNING TESTS:**

```bash
# Step 1: Check if Docker runtime is running
docker compose -f docker/docker-compose.yaml ps runtime

# Step 2: If NOT running, start it first
docker compose -f docker/docker-compose.yaml up runtime -d

# Step 3: Wait a few seconds for services to initialize
sleep 5

# Step 4: Now run tests
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/ -v
```

**❌ COMMON ERROR:** Running `pytest` with `exec` when Docker is not running will fail with "service not running" error.

**✅ SOLUTION:** Always start Docker with `up -d` before using `exec` commands.

### Running Tests

```bash
# Run all tests in Docker (ASSUMES Docker is already running)
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/ -v

# Run with coverage
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/ --cov=runtime --cov-report=term-missing

# Run specific test
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/ -k test_name
```

### Integration Testing Philosophy

**This project uses REAL integration tests ONLY. Mocked unit tests are FORBIDDEN.**

**Core Principles:**

1. **NO MOCKING - EVER**
   - Test against real database
   - Test complete request/response cycle
   - Verify actual database state changes

2. **NO SKIPPING TESTS - EVER**
   - Tests must either run or fail with clear error messages
   - Configure Docker environment with all dependencies

3. **REAL DATABASE CHANGES**
   - Tests create, update, and delete real database records
   - Verify database state before and after operations
   - Test actual SQL queries and constraints

4. **REAL UI TESTING WITH CHROME DEVTOOLS**
   - Use MCP Chrome DevTools for UI integration tests
   - Test actual browser interactions
   - Verify real DOM elements and page content

### Integration Test Example

```python
# ✅ CORRECT - Real integration test
def test_create_post_integration(logged_client):
    """Test post creation with real database"""
    # Make real HTTP request
    response = logged_client.post('/api/posts', data={
        'title': 'Integration Test Post',
        'text': 'Real content'
    })
    
    # Verify HTTP response
    assert response.status == 201
    
    # Verify REAL database state changed
    with db.connection():
        post = Post.where(lambda p: p.title == 'Integration Test Post').first()
        assert post is not None
        assert post.text == 'Real content'
    
    # Cleanup
    with db.connection():
        post.delete_record()
```

### Chrome DevTools MCP Tools

When testing UI, use these MCP tools:

- `navigate_page(url)` - Navigate to real page
- `take_snapshot()` - Get real DOM snapshot with UIDs
- `click(uid)` - Click real element
- `fill(uid, value)` - Fill real form field
- `take_screenshot(filePath)` - Capture real screenshot
- `wait_for(text, timeout)` - Wait for real content
- `list_network_requests()` - Get real network activity

See `documentation/README_UI_TESTING.md` for complete UI testing guide.

---

## Key Dependencies

- **Emmett 2.5.0+**: Web framework
- **pyDAL**: ORM system
- **Renoir**: Template engine
- **pytest**: Testing framework
- **Pyright**: Type checking
- **Chrome DevTools MCP**: UI testing (via MCP server)
- **Bugsink**: Error tracking (Sentry-compatible)

---

## Architecture Notes

Emmett follows these patterns:

1. **Single Application File**: Core app definition in `app.py`
2. **Decorator-Based Routing**: Routes defined with `@app.route()` decorator
3. **pyDAL ORM**: Database models with automatic validation
4. **Pipeline System**: Request processing through middleware
5. **Renoir Templates**: Python-like template syntax
6. **Built-in Tools**: Auth, sessions, caching, forms all included

---

## Monitoring and Observability

**Error Tracking (Bugsink):**
- URL: http://localhost:8000
- Credentials: admin:admin_password
- Sentry-compatible API

**Metrics (Prometheus):**
- Application metrics: http://localhost:8081/metrics
- Prometheus UI: http://localhost:9090
- Grafana dashboards: http://localhost:3000 (admin:admin)

**API Documentation (Swagger):**
- Interactive docs: http://localhost:8081/api/docs
- OpenAPI spec: http://localhost:8081/api/openapi.json

---

## Documentation Structure

All project documentation is organized in `/documentation/`:

- **agents.md** - This file - AI agent instructions
- **README_UI_TESTING.md** - UI testing with Chrome DevTools MCP
- **README_TAILWIND_BUILD.md** - Tailwind CSS setup
- **README_CHROME_TESTING.md** - Chrome DevTools patterns
- **bugsink-setup.md** - Error tracking configuration
- **whitepaper.md** - Project architecture

---

## Learn More

- [Emmett Framework Documentation](https://emmett.sh/docs)
- [Emmett GitHub](https://github.com/emmett-framework/emmett)
- Local Emmett docs: `/emmett_documentation/`
- Tutorial: `/emmett_documentation/docs/tutorial.md`
- ORM Guide: `/emmett_documentation/docs/orm/`
- Project docs: `/documentation/`
