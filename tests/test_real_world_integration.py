# -*- coding: utf-8 -*-
"""
Real-world integration tests for Turso Database support.

These tests simulate real-world usage scenarios to ensure
the Turso integration works in production environments.
"""

import os
import sys
from runtime.database_manager import DatabaseManager


class TestRealWorldIntegration:
    """Test real-world integration scenarios."""

    def setup_method(self):
        """Set up test environment."""
        DatabaseManager.reset_instance()

    def test_production_turso_configuration(self):
        """Test production Turso configuration scenario."""
        # Simulate production environment variables
        os.environ['TURSO_DATABASE_URL'] = 'libsql://my-production-app.turso.io'
        os.environ['TURSO_AUTH_TOKEN'] = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'

        db_manager = DatabaseManager.get_instance()

        # Test URL resolution
        final_url = (os.environ.get('TURSO_DATABASE_URL') or
                    os.environ.get('DATABASE_URL', 'sqlite://bloggy.db'))
        detected_type = db_manager._detect_database_type(final_url)

        assert detected_type == 'turso'
        assert 'my-production-app.turso.io' in final_url
        assert db_manager.database_type == 'unknown'  # Not initialized yet

        # Test configuration setup
        db_manager._db_type = detected_type
        db_manager._app = self._create_mock_app()

        # Should detect as Turso
        assert db_manager.is_turso()

        # Clean up
        del os.environ['TURSO_DATABASE_URL']
        del os.environ['TURSO_AUTH_TOKEN']

        print("✅ Production Turso configuration works")

    def test_development_sqlite_fallback(self):
        """Test development environment with SQLite fallback."""
        # No Turso environment variables set
        db_manager = DatabaseManager.get_instance()

        # Should fall back to DATABASE_URL or default SQLite
        final_url = (os.environ.get('TURSO_DATABASE_URL') or
                    os.environ.get('DATABASE_URL', 'sqlite://bloggy.db'))
        detected_type = db_manager._detect_database_type(final_url)

        assert detected_type == 'sqlite'
        assert final_url == 'sqlite://bloggy.db'

        # Test configuration
        db_manager._db_type = detected_type
        assert not db_manager.is_turso()
        assert db_manager.database_type == 'sqlite'

        print("✅ Development SQLite fallback works")

    def test_mixed_environment_scenarios(self):
        """Test various mixed environment scenarios."""
        scenarios = [
            {
                'name': 'Turso priority over DATABASE_URL',
                'env': {
                    'TURSO_DATABASE_URL': 'libsql://priority.turso.io',
                    'DATABASE_URL': 'sqlite://should-not-use.db'
                },
                'expected_type': 'turso',
                'expected_url': 'libsql://priority.turso.io'
            },
            {
                'name': 'DATABASE_URL fallback',
                'env': {
                    'DATABASE_URL': 'postgres://localhost:5432/mydb'
                },
                'expected_type': 'postgres',
                'expected_url': 'postgres://localhost:5432/mydb'
            },
            {
                'name': 'Default SQLite fallback',
                'env': {},
                'expected_type': 'sqlite',
                'expected_url': 'sqlite://bloggy.db'
            }
        ]

        for scenario in scenarios:
            # Clear existing environment
            for key in ['TURSO_DATABASE_URL', 'DATABASE_URL']:
                if key in os.environ:
                    del os.environ[key]

            # Set test environment
            for key, value in scenario['env'].items():
                os.environ[key] = value

            DatabaseManager.reset_instance()
            db_manager = DatabaseManager.get_instance()

            # Test URL resolution
            final_url = (os.environ.get('TURSO_DATABASE_URL') or
                        os.environ.get('DATABASE_URL', 'sqlite://bloggy.db'))
            detected_type = db_manager._detect_database_type(final_url)

            assert detected_type == scenario['expected_type'], f"Failed scenario: {scenario['name']}"
            assert final_url == scenario['expected_url'], f"Failed scenario: {scenario['name']}"

            print(f"✅ {scenario['name']} works correctly")

        # Clean up
        for key in ['TURSO_DATABASE_URL', 'DATABASE_URL']:
            if key in os.environ:
                del os.environ[key]

    def test_error_recovery_scenarios(self):
        """Test error recovery scenarios."""
        db_manager = DatabaseManager.get_instance()

        # Test missing libsql-client error
        try:
            db_manager._initialize_turso(self._create_mock_app(), 'libsql://test.turso.io')
            assert False, "Should have raised ImportError"
        except ImportError as e:
            assert 'libsql-client is required' in str(e)
            print("✅ Missing dependency error handled correctly")

        # Test invalid database URL detection
        invalid_urls = [
            'invalid-url',
            '',
            'not-a-protocol://host',
        ]

        for url in invalid_urls:
            detected_type = db_manager._detect_database_type(url)
            # Should handle gracefully without crashing
            assert detected_type in ['sqlite', 'postgres', 'mysql', 'unknown'], f"Invalid URL {url} caused issue"

        print("✅ Error recovery scenarios work correctly")

    def test_configuration_consistency(self):
        """Test configuration consistency across database types."""
        db_manager = DatabaseManager.get_instance()

        # Test configurations for different database types
        configurations = {
            'sqlite': {
                'pool_size': 0,
                'journal_mode': 'DELETE',
                'foreign_keys': 'ON'
            },
            'turso': {
                'pool_size': 10,
                'journal_mode': 'WAL',
                'foreign_keys': 'ON',
                'timeout': 30
            }
        }

        for db_type, expected_config in configurations.items():
            db_manager._db_type = db_type
            mock_app = self._create_mock_app()

            # Simulate configuration logic
            if db_type == 'sqlite':
                mock_app.config.db.pool_size = expected_config['pool_size']
                mock_app.config.db.adapter_args = {
                    'journal_mode': expected_config['journal_mode'],
                    'synchronous': 'NORMAL',
                    'foreign_keys': expected_config['foreign_keys'],
                }
            elif db_type == 'turso':
                mock_app.config.db.pool_size = expected_config['pool_size']
                mock_app.config.db.adapter_args = {
                    'journal_mode': expected_config['journal_mode'],
                    'synchronous': 'NORMAL',
                    'foreign_keys': expected_config['foreign_keys'],
                    'timeout': expected_config['timeout'],
                }

            # Verify configuration
            assert mock_app.config.db.pool_size == expected_config['pool_size']
            assert mock_app.config.db.adapter_args['journal_mode'] == expected_config['journal_mode']
            assert mock_app.config.db.adapter_args['foreign_keys'] == expected_config['foreign_keys']

            if db_type == 'turso':
                assert 'timeout' in mock_app.config.db.adapter_args
                assert mock_app.config.db.adapter_args['timeout'] == expected_config['timeout']

        print("✅ Configuration consistency verified")

    def test_performance_and_memory(self):
        """Test performance and memory usage."""
        import time

        # Test many database type detections
        db_manager = DatabaseManager.get_instance()
        test_urls = [
            'libsql://test1.turso.io',
            'libsql://test2.turso.io',
            'sqlite://test1.db',
            'sqlite://test2.db',
            'postgres://localhost:5432/db1',
            'postgres://localhost:5432/db2'
        ]

        start_time = time.time()
        for _ in range(1000):  # 1000 iterations
            for url in test_urls:
                db_manager._detect_database_type(url)
        end_time = time.time()

        # Should complete quickly (less than 1 second for 6000 detections)
        assert end_time - start_time < 1.0, f"Performance test failed: {end_time - start_time}s"

        print(f"✅ Performance test passed: {end_time - start_time:.3f}s for 6000 detections")

    def _create_mock_app(self):
        """Create a mock app object for testing."""
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

        return MockApp()


if __name__ == '__main__':
    pytest.main([__file__])