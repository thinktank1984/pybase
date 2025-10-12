# Emmett Active Record Pattern - Comprehensive Guide

## Table of Contents
1. [Introduction](#introduction)
2. [What is Active Record?](#what-is-active-record)
3. [Emmett's Active Record Implementation](#emmetts-active-record-implementation)
4. [Model Organization Best Practices](#model-organization-best-practices)
5. [Field Definitions](#field-definitions)
6. [Validation](#validation)
7. [Computed & Virtual Fields](#computed--virtual-fields)
8. [Form Configuration](#form-configuration)
9. [REST API Auto-Generation](#rest-api-auto-generation)
10. [CRUD UI Auto-Generation](#crud-ui-auto-generation)
11. [OpenAPI/Swagger Integration](#openapiswagger-integration)
12. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
13. [Testing Models](#testing-models)

---

## Introduction

This guide provides comprehensive documentation on using Emmett's built-in Active Record pattern effectively. Emmett's `Model` class already implements the Active Record pattern, providing a rich set of features out of the box.

**Key Point**: You don't need to create a custom `ActiveRecord` base class - Emmett's `Model` already provides everything you need!

---

## What is Active Record?

Active Record is an architectural pattern where:
- A model class corresponds to a database table
- An instance of the model represents a row in the table
- The model has methods to save, update, and delete itself
- Business logic lives in the model

**Example:**
```python
post = Post.get(1)
post.title = "Updated Title"
post.save()  # Active Record pattern - object knows how to save itself
```

---

## Emmett's Active Record Implementation

Emmett's `Model` class provides the following Active Record methods:

### Instance Methods (operate on single records)
- `save()` - Save changes to the database
- `update_record(**fields)` - Update specific fields
- `delete_record()` - Delete this record
- `destroy()` - Alias for delete_record()

### Class Methods (operate on the model/table)
- `create(**fields)` - Create a new record
- `get(id)` - Get record by ID
- `all()` - Get all records
- `where(query)` - Filter records
- `first()` - Get first record
- `last()` - Get last record
- `count()` - Count records

### Example:
```python
from emmett.orm import Model, Field

class Post(Model):
    title = Field()
    content = Field.text()
    published = Field.bool(default=False)
    
    validation = {
        'title': {'presence': True, 'len': {'gte': 3}},
        'content': {'presence': True}
    }

# Using Active Record methods
post = Post.create(title="My Post", content="Content here")
post.published = True
post.save()

# Query methods
all_posts = Post.all().select()
published = Post.where(lambda p: p.published == True).select()
```

---

## Model Organization Best Practices

### Recommended Structure

Organize your models following this structure:

```python
from emmett.orm import Model, Field, belongs_to, has_many
from emmett import now

class Post(Model):
    """Blog post model.
    
    Represents a blog post with title, content, and metadata.
    Posts belong to users and can have many comments.
    """
    
    # 1. Relationships (at the top for clarity)
    belongs_to('user')
    has_many('comments')
    
    # 2. Field Definitions
    title = Field()
    content = Field.text()
    published = Field.bool(default=False)
    published_at = Field.datetime()
    created_at = Field.datetime()
    updated_at = Field.datetime()
    
    # 3. Model Configuration
    tablename = "posts"  # Optional: customize table name
    
    # 4. Default Values
    default_values = {
        'created_at': now,
        'updated_at': now,
        'published': False
    }
    
    # 5. Validation Rules
    validation = {
        'title': {'presence': True, 'len': {'gte': 3, 'lte': 200}},
        'content': {'presence': True, 'len': {'gte': 10}},
        'user': {'presence': True}
    }
    
    # 6. Update Triggers
    update_values = {
        'updated_at': now
    }
    
    # 7. Field Visibility (for forms and APIs)
    fields_rw = {
        'created_at': False,  # Not writable in forms
        'updated_at': False,
        'user': (False, True)  # Hidden in forms, but writable via API
    }
    
    # 8. Form Configuration
    form_labels = {
        'title': 'Post Title',
        'content': 'Post Content',
        'published': 'Publish Now'
    }
    
    form_info = {
        'title': 'Enter a descriptive title for your blog post',
        'content': 'Write your post content here (Markdown supported)'
    }
    
    # 9. Computed Fields (if needed)
    @property
    def excerpt(self):
        """Generate excerpt from content."""
        if not self.content:
            return ""
        return self.content[:100] + "..." if len(self.content) > 100 else self.content
    
    @property
    def is_published(self):
        """Check if post is published."""
        return self.published and self.published_at is not None
    
    # 10. Business Logic Methods
    def publish(self):
        """Publish the post."""
        self.published = True
        self.published_at = now()
        self.save()
    
    def unpublish(self):
        """Unpublish the post."""
        self.published = False
        self.published_at = None
        self.save()
    
    def can_edit(self, user):
        """Check if user can edit this post."""
        return user and (user.id == self.user or user.is_admin())
    
    def get_comment_count(self):
        """Get number of comments."""
        return self.comments.count()
```

### What Belongs in Models

✅ **DO include in models:**
- Field definitions
- Validation rules
- Default values
- Computed properties (derived from existing fields)
- Business logic methods (publish, archive, etc.)
- Permission checking methods (can_edit, can_delete)
- Simple query helpers
- Relationships

❌ **DON'T include in models:**
- HTTP request handling
- Response formatting
- Template rendering
- External API calls
- Email sending (should be in services)
- Complex queries (use repositories/services)
- Session management
- Routing logic

---

## Field Definitions

### Available Field Types

```python
from emmett.orm import Field

class MyModel(Model):
    # String (default)
    name = Field()
    email = Field()
    
    # Text (long strings)
    description = Field.text()
    content = Field.text()
    
    # Numbers
    count = Field.int()
    price = Field.float()
    precise_value = Field.decimal(10, 2)
    
    # Boolean
    active = Field.bool()
    published = Field.bool(default=False)
    
    # Dates and Times
    created_at = Field.datetime()
    birth_date = Field.date()
    meeting_time = Field.time()
    
    # Special Types
    password = Field.password()  # Automatically hashed
    avatar = Field.upload()      # File upload
    data = Field.json()          # JSON storage
    tags = Field.string_list()   # List of strings
```

### Field Parameters

```python
# Common field parameters
title = Field(
    length=200,              # Maximum length for strings
    default="Untitled",      # Default value
    notnull=True,           # Require value (NOT NULL)
    unique=True,            # Unique constraint
    rw=(True, True),        # Read-write permissions (read, write)
    label="Post Title",     # Form label
    comment="The title",    # Database comment
)

# Numeric fields
price = Field.float(
    default=0.0,
    ge=0.0,                 # Greater than or equal
    le=1000000.0,           # Less than or equal
)

# Date/time fields
created_at = Field.datetime(
    default=now,            # Function called on create
    update=now,             # Function called on update
)
```

---

## Validation

### Built-in Validation Rules

Emmett provides comprehensive validation through the `validation` attribute:

```python
class User(Model):
    email = Field()
    username = Field()
    age = Field.int()
    bio = Field.text()
    
    validation = {
        # Presence validation
        'email': {'presence': True},
        
        # Length validation
        'username': {
            'presence': True,
            'len': {'gte': 3, 'lte': 20}  # Between 3 and 20 chars
        },
        
        # Range validation (for numbers)
        'age': {
            'allow': 'empty',  # Optional field
            'gte': 13,         # Greater than or equal
            'lte': 120         # Less than or equal
        },
        
        # Format validation (regex)
        'email': {
            'presence': True,
            'is': {'email': True}  # Email format
        },
        
        # Custom validation
        'bio': {
            'len': {'lte': 500},
            'custom': {
                'rule': lambda value: 'spam' not in value.lower(),
                'message': 'Bio contains forbidden content'
            }
        }
    }
```

### Common Validation Rules

```python
validation = {
    # Presence
    'field': {'presence': True},
    
    # Allow empty/null
    'field': {'allow': 'empty'},  # or 'blank' or 'none'
    
    # Length
    'field': {'len': {'gte': 3, 'lte': 100}},
    'field': {'len': {'eq': 10}},  # Exactly 10 chars
    
    # Numeric ranges
    'field': {'gt': 0, 'lt': 100},   # Greater than / less than
    'field': {'gte': 0, 'lte': 100}, # Greater/less or equal
    
    # Format validation
    'email': {'is': {'email': True}},
    'url': {'is': {'url': True}},
    'ip': {'is': {'ip': True}},
    
    # Pattern matching
    'field': {'match': r'^[A-Z][a-z]+$'},
    
    # In list
    'status': {'in': ['draft', 'published', 'archived']},
    
    # Not in list
    'username': {'not_in': ['admin', 'root', 'system']},
    
    # Unique
    'email': {'unique': True},
    
    # Custom validation
    'field': {
        'custom': {
            'rule': lambda value: custom_check(value),
            'message': 'Custom validation failed'
        }
    }
}
```

### Custom Validation Functions

```python
def validate_username(value):
    """Custom validation for username."""
    if not value:
        return False
    if value.lower() in ['admin', 'root']:
        return False
    if not value[0].isalpha():
        return False
    return True

class User(Model):
    username = Field()
    
    validation = {
        'username': {
            'presence': True,
            'custom': {
                'rule': validate_username,
                'message': 'Invalid username'
            }
        }
    }
```

---

## Computed & Virtual Fields

### Property-based Computed Fields

```python
class Post(Model):
    content = Field.text()
    created_at = Field.datetime()
    
    @property
    def excerpt(self):
        """Computed field: excerpt from content."""
        if not self.content:
            return ""
        return self.content[:100] + "..." if len(self.content) > 100 else self.content
    
    @property
    def age_days(self):
        """Computed field: days since creation."""
        if not self.created_at:
            return 0
        from datetime import datetime
        return (datetime.now() - self.created_at).days

# Usage
post = Post.get(1)
print(post.excerpt)    # Automatically computed
print(post.age_days)   # Automatically computed
```

### Virtual Fields (Emmett's approach)

```python
class Post(Model):
    title = Field()
    content = Field.text()
    
    # Define virtual/computed fields
    virtual_fields = {
        'word_count': lambda self: len(self.content.split()) if self.content else 0,
        'title_upper': lambda self: self.title.upper() if self.title else ''
    }

# Usage
post = Post.get(1)
print(post.word_count)   # Computed on access
```

---

## Form Configuration

### Form Labels

```python
class Post(Model):
    title = Field()
    content = Field.text()
    published = Field.bool()
    
    form_labels = {
        'title': 'Post Title',
        'content': 'Post Content',
        'published': 'Publish Immediately'
    }
```

### Form Help Text

```python
class Post(Model):
    title = Field()
    content = Field.text()
    
    form_info = {
        'title': 'Enter a descriptive title (3-200 characters)',
        'content': 'Write your post content here. Markdown is supported.'
    }
```

### Custom Form Widgets

```python
class Post(Model):
    content = Field.text()
    status = Field()
    
    form_widgets = {
        'content': 'text',  # Use textarea widget
        'status': 'select'   # Use dropdown
    }
```

### Field Visibility in Forms

```python
class Post(Model):
    user_id = Field.int()
    created_at = Field.datetime()
    updated_at = Field.datetime()
    
    # Control which fields appear in forms
    fields_rw = {
        'user_id': False,      # Hidden in forms (set by system)
        'created_at': False,   # Hidden in forms (auto-set)
        'updated_at': False    # Hidden in forms (auto-updated)
    }
```

---

## REST API Auto-Generation

Emmett can automatically generate REST API endpoints for your models:

### Basic REST API Setup

```python
from emmett import App
from emmett.orm import Database
from emmett_rest import REST

app = App(__name__)
db = Database(app)

# Enable REST extension
app.use_extension(REST)

# Define your model
class Post(Model):
    title = Field()
    content = Field.text()
    
    validation = {
        'title': {'presence': True},
        'content': {'presence': True}
    }

db.define_models(Post)

# Auto-generate REST API
posts_api = app.rest_module(
    __name__,
    'posts_api',
    Post,
    url_prefix='api/posts'
)

# This automatically creates:
# GET    /api/posts       - List all posts
# GET    /api/posts/:id   - Get single post
# POST   /api/posts       - Create post
# PUT    /api/posts/:id   - Update post
# DELETE /api/posts/:id   - Delete post
```

### Customizing REST API

```python
class Post(Model):
    title = Field()
    content = Field.text()
    user_id = Field.int()
    
    # Control API read/write permissions
    rest_rw = {
        'user_id': (False, True),  # Hidden in output, writable in input
        'created_at': (True, False)  # Visible in output, not writable
    }

# Create API with custom configuration
posts_api = app.rest_module(
    __name__,
    'posts_api',
    Post,
    url_prefix='api/posts',
    enabled_methods=['index', 'read', 'create'],  # Only GET and POST
    disabled_methods=['update', 'delete']  # No PUT or DELETE
)

# Add callbacks for custom logic
@posts_api.before_create
def set_user(attrs):
    """Set user_id from current session."""
    if session.auth:
        attrs['user_id'] = session.auth.user.id

@posts_api.before_update
def check_permission(dbset, attrs):
    """Check user can update this post."""
    post = dbset.select().first()
    if not post or post.user_id != session.auth.user.id:
        abort(403)
```

---

## CRUD UI Auto-Generation

Use the existing `auto_ui_generator.py` to automatically generate CRUD interfaces:

### Basic Auto UI Setup

```python
from auto_ui_generator import auto_ui

# Enable auto-generated CRUD interface
auto_ui(app, Post, '/admin/posts')

# This automatically creates:
# GET  /admin/posts/         - List view with pagination
# GET  /admin/posts/new      - Create form
# POST /admin/posts/         - Create action
# GET  /admin/posts/:id      - Detail view
# GET  /admin/posts/:id/edit - Edit form
# POST /admin/posts/:id      - Update action
# POST /admin/posts/:id/delete - Delete action
```

### Customizing Auto UI

```python
class Post(Model):
    title = Field()
    content = Field.text()
    published = Field.bool()
    created_at = Field.datetime()
    
    # Configure auto UI behavior
    auto_ui_config = {
        'display_name': 'Blog Post',
        'display_name_plural': 'Blog Posts',
        'list_columns': ['id', 'title', 'published', 'created_at'],
        'search_fields': ['title', 'content'],
        'sort_default': '-created_at',  # Newest first
        'page_size': 25,
        
        # Permissions
        'permissions': {
            'list': lambda: True,  # Anyone can view
            'create': lambda: session.auth is not None,  # Must be logged in
            'read': lambda: True,
            'update': lambda: session.auth is not None,
            'delete': lambda: session.auth and session.auth.user.is_admin()
        },
        
        # Field-specific configuration
        'field_config': {
            'title': {
                'display_name': 'Post Title',
                'help_text': 'Enter a descriptive title'
            },
            'content': {
                'display_name': 'Content',
                'help_text': 'Write your post content'
            }
        }
    }

# Apply auto UI with configuration
auto_ui(app, Post, '/admin/posts')
```

---

## OpenAPI/Swagger Integration

The existing `openapi_generator.py` automatically generates OpenAPI/Swagger docs:

### Setup

```python
from openapi_generator import OpenAPIGenerator

# Initialize OpenAPI generator
openapi_gen = OpenAPIGenerator(
    app,
    title="My API",
    version="1.0.0",
    description="API documentation"
)

# Register your REST modules
openapi_gen.register_rest_module('posts_api', Post, 'api/posts')
openapi_gen.register_rest_module('comments_api', Comment, 'api/comments')

# Serve OpenAPI spec
@app.route('/api/openapi.json')
async def openapi_spec():
    return openapi_gen.generate()

# Serve Swagger UI
@app.route('/api/docs')
async def swagger_ui():
    # Return Swagger UI HTML (see openapi_generator.py)
    pass
```

---

## Anti-Patterns to Avoid

### ❌ DON'T: Mix HTTP concerns with models

```python
# BAD
class Post(Model):
    title = Field()
    
    def create_from_request(self, request):
        """Don't handle HTTP requests in models!"""
        self.title = request.body_params.get('title')
        self.save()
    
    def to_json_response(self):
        """Don't format responses in models!"""
        return {'id': self.id, 'title': self.title}
```

```python
# GOOD
class Post(Model):
    title = Field()
    
    # Models should only have domain logic
    def publish(self):
        self.published = True
        self.save()

# Handle HTTP in controllers
@app.route('/posts', methods=['post'])
async def create_post():
    title = request.body_params.get('title')
    post = Post.create(title=title)
    return {'id': post.id, 'title': post.title}
```

### ❌ DON'T: Put presentation logic in models

```python
# BAD
class Post(Model):
    content = Field.text()
    
    def render_html(self):
        """Don't generate HTML in models!"""
        return f"<div class='post'>{self.content}</div>"
```

```python
# GOOD
class Post(Model):
    content = Field.text()
    
    @property
    def excerpt(self):
        """Data transformation is OK"""
        return self.content[:100] + "..."

# Handle presentation in templates
# templates/post.html
# <div class="post">{{ post.content }}</div>
```

### ❌ DON'T: Make external API calls in models

```python
# BAD
class User(Model):
    email = Field()
    
    def send_welcome_email(self):
        """Don't call external services directly!"""
        import requests
        requests.post('https://api.sendgrid.com/...')
```

```python
# GOOD
class User(Model):
    email = Field()
    
    def mark_welcomed(self):
        """Domain logic only"""
        self.welcomed = True
        self.save()

# Use a service for external calls
class EmailService:
    def send_welcome_email(self, user):
        import requests
        requests.post('https://api.sendgrid.com/...')
        user.mark_welcomed()
```

### ❌ DON'T: Put complex business logic in models

```python
# BAD
class Order(Model):
    def process_payment_and_ship(self, payment_method, address):
        """Too many responsibilities!"""
        # Payment processing
        # Inventory management
        # Shipping logic
        # Email notifications
        # All in one method!
```

```python
# GOOD
class Order(Model):
    def mark_paid(self):
        """Simple state change"""
        self.paid = True
        self.save()
    
    def mark_shipped(self):
        """Simple state change"""
        self.shipped = True
        self.save()

# Use services for complex workflows
class OrderService:
    def process_order(self, order, payment, address):
        PaymentService.process(payment)
        order.mark_paid()
        InventoryService.reserve(order)
        ShippingService.ship(order, address)
        order.mark_shipped()
        EmailService.send_confirmation(order)
```

---

## Testing Models

### Unit Testing Models

```python
import pytest
from emmett.orm import Database
from emmett.testing import DatabaseTestCase

class TestPost(DatabaseTestCase):
    def setup_method(self):
        """Setup test database."""
        self.db = Database(self.app)
        self.db.define_models(Post)
    
    def test_create_post(self):
        """Test creating a post."""
        post = Post.create(
            title="Test Post",
            content="Test content"
        )
        assert post.id is not None
        assert post.title == "Test Post"
    
    def test_validation(self):
        """Test validation rules."""
        with pytest.raises(ValidationError):
            Post.create(title="", content="Test")  # Empty title
    
    def test_excerpt(self):
        """Test computed field."""
        post = Post.create(
            title="Test",
            content="A" * 200
        )
        assert len(post.excerpt) <= 103  # 100 chars + "..."
    
    def test_publish(self):
        """Test business logic method."""
        post = Post.create(
            title="Test",
            content="Content",
            published=False
        )
        post.publish()
        assert post.published is True
        assert post.published_at is not None
```

---

## Summary

Emmett provides a comprehensive Active Record implementation with:

✅ **Built-in features:**
- Active Record pattern (create, save, update, delete)
- Comprehensive validation
- Computed/virtual fields
- Form configuration
- REST API auto-generation
- CRUD UI auto-generation (via auto_ui_generator.py)
- OpenAPI/Swagger integration

✅ **Best practices:**
- Keep models focused on data and domain logic
- Use validation attribute for data validation
- Use properties for computed fields
- Configure forms via model attributes
- Separate concerns (models, controllers, services)

✅ **Available now:**
- No need for custom ActiveRecord base class
- No need for custom validators
- No need for custom API generators

**Remember**: Emmett's `Model` class IS Active Record. Use it!

