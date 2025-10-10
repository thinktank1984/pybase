# AGENTS.md - Critical Agent Instructions

This file provides guidance to AI agents (Claude Code, Gemini, etc.) when working with code in this repository.

---

## ⚡ Quick Summary

**Application code goes in `userapp/` - Framework code in `djangobase/` is READ-ONLY**

- ✅ **DO**: Create models in `userapp/models/` directory
- ✅ **DO**: Create tests in `userapp/tests/` directory
- ✅ **DO**: Auto-registration handles everything
- ❌ **DON'T**: Modify anything in `djangobase/` directory
- ❌ **DON'T**: Touch framework files unless explicitly requested
- ❌ **DON'T**: Add code to `djangobase/` (that's for framework only)

---

## 🚨 CRITICAL: Framework Protection Rules

### ⛔ MODIFYING `djangobase/` IS ILLEGAL

**The `djangobase/` directory is the FRAMEWORK. Changes to this directory are FORBIDDEN.**

**⚠️ ABSOLUTE RULES - VIOLATION IS NOT PERMITTED:**

1. **ILLEGAL**: Modifying any file in `djangobase/djangobase/` (framework core)
2. **ILLEGAL**: Modifying any file in `djangobase/config/` (framework configuration)
3. **ILLEGAL**: Modifying any file in `djangobase/djangobase/extensions/` (plugin system)
4. **ILLEGAL**: Changing `djangobase/pyproject.toml` or any dependencies
5. **ILLEGAL**: Adding, editing, or deleting ANY file in the `djangobase/` directory tree

**Exception:** ONLY modify framework if user explicitly says:
- "Update the framework..."
- "Modify djangobase core..."
- "Change the extensions plugin..."

**Why?** `djangobase/` is a framework, not an application. Any changes break all applications built on it. Treat it as read-only system code.

### ✅ WHERE TO ADD APPLICATION CODE

All application code goes in the `userapp/` directory:

```
/userapp/              ← YOUR APPLICATION (full control)
  ├── README.md        ← User app documentation
  │
  ├── models/          ← Place ALL your models here
  │   ├── __init__.py
  │   ├── articles.py  ← Example: Article model
  │   ├── products.py  ← Your Product model
  │   └── *.py         ← Add more models
  │
  └── tests/           ← Place ALL your tests here
      ├── __init__.py
      ├── conftest.py  ← Pytest configuration
      ├── test_articles.py
      └── test_*.py    ← Add more tests
```

**Clear Separation:**
```
djangobase/    ← FRAMEWORK (read-only, like Django itself)
userapp/       ← YOUR APP (your code, full control)
```

**Auto-Registration:**
- Models in `userapp/models/` are automatically discovered and registered
- Just inherit from `BaseActiveRecord` - that's it!
- No need to touch Django settings or apps
- No framework modifications needed

**Testing:**
- All application tests go in `userapp/tests/` directory
- Use pytest fixtures and Django test tools
- **Run application tests only**: `./run_tests.sh --phase3` (runs only userapp tests in Docker)
- **Run all tests**: `./run_tests.sh` (runs framework + application tests in Docker)
- Tests are automatically discovered and run by the test runner
- Framework tests are in `djangobase/tests/` (DO NOT MODIFY)
- **IMPORTANT**: All tests and app execution MUST use Docker - no local Python execution

**Test Runner:**
- The test runner (`./run_tests.sh`) automatically includes `userapp/tests/` directory
- Any new test file in `userapp/tests/test_*.py` will be automatically discovered
- No configuration needed - just create the file and run `./run_tests.sh`

### 📋 Development Workflow

**For Model Development:**
1. Create `.py` file in `userapp/models/` directory
2. Import `BaseActiveRecord` from `djangobase.extensions.models`
3. Define your model (inherit from `BaseActiveRecord`)
4. Run migrations: `just manage makemigrations && just manage migrate`
5. Done! API endpoints auto-generated at `/api/ext/<model_name>/`

**For Test Development:**
1. Create `test_*.py` file in `userapp/tests/` directory
2. Write tests using pytest and Django test tools
3. Run tests: `./run_tests.sh` (automatically runs in Docker and discovers all tests in `userapp/tests/`)
4. Done! No configuration or registration needed

**CRITICAL - Docker-Only Execution:**
- **ALL** commands MUST run in Docker containers
- **NEVER** run Python/Django commands directly on the host machine
- **NEVER** use `uv run` or direct Python execution outside containers
- Always use: `just manage <command>` for Django management commands
- Always use: `just shell` to access the container bash shell
- Always use: `./run_tests.sh` for all testing (handles Docker automatically)
- Always use: `just up` / `just down` to start/stop containers

**Example:**
```python
# userapp/models/products.py
from djangobase.extensions.models import BaseActiveRecord
from django.db import models

class Product(BaseActiveRecord):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

That's it. No framework changes needed.

**Extending Model Functionality:**
Models in `userapp/models/` should be kept **declarative and minimal**. Only include:

1. **Field Definitions**: Django model fields (CharField, IntegerField, ForeignKey, etc.)
2. **Decorator Attributes**: UI-element definitions, metadata decorators (e.g., `@admin.display`, field options)
3. **Method Decorators**: Decorators that modify behavior (e.g., `@route()`, `@property`, `@classmethod`, permission decorators)
4. **Method Overrides**: Override `BaseActiveRecord` or Django model methods ONLY (e.g., `save()`, `delete()`, `clean()`, `validate()`)
5. **Custom Route Definitions**: Use `@BaseActiveRecord.route()` decorator for custom API endpoints

**❌ DO NOT ADD:**
- Complex business logic in methods
- Helper functions or utility methods
- Data processing code
- External API calls
- Complex calculations (beyond simple properties)

**Keep models clean and declarative.** If you need business logic, use Django services, managers, or separate utility modules outside the model class.

**Example of Good Model Structure:**
```python
# userapp/models/products.py
from djangobase.extensions.models import BaseActiveRecord
from django.db import models

class Product(BaseActiveRecord):
    # 1. Field definitions
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    # 2. Simple properties (computed from fields)
    @property
    def display_price(self):
        return f"${self.price:.2f}"
    
    # 3. Method overrides (framework hooks)
    def validate(self):
        if self.price < 0:
            return {"price": "Price cannot be negative"}
        return None
    
    # 4. Custom routes (declarative)
    @BaseActiveRecord.route(method='GET', path='discounted')
    @classmethod
    def get_discounted(cls, request):
        return cls.objects.filter(price__lt=10)
```

**❌ Bad - Don't do this:**
```python
class Product(BaseActiveRecord):
    name = models.CharField(max_length=200)
    
    def calculate_complex_metrics(self):
        # Complex business logic - DON'T PUT THIS HERE
        result = self.fetch_external_data()
        processed = self.transform_data(result)
        return self.aggregate_results(processed)
```

### 🛡️ When Framework Updates ARE Allowed

Only modify `djangobase/` when user explicitly requests:
- "Update the framework to add feature X"
- "Modify the extensions plugin to support Y"
- "Add a new framework capability for Z"
- "Update djangobase dependencies"

**Always ask for confirmation before framework changes.**

---

## 📚 Reference Documentation

### Emmett Framework Documentation

The `emmett_documentation/` directory contains comprehensive documentation for the Emmett web framework, which provides reference patterns and architectural guidance for this Django-based project.

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
- Look for architectural patterns that can be adapted to Django/DRF
- Use ORM documentation as reference for database design patterns

**Important Note:** This is reference documentation only. Do not attempt to integrate the Emmett framework directly into this Django-based project. Use it for architectural inspiration and pattern guidance.

---

## Project Overview

DjangoBase is a Django-based PocketBase replacement - an API-centric, real-time, file-enabled authenticated platform. The project is built on Cookiecutter-Django and aims to provide feature parity with PocketBase while leveraging Django's ecosystem.

**Key Objectives:**
- Dynamic collections and fields (not yet implemented)
- REST API with Django REST Framework
- Real-time subscriptions via WebSockets
- File storage (S3/Azure/local)
- JWT authentication and role-based permissions
- OpenAPI documentation via drf-spectacular

## Project Structure

This is a Cookiecutter-Django project with the following key directories:

```
djangobase/               # Main Django project root
├── config/              # Project configuration (settings, urls, ASGI/WSGI)
│   ├── settings/       # Split settings (base.py, local.py, production.py, test.py)
│   ├── api_router.py   # DRF router for API endpoints
│   ├── asgi.py         # ASGI application with WebSocket support
│   └── websocket.py    # WebSocket handler (basic ping/pong implementation)
├── djangobase/          # Main app directory
│   ├── users/          # Custom user app (extends AbstractUser)
│   ├── static/         # Static files
│   ├── templates/      # Django templates
│   └── contrib/        # Django contrib customizations (e.g., sites migrations)
├── compose/             # Docker compose configuration files
├── .envs/              # Environment variable files for different environments
├── locale/             # Translation files
└── tests/              # Project-level tests
```

## Development Commands

All commands should be run from the `djangobase/` directory (the one containing `manage.py`).

### Using uv (preferred)

This project uses `uv` for Python package management:

```bash
# Run Django management commands
uv run python manage.py <command>

# Create superuser
uv run python manage.py createsuperuser

# Run development server
uv run python manage.py runserver

# Run migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Type checking
uv run mypy djangobase

# Run tests
uv run pytest

# Test with coverage
uv run coverage run -m pytest
uv run coverage html
uv run open htmlcov/index.html

# Run Celery worker (from djangobase/ directory)
uv run celery -A config.celery_app worker -l info

# Run Celery beat scheduler
uv run celery -A config.celery_app beat

# Run Celery worker with embedded beat (dev only)
uv run celery -A config.celery_app worker -B -l info
```

### Using Docker

Docker commands via justfile or docker compose:

```bash
# Using just (recommended - from repo root)
just build          # Build containers
just up             # Start containers
just down           # Stop containers
just logs           # View logs
just manage <cmd>   # Run manage.py commands in container
just shell          # Open bash in Django container

# Direct docker compose (alternative - requires COMPOSE_FILE env var)
docker compose -f djangobase/docker-compose.local.yml up
docker compose -f djangobase/docker-compose.local.yml run --rm django python ./manage.py <command>
```

### Code Quality

```bash
# Linting with Ruff
uv run ruff check .
uv run ruff format .

# Django template linting
uv run djlint djangobase/templates --reformat

# Pre-commit hooks
pre-commit run --all-files
```

## Architecture Details

### Settings Architecture

Settings are split across multiple files in `config/settings/`:
- `base.py` - Common settings for all environments
- `local.py` - Development settings (DEBUG=True, debug toolbar, etc.)
- `production.py` - Production settings (security, caching, etc.)
- `test.py` - Test-specific settings

Set via `DJANGO_SETTINGS_MODULE` environment variable (defaults to `config.settings.local`).

### ASGI and WebSocket Architecture

The project uses ASGI for async support with both HTTP and WebSocket protocols:

- **ASGI Application** (`config/asgi.py:application`): Routes requests based on scope type
  - `scope["type"] == "http"` → Django HTTP application
  - `scope["type"] == "websocket"` → WebSocket application
- **WebSocket Handler** (`config/websocket.py:websocket_application`): Currently implements basic ping/pong
  - Future: Real-time subscriptions for collection updates

### API Architecture

- **API Router** (`config/api_router.py`): Central DRF router
  - Currently registers: `UserViewSet`
  - Add new viewsets here for API endpoints
- **URL Structure**:
  - `/api/` - API base (routed to `config.api_router`)
  - `/api/auth-token/` - DRF token authentication
  - `/api/schema/` - OpenAPI schema (drf-spectacular)
  - `/api/docs/` - Swagger UI (admin only)

### Authentication

- **Backend**: Django Allauth with email-only login (no username)
- **API Auth**: Session authentication + Token authentication (DRF)
- **Password Hashing**: Argon2 (primary), PBKDF2, BCrypt (fallback)
- **User Model**: Custom user model at `djangobase.users.User`

### Celery Architecture

- **Broker**: Redis (configurable via `REDIS_URL`)
- **Result Backend**: Redis
- **Beat Scheduler**: Database-backed via `django-celery-beat`
- **Task Location**: Tasks should be defined in `<app>/tasks.py` (e.g., `djangobase/users/tasks.py`)
- **Important**: Run Celery commands from the `djangobase/` directory (same level as `manage.py`)

### Static and Media Files

- **Static Files**: Collected to `staticfiles/`, served via WhiteNoise
- **Media Files**: Uploaded to `djangobase/media/` (local) or cloud storage (S3/Azure/GCS)
- **Webpack**: Frontend assets built via Webpack, stats in `webpack-stats.json`

## Testing Strategy

- **Test Files**: Use `test_*.py` or `tests.py` naming convention
- **Test Settings**: Tests use `config.settings.test` (configured in `pyproject.toml`)
- **Database**: Tests use `--reuse-db` flag for faster runs
- **Factories**: User factories in `djangobase/users/tests/factories.py` (uses factory_boy)

## Key Dependencies

- **Django 5.2.7**: Main web framework
- **Django REST Framework 3.16.1**: API framework
- **drf-spectacular 0.28.0**: OpenAPI documentation
- **Django Allauth 65.12.0**: Authentication with MFA support
- **Celery 5.5.3**: Async task queue
- **Redis**: Celery broker and result backend
- **Uvicorn**: ASGI server
- **WhiteNoise**: Static file serving
- **django-storages**: Cloud storage support (S3, Azure, GCS)

## Environment Variables

Key environment variables (see `.envs/` directory):
- `DJANGO_SETTINGS_MODULE` - Which settings module to use
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection (default: `redis://redis:6379/0`)
- `DJANGO_SECRET_KEY` - Secret key for production
- `DJANGO_DEBUG` - Enable/disable debug mode
- `USE_DOCKER` - Set to "yes" when running in Docker

## Planned Features (Not Yet Implemented)

Based on the whitepaper (`specifications/whitepaper.md`):
- Dynamic Collection and FieldDef models
- Per-collection ACL/permission rules
- JWT authentication (djangorestframework-simplejwt)
- Real-time WebSocket subscriptions via Django Channels
- Role-based permissions
- Schema migration UI

## Important Notes

- The project uses Python 3.13
- All Django apps should be added to `LOCAL_APPS` in `config/settings/base.py`
- API viewsets should be registered in `config/api_router.py`
- Custom user model is `djangobase.users.User` (email-based, no username)
- ASGI is configured for both HTTP and WebSocket protocols
- Celery tasks must be run from the `djangobase/` directory
