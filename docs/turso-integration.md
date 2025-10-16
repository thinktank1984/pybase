# Turso Database Integration

This document explains how to use Turso Database as a backend for your pybase application.

## Overview

Turso is an edge-native, SQLite-compatible database that provides:
- **Edge-native deployment** with global replication
- **SQLite compatibility** - no code changes needed
- **Serverless architecture** with automatic scaling
- **Built-in connection pooling** and retry logic

## Quick Start

### 1. Install Dependencies

```bash
pip install libsql-client
```

### 2. Configure Environment

Set your Turso database URL and authentication token:

```bash
export TURSO_DATABASE_URL="libsql://your-app.turso.io"
export TURSO_AUTH_TOKEN="your-auth-token-here"
```

### 3. Use in Your Application

```python
from runtime.database_manager import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager.get_instance()
app = YourEmmettApp()  # Your Emmett application
db_manager.initialize(app)  # Will auto-detect Turso from environment

# Check database type
if db_manager.is_turso():
    print("Using Turso Database!")
else:
    print("Using local database")
```

## Configuration

### Environment Variables

- `TURSO_DATABASE_URL`: Your Turso database URL (takes precedence)
- `TURSO_AUTH_TOKEN`: Your Turso authentication token
- `DATABASE_URL`: Fallback database URL (SQLite by default)

### URL Formats

Turso supports these URL patterns:

```bash
# Basic libsql URL
libsql://your-app.turso.io

# With auth token in URL fragment
libsql://your-app.turso.io#your-auth-token

# HTTPS format (with turso in hostname)
https://your-app.turso.io
```

## Features

### Automatic Database Detection

The `DatabaseManager` automatically detects your database type:

```python
db_manager = DatabaseManager.get_instance()

# Check database type
print(f"Database type: {db_manager.database_type}")
print(f"Is Turso: {db_manager.is_turso()}")
```

### Connection Management

- **Retry Logic**: Automatic retries with exponential backoff
- **Connection Pooling**: Optimized for distributed access
- **Timeout Handling**: 30-second connection timeout
- **Graceful Fallback**: Falls back to SQLite if Turso is unavailable

### SQLite Compatibility

Since Turso is SQLite-compatible, all your existing code works unchanged:

```python
# Works with both SQLite and Turso
with db_manager.connection():
    users = User.where(lambda u: u.active == True).select()
    posts = Post.create(title="Hello", content="World")
```

## Migration

### From SQLite to Turso

1. **Create Turso Database**: Sign up at [turso.tech](https://turso.tech/)
2. **Export Data**: Use SQLite tools to export your data
3. **Import Data**: Use Turso CLI or API to import your data
4. **Update Configuration**: Set `TURSO_DATABASE_URL` environment variable
5. **Deploy**: Your application works without code changes

### From Turso to SQLite

Simply remove the `TURSO_DATABASE_URL` environment variable, and the application will automatically fall back to SQLite.

## Troubleshooting

### Missing Dependency

If you see this error:
```
ImportError: libsql-client is required for Turso database support
```

Install the dependency:
```bash
pip install libsql-client
```

### Connection Issues

If Turso connection fails, the system will:
1. Log the error
2. Fall back to SQLite automatically
3. Continue working with local database

### Authentication

Make sure to set your auth token:
```bash
export TURSO_AUTH_TOKEN="your-auth-token"
```

## Testing

The Turso integration includes comprehensive tests:

```bash
python -m pytest tests/test_turso_integration.py -v
```

## Example Applications

See `examples/turso_database_example.py` for a complete working example.

## Additional Resources

- [Turso Documentation](https://docs.turso.tech/)
- [libsql-client Python](https://github.com/tursodatabase/libsql-client-python)
- [pybase Documentation](../README.md)