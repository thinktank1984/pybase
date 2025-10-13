# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for integration tests.
"""

import pytest
import sys
import os

# Add runtime to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime'))

# Import modules (use aliases to avoid fixture name conflicts)
import app as app_module
import models


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """
    Setup test environment - runs once per test session.
    This ensures the database is properly initialized before any tests run.
    """
    # Set up database with migrations
    print("\n🔧 Setting up test database (session-level)...")
    import sqlite3
    from emmett.orm.migrations.utils import generate_runtime_migration
    
    db = app_module.db
    db_path = os.path.join(os.path.dirname(__file__), '..', 'runtime', 'databases', 'bloggy.db')
    db_dir = os.path.dirname(db_path)
    
    # Ensure database directory exists
    os.makedirs(db_dir, exist_ok=True)
    
    # Check if database needs to be created
    needs_setup = not os.path.exists(db_path)
    
    if needs_setup:
        print("   🔧 Creating fresh database...")
        with db.connection():
            migration = generate_runtime_migration(db)
            migration.up()
            db.commit()
        print("   ✅ Database created")
    else:
        # Database exists, just verify tables exist
        try:
            with db.connection():
                db.executesql("SELECT COUNT(*) FROM users LIMIT 1")
                print("   ✅ Database already exists")
        except:
            # Tables don't exist, create them
            print("   🔧 Creating database tables...")
            with db.connection():
                migration = generate_runtime_migration(db)
                migration.up()
                db.commit()
            print("   ✅ Database tables created")
    
    yield
    
    # Teardown - nothing to clean up (let individual tests handle cleanup)


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


@pytest.fixture(scope='function')
def app():
    """
    Provide the Emmett application instance for function scope.
    
    Returns:
        App: Emmett application instance
    """
    return app_module.app


@pytest.fixture(scope='function')
def db():
    """
    Provide the database instance for function scope.
    
    Returns:
        Database: Emmett database instance
    """
    return app_module.db
