# -*- coding: utf-8 -*-
"""
Comment model definition.
"""

from emmett import now
from emmett.orm import Model, Field, belongs_to


class Comment(Model):
    """
    Comment model.
    
    Represents comments on blog posts, with author, content, and timestamp.
    """
    belongs_to('user', 'post')

    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: _get_current_user_id(),
        'date': now
    }
    validation = {
        'text': {'presence': True},
        'user': {'allow': 'empty'},  # Allow empty for REST API (will be set by callback)
        'post': {'presence': True}
    }
    fields_rw = {
        'user': False,  # Hidden in forms
        'post': False,
        'date': False
    }
    rest_rw = {
        'id': (True, False),     # Visible in output, not writable in input
        'user': (False, True),  # Hidden in output, writable in input for REST API
        'post': (True, True),    # Visible and writable for REST API
        'date': (True, False)    # Visible in output, not writable in input
    }


def _get_current_user_id():
    """
    Helper function to get current user ID for default values.
    
    Returns:
        User ID or None
    """
    try:
        from emmett import current
        if hasattr(current, 'session') and hasattr(current.session, 'auth') and current.session.auth:
            return current.session.auth.user.id
    except:
        pass
    return None

