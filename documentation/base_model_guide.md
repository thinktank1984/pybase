# BaseModel Guide: Full-Stack Fat Models

## Overview

`BaseModel` is a comprehensive base class that gives models full-stack capabilities:
- HTTP request handling
- Response formatting
- Template rendering
- External API calls
- Email sending
- Session management
- Routing logic

All features have **sensible defaults** that can be **overridden with decorators**.

---

## Philosophy: Fat Models vs Thin Models

### Traditional "Thin Model" Approach
- Models only contain data and domain logic
- Controllers handle HTTP, templates, responses
- Services handle external APIs, emails
- **Pros**: Clear separation of concerns
- **Cons**: More files, more boilerplate

### "Fat Model" Approach (BaseModel)
- Models contain everything related to that entity
- HTTP, templates, APIs all in one place
- Decorators for customization
- **Pros**: Everything in one place, less boilerplate
- **Cons**: Models can become large

**BaseModel supports the Fat Model approach with sensible defaults.**

---

## Installation

```python
from base_model import BaseModel

class Post(BaseModel):
    title = Field()
    content = Field.text()
```

That's it! Your model now has full HTTP, template, API, email, session, and routing capabilities.

---

## 1. HTTP Request Handling

### Default Behavior

```python
class Post(BaseModel):
    title = Field()
    content = Field.text()

# Use default HTTP handlers
post = Post.get(1)

# Handle create request
response = post.handle_request('create', request)
# Default: Creates from request.body_params

# Handle read request
response = post.handle_request('read', request)
# Default: Returns to_dict()

# Handle update request
response = post.handle_request('update', request)
# Default: Updates from request.body_params

# Handle delete request
response = post.handle_request('delete', request)
# Default: Deletes the record
```

### Override with Decorator

```python
from base_model import BaseModel, http_handler

class Post(BaseModel):
    title = Field()
    content = Field.text()
    user_id = Field.int()
    
    @http_handler('create')
    def custom_create(self, req):
        """Custom create logic."""
        # Validate
        if not req.body_params.get('title'):
            abort(400, "Title required")
        
        # Set user from session
        self.user_id = session.auth.user.id
        
        # Create
        self.title = req.body_params['title']
        self.content = req.body_params.get('content', '')
        self.save()
        
        return {
            'id': self.id,
            'message': 'Post created successfully',
            'url': self.generate_route('show')
        }
    
    @http_handler('update')
    def custom_update(self, req):
        """Custom update with permission check."""
        # Check permission
        if self.user_id != session.auth.user.id:
            abort(403, "Not authorized")
        
        # Update
        self.update_record(**req.body_params)
        
        return {
            'id': self.id,
            'message': 'Updated successfully'
        }
```

### In Controllers

```python
@app.route('/posts', methods=['post'])
async def create_post():
    post = Post()
    response_data = post.handle_request('create')
    return response_data

@app.route('/posts/<int:id>', methods=['put'])
async def update_post(id):
    post = Post.get(id)
    if not post:
        abort(404)
    response_data = post.handle_request('update')
    return response_data
```

---

## 2. Response Formatting

### Default Behavior

```python
post = Post.get(1)

# JSON format (default)
json_response = post.format_response(post, 'json')
# Returns: {'id': 1, 'title': '...', 'content': '...'}

# XML format
xml_response = post.format_response(post, 'xml')
# Returns XML string

# HTML format
html_response = post.format_response(post, 'html')
# Returns HTML div
```

### Override with Decorator

```python
from base_model import BaseModel, response_formatter

class Post(BaseModel):
    title = Field()
    content = Field.text()
    user_id = Field.int()
    
    @response_formatter('json')
    def custom_json(self, data):
        """Custom JSON format with extra fields."""
        base = self.to_dict()
        
        # Add computed fields
        base['excerpt'] = self.content[:100] + "..."
        base['author'] = User.get(self.user_id).username
        base['comment_count'] = self.comments.count()
        
        # Add links
        base['_links'] = {
            'self': self.generate_route('show'),
            'edit': self.generate_route('edit'),
            'delete': self.generate_route('delete')
        }
        
        return base
    
    @response_formatter('xml')
    def custom_xml(self, data):
        """Custom XML format."""
        return f"""<?xml version="1.0"?>
<post>
    <id>{self.id}</id>
    <title><![CDATA[{self.title}]]></title>
    <content><![CDATA[{self.content}]]></content>
    <author>{User.get(self.user_id).username}</author>
</post>"""
```

### In Controllers

```python
@app.route('/api/posts/<int:id>')
async def get_post_json(id):
    post = Post.get(id)
    return post.format_response(post, 'json')

@app.route('/api/posts/<int:id>.xml')
async def get_post_xml(id):
    post = Post.get(id)
    response.headers['Content-Type'] = 'application/xml'
    return post.format_response(post, 'xml')
```

---

## 3. Template Rendering

### Default Behavior

```python
post = Post.get(1)

# Render with default template (post.html)
html = post.render_template()

# Render with specific template
html = post.render_template('post_detail.html', extra_var='value')
```

### Override with Decorator

```python
from base_model import BaseModel, template_renderer

class Post(BaseModel):
    title = Field()
    content = Field.text()
    
    @template_renderer('post.html')
    def custom_render(self, **context):
        """Custom template rendering with extra context."""
        # Add computed data
        context['excerpt'] = self.content[:100]
        context['word_count'] = len(self.content.split())
        context['related_posts'] = Post.where(
            lambda p: p.user_id == self.user_id and p.id != self.id
        ).select(limitby=(0, 5))
        
        # Render
        return current.app.template('post_detail.html', **context)
```

### In Controllers

```python
@app.route('/posts/<int:id>')
async def show_post(id):
    post = Post.get(id)
    return post.render_template()
```

---

## 4. External API Calls

### Default Behavior

```python
post = Post.get(1)

# GET request
data = post.call_api('https://api.example.com/posts/1')

# POST request
result = post.call_api(
    'https://api.example.com/posts',
    method='POST',
    data={'title': post.title}
)
```

### Override with Decorator

```python
from base_model import BaseModel, api_client

class Post(BaseModel):
    title = Field()
    content = Field.text()
    
    @api_client('/external/analyze')
    def call_sentiment_api(self, method, data):
        """Custom API call with authentication."""
        import requests
        
        headers = {
            'Authorization': f'Bearer {os.environ.get("API_KEY")}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api.sentiment.com/analyze',
            json={'text': self.content},
            headers=headers
        )
        
        return response.json()
    
    def analyze_sentiment(self):
        """Analyze post sentiment."""
        result = self.call_api('/external/analyze', 'POST', {'text': self.content})
        return result.get('sentiment', 'neutral')
```

### Usage

```python
post = Post.get(1)
sentiment = post.analyze_sentiment()
print(f"Post sentiment: {sentiment}")
```

---

## 5. Email Sending

### Default Behavior

```python
post = Post.get(1)

# Send email with default handler
result = post.send_email(
    to='user@example.com',
    subject='New Post Published',
    body=f'Check out: {post.title}'
)
```

### Override with Decorator

```python
from base_model import BaseModel, email_handler

class Post(BaseModel):
    title = Field()
    content = Field.text()
    user_id = Field.int()
    
    @email_handler('published')
    def send_published_email(self, to, subject, body):
        """Custom email for published posts."""
        from emmett import current
        mailer = current.app.ext.Mailer
        
        # Get author
        author = User.get(self.user_id)
        
        # Render email template
        html_body = current.app.template('emails/post_published.html', 
                                         post=self,
                                         author=author)
        
        # Send
        mailer.send(
            to=to,
            subject=f"New post by {author.username}: {self.title}",
            body=html_body,
            sender=f"{author.username} <noreply@example.com>"
        )
        
        return {'success': True}
    
    def notify_subscribers(self):
        """Notify all subscribers about new post."""
        subscribers = User.where(lambda u: u.subscribed == True).select()
        
        for subscriber in subscribers:
            self.send_email(
                to=subscriber.email,
                subject='New Post',
                body='',
                email_type='published'
            )
```

---

## 6. Session Management

### Default Behavior

```python
post = Post.get(1)

# Get from session
view_count = post.get_session_data('post_views', default=0)

# Set in session
post.set_session_data('post_views', view_count + 1)
```

### Override with Decorator

```python
from base_model import BaseModel, session_handler

class Post(BaseModel):
    title = Field()
    
    @session_handler('get', 'viewed_posts')
    def get_viewed_posts(self, key, default):
        """Custom session handler for viewed posts."""
        viewed = session.get('viewed_posts', [])
        return viewed if isinstance(viewed, list) else []
    
    @session_handler('set', 'viewed_posts')
    def set_viewed_posts(self, key, value):
        """Custom session handler for viewed posts."""
        if not isinstance(value, list):
            value = [value]
        session['viewed_posts'] = value
        return True
    
    def mark_as_viewed(self):
        """Mark this post as viewed in session."""
        viewed = self.get_session_data('viewed_posts', [])
        if self.id not in viewed:
            viewed.append(self.id)
            self.set_session_data('viewed_posts', viewed)
    
    def is_viewed(self):
        """Check if user has viewed this post."""
        viewed = self.get_session_data('viewed_posts', [])
        return self.id in viewed
```

---

## 7. Routing Logic

### Default Behavior

```python
post = Post.get(1)

# Generate URLs
show_url = post.generate_route('show')        # /posts/1
edit_url = post.generate_route('edit')        # /posts/1/edit
delete_url = post.generate_route('delete')    # /posts/1/delete
list_url = post.generate_route('list')        # /posts

# Redirect
post.redirect_to('show')  # Redirects to /posts/1
```

### Override with Decorator

```python
from base_model import BaseModel, route_handler

class Post(BaseModel):
    title = Field()
    slug = Field()
    
    @route_handler('show')
    def custom_show_route(self, **params):
        """Custom route using slug instead of ID."""
        return url('post_by_slug', self.slug)
    
    @route_handler('edit')
    def custom_edit_route(self, **params):
        """Custom edit route with extra param."""
        return url('admin_edit_post', self.id, **params)
    
    def get_public_url(self):
        """Get public URL for this post."""
        return self.generate_route('show')
    
    def get_admin_url(self):
        """Get admin URL for this post."""
        return self.generate_route('edit', source='admin')
```

---

## 8. Complex Queries (Methods in Child Model)

Complex queries should be methods in the respective child model:

```python
class Post(BaseModel):
    title = Field()
    content = Field.text()
    published = Field.bool()
    user_id = Field.int()
    created_at = Field.datetime()
    
    # Complex query methods
    @classmethod
    def get_published(cls):
        """Get all published posts."""
        return cls.where(lambda p: p.published == True).select(
            orderby=~cls.created_at
        )
    
    @classmethod
    def get_by_author(cls, user_id):
        """Get posts by specific author."""
        return cls.where(lambda p: p.user_id == user_id).select(
            orderby=~cls.created_at
        )
    
    @classmethod
    def get_popular(cls, days=7):
        """Get popular posts from last N days."""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        return cls.where(
            lambda p: (p.published == True) & (p.created_at > cutoff)
        ).select(
            orderby=~cls.view_count,
            limitby=(0, 10)
        )
    
    @classmethod
    def search(cls, query):
        """Full-text search."""
        return cls.where(
            lambda p: (p.title.contains(query)) | (p.content.contains(query))
        ).select()
    
    def get_related_posts(self, limit=5):
        """Get posts related to this one."""
        return Post.where(
            lambda p: (p.user_id == self.user_id) & 
                     (p.id != self.id) & 
                     (p.published == True)
        ).select(limitby=(0, limit))
    
    def get_comments_with_author(self):
        """Get comments with author info (complex join)."""
        # Complex query that joins comments with users
        return db(
            (Comment.post == self.id) & 
            (Comment.user == User.id)
        ).select(
            Comment.ALL,
            User.username,
            User.email,
            orderby=~Comment.created_at
        )
```

---

## Complete Example

Here's a complete example using all features:

```python
from base_model import (
    BaseModel, 
    http_handler, 
    response_formatter,
    template_renderer,
    api_client,
    email_handler,
    session_handler,
    route_handler
)
from emmett.orm import Field, belongs_to, has_many
from emmett import now, abort

class Post(BaseModel):
    """Complete fat model with all features."""
    
    # Relationships
    belongs_to('user')
    has_many('comments')
    
    # Fields
    title = Field()
    content = Field.text()
    slug = Field()
    published = Field.bool(default=False)
    published_at = Field.datetime()
    created_at = Field.datetime()
    view_count = Field.int(default=0)
    
    # Validation
    validation = {
        'title': {'presence': True, 'len': {'gte': 3, 'lte': 200}},
        'content': {'presence': True}
    }
    
    # Defaults
    default_values = {
        'created_at': now,
        'view_count': 0
    }
    
    # ========================================================================
    # HTTP Handlers
    # ========================================================================
    
    @http_handler('create')
    def handle_create(self, req):
        """Custom create with slug generation."""
        self.title = req.body_params['title']
        self.content = req.body_params['content']
        self.slug = self.generate_slug(self.title)
        self.user_id = session.auth.user.id
        self.save()
        
        return {
            'id': self.id,
            'slug': self.slug,
            'url': self.generate_route('show')
        }
    
    @http_handler('update')
    def handle_update(self, req):
        """Custom update with permission check."""
        if self.user_id != session.auth.user.id:
            abort(403)
        
        self.update_record(**req.body_params)
        return {'id': self.id, 'message': 'Updated'}
    
    # ========================================================================
    # Response Formatters
    # ========================================================================
    
    @response_formatter('json')
    def format_json(self, data):
        """JSON with computed fields."""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.content[:100],
            'published': self.published,
            'view_count': self.view_count,
            'comment_count': self.comments.count(),
            '_links': {
                'self': self.generate_route('show'),
                'comments': url('post_comments', self.id)
            }
        }
    
    # ========================================================================
    # Template Rendering
    # ========================================================================
    
    @template_renderer('post.html')
    def render_post(self, **context):
        """Render with related data."""
        context['related_posts'] = self.get_related_posts()
        context['sentiment'] = self.analyze_sentiment()
        self.increment_views()
        return current.app.template('post_detail.html', **context)
    
    # ========================================================================
    # External APIs
    # ========================================================================
    
    @api_client('/sentiment')
    def call_sentiment_api(self, method, data):
        """Call sentiment analysis API."""
        import requests
        resp = requests.post(
            'https://api.sentiment.com/analyze',
            json={'text': self.content},
            headers={'Authorization': f'Bearer {os.environ.get("SENTIMENT_API_KEY")}'}
        )
        return resp.json()
    
    # ========================================================================
    # Email Handlers
    # ========================================================================
    
    @email_handler('published')
    def send_publish_notification(self, to, subject, body):
        """Send custom publish notification."""
        from emmett import current
        mailer = current.app.ext.Mailer
        
        html = current.app.template('emails/post_published.html', post=self)
        mailer.send(to=to, subject=f"New: {self.title}", body=html)
        
        return {'success': True}
    
    # ========================================================================
    # Session Handlers
    # ========================================================================
    
    @session_handler('get', 'viewed_posts')
    def get_viewed(self, key, default):
        """Get viewed posts from session."""
        return session.get('viewed_posts', [])
    
    @session_handler('set', 'viewed_posts')
    def set_viewed(self, key, value):
        """Set viewed posts in session."""
        session['viewed_posts'] = value
        return True
    
    # ========================================================================
    # Route Handlers
    # ========================================================================
    
    @route_handler('show')
    def show_route(self, **params):
        """Custom route using slug."""
        return url('post_by_slug', self.slug)
    
    # ========================================================================
    # Complex Queries
    # ========================================================================
    
    @classmethod
    def get_published(cls):
        """Get published posts."""
        return cls.where(lambda p: p.published == True).select(
            orderby=~cls.published_at
        )
    
    @classmethod
    def search(cls, query):
        """Search posts."""
        return cls.where(
            lambda p: p.title.contains(query) | p.content.contains(query)
        ).select()
    
    def get_related_posts(self, limit=5):
        """Get related posts."""
        return Post.where(
            lambda p: (p.user_id == self.user_id) & (p.id != self.id)
        ).select(limitby=(0, limit))
    
    # ========================================================================
    # Business Logic
    # ========================================================================
    
    def publish(self):
        """Publish post and notify subscribers."""
        self.published = True
        self.published_at = now()
        self.save()
        
        # Notify subscribers
        subscribers = User.where(lambda u: u.subscribed == True).select()
        for sub in subscribers:
            self.send_email(
                to=sub.email,
                subject='',
                body='',
                email_type='published'
            )
    
    def increment_views(self):
        """Increment view count."""
        self.view_count += 1
        self.save()
        self.set_session_data('viewed_posts', self.id)
    
    def analyze_sentiment(self):
        """Analyze content sentiment."""
        result = self.call_api('/sentiment', 'POST', {'text': self.content})
        return result.get('sentiment', 'neutral')
    
    def generate_slug(self, title):
        """Generate URL slug from title."""
        import re
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
```

---

## Best Practices

### 1. Use Defaults When Possible
The default implementations are sensible. Only override when you need custom behavior.

### 2. Keep Decorators Simple
Decorators should contain minimal logic. Extract complex logic into helper methods.

### 3. Document Your Overrides
Always document why you're overriding the default.

### 4. Group Related Methods
Organize your model code by feature (HTTP, templates, APIs, etc.).

### 5. Complex Queries as Class Methods
Use `@classmethod` for queries that don't need an instance.

---

---

## 9. Automatic Route Generation

### Overview

BaseModel supports **automatic route generation** through the `auto_routes` class attribute. This eliminates the need for manual `setup()` functions in your model modules.

**Benefits**:
- ✅ Zero boilerplate - enable with one line
- ✅ Consistent URL patterns across all models
- ✅ Automatic REST API generation
- ✅ Declarative configuration
- ✅ Backward compatible with manual setup()

### Quick Start

```python
from base_model import BaseModel

class Role(BaseModel):
    name = Field.string()
    description = Field.text()
    
    # Enable automatic routes with defaults
    auto_routes = True
```

**That's it!** Your model now has:
- **HTML routes**: `/roles/`, `/roles/<id>`, `/roles/new`, `/roles/<id>/edit`, `/roles/<id>/delete`
- **REST API**: `GET/POST /api/roles`, `GET/PUT/DELETE /api/roles/<id>`

### Configuration API

#### Basic Configuration

```python
class Role(BaseModel):
    name = Field.string()
    
    auto_routes = {
        'url_prefix': '/admin/roles',           # Default: /{tablename}
        'rest_api': True,                       # Default: True
        'rest_prefix': '/api/v1/roles',         # Default: /api/{tablename}
        'enabled_actions': ['list', 'detail'],  # Default: all actions
    }
```

#### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url_prefix` | `str` | `/{tablename}` | Base URL for HTML routes |
| `rest_api` | `bool` | `True` | Generate REST API endpoints |
| `rest_prefix` | `str` | `/api/{tablename}` | Base URL for REST endpoints |
| `enabled_actions` | `list` | All | Actions to enable: `list`, `detail`, `create`, `update`, `delete` |
| `permissions` | `dict` | `{}` | Permission functions per action |
| `auto_ui_config` | `dict` | `{}` | Pass-through config to auto_ui |
| `custom_handlers` | `dict` | `{}` | Custom route handlers (future) |

#### Permission Integration

```python
from model_permissions import requires_role

class Role(BaseModel):
    name = Field.string()
    
    auto_routes = {
        'url_prefix': '/admin/roles',
        'permissions': {
            'list': lambda: requires_role('Admin'),
            'create': lambda: requires_role('Admin'),
            'update': lambda: requires_role('Admin'),
            'delete': lambda: requires_role('Admin'),
        }
    }
```

#### Selective Action Enabling

```python
class Role(BaseModel):
    name = Field.string()
    
    # Only allow viewing, no modifications
    auto_routes = {
        'enabled_actions': ['list', 'detail']
    }
```

#### Advanced Configuration

```python
class Post(BaseModel):
    title = Field.string()
    content = Field.text()
    
    auto_routes = {
        'url_prefix': '/blog/posts',
        'rest_prefix': '/api/v2/posts',
        'enabled_actions': ['list', 'detail', 'create', 'update'],
        'permissions': {
            'create': lambda: requires_role('Author'),
            'update': lambda: requires_permission('post.edit.own'),
        },
        'auto_ui_config': {
            'list_columns': ['title', 'created_at', 'author'],
            'search_fields': ['title', 'content'],
            'sort_default': '-created_at'
        }
    }
```

### Generated Routes

When `auto_routes = True`, the following routes are generated:

**HTML Routes**:
| Route | Method | Action | Description |
|-------|--------|--------|-------------|
| `{url_prefix}/` | GET | list | List all records |
| `{url_prefix}/new` | GET | create | Show create form |
| `{url_prefix}/` | POST | create | Process create form |
| `{url_prefix}/<id>` | GET | detail | Show single record |
| `{url_prefix}/<id>/edit` | GET | update | Show edit form |
| `{url_prefix}/<id>` | POST | update | Process update form |
| `{url_prefix}/<id>/delete` | GET | delete | Show delete confirmation |
| `{url_prefix}/<id>/delete` | POST | delete | Process deletion |

**REST API Routes** (when `rest_api: True`):
| Route | Method | Action | Description |
|-------|--------|--------|-------------|
| `{rest_prefix}` | GET | list | List all records (JSON) |
| `{rest_prefix}` | POST | create | Create record (JSON) |
| `{rest_prefix}/<id>` | GET | detail | Get single record (JSON) |
| `{rest_prefix}/<id>` | PUT | update | Update record (JSON) |
| `{rest_prefix}/<id>` | DELETE | delete | Delete record (JSON) |

### Precedence Rules

**Manual setup() takes precedence over auto_routes**:

```python
# models/role/model.py
class Role(BaseModel):
    name = Field.string()
    auto_routes = True  # This will be IGNORED if setup() exists

# models/role/__init__.py
from .model import Role

def setup(app, db):
    """Manual setup takes precedence."""
    # Custom routes here
    @app.route('/custom/roles')
    async def custom_roles():
        return {'roles': Role.all().select()}
```

**Why?** Manual setup provides maximum flexibility. The auto discovery system checks for `setup()` functions and skips models that have them.

**Precedence order**:
1. **Manual setup() function** - Highest priority
2. **auto_routes configuration** - Used if no setup()
3. **Default behavior** - Models without either are not auto-registered

### Disabling Auto Routes

```python
class InternalModel(BaseModel):
    data = Field.text()
    
    # Explicitly disable auto routes
    auto_routes = False
```

Or simply omit the `auto_routes` attribute entirely.

### Common Use Cases

#### 1. Admin-Only Model

```python
class Permission(BaseModel):
    name = Field.string()
    resource = Field.string()
    action = Field.string()
    
    auto_routes = {
        'url_prefix': '/admin/permissions',
        'permissions': {
            'list': lambda: requires_role('Admin'),
            'create': lambda: requires_role('Admin'),
            'update': lambda: requires_role('Admin'),
            'delete': lambda: requires_role('Admin'),
        }
    }
```

#### 2. Read-Only API

```python
class Report(BaseModel):
    title = Field.string()
    data = Field.text()
    
    auto_routes = {
        'enabled_actions': ['list', 'detail'],
        'rest_api': True
    }
```

#### 3. Custom URL Structure

```python
class BlogPost(BaseModel):
    title = Field.string()
    slug = Field.string()
    
    auto_routes = {
        'url_prefix': '/blog/posts',
        'rest_prefix': '/api/blog/posts',
        'auto_ui_config': {
            'list_columns': ['title', 'slug', 'created_at'],
            'search_fields': ['title', 'content']
        }
    }
```

#### 4. Public + Admin Access

```python
class Article(BaseModel):
    title = Field.string()
    published = Field.bool()
    
    auto_routes = {
        'url_prefix': '/articles',
        'permissions': {
            # List and detail are public (no permission)
            'create': lambda: requires_role('Editor'),
            'update': lambda: requires_permission('article.edit.own'),
            'delete': lambda: requires_role('Admin'),
        }
    }
```

### Migration Guide

#### From Manual setup() to auto_routes

**Before** (manual setup):
```python
# models/role/model.py
from base_model import BaseModel

class Role(BaseModel):
    name = Field.string()
    description = Field.text()

# models/role/__init__.py
from .model import Role
from auto_ui_generator import auto_ui

def setup(app, db):
    """Manual route setup."""
    auto_ui(app, Role, '/admin/roles', {
        'permissions': {
            'list': lambda: requires_role('Admin'),
            'create': lambda: requires_role('Admin'),
            'update': lambda: requires_role('Admin'),
            'delete': lambda: requires_role('Admin'),
        }
    })
```

**After** (auto_routes):
```python
# models/role/model.py
from base_model import BaseModel
from model_permissions import requires_role

class Role(BaseModel):
    name = Field.string()
    description = Field.text()
    
    auto_routes = {
        'url_prefix': '/admin/roles',
        'permissions': {
            'list': lambda: requires_role('Admin'),
            'create': lambda: requires_role('Admin'),
            'update': lambda: requires_role('Admin'),
            'delete': lambda: requires_role('Admin'),
        }
    }

# models/role/__init__.py - DELETE this file or remove setup()
# from .model import Role  # Remove setup() function
```

**Benefits**:
- ✅ 15 lines → 12 lines
- ✅ No separate `__init__.py` needed
- ✅ Configuration lives with the model
- ✅ Easier to understand at a glance

#### Migration Steps

1. **Add auto_routes to model class**:
   ```python
   auto_routes = True  # Start simple
   ```

2. **Remove or comment out setup() function**:
   ```python
   # def setup(app, db):  # Commented out
   #     auto_ui(app, Role, '/admin/roles')
   ```

3. **Test the application**:
   ```bash
   ./run_bloggy.sh
   # Visit your model's URL to verify routes work
   ```

4. **Add configuration if needed**:
   ```python
   auto_routes = {
       'url_prefix': '/admin/roles',
       'permissions': {...}
   }
   ```

5. **Delete setup() completely** once verified

#### Keeping Manual setup() for Complex Cases

Some models may need custom route logic that auto_routes can't handle:

```python
# Keep manual setup() for:
# - Custom route handlers
# - Non-standard URL patterns
# - Complex permission logic
# - Integration with external systems

def setup(app, db):
    """Custom routes that auto_routes can't generate."""
    
    @app.route('/roles/export', methods=['get'])
    async def export_roles():
        # Custom export logic
        pass
    
    @app.route('/roles/import', methods=['post'])
    async def import_roles():
        # Custom import logic
        pass
```

**You can mix both approaches**: Use manual setup() for custom routes and let other models use auto_routes.

### Integration with Application

Auto routes are discovered and registered automatically on application startup:

```python
# runtime/app.py
from emmett import App
from emmett.orm import Database

app = App(__name__)
db = Database(app, auto_migrate=True)

# Define all models
db.define_models()

# Auto-discover and register routes for models with auto_routes
from auto_routes import discover_and_register_auto_routes
discover_and_register_auto_routes(app, db)

# This happens automatically - no need to import each model!
```

**Discovery process**:
1. Scans all BaseModel subclasses
2. Finds models with `auto_routes` attribute
3. Checks if model has manual `setup()` (skips if found)
4. Parses and validates configuration
5. Generates HTML and REST API routes
6. Registers routes with the app

### Troubleshooting

#### Routes Not Generating

**Problem**: Model has `auto_routes = True` but routes don't appear.

**Solutions**:
- Check if model has manual `setup()` function (takes precedence)
- Verify `discover_and_register_auto_routes()` is called in app.py
- Check application logs for discovery errors
- Ensure model is imported and registered with database

#### Permission Errors

**Problem**: Routes generate but permission checks fail.

**Solutions**:
- Verify permission functions are callable: `lambda: requires_role('Admin')`
- Check that permission functions are imported properly
- Test permission functions independently
- Review logs for permission-related errors

#### URL Conflicts

**Problem**: Auto-generated routes conflict with existing routes.

**Solutions**:
- Change `url_prefix` to avoid conflicts
- Use manual `setup()` for models with conflicting URLs
- Review route registration order in app.py

#### REST API Not Generating

**Problem**: HTML routes work but REST API doesn't generate.

**Solutions**:
- Verify `rest_api: True` in configuration
- Check `rest_prefix` doesn't conflict with existing routes
- Review logs for REST API generation errors

### Best Practices

1. **Start Simple**: Begin with `auto_routes = True`, add configuration as needed

2. **Use Descriptive URL Prefixes**: 
   ```python
   url_prefix = '/admin/roles'  # Good
   url_prefix = '/r'            # Bad
   ```

3. **Group Related Models**: Use consistent URL structure
   ```python
   # Good: Consistent structure
   Role: url_prefix = '/admin/roles'
   Permission: url_prefix = '/admin/permissions'
   User: url_prefix = '/admin/users'
   ```

4. **Document Custom Configurations**: Add comments for non-obvious settings
   ```python
   auto_routes = {
       # Only admins can manage permissions
       'permissions': {
           'list': lambda: requires_role('Admin')
       }
   }
   ```

5. **Test After Enabling**: Always verify routes work after adding auto_routes

6. **Keep Manual setup() for Truly Custom Routes**: Don't fight the framework

---

## Summary

**BaseModel provides**:
- ✅ HTTP request handling with `handle_request()`
- ✅ Response formatting with `format_response()`
- ✅ Template rendering with `render_template()`
- ✅ External API calls with `call_api()`
- ✅ Email sending with `send_email()`
- ✅ Session management with `get_session_data()` / `set_session_data()`
- ✅ Routing logic with `generate_route()` / `redirect_to()`
- ✅ Complex queries as model methods
- ✅ **Automatic route generation with `auto_routes`** ⭐ NEW

**All with sensible defaults and decorator-based overrides!**

