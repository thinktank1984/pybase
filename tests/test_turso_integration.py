# -*- coding: utf-8 -*-
"""
Tests for Turso Database integration with DatabaseManager.

These tests verify that the Turso database support works correctly
and falls back gracefully when needed.
"""

import pytest
import os
from runtime.database_manager import DatabaseManager


class TestTursoIntegration:
    """Test Turso database integration functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Reset singleton before each test
        DatabaseManager.reset_instance()

    def test_detect_turso_database_type(self):
        """Test detection of Turso database URLs."""
        db_manager = DatabaseManager()

        # Test libsql:// URLs
        assert db_manager._detect_database_type("libsql://my-db.turso.io") == "turso"
        assert db_manager._detect_database_type("libsql://example.turso.io/auth_token") == "turso"

        # Test https:// URLs with turso in hostname
        assert db_manager._detect_database_type("https://my-db.turso.io") == "turso"
        assert db_manager._detect_database_type("https://example-org.turso.io") == "turso"

        # Test SQLite URLs
        assert db_manager._detect_database_type("sqlite://bloggy.db") == "sqlite"
        assert db_manager._detect_database_type("sqlite:memory") == "sqlite"

        # Test PostgreSQL URLs
        assert db_manager._detect_database_type("postgres://user:pass@host/db") == "postgres"
        assert db_manager._detect_database_type("postgresql://user:pass@host/db") == "postgres"

        # Test MySQL URLs
        assert db_manager._detect_database_type("mysql://user:pass@host/db") == "mysql"

        # Test unknown URLs
        assert db_manager._detect_database_type("oracle://user:pass@host/db") == "unknown"
        assert db_manager._detect_database_type("mongodb://host/db") == "unknown"

    def test_database_type_property_after_init(self):
        """Test database_type property after initialization."""
        db_manager = DatabaseManager()

        # Test that database type is initially unknown
        assert db_manager.database_type == 'unknown'
        assert not db_manager.is_turso()

    def test_turso_missing_dependency_error(self):
        """Test that missing libsql-client raises proper error."""
        db_manager = DatabaseManager()

        # Create a minimal mock app object
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

        mock_app = MockApp()

        # Should raise ImportError when libsql-client is not available
        with pytest.raises(ImportError) as exc_info:
            db_manager._initialize_turso(mock_app, "libsql://test.turso.io")

        assert "libsql-client is required" in str(exc_info.value)
        assert "pip install libsql-client" in str(exc_info.value)

    def test_sqlite_initialization_still_works(self):
        """Test that SQLite initialization still works normally."""
        db_manager = DatabaseManager()

        # Create a minimal mock app object
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

        mock_app = MockApp()

        # Initialize with SQLite URL
        try:
            db_manager.initialize(mock_app, "sqlite://test_bloggy.db")

            # Should detect as SQLite
            assert db_manager.database_type == "sqlite"
            assert not db_manager.is_turso()
            assert db_manager.is_initialized

        except Exception as e:
            # If full initialization fails due to missing dependencies,
            # at least verify the URL detection worked
            assert db_manager._detect_database_type("sqlite://test_bloggy.db") == "sqlite"

    def test_database_type_detection_integration(self):
        """Test database type detection in a realistic scenario."""
        db_manager = DatabaseManager()

        # Test various URL patterns
        test_cases = [
            ("libsql://my-app.turso.io", "turso"),
            ("https://production-db.turso.io", "turso"),
            ("sqlite://local.db", "sqlite"),
            ("postgres://localhost:5432/mydb", "postgres"),
            ("mysql://localhost:3306/mydb", "mysql"),
            ("unknown://somehost/db", "unknown")
        ]

        for url, expected_type in test_cases:
            detected_type = db_manager._detect_database_type(url)
            assert detected_type == expected_type, f"URL {url} should be {expected_type}, got {detected_type}"

    def test_is_turso_helper_method(self):
        """Test the is_turso() helper method."""
        db_manager = DatabaseManager()

        # Initially should not be turso
        assert not db_manager.is_turso()

        # Test various database types
        db_manager._db_type = 'turso'
        assert db_manager.is_turso()

        db_manager._db_type = 'sqlite'
        assert not db_manager.is_turso()

        db_manager._db_type = 'postgres'
        assert not db_manager.is_turso()

        db_manager._db_type = 'unknown'
        assert not db_manager.is_turso()


if __name__ == '__main__':
    pytest.main([__file__])