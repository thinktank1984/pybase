# -*- coding: utf-8 -*-
"""
REST API configuration for Permission model.
"""


def setup_rest_api(app):
    """
    Setup REST API for Permission model.
    Admin-only access, read-only for most operations.
    
    Args:
        app: Emmett application instance
        
    Returns:
        REST module instance
    """
    from .model import Permission
    
    permissions_api = app.rest_module(
        __name__,
        'permissions_api',
        Permission,
        url_prefix='api/permissions',
        # Read-only for non-admins
        # Permissions are typically managed through seeding, not CRUD
        disabled_methods=['delete']  # Prevent accidental deletion
    )
    
    return permissions_api

