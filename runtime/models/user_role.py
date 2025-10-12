# -*- coding: utf-8 -*-
"""
UserRole association model for many-to-many relationship between users and roles.
"""

from emmett.orm import Model, Field, belongs_to
from emmett import now


class UserRole(Model):
    """
    Association model linking users to roles.
    
    Tracks when a role was assigned and who assigned it for audit purposes.
    """
    
    tablename = 'user_roles'
    
    # Foreign key relationships
    belongs_to('user', 'role')
    
    # Audit fields
    assigned_at = Field.datetime(default=lambda: now())
    assigned_by = Field.int()  # ID of user who made the assignment
    
    # Validation - ensure unique user-role combinations
    validation = {
        'user': {'presence': True},
        'role': {'presence': True}
    }
    
    @classmethod
    def assign_role(cls, user_id, role_id, assigned_by_id=None):
        """
        Assign a role to a user.
        
        Args:
            user_id (int): User ID
            role_id (int): Role ID
            assigned_by_id (int): Optional ID of user making the assignment
            
        Returns:
            UserRole: Created association or existing one
        """
        try:
            from .utils import get_db
            db = get_db()
            
            # Check if already exists
            existing = db(
                (db.user_roles.user == user_id) &
                (db.user_roles.role == role_id)
            ).select().first()
            
            if existing:
                return existing
            
            # Create new association
            association_id = db.user_roles.insert(
                user=user_id,
                role=role_id,
                assigned_by=assigned_by_id
            )
            
            return db.user_roles[association_id]
        except Exception as e:
            print(f"Error assigning role to user: {e}")
            return None
    
    @classmethod
    def remove_role(cls, user_id, role_id):
        """
        Remove a role from a user.
        
        Args:
            user_id (int): User ID
            role_id (int): Role ID
            
        Returns:
            bool: True if removed successfully
        """
        try:
            from .utils import get_db
            db = get_db()
            
            db(
                (db.user_roles.user == user_id) &
                (db.user_roles.role == role_id)
            ).delete()
            
            return True
        except Exception as e:
            print(f"Error removing role from user: {e}")
            return False
    
    @classmethod
    def get_user_roles(cls, user_id):
        """
        Get all roles for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of Role instances
        """
        try:
            from .utils import get_db
            db = get_db()
            
            rows = db(
                (db.user_roles.user == user_id) &
                (db.user_roles.role == db.roles.id)
            ).select(db.roles.ALL)
            
            return [row for row in rows]
        except Exception as e:
            print(f"Error getting user roles: {e}")
            return []
    
    @classmethod
    def get_role_users(cls, role_id):
        """
        Get all users with a specific role.
        
        Args:
            role_id (int): Role ID
            
        Returns:
            list: List of user IDs
        """
        try:
            from .utils import get_db
            db = get_db()
            
            rows = db(
                (db.user_roles.role == role_id) &
                (db.user_roles.user == db.auth_users.id)
            ).select(db.auth_users.id)
            
            return [row.id for row in rows]
        except Exception as e:
            print(f"Error getting role users: {e}")
            return []

