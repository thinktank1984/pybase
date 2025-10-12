# -*- coding: utf-8 -*-
"""
Permission model for granular access control.
"""

from emmett.orm import Model, Field, has_many
from emmett import now
import re


class Permission(Model):
    """
    Permission model representing a specific permission in the system.
    
    Permissions follow the naming convention: {resource}.{action}[.{scope}]
    Examples: post.create, post.edit.own, post.delete.any
    """
    
    tablename = 'permissions'
    
    # Fields
    name = Field.string(length=120, unique=True, notnull=True)
    resource = Field.string(length=40, notnull=True)
    action = Field.string(length=40, notnull=True)
    scope = Field.string(length=20)  # Optional: 'own', 'any', or empty
    description = Field.text()
    created_at = Field.datetime(default=lambda: now())
    
    # Relationships
    has_many('role_permissions')
    
    # REST API configuration
    rest_rw = {
        'id': (True, False),
        'name': (True, False),  # Read-only, generated from resource+action+scope
        'resource': (True, True),
        'action': (True, True),
        'scope': (True, True),
        'description': (True, True),
        'created_at': (True, False)
    }
    
    # Validation
    validation = {
        'name': {
            'presence': True,
            'len': {'range': (3, 120)}
        },
        'resource': {
            'presence': True,
            'len': {'range': (1, 40)},
            'match': '^[a-z][a-z0-9_]*$'  # Lowercase, start with letter
        },
        'action': {
            'presence': True,
            'len': {'range': (1, 40)},
            'match': '^[a-z][a-z0-9_]*$'  # Lowercase, start with letter
        }
    }
    
    def _before_insert(self):
        """Generate permission name before insert."""
        self._generate_name()
        self._validate_name()
    
    def _before_update(self):
        """Regenerate permission name before update."""
        self._generate_name()
        self._validate_name()
    
    def _generate_name(self):
        """Generate permission name from resource, action, and scope."""
        if self.scope:
            self.name = f"{self.resource}.{self.action}.{self.scope}"
        else:
            self.name = f"{self.resource}.{self.action}"
    
    def _validate_name(self):
        """Validate permission name format."""
        pattern = r'^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)?$'
        if not re.match(pattern, self.name):
            raise ValueError(
                f"Invalid permission name format: {self.name}. "
                "Expected format: resource.action or resource.action.scope"
            )
    
    @classmethod
    def get_by_name(cls, name):
        """
        Get a permission by name.
        
        Args:
            name (str): Permission name (e.g., 'post.create')
            
        Returns:
            Permission: Permission instance or None if not found
        """
        try:
            from ..utils import get_db
            db = get_db()
            return db(db.permissions.name == name).select().first()
        except Exception as e:
            print(f"Error in Permission.get_by_name: {e}")
            return None
    
    @classmethod
    def get_by_resource(cls, resource):
        """
        Get all permissions for a specific resource.
        
        Args:
            resource (str): Resource name (e.g., 'post')
            
        Returns:
            list: List of Permission instances
        """
        try:
            from ..utils import get_db
            db = get_db()
            return db(db.permissions.resource == resource).select(orderby='action')
        except Exception as e:
            print(f"Error in Permission.get_by_resource: {e}")
            return []
    
    @classmethod
    def get_all(cls):
        """
        Get all permissions ordered by resource and action.
        
        Returns:
            list: List of Permission instances
        """
        try:
            from ..utils import get_db
            db = get_db()
            return db(db.permissions).select(orderby='resource|action')
        except Exception as e:
            print(f"Error in Permission.get_all: {e}")
            return []
    
    @classmethod
    def create_from_name(cls, name, description=''):
        """
        Create a permission from a name string.
        
        Args:
            name (str): Permission name (e.g., 'post.create' or 'post.edit.own')
            description (str): Optional description
            
        Returns:
            Permission: Created permission instance or None
        """
        try:
            from ..utils import get_db
            db = get_db()
            
            # Check if already exists
            existing = cls.get_by_name(name)
            if existing:
                return existing
            
            # Parse name
            parts = name.split('.')
            if len(parts) < 2 or len(parts) > 3:
                print(f"Invalid permission name format: {name}")
                return None
            
            resource = parts[0]
            action = parts[1]
            scope = parts[2] if len(parts) == 3 else ''
            
            # Create permission
            permission_id = db.permissions.insert(
                resource=resource,
                action=action,
                scope=scope,
                description=description
            )
            
            return db.permissions[permission_id]
        except Exception as e:
            print(f"Error creating permission {name}: {e}")
            return None
    
    def get_roles(self):
        """
        Get all roles that have this permission.
        
        Returns:
            list: List of Role instances
        """
        try:
            from ..utils import get_db
            db = get_db()
            
            rows = db(
                (db.role_permissions.permission == self.id) &
                (db.role_permissions.role == db.roles.id)
            ).select(db.roles.ALL)
            
            return [row for row in rows]
        except Exception as e:
            print(f"Error getting roles for permission {self.name}: {e}")
            return []

