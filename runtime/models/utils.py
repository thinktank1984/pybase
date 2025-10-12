# -*- coding: utf-8 -*-
"""
Shared utility functions for models.
"""

from emmett import abort, current, session


def get_db():
    """
    Get database instance from current context or app module.
    
    Works in both application runtime and test contexts.
    
    Returns:
        Database instance
    """
    try:
        # Try current context first (works in app runtime)
        return current.app.ext.db
    except (AttributeError, RuntimeError):
        # Fallback to importing from app module (works in tests)
        try:
            from app import db
            return db
        except ImportError:
            raise RuntimeError("Cannot access database. Make sure app.db is initialized.")


def get_or_404(model, record_id):
    """
    Get model instance by ID or abort with 404.
    
    Args:
        model: Emmett Model class
        record_id: Primary key value
        
    Returns:
        Model instance
        
    Raises:
        404 if not found
    """
    # Get database instance from current context
    db = get_db()
    
    with db.connection():
        record = model.get(record_id)
        if not record:
            abort(404, f"{model.__name__} with id {record_id} not found")
        return record


# =============================================================================
# User Role Helper Functions
# =============================================================================


def user_get_roles(user_id):
    """
    Get all roles assigned to a user.
    
    Args:
        user_id (int): User ID
        
    Returns:
        list: List of Role instances
    """
    try:
        from .user_role import UserRole
        return UserRole.get_user_roles(user_id)
    except Exception as e:
        print(f"Error getting roles for user {user_id}: {e}")
        return []


def user_has_role(user_id, role_name):
    """
    Check if user has a specific role.
    
    Args:
        user_id (int): User ID
        role_name (str): Role name (e.g., 'admin', 'moderator')
        
    Returns:
        bool: True if user has the role
    """
    try:
        roles = user_get_roles(user_id)
        return any(role.name.lower() == role_name.lower() for role in roles)
    except:
        return False


def user_has_any_role(user_id, *role_names):
    """
    Check if user has any of the specified roles.
    
    Args:
        user_id (int): User ID
        *role_names: Variable number of role names
        
    Returns:
        bool: True if user has at least one of the roles
    """
    try:
        user_roles = {role.name.lower() for role in user_get_roles(user_id)}
        return any(role_name.lower() in user_roles for role_name in role_names)
    except:
        return False


def user_has_all_roles(user_id, *role_names):
    """
    Check if user has all of the specified roles.
    
    Args:
        user_id (int): User ID
        *role_names: Variable number of role names
        
    Returns:
        bool: True if user has all of the roles
    """
    try:
        user_roles = {role.name.lower() for role in user_get_roles(user_id)}
        return all(role_name.lower() in user_roles for role_name in role_names)
    except:
        return False


def user_get_permissions(user_id, use_cache=True):
    """
    Get all permissions granted to a user through their roles.
    
    Args:
        user_id (int): User ID
        use_cache (bool): Whether to use session cache
        
    Returns:
        set: Set of permission names
    """
    # Check cache first
    if use_cache and hasattr(session, 'user_permissions') and session.user_permissions:
        if session.get('user_permissions_id') == user_id:
            return session.user_permissions
    
    try:
        permissions = set()
        roles = user_get_roles(user_id)
        
        for role in roles:
            role_permissions = role.get_permissions()
            for perm in role_permissions:
                permissions.add(perm.name)
        
        # Cache in session
        if use_cache:
            session.user_permissions = permissions
            session.user_permissions_id = user_id
        
        return permissions
    except Exception as e:
        print(f"Error getting permissions for user {user_id}: {e}")
        return set()


def user_has_permission(user_id, permission_name):
    """
    Check if user has a specific permission.
    
    Args:
        user_id (int): User ID
        permission_name (str): Permission name (e.g., 'post.create')
        
    Returns:
        bool: True if user has the permission
    """
    # Admin role has all permissions
    if user_has_role(user_id, 'admin'):
        return True
    
    try:
        permissions = user_get_permissions(user_id)
        return permission_name in permissions
    except:
        return False


def user_has_any_permission(user_id, *permission_names):
    """
    Check if user has any of the specified permissions.
    
    Args:
        user_id (int): User ID
        *permission_names: Variable number of permission names
        
    Returns:
        bool: True if user has at least one permission
    """
    # Admin role has all permissions
    if user_has_role(user_id, 'admin'):
        return True
    
    try:
        permissions = user_get_permissions(user_id)
        return any(perm in permissions for perm in permission_names)
    except:
        return False


def user_can_access_resource(user_id, resource, action, instance=None, scope='any'):
    """
    Check if user can access a resource with a specific action.
    Supports ownership-based permissions.
    
    Args:
        user_id (int): User ID
        resource (str): Resource name (e.g., 'post')
        action (str): Action name (e.g., 'edit', 'delete')
        instance: Optional resource instance to check ownership
        scope (str): 'own', 'any', or 'both'
        
    Returns:
        bool: True if user can access the resource
    """
    # Admin role has all permissions
    if user_has_role(user_id, 'admin'):
        return True
    
    try:
        permissions = user_get_permissions(user_id)
        
        # Check for 'any' scope permission
        any_perm = f"{resource}.{action}.any"
        if any_perm in permissions:
            return True
        
        # Check for 'own' scope permission with ownership
        own_perm = f"{resource}.{action}.own"
        if own_perm in permissions:
            if instance is None:
                # No instance provided, grant access
                return True
            
            # Check ownership
            owner_field = getattr(instance, 'user', None) or getattr(instance, 'owner', None)
            if owner_field:
                owner_id = owner_field.id if hasattr(owner_field, 'id') else owner_field
                return owner_id == user_id
        
        # Check for permission without scope
        base_perm = f"{resource}.{action}"
        return base_perm in permissions
        
    except Exception as e:
        print(f"Error checking resource access: {e}")
        return False


def user_add_role(user_id, role):
    """
    Add a role to a user.
    
    Args:
        user_id (int): User ID
        role: Role instance or role ID
        
    Returns:
        bool: True if added successfully
    """
    try:
        from .user_role import UserRole
        role_id = role.id if hasattr(role, 'id') else role
        
        result = UserRole.assign_role(user_id, role_id)
        
        # Invalidate permission cache
        user_refresh_permissions(user_id)
        
        return result is not None
    except Exception as e:
        print(f"Error adding role to user: {e}")
        return False


def user_remove_role(user_id, role):
    """
    Remove a role from a user.
    
    Args:
        user_id (int): User ID
        role: Role instance or role ID
        
    Returns:
        bool: True if removed successfully
    """
    try:
        from .user_role import UserRole
        role_id = role.id if hasattr(role, 'id') else role
        
        result = UserRole.remove_role(user_id, role_id)
        
        # Invalidate permission cache
        user_refresh_permissions(user_id)
        
        return result
    except Exception as e:
        print(f"Error removing role from user: {e}")
        return False


def user_refresh_permissions(user_id):
    """
    Refresh the cached permissions for a user.
    
    Args:
        user_id (int): User ID
    """
    try:
        if hasattr(session, 'user_permissions'):
            del session.user_permissions
        if hasattr(session, 'user_permissions_id'):
            del session.user_permissions_id
        
        # Reload permissions
        user_get_permissions(user_id, use_cache=True)
    except:
        pass

