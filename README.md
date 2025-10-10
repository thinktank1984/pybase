# PyBase - Python Web Application Framework Collection

A comprehensive collection of Python web frameworks and applications, featuring DjangoBase (Django-based PocketBase alternative) and example applications demonstrating modern web development patterns.

## 📦 What's Included

### 1. DjangoBase (Main Application)
**Location**: `djangobase/`

A Django-based PocketBase replacement - an API-centric, real-time, file-enabled authenticated platform built on Cookiecutter-Django.

**Key Features:**
- REST API with Django REST Framework
- Real-time subscriptions via WebSockets
- File storage (S3/Azure/local)
- JWT authentication and role-based permissions
- OpenAPI documentation via drf-spectacular
- Docker-based development environment
- Auto-registration of models in `userapp/`

**Documentation**: See `agents.md` for comprehensive development guide

### 2. Bloggy (Example Application)
**Location**: `bloggy/`

A micro-blogging application built with the Emmett web framework, demonstrating authentication, database operations, and web application patterns.

**Key Features:**
- User authentication and authorization
- Admin-only post creation
- Comments system
- Database ORM with relationships
- Form handling and validation

**Documentation**: See `bloggy/README.md`

### 3. Emmett Framework Documentation
**Location**: `emmett_documentation/`

Comprehensive documentation for the Emmett web framework, providing reference patterns and architectural guidance.

**Quick Reference**: `emmett_documentation/documentation_summary.md`

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (Python 3.13+ recommended)
- **Docker & Docker Compose** (for DjangoBase)
- **uv** package manager (will be installed automatically)
- **just** command runner (optional, for easier Docker commands)

### Setup DjangoBase

```bash
# Run the interactive setup script
./setup/setup.sh

# Choose your setup mode:
# 1) Docker (recommended)
# 2) Local
# 3) Both

# Start the application (Docker mode)
./run.sh
# Or manually
just up

# Access the application
# http://localhost:8000/admin/
# http://localhost:8000/api/
# http://localhost:8000/api/docs/
```

### Setup Bloggy

```bash
# Run the Bloggy setup script
./setup/setup_bloggy.sh

# Start Bloggy
./run_bloggy.sh

# Access the application
# http://localhost:8000/
# Login: doc@emmettbrown.com / fluxcapacitor
```

## 📁 Project Structure

```
pybase/
├── agents.md                      # AI agent instructions (CRITICAL - READ FIRST)
├── README.md                      # This file
│
├── djangobase/                    # Main Django application (FRAMEWORK)
│   ├── config/                   # Django settings and configuration
│   ├── djangobase/               # Core Django app with extensions
│   ├── compose/                  # Docker compose files
│   └── pyproject.toml            # Python dependencies
│
├── userapp/                       # User application code (YOUR CODE HERE)
│   ├── models/                   # Place your Django models here
│   └── tests/                    # Place your tests here
│
├── bloggy/                        # Emmett example application
│   ├── app.py                    # Main Emmett app
│   ├── tests.py                  # Test suite
│   ├── templates/                # HTML templates
│   ├── static/                   # Static files
│   ├── migrations/               # Database migrations
│   ├── README.md                 # Bloggy documentation
│   └── run.sh                    # Quick start script
│
├── emmett_documentation/          # Emmett framework reference docs
│   ├── documentation_summary.md  # Table of contents
│   ├── docs/                     # Detailed documentation
│   └── README.md                 # Overview
│
├── setup/                         # Setup scripts and requirements
│   ├── setup.sh                  # DjangoBase setup
│   ├── setup_bloggy.sh           # Bloggy setup
│   └── requirements.txt          # Optional dependencies
│
├── documentation/                 # Project documentation
│   ├── whitepaper.md             # Project specifications
│   └── todo.md                   # Development tasks
│
├── justfile                       # Just command runner recipes
├── run.sh                         # Quick start for DjangoBase
└── run_tests.sh                  # Test runner
```

## 🛠️ Development Workflow

### DjangoBase Development

**IMPORTANT**: Application code goes in `userapp/` - Framework code in `djangobase/` is READ-ONLY

```bash
# Create a new model (in userapp/models/)
cd userapp/models
# Create your_model.py with BaseActiveRecord

# Run migrations
just manage makemigrations
just manage migrate

# Access your model's API
# Auto-generated at: /api/ext/<model_name>/

# Run tests
./run_tests.sh --docker

# View logs
just logs
```

See `agents.md` for detailed development guidelines.

### Bloggy Development

```bash
cd bloggy

# Start development server
uv run emmett develop

# Run tests
uv run pytest tests.py

# Generate migration
uv run emmett migrations generate

# Apply migrations
uv run emmett migrations up

# Interactive shell
uv run emmett shell
```

## 🧪 Testing

### DjangoBase Tests

```bash
# Run all tests in Docker (recommended)
./run_tests.sh --docker

# Run quick tests only
./run_tests.sh --docker --quick

# Run specific test phase
./run_tests.sh --docker --phase1  # Framework tests
./run_tests.sh --docker --phase3  # Userapp tests

# Local tests (requires local setup)
./run_tests.sh
```

### Bloggy Tests

```bash
cd bloggy
uv run pytest tests.py -v

# With coverage
uv run pytest tests.py --cov=app
```

## 📚 Key Commands

### DjangoBase (Docker)

```bash
just build          # Build Docker containers
just up             # Start all services
just down           # Stop all services
just logs           # View logs
just shell          # Open bash in Django container
just manage <cmd>   # Run Django management command
just services       # Start only support services (no Django)
```

### DjangoBase (Local)

```bash
cd djangobase
uv run python manage.py runserver
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run pytest
```

### Bloggy

```bash
cd bloggy
uv run emmett develop           # Start server
uv run emmett migrations up     # Run migrations
uv run emmett setup             # Setup admin user
uv run emmett shell             # Interactive shell
uv run pytest tests.py          # Run tests
```

## 🎯 Use Cases

### Use DjangoBase when you need:
- Full-featured Django backend with DRF
- PostgreSQL, Redis, Celery integration
- Docker-based production deployment
- OpenAPI documentation
- Complex permissions and authentication
- WebSocket support with Django Channels

### Use Bloggy/Emmett when you need:
- Lightweight web applications
- Simple, direct patterns
- Less boilerplate
- Single-file application structure
- Educational reference for web patterns

## 📖 Documentation

### Essential Reading

1. **Start here**: `agents.md` - Critical instructions for development
2. **DjangoBase**: `djangobase/README.md` - Django app documentation
3. **Bloggy**: `bloggy/README.md` - Emmett app documentation
4. **Emmett Reference**: `emmett_documentation/documentation_summary.md`
5. **Specifications**: `documentation/whitepaper.md`

### Key Concepts

- **Framework Separation**: `djangobase/` is READ-ONLY framework code
- **Application Code**: All your code goes in `userapp/`
- **Auto-Registration**: Models in `userapp/models/` are auto-discovered
- **Docker-First**: All commands run in Docker containers
- **Testing**: Comprehensive test coverage with pytest

## 🔧 Configuration

### DjangoBase

Configuration via environment variables in `.envs/` directory:
- `DJANGO_SETTINGS_MODULE` - Settings module to use
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection
- `DJANGO_SECRET_KEY` - Secret key for production
- `DJANGO_DEBUG` - Enable/disable debug mode
- `USE_DOCKER` - Set to "yes" when running in Docker

### Bloggy

Configuration in `bloggy/app.py`:
- Database connection (SQLite by default)
- Authentication settings
- Session configuration

## 🤝 Contributing

This is a development framework collection. Follow these guidelines:

1. **Never modify** `djangobase/` directory (framework code)
2. **Add application code** to `userapp/` directory
3. **Follow patterns** shown in `bloggy/` for Emmett apps
4. **Run tests** before committing
5. **Read** `agents.md` before making changes

## 📝 License

See individual component licenses:
- DjangoBase: Built on Cookiecutter-Django (BSD License)
- Emmett: See Emmett framework license
- Application code: Specify your own license

## 🆘 Troubleshooting

### Docker Issues

```bash
# Docker not running
open -a Docker  # Start Docker Desktop

# Rebuild containers
just build

# Clean restart
just down
just build
just up
```

### Database Issues

```bash
# Reset database (DjangoBase)
just down
docker volume rm pybase_postgres_data
just up
just manage migrate

# Reset database (Bloggy)
cd bloggy
rm *.db
uv run emmett setup
```

### Port Conflicts

```bash
# Change port in docker-compose.local.yml (DjangoBase)
# Or use different port for Bloggy
uv run emmett develop --port 8001
```

## 🚀 Next Steps

1. **Setup your environment**: Run `./setup/setup.sh`
2. **Read the guides**: Start with `agents.md`
3. **Explore examples**: Check out `bloggy/`
4. **Build your app**: Create models in `userapp/models/`
5. **Run tests**: Use `./run_tests.sh`

## 📞 Support

- **Documentation**: See `documentation/` and `emmett_documentation/`
- **Issues**: Check existing issues or create new ones
- **Framework Docs**:
  - [Django](https://docs.djangoproject.com/)
  - [Django REST Framework](https://www.django-rest-framework.org/)
  - [Emmett](https://emmett.sh/docs)

---

**Happy coding!** 🚀

