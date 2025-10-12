# -*- coding: utf-8 -*-
"""
Comment model with REST API.
"""

from emmett import now, session
from emmett.orm import Model, Field, belongs_to


class Comment(Model):
    """Comment model for blog posts."""
    
    belongs_to('user', 'post')

    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: _get_current_user_id(),
        'date': now
    }
    validation = {
        'text': {'presence': True},
        'user': {'allow': 'empty'},
        'post': {'presence': True}
    }
    fields_rw = {
        'user': False,
        'post': False,
        'date': False
    }
    rest_rw = {
        'id': (True, False),
        'user': (False, True),
        'post': (True, True),
        'date': (True, False)
    }
    
    # Permission configuration
    class Meta:
        permissions = {
            'create': 'comment.create',
            'read': None,  # Public
            'update.own': 'comment.edit.own',
            'update.any': 'comment.edit.any',
            'delete.own': 'comment.delete.own',
            'delete.any': 'comment.delete.any',
        }
        ownership_field = 'user'
    
    def can_edit(self, user=None):
        """
        Check if user can edit this comment using role-based permissions.
        
        Args:
            user: User instance (defaults to current user)
            
        Returns:
            bool: True if user can edit this comment
        """
        if user is None:
            from ..user import get_current_user
            user = get_current_user()
        
        if not user:
            return False
        
        # Check if user has permission to edit this comment
        return user.can_access_resource('comment', 'edit', self)
    
    def can_delete(self, user=None):
        """
        Check if user can delete this comment using role-based permissions.
        
        Args:
            user: User instance (defaults to current user)
            
        Returns:
            bool: True if user can delete this comment
        """
        if user is None:
            from ..user import get_current_user
            user = get_current_user()
        
        if not user:
            return False
        
        # Check if user has permission to delete this comment
        return user.can_access_resource('comment', 'delete', self)


def _get_current_user_id():
    """Get current user ID for default values."""
    try:
        from emmett import current
        if hasattr(current, 'session') and hasattr(current.session, 'auth') and current.session.auth:
            return current.session.auth.user.id
    except:
        pass
    return None


def setup(app):
    """Setup REST API for Comment model."""
    comments_api = app.rest_module(__name__, 'comments_api', Comment, url_prefix='api/comments')
    
    @comments_api.before_create
    def set_comment_user(attrs):
        """Automatically set user from session if authenticated."""
        if session.auth and session.auth.user:
            if 'user' not in attrs:
                attrs['user'] = session.auth.user.id
    
    return comments_api
