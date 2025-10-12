# -*- coding: utf-8 -*-

from emmett import App, session, now, url, redirect, abort, response
from emmett.orm import Database, Model, Field, belongs_to, has_many
from emmett.tools import requires, service
from emmett.tools.auth import Auth, AuthUser
from emmett.tools import Mailer
from emmett.sessions import SessionManager
from emmett_rest import REST
import json
import os

# Import OpenAPI generator (deferred to avoid import issues)
import sys
sys.path.insert(0, os.path.dirname(__file__))
from openapi_generator import OpenAPIGenerator

# Import Sentry extension for error tracking
try:
    from emmett_sentry import Sentry
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    print("Warning: emmett-sentry not installed. Error tracking disabled.")

# Import Prometheus client for metrics
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Warning: prometheus-client not installed. Metrics collection disabled.")

# Import Valkey for caching (optional)
try:
    from valkey import Valkey
    import pickle
    VALKEY_AVAILABLE = True
except ImportError:
    VALKEY_AVAILABLE = False
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
app.config.db.uri = f"sqlite://{os.path.join(os.path.dirname(__file__), 'databases', 'bloggy.db')}"

#: sentry/bugsink error tracking configuration
SENTRY_ENABLED = os.environ.get('SENTRY_ENABLED', 'true').lower() == 'true'
SENTRY_DSN = os.environ.get('SENTRY_DSN', 'http://public@bugsink:8000/1')
SENTRY_ENVIRONMENT = os.environ.get('SENTRY_ENVIRONMENT', os.environ.get('EMMETT_ENV', 'development'))
SENTRY_TRACES_SAMPLE_RATE = float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1'))

if SENTRY_ENABLED and SENTRY_AVAILABLE:
    app.config.Sentry.dsn = SENTRY_DSN
    app.config.Sentry.environment = SENTRY_ENVIRONMENT
    app.config.Sentry.traces_sample_rate = SENTRY_TRACES_SAMPLE_RATE
    app.config.Sentry.release = "bloggy@1.0.0"
    app.use_extension(Sentry)
    print(f"✓ Error tracking enabled: {SENTRY_DSN} (environment: {SENTRY_ENVIRONMENT})")
else:
    if not SENTRY_ENABLED:
        print("✗ Error tracking disabled via SENTRY_ENABLED=false")
    elif not SENTRY_AVAILABLE:
        print("✗ Error tracking unavailable: emmett-sentry not installed")

#: prometheus metrics configuration
PROMETHEUS_ENABLED = os.environ.get('PROMETHEUS_ENABLED', 'true').lower() == 'true'

# Initialize Prometheus metrics
if PROMETHEUS_ENABLED and PROMETHEUS_AVAILABLE:
    # Define custom metrics
    http_requests_total = Counter(
        'emmett_http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )
    
    http_request_duration_seconds = Histogram(
        'emmett_http_request_duration_seconds',
        'HTTP request latency in seconds',
        ['method', 'endpoint']
    )
    
    http_request_size_bytes = Histogram(
        'emmett_http_request_size_bytes',
        'HTTP request size in bytes',
        ['method', 'endpoint']
    )
    
    http_response_size_bytes = Histogram(
        'emmett_http_response_size_bytes',
        'HTTP response size in bytes',
        ['method', 'endpoint', 'status']
    )
    
    print(f"✓ Prometheus metrics enabled at /metrics (custom integration)")
else:
    if not PROMETHEUS_ENABLED:
        print("✗ Prometheus metrics disabled via PROMETHEUS_ENABLED=false")
    elif not PROMETHEUS_AVAILABLE:
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
        if not VALKEY_AVAILABLE:
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
            return pickle.loads(value)
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
                    return self.client.delete(*keys)
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
# if VALKEY_ENABLED and VALKEY_AVAILABLE:
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
#     elif not VALKEY_AVAILABLE:
#         print("✗ Valkey cache unavailable: valkey not installed")


#: define models
class User(AuthUser):
    # will create "auth_user" table and groups/permissions ones
    has_many('posts', 'comments')


class Post(Model):
    belongs_to('user')
    has_many('comments')

    title = Field()
    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: session.auth.user.id if session.auth else None,
        'date': now
    }
    validation = {
        'title': {'presence': True},
        'text': {'presence': True},
        'user': {'allow': 'empty'}  # Allow empty for REST API (will be set by callback)
    }
    fields_rw = {
        'user': False,  # Hidden in forms
        'date': False
    }
    rest_rw = {
        'user': (False, True),  # Hidden in output, writable in input for REST API
        'date': (True, False)    # Visible in output, not writable in input
    }


class Comment(Model):
    belongs_to('user', 'post')

    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: session.auth.user.id if session.auth else None,
        'date': now
    }
    validation = {
        'text': {'presence': True},
        'user': {'allow': 'empty'},  # Allow empty for REST API (will be set by callback)
        'post': {'presence': True}
    }
    fields_rw = {
        'user': False,  # Hidden in forms
        'post': False,
        'date': False
    }
    rest_rw = {
        'user': (False, True),  # Hidden in output, writable in input for REST API
        'post': (True, True),    # Visible and writable for REST API
        'date': (True, False)    # Visible in output, not writable in input
    }


#: init db, mailer and auth
db = Database(app)
mailer = Mailer(app)
auth = Auth(app, db, user_model=User)
db.define_models(Post, Comment)

#: init REST extension
app.use_extension(REST)
rest_ext = app.ext.REST


#: setup helping function
def setup_admin():
    with db.connection():
        # Check if user already exists
        existing_user = User.where(lambda u: u.email == "doc@emmettbrown.com").select().first()
        if existing_user:
            print("Admin user already exists!")
            return
        
        # create the user
        user = User.create(
            email="doc@emmettbrown.com",
            first_name="Emmett",
            last_name="Brown",
            password="fluxcapacitor"
        )
        
        # create an admin group using raw database access
        existing_group = db(db.auth_groups.role == "admin").select().first()
        if existing_group:
            group_id = existing_group.id
        else:
            group_id = db.auth_groups.insert(role="admin", description="Administrators")
        
        # add user to admins group
        db.auth_memberships.insert(user=user.id, auth_group=group_id)
        db.commit()
        print("Admin user created: doc@emmettbrown.com")


@app.command('setup')
def setup():
    setup_admin()


#: pipeline
app.pipeline = [
    SessionManager.cookies('GreatScott'),
    db.pipe,
    auth.pipe
]

#: prometheus metrics decorator (defined early so routes can use it)
def track_metrics(endpoint_name=None):
    """
    Decorator to automatically track Prometheus metrics for a route.
    Usage: @app.track_metrics() or @app.track_metrics('/custom-name')
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Only track if Prometheus is available
            if not (PROMETHEUS_ENABLED and PROMETHEUS_AVAILABLE):
                return await func(*args, **kwargs)
                
            import time
            from emmett import request, response
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                method = request.method
                endpoint = endpoint_name or request.path
                status = str(response.status).split()[0] if response.status else '200'
                
                http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
                http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                method = request.method
                endpoint = endpoint_name or request.path
                
                http_requests_total.labels(method=method, endpoint=endpoint, status='500').inc()
                http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
                raise
        return wrapper
    return decorator

app.track_metrics = track_metrics


#: exposing functions
@app.route("/")
@app.track_metrics() if PROMETHEUS_ENABLED and PROMETHEUS_AVAILABLE else lambda f: f
async def index():
    posts = Post.all().select(orderby=~Post.date)
    return dict(posts=posts)


@app.route("/post/<int:pid>")
@app.track_metrics('/post/:id') if PROMETHEUS_ENABLED and PROMETHEUS_AVAILABLE else lambda f: f
async def one(pid):
    def _validate_comment(form):
        # manually set post id in comment form
        form.params.post = pid
    # get post and return 404 if doesn't exist
    post = Post.get(pid)
    if not post:
        abort(404)
    # get comments
    comments = post.comments(orderby=~Comment.date)
    # and create a form for commenting if the user is logged in
    if session.auth:
        form = await Comment.form(onvalidation=_validate_comment)
        if form.accepted:
            redirect(url('one', pid))
    return locals()


@app.route("/new")
@app.track_metrics() if PROMETHEUS_ENABLED and PROMETHEUS_AVAILABLE else lambda f: f
@requires(lambda: session.auth, '/')
async def new_post():
    form = await Post.form()
    if form.accepted:
        redirect(url('one', form.params.id))
    return dict(form=form)


auth_routes = auth.module(__name__)


#: REST API configuration
# REST endpoints for Posts
posts_api = app.rest_module(
    __name__, 
    'posts_api', 
    Post, 
    url_prefix='api/posts'
)

# REST endpoints for Comments
comments_api = app.rest_module(
    __name__, 
    'comments_api', 
    Comment, 
    url_prefix='api/comments'
)

# REST endpoints for Users (read-only)
users_api = app.rest_module(
    __name__, 
    'users_api', 
    User, 
    url_prefix='api/users',
    disabled_methods=['create', 'update', 'delete']
)

# Use callbacks to automatically set user from session
@posts_api.before_create
def set_post_user(attrs):
    """Automatically set user from session if authenticated"""
    if session.auth and 'user' not in attrs:
        attrs['user'] = session.auth.user.id

@comments_api.before_create
def set_comment_user(attrs):
    """Automatically set user from session if authenticated"""
    if session.auth and 'user' not in attrs:
        attrs['user'] = session.auth.user.id


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
    
    ## Authentication
    Currently, the API endpoints are accessible without authentication.
    User context is automatically set from session cookies when available.
    
    ## Response Format
    - List endpoints return paginated data with metadata
    - Single resource endpoints return the object directly
    - Validation errors return a 422 status with error details
    """
)

# Register all REST modules with the OpenAPI generator
openapi_gen.register_rest_module('posts_api', Post, 'api/posts')
openapi_gen.register_rest_module('comments_api', Comment, 'api/comments')
openapi_gen.register_rest_module('users_api', User, 'api/users', 
                                disabled_methods=['create', 'update', 'delete'])


@app.route('/api/openapi.json')
@app.track_metrics() if PROMETHEUS_ENABLED and PROMETHEUS_AVAILABLE else lambda f: f
@service.json
async def openapi_spec():
    """Serve OpenAPI 3.0 specification as JSON"""
    return openapi_gen.generate()


@app.route('/api/docs')
@app.track_metrics() if PROMETHEUS_ENABLED and PROMETHEUS_AVAILABLE else lambda f: f
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
@app.track_metrics()
@service.json
async def api_root():
    """API root with links to documentation"""
    return {
        'message': 'Bloggy REST API',
        'version': '1.0.0',
        'documentation': {
            'swagger_ui': 'http://localhost:8081/api/docs',
            'openapi_spec': 'http://localhost:8081/api/openapi.json'
        },
        'endpoints': {
            'posts': '/api/posts',
            'comments': '/api/comments',
            'users': '/api/users'
        }
    }


@app.route('/test-error')
async def test_error():
    """Test endpoint for error tracking - raises an intentional exception"""
    # This endpoint is useful for verifying that error tracking is working
    # Access this endpoint to trigger an error that should appear in Bugsink
    raise Exception("This is a test error for Bugsink error tracking verification")


@app.route('/test-metrics')
@app.track_metrics()
@service.json
async def test_metrics():
    """Test endpoint for automatic metric tracking"""
    return dict(message='Metrics tracked automatically via decorator', automatic=True)


@app.route('/test-error-division')
async def test_error_division():
    """Test endpoint for error tracking - raises a ZeroDivisionError"""
    result = 42 / 0
    return {'result': result}


#: Prometheus metrics endpoint and pipeline
if PROMETHEUS_ENABLED and PROMETHEUS_AVAILABLE:
    from emmett import Pipe
    
    @app.route('/metrics')
    async def metrics():
        """Expose Prometheus metrics"""
        response.headers['Content-Type'] = CONTENT_TYPE_LATEST
        return generate_latest().decode('utf-8')
    
    print(f"✓ Prometheus metrics helper available: @app.track_metrics()")
