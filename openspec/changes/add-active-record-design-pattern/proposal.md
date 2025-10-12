# Emmett Model Best Practices & Enhancements

## Why

After review, **Emmett already implements the Active Record pattern comprehensively**. However, the application would benefit from:
- **Documentation**: Clear guide on using Emmett's Active Record features effectively
- **Pattern enforcement**: Tools to prevent anti-patterns in models
- **Testing utilities**: Helpers to make model testing easier
- **Permission enhancements**: Row-level and field-level permission helpers

The goal is to **enhance and document** existing Emmett capabilities, not replace them.

## Current State Analysis

### ✅ What Emmett Already Provides

Emmett's `Model` class already provides:
- **Active Record pattern**: `create()`, `save()`, `update_record()`, `delete_record()`
- **Comprehensive validation**: `validation` attribute with rich rules
- **Form configuration**: `form_labels`, `form_info`, `form_widgets`
- **Field visibility**: `fields_rw`, `rest_rw`
- **Computed fields**: Properties and `virtual_fields`
- **Relationships**: `belongs_to()`, `has_many()`, `has_one()`
- **REST API auto-generation**: Via `app.rest_module()` (emmett_rest)
- **Lifecycle callbacks**: Via pyDAL hooks

### ✅ What's Already Implemented

The application already has:
- **CRUD UI auto-generation**: `auto_ui_generator.py`
- **OpenAPI/Swagger**: `openapi_generator.py`
- **Database migrations**: Via Emmett migrations

### ❌ What's Actually Missing

1. **Comprehensive documentation** on using Emmett's features
2. **Pattern validation tool** to detect anti-patterns
3. **Row-level permissions** helper
4. **Model factory** for testing
5. **Best practices guide**

## What Changes

Instead of creating a new Active Record system, we're **enhancing** Emmett's existing implementation:

### 1. Documentation ✅ IMPLEMENTED
- Create comprehensive guide: `documentation/emmett_active_record_guide.md`
- Document Emmett's built-in Active Record features
- Provide examples of proper model structure
- Document anti-patterns to avoid
- Include testing patterns

### 2. Pattern Validation Tool ✅ IMPLEMENTED
- Create `runtime/validate_models.py` CLI tool
- Detect anti-patterns (HTTP handling, template rendering, etc.)
- Check for missing validation rules
- Check for missing docstrings
- Provide actionable suggestions
- Support JSON output for CI/CD

### 3. Row-Level Permissions ✅ IMPLEMENTED
- Create `runtime/model_permissions.py` mixin
- Support row-level permission checks
- Support field-level permission checks
- Integrate with existing auth system
- No changes to Emmett core

### 4. Testing Utilities ✅ IMPLEMENTED
- Create `runtime/model_factory.py`
- Easy test data creation
- Support for factories with sequences
- Optional Faker integration
- No external dependencies required

### 5. Missing Features Analysis ✅ DOCUMENTED
- Document what's available vs what's missing
- Prioritize actual needs
- Defer nice-to-have features

### Key Principles

1. **Models contain data and behavior**, not presentation or routing
2. **UI hints are metadata**, not UI logic
3. **Decorators extend behavior**, not replace it
4. **Methods are pure domain logic**, not infrastructure concerns
5. **Convention over configuration**: Standard structure enables automatic generation
6. **Single source of truth**: Model definition drives API, UI, and permissions

## Impact

### Affected Specs
- `orm` - Documentation added (no code changes - Emmett already provides Active Record)
- `auto-ui-generation` - No changes needed (already works with Emmett models)
- `testing` - Documentation added for testing utilities

### New Files Created
- ✅ `documentation/emmett_active_record_guide.md` - Comprehensive guide
- ✅ `documentation/missing_features_analysis.md` - Feature analysis
- ✅ `runtime/validate_models.py` - Pattern validation CLI tool
- ✅ `runtime/model_permissions.py` - Row/field-level permissions mixin
- ✅ `runtime/model_factory.py` - Model factory for testing

### Existing Files (No Changes Needed)
- `runtime/app.py` - No changes (Emmett Model already provides Active Record)
- `runtime/auto_ui_generator.py` - No changes (works with existing models)
- `runtime/openapi_generator.py` - No changes (works with existing models)
- Models (User, Post, Comment) - No changes required (already follow pattern)

### Compatibility
- **✅ 100% Non-breaking**: All additions are opt-in utilities
- **✅ No migration needed**: Existing models work as-is
- **✅ Backward compatible**: New features don't affect existing code

### Benefits
- **Better documentation**: Clear guide on using Emmett's features
- **Pattern enforcement**: Automated detection of anti-patterns
- **Easier testing**: Factory pattern for test data creation
- **Enhanced security**: Row-level and field-level permissions
- **Faster development**: Understanding what Emmett already provides
- **Team alignment**: Clear conventions documented
- **Quality assurance**: Validation tool catches issues early

### Example Structure - Using Emmett's Built-in Features

```python
from emmett.orm import Model, Field, belongs_to, has_many
from emmett import now
from model_permissions import PermissionMixin  # Optional: for row-level permissions

class Post(Model, PermissionMixin):  # PermissionMixin is optional
    """Blog post model using Emmett's Active Record pattern."""
    
    # Relationships
    belongs_to('user')
    has_many('comments')
    
    # Field definitions (Emmett's Active Record)
    title = Field()
    content = Field.text()
    published = Field.bool(default=False)
    created_at = Field.datetime()
    updated_at = Field.datetime()
    
    # Default values (Emmett feature)
    default_values = {
        'created_at': now,
        'updated_at': now,
        'published': False
    }
    
    # Validation rules (Emmett feature)
    validation = {
        'title': {'presence': True, 'len': {'gte': 3, 'lte': 200}},
        'content': {'presence': True, 'len': {'gte': 10}},
        'user': {'presence': True}
    }
    
    # Update triggers (Emmett feature)
    update_values = {
        'updated_at': now
    }
    
    # Form configuration (Emmett feature)
    form_labels = {
        'title': 'Post Title',
        'content': 'Post Content',
        'published': 'Publish Now'
    }
    
    form_info = {
        'title': 'Enter a descriptive title (3-200 characters)',
        'content': 'Write your post content. Markdown supported.'
    }
    
    # Field visibility (Emmett feature)
    fields_rw = {
        'user': False,
        'created_at': False,
        'updated_at': False
    }
    
    # Auto-UI configuration (custom feature)
    auto_ui_config = {
        'display_name': 'Blog Post',
        'display_name_plural': 'Blog Posts',
        'list_columns': ['id', 'title', 'published', 'created_at'],
        'search_fields': ['title', 'content'],
        'sort_default': '-created_at'
    }
    
    # Row-level permissions (new mixin)
    permissions = {
        'read': lambda record, user: record.published or record.user == user.id,
        'update': lambda record, user: record.user == user.id or user.is_admin(),
        'delete': lambda record, user: user.is_admin()
    }
    
    # Computed fields (Python properties)
    @property
    def excerpt(self):
        """Generate excerpt from content."""
        if not self.content:
            return ""
        return self.content[:100] + "..." if len(self.content) > 100 else self.content
    
    @property
    def word_count(self):
        """Calculate word count."""
        return len(self.content.split()) if self.content else 0
    
    # Business logic methods (Active Record pattern)
    def publish(self):
        """Publish the post."""
        self.published = True
        self.published_at = now()
        self.save()  # Emmett's Active Record save()
    
    def unpublish(self):
        """Unpublish the post."""
        self.published = False
        self.save()
    
    def get_comment_count(self):
        """Get number of comments."""
        return self.comments.count()


# Using the model (Emmett's Active Record methods)
post = Post.create(title="My Post", content="Content here", user=1)
post.publish()
post.save()

# Using REST API (already auto-generated by emmett_rest)
posts_api = app.rest_module(__name__, 'posts_api', Post, url_prefix='api/posts')

# Using Auto-UI (already implemented)
from auto_ui_generator import auto_ui
auto_ui(app, Post, '/admin/posts')
```

### What Gets Auto-Generated

From the `Post` model above, the system **automatically generates**:

#### 1. REST API Endpoints
```
GET    /api/posts          - List all posts
GET    /api/posts/:id      - Get single post
POST   /api/posts          - Create post (requires auth)
PUT    /api/posts/:id      - Update post (requires ownership or admin)
DELETE /api/posts/:id      - Delete post (requires ownership or admin)
```

#### 2. Swagger/OpenAPI Documentation
```yaml
/api/posts:
  get:
    summary: List posts
    responses:
      200:
        schema:
          type: array
          items:
            $ref: '#/definitions/Post'
  post:
    summary: Create post
    parameters:
      - name: title
        required: true
        minLength: 3
      - name: content
        required: true
```

#### 3. CRUD Pages
```
/posts              - List view with pagination
/posts/new          - Create form (admin only, from @requires_permission)
/posts/:id          - Detail view
/posts/:id/edit     - Edit form (owner or admin)
```

#### 4. Permission System
```python
# Automatically enforced:
- POST /api/posts: Requires authentication
- PUT /api/posts/:id: Requires ownership (user_id match) OR admin
- DELETE /api/posts/:id: Requires ownership OR admin
- GET /posts/new: Requires admin role
- Custom method delete_permanently(): Requires admin (from decorator)
```

### Configuration Options

```python
class Post(Model, ActiveRecord):
    # Control auto-generation
    class Meta:
        auto_generate_api = True      # Default: True
        auto_generate_pages = True     # Default: True
        auto_generate_swagger = True   # Default: True
        api_prefix = '/api/v1'        # Default: '/api'
        require_auth_for_write = True  # Default: True
        list_page_size = 20           # Default: 25
```

### Anti-Patterns to Prevent

```python
# BAD: Don't put HTTP handling in models
class Post(Model):
    def create_from_request(self, request):  # ❌ No HTTP concerns
        pass
    
    def render_html(self):  # ❌ No presentation logic
        return f"<div>{self.title}</div>"
    
    def send_to_api(self, api_client):  # ❌ No external service calls
        pass

# GOOD: Keep models focused on domain
class Post(Model):
    def publish(self):  # ✅ Domain logic
        self.published = True
        return self.save()
```

## Migration Plan

### Phase 1: Foundation (Week 1)
- Create `ActiveRecord` base class
- Document pattern and examples
- Add model validation utilities

### Phase 2: Pilot (Week 2)
- Refactor one model (Post) to follow pattern
- Update auto-UI generation to use new structure
- Gather feedback

### Phase 3: Migration (Week 3-4)
- Refactor remaining models (User, Comment)
- Update all references
- Add linting rules to enforce pattern

### Phase 4: Documentation (Week 4)
- Complete pattern guide
- Add migration examples
- Update onboarding documentation

