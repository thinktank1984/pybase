# -*- coding: utf-8 -*-
"""
Models package for Bloggy application.

Each model is self-contained with model definition, routes, and REST API
all in a single model.py file.
"""

from .user import User, is_admin, get_current_user, is_authenticated
from .post import Post
from .comment import Comment
from .role import Role
from .permission import Permission
from .user_role import UserRole
from .role_permission import RolePermission
from .utils import (
    get_or_404,
    user_get_roles, user_has_role, user_has_any_role, user_has_all_roles,
    user_get_permissions, user_has_permission, user_has_any_permission,
    user_can_access_resource, user_add_role, user_remove_role,
    user_refresh_permissions
)
from .decorators import (
    requires_role, requires_any_role, requires_all_roles,
    requires_permission, requires_any_permission,
    check_permission, check_role
)
from .seeder import (
    seed_all, seed_permissions, seed_roles, 
    ensure_permissions_exist, ensure_roles_exist
)

# Try to import OAuth models if they exist
try:
    from .oauth_account import OAuthAccount
    from .oauth_token import OAuthToken
    _oauth_available = True
except ImportError:
    OAuthAccount = None
    OAuthToken = None
    _oauth_available = False

__all__ = [
    'User', 'Post', 'Comment', 'Role', 'Permission', 'UserRole', 'RolePermission',
    'is_admin', 'get_current_user', 'is_authenticated', 'get_or_404',
    'user_get_roles', 'user_has_role', 'user_has_any_role', 'user_has_all_roles',
    'user_get_permissions', 'user_has_permission', 'user_has_any_permission',
    'user_can_access_resource', 'user_add_role', 'user_remove_role',
    'user_refresh_permissions',
    'requires_role', 'requires_any_role', 'requires_all_roles',
    'requires_permission', 'requires_any_permission',
    'check_permission', 'check_role',
    'seed_all', 'seed_permissions', 'seed_roles', 
    'ensure_permissions_exist', 'ensure_roles_exist'
]

# Add OAuth models to __all__ if available
if _oauth_available:
    __all__.extend(['OAuthAccount', 'OAuthToken'])


def setup_all(app):
    """
    Setup routes and REST APIs for all models.
    
    Args:
        app: Emmett application instance
        
    Returns:
        dict: Dictionary of API modules by name
    """
    from .post import setup as post_setup
    from .comment import setup as comment_setup
    from .user import setup as user_setup
    
    # Setup each model (routes and APIs)
    apis = {
        'posts_api': post_setup(app),
        'comments_api': comment_setup(app),
        'users_api': user_setup(app)
    }
    
    return apis
