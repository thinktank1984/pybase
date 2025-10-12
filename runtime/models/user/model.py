# -*- coding: utf-8 -*-
"""
User model definition and authentication utilities.
"""

from emmett.orm import has_many
from emmett.tools.auth import AuthUser
from emmett import current, session


class User(AuthUser):
    """
    User model extending Emmett's AuthUser.
    
    This will create "auth_user" table and related groups/permissions tables.
    """
    # will create "auth_user" table and groups/permissions ones
    has_many('posts', 'comments')
    
    rest_rw = {
        'id': (True, False),  # Visible in output, not writable in input
        'email': (True, False),  # Visible in output, not writable
        'first_name': (True, False),
        'last_name': (True, False)
    }


def get_current_user():
    """
    Get currently authenticated user.
    
    Returns:
        User object or None if not authenticated
    """
    try:
        # Try to get from current context first (works in request context)
        if hasattr(current, 'session') and hasattr(current.session, 'auth') and current.session.auth:
            return current.session.auth.user
        # Fallback to session (works in non-request context)
        elif hasattr(session, 'auth') and session.auth:
            return session.auth.user
    except:
        pass
    return None


def is_authenticated():
    """
    Check if user is authenticated.
    
    Returns:
        True if user is authenticated, False otherwise
    """
    return get_current_user() is not None


def is_admin():
    """
    Check if current user has admin role.
    
    Returns:
        True if user is admin, False otherwise
    """
    from emmett import session, current
    
    if not session.auth:
        return False
    
    user = session.auth.user
    
    if not user:
        return False
    
    try:
        # Get database instance from current context
        db = current.app.ext.db
        
        # Query the database for admin group membership
        # Try both possible field names (depends on Emmett version)
        try:
            membership = db(
                (db.auth_memberships.user == user.id) &
                (db.auth_memberships.auth_group == db.auth_groups.id) &
                (db.auth_groups.role == 'admin')
            ).select().first()
        except AttributeError:
            # Fallback to auth_user if user field doesn't exist
            membership = db(
                (db.auth_memberships.auth_user == user.id) &
                (db.auth_memberships.auth_group == db.auth_groups.id) &
                (db.auth_groups.role == 'admin')
            ).select().first()
        
        return membership is not None
    except Exception as e:
        print(f"is_admin error: {e}")
        return False

