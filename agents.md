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

## ⚡ Quick Summary

**This is an Emmett Framework application **

- ✅ **DO**: Use Docker for running and testing the application
- ✅ **DO**: Work with Emmett patterns (app.py, routes, ORM models)
- ✅ **DO**: Reference Emmett documentation in `/emmett_documentation/`
- ✅ **DO**: Create application code in `runtime/` directory
- ✅ **DO**: Use Emmett's pyDAL ORM for database operations
- ✅ **DO**: Write REAL integration tests with actual database changes
- ✅ **DO**: Test real UI with Chrome DevTools MCP (not Selenium)
- ✅ **DO**: Build Tailwind CSS before running (`npm run build:css` in runtime/)
- ⚠️ **PREFERRED**: Always use Docker commands over local development scripts
- ❌ **NEVER**: Mock database calls, HTTP requests, or external services in tests

---

## 📚 Emmett Framework Documentation

The `emmett_documentation/` directory contains comprehensive documentation for the Emmett web framework.

**Location**: `/emmett_documentation/`

**Quick Reference**: See `emmett_documentation/documentation_summary.md` for a complete table of contents with descriptions of all available documentation.

**Key Documentation Areas:**

1. **Getting Started**
   - Installation, Quickstart, Tutorial
   - Building a complete micro-blogging application example

2. **Application Structure**
   - Application and module organization patterns
   - Routing with decorators and variable paths
   - Best practices for scaling applications

3. **Request/Response Handling**
   - Request object (headers, cookies, body, files)
   - Response customization (status, headers, streaming)
   - Pipeline system for request processing

4. **Templates and Output**
   - Renoir templating engine
   - HTML generation without templates
   - Service decorators for JSON/XML APIs

5. **Forms and Validation**
   - Form class with Field objects
   - ModelForm for database-backed forms
   - Built-in validators (email, URL, numeric, custom)

6. **Database and ORM**
   - ORM overview (based on pyDAL)
   - Database connections and configuration
   - Models with field types and validation
   - Relations (belongs_to, has_many, has_one)
   - CRUD operations and queries
   - Migrations with up/down methods
   - Callbacks (before/after insert/update/delete)
   - Scopes for reusable query filters
   - Virtuals and computed attributes
   - Advanced patterns (inheritance, polymorphism)

7. **Authentication and Security**
   - Auth module with login/logout/registration
   - Permission systems and group management
   - @requires decorator for protected routes

8. **Sessions and State**
   - Cookie-based, file-based, and Redis-backed sessions
   - Session configuration and expiration

9. **Real-Time Communication**
   - WebSocket routing and handling
   - Bidirectional messaging patterns

10. **Internationalization**
    - Multi-language support with T() translator
    - Translation file organization

11. **Performance**
    - Caching strategies (RAM, Disk, Redis, Valkey)
    - Cache decorators and manual operations

12. **Utilities**
    - Mailer for sending emails
    - Extensions system for custom functionality

13. **Development and Debugging**
    - CLI commands and custom commands
    - Logging configuration
    - Testing with test client

14. **Deployment**
    - Production server configuration
    - Docker deployment
    - Upgrading between versions

**When to Reference:**
- When implementing ORM patterns, relationships, or migrations
- When designing API structures or REST endpoints
- When looking for authentication/authorization patterns
- When implementing real-time features or WebSocket support
- When setting up forms and validation logic
- When organizing application structure and modules
- When implementing caching or performance optimizations
- When designing testing strategies

**How to Use:**
- Consult `documentation_summary.md` for an overview of all topics
- Read specific documentation files in `docs/` or `docs/orm/` for detailed guidance
- Follow Emmett patterns and conventions

---

## Project Overview

This project contains an Emmett-based web application framework with example applications demonstrating Emmett's capabilities.

**Key Features:**
- Emmett web framework (2.5.0+)
- pyDAL ORM for database operations
- Renoir templating engine
- Built-in authentication and authorization
- WebSocket support
- RESTful API capabilities
- Docker deployment

## Project Structure

```
runtime/                 # Main application directory
├── app.py              # Main Emmett application
├── migrations/         # Database migrations
├── databases/          # SQLite database files
├── templates/          # Renoir templates
│   ├── layout.html    # Base template
│   ├── index.html     # Home page
│   └── auth/          # Authentication templates
├── static/            # Static files (CSS, JS, images)
└── tests.py           # Application tests

docker/                # Docker configuration
├── docker-compose.yaml
└── Dockerfile

emmett_documentation/  # Emmett framework documentation
└── docs/              # Detailed documentation

setup/                 # Setup scripts
└── setup.sh           # Environment setup
```

## Development Commands

### Using Docker (Recommended - Use This!)

**⚠️ IMPORTANT: Always use Docker for running and testing. The Docker environment has all dependencies pre-configured including Gemini CLI, Python packages, and system libraries.**

```bash
# Rebuild container (after Dockerfile changes)
docker compose -f docker/docker-compose.yaml build runtime

# Start the application
docker compose -f docker/docker-compose.yaml up runtime

# Run in detached mode
docker compose -f docker/docker-compose.yaml up runtime -d

# View logs
docker compose -f docker/docker-compose.yaml logs -f runtime

# Stop the service
docker compose -f docker/docker-compose.yaml down

# Run commands in container
docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py

# Run tests in Docker
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -v

# Access Gemini CLI in container
docker compose -f docker/docker-compose.yaml exec runtime gemini --version
```

Application will be available at: **http://localhost:8081/**

### Local Development (Fallback Only)

```bash
# Run the application
./run_bloggy.sh

# Or manually
cd runtime
uv run emmett develop

# Run tests
./run_tests.sh

# Or manually
cd runtime
uv run pytest tests.py

# Database migrations
cd runtime
uv run emmett migrations generate
uv run emmett migrations up
uv run emmett migrations down

# Setup admin user
cd runtime
uv run emmett setup
```

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
from emmett import App, request

app = App(__name__)

@app.route('/')
async def index():
    posts = Post.all().select()
    return {'posts': posts}

@app.route('/post/<int:id>')
async def show_post(id):
    post = Post.get(id)
    return {'post': post}
```

### Authentication

```python
from emmett.tools import requires

@app.route('/admin')
@requires(lambda: auth.user is not None, url('login'))
async def admin():
    return {}
```

### Forms

```python
from emmett.orm import Field
from emmett.tools import Form

@app.route('/new', methods=['get', 'post'])
async def new_post():
    form = await Form.from_model(Post)
    if form.accepted:
        # form data is validated and saved
        redirect(url('index'))
    return {'form': form}
```

## Testing

**⚠️ IMPORTANT: Always use Docker for testing to ensure consistent environment.**

### Docker Testing (Recommended)

```bash
# Run all tests in Docker
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py

# Run with verbose output
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -v

# Run with coverage
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py --cov=runtime --cov-report=term-missing

# Run specific test
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -k test_name

# Run tests with detailed output
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -vv
```

### Local Testing (Fallback Only)

```bash
# Run all tests locally
./run_tests.sh

# Run with verbose output
./run_tests.sh -v

# Run without coverage
./run_tests.sh --no-coverage

# Run specific test
cd runtime
uv run pytest tests.py -k test_name
```

## Integration Testing Philosophy

**⚠️ CRITICAL: This project uses REAL integration tests, not mocked unit tests.**

### Core Principles

1. **NO MOCKING - EVER**
   - ❌ **NEVER** mock database calls
   - ❌ **NEVER** mock HTTP requests
   - ❌ **NEVER** mock external services
   - ❌ **NEVER** use test doubles, stubs, or mocks
   - ✅ **ALWAYS** test against real database
   - ✅ **ALWAYS** test complete request/response cycle
   - ✅ **ALWAYS** verify actual database state changes

2. **REAL DATABASE CHANGES**
   - Tests must create, update, and delete real database records
   - Use test database or isolated database for tests
   - Verify database state before and after operations
   - Test actual SQL queries, not simulated behavior
   - Test database relationships and constraints for real

3. **REAL UI TESTING WITH CHROME DEVTOOLS**
   - Use MCP Chrome DevTools for UI integration tests
   - Test actual browser interactions (clicks, form fills, navigation)
   - Verify real DOM elements and page content
   - Test JavaScript execution in real browser
   - Capture screenshots and snapshots for validation
   - Test actual network requests and responses

### Integration Test Structure

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
        assert post.user == logged_client.user_id
    
    # Cleanup (also real database operation)
    with db.connection():
        post.delete_record()

# ❌ WRONG - Mocked test (DO NOT DO THIS)
def test_create_post_mocked(mock_db):  # ❌ NO MOCKS!
    """This is NOT how we test"""
    mock_db.create.return_value = Mock(id=1)  # ❌ NEVER MOCK
    # ... rest of fake test
```

### UI Testing with Chrome DevTools MCP

```python
# ✅ CORRECT - Real browser UI test
async def test_login_ui_real_browser():
    """Test login with real Chrome browser"""
    from mcp_chrome_devtools import navigate_page, take_snapshot, fill, click
    
    # Navigate to real page
    await navigate_page(url='http://localhost:8081/auth/login')
    
    # Take snapshot of real DOM
    snapshot = await take_snapshot()
    
    # Find real form fields by UID from snapshot
    email_field = find_element_by_label(snapshot, 'Email')
    password_field = find_element_by_label(snapshot, 'Password')
    
    # Fill real form fields
    await fill(uid=email_field.uid, value='doc@emmettbrown.com')
    await fill(uid=password_field.uid, value='fluxcapacitor')
    
    # Click real submit button
    submit_button = find_element_by_text(snapshot, 'Login')
    await click(uid=submit_button.uid)
    
    # Verify real navigation happened
    await wait_for(text='Welcome')
    
    # Verify real database session was created
    with db.connection():
        session = Session.where(lambda s: s.user_email == 'doc@emmettbrown.com').first()
        assert session is not None

# ❌ WRONG - Mocked UI test (DO NOT DO THIS)
def test_login_ui_mocked(mock_browser):  # ❌ NO MOCKS!
    """This is NOT how we test UI"""
    mock_browser.navigate.return_value = True  # ❌ NEVER MOCK
    # ... rest of fake test
```

### What to Test (Integration Level)

#### ✅ DO Test:
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

#### ❌ DON'T Test (Use Integration, Not Mocks):
- **Isolated function logic** → Test via real HTTP endpoint instead
- **Database queries in isolation** → Test via complete route handlers
- **Template rendering alone** → Test by requesting page and verifying HTML
- **Form validation alone** → Test by submitting real forms

### Test Data Management

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

# ❌ WRONG - Fake in-memory test data (DO NOT DO THIS)
@pytest.fixture()
def mock_posts():  # ❌ NO MOCKS!
    """DO NOT create fake test data"""
    return [Mock(id=1, title='Fake'), Mock(id=2, title='Fake')]  # ❌ NEVER
```

### Chrome DevTools MCP Tools Available

When testing UI, use these MCP tools:

- `navigate_page(url)` - Navigate to real page
- `take_snapshot()` - Get real DOM snapshot with UIDs
- `click(uid)` - Click real element
- `fill(uid, value)` - Fill real form field
- `fill_form(elements)` - Fill multiple form fields
- `hover(uid)` - Hover over real element
- `take_screenshot(filePath)` - Capture real screenshot
- `wait_for(text, timeout)` - Wait for real content
- `list_network_requests()` - Get real network activity
- `list_console_messages()` - Get real console logs

See `runtime/README_UI_TESTING.md` for complete UI testing guide.

### Test Database Isolation

```python
# Test database configuration
@pytest.fixture(scope='module', autouse=True)
def _prepare_db(request):
    """Setup real test database"""
    with db.connection():
        # Run real migrations
        migration = generate_runtime_migration(db)
        migration.up()
        
        # Create real admin user
        setup_admin()
    
    yield
    
    # Real teardown
    with db.connection():
        # Delete real data
        User.all().delete()
        Post.all().delete()
        Comment.all().delete()
        auth.delete_group('admin')
        
        # Rollback real migrations
        migration.down()
```

### Coverage Requirements

- **95%+ line coverage** - All code paths tested with real requests
- **90%+ branch coverage** - All conditionals tested with real data
- **100% endpoint coverage** - Every route tested with real HTTP
- **100% database operations** - Every CRUD operation tested for real

### Running Integration Tests

```bash
# Run all integration tests (real database, real HTTP)
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py

# Run with coverage (measure real code execution)
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py --cov=app --cov-report=term-missing

# Run UI tests (real browser)
docker compose -f docker/docker-compose.yaml exec runtime pytest ui_tests.py

# Run specific integration test
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -k test_api_posts_create
```

### Why No Mocking?

**Mocking creates false confidence:**
- ✗ Mocked tests pass but real code fails
- ✗ Mocks don't catch integration issues
- ✗ Mocks don't test actual database behavior
- ✗ Mocks don't test real serialization/deserialization
- ✗ Mocks don't test real error handling
- ✗ Mocks become outdated when implementation changes

**Integration tests provide real confidence:**
- ✓ Tests fail when real code has bugs
- ✓ Tests catch integration issues between components
- ✓ Tests verify actual database behavior and constraints
- ✓ Tests verify real API contracts
- ✓ Tests verify real error handling
- ✓ Tests verify actual user experience

**Example of mock hiding bug:**
```python
# ❌ Mocked test passes but hides bug
def test_create_post_mocked(mock_db):
    mock_db.create.return_value = Mock(id=1)  # ❌ Always succeeds
    # Test passes but doesn't catch that Post.create() has a bug
    
# ✅ Real test catches bug
def test_create_post_integration(client):
    response = client.post('/api/posts', data={'title': '', 'text': 'content'})
    # Real test FAILS because title validation is broken
    # We catch the bug before production!
```

### When Tests Are Slow

If integration tests become slow:
- ✅ Use module-scoped fixtures for expensive setup (database, admin user)
- ✅ Use function-scoped fixtures for test-specific data
- ✅ Parallelize with pytest-xdist if needed
- ✅ Optimize database operations (bulk creates)
- ❌ **NEVER** switch to mocking to make tests faster

**Speed is not a reason to compromise test quality.**

## Key Dependencies

- **Emmett 2.5.0+**: Web framework
- **pyDAL**: ORM system
- **Renoir**: Template engine
- **pytest**: Testing framework
- **coverage**: Test coverage
- **granian**: ASGI server
- **Chrome DevTools MCP**: UI testing (via MCP server)

## Environment & Configuration

Emmett applications use a simple configuration pattern:

```python
# In app.py
from emmett import App

app = App(__name__)
app.config.url_default_namespace = "main"
app.config.auth.single_template = True
# ... more config
```

Environment-specific settings can be handled via environment variables or config files.

## Architecture Notes

Emmett follows these patterns:

1. **Single Application File**: Core app definition in `app.py`
2. **Decorator-Based Routing**: Routes defined with `@app.route()` decorator
3. **pyDAL ORM**: Database models with automatic validation
4. **Pipeline System**: Request processing through middleware
5. **Renoir Templates**: Python-like template syntax
6. **Built-in Tools**: Auth, sessions, caching, forms all included

## Important Notes

- **🐳 USE DOCKER**: Always use Docker for running and testing - it has all dependencies pre-configured
- The project uses Python 3.9+ (3.13+ recommended)
- Emmett uses pyDAL for ORM 
- Migrations are managed via `emmett migrations` command
- Templates use Renoir syntax (similar to Django templates but with differences)
- Authentication uses Emmett's built-in `Auth` module
- WebSocket support is built-in
- Docker environment includes:
  - Gemini CLI for AI assistance
  - All Python dependencies from requirements.txt
  - System libraries (gcc, g++, Node.js)
  - Consistent environment across all development machines


## Example Application

The `runtime/` directory contains "Bloggy", a complete micro-blogging application demonstrating:
- User authentication and registration
- Admin-only content creation
- Blog posts with comments
- Form handling and validation
- Template inheritance
- Database relationships

See `runtime/README.md` for detailed documentation on the example application.

## Reference vs Implementation

- **Emmett Documentation** (`/emmett_documentation/`): Reference material
- **Runtime Application** (`/runtime/`): Working implementation
- **Setup Scripts** (`/setup/`): Environment setup helpers
- **Docker Config** (`/docker/`): Container deployment

## Learn More

- [Emmett Framework Documentation](https://emmett.sh/docs)
- [Emmett GitHub](https://github.com/emmett-framework/emmett)
- Local Emmett docs: `/emmett_documentation/`
- Tutorial: `/emmett_documentation/docs/tutorial.md`
- ORM Guide: `/emmett_documentation/docs/orm/`
