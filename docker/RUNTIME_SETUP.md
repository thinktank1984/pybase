# Runtime Docker Setup

This document describes the Docker configuration for the Runtime Emmett application.

## Overview

The runtime service runs the Emmett-based micro-blogging application in a Docker container with the full repository mounted for live development.

## Files Created

1. **`runtime/Dockerfile`** - Docker image definition
   - Based on Python 3.12-slim
   - Installs Emmett, Granian (ASGI server), and testing tools
   - Exposes port 8081

2. **`docker/docker-compose.yaml`** - Service definition (updated)
   - Added `runtime` service
   - Mounts full repository to `/app` in container
   - Configured with environment variables

3. **`runtime/.dockerignore`** - Docker ignore file
   - Excludes unnecessary files from Docker context

4. **`run_runtime.sh`** - Convenience script
   - Quick start script to launch the runtime service

## Quick Start

### Option 1: Using the convenience script

```bash
# From project root
./run_runtime.sh

# Make it executable first if needed
chmod +x run_runtime.sh
```

### Option 2: Using docker compose directly

```bash
# From the docker directory
cd docker
docker compose up runtime --build

# Or from project root
docker compose -f docker/docker-compose.yaml up runtime --build
```

### Option 3: Run in detached mode

```bash
cd docker
docker compose up runtime -d --build

# View logs
docker compose logs -f runtime

# Stop when done
docker compose down
```

## Service Details

- **Container Name**: `runtime`
- **Port**: 8081 (http://localhost:8081)
- **Base Image**: python:3.12-slim
- **Server**: Granian ASGI server
- **Working Directory**: `/app` (full repo mounted)

## Key Features

### Full Repository Mount

The entire repository is mounted to `/app` in the container:

```yaml
volumes:
  - ..:/app
```

**Benefits:**
- Live code changes reflected immediately
- No need to rebuild for application code changes
- Access to all project files within the container
- Easy debugging and development

### Environment Variables

- `PYTHONUNBUFFERED=1` - Unbuffered Python output for better logging
- `EMMETT_ENV=development` - Development mode

### Database Persistence

The SQLite database is stored in `runtime/databases/bloggy.db` which persists between container restarts because the full repository is mounted.

## Running Commands Inside the Container

### Setup admin user

```bash
docker compose -f docker/docker-compose.yaml exec runtime emmett setup
```

### Run migrations

```bash
docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up
```

### Run tests

```bash
docker compose -f docker/docker-compose.yaml exec runtime pytest runtime/tests.py
```

### Access shell

```bash
docker compose -f docker/docker-compose.yaml exec runtime bash
```

### Python shell

```bash
docker compose -f docker/docker-compose.yaml exec runtime python
```

### Emmett interactive shell

```bash
docker compose -f docker/docker-compose.yaml exec runtime emmett shell
```

## Rebuilding the Image

Rebuild when you change:
- Python dependencies
- Dockerfile
- System packages

```bash
cd docker
docker compose build runtime
docker compose up runtime
```

Or in one command:

```bash
docker compose up runtime --build
```

## Troubleshooting

### Port already in use

If port 8081 is already in use, edit `docker/docker-compose.yaml`:

```yaml
ports:
  - "8082:8081"  # Change 8082 to any available port
```

### Container won't start

Check logs:

```bash
docker compose -f docker/docker-compose.yaml logs runtime
```

### Permission issues

If you encounter permission issues with the mounted volume:

```bash
# On Linux, you may need to adjust file permissions
sudo chown -R $USER:$USER runtime/databases/
```

### Rebuild from scratch

```bash
cd docker
docker compose down
docker compose build --no-cache runtime
docker compose up runtime
```

## Integration with Other Services

The runtime service is part of a larger docker-compose stack including:
- **Bugsink** (port 8000) - Error tracking
- **Prometheus** (port 9090) - Metrics
- **Grafana** (port 3000) - Dashboards
- **Alertmanager** (port 9093) - Alerts
- **cAdvisor** (port 8080) - Container metrics
- **Runtime** (port 8081) - Emmett application

You can run all services together:

```bash
cd docker
docker compose up
```

Or run specific services:

```bash
docker compose up runtime prometheus grafana
```

## Default Credentials

**Admin User:**
- Email: `doc@emmettbrown.com`
- Password: `fluxcapacitor`

**Regular User (if exists):**
- Email: `a@a.com`
- Password: (check with admin)

## Development Workflow

1. **Start the service:**
   ```bash
   ./run_runtime.sh
   ```

2. **Make code changes** in your editor (changes are live due to volume mount)

3. **Refresh browser** to see changes (Granian auto-reloads in dev mode)

4. **Run tests:**
   ```bash
   docker compose -f docker/docker-compose.yaml exec runtime pytest runtime/tests.py -v
   ```

5. **View logs:**
   ```bash
   docker compose -f docker/docker-compose.yaml logs -f runtime
   ```

6. **Stop when done:**
   Press `Ctrl+C` or run `docker compose down`

## Next Steps

- Set up database migrations if schema changes
- Configure production settings
- Add health checks
- Set up CI/CD pipeline
- Configure SSL/TLS for production
- Add monitoring and alerting

## Resources

- Emmett Documentation: https://emmett.sh/docs
- Granian Documentation: https://github.com/emmett-framework/granian
- Docker Compose Documentation: https://docs.docker.com/compose/
- Project Emmett Documentation: `/emmett_documentation/`

