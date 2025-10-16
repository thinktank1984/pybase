# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- **Docker mode (default)**: `./run_bloggy.sh` or `./run_bloggy.sh --docker`
- **Local mode**: `./run_bloggy.sh --local`
- **Docker foreground**: `./run_bloggy.sh --foreground`
- **Local development server runs on**: http://localhost:8000
- **Docker services**: Runtime App (http://localhost:8081), Bugsink (http://localhost:8000), Prometheus (http://localhost:9090), Grafana (http://localhost:3000)
Never rm or drop the database
it is illegal to remove the database
no mockup tests
illegal to create or run mockup tests
no inmemeory tests
Never change /workspaces/pybase/inject_meta_data_into_context.json
it is illegal to modify the metadata injection file

### Testing
- **Run all tests**: `./run_tests.sh` (runs 8 test suites separately by default)
- **Run app tests only**: `./run_tests.sh --app`
- **Run Chrome UI tests**: `./run_tests.sh --chrome`
- **Run specific test pattern**: `./run_tests.sh -k test_api`
- **Verbose tests**: `./run_tests.sh -v` or `./run_tests.sh -vv`
- **Stop on first failure**: `./run_tests.sh -x`
- **Test coverage**: Enabled by default, generates HTML report at `runtime/htmlcov/index.html`

### Type Checking
- **Docker mode (default)**: `./run_type_check.sh`
- **Local mode**: `./run_type_check.sh --local`
- **Check specific files**: `./run_type_check.sh runtime/app.py`
- **Configuration**: Uses `setup/pyrightconfig.json`

### Database
- **Local SQLite Database**: `/workspaces/pybase/runtime/databases/main.db` - Used for both development and testing
- **Environment variables**: `DATABASE_URL="sqlite://runtime/databases/main.db"` for development
- **Migrations**: Run automatically before tests with `../venv/bin/emmett migrations up`

## Architecture Overview

### Core Framework
- **Emmett Framework**: Python web framework similar to Flask/Django
- **Database**: Local SQLite Database
- **ORM**: Emmett's built-in ORM with model validation
- **Design Pattern**: Active Record pattern - models encapsulate both data and behavior

### Key Components

#### Database Layer
- `runtime/database_manager.py`: Database manager for SQLite database connection
- `runtime/models/`: All database models (User, Post, Comment, Role, Permission, OAuthAccount, OAuthToken)
- `runtime/models/seeders.py`: Database seeding functionality
- `runtime/validate_models.py`: Model validation for anti-patterns

#### Authentication & Authorization
- `runtime/auth/`: Complete authentication system
- OAuth providers: Google, GitHub, Microsoft, Facebook
- Token management and refresh
- Role-based access control (RBAC) with permissions
- `runtime/models/role/` and `runtime/models/permission/`: RBAC implementation

#### API & UI Generation
- `runtime/auto_routes.py`: Automatic REST API route generation
- `runtime/auto_ui_generator.py`: Automatic UI generation from models
- `runtime/openapi_generator.py`: OpenAPI specification generation
- `runtime/emmett_rest/`: REST framework implementation

### Auto-Generated Forms and Pages
Forms and pages are automatically generated from database models using the **Active Record pattern**:

**How it works:**
1. **Model introspection**: The `auto_ui_generator.py` analyzes model fields, relationships, and validation rules
2. **Dynamic form generation**: Creates appropriate form inputs based on field types (text, email, password, select, etc.)
3. **CRUD page generation**: Automatically creates Create, Read, Update, Delete pages for each model
4. **Template rendering**: Uses Emmett templates with Tailwind CSS for responsive UI

**Generation process:**
- Models define fields, relationships, and validation rules
- `auto_ui` decorator automatically registers UI routes
- Forms are generated dynamically with proper validation
- Pages are created using templates in `runtime/templates/`
- REST API endpoints are created alongside UI pages

**Key files:**
- `runtime/auto_ui_generator.py`: Core UI generation logic
- `runtime/templates/`: HTML templates for auto-generated pages
- Model files in `runtime/models/`: Define the structure and validation rules

#### Frontend
- Templates in `runtime/templates/`
- Tailwind CSS for styling (built with npm)
- Auto-generated UI components based on models

### Project Structure
```
runtime/                  # Main application code
├── app.py               # Application entry point
├── database_manager.py  # Database singleton
├── models/              # Data models
├── auth/                # Authentication system
├── templates/           # HTML templates
├── static/              # Static assets
└── databases/           # Local SQLite database files

integration_tests/       # Test suites
├── tests.py                    # Main integration tests
├── test_oauth_real.py          # OAuth integration tests
├── test_roles_integration.py   # RBAC tests
├── test_ui_chrome_real.py      # Chrome DevTools UI tests
└── [other test files]

docker/                  # Docker configuration
setup/                   # Setup and configuration files
```

### Testing Strategy
- **8 test suites** covering different aspects of the application
- **Integration tests**: Real local SQLite database and API testing
- **Chrome DevTools tests**: Real browser automation
- **No mocking policy**: Tests use real services and databases (local SQLite)
- **Separate execution**: Each test suite runs independently with separate output files

### Default Credentials
- **Email**: doc@emmettbrown.com
- **Password**: fluxcapacitor

### Development Notes
- All tests run on the host machine (not in containers)
- Database migrations run automatically before tests
- Type checking uses Pyright with configuration in `setup/pyrightconfig.json`
- The application supports both Docker and local development modes
- Model validation runs automatically on startup to check for anti-patterns
- mem
- never remove functionaly without explicit instruction from the user