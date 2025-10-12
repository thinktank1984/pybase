# User Role System - Proposal Summary

## Overview
Implement a comprehensive Role-Based Access Control (RBAC) system to replace the basic group-based authorization currently in the application.

## Quick Facts
- **Change ID**: `add-user-role-system`
- **Status**: Proposal complete, ready for review
- **Estimated Effort**: 24 hours (6-7 days part-time)
- **Breaking Changes**: Optional - can run in parallel with existing system during migration

## Problem Statement
Current application only supports binary authorization (admin vs regular user) with hard-coded checks scattered throughout the codebase. This limits flexibility and makes it difficult to implement granular permissions.

## Solution
Implement a full RBAC system with:
1. **Role and Permission models** following Active Record pattern
2. **Many-to-many relationships** between users-roles and roles-permissions
3. **Decorator-based protection** for routes and methods
4. **Auto-generated UIs** for managing roles, permissions, and assignments
5. **Permission caching** for performance
6. **Standard permission naming** convention

## Key Components

### Models
- **Role**: Represents a role (Admin, Moderator, Author, Viewer)
- **Permission**: Represents a specific permission (post.create, comment.delete)
- **UserRole**: Many-to-many association with audit fields
- **RolePermission**: Many-to-many association with audit fields

### Decorators
- `@requires_role('admin')` - Route/method requires specific role
- `@requires_any_role('admin', 'moderator')` - Requires any of specified roles
- `@requires_permission('post.delete')` - Requires specific permission

### Default Roles
| Role | Description | Example Permissions |
|------|-------------|-------------------|
| Admin | Full access | All permissions |
| Moderator | Content management | post.edit.any, comment.delete.any |
| Author | Own content management | post.create, post.edit.own, post.delete.own |
| Viewer | Read-only access | post.read, comment.read |

### Permission Naming Convention
- Standard: `{resource}.{action}` (e.g., `post.create`, `user.read`)
- Ownership-based: `{resource}.{action}.{own|any}` (e.g., `post.edit.own`, `post.delete.any`)

## User Interface
Auto-generated admin interfaces for:
- **Role Management**: List, create, edit, delete roles
- **Permission Management**: View all permissions grouped by resource
- **Role-Permission Assignment**: Matrix view and checkboxes
- **User-Role Assignment**: Assign/remove roles from users
- **Permission Matrix**: Visual roles × permissions grid

## API Integration
- REST API endpoints for roles and permissions (admin-only)
- Automatic permission enforcement on all model APIs
- OpenAPI documentation includes security requirements
- Ownership checks for update/delete operations

## Template Integration
New template helpers:
```html
{% if current_user.has_permission('post.create') %}
    <a href="/new">Create Post</a>
{% endif %}

{% if current_user.has_role('admin') %}
    <a href="/admin">Admin Panel</a>
{% endif %}
```

## Example Usage

### Protect a Route
```python
@app.route('/admin/users')
@requires_role('admin')
async def manage_users():
    users = User.all().select()
    return dict(users=users)
```

### Protect a Model Method
```python
class Post(Model, ActiveRecord):
    @requires_permission('post.publish')
    def publish(self):
        self.published = True
        return self.save()
```

### Check Permissions Programmatically
```python
user = get_current_user()

if user.has_role('admin'):
    # Admin logic
    pass

if user.has_permission('post.delete.any'):
    # Can delete any post
    pass

if user.can_access_resource('post', 'edit', post_instance):
    # Can edit this specific post (ownership check)
    pass
```

## Migration Strategy
1. **Phase 1**: Create models and seed default roles/permissions
2. **Phase 2**: Add decorators and user methods (parallel with old system)
3. **Phase 3**: Generate management UIs
4. **Phase 4**: Migrate existing code from `is_admin()` to role checks
5. **Phase 5**: Remove old group-based system (optional)

## Affected Areas
- ✨ **New**: Role, Permission, UserRole, RolePermission models
- ✨ **New**: Role/permission management UIs
- ✨ **New**: Decorators for route/method protection
- 🔧 **Modified**: User model (add role methods)
- 🔧 **Modified**: Post/Comment models (use permission decorators)
- 🔧 **Modified**: Templates (add permission checks)
- 🔧 **Modified**: OpenAPI generator (document security)

## Benefits
- ✅ **Granular control**: Fine-grained permissions per action
- ✅ **Flexible**: Easy to add new roles without code changes
- ✅ **Self-service**: Admins manage permissions through UI
- ✅ **Scalable**: Grows with application needs
- ✅ **Secure**: Explicit permissions, fail closed by default
- ✅ **Auditable**: Track permission grants and changes
- ✅ **Developer-friendly**: Declarative decorators

## Testing Strategy
- Unit tests for models and decorators
- Integration tests for authorization flows
- UI tests for management interfaces
- API tests for permission enforcement
- Performance tests for caching

## Documentation Deliverables
- Code documentation with docstrings
- Usage guide for developers
- Migration guide from existing system
- Admin user guide for role management

## Open Questions
1. Should we implement role hierarchy (inheritance)?
2. Should we support time-based permissions (temporary access)?
3. Should we implement approval workflows for sensitive role changes?
4. Should we keep backward compatibility with auth_groups indefinitely?

## Next Steps
1. ✅ Validate proposal with OpenSpec CLI
2. 📋 Present to stakeholders for approval
3. 🚀 Begin implementation after approval
4. 🧪 Test thoroughly during development
5. 📚 Update documentation
6. 🎯 Deploy with monitoring

## References
- Proposal: `openspec/changes/add-user-role-system/proposal.md`
- Tasks: `openspec/changes/add-user-role-system/tasks.md`
- Spec Deltas: `openspec/changes/add-user-role-system/specs/`

## Validation
```bash
# Validate proposal
openspec validate add-user-role-system --strict

# View proposal details
openspec show add-user-role-system

# View spec differences
openspec diff add-user-role-system
```

---

**Status**: ✅ Proposal validated and ready for review  
**Created**: 2025-10-12  
**Author**: AI Assistant  
**Reviewers**: [To be assigned]

