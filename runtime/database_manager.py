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

# Import turso package for compatibility
try:
    import turso
    print("✅ Using turso package - SQLite compatible mode")
    TURSO_AVAILABLE = True
except ImportError:
    print("⚠️  turso package not available, using standard SQLite")
    TURSO_AVAILABLE = False


class TursoDatabaseAdapter:
    """
    Adapter class to configure Turso database for Emmett ORM.

    This adapter configures Emmett's Database to work with Turso
    by setting up the proper SQLite-compatible configuration.
    """

    @staticmethod
    def configure_turso_database(app: Any, database_url: str) -> Database:
        """
        Configure Emmett Database to use Turso as SQLite-compatible backend.

        Args:
            app: Emmett application instance
            database_url: Database connection URL

        Returns:
            Database: Configured Emmett Database instance
        """
        # Configure the database URI for Emmett
        # Turso is SQLite-compatible, so we can use sqlite:// prefix
        app.config.db.uri = database_url

        # Set additional configuration for Turso compatibility
        app.config.db.adapter = 'sqlite'
        app.config.db.folder = 'runtime'  # Set to runtime directory

        # Create and return the Emmett Database instance
        db = Database(app)

        print(f"✅ Configured Emmett Database with Turso: {database_url}")
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
        self._app: Optional[Any] = None
        self._db_type: str = 'sqlite'  # Using SQLite adapter for Turso compatibility
    
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
    
    def initialize(self, app: Any, database_url: Optional[str] = None) -> Database:
        """
        Initialize the database with the given Emmett app using Turso SQLite compatibility.

        Args:
            app: Emmett application instance
            database_url: Optional database URL (defaults to environment variable)

        Returns:
            Database: Initialized database instance
        """
        if self._initialized:
            print("⚠️  DatabaseManager already initialized, returning existing instance")
            return self._db  # type: ignore[return-value]

        self._app = app

        # Configure database URL for Turso (SQLite-compatible)
        if database_url is None:
            database_url = os.environ.get(
                'DATABASE_URL',
                'sqlite://bloggy.turso.db'
            )

        print(f"🔍 Using Turso database with SQLite compatibility: {database_url}")

        # Use the Turso adapter to configure Emmett Database
        self._db = TursoDatabaseAdapter.configure_turso_database(app, database_url)
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
        """Get the database type (SQLite for Turso compatibility)."""
        return self._db_type

    def is_turso(self) -> bool:
        """Check if using Turso database (SQLite compatible)."""
        return True  # Always True since we're using Turso
    
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
        Get existing record or create new one using Emmett ORM.

        Args:
            model: Emmett Model class
            **kwargs: Fields to match/create

        Returns:
            (instance, created) tuple where created is True if new record was created
        """
        with self.connection():
            # Try to find existing
            query = model.where(lambda m: all(
                getattr(m, k) == v for k, v in kwargs.items()
            ))
            existing = self.safe_first(query)

            if existing:
                return (existing, False)

            # Create new
            instance = model.create(**kwargs)
            self.commit()
            return (instance, True)

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

    

# Convenience function for getting the singleton instance
def get_db_manager() -> DatabaseManager:
    """
    Get the DatabaseManager singleton instance.

    Returns:
        DatabaseManager: The singleton instance
    """
    return DatabaseManager.get_instance()



