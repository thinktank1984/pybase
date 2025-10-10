# DevContainer Configuration for DjangoBase

This directory contains the Visual Studio Code DevContainer configuration for the DjangoBase project.

## What is a DevContainer?

DevContainers allow you to use a Docker container as a full-featured development environment. It ensures that everyone on the team has the same development environment with all dependencies pre-configured.

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Getting Started

1. **Open in Container**
   - Open this project in VS Code
   - Press `F1` and select `Dev Containers: Reopen in Container`
   - Or click the notification to reopen in container

2. **Wait for Container Build**
   - First time will take several minutes as it builds the Docker images
   - Subsequent launches will be much faster

3. **Start Developing**
   - The Django development server should start automatically
   - Access the application at http://localhost:8000

## What's Included

### Services
- **Django** - Main application (port 8000)
- **PostgreSQL** - Database (port 5432)
- **Redis** - Caching and Celery broker (port 6379)
- **Mailpit** - Email testing (SMTP: 1025, Web UI: 8025)

### VS Code Extensions
- Python development tools (Pylance, Black, isort, Flake8)
- Django support
- Git tools (GitLens, Git History)
- Docker tools
- GitHub Copilot (if you have access)
- YAML and TOML support

### Python Tools
- Black (code formatting)
- isort (import sorting)
- Flake8 (linting)
- pytest (testing)

## Configuration

### Environment Variables
The following environment variables are automatically set:
- `DJANGO_SETTINGS_MODULE=config.settings.local`
- `DATABASE_URL=postgres://debug:debug@postgres:5432/djangobase`
- `CELERY_BROKER_URL=redis://redis:6379/0`
- `USE_DOCKER=yes`

### Port Forwarding
Ports are automatically forwarded to your local machine:
- **8000**: Django application
- **5432**: PostgreSQL database
- **6379**: Redis
- **1025**: Mailpit SMTP
- **8025**: Mailpit web interface

## Common Tasks

### Run Django Management Commands
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

### Run Tests
```bash
pytest
# or with coverage
pytest --cov
```

### Check Code Quality
```bash
# Format code
black .
isort .

# Lint
flake8

# Type checking
mypy .
```

### Access Services
- Django: http://localhost:8000
- Mailpit: http://localhost:8025
- PostgreSQL: `psql -h localhost -U debug -d djangobase`

## Customization

### Add Extensions
Edit `.devcontainer/devcontainer.json` and add extension IDs to the `extensions` array.

### Change Settings
Edit VS Code settings in `customizations.vscode.settings`.

### Add Environment Variables
Add to the `remoteEnv` section in `devcontainer.json`.

## Troubleshooting

### Container won't start
1. Check Docker Desktop is running
2. Run `docker compose -f local.yml down -v` to clean up
3. Rebuild container: `F1` → `Dev Containers: Rebuild Container`

### Can't connect to services
- Ensure ports aren't already in use on your host machine
- Check `docker compose -f local.yml ps` to see running services

### Python interpreter not found
- Reload the window: `F1` → `Developer: Reload Window`
- Check interpreter path: `/usr/local/bin/python`

## Notes

- The container runs as `root` user for convenience
- Your `.ssh` and `.gitconfig` are mounted for git operations
- The container stops when VS Code closes but doesn't remove volumes
- Database and Redis data persists between container restarts

## Learn More

- [VS Code DevContainers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [DevContainer Specification](https://containers.dev/)
