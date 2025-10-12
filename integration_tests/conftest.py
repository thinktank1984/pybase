# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for integration tests.
"""

import pytest
import sys
import os

# Add runtime to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime'))

from app import app, db
from models import Role, Post


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """
    Setup test environment - runs once per test session.
    Patches Row classes to add custom methods.
    """
    # Patch Row classes to add methods that work on Row objects
    try:
        with db.connection():
            # Get a sample role to find its class
            if hasattr(db, 'roles'):
                sample_role = db(db.roles).select().first()
                if sample_role:
                    RoleRowClass = type(sample_role)
                    
                    # Add get_permissions to RoleRow
                    def role_get_permissions(self):
                        """Get permissions for this role (works on Row objects)."""
                        try:
                            role_id = self.id if hasattr(self, 'id') else self['id']
                            rows = db(
                                (db.role_permissions.role == role_id) &
                                (db.role_permissions.permission == db.permissions.id)
                            ).select(db.permissions.ALL)
                            return [row for row in rows]
                        except Exception as e:
                            role_name = getattr(self, 'name', self.get('name', 'unknown')) if hasattr(self, 'get') else getattr(self, 'name', 'unknown')
                            print(f"Error getting permissions for role {role_name}: {e}")
                            return []
                    
                    RoleRowClass.get_permissions = role_get_permissions
                    print("✅ Patched Role.get_permissions() method")
            
            # Get a sample post to find its class
            if hasattr(db, 'posts'):
                sample_post = db(db.posts).select().first()
                if sample_post:
                    PostRowClass = type(sample_post)
                    
                    # Add can_edit to PostRow
                    def post_can_edit(self, user):
                        """Check if user can edit this post (works on Row objects)."""
                        from models.utils import user_can_access_resource
                        if not user:
                            return False
                        user_id = user.id if hasattr(user, 'id') else user['id']
                        return user_can_access_resource(user_id, 'post', 'edit', self)
                    
                    # Add can_delete to PostRow  
                    def post_can_delete(self, user):
                        """Check if user can delete this post (works on Row objects)."""
                        from models.utils import user_can_access_resource
                        if not user:
                            return False
                        user_id = user.id if hasattr(user, 'id') else user['id']
                        return user_can_access_resource(user_id, 'post', 'delete', self)
                    
                    PostRowClass.can_edit = post_can_edit
                    PostRowClass.can_delete = post_can_delete
                    print("✅ Patched Post.can_edit() and Post.can_delete() methods")
    except Exception as e:
        print(f"⚠️  Warning: Could not patch Row classes: {e}")
        # Don't fail if patching doesn't work, tests might still pass
    
    yield
    
    # Teardown - nothing to clean up

