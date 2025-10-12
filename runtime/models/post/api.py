# -*- coding: utf-8 -*-
"""
Post REST API configuration.
"""

from .model import Post


def setup_rest_api(app):
    """
    Setup REST API endpoints for Post model.
    
    Args:
        app: Emmett application instance
        
    Returns:
        REST module instance
    """
    # Create REST module for Posts
    posts_api = app.rest_module(
        __name__, 
        'posts_api', 
        Post, 
        url_prefix='api/posts'
    )
    
    @posts_api.before_create
    def set_post_user(attrs):
        """Automatically set user from session if authenticated"""
        from emmett import session
        
        if session.auth and session.auth.user:
            user = session.auth.user
            if 'user' not in attrs:
                attrs['user'] = user.id
    
    return posts_api

