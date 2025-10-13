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
    Note: Row class patching is now done in individual test file fixtures.
    """
    yield
    # Teardown - nothing to clean up


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
