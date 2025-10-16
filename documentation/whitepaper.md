# EmmettBase: Emmett-Based PocketBase Replacement
**Whitepaper – Design and Implementation Guide**

## 1. Objective
This document outlines **EmmettBase**: a framework that provides PocketBase-equivalent functionality using Emmett. EmmettBase leverages Emmett's simplicity and built-in features to enable developers to build API-centric, real-time, file-enabled, authenticated platforms with minimal code.

## 1.1 Architecture Philosophy

**Simple, Declarative Development:**

```python
from emmett import App
from emmett.orm import Database, Model, Field
from emmett.tools import service

class Product(Model):
    name = Field.string()
    price = Field.decimal(10, 2)

app = App(__name__)
db = Database(app)
db.define_models(Product)

@app.route('/api/products', methods='get')
@service.json
async def list_products():
    return {'products': Product.all().select()}
```

This approach ensures:
- Minimal boilerplate with maximum functionality
- Models are simple and declarative
- Built-in API generation with service decorators
- Clear, readable code that's easy to maintain

## 2. Why Emmett
Emmett is selected as the base framework because it provides:
- **Simplicity-first design** – Clean, readable Python code
- **Built-in ORM** – pyDAL-based with support for SQLite, PostgreSQL, MySQL, and more
- **Native async/await** – Full ASGI support with WebSocket capabilities
- **Integrated Auth system** – User management, groups, permissions out-of-the-box
- **Service decorators** – `@service.json` and `@service.xml` for instant API generation
- **File upload support** – `Field.upload()` for file storage
- **Validation system** – Built-in validators for data integrity
- **Production-ready** – Compatible with Python 3.9+

These features reduce boilerplate work, allowing focus on building robust APIs, permissions, and real-time data flow.

## 3. Programming Model: Active-Record Pattern
This implementation follows an **active-record pattern** where:
- **The model is the source of truth** – Emmett models define the schema
- **Service decorators** – `@service.json` automatically generates JSON API endpoints
- **CRUD operations on models** – Built-in query methods like `Model.all()`, `Model.where()`
- **Automatic API generation** – Endpoints created with simple decorators

## 4. Feature Parity with PocketBase
| PocketBase Feature | Emmett Component | Status |
|---------------------|------------------|--------|
| Models & CRUD | Emmett ORM (pyDAL) with Model classes | ✅ Built-in |
| Authentication (Email/Password) | Emmett Auth module (built-in) | ✅ Built-in |
| OAuth2 Providers | Custom OAuth2 implementation | 🔄 Extensible |
| File Storage (Local) | `Field.upload()` with uploadfolder | ✅ Built-in |
| File Storage (S3/Cloud) | Custom storage adapters | 📋 Planned |
| Permissions / ACL | Auth groups, memberships, permissions | ✅ Built-in |
| Real-Time Subscriptions | `@app.websocket()` decorator (native) | ✅ Built-in |
| Admin Dashboard | Custom admin UI generation | 📋 Planned |
| Schema Migrations | `emmett migrations` CLI | ✅ Built-in |
| API Documentation | Service decorators with OpenAPI | 🔄 Extensible |
| Background Tasks | Async tasks with async/await | ✅ Built-in |
| Batch Operations | ORM bulk operations | ✅ Built-in |
| Filtering & Sorting | Query expressions with `Model.where()` | ✅ Built-in |
| Auto-Pagination | Query `.select(paginate=(page, size))` | ✅ Built-in |
| Relations (has_many, belongs_to) | Model relationship methods | ✅ Built-in |
| Expand/Nested Queries | Query with relationship includes | ✅ Built-in |
| Hooks/Callbacks | Model callbacks and custom pipes | ✅ Built-in |
| CORS Support | Custom CORS pipe | 🔄 Extensible |
| Rate Limiting | Custom rate-limiting pipe | 🔄 Extensible |
| Request Logging | Custom logging pipe | 🔄 Extensible |
| Health Check Endpoint | Custom health check route | 🔄 Extensible |
| Email Templates | Email rendering with templates | ✅ Built-in |
| 2FA/MFA | Custom MFA implementation | 📋 Planned |
| Data Backup/Restore | Database export/import tools | 🔄 Extensible |
| Webhooks | Custom event dispatcher | 🔄 Extensible |
| SQLite Support | Native pyDAL SQLite support | ✅ Built-in |
| PostgreSQL/MySQL Support | Native pyDAL multi-DB support | ✅ Built-in |
| CSRF Protection | Auth module CSRF configuration | ✅ Built-in |
| XSS Protection | Template auto-escaping | ✅ Built-in |
| HTTPS/TLS | Reverse proxy (nginx, Traefik) | ✅ Standard |

**Legend:**
- ✅ **Built-in**: Feature available out-of-the-box
- 🔄 **Extensible**: Easily implemented with Emmett's extension system
- 📋 **Planned**: On the roadmap for future implementation


## 5. System Architecture
- **Emmett** – Full-stack Python framework with async support
- **pyDAL ORM** – Database abstraction layer supporting multiple engines
- **Native WebSocket** – Built-in real-time subscriptions via `@app.websocket()`
- **SQLite/PostgreSQL/MySQL** – Multiple database engine support
- **File Storage** – Built-in upload handling with `Field.upload()`
- **Auth Module** – Integrated user, group, and permission management
- **Service API** – JSON/XML services via decorators
- **Pipeline System** – Request/response middleware for cross-cutting concerns

## 6. Implementation Steps
1. Install Emmett: `pip install emmett`
2. Define models with `Model` and `Field` classes
3. Configure database connection via `app.config.db.uri`
4. Set up Auth module with `Auth(app, db, user_model=User)`
5. Create API endpoints with `@service.json` decorator
6. Add WebSocket handlers with `@app.websocket()` decorator
7. Implement access control with `@requires` decorator
8. Configure file uploads with `Field.upload()`
9. Add pagination, filtering, and validation
10. Deploy with ASGI server (uvicorn, gunicorn with uvicorn workers)

## 7. Example Flow

**Developer Experience with EmmettBase:**

1. **Define Model** in `app.py`:
   ```python
   from emmett import App
   from emmett.orm import Database, Model, Field
   from emmett.tools import service, requires
   from emmett.tools.auth import Auth, AuthUser

   app = App(__name__)
   app.config.db.uri = "sqlite:///database.db"
   
   class User(AuthUser):
       pass

   class Product(Model):
       name = Field.string()
       price = Field.decimal(10, 2)
       description = Field.text()
       in_stock = Field.bool(default=True)
       
       validation = {
           'name': {'presence': True},
           'price': {'presence': True}
       }

   db = Database(app)
   auth = Auth(app, db, user_model=User)
   db.define_models(User, Product)
   
   app.pipeline = [db.pipe, auth.pipe]
   ```

2. **Auto-Generated Forms**:
   ```python
   @app.route('/products/new', methods=['get', 'post'])
   @requires(auth.is_logged)
   async def new_product():
       form = await Product.form()
       if form.accepted:
           return redirect(url('products'))
       return dict(form=form)
   ```

3. **JSON API Endpoints**:
   ```python
   @app.route('/api/products', methods='get')
   @service.json
   async def list_products():
       page = request.query_params.page or 1
       products = Product.where(
           lambda p: p.in_stock == True
       ).select(paginate=(page, 20))
       return {'products': products}

   @app.route('/api/products', methods='post')
   @requires(auth.is_logged)
   @service.json
   async def create_product():
       product = Product.create(
           name=request.body_params.name,
           price=request.body_params.price,
           description=request.body_params.description
       )
       return {'product': product, 'id': product.id}
   ```

4. **Real-Time WebSocket**:
   ```python
   from emmett import websocket
   
   @app.websocket('/ws/products')
   async def products_stream():
       while True:
           message = await websocket.receive()
           # Broadcast product updates
           products = Product.all().select()
           await websocket.send({'products': products})
   ```

5. **Full-Stack Benefits**:
   - **Auto-generated forms** from models with `Model.form()`
   - **Built-in validation** with declarative rules
   - **JSON APIs** with `@service.json` decorator
   - **WebSocket support** out-of-the-box
   - **Authentication** integrated with minimal code
   - **Template rendering** for HTML views
   - **Single file or modular** architecture

## 8. Security
- **HMAC password hashing** – pbkdf2(2000,20,sha512) by default
- **Session management** – Secure cookie-based sessions
- **CSRF Protection** – Built into Auth module forms
- **XSS Protection** – Template auto-escaping
- **Access control** – `@requires` decorator with custom conditions
- **Role-based permissions** – Groups, memberships, and fine-grained permissions
- **User blocking** – Disable or block user accounts
- **Email verification** – Optional registration email verification
- **Password reset** – Secure password recovery flow
- **HTTPS/TLS** – Deploy behind reverse proxy (nginx, Traefik)

## 9. Full-Stack Form Generation

**Emmett's built-in form system provides:**

- **Auto-generated forms** from models using `Model.form()`
- **Validation integration** – Form validates using model validation rules
- **Custom widgets** – Override default form widgets per field
- **Form labels and info** – `form_labels` and `form_info` attributes
- **Field accessibility** – Control read/write with `fields_rw`
- **Multi-step forms** – Support for complex form flows
- **File upload forms** – Automatic handling of `Field.upload()` fields
- **CSRF protection** – Built-in when using Auth module
- **Error handling** – Automatic error display with `form.errors`
- **Success callbacks** – `form.accepted` for post-submission logic

**Example with Custom Form Styling:**

```python
from emmett.orm import Model, Field

class Article(Model):
    title = Field.string()
    body = Field.text()
    published = Field.bool(default=False)
    
    form_labels = {
        'title': 'Article Title',
        'body': 'Article Content',
        'published': 'Publish Now?'
    }
    
    form_info = {
        'body': 'Markdown supported'
    }
    
    validation = {
        'title': {'presence': True, 'len': {'gte': 5}},
        'body': {'presence': True}
    }

@app.route('/articles/new', methods=['get', 'post'])
async def new_article():
    form = await Article.form()
    if form.accepted:
        redirect(url('articles'))
    return dict(form=form)
```

## 10. Performance & Scalability
- **Async/await** – Native async support for concurrent request handling
- **Connection pooling** – Efficient database connection management
- **Query optimization** – pyDAL query optimization and indexing
- **ASGI server** – Deploy with uvicorn or gunicorn for high concurrency
- **WebSocket scaling** – Native WebSocket support without external services
- **Caching** – Built-in caching decorators and strategies
- **Pagination** – `.select(paginate=(page, size))` for efficient data loading
- **Lazy loading** – Efficient query execution and relationship loading
- **Lightweight** – Minimal dependencies and overhead

## 11. Complete Full-Stack Example

**Building a complete blog with forms, API, and real-time updates:**

```python
from emmett import App, request, response, url, redirect, websocket
from emmett.orm import Database, Model, Field
from emmett.tools import service, requires
from emmett.tools.auth import Auth, AuthUser
from emmett.sessions import SessionManager

# Initialize app
app = App(__name__)
app.config.db.uri = "sqlite:///bloggy.db"
app.config.auth.hmac_key = "your-secret-key"
app.config.auth.single_template = True

# Define models
class User(AuthUser):
    bio = Field.text()
    avatar = Field.upload(uploadfolder="uploads")
    
    form_profile_rw = {
        'bio': True,
        'avatar': True
    }

class Post(Model):
    author = Field.belongs_to('User')
    title = Field.string()
    body = Field.text()
    published = Field.bool(default=False)
    created_at = Field.datetime(default=lambda: request.now)
    
    has_many('comments')
    
    validation = {
        'title': {'presence': True, 'len': {'gte': 5, 'lte': 200}},
        'body': {'presence': True, 'len': {'gte': 10}}
    }
    
    form_labels = {
        'title': 'Post Title',
        'body': 'Post Content (Markdown supported)',
        'published': 'Publish immediately?'
    }

class Comment(Model):
    post = Field.belongs_to('Post')
    author = Field.belongs_to('User')
    body = Field.text()
    created_at = Field.datetime(default=lambda: request.now)
    
    validation = {
        'body': {'presence': True}
    }

# Setup database and auth
db = Database(app)
auth = Auth(app, db, user_model=User)
db.define_models(User, Post, Comment)

app.pipeline = [
    SessionManager.cookies('session-secret-key'),
    db.pipe,
    auth.pipe
]

# HTML Routes with Auto-Generated Forms

@app.route('/posts/new', methods=['get', 'post'])
@requires(auth.is_logged, url('login'))
async def new_post():
    """Create new post with auto-generated form"""
    form = await Post.form()
    if form.accepted:
        # Set current user as author
        post = db.Post(form.params.id)
        post.update_record(author=auth.user.id)
        redirect(url('view_post', post.id))
    return dict(form=form, title="New Post")

@app.route('/posts/<int:post_id>/edit', methods=['get', 'post'])
@requires(auth.is_logged)
async def edit_post(post_id):
    """Edit post with auto-generated form"""
    post = db.Post.get(post_id)
    if not post or post.author != auth.user.id:
        redirect(url('index'))
    
    form = await Post.form(record=post)
    if form.accepted:
        redirect(url('view_post', post_id))
    return dict(form=form, post=post, title="Edit Post")

@app.route('/posts/<int:post_id>')
async def view_post(post_id):
    """View post with comment form"""
    post = db.Post.get(post_id)
    if not post:
        redirect(url('index'))
    
    # Auto-generated comment form
    comment_form = await Comment.form()
    if comment_form.accepted:
        comment = db.Comment(comment_form.params.id)
        comment.update_record(
            post=post_id,
            author=auth.user.id if auth.user else None
        )
    
    comments = post.comments().select(orderby=~db.Comment.created_at)
    return dict(post=post, comments=comments, form=comment_form)

# JSON API Routes

@app.route('/api/posts', methods='get')
@service.json
async def api_list_posts():
    """List posts with pagination"""
    page = int(request.query_params.page or 1)
    published_only = request.query_params.published == 'true'
    
    query = Post.published == True if published_only else Post.id > 0
    posts = Post.where(lambda p: query).select(
        paginate=(page, 20),
        orderby=~Post.created_at
    )
    
    return {
        'posts': posts,
        'page': page,
        'has_more': len(posts) == 20
    }

@app.route('/api/posts/<int:post_id>', methods='get')
@service.json
async def api_get_post(post_id):
    """Get single post with comments"""
    post = db.Post.get(post_id)
    if not post:
        response.status = 404
        return {'error': 'Post not found'}
    
    comments = post.comments().select()
    return {
        'post': post,
        'author': post.author,
        'comments': comments
    }

@app.route('/api/posts', methods='post')
@requires(auth.is_logged, lambda: {'error': 'Not authenticated'})
@service.json
async def api_create_post():
    """Create post via API"""
    errors = Post.validate(
        title=request.body_params.title,
        body=request.body_params.body
    )
    
    if errors:
        response.status = 400
        return {'errors': errors}
    
    post = Post.create(
        author=auth.user.id,
        title=request.body_params.title,
        body=request.body_params.body,
        published=request.body_params.published or False
    )
    
    return {'post': post, 'id': post.id}

# WebSocket for Real-Time Updates

@app.websocket('/ws/posts')
async def posts_stream():
    """Real-time post updates"""
    await websocket.accept()
    
    while True:
        message = await websocket.receive()
        
        if message.get('action') == 'subscribe':
            # Send latest posts
            posts = Post.where(
                lambda p: p.published == True
            ).select(limitby=(0, 10))
            
            await websocket.send({
                'type': 'posts_update',
                'posts': posts
            })
        
        elif message.get('action') == 'new_comment':
            post_id = message.get('post_id')
            # Broadcast new comment notification
            await websocket.send({
                'type': 'comment_added',
                'post_id': post_id
            })

# Auth routes
auth_routes = auth.module(__name__)

# Run app
if __name__ == '__main__':
    app.run()
```

**Template Example (templates/new_post.html):**

```html
{{extend 'layout.html'}}

<h1>{{=title}}</h1>

<div class="post-form">
    {{=form}}
</div>

<style>
/* Form auto-styled by Emmett */
.emmett-form { max-width: 600px; margin: 0 auto; }
.form-field { margin-bottom: 1rem; }
.form-error { color: red; font-size: 0.9em; }
</style>
```

## 12. Implementing Missing PocketBase Features

While Emmett provides the foundation, some PocketBase-specific features need custom implementation. Here's how to add them:

### 12.1 CORS Support

```python
from emmett.pipeline import Pipe

class CORSPipe(Pipe):
    async def open(self):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    async def on_pipe_success(self):
        pass

app.pipeline = [CORSPipe(), db.pipe, auth.pipe]
```

### 12.2 Rate Limiting

```python
from emmett.cache import Cache
from emmett.pipeline import Pipe
from datetime import datetime, timedelta

cache = Cache()

class RateLimitPipe(Pipe):
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def open(self):
        ip = request.headers.get('X-Forwarded-For', request.client)
        key = f"ratelimit:{ip}"
        
        count = cache.get(key, 0)
        if count >= self.max_requests:
            response.status = 429
            return {'error': 'Rate limit exceeded'}
        
        cache.set(key, count + 1, self.window_seconds)

# Apply to specific routes
@app.route('/api/products', pipeline=[RateLimitPipe(max_requests=60)])
@service.json
async def list_products():
    return {'products': Product.all().select()}
```

### 12.3 Request Logging

```python
import logging
from emmett.pipeline import Pipe

logger = logging.getLogger('api')

class LoggingPipe(Pipe):
    async def open(self):
        self.start_time = datetime.now()
        logger.info(f"{request.method} {request.path} - {request.client}")
    
    async def close(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"Response {response.status} - {duration:.3f}s")

app.pipeline = [LoggingPipe(), db.pipe, auth.pipe]
```

### 12.4 Health Check Endpoint

```python
@app.route('/health')
@service.json
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db._adapter.reconnect()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        response.status = 503
    
    return {
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status,
        'version': '1.0.0'
    }
```

### 12.5 OAuth2 Authentication

```python
from emmett.tools.service import ServicePipe
import requests

class OAuth2Provider:
    def __init__(self, client_id, client_secret, authorize_url, token_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url

# Google OAuth2 example
google_oauth = OAuth2Provider(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    token_url='https://oauth2.googleapis.com/token'
)

@app.route('/auth/google')
async def oauth_google_login():
    """Redirect to Google OAuth"""
    redirect_uri = url('oauth_google_callback', _full=True)
    auth_url = f"{google_oauth.authorize_url}?client_id={google_oauth.client_id}&redirect_uri={redirect_uri}&response_type=code&scope=openid email profile"
    redirect(auth_url)

@app.route('/auth/google/callback')
async def oauth_google_callback():
    """Handle OAuth callback"""
    code = request.query_params.code
    
    # Exchange code for token
    token_response = requests.post(google_oauth.token_url, data={
        'code': code,
        'client_id': google_oauth.client_id,
        'client_secret': google_oauth.client_secret,
        'redirect_uri': url('oauth_google_callback', _full=True),
        'grant_type': 'authorization_code'
    })
    
    token_data = token_response.json()
    access_token = token_data.get('access_token')
    
    # Get user info
    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()
    
    # Find or create user
    user = User.where(lambda u: u.email == user_info['email']).first()
    if not user:
        user = User.create(
            email=user_info['email'],
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', '')
        )
    
    # Log in user
    auth.login_user(user)
    redirect(url('index'))
```

### 12.6 Expand/Nested Queries

```python
@app.route('/api/posts/<int:post_id>', methods='get')
@service.json
async def api_get_post_expanded(post_id):
    """Get post with expanded relationships"""
    post = db.Post.get(post_id)
    if not post:
        response.status = 404
        return {'error': 'Not found'}
    
    # Check if expand parameter is present
    expand = request.query_params.expand
    
    result = {'post': post}
    
    if expand:
        expand_fields = expand.split(',')
        
        if 'author' in expand_fields:
            result['author'] = post.author
        
        if 'comments' in expand_fields:
            result['comments'] = post.comments().select()
            
            if 'comments.author' in expand_fields:
                # Nested expansion
                for comment in result['comments']:
                    comment['author'] = comment.author
    
    return result
```

### 12.7 Model Hooks/Callbacks

```python
class Post(Model):
    title = Field.string()
    body = Field.text()
    slug = Field.string()
    created_at = Field.datetime()
    updated_at = Field.datetime()
    
    # Before insert callback
    def _before_insert(self):
        # Auto-generate slug from title
        self.slug = self.title.lower().replace(' ', '-')
        self.created_at = request.now
        self.updated_at = request.now
    
    # Before update callback
    def _before_update(self):
        self.updated_at = request.now
    
    # After insert callback
    def _after_insert(self):
        # Send notification
        print(f"New post created: {self.title}")
    
    # Custom validation
    def validate(self):
        errors = {}
        if self.title and len(self.title) < 5:
            errors['title'] = 'Title must be at least 5 characters'
        return errors or None
```

### 12.8 Data Backup/Restore

```python
import json
from datetime import datetime

@app.route('/admin/backup')
@requires(lambda: auth.has_membership('administrators'))
@service.json
async def backup_data():
    """Export database to JSON"""
    backup = {
        'timestamp': datetime.utcnow().isoformat(),
        'models': {}
    }
    
    # Export all models
    for model_name in ['User', 'Post', 'Comment']:
        model = getattr(db, model_name)
        records = model.all().select()
        backup['models'][model_name] = records
    
    return backup

@app.route('/admin/restore', methods='post')
@requires(lambda: auth.has_membership('administrators'))
@service.json
async def restore_data():
    """Import database from JSON"""
    backup = request.body_params.backup
    
    for model_name, records in backup['models'].items():
        model = getattr(db, model_name)
        for record in records:
            model.create(**record)
    
    return {'status': 'success', 'restored': len(backup['models'])}
```

### 12.9 Email Templates

```python
from emmett.tools.mail import Mailer

# Configure mailer
mailer = Mailer(
    sender=os.getenv('MAIL_SENDER'),
    server=os.getenv('MAIL_SERVER'),
    username=os.getenv('MAIL_USERNAME'),
    password=os.getenv('MAIL_PASSWORD')
)

# Custom email templates
@auth.registration_mail
def send_registration_email(user, data):
    """Custom registration email with template"""
    subject = "Welcome to EmmettBase!"
    
    # Render email template
    html_body = f"""
    <html>
        <body>
            <h1>Welcome {user.first_name}!</h1>
            <p>Thank you for registering. Please verify your email by clicking the link below:</p>
            <a href="{data['link']}">Verify Email</a>
        </body>
    </html>
    """
    
    mailer.send_mail(
        recipients=user.email,
        subject=subject,
        body=html_body,
        html=True
    )

@auth.reset_password_mail
def send_password_reset_email(user, data):
    """Custom password reset email"""
    subject = "Password Reset Request"
    
    html_body = f"""
    <html>
        <body>
            <h1>Password Reset</h1>
            <p>Click the link below to reset your password:</p>
            <a href="{data['link']}">Reset Password</a>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    
    mailer.send_mail(
        recipients=user.email,
        subject=subject,
        body=html_body,
        html=True
    )
```

### 12.10 Dynamic Collections (PocketBase-style)

```python
from emmett.orm import Field

class Collection(Model):
    """Meta-model for defining dynamic collections"""
    name = Field.string()
    schema = Field.json()  # Store field definitions as JSON
    created_at = Field.datetime()

class CollectionRecord(Model):
    """Generic record storage for dynamic collections"""
    collection = Field.belongs_to('Collection')
    data = Field.json()  # Store record data as JSON
    created_at = Field.datetime()
    updated_at = Field.datetime()

@app.route('/api/collections/<collection_name>', methods='get')
@service.json
async def get_collection_records(collection_name):
    """Get records from a dynamic collection"""
    collection = Collection.where(
        lambda c: c.name == collection_name
    ).first()
    
    if not collection:
        response.status = 404
        return {'error': 'Collection not found'}
    
    records = CollectionRecord.where(
        lambda r: r.collection == collection.id
    ).select()
    
    return {
        'collection': collection_name,
        'records': [r.data for r in records]
    }

@app.route('/api/collections/<collection_name>', methods='post')
@service.json
async def create_collection_record(collection_name):
    """Create a record in a dynamic collection"""
    collection = Collection.where(
        lambda c: c.name == collection_name
    ).first()
    
    if not collection:
        response.status = 404
        return {'error': 'Collection not found'}
    
    # Validate against schema
    data = request.body_params
    # TODO: Add schema validation
    
    record = CollectionRecord.create(
        collection=collection.id,
        data=data,
        created_at=request.now,
        updated_at=request.now
    )
    
    return {'id': record.id, 'data': record.data}
```

## 13. Roadmap

**Current Features (✅):**
- Auto-generated forms from models
- REST API with `@service.json`
- Real-time WebSocket support
- File uploads (local storage)
- Built-in authentication (email/password)
- Groups and permissions
- Validation system
- Database migrations
- Multiple database engines
- Model relationships and nested queries
- CSRF and XSS protection

**In Progress (🔄):**
- Admin UI auto-generated from models
- OAuth2 provider integrations (Google, GitHub, Facebook)
- Advanced rate limiting with Redis
- Request logging and monitoring
- CORS configuration middleware
- Health check and metrics endpoints
- Email template system enhancements
- Data backup and restore tools

**Planned (📋):**
- file storage backends
- Two-factor authentication (2FA/MFA)
- Real-time pub/sub
- API versioning support
- Advanced caching (multi-tier)
- Schema migration UI
- Advanced webhooks with retry logic
- Performance monitoring dashboard
- CLI tools for code generation
- Plugin/extension
