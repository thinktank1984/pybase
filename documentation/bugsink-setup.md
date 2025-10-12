# Bugsink Error Tracking Setup

## Overview

Bugsink is a self-hosted, Sentry-compatible error tracking system integrated with the Bloggy application. It captures and reports application errors, exceptions, and performance metrics.

## Services

- **Bugsink UI**: http://localhost:8000
- **Bugsink Database**: PostgreSQL on port 5432 (internal)
- **Runtime Application**: http://localhost:8081

## Initial Setup

### 1. Start Services

```bash
cd /Users/ed.sharood2/code/pybase
docker compose -f docker/docker-compose.yaml up bugsink bugsink_db runtime -d
```

### 2. Access Bugsink Dashboard

1. Open http://localhost:8000 in your browser
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin_password`

### 3. Create a Project

1. After logging in, create a new project in Bugsink
2. Note the DSN (Data Source Name) provided
3. The default DSN is configured as: `http://public@bugsink:8000/1`
4. If you need to change it, update the `SENTRY_DSN` environment variable

### 4. Verify Error Tracking

Test that errors are being captured:

```bash
# Test with a generic exception
curl http://localhost:8081/test-error

# Test with a division by zero error
curl http://localhost:8081/test-error-division
```

After triggering errors, check the Bugsink dashboard to see them appear.

## Configuration

### Environment Variables

The following environment variables control error tracking behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_ENABLED` | `true` | Enable/disable error tracking |
| `SENTRY_DSN` | `http://public@bugsink:8000/1` | Bugsink Data Source Name |
| `SENTRY_ENVIRONMENT` | `development` | Environment name (development, staging, production) |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Performance monitoring sampling rate (0.0 to 1.0) |

### Example: Disable Error Tracking

Add to docker-compose.yaml under `runtime` service:

```yaml
environment:
  - SENTRY_ENABLED=false
```

### Example: Change Environment

```yaml
environment:
  - SENTRY_ENVIRONMENT=production
  - SENTRY_TRACES_SAMPLE_RATE=0.05  # Lower sampling in production
```

### Example: Use External Sentry

If you want to use hosted Sentry instead of Bugsink:

```yaml
environment:
  - SENTRY_DSN=https://your-key@o123456.ingest.sentry.io/789012
```

## What Gets Captured

### Errors

- Unhandled exceptions during request processing
- Full stack traces
- Request context:
  - HTTP method, URL path, query parameters
  - Request headers (sensitive ones excluded)
  - Request body (when available)
- User information (when authenticated):
  - User ID
  - User email
  - No passwords or tokens

### Performance Monitoring

- Request duration
- Slow requests identification
- Database query performance
- Sampling rate: 10% by default (configurable)

### Environment Information

- Python version
- Emmett version
- Server hostname
- Environment name (development, production, etc.)

## Error Dashboard Features

Access Bugsink at http://localhost:8000 to:

- View all captured errors
- See error frequency and trends
- Inspect full stack traces
- View request context for each error
- Group similar errors together
- Search and filter errors
- Mark errors as resolved
- Set up error assignments and workflows

## Test Endpoints

The application includes test endpoints for verifying error tracking:

- `/test-error` - Raises a generic Exception
- `/test-error-division` - Raises a ZeroDivisionError

These endpoints are useful for:
- Verifying error tracking is working
- Testing error grouping
- Checking error context capture

## Troubleshooting

### Errors not appearing in Bugsink

1. **Check if error tracking is enabled**:
   ```bash
   docker compose -f docker/docker-compose.yaml logs runtime | grep "Error tracking"
   ```
   Should show: `✓ Error tracking enabled`

2. **Verify Bugsink is running**:
   ```bash
   docker compose -f docker/docker-compose.yaml ps bugsink
   ```
   Status should show "Up" and "healthy"

3. **Check project exists in Bugsink**:
   - Login to http://localhost:8000
   - Ensure project ID matches DSN (default is project 1)

4. **Check network connectivity**:
   ```bash
   docker compose -f docker/docker-compose.yaml exec runtime ping -c 3 bugsink
   ```

5. **Verify DSN format**:
   - Format: `http://public@bugsink:8000/PROJECT_ID`
   - Must match a project created in Bugsink

### Application won't start

If the application fails to start due to Sentry extension:

1. **Disable error tracking temporarily**:
   ```bash
   SENTRY_ENABLED=false docker compose -f docker/docker-compose.yaml up runtime
   ```

2. **Check if emmett-sentry is installed**:
   ```bash
   docker compose -f docker/docker-compose.yaml exec runtime pip show emmett-sentry
   ```

### Bugsink showing 400 errors

This typically means:
- Project doesn't exist in Bugsink yet
- DSN project ID doesn't match an actual project
- Solution: Create project in Bugsink UI with matching ID

## Data Persistence

Bugsink data is persisted in Docker volumes:

- `bugsink_db_data` - PostgreSQL database
- `bugsink_data` - File-based event storage

To clear all error data:

```bash
docker compose -f docker/docker-compose.yaml down
docker volume rm pybase_bugsink_db_data pybase_bugsink_data
docker compose -f docker/docker-compose.yaml up bugsink bugsink_db -d
```

## Production Considerations

When deploying to production:

1. **Change admin password**:
   - Update `CREATE_SUPERUSER` in docker-compose.yaml
   - Or change password via Bugsink UI

2. **Secure Bugsink**:
   - Use HTTPS proxy in front of Bugsink
   - Set `BEHIND_HTTPS_PROXY=true`
   - Update `BASE_URL` to match your domain

3. **Adjust sampling rates**:
   - Lower performance sampling (e.g., 5% or 1%)
   - Keep error sampling at 100%

4. **Configure data retention**:
   - Set retention policies in Bugsink
   - Default: 30 days

5. **Set up alerting**:
   - Configure notifications in Bugsink
   - Integrate with Slack, email, etc.

6. **Use environment-specific DSNs**:
   - Different projects for dev, staging, production
   - Makes error filtering easier

## Integration Details

### Emmett Framework Integration

The integration uses the official `emmett-sentry` extension:

```python
# In app.py
from emmett_sentry import Sentry

app.config.Sentry.dsn = SENTRY_DSN
app.config.Sentry.environment = SENTRY_ENVIRONMENT
app.config.Sentry.traces_sample_rate = SENTRY_TRACES_SAMPLE_RATE
app.config.Sentry.release = "bloggy@1.0.0"
app.use_extension(Sentry)
```

### Captured Context

The extension automatically captures:
- Request details
- User information (from session)
- Environment variables
- Application version
- Server information

### Excluded from Capture

The following are automatically scrubbed:
- Passwords
- Tokens and API keys
- Cookie values
- Authorization headers
- Any field named: password, secret, token, api_key

## References

- [Bugsink Documentation](https://bugsink.com/docs)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [emmett-sentry Extension](https://github.com/emmett-framework/sentry)
- [Emmett Framework](https://emmett.sh/docs)

## Support

For issues with:
- Bugsink: https://github.com/bugsink/bugsink/issues
- emmett-sentry: https://github.com/emmett-framework/sentry/issues
- Emmett: https://github.com/emmett-framework/emmett/issues

