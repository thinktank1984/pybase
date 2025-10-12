# -*- coding: utf-8 -*-
"""
Model-Level Permissions System

Provides row-level and field-level permissions for Emmett models.

Usage:
    from model_permissions import PermissionMixin, requires_permission

    class Post(Model, PermissionMixin):
        user_id = Field.int()
        title = Field()
        published = Field.bool()
        
        # Define permission rules
        permissions = {
            'read': lambda record, user: record.published or record.user_id == user.id,
            'update': lambda record, user: record.user_id == user.id or user.is_admin(),
            'delete': lambda record, user: record.user_id == user.id or user.is_admin(),
        }
    
    # Check permissions
    post = Post.get(1)
    if post.can_read(current_user):
        # Show post
        pass
"""

from functools import wraps
from typing import Callable, Dict, Optional, Any
from emmett import abort


class PermissionMixin:
    """
    Mixin to add row-level permissions to Emmett models.
    
    Define permission rules in the model using the 'permissions' attribute:
    
    permissions = {
        'read': lambda record, user: ...,
        'update': lambda record, user: ...,
        'delete': lambda record, user: ...,
    }
    """
    
    permissions: Dict[str, Callable] = {}
    
    def can(self, operation: str, user: Any = None) -> bool:
        """
        Check if user has permission for operation on this record.
        
        Args:
            operation: Operation name ('read', 'update', 'delete', etc.)
            user: User object (uses current user if None)
            
        Returns:
            True if user has permission, False otherwise
        """
        if not hasattr(self.__class__, 'permissions'):
            return True  # No permissions defined = allow all
        
        permission_func = self.__class__.permissions.get(operation)
        if not permission_func:
            return True  # No rule for this operation = allow
        
        if user is None:
            # Try to get current user from session
            try:
                from emmett import current
                user = current.session.auth.user if hasattr(current.session, 'auth') else None
            except (AttributeError, RuntimeError):
                user = None
        
        if user is None:
            return False  # No user = deny
        
        try:
            return permission_func(self, user)
        except Exception as e:
            print(f"Permission check error: {e}")
            return False
    
    def can_read(self, user: Any = None) -> bool:
        """Check if user can read this record."""
        return self.can('read', user)
    
    def can_update(self, user: Any = None) -> bool:
        """Check if user can update this record."""
        return self.can('update', user)
    
    def can_delete(self, user: Any = None) -> bool:
        """Check if user can delete this record."""
        return self.can('delete', user)
    
    def require_permission(self, operation: str, user: Any = None):
        """
        Require permission for operation, abort if denied.
        
        Args:
            operation: Operation name
            user: User object
            
        Raises:
            401 if no user
            403 if permission denied
        """
        if user is None:
            try:
                from emmett import current
                user = current.session.auth.user if hasattr(current.session, 'auth') else None
            except (AttributeError, RuntimeError):
                user = None
        
        if user is None:
            abort(401, "Authentication required")
        
        if not self.can(operation, user):
            abort(403, f"Permission denied for {operation} on {self.__class__.__name__}")
    
    @classmethod
    def filter_by_permission(cls, records, operation: str, user: Any = None):
        """
        Filter a list of records by permission.
        
        Args:
            records: Iterable of record instances
            operation: Operation name
            user: User object
            
        Returns:
            List of records user has permission for
        """
        return [r for r in records if r.can(operation, user)]


def requires_permission(operation: str = 'read'):
    """
    Decorator to require permission for a model method.
    
    Usage:
        class Post(Model, PermissionMixin):
            @requires_permission('update')
            def publish(self):
                self.published = True
                self.save()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.require_permission(operation)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


class FieldPermissionMixin:
    """
    Mixin to add field-level permissions to Emmett models.
    
    Define field permission rules using the 'field_permissions' attribute:
    
    field_permissions = {
        'salary': {
            'read': lambda record, user: user.is_admin() or user.id == record.user_id,
            'write': lambda record, user: user.is_admin(),
        }
    }
    """
    
    field_permissions: Dict[str, Dict[str, Callable]] = {}
    
    def can_read_field(self, field_name: str, user: Any = None) -> bool:
        """Check if user can read a specific field."""
        if not hasattr(self.__class__, 'field_permissions'):
            return True
        
        field_perms = self.__class__.field_permissions.get(field_name, {})
        read_perm = field_perms.get('read')
        
        if not read_perm:
            return True
        
        if user is None:
            try:
                from emmett import current
                user = current.session.auth.user if hasattr(current.session, 'auth') else None
            except (AttributeError, RuntimeError):
                user = None
        
        if user is None:
            return False
        
        try:
            return read_perm(self, user)
        except Exception as e:
            print(f"Field permission check error: {e}")
            return False
    
    def can_write_field(self, field_name: str, user: Any = None) -> bool:
        """Check if user can write a specific field."""
        if not hasattr(self.__class__, 'field_permissions'):
            return True
        
        field_perms = self.__class__.field_permissions.get(field_name, {})
        write_perm = field_perms.get('write')
        
        if not write_perm:
            return True
        
        if user is None:
            try:
                from emmett import current
                user = current.session.auth.user if hasattr(current.session, 'auth') else None
            except (AttributeError, RuntimeError):
                user = None
        
        if user is None:
            return False
        
        try:
            return write_perm(self, user)
        except Exception as e:
            print(f"Field permission check error: {e}")
            return False
    
    def get_visible_fields(self, user: Any = None) -> Dict[str, Any]:
        """
        Get dict of fields user can read.
        
        Returns:
            Dictionary of field_name: field_value for visible fields
        """
        result = {}
        
        # Get all fields
        for key in dir(self):
            if key.startswith('_'):
                continue
            
            try:
                value = getattr(self, key)
                if callable(value):
                    continue
                
                if self.can_read_field(key, user):
                    result[key] = value
            except:
                continue
        
        return result


# Example usage in models:
"""
from model_permissions import PermissionMixin, FieldPermissionMixin, requires_permission

class Post(Model, PermissionMixin, FieldPermissionMixin):
    user_id = Field.int()
    title = Field()
    content = Field.text()
    published = Field.bool()
    salary = Field.float()  # Sensitive field
    
    # Row-level permissions
    permissions = {
        'read': lambda record, user: record.published or record.user_id == user.id or user.is_admin(),
        'update': lambda record, user: record.user_id == user.id or user.is_admin(),
        'delete': lambda record, user: user.is_admin(),
    }
    
    # Field-level permissions
    field_permissions = {
        'salary': {
            'read': lambda record, user: user.is_admin() or user.id == record.user_id,
            'write': lambda record, user: user.is_admin(),
        }
    }
    
    # Method with permission check
    @requires_permission('update')
    def publish(self):
        self.published = True
        self.save()
    
    @requires_permission('delete')
    def archive(self):
        self.archived = True
        self.save()

# In controllers:
@app.route('/posts/<int:id>')
async def show_post(id):
    post = Post.get(id)
    if not post:
        abort(404)
    
    # Check permission
    if not post.can_read(current_user):
        abort(403)
    
    # Get only fields user can see
    visible_data = post.get_visible_fields(current_user)
    
    return dict(post=post, data=visible_data)
"""

