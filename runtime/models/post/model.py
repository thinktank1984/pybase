# -*- coding: utf-8 -*-
"""
Post model definition.
"""

from emmett import now, session
from emmett.orm import Model, Field, belongs_to, has_many


class Post(Model):
    """
    Blog post model.
    
    Represents individual blog posts with title, content, author, and timestamp.
    """
    belongs_to('user')
    has_many('comments')

    title = Field()
    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: _get_current_user_id(),
        'date': now
    }
    validation = {
        'title': {'presence': True},
        'text': {'presence': True},
        'user': {'allow': 'empty'}  # Allow empty for REST API (will be set by callback)
    }
    fields_rw = {
        'user': False,  # Hidden in forms
        'date': False
    }
    rest_rw = {
        'id': (True, False),     # Visible in output, not writable in input
        'user': (False, True),  # Hidden in output, writable in input for REST API
        'date': (True, False)    # Visible in output, not writable in input
    }
    
    # Auto UI configuration
    auto_ui_config = {
        'display_name': 'Blog Post',
        'display_name_plural': 'Blog Posts',
        'list_columns': ['id', 'title', 'user', 'date'],
        'search_fields': ['title', 'text'],
        'sort_default': '-date',
        'permissions': {
            'list': lambda: True,  # Anyone can view list
            'create': lambda: session.auth is not None,  # Must be logged in to create
            'read': lambda: True,  # Anyone can view details
            'update': lambda: session.auth is not None,  # Must be logged in to update
            'delete': lambda: session.auth is not None,  # Must be logged in to delete
        },
        'field_config': {
            'title': {
                'display_name': 'Post Title',
                'help_text': 'Enter a descriptive title for your blog post'
            },
            'text': {
                'display_name': 'Content',
                'help_text': 'Write your blog post content here'
            },
            'user': {
                'display_name': 'Author',
                'readonly': True
            },
            'date': {
                'display_name': 'Published Date',
                'readonly': True
            }
        }
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

