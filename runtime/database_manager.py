# -*- coding: utf-8 -*-
"""
DatabaseManager Singleton - Centralized database management for Emmett applications.

This module provides a singleton class that manages all database-related concerns:
- Database initialization and configuration
- Connection management and pooling
- Model registration
- Helper methods for common database operations
"""

import os
import sys
import re
import time
from typing import Optional, Any, Tuple
from urllib.parse import urlparse
from emmett.orm import Database

# Using native SQLite - no external dependencies required


class SQLiteDatabaseAdapter:
    """
    Adapter class to configure SQLite database for Emmett ORM.

    This adapter configures Emmett's Database to work with SQLite
    by setting up the proper native SQLite configuration.
    """

    @staticmethod
    def configure_sqlite_database(app: Any, database_url: str, pool_size: int = 10,
                                  enable_wal: bool = True, keep_alive_timeout: int = 300) -> Database:
        """
        Configure Emmett Database to use native SQLite backend with enhanced concurrency.

        Args:
            app: Emmett application instance
            database_url: Database connection URL
            pool_size: Connection pool size (default: 10)
            enable_wal: Enable WAL mode for better concurrency (default: True)
            keep_alive_timeout: Connection reuse timeout in seconds (default: 300)

        Returns:
            Database: Configured Emmett Database instance
        """
        # Extract database file from URL
        database_file = database_url.replace('sqlite://', '')

        # Configure the database URI for Emmett
        app.config.db.uri = database_url

        # Set configuration for native SQLite with enhanced features
        app.config.db.adapter = 'sqlite'
        app.config.db.database = database_file  # Set explicit database file path

        # Enable connection pooling for better concurrency
        app.config.db.pool_size = pool_size
        app.config.db.keep_alive_timeout = keep_alive_timeout

        # Configure SQLite adapter arguments for WAL mode and better performance
        adapter_args = {
            'journal_mode': 'WAL' if enable_wal else 'DELETE',
            'synchronous': 'NORMAL',
            'foreign_keys': 'ON',
            'cache_size': 2000,  # 2MB cache
            'temp_store': 'memory',
            'mmap_size': 268435456,  # 256MB memory mapped I/O
        }

        if enable_wal:
            # Additional WAL optimizations
            adapter_args.update({
                'wal_autocheckpoint': 1000,
                'wal_checkpoint_mode': 'PASSIVE'
            })

        app.config.db.adapter_args = adapter_args

        # Create and return the Emmett Database instance
        db = Database(app)

        print(f"✅ Configured Enhanced SQLite Database:")
        print(f"   - Database: {database_url}")
        print(f"   - Pool Size: {pool_size}")
        print(f"   - WAL Mode: {enable_wal}")
        print(f"   - Keep Alive: {keep_alive_timeout}s")
        return db


class DatabaseManager:
    """
    Singleton class for centralized database management using Emmett ORM.

    This class manages the database instance, connections, and provides
    helper methods for database operations. It ensures only one database
    instance exists throughout the application lifecycle.

    Usage:
        # Initialize (typically in app.py)
        db_manager = DatabaseManager.get_instance()
        db_manager.initialize(app)

        # Use in other modules
        db_manager = DatabaseManager.get_instance()
        with db_manager.db.connection():
            user = User.create(...)
    """

    _instance: Optional['DatabaseManager'] = None
    _initialized: bool = False

    def __init__(self):
        """Private constructor - use get_instance() instead."""
        if DatabaseManager._instance is not None:
            raise RuntimeError(
                "DatabaseManager is a singleton. Use DatabaseManager.get_instance() instead."
            )

        self._db: Optional[Database] = None
        self._read_db: Optional[Database] = None
        self._write_db: Optional[Database] = None
        self._app: Optional[Any] = None
        self._db_type: str = 'sqlite'  # Using native SQLite
        self._pool_size: int = 10
        self._enable_wal: bool = True
        self._keep_alive_timeout: int = 300
    
    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        """
        Get the singleton instance of DatabaseManager.
        
        Returns:
            DatabaseManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """
        Reset the singleton instance (useful for testing).
        
        Warning: This should only be used in test environments.
        """
        cls._instance = None
        cls._initialized = False
    
    def initialize(self, app: Any, database_url: Optional[str] = None,
                   pool_size: Optional[int] = None, enable_wal: Optional[bool] = None,
                   keep_alive_timeout: Optional[int] = None,
                   separate_read_write: bool = True) -> Database:
        """
        Initialize the database with the given Emmett app using enhanced SQLite configuration.

        Args:
            app: Emmett application instance
            database_url: Optional database URL (defaults to environment variable)
            pool_size: Connection pool size (defaults to 10)
            enable_wal: Enable WAL mode (defaults to True)
            keep_alive_timeout: Connection reuse timeout in seconds (defaults to 300)
            separate_read_write: Create separate read/write instances (defaults to True)

        Returns:
            Database: Main database instance
        """
        if self._initialized:
            print("⚠️  DatabaseManager already initialized, returning existing instance")
            return self._db  # type: ignore[return-value]

        self._app = app

        # Set configuration parameters
        if pool_size is not None:
            self._pool_size = pool_size
        if enable_wal is not None:
            self._enable_wal = enable_wal
        if keep_alive_timeout is not None:
            self._keep_alive_timeout = keep_alive_timeout

        # Configure database URL for SQLite
        if database_url is None:
            database_url = os.environ.get(
                'DATABASE_URL',
                'sqlite://runtime/databases/main.db'
            )

        print(f"🔍 Initializing Enhanced SQLite Database: {database_url}")
        print(f"   - Pool Size: {self._pool_size}")
        print(f"   - WAL Mode: {self._enable_wal}")
        print(f"   - Separate R/W: {separate_read_write}")

        if separate_read_write:
            # Create separate read and write database instances
            print("   - Creating separate READ and WRITE database instances...")

            # Main database (for backward compatibility)
            self._db = SQLiteDatabaseAdapter.configure_sqlite_database(
                app, database_url, self._pool_size, self._enable_wal, self._keep_alive_timeout
            )

            # Read-optimized database
            read_config = self._create_read_app_config(app, database_url)
            self._read_db = SQLiteDatabaseAdapter.configure_sqlite_database(
                read_config, database_url, max(self._pool_size * 2, 20),
                self._enable_wal, self._keep_alive_timeout
            )

            # Write-optimized database
            write_config = self._create_write_app_config(app, database_url)
            self._write_db = SQLiteDatabaseAdapter.configure_sqlite_database(
                write_config, database_url, max(self._pool_size // 2, 5),
                self._enable_wal, self._keep_alive_timeout
            )

            print(f"   - Read DB Pool: {max(self._pool_size * 2, 20)} connections")
            print(f"   - Write DB Pool: {max(self._pool_size // 2, 5)} connections")
        else:
            # Single database instance
            self._db = SQLiteDatabaseAdapter.configure_sqlite_database(
                app, database_url, self._pool_size, self._enable_wal, self._keep_alive_timeout
            )
            self._read_db = self._db
            self._write_db = self._db

        self._initialized = True

        # Define models that were passed in app.py
        # Models will be registered by app.py using db_manager.define_models()

        return self._db
    
    @property
    def db(self) -> Database:
        """
        Get the database instance.
        
        Returns:
            Database: The database instance
            
        Raises:
            RuntimeError: If database is not initialized
        """
        if self._db is None:
            raise RuntimeError(
                "Database not initialized. Call initialize(app) first."
            )
        return self._db
    
    @property
    def is_initialized(self) -> bool:
        """Check if the database manager is initialized."""
        return self._initialized

    @property
    def database_type(self) -> str:
        """Get the database type (SQLite)."""
        return self._db_type

    def is_turso(self) -> bool:
        """Check if using Turso database."""
        return False  # Now using native SQLite
    
    def define_models(self, *models):
        """
        Register models with the database using Emmett's model registration.

        Args:
            *models: Model classes to register
        """
        if self._db is None:
            raise RuntimeError("Database not initialized")

        # Use Emmett's built-in model definition
        self._db.define_models(*models)
        print(f"✅ Registered {len(models)} models with Emmett Database")

    def connection(self):
        """
        Get a database connection context manager using Emmett's connection management.

        Returns:
            Context manager for database connection

        Usage:
            with db_manager.connection():
                user = User.create(...)
        """
        if self._db is None:
            raise RuntimeError("Database not initialized")

        return self._db.connection()
    
    def commit(self):
        """Commit the current database transaction using Emmett's transaction management."""
        if self._db is None:
            raise RuntimeError("Database not initialized")

        self._db.commit()

    def rollback(self):
        """Rollback the current database transaction using Emmett's transaction management."""
        if self._db is None:
            raise RuntimeError("Database not initialized")

        self._db.rollback()

    def executesql(self, sql: str, *args, **kwargs):
        """
        Execute raw SQL query using Emmett's database interface.

        Args:
            sql: SQL query string
            *args: Positional arguments for query
            **kwargs: Keyword arguments for query

        Returns:
            Query result
        """
        if self._db is None:
            raise RuntimeError("Database not initialized")

        return self._db.executesql(sql, *args, **kwargs)
    
    def safe_first(self, query, default=None):
        """
        Safely get first result from query using Emmett's query interface.

        Args:
            query: Emmett query object or Set
            default: Value to return if no results

        Returns:
            First result or default value
        """
        try:
            with self.connection():
                # Check if query has select method (Set object)
                if hasattr(query, 'select'):
                    result = query.select().first()
                else:
                    result = query.first()
                return result if result else default
        except Exception as e:
            print(f"Query error: {e}")
            return default

    def get_or_create(self, model, **kwargs) -> Tuple[Any, bool]:
        """
        Get existing record or create new one using write-optimized connection.

        Args:
            model: Emmett Model class
            **kwargs: Fields to match/create

        Returns:
            (instance, created) tuple where created is True if new record was created
        """
        # Use read connection for querying, write connection for creating
        with self.read_connection():
            # Try to find existing
            query = model.where(lambda m: all(
                getattr(m, k) == v for k, v in kwargs.items()
            ))
            existing = self.safe_first(query)

            if existing:
                return (existing, False)

        # Use write connection for creating
        with self.write_connection():
            # Create new
            instance = model.create(**kwargs)
            self.commit()
            return (instance, True)

    def safe_select(self, model, *args, **kwargs):
        """
        Safely select records using read-optimized connection.

        Args:
            model: Emmett Model class
            *args: Arguments for query
            **kwargs: Keyword arguments for query

        Returns:
            List of records or empty list if error
        """
        try:
            with self.read_connection():
                return model.select(*args, **kwargs)
        except Exception as e:
            print(f"Select error: {e}")
            return []

    def safe_first_read(self, query, default=None):
        """
        Safely get first result from query using read-optimized connection.

        Args:
            query: Emmett query object or Set
            default: Value to return if no results

        Returns:
            First result or default value
        """
        try:
            with self.read_connection():
                # Check if query has select method (Set object)
                if hasattr(query, 'select'):
                    result = query.select().first()
                else:
                    result = query.first()
                return result if result else default
        except Exception as e:
            print(f"Query error: {e}")
            return default

    def batch_insert(self, model, records: list) -> list:
        """
        Batch insert records using write-optimized connection for better performance.

        Args:
            model: Emmett Model class
            records: List of dictionaries with field values

        Returns:
            List of created instances
        """
        created_instances = []
        with self.write_connection():
            for record_data in records:
                try:
                    instance = model.create(**record_data)
                    created_instances.append(instance)
                except Exception as e:
                    print(f"Batch insert error for record {record_data}: {e}")
                    continue
            self.commit()
        return created_instances

    def get_connection_stats(self) -> dict:
        """
        Get database connection statistics and pool information.

        Returns:
            Dictionary with connection statistics
        """
        stats = {
            'pool_size': self._pool_size,
            'enable_wal': self._enable_wal,
            'keep_alive_timeout': self._keep_alive_timeout,
            'separate_read_write': self._read_db != self._write_db,
            'main_db_configured': self._db is not None,
            'read_db_configured': self._read_db is not None,
            'write_db_configured': self._write_db is not None,
        }

        if self._read_db and self._write_db:
            stats.update({
                'read_pool_size': max(self._pool_size * 2, 20),
                'write_pool_size': max(self._pool_size // 2, 5),
            })

        return stats

    def create_connection_pipe(self):
        """
        Create a pipeline component for database connection management using Emmett's built-in pipe.

        Returns:
            Database pipe instance from Emmett's Database
        """
        if self._db is None:
            raise RuntimeError("Database not initialized")

        # Use Emmett's built-in database pipe
        return self._db.pipe
    
    def patch_row_methods(self, patches: dict):
        """
        Apply custom methods to Row classes for models.
        
        This allows methods defined on Model classes to work on Row objects
        returned from queries.
        
        Args:
            patches: Dictionary mapping table names to method dictionaries
                     Example: {'roles': {'get_permissions': func}, 'posts': {'can_edit': func}}
        """
        if self._db is None:
            raise RuntimeError("Database not initialized")
        
        try:
            for table_name, methods in patches.items():
                table = getattr(self._db, table_name, None)
                if table and hasattr(table, '_rowclass'):
                    for method_name, method_func in methods.items():
                        setattr(table._rowclass, method_name, method_func)
                    print(f"✅ Patched {len(methods)} methods on {table_name} Row class")
        except Exception as e:
            print(f"⚠️  Warning: Could not patch Row methods: {e}")
    
    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying database instance.
        
        This allows db_manager.users to work like db.users
        """
        if self._db is None:
            raise RuntimeError("Database not initialized")
        
        return getattr(self._db, name)
    
    def __call__(self, *args, **kwargs):
        """
        Delegate calls to the underlying database instance.
        
        This allows db_manager(query) to work like db(query)
        """
        if self._db is None:
            raise RuntimeError("Database not initialized")
        
        return self._db(*args, **kwargs)

    def _create_read_app_config(self, app: Any, database_url: str) -> Any:
        """Create a read-optimized app configuration."""
        from emmett import App

        read_app = App(__name__ + "_read")
        read_app.config.db.uri = database_url
        read_app.config.db.adapter = 'sqlite'
        read_app.config.db.database = database_url.replace('sqlite://', '')
        read_app.config.db.pool_size = max(self._pool_size * 2, 20)
        read_app.config.db.keep_alive_timeout = self._keep_alive_timeout

        # Read-optimized adapter arguments
        read_adapter_args = {
            'journal_mode': 'WAL' if self._enable_wal else 'DELETE',
            'synchronous': 'NORMAL',
            'foreign_keys': 'ON',
            'cache_size': 4000,  # 4MB cache for reads
            'temp_store': 'memory',
            'mmap_size': 536870912,  # 512MB memory mapped I/O for reads
            'readonly': False,  # SQLite doesn't support true readonly mode
        }

        if self._enable_wal:
            read_adapter_args.update({
                'wal_autocheckpoint': 2000,
                'wal_checkpoint_mode': 'PASSIVE'
            })

        read_app.config.db.adapter_args = read_adapter_args
        return read_app

    def _create_write_app_config(self, app: Any, database_url: str) -> Any:
        """Create a write-optimized app configuration."""
        from emmett import App

        write_app = App(__name__ + "_write")
        write_app.config.db.uri = database_url
        write_app.config.db.adapter = 'sqlite'
        write_app.config.db.database = database_url.replace('sqlite://', '')
        write_app.config.db.pool_size = max(self._pool_size // 2, 5)
        write_app.config.db.keep_alive_timeout = self._keep_alive_timeout

        # Write-optimized adapter arguments
        write_adapter_args = {
            'journal_mode': 'WAL' if self._enable_wal else 'DELETE',
            'synchronous': 'FULL',  # More durable for writes
            'foreign_keys': 'ON',
            'cache_size': 1000,  # 1MB cache
            'temp_store': 'memory',
            'mmap_size': 134217728,  # 128MB memory mapped I/O
        }

        if self._enable_wal:
            write_adapter_args.update({
                'wal_autocheckpoint': 500,  # More frequent checkpoints for writes
                'wal_checkpoint_mode': 'RESTART'
            })

        write_app.config.db.adapter_args = write_adapter_args
        return write_app

    def read_connection(self):
        """
        Get a read-optimized database connection context manager.

        Returns:
            Context manager for read database connection

        Usage:
            with db_manager.read_connection():
                data = User.select().all()
        """
        if self._read_db is None:
            raise RuntimeError("Database not initialized")
        return self._read_db.connection()

    def write_connection(self):
        """
        Get a write-optimized database connection context manager.

        Returns:
            Context manager for write database connection

        Usage:
            with db_manager.write_connection():
                user = User.create(...)
                db.commit()
        """
        if self._write_db is None:
            raise RuntimeError("Database not initialized")
        return self._write_db.connection()

    def get_read_db(self) -> Database:
        """
        Get the read-optimized database instance.

        Returns:
            Database: Read-optimized database instance
        """
        if self._read_db is None:
            raise RuntimeError("Database not initialized")
        return self._read_db

    def get_write_db(self) -> Database:
        """
        Get the write-optimized database instance.

        Returns:
            Database: Write-optimized database instance
        """
        if self._write_db is None:
            raise RuntimeError("Database not initialized")
        return self._write_db

# Convenience function for getting the singleton instance
def get_db_manager() -> DatabaseManager:
    """
    Get the DatabaseManager singleton instance.

    Returns:
        DatabaseManager: The singleton instance
    """
    return DatabaseManager.get_instance()



