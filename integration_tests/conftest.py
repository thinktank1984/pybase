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
    Runs migrations to ensure schema is up to date.
    NEVER touches the database structure - Docker maintains persistent state.
    """
    print("\n🔧 Setting up test environment (session-level)...")
    import subprocess
    from emmett.orm.migrations.utils import generate_runtime_migration
    
    # Get database configuration from environment
    test_db_url = os.environ.get(
        'TEST_DATABASE_URL',
        'postgres://bloggy:bloggy_password@postgres:5432/bloggy_test'
    )
    
    print(f"   ✅ Using persistent test database from Docker")
    
    # Check if migrations have been run
    print("   🔧 Checking database schema...")
    try:
        with app_module.db.connection():
            # Check if emmett_schema table exists (created by migrations)
            result = app_module.db.executesql(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'emmett_schema')"
            )
            schema_exists = result[0][0] if result else False
            
            if schema_exists:
                print("   ✅ Database schema already up to date")
            else:
                print("   🔧 Running database migrations...")
                # Try migrations first
                runtime_dir = os.path.join(os.path.dirname(__file__), '..', 'runtime')
                env = os.environ.copy()
                env['DATABASE_URL'] = test_db_url
                
                result = subprocess.run(
                    ['emmett', 'migrations', 'up'],
                    cwd=runtime_dir,
                    capture_output=True,
                    text=True,
                    env=env
                )
                if result.returncode == 0:
                    print("   ✅ Migrations completed successfully")
                else:
                    print(f"   ⚠️  Migration command failed, database may already be initialized")
                    print("   ✅ Using existing database schema")
    except Exception as e:
        print(f"   ⚠️  Schema check error: {e}")
        print("   ✅ Proceeding with existing schema")
    
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
    
    # Teardown - DO NOT drop database (Docker maintains persistent state)
    # Clean up test data instead of dropping the database
    print("\n   🧹 Cleaning up test data (preserving database for next run)...")
    try:
        with app_module.db.connection():
            # Clean up test users and their related data
            # Use explicit type casting for foreign key comparisons
            # Note: Both posts and comments use 'user' column, not 'author'
            app_module.db.executesql("DELETE FROM user_roles WHERE user::text IN (SELECT id::text FROM users WHERE email LIKE '%@example.com%')")
            app_module.db.executesql("DELETE FROM oauth_tokens WHERE user::text IN (SELECT id::text FROM users WHERE email LIKE '%@example.com%')")
            app_module.db.executesql("DELETE FROM oauth_accounts WHERE user::text IN (SELECT id::text FROM users WHERE email LIKE '%@example.com%')")
            app_module.db.executesql('DELETE FROM comments WHERE "user"::text IN (SELECT id::text FROM users WHERE email LIKE \'%@example.com%\')')
            app_module.db.executesql('DELETE FROM posts WHERE "user"::text IN (SELECT id::text FROM users WHERE email LIKE \'%@example.com%\')')
            app_module.db.executesql("DELETE FROM users WHERE email LIKE '%@example.com%'")
            app_module.db.commit()
            print("   ✅ Test data cleaned up (database preserved)")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")


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
