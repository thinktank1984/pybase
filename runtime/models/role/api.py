# -*- coding: utf-8 -*-
"""
REST API configuration for Role model.
"""


def setup_rest_api(app):
    """
    Setup REST API for Role model.
    Admin-only access.
    
    Args:
        app: Emmett application instance
        
    Returns:
        REST module instance
    """
    from .model import Role
    
    roles_api = app.rest_module(
        __name__,
        'roles_api',
        Role,
        url_prefix='api/roles',
        # Only admin can manage roles
        # All CRUD operations enabled
    )
    
    return roles_api

