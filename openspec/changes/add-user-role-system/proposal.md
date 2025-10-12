# User Role System

## Why

Currently, the application has a basic group-based authorization system with only an "admin" check. This approach is limiting:
- **No granular permissions**: Users are either admin or regular users with no intermediate roles
- **Hard-coded checks**: Authorization logic is scattered with hard-coded `is_admin()` calls
- **Limited flexibility**: Cannot easily add new roles (moderator, editor, viewer) without code changes
- **No role management UI**: Admins must manually edit database to assign roles
- **Inconsistent permissions**: Each model implements its own `can_edit()`/`can_delete()` methods with duplicated logic

Implementing a proper Role-Based Access Control (RBAC) system will:
- **Enable granular permissions**: Define specific permissions (create_post, delete_comment, manage_users)
- **Centralize authorization**: Single source of truth for permission checks
- **Support multiple roles**: Admin, Moderator, Editor, Author, Viewer with different permission sets
- **Provide management UI**: Auto-generated interfaces for role and permission management
- **Integrate with Active Record**: Permission decorators work seamlessly with models
- **Scale easily**: Add new roles/permissions through configuration, not code changes

## What Changes

- Create `Role` and `Permission` models following Active Record pattern
- Define standard permissions for CRUD operations on each model
- Add role management UI (list, create, edit, delete roles and their permissions)
- Implement permission checking system integrated with Active Record decorators
- Add `@requires_role()` and `@requires_any_role()` decorators for route protection
- Extend User model with role management methods
- Update existing `can_edit()`/`can_delete()` methods to use role-based permissions
- Create role seeding system for initial roles (Admin, Moderator, Author, Viewer)
- Add user-role assignment UI in admin interface
- Update OpenAPI generator to document permission requirements

### Key Features

1. **Predefined Roles**:
   - **Admin**: Full access to everything
   - **Moderator**: Can edit/delete any content, cannot manage users
   - **Author**: Can create/edit/delete own content
   - **Viewer**: Read-only access

2. **Permission Naming Convention**:
   - Format: `{model}.{action}` (e.g., `post.create`, `comment.delete`, `user.manage`)
   - Special: `{model}.{action}.own` for ownership-based permissions (e.g., `post.edit.own`)

3. **Decorator Integration**:
   ```python
   @requires_permission('post.delete')
   def delete_post(self):
       return self.destroy()
   
   @requires_role('admin', 'moderator')
   def moderate_content(self):
       pass
   ```

4. **Route Protection**:
   ```python
   @app.route('/admin/users')
   @requires_role('admin')
   async def manage_users():
       pass
   ```

## Impact

### Affected Specs
- `auth` - **NEW SPEC** for authentication and authorization patterns
- `permissions` - **MODIFIED** to add role-based permission system details
- `auto-ui-generation` - **MODIFIED** to include Role and Permission model UIs
- `orm` - **MODIFIED** to document permission decorators integration

### Affected Code
- `runtime/app.py`:
  - Add `Role` and `Permission` models
  - Add role management methods to User model
  - Create `@requires_role()` and `@requires_any_role()` decorators
  - Update `requires_permission()` decorator to check user roles
  - Add role seeding in `setup_admin()` function
- `runtime/models/` (new directory structure):
  - Move models to separate files for better organization
  - `user.py` - User model with role methods
  - `role.py` - Role model
  - `permission.py` - Permission model
  - `post.py` - Post model with permission decorators
  - `comment.py` - Comment model with permission decorators
- `runtime/auto_ui_generator.py`:
  - Add Role and Permission management UIs
  - Add user-role assignment interface
- `runtime/openapi_generator.py`:
  - Document permission requirements in API endpoints
- `runtime/templates/`:
  - Add role management templates
  - Add user-role assignment templates
- Tests:
  - Unit tests for role/permission system
  - Integration tests for authorization

### Compatibility
- **Breaking change** if strict enforcement enabled: Existing code using `is_admin()` needs migration
- **Non-breaking** if implemented as additive: Can run in parallel with existing group system
- **Recommendation**: Implement as migration - support both systems during transition, then remove old group-based checks

### Benefits
- **Granular control**: Fine-grained permissions per action and resource
- **Flexible roles**: Easy to create new roles for different use cases
- **Self-service**: Admins can manage roles/permissions through UI without code changes
- **Audit trail**: Track who has which permissions and when they were granted
- **Secure by default**: Explicit permission requirements, fail closed
- **Better UX**: Users see only actions they're permitted to perform
- **Developer friendly**: Decorators make permission checks declarative and testable
- **Scalable**: System grows with application needs without architectural changes

### Example Usage

#### Define Model with Permissions
```python
class Post(Model, ActiveRecord):
    title = Field.string()
    content = Field.text()
    
    @requires_permission('post.publish')
    def publish(self):
        self.published = True
        return self.save()
    
    @requires_permission('post.delete')
    def delete_permanently(self):
        return self.destroy()
    
    class Meta:
        permissions = {
            'create': 'post.create',
            'read': None,  # Public
            'update.own': 'post.edit.own',
            'update.any': 'post.edit.any',
            'delete.own': 'post.delete.own',
            'delete.any': 'post.delete.any',
        }
```

#### Protect Routes
```python
@app.route('/admin/posts')
@requires_role('admin', 'moderator')
async def admin_posts():
    posts = Post.all().select()
    return dict(posts=posts)

@app.route('/moderate/<int:pid>')
@requires_permission('post.edit.any')
async def moderate_post(pid):
    post = get_or_404(Post, pid)
    # ... moderation logic
```

#### Check Permissions in Templates
```html
{% if current_user.has_permission('post.create') %}
    <a href="/new">Create Post</a>
{% endif %}

{% if current_user.has_role('admin') %}
    <a href="/admin">Admin Panel</a>
{% endif %}
```

#### Programmatic Role Assignment
```python
# In app setup
admin_role = Role.get_by_name('admin')
moderator_role = Role.get_by_name('moderator')

user.add_role(admin_role)
user.remove_role(moderator_role)

if user.has_role('admin'):
    # Admin-only logic
    pass

if user.has_permission('post.delete.any'):
    # Can delete any post
    pass
```

## Migration Plan

### Phase 1: Foundation (Week 1)
- Create Role and Permission models
- Implement permission checking system
- Add decorators for permission/role requirements
- Create role seeding with default roles
- Write unit tests for core functionality

### Phase 2: Integration (Week 1-2)
- Update User model with role methods
- Migrate existing `is_admin()` checks to use new system
- Update Post and Comment models to use permission decorators
- Add backward compatibility layer for old group system

### Phase 3: UI Generation (Week 2)
- Auto-generate Role management UI (list, create, edit, delete)
- Auto-generate Permission management UI
- Add user-role assignment interface
- Add role/permission display in user profile

### Phase 4: Documentation & Testing (Week 2-3)
- Write integration tests
- Document permission system usage
- Create migration guide for developers
- Add permission requirements to OpenAPI docs

### Phase 5: Cleanup (Week 3)
- Remove backward compatibility layer (if approved)
- Remove old group-based authorization code
- Final testing and validation

## Risks & Mitigation

### Risk: Breaking existing authorization
- **Mitigation**: Run both systems in parallel during transition, comprehensive test coverage

### Risk: Performance impact of permission checks
- **Mitigation**: Cache user permissions in session, implement permission query optimization

### Risk: Over-complication of simple use cases
- **Mitigation**: Provide sensible defaults, keep simple cases simple (public/authenticated/admin)

### Risk: Database migration complexity
- **Mitigation**: Keep existing auth_groups/auth_memberships tables, add new role tables alongside

