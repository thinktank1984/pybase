# -*- coding: utf-8 -*-
"""
Role model for Role-Based Access Control (RBAC).
"""

from emmett.orm import Field, has_many
from emmett import now
from base_model import BaseModel


class Role(BaseModel):
    """
    Role model representing a user role in the system.
    
    Roles are containers for permissions and can be assigned to users.
    Standard roles include: Admin, Moderator, Author, Viewer.
    """
    
    tablename = 'roles'
    
    # Fields
    name = Field.string(length=80, unique=True, notnull=True)
    description = Field.text()
    created_at = Field.datetime(default=lambda: now())
    
    # Relationships
    has_many('user_roles', 'role_permissions')
    
    # Auto Routes Configuration (enables automatic route generation)
    auto_routes = True
    
    # REST API configuration
    rest_rw = {
        'id': (True, False),
        'name': (True, True),
        'description': (True, True),
        'created_at': (True, False)
    }
    
    # Validation
    validation = {
        'name': {
            'presence': True,
            'len': {'range': (1, 80)},
            'match': '^[A-Za-z][A-Za-z0-9_]*$'  # Start with letter, alphanumeric + underscore
        }
    }
    
    @classmethod
    def get_by_name(cls, name):
        """
        Get a role by name.
        
        Args:
            name (str): Role name
            
        Returns:
            Role: Role instance or None if not found
        """
        try:
            from ..utils import get_db
            db = get_db()
            return db(db.roles.name == name).select().first()
        except Exception as e:
            print(f"Error in Role.get_by_name: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Get all roles ordered by name.
        
        Returns:
            list: List of Role instances
        """
        try:
            from ..utils import get_db
            db = get_db()
            return db(db.roles).select(orderby='name')
        except Exception as e:
            print(f"Error in Role.get_all: {e}")
            return []
    
    def get_permissions(self):
        """
        Get all permissions associated with this role.
        Works on both Model instances and Row objects.
        
        Returns:
            list: List of Permission instances
        """
        try:
            from ..utils import get_db
            db = get_db()
            
            # Get role ID (works for both Model and Row objects)
            role_id = self.id if hasattr(self, 'id') else self['id']  # type: ignore[attr-defined, index]
            
            # Query permissions through role_permissions association
            rows = db(
                (db.role_permissions.role == role_id) &
                (db.role_permissions.permission == db.permissions.id)
            ).select(db.permissions.ALL)
            
            return [row for row in rows]
        except Exception as e:
            role_name = getattr(self, 'name', None) or self.get('name', 'unknown')
            print(f"Error getting permissions for role {role_name}: {e}")
            return []
    
    def has_permission(self, permission_name):
        """
        Check if this role has a specific permission.
        
        Args:
            permission_name (str): Permission name (e.g., 'post.create')
            
        Returns:
            bool: True if role has the permission
        """
        try:
            from ..utils import get_db
            db = get_db()
            
            result = db(
                (db.role_permissions.role == self.id) &  # type: ignore[attr-defined]
                (db.role_permissions.permission == db.permissions.id) &
                (db.permissions.name == permission_name)
            ).select().first()
            
            return result is not None
        except Exception as e:
            print(f"Error in Role.has_permission: {e}")
            return False
    
    def add_permission(self, permission):
        """
        Add a permission to this role.
        
        Args:
            permission: Permission instance or permission ID
            
        Returns:
            bool: True if added successfully
        """
        try:
            from ..utils import get_db
            db = get_db()
            
            permission_id = permission.id if hasattr(permission, 'id') else permission  # type: ignore[attr-defined]
            
            # Check if already exists
            existing = db(
                (db.role_permissions.role == self.id) &  # type: ignore[attr-defined]
                (db.role_permissions.permission == permission_id)
            ).select().first()
            
            if existing:
                return True
            
            # Create new association
            db.role_permissions.insert(
                role=self.id,  # type: ignore[attr-defined]
                permission=permission_id,
                granted_at=now()
            )
            
            return True
        except Exception as e:
            print(f"Error adding permission to role: {e}")
            return False
    
    def remove_permission(self, permission):
        """
        Remove a permission from this role.
        
        Args:
            permission: Permission instance or permission ID
            
        Returns:
            bool: True if removed successfully
        """
        try:
            from ..utils import get_db
            db = get_db()
            
            permission_id = permission.id if hasattr(permission, 'id') else permission  # type: ignore[attr-defined]
            
            db(
                (db.role_permissions.role == self.id) &  # type: ignore[attr-defined]
                (db.role_permissions.permission == permission_id)
            ).delete()
            
            return True
        except Exception as e:
            print(f"Error removing permission from role: {e}")
            return False

