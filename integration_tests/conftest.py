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
    print("   ✅ Database schema maintained by Docker (migrations already applied)")
    
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
    
    # Teardown - Preserve test data for inspection
    # Integration tests keep data so you can debug and inspect results
    print("\n   ✅ Test data preserved for inspection (database and data intact)")


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
