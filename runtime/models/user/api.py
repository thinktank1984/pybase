# -*- coding: utf-8 -*-
"""
User REST API configuration.
"""

from .model import User


def setup_rest_api(app):
    """
    Setup REST API endpoints for User model.
    
    Args:
        app: Emmett application instance
        
    Returns:
        REST module instance
        
    Note:
        User API is read-only. User creation/update/deletion
        is handled through Emmett's auth system.
    """
    # Create REST module for Users (read-only)
    users_api = app.rest_module(
        __name__, 
        'users_api', 
        User, 
        url_prefix='api/users',
        disabled_methods=['create', 'update', 'delete']
    )
    
    return users_api

