# Quick Start: New Utilities

## Overview

This guide shows you how to use the newly added utilities for Emmett model development.

---

## 1. Pattern Validation Tool

**Purpose**: Automatically check models for anti-patterns and best practices.

**Location**: `runtime/validate_models.py`

### Basic Usage

```bash
# Validate all models
cd runtime
python validate_models.py --all

# Validate specific models
python validate_models.py Post Comment

# Show only errors (hide warnings and info)
python validate_models.py --all --severity error

# Output as JSON for CI/CD
python validate_models.py --all --json

# Verbose output
python validate_models.py --all --verbose
```

### What It Checks

- ❌ HTTP request/response handling in models
- ❌ Template rendering in models
- ❌ HTML generation in models
- ❌ External API calls in models
- ❌ Direct session access in models
- ❌ Email sending in models
- ⚠️ Overly complex methods
- ℹ️ Missing validation rules
- ℹ️ Missing docstrings

### CI/CD Integration

Add to your `.github/workflows/test.yml` or similar:

```yaml
- name: Validate Models
  run: |
    cd runtime
    python validate_models.py --all --json --severity error
```

---

## 2. Row-Level Permissions

**Purpose**: Add row-level and field-level permissions to models.

**Location**: `runtime/model_permissions.py`

### Basic Example

```python
from emmett.orm import Model, Field
from model_permissions import PermissionMixin

class Post(Model, PermissionMixin):
    user_id = Field.int()
    title = Field()
    content = Field.text()
    published = Field.bool()
    
    # Define permission rules
    permissions = {
        'read': lambda record, user: record.published or record.user_id == user.id,
        'update': lambda record, user: record.user_id == user.id or user.is_admin(),
        'delete': lambda record, user: user.is_admin()
    }
```

### Usage in Controllers

```python
@app.route('/posts/<int:id>')
async def show_post(id):
    post = Post.get(id)
    if not post:
        abort(404)
    
    # Check permission
    if not post.can_read(current_user):
        abort(403)
    
    return dict(post=post)

@app.route('/posts/<int:id>/edit', methods=['post'])
async def update_post(id):
    post = Post.get(id)
    if not post:
        abort(404)
    
    # Automatically abort if no permission
    post.require_permission('update', current_user)
    
    # Update post...
    post.update_record(**request.body_params)
    return dict(success=True)
```

### Method-Level Permissions

```python
from model_permissions import requires_permission

class Post(Model, PermissionMixin):
    # ... fields ...
    
    @requires_permission('update')
    def publish(self):
        """Only users who can update can publish."""
        self.published = True
        self.save()
    
    @requires_permission('delete')
    def archive(self):
        """Only users who can delete can archive."""
        self.archived = True
        self.save()
```

### Field-Level Permissions

```python
from model_permissions import FieldPermissionMixin

class Employee(Model, PermissionMixin, FieldPermissionMixin):
    name = Field()
    salary = Field.float()
    department = Field()
    
    # Row-level permissions
    permissions = {
        'read': lambda record, user: user.department == record.department or user.is_hr(),
        'update': lambda record, user: user.is_manager()
    }
    
    # Field-level permissions
    field_permissions = {
        'salary': {
            'read': lambda record, user: user.is_hr() or record.id == user.id,
            'write': lambda record, user: user.is_hr()
        }
    }

# Usage
employee = Employee.get(1)
if employee.can_read_field('salary', current_user):
    print(f"Salary: {employee.salary}")

# Get only visible fields
visible_data = employee.get_visible_fields(current_user)
```

---

## 3. Model Factory for Testing

**Purpose**: Easily create test data for models.

**Location**: `runtime/model_factory.py`

### Define a Factory

```python
from model_factory import Factory, Generators
from app import Post

class PostFactory(Factory):
    model = Post
    
    # Static values
    published = False
    
    # Dynamic values with {n} placeholder
    title = "Test Post {n}"
    
    # Callable generators
    user_id = lambda n: 1
    date = Generators.datetime_past
    
    # Or use lambda for more control
    content = lambda n: f"This is test content for post number {n}."
```

### Use in Tests

```python
import pytest
from factories import PostFactory

def test_post_creation():
    """Test creating a post."""
    post = PostFactory.create()
    
    assert post.id is not None
    assert post.title.startswith("Test Post")
    assert post.user_id == 1

def test_multiple_posts():
    """Test creating multiple posts."""
    posts = PostFactory.create_batch(10)
    
    assert len(posts) == 10
    assert all(p.id is not None for p in posts)

def test_custom_post():
    """Test creating post with custom values."""
    post = PostFactory.create(
        title="Custom Title",
        published=True
    )
    
    assert post.title == "Custom Title"
    assert post.published == True

def test_with_faker():
    """Test using Faker generators (if installed)."""
    from model_factory import FakerGenerators
    
    class UserFactory(Factory):
        model = User
        email = FakerGenerators.email
        name = FakerGenerators.name
    
    user = UserFactory.create()
    assert '@' in user.email
```

### Built-in Generators

```python
from model_factory import Generators

# Email and username
email = Generators.email  # user{n}@example.com
username = Generators.username  # user{n}

# Random data
random_str = Generators.random_string(length=10)
random_int = Generators.random_int(min_val=0, max_val=100)
random_bool = Generators.random_bool()
random_choice = lambda: Generators.random_choice(['a', 'b', 'c'])

# Dates
datetime_now = Generators.datetime_now
datetime_past = Generators.datetime_past  # Random date in last 30 days
datetime_future = Generators.datetime_future  # Random date in next 30 days
```

### Complex Example

```python
class UserFactory(Factory):
    model = User
    email = Generators.email
    username = Generators.username
    first_name = "John"
    last_name = lambda n: f"Doe{n}"
    password = "testpass123"

class PostFactory(Factory):
    model = Post
    title = "Post {n}"
    content = lambda n: f"Content for post {n}"
    user_id = lambda: UserFactory.create().id  # Create related user
    date = Generators.datetime_past
    published = Generators.random_bool

class CommentFactory(Factory):
    model = Comment
    text = "Comment {n}"
    user_id = 1
    post_id = lambda: PostFactory.create().id  # Create related post
    date = Generators.datetime_now

# Use in tests
def test_full_blog():
    """Test creating full blog structure."""
    user = UserFactory.create()
    post = PostFactory.create(user_id=user.id, published=True)
    comments = CommentFactory.create_batch(5, post_id=post.id, user_id=user.id)
    
    assert post.user_id == user.id
    assert len(comments) == 5
    assert all(c.post_id == post.id for c in comments)
```

---

## 4. Comprehensive Documentation

**Location**: `documentation/emmett_active_record_guide.md`

**Contents**:
- Complete guide to Emmett's Active Record features
- Model organization best practices
- Field types and validation
- Form configuration
- REST API auto-generation
- CRUD UI auto-generation
- Anti-patterns to avoid
- Testing strategies

**When to Read**: Before creating new models or when unsure about Emmett features.

---

## 5. Missing Features Analysis

**Location**: `documentation/missing_features_analysis.md`

**Contents**:
- What Emmett already provides
- What's actually missing
- Priority assessment
- Implementation recommendations

**When to Read**: When considering new features or enhancements.

---

## Best Practices

### Model Organization

Follow this structure in your models:

```python
from emmett.orm import Model, Field, belongs_to, has_many
from emmett import now

class MyModel(Model):
    """Model docstring explaining purpose."""
    
    # 1. Relationships
    belongs_to('user')
    has_many('related_items')
    
    # 2. Fields
    name = Field()
    description = Field.text()
    created_at = Field.datetime()
    
    # 3. Configuration
    tablename = "my_models"  # Optional
    
    # 4. Defaults
    default_values = {
        'created_at': now
    }
    
    # 5. Validation
    validation = {
        'name': {'presence': True, 'len': {'gte': 3}}
    }
    
    # 6. Form config
    form_labels = {
        'name': 'Display Name'
    }
    
    # 7. Visibility
    fields_rw = {
        'created_at': False
    }
    
    # 8. Computed properties
    @property
    def formatted_name(self):
        return self.name.upper()
    
    # 9. Business logic
    def activate(self):
        """Activate this item."""
        self.active = True
        self.save()
```

### What Belongs in Models

✅ **DO**:
- Field definitions
- Validation rules
- Default values
- Computed properties
- Business logic methods
- Permission checks
- Simple queries

❌ **DON'T**:
- HTTP handling
- Template rendering
- External API calls
- Email sending
- Complex workflows
- Session management

---

## Common Patterns

### Pattern: Publishable Content

```python
class Post(Model):
    published = Field.bool(default=False)
    published_at = Field.datetime()
    
    def publish(self):
        """Publish this post."""
        self.published = True
        self.published_at = now()
        self.save()
    
    def unpublish(self):
        """Unpublish this post."""
        self.published = False
        self.published_at = None
        self.save()
    
    @property
    def is_published(self):
        """Check if published."""
        return self.published and self.published_at is not None
```

### Pattern: Soft Delete

```python
class Post(Model):
    deleted = Field.bool(default=False)
    deleted_at = Field.datetime()
    
    def soft_delete(self):
        """Soft delete this record."""
        self.deleted = True
        self.deleted_at = now()
        self.save()
    
    def restore(self):
        """Restore soft deleted record."""
        self.deleted = False
        self.deleted_at = None
        self.save()
    
    @classmethod
    def active(cls):
        """Get only non-deleted records."""
        return cls.where(lambda p: p.deleted == False)
```

### Pattern: Timestamps

```python
class Post(Model):
    created_at = Field.datetime()
    updated_at = Field.datetime()
    
    default_values = {
        'created_at': now,
        'updated_at': now
    }
    
    update_values = {
        'updated_at': now
    }
```

---

## Getting Help

1. **Read the docs**: `documentation/emmett_active_record_guide.md`
2. **Validate your code**: `python validate_models.py --all`
3. **Check examples**: Review `runtime/app.py` for working examples
4. **Emmett docs**: https://emmett.sh/docs

---

## Summary

### New Tools Available

1. ✅ **validate_models.py** - Check for anti-patterns
2. ✅ **model_permissions.py** - Row/field-level permissions
3. ✅ **model_factory.py** - Easy test data creation
4. ✅ **Comprehensive docs** - Learn Emmett's features
5. ✅ **Feature analysis** - Understand what's available

### Next Steps

1. Read `documentation/emmett_active_record_guide.md`
2. Run `python validate_models.py --all` on your models
3. Add permissions to sensitive models using `PermissionMixin`
4. Create factories for your models to improve testing
5. Follow best practices in new models

**Remember**: Emmett already provides Active Record. Use its features!

