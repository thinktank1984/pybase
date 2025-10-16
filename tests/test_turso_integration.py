# -*- coding: utf-8 -*-
"""
Tests for Turso Database integration with DatabaseManager.

These tests verify that the Turso database support works correctly
and falls back gracefully when needed.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
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

    def test_database_type_property(self):
        """Test database_type property returns detected type."""
        db_manager = DatabaseManager()

        # Mock the app object
        mock_app = MagicMock()

        # Test Turso URL
        with patch.object(db_manager, '_initialize_turso') as mock_init:
            mock_init.return_value = MagicMock()
            db_manager.initialize(mock_app, "libsql://test.turso.io")
            assert db_manager.database_type == "turso"
            assert db_manager.is_turso() is True

    @patch('runtime.database_manager.libsql_client')
    def test_turso_initialization_success(self, mock_libsql):
        """Test successful Turso database initialization."""
        db_manager = DatabaseManager()
        mock_app = MagicMock()

        # Mock libsql client
        mock_client = MagicMock()
        mock_libsql.create_client_sync.return_value = mock_client
        mock_client.execute.return_value = MagicMock()

        # Mock Database constructor
        with patch('runtime.database_manager.Database') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_class.return_value = mock_db_instance

            # Test with auth token
            os.environ['TURSO_AUTH_TOKEN'] = 'test_token'
            result = db_manager._initialize_turso(mock_app, "libsql://test.turso.io")

            # Verify initialization
            assert result == mock_db_instance
            assert db_manager.is_initialized is True
            assert db_manager.is_turso() is True
            assert db_manager._turso_client == mock_client

            # Verify libsql client was called correctly
            mock_libsql.create_client_sync.assert_called_once_with(
                url="https://test.turso.io",
                auth_token="test_token"
            )

            # Verify app configuration
            assert "turso_host=test.turso.io" in mock_app.config.db.uri
            assert "turso_token=test_token" in mock_app.config.db.uri
            assert mock_app.config.db.adapter_args['journal_mode'] == 'WAL'

            # Clean up
            del os.environ['TURSO_AUTH_TOKEN']

    @patch('runtime.database_manager.libsql_client')
    def test_turso_initialization_no_auth_token(self, mock_libsql):
        """Test Turso initialization without auth token."""
        db_manager = DatabaseManager()
        mock_app = MagicMock()

        # Mock libsql client
        mock_client = MagicMock()
        mock_libsql.create_client_sync.return_value = mock_client
        mock_client.execute.return_value = MagicMock()

        # Mock Database constructor
        with patch('runtime.database_manager.Database') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_class.return_value = mock_db_instance

            # Test without auth token
            with patch('builtins.print') as mock_print:
                result = db_manager._initialize_turso(mock_app, "libsql://test.turso.io")

                # Verify warning was printed
                mock_print.assert_any_call("⚠️  Warning: No Turso auth token found. Set TURSO_AUTH_TOKEN environment variable.")

                # Verify client was created without auth token
                mock_libsql.create_client_sync.assert_called_once_with(
                    url="https://test.turso.io"
                )

    @patch('runtime.database_manager.libsql_client')
    def test_turso_retry_logic(self, mock_libsql):
        """Test Turso connection retry logic."""
        db_manager = DatabaseManager()

        # Mock libsql client to fail twice, then succeed
        mock_client = MagicMock()
        mock_libsql.create_client_sync.side_effect = [
            Exception("Connection failed"),
            Exception("Connection failed again"),
            mock_client
        ]
        mock_client.execute.return_value = MagicMock()

        # Test retry logic
        with patch('time.sleep'):  # Skip actual sleep
            result = db_manager._create_turso_client_with_retry("test.turso.io", "token")

            # Should have been called 3 times (2 failures + 1 success)
            assert mock_libsql.create_client_sync.call_count == 3
            assert result == mock_client

    @patch('runtime.database_manager.libsql_client')
    def test_turso_fallback_to_sqlite(self, mock_libsql):
        """Test fallback to SQLite when Turso initialization fails."""
        db_manager = DatabaseManager()
        mock_app = MagicMock()

        # Mock libsql client to always fail
        mock_libsql.create_client_sync.side_effect = Exception("Always fails")

        # Mock Database constructor for fallback
        with patch('runtime.database_manager.Database') as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_class.return_value = mock_db_instance

            with patch('builtins.print') as mock_print:
                result = db_manager._initialize_turso(mock_app, "libsql://test.turso.io")

                # Should fall back to SQLite
                assert result == mock_db_instance
                mock_print.assert_any_call("🔄 Falling back to SQLite database...")
                assert mock_app.config.db.uri == 'sqlite://bloggy_turso_fallback.db'

    @patch('runtime.database_manager.libsql_client')
    def test_turso_missing_dependency(self, mock_libsql):
        """Test behavior when libsql-client is not installed."""
        db_manager = DatabaseManager()
        mock_app = MagicMock()

        # Mock ImportError for libsql_client
        mock_libsql.side_effect = ImportError("No module named 'libsql_client'")

        # Should raise ImportError with helpful message
        with pytest.raises(ImportError) as exc_info:
            db_manager._initialize_turso(mock_app, "libsql://test.turso.io")

        assert "libsql-client is required" in str(exc_info.value)
        assert "pip install libsql-client" in str(exc_info.value)

    def test_initialize_with_turso_environment_variable(self):
        """Test initialization using TURSO_DATABASE_URL environment variable."""
        db_manager = DatabaseManager()
        mock_app = MagicMock()

        # Set environment variable
        os.environ['TURSO_DATABASE_URL'] = 'libsql://env-test.turso.io'

        with patch.object(db_manager, '_initialize_turso') as mock_init:
            mock_init.return_value = MagicMock()
            db_manager.initialize(mock_app)

            # Should use environment variable
            mock_init.assert_called_once_with(mock_app, 'libsql://env-test.turso.io')

            # Clean up
            del os.environ['TURSO_DATABASE_URL']

    def test_prefer_turso_over_database_url(self):
        """Test that TURSO_DATABASE_URL takes precedence over DATABASE_URL."""
        db_manager = DatabaseManager()
        mock_app = MagicMock()

        # Set both environment variables
        os.environ['TURSO_DATABASE_URL'] = 'libsql://turso-test.turso.io'
        os.environ['DATABASE_URL'] = 'sqlite://bloggy.db'

        with patch.object(db_manager, '_initialize_turso') as mock_init:
            mock_init.return_value = MagicMock()
            db_manager.initialize(mock_app)

            # Should prefer Turso URL
            mock_init.assert_called_once_with(mock_app, 'libsql://turso-test.turso.io')

            # Clean up
            del os.environ['TURSO_DATABASE_URL']
            del os.environ['DATABASE_URL']


if __name__ == '__main__':
    pytest.main([__file__])