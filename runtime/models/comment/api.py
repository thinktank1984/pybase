# -*- coding: utf-8 -*-
"""
Comment REST API configuration.
"""

from .model import Comment


def setup_rest_api(app):
    """
    Setup REST API endpoints for Comment model.
    
    Args:
        app: Emmett application instance
        
    Returns:
        REST module instance
    """
    # Create REST module for Comments
    comments_api = app.rest_module(
        __name__, 
        'comments_api', 
        Comment, 
        url_prefix='api/comments'
    )
    
    @comments_api.before_create
    def set_comment_user(attrs):
        """Automatically set user from session if authenticated"""
        from emmett import session
        
        if session.auth and session.auth.user:
            user = session.auth.user
            if 'user' not in attrs:
                attrs['user'] = user.id
    
    return comments_api

