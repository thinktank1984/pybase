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
from typing import Optional, Any, Tuple
from emmett.orm import Database


class DatabaseManager:
    """
    Singleton class for centralized database management.
    
    This class manages the database instance, connections, and provides
    helper methods for database operations. It ensures only one database
    instance exists throughout the application lifecycle.
    
    Usage:
        # Initialize (typically in app.py)
        db_manager = DatabaseManager.get_instance()
        db_manager.initialize(app)
        
        # Use in other modules
        db_manager = DatabaseManager.get_instance()
        with db_manager.connection():
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
        self._connection_pipe: Optional[Any] = None
    
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
        Initialize the database with the given Emmett app.
        
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
        
        # Configure database URL
        if database_url is None:
            database_url = os.environ.get(
                'DATABASE_URL',
                'postgres://bloggy:bloggy_password@postgres:5432/bloggy'
            )
        
        app.config.db.uri = database_url
        
        # Configure connection pooling based on environment
        is_test = 'pytest' in sys.modules or 'TEST_DATABASE_URL' in os.environ or \
                  os.path.basename(sys.argv[0]) == 'validate_models.py'

        # Use pool_size=0 (no pooling) for tests and SQLite to avoid transaction issues
        is_sqlite = database_url.startswith('sqlite:')
        app.config.db.pool_size = 0 if is_test or is_sqlite else int(os.environ.get('DB_POOL_SIZE', '20'))

        # SQLite-specific configuration to avoid transaction issues
        if is_sqlite:
            app.config.db.adapter_args = {
                'journal_mode': 'WAL',  # Write-Ahead Logging for better concurrency
                'synchronous': 'NORMAL',  # Less strict sync for development
                'foreign_keys': 'ON',  # Enable foreign key constraints
            }
        else:
            app.config.db.adapter_args = {
                'sslmode': 'prefer',  # Use SSL if available, but don't require it
            }
        
        # Initialize database
        self._db = Database(app)
        
        print(f"✅ DatabaseManager initialized: {database_url}")
        print(f"   Pool size: {app.config.db.pool_size} (test mode: {is_test})")
        
        self._initialized = True
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
    
    def define_models(self, *models):
        """
        Register models with the database.
        
        Args:
            *models: Model classes to register
        """
        if self._db is None:
            raise RuntimeError("Database not initialized")
        
        self._db.define_models(*models)
        print(f"✅ Registered {len(models)} models with database")
    
    def connection(self):
        """
        Get a database connection context manager.
        
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
        """Commit the current database transaction."""
        if self._db is None:
            raise RuntimeError("Database not initialized")
        
        self._db.commit()
    
    def rollback(self):
        """Rollback the current database transaction."""
        if self._db is None:
            raise RuntimeError("Database not initialized")
        
        self._db.rollback()
    
    def executesql(self, sql: str, *args, **kwargs):
        """
        Execute raw SQL query.
        
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
        Safely get first result from query.
        
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
        Get existing record or create new one.
        
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
        Create a pipeline component for explicit database connection management.
        
        This is required for PostgreSQL to ensure all database queries have
        access to a connection context.
        
        Returns:
            DatabaseConnectionPipe instance
        """
        from emmett.pipeline import Pipe
        
        db_instance = self._db
        
        class DatabaseConnectionPipe(Pipe):
            """
            Pipeline component that explicitly wraps requests in database connection contexts.
            
            This is required for PostgreSQL to ensure all database queries (including those
            in auth handlers) have access to a connection context.
            """
            async def open(self):
                """Establish database connection at start of request"""
                self._connection = db_instance.connection()  # type: ignore[union-attr]
                await self._connection.__aenter__()
            
            async def close(self):
                """Close database connection at end of request"""
                if hasattr(self, '_connection'):
                    try:
                        await self._connection.__aexit__(None, None, None)
                    except (KeyError, AttributeError):
                        # Connection already closed or doesn't exist - this is fine
                        # Can happen in test contexts or if connection was closed elsewhere
                        pass
        
        self._connection_pipe = DatabaseConnectionPipe()
        return self._connection_pipe
    
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



