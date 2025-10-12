# -*- coding: utf-8 -*-
"""
Authorization decorators for role-based and permission-based access control.
"""

from functools import wraps
from emmett import session, abort, redirect, url
from .user import get_current_user, is_authenticated


def requires_role(*role_names):
    """
    Decorator to require specific role(s) for route or method access.
    
    Usage:
        @requires_role('admin')
        async def admin_only_route():
            pass
        
        @requires_role('admin', 'moderator')
        async def moderator_route():
            pass
    
    Args:
        *role_names: One or more role names required
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            # Check authentication
            if not is_authenticated():
                abort(401, "Authentication required")
            
            user = get_current_user()
            if not user:
                abort(401, "Authentication required")
            
            # Check if user has any of the required roles
            if not user.has_any_role(*role_names):
                role_list = ', '.join(role_names)
                abort(403, f"Access denied. Required role(s): {role_list}")
            
            return await f(*args, **kwargs)
        
        return wrapped
    return decorator


def requires_any_role(*role_names):
    """
    Decorator to require at least one of the specified roles.
    This is an alias for requires_role for clarity.
    
    Usage:
        @requires_any_role('admin', 'moderator', 'author')
        async def content_management():
            pass
    
    Args:
        *role_names: One or more role names (user needs at least one)
        
    Returns:
        Decorated function
    """
    return requires_role(*role_names)


def requires_all_roles(*role_names):
    """
    Decorator to require all of the specified roles.
    
    Usage:
        @requires_all_roles('admin', 'moderator')
        async def special_route():
            pass
    
    Args:
        *role_names: Role names (user must have all)
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            # Check authentication
            if not is_authenticated():
                abort(401, "Authentication required")
            
            user = get_current_user()
            if not user:
                abort(401, "Authentication required")
            
            # Check if user has all required roles
            if not user.has_all_roles(*role_names):
                role_list = ', '.join(role_names)
                abort(403, f"Access denied. Required roles: {role_list}")
            
            return await f(*args, **kwargs)
        
        return wrapped
    return decorator


def requires_permission(permission_name, instance_param=None):
    """
    Decorator to require a specific permission for method or route access.
    Supports ownership-based permissions.
    
    Usage:
        @requires_permission('post.delete')
        async def delete_post(post_id):
            pass
        
        # With ownership check
        @requires_permission('post.edit.own', instance_param='post')
        async def edit_post(post):
            # post parameter will be checked for ownership
            pass
    
    Args:
        permission_name (str): Permission name (e.g., 'post.create', 'post.edit.own')
        instance_param (str): Optional parameter name for ownership checking
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            # Check authentication
            if not is_authenticated():
                abort(401, "Authentication required")
            
            user = get_current_user()
            if not user:
                abort(401, "Authentication required")
            
            # Admin bypass
            if user.has_role('admin'):
                return await f(*args, **kwargs)
            
            # Parse permission name for ownership check
            parts = permission_name.split('.')
            if len(parts) >= 3 and parts[2] in ('own', 'any'):
                # Ownership-based permission
                resource = parts[0]
                action = parts[1]
                scope = parts[2]
                
                # Get instance for ownership check if specified
                instance = None
                if instance_param and instance_param in kwargs:
                    instance = kwargs[instance_param]
                elif instance_param and len(args) > 0:
                    # Try to get from positional args (not ideal, but fallback)
                    instance = args[0]
                
                # Check resource access
                if not user.can_access_resource(resource, action, instance, scope):
                    abort(403, f"Access denied. Required permission: {permission_name}")
            else:
                # Simple permission check
                if not user.has_permission(permission_name):
                    abort(403, f"Access denied. Required permission: {permission_name}")
            
            return await f(*args, **kwargs)
        
        return wrapped
    return decorator


def requires_any_permission(*permission_names):
    """
    Decorator to require at least one of the specified permissions.
    
    Usage:
        @requires_any_permission('post.create', 'post.edit')
        async def post_action():
            pass
    
    Args:
        *permission_names: Permission names (user needs at least one)
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            # Check authentication
            if not is_authenticated():
                abort(401, "Authentication required")
            
            user = get_current_user()
            if not user:
                abort(401, "Authentication required")
            
            # Admin bypass
            if user.has_role('admin'):
                return await f(*args, **kwargs)
            
            # Check if user has any of the required permissions
            if not user.has_any_permission(*permission_names):
                perm_list = ', '.join(permission_names)
                abort(403, f"Access denied. Required permission(s): {perm_list}")
            
            return await f(*args, **kwargs)
        
        return wrapped
    return decorator


def check_permission(permission_name, user=None, instance=None):
    """
    Helper function to check permissions programmatically (not a decorator).
    
    Usage:
        if check_permission('post.delete', user, post):
            # Allow deletion
        else:
            # Deny deletion
    
    Args:
        permission_name (str): Permission name
        user: User instance (defaults to current user)
        instance: Optional resource instance for ownership check
        
    Returns:
        bool: True if user has the permission
    """
    if user is None:
        user = get_current_user()
    
    if not user:
        return False
    
    # Admin bypass
    if user.has_role('admin'):
        return True
    
    # Parse permission for ownership check
    parts = permission_name.split('.')
    if len(parts) >= 3 and parts[2] in ('own', 'any'):
        resource = parts[0]
        action = parts[1]
        scope = parts[2]
        return user.can_access_resource(resource, action, instance, scope)
    else:
        return user.has_permission(permission_name)


def check_role(role_name, user=None):
    """
    Helper function to check roles programmatically (not a decorator).
    
    Usage:
        if check_role('admin', user):
            # Show admin content
    
    Args:
        role_name (str): Role name
        user: User instance (defaults to current user)
        
    Returns:
        bool: True if user has the role
    """
    if user is None:
        user = get_current_user()
    
    if not user:
        return False
    
    return user.has_role(role_name)

