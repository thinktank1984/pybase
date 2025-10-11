# AGENTS.md - Critical Agent Instructions

This file provides guidance to AI agents (Claude Code, Gemini, etc.) when working with code in this repository.

---

## ⚡ Quick Summary

**This is an Emmett Framework application **

- ✅ **DO**: Work with Emmett patterns (app.py, routes, ORM models)
- ✅ **DO**: Reference Emmett documentation in `/emmett_documentation/`
- ✅ **DO**: Create application code in `runtime/` directory
- ✅ **DO**: Use Emmett's pyDAL ORM for database operations

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
    - Caching strategies (RAM, Disk, Redis)
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

### Using Docker (Recommended)

```bash
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
```

Application will be available at: **http://localhost:8081/**

### Local Development

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

```bash
# Run all tests
./run_tests.sh

# Run with verbose output
./run_tests.sh -v

# Run without coverage
./run_tests.sh --no-coverage

# Run specific test
cd runtime
uv run pytest tests.py -k test_name
```

## Key Dependencies

- **Emmett 2.5.0+**: Web framework
- **pyDAL**: ORM system
- **Renoir**: Template engine
- **pytest**: Testing framework
- **coverage**: Test coverage
- **granian**: ASGI server

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

- The project uses Python 3.9+ (3.13+ recommended)
- Emmett uses pyDAL for ORM 
- Migrations are managed via `emmett migrations` command
- Templates use Renoir syntax (similar to Django templates but with differences)
- Authentication uses Emmett's built-in `Auth` module
- WebSocket support is built-in


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
