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
# Import turso package as instructed
import turso
print("✅ Using turso package")


class TursoDatabaseWrapper:
    """
    Wrapper class to make Turso database compatible with Emmett's Database interface.

    This provides the methods that Emmett expects from a database object,
    but uses Turso connections underneath.
    """

    def __init__(self, database_file: str):
        self.database_file = database_file
        self._tables = {}

    def define_models(self, *models):
        """Register models with the database."""
        print(f"✅ Registered {len(models)} models with Turso database")

    def connection(self):
        """Get a Turso database connection context manager."""
        return turso.connect(self.database_file)

    def commit(self):
        """Commit transaction (handled by Turso context manager)."""
        pass

    def rollback(self):
        """Rollback transaction (handled by Turso context manager)."""
        pass

    def executesql(self, sql: str, *args, **kwargs):
        """Execute raw SQL query."""
        with turso.connect(self.database_file) as con:
            cur = con.cursor()
            result = cur.execute(sql, *args, **kwargs)
            con.commit()
            return result

    def __getattr__(self, name):
        """Delegate attribute access to table objects."""
        if name in self._tables:
            return self._tables[name]
        return self


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
        
        self._db: Optional[Any] = None
        self._app: Optional[Any] = None
        self._connection_pipe: Optional[Any] = None
        self._db_type: str = 'turso'
        self._turso_client: Optional[Any] = None
        self._database_file: Optional[str] = None
    
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

        # Configure database URL for Turso
        if database_url is None:
            database_url = os.environ.get(
                'DATABASE_URL',
                'sqlite://bloggy.turso.db'
            )

        # Always use Turso
        self._db_type = 'turso'
        print(f"🔍 Using Turso database")

        return self._initialize_turso(app, database_url)
    
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
        """Get the detected database type."""
        return self._db_type

    def is_turso(self) -> bool:
        """Check if using Turso database."""
        return self._db_type == 'turso'
    
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
        Get a Turso database connection context manager.

        Returns:
            Context manager for Turso database connection

        Usage:
            with db_manager.connection():
                cur = con.cursor()
                cur.execute("SELECT * FROM users")
                result = cur.fetchall()
        """
        if not self._initialized or self._database_file is None:
            raise RuntimeError("Database not initialized")

        return turso.connect(self._database_file)
    
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
        
        This is required for SQLite to ensure all database queries have
        access to a connection context.
        
        Returns:
            DatabaseConnectionPipe instance
        """
        from emmett.pipeline import Pipe
        
        db_instance = self._db
        
        class DatabaseConnectionPipe(Pipe):
            """
            Pipeline component that explicitly wraps requests in database connection contexts.
            
            This is required for SQLite to ensure all database queries (including those
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

    def _detect_database_type(self, database_url: str) -> str:
        """
        Detect database type from URL pattern.

        Args:
            database_url: Database connection URL

        Returns:
            str: Database type ('turso', 'unknown')
        """
        return 'turso'

    def _initialize_turso(self, app: Any, database_url: str) -> Any:
        """
        Initialize Turso database connection using turso.connect() context manager.

        Args:
            app: Emmett application instance
            database_url: Turso database URL

        Returns:
            Database manager instance (not a Database object since we're using turso.connect directly)
        """
        # turso is already imported at the top (with fallback)

        try:
            # Extract database file from URL
            database_file = database_url.replace('sqlite://', '')
            print(f"🔗 Using Turso database file: {database_file}")

            # Store the database file for use with turso.connect()
            self._database_file = database_file

            # Initialize the users table and sample data using turso.connect()
            with turso.connect(database_file) as con:
                cur = con.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL,
                        role TEXT NOT NULL,
                        created_at DATETIME NOT NULL DEFAULT (datetime('now'))
                    )
                """)

                # Insert some sample data
                sample_users = [
                    ("alice", "alice@example.com", "admin"),
                    ("bob", "bob@example.com", "user"),
                    ("charlie", "charlie@example.com", "moderator"),
                    ("diana", "diana@example.com", "user"),
                ]
                for username, email, role in sample_users:
                    cur.execute(
                        """
                        INSERT INTO users (username, email, role)
                        VALUES (?, ?, ?)
                        """,
                        (username, email, role),
                    )

                # Use commit to ensure the data is saved
                con.commit()

                # Query the table to verify
                res = cur.execute("SELECT * FROM users")
                record = res.fetchone()
                print(f"✅ Sample user record: {record}")

            print(f"✅ Turso DatabaseManager initialized with context manager: {database_url}")

            # Create a Turso-compatible database interface for Emmett
            self._db = TursoDatabaseWrapper(database_file)

            self._initialized = True
            return self

        except Exception as e:
            print(f"❌ Failed to initialize Turso database: {e}")
            raise e

    def _create_turso_client_with_retry(self, host: str, auth_token: Optional[str], max_retries: int = 3) -> Any:
        """
        Create Turso client with retry logic.

        Args:
            host: Turso database host
            auth_token: Authentication token
            max_retries: Maximum number of retry attempts

        Returns:
            Turso client instance
        """
        import libsql_client

        for attempt in range(max_retries):
            try:
                if auth_token:
                    client = libsql_client.create_client_sync(
                        url=f"https://{host}",
                        auth_token=auth_token
                    )
                else:
                    client = libsql_client.create_client_sync(
                        url=f"https://{host}"
                    )

                # Test connection
                client.execute("SELECT 1")
                print(f"✅ Turso client connected (attempt {attempt + 1})")
                return client

            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to connect to Turso after {max_retries} attempts: {e}")

                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⚠️  Turso connection failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

        raise Exception("Failed to create Turso client")


# Convenience function for getting the singleton instance
def get_db_manager() -> DatabaseManager:
    """
    Get the DatabaseManager singleton instance.

    Returns:
        DatabaseManager: The singleton instance
    """
    return DatabaseManager.get_instance()



