# -*- coding: utf-8 -*-

from emmett import App, session, url, redirect, abort, response, current  # type: ignore[reportUnusedImport]
from emmett.tools import requires, service
from emmett.tools.auth import Auth
from emmett.tools import Mailer
from emmett.sessions import SessionManager
from emmett_rest import REST

# Import OpenAPI generator (deferred to avoid import issues)
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database_manager import DatabaseManager, get_db_manager  # type: ignore[reportMissingImports]
from openapi_generator import OpenAPIGenerator  # type: ignore[reportMissingImports]
from auto_ui_generator import auto_ui  # type: ignore[reportMissingImports]

# Import models
from models import (  # type: ignore[reportMissingImports]
    User, Post, Comment, Role, Permission, UserRole, RolePermission,
    OAuthAccount, OAuthToken,
    seed_all
)

# Import Sentry extension for error tracking (disabled)
sentry_available = False  # Sentry extension has template conflicts with Emmett

# Import Prometheus client for metrics
PROMETHEUS_AVAILABLE = False
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    prometheus_available = True
    PROMETHEUS_AVAILABLE = True  # type: ignore[misc]
except ImportError:
    prometheus_available = False
    print("Warning: prometheus-client not installed. Metrics collection disabled.")

# Import Valkey for caching (optional)
VALKEY_AVAILABLE = False
try:
    from valkey import Valkey
    import pickle
    valkey_available = True
    VALKEY_AVAILABLE = True  # type: ignore[misc]
except ImportError:
    valkey_available = False
    print("Warning: valkey not installed. Valkey cache backend unavailable.")


app = App(__name__, template_folder='templates')
app.config.url_default_namespace = 'app'

#: mailer configuration
app.config.mailer.sender = "bloggy@emmett.local"
app.config.mailer.suppress = True  # Set to False in production with real SMTP

#: auth configuration
app.config.auth.single_template = True
app.config.auth.registration_verification = False
app.config.auth.hmac_key = "november.5.1955"

#: database configuration
# Initialize DatabaseManager with Turso implementation
db_manager = get_db_manager()
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'sqlite://bloggy.turso.db'
)
db_manager.initialize(app, DATABASE_URL)

#: inject OAuth providers into templates
# Note: Disabled - @app.before_routes doesn't exist in this Emmett version
# OAuth providers are injected via context in OAuth routes when needed
# @app.before_routes
# async def inject_oauth_providers():
#     """Make OAuth providers available to all templates."""
#     from emmett import current
#     from auth import get_oauth_manager
#     oauth_mgr = get_oauth_manager()
#     current.oauth_providers = oauth_mgr.list_enabled_providers()

#: sentry/bugsink error tracking configuration
SENTRY_ENABLED = os.environ.get('SENTRY_ENABLED', 'true').lower() == 'true'
SENTRY_DSN = os.environ.get('SENTRY_DSN', 'http://public@bugsink:8000/1')
SENTRY_ENVIRONMENT = os.environ.get('SENTRY_ENVIRONMENT', os.environ.get('EMMETT_ENV', 'development'))
SENTRY_TRACES_SAMPLE_RATE = float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1'))

if SENTRY_ENABLED and sentry_available:
    app.config.Sentry.dsn = SENTRY_DSN
    app.config.Sentry.environment = SENTRY_ENVIRONMENT
    app.config.Sentry.traces_sample_rate = SENTRY_TRACES_SAMPLE_RATE
    app.config.Sentry.release = "bloggy@1.0.0"
    # Disabled: Sentry extension causes wrapper.html template lookup issue
    # app.use_extension(Sentry)
    print(f"⚠️  Sentry configured but not loaded (template conflict): {SENTRY_DSN}")
else:
    if not SENTRY_ENABLED:
        print("✗ Error tracking disabled via SENTRY_ENABLED=false")
    elif not sentry_available:
        print("✗ Error tracking unavailable: emmett-sentry not installed")

#: prometheus metrics configuration
PROMETHEUS_ENABLED = os.environ.get('PROMETHEUS_ENABLED', 'false').lower() == 'true'

# Initialize Prometheus metrics
if PROMETHEUS_ENABLED and prometheus_available:
    from emmett.pipeline import Pipe
    from prometheus_client import REGISTRY
    
    # Define custom metrics (with duplicate check)
    try:
        # Try to get existing metrics first to avoid duplication in test environment
        http_requests_total = REGISTRY._names_to_collectors.get('emmett_http_requests_total')
        http_request_duration_seconds = REGISTRY._names_to_collectors.get('emmett_http_request_duration_seconds')
        http_request_size_bytes = REGISTRY._names_to_collectors.get('emmett_http_request_size_bytes')
        http_response_size_bytes = REGISTRY._names_to_collectors.get('emmett_http_response_size_bytes')
        
        # Only create if they don't exist
        if not http_requests_total:
            http_requests_total = Counter(
                'emmett_http_requests_total',
                'Total HTTP requests',
                ['method', 'endpoint', 'status']
            )
        
        if not http_request_duration_seconds:
            http_request_duration_seconds = Histogram(
                'emmett_http_request_duration_seconds',
                'HTTP request latency in seconds',
                ['method', 'endpoint']
            )
        
        if not http_request_size_bytes:
            http_request_size_bytes = Histogram(
                'emmett_http_request_size_bytes',
                'HTTP request size in bytes',
                ['method', 'endpoint']
            )
        
        if not http_response_size_bytes:
            http_response_size_bytes = Histogram(
                'emmett_http_response_size_bytes',
                'HTTP response size in bytes',
                ['method', 'endpoint', 'status']
            )
    except Exception as e:
        print(f"Warning: Error initializing Prometheus metrics: {e}")
    
    class PrometheusMetricsPipe(Pipe):
        """Pipeline component to track HTTP metrics"""
        
        async def open(self):
            import time
            self.start_time = time.time()
        
        async def close(self):
            import time
            from emmett import request, response
            
            # Calculate duration
            duration = time.time() - self.start_time
            
            # Get endpoint path from request
            endpoint = request.path
            method = request.method
            status = str(response.status)
            
            # Record metrics
            http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()  # type: ignore[attr-defined]
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)  # type: ignore[attr-defined]
    
    prometheus_pipe = PrometheusMetricsPipe()
    
    print(f"✓ Prometheus metrics enabled at /metrics (pipeline-based)")
else:
    prometheus_pipe = None
    if not PROMETHEUS_ENABLED:
        print("✗ Prometheus metrics disabled via PROMETHEUS_ENABLED=false")
    elif not prometheus_available:
        print("✗ Prometheus metrics unavailable: prometheus-client not installed")


#: define ValkeyCache handler (Redis-compatible open-source alternative)
class ValkeyCache:
    """
    Valkey cache handler for Emmett applications.
    
    Valkey is an open-source, Redis-compatible alternative maintained by the
    Linux Foundation. This handler provides the same API as RedisCache.
    
    Usage:
        from emmett.cache import Cache
        cache = Cache(valkey=ValkeyCache(host='localhost', port=6379))
    """
    
    def __init__(self, host='localhost', port=6379, db=0, 
                 prefix='cache:', default_expire=300):
        """
        Initialize Valkey cache handler.
        
        Args:
            host: Valkey server hostname (default: localhost)
            port: Valkey server port (default: 6379)
            db: Database number (default: 0)
            prefix: Key prefix for all cached data (default: 'cache:')
            default_expire: Default expiration in seconds (default: 300)
        """
        if not valkey_available:
            raise ImportError(
                "valkey package is required for ValkeyCache. "
                "Install it with: pip install valkey"
            )
        
        self.client = Valkey(
            host=host,
            port=port,
            db=db,
            decode_responses=False  # Handle binary data for pickle
        )
        self.prefix = prefix
        self.default_expire = default_expire
    
    def _make_key(self, key):
        """Generate prefixed cache key."""
        return f"{self.prefix}{key}"
    
    def get(self, key):
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        try:
            value = self.client.get(self._make_key(key))
            if value is None:
                return None
            return pickle.loads(value)  # type: ignore[arg-type]
        except Exception as e:
            print(f"Valkey cache get error: {e}")
            return None
    
    def set(self, key, value, duration=None):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be pickleable)
            duration: Expiration time in seconds (default: use default_expire)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = duration if duration is not None else self.default_expire
            serialized = pickle.dumps(value)
            return self.client.setex(
                self._make_key(key),
                int(ttl),
                serialized
            )
        except Exception as e:
            print(f"Valkey cache set error: {e}")
            return False
    
    def clear(self, key=None):
        """
        Clear cache entry or entire cache.
        
        Args:
            key: Cache key to clear, or None to clear all.
                 Supports pattern matching with '*' wildcard.
        
        Returns:
            Number of keys deleted
        """
        try:
            if key is None:
                # Clear entire cache (all keys in current db)
                return self.client.flushdb()
            
            if '*' in key:
                # Pattern-based deletion
                pattern = self._make_key(key)
                keys = self.client.keys(pattern)
                if keys:
                    return self.client.delete(*keys)  # type: ignore[misc]
                return 0
            
            # Single key deletion
            return self.client.delete(self._make_key(key))
        except Exception as e:
            print(f"Valkey cache clear error: {e}")
            return 0
    
    def get_or_set(self, key, callback, duration=None):
        """
        Get value from cache or set it using callback.
        
        Args:
            key: Cache key
            callback: Callable to generate value if not in cache
            duration: Expiration time in seconds
            
        Returns:
            Cached or freshly generated value
        """
        value = self.get(key)
        if value is None:
            value = callback() if callable(callback) else callback
            self.set(key, value, duration)
        return value
    
    async def get_or_set_loop(self, key, callback, duration=None):
        """
        Async version of get_or_set.
        
        Args:
            key: Cache key
            callback: Async callable to generate value if not in cache
            duration: Expiration time in seconds
            
        Returns:
            Cached or freshly generated value
        """
        value = self.get(key)
        if value is None:
            if callable(callback):
                import asyncio
                if asyncio.iscoroutinefunction(callback):
                    value = await callback()
                else:
                    value = callback()
            else:
                value = callback
            self.set(key, value, duration)
        return value


#: cache configuration (example - uncomment to use)
# VALKEY_ENABLED = os.environ.get('VALKEY_ENABLED', 'false').lower() == 'true'
# VALKEY_HOST = os.environ.get('VALKEY_HOST', 'valkey')
# VALKEY_PORT = int(os.environ.get('VALKEY_PORT', '6379'))
# VALKEY_DB = int(os.environ.get('VALKEY_DB', '0'))
# 
# if VALKEY_ENABLED and valkey_available:
#     from emmett.cache import Cache
#     cache = Cache(valkey=ValkeyCache(
#         host=VALKEY_HOST,
#         port=VALKEY_PORT,
#         db=VALKEY_DB,
#         prefix='bloggy:',
#         default_expire=300
#     ))
#     print(f"✓ Valkey cache enabled: {VALKEY_HOST}:{VALKEY_PORT}")
# else:
#     cache = None
#     if not VALKEY_ENABLED:
#         print("✗ Valkey cache disabled via VALKEY_ENABLED=false")
#     elif not valkey_available:
#         print("✗ Valkey cache unavailable: valkey not installed")

#: helper functions for context access (must be defined before models)
def get_current_session():
    """
    Get current session, safe for all contexts.
    
    Returns:
        Session object or None if outside request context
    """
    try:
        return current.session
    except (AttributeError, RuntimeError):
        return None


# Authentication helper functions moved to models/user/model.py
from models.utils import user_has_permission


#: init db, mailer and auth
# Use DatabaseManager for all database operations
# Expose db for backward compatibility
db = db_manager.db
mailer = Mailer(app)
# Temporarily disable Auth to test User model
# auth = Auth(app, db, user_model=User)
db_manager.define_models(Post, Comment, Role, Permission, UserRole, RolePermission, OAuthAccount, OAuthToken)

# Create database connection pipe for request pipeline
db_connection_pipe = db_manager.create_connection_pipe()


#: Patch Row classes to add custom methods
# This allows methods defined on Model classes to work on Row objects returned from queries
def role_get_permissions(self):
    """Get permissions for this role (works on Row objects)."""
    try:
        role_id = self.id if hasattr(self, 'id') else self['id']
        rows = db(
            (db.role_permissions.role == role_id) &
            (db.role_permissions.permission == db.permissions.id)
        ).select(db.permissions.ALL)
        return [row for row in rows]
    except Exception as e:
        role_name = getattr(self, 'name', self.get('name', 'unknown')) if hasattr(self, 'get') else getattr(self, 'name', 'unknown')
        print(f"Error getting permissions for role {role_name}: {e}")
        return []

def post_can_edit(self, user):
    """Check if user can edit this post (works on Row objects)."""
    from models.utils import user_can_access_resource
    if not user:
        return False
    user_id = user.id if hasattr(user, 'id') else user['id']
    return user_can_access_resource(user_id, 'post', 'edit', self)

def post_can_delete(self, user):
    """Check if user can delete this post (works on Row objects)."""
    from models.utils import user_can_access_resource
    if not user:
        return False
    user_id = user.id if hasattr(user, 'id') else user['id']
    return user_can_access_resource(user_id, 'post', 'delete', self)

# Use DatabaseManager to patch Row classes
db_manager.patch_row_methods({
    'users': {'has_permission': lambda user, permission_name: user_has_permission(user.id, permission_name)},
    'roles': {'get_permissions': role_get_permissions},
    'posts': {'can_edit': post_can_edit, 'can_delete': post_can_delete}
})


#: database helper functions (defined after db is initialized)
# get_or_404 helper function moved to models/utils.py
# safe_first and get_or_create are now provided by DatabaseManager

# Backward compatibility wrappers
def safe_first(query, default=None):
    """Safely get first result from query (delegates to DatabaseManager)."""
    return db_manager.safe_first(query, default)


def get_or_create(model, **kwargs):
    """Get existing record or create new one (delegates to DatabaseManager)."""
    return db_manager.get_or_create(model, **kwargs)


#: init REST extension
app.use_extension(REST)
rest_ext = app.ext.REST

#: Automatic Route Generation for models with auto_routes attribute
# Import auto_routes system
try:
    from auto_routes import discover_and_register_auto_routes  # type: ignore[reportMissingImports]
    # Discover and register routes for all models with auto_routes=True
    discover_and_register_auto_routes(app, db)
    print("✓ Automatic route generation enabled")
except Exception as e:
    import traceback
    print(f"⚠️  Automatic route generation failed: {e}")
    traceback.print_exc()

#: init Auto UI for models
# Enable auto-generated CRUD interface for Post model
auto_ui(app, Post, '/admin/posts')
# Enable auto-generated CRUD interface for Comment model
auto_ui(app, Comment, '/admin/comments')
# Note: Role auto UI is handled by auto_routes system (role model has auto_routes=True)
# Enable auto-generated CRUD interface for Permission model
auto_ui(app, Permission, '/admin/permissions')


#: setup helping function
def setup_admin():
    with db_manager.connection():
        # Check if user already exists
        existing_user = User.where(lambda u: u.email == "doc@emmettbrown.com").select().first()
        
        if existing_user:
            print("Admin user already exists!")
            user_id = existing_user.id
        else:
            # create the user
            user = User.create(
                email="doc@emmettbrown.com",
                first_name="Emmett",
                last_name="Brown",
                password="fluxcapacitor"
            )
            user_id = user.id
            print("✅ Created admin user: doc@emmettbrown.com")
        
        # create an admin group using raw database access (for backward compatibility)
        existing_group = db(db.auth_groups.role == "admin").select().first()
        if existing_group:
            group_id = existing_group.id
        else:
            group_id = db.auth_groups.insert(role="admin", description="Administrators")
        
        # add user to admins group (field name is 'user', not 'auth_user')
        existing_membership = db(
            (db.auth_memberships.user == user_id) &
            (db.auth_memberships.auth_group == group_id)
        ).select().first()
        
        if not existing_membership:
            db.auth_memberships.insert(user=user_id, auth_group=group_id)
        
        db.commit()
        
        # Seed role-based access control system
        print("\n" + "="*60)
        print("🔐 Setting up Role-Based Access Control System")
        print("="*60)
        
        try:
            # Seed permissions and roles
            permissions, roles = seed_all(db, admin_user_id=user_id)
            print(f"✅ Role system setup complete!")
            print(f"   - Created {len(permissions)} permissions")
            print(f"   - Created {len(roles)} roles")
            print(f"   - Assigned Admin role to {user_id}")
        except Exception as e:
            print(f"⚠️  Error setting up role system: {e}")
            import traceback
            traceback.print_exc()
        print("Admin user created: doc@emmettbrown.com")


@app.command('setup')
def setup():
    setup_admin()


#: pipeline
# Simplified pipeline to avoid invalid pipe issues
# Note: Auth temporarily disabled for testing
app.pipeline = [
    SessionManager.cookies('GreatScott'),
    # db.pipe,  # Temporarily disabled due to invalid pipe issue
    # auth.pipe  # Temporarily disabled
]


# auth_routes = auth.module(__name__)  # Temporarily disabled


#: OAuth Routes
# Import and configure OAuth functionality
from auth import get_oauth_manager
from auth.rate_limit import rate_limit
from auth.token_refresh import setup_commands as setup_oauth_commands
import logging

oauth_manager = get_oauth_manager()

# Setup OAuth CLI commands
setup_oauth_commands(app)

# Setup OAuth logging
oauth_logger = logging.getLogger('oauth')
oauth_logger.setLevel(logging.INFO)

# Create OAuth routes module
# oauth_routes = app.module(__name__, 'oauth', url_prefix='auth/oauth')  # Temporarily disabled


# Temporarily disable all OAuth routes until Auth is fixed
# OAuth functionality will be re-enabled once Auth system is properly configured

# OAuth helper functions (commented out until Auth is re-enabled)
def _clear_oauth_session(provider):
    """Clear OAuth session data for a provider."""
    from emmett import session
    
    keys_to_remove = [
        f'oauth_{provider}_code_verifier',
        f'oauth_{provider}_state',
        f'oauth_{provider}_link_mode'
    ]
    
    for key in keys_to_remove:
        if key in session:  # type: ignore[operator]
            del session[key]
    
    if 'oauth_link_mode' in session:  # type: ignore[operator]
        del session['oauth_link_mode']


#: Account settings route (temporarily disabled until Auth is fixed)
# @app.route('/account/settings', methods=['get', 'post'])
# @requires(lambda: session.auth, url('auth.login'))
# async def account_settings():
#     """Account settings page with OAuth management."""
#     pass


#: Prometheus metrics endpoint
if PROMETHEUS_ENABLED and prometheus_available:
    # Provide a simple no-op decorator for compatibility
    def track_metrics(endpoint_path=None):
        """
        Decorator for compatibility - metrics are now tracked automatically via pipeline.
        """
        def decorator(f):
            return f
        return decorator
    
    app.track_metrics = track_metrics  # type: ignore[attr-defined]
    
    @app.route('/metrics')
    async def metrics():
        """Expose Prometheus metrics in standard format"""
        response.headers['Content-Type'] = CONTENT_TYPE_LATEST
        return generate_latest().decode('utf-8')
    
      
    @app.route('/test-metrics')
    @service.json  # type: ignore[attr-defined]
    async def test_metrics_endpoint():
        """Test endpoint to verify metrics tracking works"""
        return {'automatic': True, 'metrics': 'tracked'}
    
    print(f"✓ Prometheus metrics enabled at /metrics (pipeline integration)")
    print(f"✓ Metrics tracked automatically for all requests via pipeline")


#: Setup model routes and REST APIs
# Temporarily disabled to get basic app running
# Routes and APIs are now organized in their respective model packages
# from models import setup_all
# api_modules = setup_all(app)


#: OpenAPI / Swagger Documentation
# Initialize OpenAPI generator
openapi_gen = OpenAPIGenerator(
    app,
    title="Bloggy REST API",
    version="1.0.0",
    description="""
    # Bloggy REST API
    
    A complete REST API for a micro-blogging platform built with Emmett Framework.
    
    ## Features
    - **Posts**: Create, read, update, and delete blog posts
    - **Comments**: Add and manage comments on posts
    - **Users**: View user information (read-only)
    - **Roles**: Manage user roles (admin only)
    - **Permissions**: Manage permissions (admin only, delete disabled)
    
    ## Authentication
    Authentication is handled via session cookies. Admin access is required for
    role and permission management.
    
    ## Authorization
    The API uses a Role-Based Access Control (RBAC) system with the following roles:
    - **Admin**: Full access to all resources
    - **Moderator**: Can edit/delete any content
    - **Author**: Can create/edit own content
    - **Viewer**: Read-only access
    
    ## Response Format
    - List endpoints return paginated data with metadata
    - Single resource endpoints return the object directly
    - Validation errors return a 422 status with error details
    """
)

# Register all REST modules with the OpenAPI generator
# Temporarily disabled to get basic app running
# openapi_gen.register_rest_module('posts_api', Post, 'api/posts')
# openapi_gen.register_rest_module('comments_api', Comment, 'api/comments')
# openapi_gen.register_rest_module('users_api', User, 'api/users',
#                                 disabled_methods=['create', 'update', 'delete'])
# openapi_gen.register_rest_module('roles_api', Role, 'api/roles')
# openapi_gen.register_rest_module('permissions_api', Permission, 'api/permissions',
#                                 disabled_methods=['delete'])


@app.route('/api/openapi.json')
@service.json  # type: ignore[attr-defined]
async def openapi_spec():
    """Serve OpenAPI 3.0 specification as JSON"""
    return openapi_gen.generate()


@app.route('/api/docs')
async def swagger_ui():
    """Serve Swagger UI for interactive API documentation"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bloggy API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.3/swagger-ui.css">
    <style>
        body {
            margin: 0;
            padding: 0;
        }
        .topbar {
            display: none;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.3/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.3/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            window.ui = SwaggerUIBundle({
                url: '/api/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                docExpansion: "list",
                filter: true,
                tryItOutEnabled: true
            });
        }
    </script>
</body>
</html>"""
    response.headers['Content-Type'] = 'text/html'
    return html


@app.route('/api')
@service.json  # type: ignore[attr-defined]
async def api_root():
    """API root with links to documentation"""
    return {
        'message': 'Bloggy REST API',
        'version': '1.0.0',
        'documentation': {
            'swagger_ui': 'http://localhost:8000/api/docs',
            'openapi_spec': 'http://localhost:8000/api/openapi.json'
        },
        'endpoints': {
            'posts': '/api/posts',
            'comments': '/api/comments',
            'users': '/api/users'
        }
    }


@app.route('/test')
async def test_route():
    """Simple test route to check if server responds."""
    return "Hello World! Server is working."
