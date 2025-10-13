# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for integration tests.
"""

import pytest
import sys
import os

# Set test database URL BEFORE importing app so it initializes with test database
TEST_DATABASE_URL = os.environ.get(
    'TEST_DATABASE_URL',
    'postgres://bloggy:bloggy_password@postgres:5432/bloggy_test'
)
os.environ['DATABASE_URL'] = TEST_DATABASE_URL

# Add runtime to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime'))

# Import modules (use aliases to avoid fixture name conflicts)
# These will now initialize with TEST_DATABASE_URL
import app as app_module
import models


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """
    Setup test environment - runs once per test session.
    This ensures the PostgreSQL test database is properly initialized before any tests run.
    """
    # Set up PostgreSQL test database with migrations
    print("\n🔧 Setting up PostgreSQL test database (session-level)...")
    import subprocess
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from emmett.orm.migrations.utils import generate_runtime_migration
    
    # Get database configuration from environment
    test_db_url = os.environ.get(
        'TEST_DATABASE_URL',
        'postgres://bloggy:bloggy_password@postgres:5432/bloggy_test'
    )
    
    # Parse connection parameters
    # Format: postgres://user:password@host:port/dbname
    parts = test_db_url.replace('postgres://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    
    db_user = user_pass[0]
    db_password = user_pass[1] if len(user_pass) > 1 else ''
    db_host = host_port[0]
    db_port = int(host_port[1]) if len(host_port) > 1 else 5432
    db_name = host_port_db[1]
    
    # Connect to PostgreSQL server (postgres database) to create test database
    print(f"   🔗 Connecting to PostgreSQL at {db_host}:{db_port}...")
    try:
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Terminate all existing connections to the test database
        print(f"   🔌 Terminating existing connections to '{db_name}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
              AND pid <> pg_backend_pid()
        """)
        
        # Drop test database if it exists
        print(f"   🗑️  Dropping existing test database '{db_name}' if it exists...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        
        # Create fresh test database
        print(f"   ✨ Creating fresh test database '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name}")
        
        cursor.close()
        conn.close()
        print("   ✅ Test database created successfully")
    except psycopg2.Error as e:
        pytest.fail(f"PostgreSQL test database setup failed: {e}. Ensure PostgreSQL is running in Docker.")
    
    # Database is already configured to use test database (via DATABASE_URL env var)
    # No need to reconfigure - app.py initialized with test database
    print(f"   ✅ Database configured with test database: {db_name}")
    
    # Run migrations to create tables
    print("   🔧 Running database migrations...")
    runtime_dir = os.path.join(os.path.dirname(__file__), '..', 'runtime')
    try:
        # Set environment variable for migrations
        env = os.environ.copy()
        env['DATABASE_URL'] = test_db_url
        
        result = subprocess.run(
            ['emmett', 'migrations', 'up'],
            cwd=runtime_dir,
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        print("   ✅ Migrations completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Migration command failed: {e.stderr}")
        print("   Trying runtime migration...")
        # Fallback to runtime migration
        with app_module.db.connection():
            migration = generate_runtime_migration(app_module.db)
            migration.up()
            app_module.db.commit()
        print("   ✅ Database created with runtime migration")
    
    # CRITICAL: Re-define models after migrations to sync pyDAL table metadata
    # This is necessary because define_models() was called when app.py was imported
    # (before the database existed), so the table metadata needs to be refreshed
    print("   🔄 Re-syncing pyDAL table metadata after migrations...")
    app_module.db.define_models(
        models.Post, models.Comment, models.Role, models.Permission,
        models.UserRole, models.RolePermission, models.OAuthAccount, models.OAuthToken
    )
    
    # Re-patch Row methods after redefining models (creates new Row classes)
    app_module._patch_row_methods()
    print("   ✅ Table metadata synchronized with PostgreSQL schema")
    
    yield
    
    # Teardown - drop test database
    print("\n   🧹 Cleaning up test database...")
    try:
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Terminate all existing connections before dropping
        print(f"   🔌 Terminating connections to '{db_name}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
              AND pid <> pg_backend_pid()
        """)
        
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cursor.close()
        conn.close()
        print("   ✅ Test database dropped successfully")
    except psycopg2.Error as e:
        print(f"   ⚠️  Failed to drop test database: {e}")


@pytest.fixture()
def test_client():
    """
    Provide a test client for making HTTP requests.
    
    Returns:
        TestClient: Emmett test client instance
    """
    return app_module.app.test_client()


@pytest.fixture()
def client():
    """
    Alias for test_client - for backwards compatibility.
    
    Returns:
        TestClient: Emmett test client instance
    """
    return app_module.app.test_client()


@pytest.fixture(scope='session')
def app():
    """
    Provide the Emmett application instance for session scope.
    
    Returns:
        App: Emmett application instance
    """
    return app_module.app


@pytest.fixture(scope='session')
def db():
    """
    Provide the database instance for session scope.
    
    Returns:
        Database: Emmett database instance
    """
    return app_module.db


def ensure_db_connection(db_instance):
    """
    Helper to ensure database operations execute within a connection context.
    
    This is a utility for tests that need to wrap database queries.
    PostgreSQL requires explicit connection contexts via `with db.connection():`.
    
    Usage:
        with ensure_db_connection(db):
            user = User.create(email="test@test.com", password="test")
    
    Args:
        db_instance: Database instance from fixture
        
    Returns:
        Context manager for database connection
    """
    return db_instance.connection()
