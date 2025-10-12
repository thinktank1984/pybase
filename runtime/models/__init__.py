# -*- coding: utf-8 -*-
"""
Models package for Bloggy application.

This package contains all database model definitions organized by model type.
Each model has its own subpackage containing:
- model.py: Model definition
- views.py: Route handlers specific to the model
- api.py: REST API configuration
- __init__.py: Package exports
"""

from .user import User, is_admin, get_current_user, is_authenticated
from .post import Post
from .comment import Comment

__all__ = ['User', 'Post', 'Comment', 'is_admin', 'get_current_user', 'is_authenticated']


def setup_all_routes(app):
    """
    Setup routes for all models.
    
    Args:
        app: Emmett application instance
    """
    from .post import views as post_views
    from .comment import views as comment_views
    from .user import views as user_views
    
    # Setup routes for each model
    post_views.setup_routes(app)
    comment_views.setup_routes(app)
    user_views.setup_routes(app)


def setup_all_apis(app):
    """
    Setup REST APIs for all models.
    
    Args:
        app: Emmett application instance
        
    Returns:
        dict: Dictionary of API modules by name
    """
    from .post import api as post_api
    from .comment import api as comment_api
    from .user import api as user_api
    
    # Setup REST APIs for each model
    apis = {
        'posts_api': post_api.setup_rest_api(app),
        'comments_api': comment_api.setup_rest_api(app),
        'users_api': user_api.setup_rest_api(app)
    }
    
    return apis
