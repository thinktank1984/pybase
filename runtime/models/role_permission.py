# -*- coding: utf-8 -*-
"""
RolePermission association model for many-to-many relationship between roles and permissions.
"""

from emmett.orm import Model, Field, belongs_to
from emmett import now


class RolePermission(Model):
    """
    Association model linking roles to permissions.
    
    Tracks when a permission was granted and who granted it for audit purposes.
    """
    
    tablename = 'role_permissions'
    
    # Foreign key relationships
    belongs_to('role', 'permission')
    
    # Audit fields
    granted_at = Field.datetime(default=lambda: now())
    granted_by = Field.int()  # ID of user who granted the permission
    
    # Validation - ensure unique role-permission combinations
    validation = {
        'role': {'presence': True},
        'permission': {'presence': True}
    }
    
    @classmethod
    def grant_permission(cls, role_id, permission_id, granted_by_id=None):
        """
        Grant a permission to a role.
        
        Args:
            role_id (int): Role ID
            permission_id (int): Permission ID
            granted_by_id (int): Optional ID of user granting the permission
            
        Returns:
            RolePermission: Created association or existing one
        """
        try:
            from emmett import current
            db = current.app.ext.db
            
            # Check if already exists
            existing = db(
                (db.role_permissions.role == role_id) &
                (db.role_permissions.permission == permission_id)
            ).select().first()
            
            if existing:
                return existing
            
            # Create new association
            association_id = db.role_permissions.insert(
                role=role_id,
                permission=permission_id,
                granted_by=granted_by_id
            )
            
            return db.role_permissions[association_id]
        except Exception as e:
            print(f"Error granting permission to role: {e}")
            return None
    
    @classmethod
    def revoke_permission(cls, role_id, permission_id):
        """
        Revoke a permission from a role.
        
        Args:
            role_id (int): Role ID
            permission_id (int): Permission ID
            
        Returns:
            bool: True if revoked successfully
        """
        try:
            from emmett import current
            db = current.app.ext.db
            
            db(
                (db.role_permissions.role == role_id) &
                (db.role_permissions.permission == permission_id)
            ).delete()
            
            return True
        except Exception as e:
            print(f"Error revoking permission from role: {e}")
            return False
    
    @classmethod
    def get_role_permissions(cls, role_id):
        """
        Get all permissions for a role.
        
        Args:
            role_id (int): Role ID
            
        Returns:
            list: List of Permission instances
        """
        try:
            from emmett import current
            db = current.app.ext.db
            
            rows = db(
                (db.role_permissions.role == role_id) &
                (db.role_permissions.permission == db.permissions.id)
            ).select(db.permissions.ALL)
            
            return [row for row in rows]
        except Exception as e:
            print(f"Error getting role permissions: {e}")
            return []
    
    @classmethod
    def get_permission_roles(cls, permission_id):
        """
        Get all roles with a specific permission.
        
        Args:
            permission_id (int): Permission ID
            
        Returns:
            list: List of Role instances
        """
        try:
            from emmett import current
            db = current.app.ext.db
            
            rows = db(
                (db.role_permissions.permission == permission_id) &
                (db.role_permissions.role == db.roles.id)
            ).select(db.roles.ALL)
            
            return [row for row in rows]
        except Exception as e:
            print(f"Error getting permission roles: {e}")
            return []

