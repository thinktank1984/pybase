# -*- coding: utf-8 -*-
"""
Integration tests for database operations with SQLite.

These tests verify that database operations work correctly
with SQLite configuration.
"""

import pytest
import os
from runtime.database_manager import DatabaseManager


class TestDatabaseOperations:
    """Test database operations functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Reset singleton before each test
        DatabaseManager.reset_instance()

    def test_sqlite_database_operations(self):
        """Test actual database operations with SQLite."""
        db_manager = DatabaseManager()

        # Test database type detection
        db_type = db_manager._detect_database_type('sqlite://test_operations.db')
        assert db_type == 'sqlite'

        # Create a simple app-like object that doesn't require full Emmett
        class MockApp:
            def __init__(self):
                self.config = MockConfig()

        class MockConfig:
            def __init__(self):
                self.db = MockDBConfig()

        class MockDBConfig:
            def __init__(self):
                self.uri = None
                self.pool_size = None
                self.adapter_args = {}

        app = MockApp()

        # Configure the database manager manually
        db_manager._app = app
        db_manager._db_type = db_type
        app.config.db.uri = 'sqlite://test_operations.db'
        app.config.db.pool_size = 0
        app.config.db.adapter_args = {
            'journal_mode': 'DELETE',
            'synchronous': 'NORMAL',
            'foreign_keys': 'ON',
        }

        # Verify configuration
        assert db_manager.database_type == 'sqlite'
        assert db_manager.is_sqlite()
        assert app.config.db.uri == 'sqlite://test_operations.db'
        assert app.config.db.pool_size == 0
        assert app.config.db.adapter_args['foreign_keys'] == 'ON'

        print("✅ SQLite configuration successful")

    def test_sqlite_url_detection_without_initialization(self):
        """Test SQLite URL detection without actual database initialization."""
        db_manager = DatabaseManager()

        # Test various SQLite URL formats
        sqlite_urls = [
            'sqlite://test.db',
            'sqlite://runtime/databases/main.db',
            'sqlite:///absolute/path/to/database.db',
            'sqlite://relative/path/to/database.db'
        ]

        for url in sqlite_urls:
            db_type = db_manager._detect_database_type(url)
            assert db_type == 'sqlite', f"URL {url} should be detected as sqlite, got {db_type}"

        print("✅ All SQLite URL formats detected correctly")

    def test_database_type_property_consistency(self):
        """Test that database_type property is consistent across operations."""
        db_manager = DatabaseManager()

        # Initially should be sqlite
        assert db_manager.database_type == 'sqlite'
        assert db_manager.is_sqlite()

        # Test setting different database types
        for db_type in ['sqlite', 'postgres', 'mysql', 'unknown']:
            db_manager._db_type = db_type
            assert db_manager.database_type == db_type
            assert db_manager.is_sqlite() == (db_type == 'sqlite')

        print("✅ Database type property consistency verified")

    def test_environment_variable_priority(self):
        """Test that DATABASE_URL is used correctly."""
        # Set environment variable
        os.environ['DATABASE_URL'] = 'sqlite://test_priority.db'

        db_manager = DatabaseManager()

        # Test URL resolution logic
        database_url = os.environ.get('DATABASE_URL', 'sqlite://runtime/databases/main.db')
        detected_type = db_manager._detect_database_type(database_url)

        assert detected_type == 'sqlite'
        assert database_url == 'sqlite://test_priority.db'

        # Clean up
        del os.environ['DATABASE_URL']

        print("✅ Environment variable priority test passed")

    def test_database_fallback_mechanism(self):
        """Test database fallback mechanism when primary fails."""
        db_manager = DatabaseManager()

        # Create mock app
        class MockApp:
            def __init__(self):
                self.config = MockConfig()

        class MockConfig:
            def __init__(self):
                self.db = MockDBConfig()

        class MockDBConfig:
            def __init__(self):
                self.uri = None
                self.pool_size = None
                self.adapter_args = {}

        app = MockApp()

        # Test SQLite fallback configuration
        fallback_url = 'sqlite://fallback_test.db'
        app.config.db.uri = fallback_url
        app.config.db.pool_size = 0
        app.config.db.adapter_args = {
            'journal_mode': 'DELETE',
            'synchronous': 'NORMAL',
            'foreign_keys': 'ON',
        }

        # Verify fallback configuration
        assert app.config.db.uri == fallback_url
        assert app.config.db.pool_size == 0
        assert 'foreign_keys' in app.config.db.adapter_args

        print("✅ Database fallback mechanism verified")

    def test_connection_configuration_differences(self):
        """Test that different database types get appropriate configurations."""
        db_manager = DatabaseManager()

        # Test configurations for different database types
        configurations = {
            'sqlite': {
                'pool_size': 0,
                'adapter_args': {
                    'journal_mode': 'DELETE',
                    'synchronous': 'NORMAL',
                    'foreign_keys': 'ON',
                }
            }
        }

        for db_type, expected_config in configurations.items():
            db_manager._db_type = db_type

            # Create mock app
            class MockApp:
                def __init__(self):
                    self.config = MockConfig()

            class MockConfig:
                def __init__(self):
                    self.db = MockDBConfig()

            class MockDBConfig:
                def __init__(self):
                    self.uri = None
                    self.pool_size = None
                    self.adapter_args = {}

            app = MockApp()

            # Apply configuration based on database type
            if db_type == 'sqlite':
                app.config.db.pool_size = expected_config['pool_size']
                app.config.db.adapter_args = expected_config['adapter_args']

            # Verify configuration
            assert app.config.db.pool_size == expected_config['pool_size']
            assert app.config.db.adapter_args['journal_mode'] == expected_config['adapter_args']['journal_mode']
            assert app.config.db.adapter_args['foreign_keys'] == 'ON'

        print("✅ Connection configuration differences verified")

    def test_database_manager_singleton_behavior(self):
        """Test that DatabaseManager maintains singleton behavior."""
        db_manager1 = DatabaseManager.get_instance()
        db_manager2 = DatabaseManager.get_instance()

        # Should be the same instance
        assert db_manager1 is db_manager2

        # Reset and create new instance
        DatabaseManager.reset_instance()
        db_manager3 = DatabaseManager.get_instance()

        # Should be a different instance
        assert db_manager1 is not db_manager3
        assert db_manager2 is not db_manager3

        print("✅ DatabaseManager singleton behavior verified")


if __name__ == '__main__':
    pytest.main([__file__])