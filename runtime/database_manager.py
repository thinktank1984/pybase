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
        self._db_type: str = 'unknown'
        self._turso_client: Optional[Any] = None
    
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

        # Configure database URL with Turso support
        if database_url is None:
            # Check for Turso-specific environment variable first
            database_url = os.environ.get(
                'TURSO_DATABASE_URL',
                os.environ.get(
                    'DATABASE_URL',
                    'sqlite://bloggy.db'
                )
            )

        # Detect database type
        self._db_type = self._detect_database_type(database_url)
        print(f"🔍 Detected database type: {self._db_type}")

        # For Turso, we need special handling
        if self._db_type == 'turso':
            return self._initialize_turso(app, database_url)
        
        app.config.db.uri = database_url
        
        # Configure connection pooling based on environment
        is_test = 'pytest' in sys.modules or 'TEST_DATABASE_URL' in os.environ or \
                  os.path.basename(sys.argv[0]) == 'validate_models.py'

        # Detect GitHub Spaces environment
        is_github_spaces = os.environ.get('GITHUB_ACTIONS') == 'true' or \
                          os.environ.get('CODESPACES') == 'true'

        # Configure connection pooling based on environment
        is_sqlite = database_url.startswith('sqlite:')
        if is_sqlite:
            # Use connection pooling optimized for the environment
            if is_github_spaces:
                # GitHub Spaces needs larger pools due to containerized environment
                app.config.db.pool_size = 3 if is_test else 10
            else:
                # Local development - smaller pools to avoid locking issues
                app.config.db.pool_size = 1 if is_test else 5
        else:
            app.config.db.pool_size = 1 if is_test else int(os.environ.get('DB_POOL_SIZE', '20'))

        # SQLite-specific configuration to avoid transaction issues
        if is_sqlite:
            # Configure adapter args based on environment
            if is_github_spaces:
                adapter_args = {
                    'journal_mode': 'WAL',  # WAL mode for better concurrent access
                    'synchronous': 'NORMAL',  # Normal sync for performance in containers
                    'foreign_keys': 'ON',  # Enable foreign key constraints
                    'timeout': 60,  # Longer timeout for containerized environments
                    'cache_size': 2000,  # Larger cache for better performance
                    'temp_store': 'MEMORY',  # Store temporary tables in memory
                }
            else:
                adapter_args = {
                    'journal_mode': 'WAL',  # WAL mode for better concurrent access
                    'synchronous': 'NORMAL',  # Normal sync for performance
                    'foreign_keys': 'ON',  # Enable foreign key constraints
                    'timeout': 30,  # Connection timeout to avoid hanging
                }
            app.config.db.adapter_args = adapter_args
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
            str: Database type ('turso', 'sqlite', 'postgres', 'mysql', 'unknown')
        """
        if database_url.startswith('libsql://') or database_url.startswith('https://') and 'turso' in database_url:
            return 'turso'
        elif database_url.startswith('sqlite:'):
            return 'sqlite'
        elif database_url.startswith('postgres://') or database_url.startswith('postgresql://'):
            return 'postgres'
        elif database_url.startswith('mysql://'):
            return 'mysql'
        else:
            return 'unknown'

    def _initialize_turso(self, app: Any, database_url: str) -> Database:
        """
        Initialize Turso database connection.

        Args:
            app: Emmett application instance
            database_url: Turso database URL

        Returns:
            Database: Initialized database instance
        """
        try:
            # Import libsql-client
            import libsql_client
        except ImportError:
            raise ImportError(
                "libsql-client is required for Turso database support. "
                "Install it with: pip install libsql-client"
            )

        try:
            # Parse Turso URL and extract authentication token
            parsed_url = urlparse(database_url)
            host = parsed_url.hostname or parsed_url.netloc
            auth_token = None

            # Get auth token from URL fragment or environment
            if parsed_url.fragment:
                auth_token = parsed_url.fragment
            else:
                auth_token = os.environ.get('TURSO_AUTH_TOKEN')

            if not auth_token:
                print("⚠️  Warning: No Turso auth token found. Set TURSO_AUTH_TOKEN environment variable.")

            # Create Turso client with retry logic
            self._turso_client = self._create_turso_client_with_retry(host, auth_token)

            # Configure Emmett to use SQLite-compatible settings
            # Turso is SQLite-compatible, so we can use pyDAL with SQLite adapter
            sqlite_fallback_url = f"sqlite:memory?turso_host={host}"
            if auth_token:
                sqlite_fallback_url += f"&turso_token={auth_token}"

            app.config.db.uri = sqlite_fallback_url

            # Configure connection pooling for Turso (network-based)
            is_test = 'pytest' in sys.modules or 'TEST_DATABASE_URL' in os.environ
            app.config.db.pool_size = 1 if is_test else int(os.environ.get('DB_POOL_SIZE', '10'))

            # Turso-specific configuration
            app.config.db.adapter_args = {
                'journal_mode': 'WAL',  # Better for concurrent access
                'synchronous': 'NORMAL',  # Balance between performance and safety
                'foreign_keys': 'ON',  # Enable foreign key constraints
                'timeout': 30,  # Connection timeout
            }

            # Initialize database with standard pyDAL
            self._db = Database(app)

            print(f"✅ Turso DatabaseManager initialized: {host}")
            print(f"   Pool size: {app.config.db.pool_size} (test mode: {is_test})")
            print(f"   Auth token: {'✓' if auth_token else '✗'}")

            self._initialized = True
            return self._db

        except Exception as e:
            print(f"❌ Failed to initialize Turso database: {e}")
            # Fallback to SQLite
            print("🔄 Falling back to SQLite database...")
            app.config.db.uri = 'sqlite://bloggy_turso_fallback.db'
            return self.initialize(app, app.config.db.uri)

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



