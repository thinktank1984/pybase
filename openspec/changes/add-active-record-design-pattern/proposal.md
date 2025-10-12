# Active Record Design Pattern

## Why

Currently, model definitions in the application are scattered with business logic, UI concerns, and data access patterns mixed together. This makes models:
- **Hard to maintain**: Logic spread across multiple files and concerns
- **Difficult to test**: Coupled dependencies make unit testing complex
- **Inconsistent**: No standard pattern for model behavior and structure
- **UI-coupled**: UI element mappings and presentation logic mixed with data models

Implementing a clean Active Record design pattern will:
- **Separate concerns**: Models focus on data and domain logic only
- **Standardize structure**: Clear conventions for attributes, methods, and decorators
- **Improve testability**: Clean separation enables easier unit testing
- **Enable auto-generation**: Standardized structure allows automatic UI generation
- **Enhance maintainability**: Predictable model structure reduces cognitive load

The Active Record pattern provides a clear contract for what belongs in a model versus what belongs in controllers, services, or UI layers.

## What Changes

- Define strict Active Record model structure with clear boundaries
- Establish model components that are allowed:
  - **Attributes**: Model field definitions (database columns)
  - **Attribute decorators**: Validation, formatting, computed fields
  - **UI element mapping decorators**: Default UI widget overrides for auto-generation
  - **Methods**: Domain logic and business rules
  - **Method decorators**: Authorization, caching, lifecycle hooks
- Create base model class that enforces Active Record pattern
- Add automatic model introspection for UI generation
- Add validation to prevent mixing of concerns (no direct HTTP handling, no template rendering)
- Document pattern with examples and anti-patterns
- Provide migration guide for existing models

### Key Principles

1. **Models contain data and behavior**, not presentation or routing
2. **UI hints are metadata**, not UI logic
3. **Decorators extend behavior**, not replace it
4. **Methods are pure domain logic**, not infrastructure concerns

## Impact

### Affected Specs
- `orm` - MODIFIED to include Active Record design pattern requirements
- `auto-ui-generation` - MODIFIED to reference Active Record structure for introspection

### Affected Code
- `runtime/app.py` - Add base `ActiveRecord` model class
- `runtime/models.py` (new) - Create separate models file following pattern
- `runtime/auto_ui_generator.py` - Update to use Active Record introspection
- Existing model definitions (User, Post, Comment) - Refactor to follow pattern
- Documentation - Add Active Record pattern guide

### Compatibility
- **Breaking change** if strict enforcement: Existing models may need refactoring
- **Non-breaking** if optional: Can introduce gradually with base class
- **Recommendation**: Introduce as optional base class, migrate models incrementally

### Benefits
- **Clearer architecture**: Separation of concerns enforced by design
- **Better auto-generation**: Standardized structure enables reliable UI generation
- **Improved testing**: Pure domain models are easier to unit test
- **Team alignment**: Clear conventions reduce debates about where code belongs
- **Faster onboarding**: New developers understand model structure immediately

### Example Structure

```python
from emmett.orm import Model, Field
from app import db

class Post(Model, ActiveRecord):
    # Attributes (database fields)
    tablename = "posts"
    
    title = Field.string()
    content = Field.text()
    published = Field.bool(default=False)
    created_at = Field.datetime()
    
    # Attribute decorators
    @validates('title')
    def validate_title(self, value):
        if len(value) < 3:
            return "Title must be at least 3 characters"
    
    @computed_field
    def excerpt(self):
        return self.content[:100] + "..." if len(self.content) > 100 else self.content
    
    # UI element mapping (metadata for auto-generation)
    @ui_override(field='content', widget='rich_text_editor')
    def content_widget(self):
        return {'toolbar': ['bold', 'italic', 'link']}
    
    # Methods (domain logic)
    def publish(self):
        """Publish the post and update timestamp."""
        self.published = True
        self.published_at = datetime.now()
        return self.save()
    
    def can_edit(self, user):
        """Check if user can edit this post."""
        return user.is_admin() or self.user_id == user.id
    
    # Method decorators
    @requires_permission('admin')
    def delete_permanently(self):
        """Permanently delete post (admin only)."""
        return self.destroy()
    
    @cached(ttl=300)
    def get_comment_count(self):
        """Get cached comment count."""
        return self.comments.count()
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

