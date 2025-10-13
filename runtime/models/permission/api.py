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
    
    @permissions_api.before_create
    def generate_permission_name(attrs):
        """Generate permission name from resource, action, and scope before creation."""
        if 'resource' in attrs and 'action' in attrs:
            scope = attrs.get('scope', '')
            if scope:
                attrs['name'] = f"{attrs['resource']}.{attrs['action']}.{scope}"
            else:
                attrs['name'] = f"{attrs['resource']}.{attrs['action']}"
    
    return permissions_api

