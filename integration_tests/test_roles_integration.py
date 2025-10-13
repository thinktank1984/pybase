# -*- coding: utf-8 -*-
"""
REAL Integration Tests for Role-Based Access Control System

🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨

⚠️ USING MOCKS, STUBS, OR TEST DOUBLES IS ILLEGAL IN THIS REPOSITORY ⚠️

This is a ZERO-TOLERANCE POLICY:
- ❌ FORBIDDEN: unittest.mock, Mock(), MagicMock(), patch()
- ❌ FORBIDDEN: pytest-mock, mocker fixture
- ❌ FORBIDDEN: Any mocking, stubbing, or test double libraries
- ❌ FORBIDDEN: Fake in-memory databases or fake HTTP responses
- ❌ FORBIDDEN: Simulated external services or APIs

✅ ONLY REAL INTEGRATION TESTS ARE ALLOWED:
- ✅ Real database operations with actual SQL
- ✅ Real HTTP requests through test client
- ✅ Real browser interactions with Chrome DevTools MCP
- ✅ Real external service calls (or skip tests if unavailable)

If you write a test with mocks, the test is INVALID and must be rewritten.

NO MOCKING - Tests use actual database operations, real HTTP requests,
and verify actual state changes.

Following repository policy: Mocking is FORBIDDEN.
"""

import pytest
import uuid
from app import User, Post, Comment
from models import (
    Role, Permission, UserRole, RolePermission,
    seed_all, user_add_role, user_remove_role, user_has_role, 
    user_has_any_role, user_has_all_roles, user_get_roles,
    user_has_permission, user_has_any_permission, user_get_permissions,
    user_can_access_resource
)

# Import app and db from conftest fixtures
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime'))
import app as app_module
app = app_module.app
db = app_module.db


def unique_email(prefix='test'):
    """Generate a unique email address for testing"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture(scope='module', autouse=True)
def _prepare_db(request):
    """Ensure roles are seeded and Row methods patched for integration tests"""
    print("\n🔧 Preparing roles integration test data")
    
    # Ensure roles are seeded (idempotent - safe for concurrent access)
    with db.connection():
        role_count = db.executesql("SELECT COUNT(*) FROM roles")[0][0]
        if role_count == 0:
            print("   🌱 Seeding roles and permissions...")
            seed_all(db)
            db.commit()
            print("   ✅ Seeded roles and permissions")
        else:
            print(f"   ✅ Roles already seeded ({role_count} roles)")
        
        # Patch Row classes with methods after seeding
        # Get a seeded role to find its Row class
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
                print("   ✅ Patched Role.get_permissions() method")
        
        # Create a temporary post to get its Row class and patch it
        if hasattr(db, 'posts'):
            # Check if temp user already exists
            temp_user = db(db.users.email == '_temp_patch@test.com').select().first()
            if temp_user:
                temp_user_id = temp_user.id
            else:
                temp_user_id = db.users.insert(
                    email='_temp_patch@test.com',
                    password='x',
                    first_name='T',
                    last_name='P'
                )
                db.commit()
            
            temp_post_id = db.posts.insert(
                title='_temp_',
                text='x',
                user=temp_user_id
            )
            db.commit()
            
            sample_post = db(db.posts.id == temp_post_id).select().first()
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
                print("   ✅ Patched Post.can_edit() and Post.can_delete() methods")
            
            # Cleanup temp data
            db(db.posts.id == temp_post_id).delete()
            db.commit()
    
    yield
    
    # Minimal cleanup - only remove test data created by this module
    print("\n🧹 Cleaning up roles integration test data")
    try:
        with db.connection():
            # Delete only test users created by fixtures (those with unique emails)
            # Pattern: test_*@example.com
            # Quote "user" column name to avoid PostgreSQL keyword conflicts
            db.executesql("DELETE FROM user_roles WHERE \"user\" IN (SELECT id FROM users WHERE email LIKE 'test_%@example.com')")
            db.executesql("DELETE FROM posts WHERE \"user\" IN (SELECT id FROM users WHERE email LIKE 'test_%@example.com')")
            db.executesql("DELETE FROM users WHERE email LIKE 'test_%@example.com'")
            db.commit()
            print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")


@pytest.fixture()
def client(app):
    """Test client for HTTP requests"""
    return app.test_client()


# ==============================================================================
# Test Role Model - REAL Database Operations
# ==============================================================================

def test_role_creation_and_retrieval():
    """Test creating and retrieving a role from real database"""
    with db.connection():
        # Create real role in database
        role_id = db.roles.insert(
            name='test_role_001',
            description='Test role for integration test'
        )
        db.commit()
        
        # Verify role exists in real database
        role = db(db.roles.id == role_id).select().first()
        assert role is not None
        assert role.name == 'test_role_001'
        assert role.description == 'Test role for integration test'
        
        # Cleanup real database
        db(db.roles.id == role_id).delete()
        db.commit()


def test_role_get_by_name():
    """Test Role.get_by_name() with real database"""
    with db.connection():
        # Use seeded admin role from real database
        admin = Role.get_by_name('admin')
        assert admin is not None
        assert admin.name == 'admin'


# ==============================================================================
# Test Permission Model - REAL Database Operations
# ==============================================================================

def test_permission_creation_and_retrieval():
    """Test creating and retrieving a permission from real database"""
    with db.connection():
        # Create real permission in database
        perm_id = db.permissions.insert(
            name='test.permission.001',
            resource='test',
            action='permission',
            description='Test permission'
        )
        db.commit()
        
        # Verify permission exists in real database
        perm = db(db.permissions.id == perm_id).select().first()
        assert perm is not None
        assert perm.name == 'test.permission.001'
        assert perm.resource == 'test'
        assert perm.action == 'permission'
        
        # Cleanup real database
        db(db.permissions.id == perm_id).delete()
        db.commit()


def test_permission_get_by_name():
    """Test Permission.get_by_name() with real database"""
    with db.connection():
        # Use seeded permission from real database
        perm = Permission.get_by_name('post.create')
        assert perm is not None
        assert perm.name == 'post.create'
        assert perm.resource == 'post'


def test_permission_get_by_resource():
    """Test Permission.get_by_resource() with real database"""
    with db.connection():
        # Query real database for post permissions
        post_perms = Permission.get_by_resource('post')
        assert len(post_perms) > 0
        assert all(p.resource == 'post' for p in post_perms)


# ==============================================================================
# Test User-Role Assignment - REAL Database Operations
# ==============================================================================

def test_user_role_assignment():
    """Test assigning role to user in real database"""
    with db.connection():
        # Create real test user in database
        user_id = db.users.insert(
            email=unique_email('test_role_user'),
            password='password123',
            first_name='Test',
            last_name='User'
        )
        db.commit()
        
        # Get real user object
        user = User.get(user_id)
        assert user is not None
        
        # Get real author role from database
        author_role = Role.get_by_name('author')
        assert author_role is not None
        
        # Assign role to user in real database
        user_add_role(user_id, author_role)
        
        # Verify role assignment in real database
        assert user_has_role(user_id, 'author') is True
        roles = user_get_roles(user_id)
        assert any(r.name == 'author' for r in roles)
        
        # Cleanup real database
        db(db.user_roles.user == user_id).delete()
        db(db.users.id == user_id).delete()
        db.commit()


def test_user_multiple_roles():
    """Test assigning multiple roles to user in real database"""
    with db.connection():
        # Create real user
        user_id = db.users.insert(
            email=unique_email('test_multi_role'),
            password='password123',
            first_name='Multi',
            last_name='Role'
        )
        db.commit()
        
        user = User.get(user_id)
        author_role = Role.get_by_name('author')
        viewer_role = Role.get_by_name('viewer')
        
        # Assign multiple roles in real database
        user_add_role(user_id, author_role)
        user_add_role(user_id, viewer_role)
        
        # Verify in real database
        roles = user_get_roles(user_id)
        role_names = [r.name for r in roles]
        assert 'author' in role_names
        assert 'viewer' in role_names
        assert user_has_any_role(user_id, 'author', 'moderator') is True
        assert user_has_all_roles(user_id, 'author', 'viewer') is True
        
        # Cleanup real database
        db(db.user_roles.user == user_id).delete()
        db(db.users.id == user_id).delete()
        db.commit()


def test_user_role_removal():
    """Test removing role from user in real database"""
    with db.connection():
        # Create real user with role
        user_id = db.users.insert(
            email=unique_email('test_remove_role'),
            password='password123',
            first_name='Remove',
            last_name='Role'
        )
        db.commit()
        
        user = User.get(user_id)
        author_role = Role.get_by_name('author')
        
        # Assign and verify in real database
        user_add_role(user_id, author_role)
        assert user_has_role(user_id, 'author') is True
        
        # Remove role from real database
        user_remove_role(user_id, author_role)
        assert user_has_role(user_id, 'author') is False
        
        # Cleanup real database
        db(db.user_roles.user == user_id).delete()
        db(db.users.id == user_id).delete()
        db.commit()


# ==============================================================================
# Test User Permissions - REAL Database Operations
# ==============================================================================

def test_user_inherits_permissions_from_role():
    """Test user inherits permissions from assigned role in real database"""
    with db.connection():
        # Create real user
        user_id = db.users.insert(
            email=unique_email('test_perms'),
            password='password123',
            first_name='Perm',
            last_name='User'
        )
        db.commit()
        
        user = User.get(user_id)
        author_role = Role.get_by_name('author')
        
        # Assign role in real database
        user_add_role(user_id, author_role)
        
        # Verify permissions from real database
        assert user_has_permission(user_id, 'post.create') is True
        
        perms = user_get_permissions(user_id, use_cache=False)
        assert len(perms) > 0
        
        # Cleanup real database
        db(db.user_roles.user == user_id).delete()
        db(db.users.id == user_id).delete()
        db.commit()


def test_admin_bypass():
    """Test admin role has all permissions (bypass) in real database"""
    with db.connection():
        # Create real admin user
        user_id = db.users.insert(
            email=unique_email('test_admin'),
            password='password123',
            first_name='Admin',
            last_name='User'
        )
        db.commit()
        
        user = User.get(user_id)
        admin_role = Role.get_by_name('admin')
        
        # Assign admin role in real database
        user_add_role(user_id, admin_role)
        
        # Verify admin bypass in real database
        assert user_has_permission(user_id, 'post.create') is True
        assert user_has_permission(user_id, 'post.delete.any') is True
        assert user_has_permission(user_id, 'user.manage') is True
        assert user_has_permission(user_id, 'any.random.permission') is True
        
        # Cleanup real database
        db(db.user_roles.user == user_id).delete()
        db(db.users.id == user_id).delete()
        db.commit()


def test_user_without_role_has_no_permissions():
    """Test user without roles has no permissions in real database"""
    with db.connection():
        # Create real user without roles
        user_id = db.users.insert(
            email=unique_email('test_no_role'),
            password='password123',
            first_name='No',
            last_name='Role'
        )
        db.commit()
        
        user = User.get(user_id)
        
        # Verify no permissions in real database
        assert user_has_permission(user_id, 'post.create') is False
        assert user_has_permission(user_id, 'user.manage') is False
        
        # Cleanup real database
        db(db.users.id == user_id).delete()
        db.commit()


# ==============================================================================
# Test Ownership-Based Permissions - REAL Database Operations
# ==============================================================================

def test_ownership_based_permissions():
    """Test ownership-based permission checks with real database"""
    with db.connection():
        # Create two real users
        owner_id = db.users.insert(
            email=unique_email('owner'),
            password='password',
            first_name='Owner',
            last_name='User'
        )
        other_id = db.users.insert(
            email=unique_email('other'),
            password='password',
            first_name='Other',
            last_name='User'
        )
        db.commit()
        
        owner = User.get(owner_id)
        other = User.get(other_id)
        author_role = Role.get_by_name('author')
        
        # Assign author role to both in real database
        user_add_role(owner_id, author_role)
        user_add_role(other_id, author_role)
        
        # Create real post owned by owner
        post_id = db.posts.insert(
            title='Owner Post',
            text='Content',
            user=owner_id
        )
        db.commit()
        
        post = Post.get(post_id)
        
        # Verify ownership checks in real database
        assert user_can_access_resource(owner_id, 'post', 'edit', post) is True
        assert user_can_access_resource(other_id, 'post', 'edit', post) is False
        
        # Cleanup real database
        db(db.posts.id == post_id).delete()
        db(db.user_roles.user == owner_id).delete()
        db(db.user_roles.user == other_id).delete()
        db(db.users.id == owner_id).delete()
        db(db.users.id == other_id).delete()
        db.commit()


def test_moderator_can_edit_any_post():
    """Test moderator with .any permission can edit any post in real database"""
    with db.connection():
        # Create real users
        owner_id = db.users.insert(
            email=unique_email('post_owner'),
            password='password',
            first_name='Owner',
            last_name='User'
        )
        mod_id = db.users.insert(
            email=unique_email('moderator'),
            password='password',
            first_name='Mod',
            last_name='User'
        )
        db.commit()
        
        owner = User.get(owner_id)
        moderator = User.get(mod_id)
        
        # Assign roles in real database
        author_role = Role.get_by_name('author')
        moderator_role = Role.get_by_name('moderator')
        user_add_role(owner_id, author_role)
        user_add_role(mod_id, moderator_role)
        
        # Create real post
        post_id = db.posts.insert(
            title='Owner Post',
            text='Content',
            user=owner_id
        )
        db.commit()
        
        post = Post.get(post_id)
        
        # Verify moderator can edit any post in real database
        assert user_can_access_resource(mod_id, 'post', 'edit', post) is True
        
        # Cleanup real database
        db(db.posts.id == post_id).delete()
        db(db.user_roles.user == owner_id).delete()
        db(db.user_roles.user == mod_id).delete()
        db(db.users.id == owner_id).delete()
        db(db.users.id == mod_id).delete()
        db.commit()


# ==============================================================================
# Test Post/Comment Permission Methods - REAL Database Operations
# ==============================================================================

def test_post_can_edit_as_owner():
    """Test Post.can_edit() for owner with real database"""
    with db.connection():
        # Create real user with author role
        user_id = db.users.insert(
            email=unique_email('can_edit'),
            password='password',
            first_name='Can',
            last_name='Edit'
        )
        db.commit()
        
        user = User.get(user_id)
        author_role = Role.get_by_name('author')
        user_add_role(user_id, author_role)
        
        # Create real post
        post_id = db.posts.insert(
            title='My Post',
            text='Content',
            user=user_id
        )
        db.commit()
        
        post = Post.get(post_id)
        
        # Verify can_edit in real database
        assert post.can_edit(user) is True
        
        # Cleanup real database
        db(db.posts.id == post_id).delete()
        db(db.user_roles.user == user_id).delete()
        db(db.users.id == user_id).delete()
        db.commit()


def test_post_can_delete_as_owner():
    """Test Post.can_delete() for owner with real database"""
    with db.connection():
        # Create real user with author role
        user_id = db.users.insert(
            email=unique_email('can_delete'),
            password='password',
            first_name='Can',
            last_name='Delete'
        )
        db.commit()
        
        user = User.get(user_id)
        author_role = Role.get_by_name('author')
        user_add_role(user_id, author_role)
        
        # Create real post
        post_id = db.posts.insert(
            title='My Post',
            text='Content',
            user=user_id
        )
        db.commit()
        
        post = Post.get(post_id)
        
        # Verify can_delete in real database
        assert post.can_delete(user) is True
        
        # Cleanup real database
        db(db.posts.id == post_id).delete()
        db(db.user_roles.user == user_id).delete()
        db(db.users.id == user_id).delete()
        db.commit()


# ==============================================================================
# Test Seeded Data - REAL Database Verification
# ==============================================================================

def test_seeded_roles_exist():
    """Verify all default roles were seeded in real database"""
    with db.connection():
        admin = Role.get_by_name('admin')
        moderator = Role.get_by_name('moderator')
        author = Role.get_by_name('author')
        viewer = Role.get_by_name('viewer')
        
        assert admin is not None
        assert moderator is not None
        assert author is not None
        assert viewer is not None


def test_seeded_permissions_exist():
    """Verify default permissions were seeded in real database"""
    with db.connection():
        post_create = Permission.get_by_name('post.create')
        post_edit_own = Permission.get_by_name('post.edit.own')
        post_edit_any = Permission.get_by_name('post.edit.any')
        user_manage = Permission.get_by_name('user.manage')
        
        assert post_create is not None
        assert post_edit_own is not None
        assert post_edit_any is not None
        assert user_manage is not None


def test_role_permission_associations():
    """Verify roles have permissions assigned in real database"""
    with db.connection():
        author = Role.get_by_name('author')
        author_perms = author.get_permissions()
        
        # Author should have permissions from seeding
        assert isinstance(author_perms, list)
        assert len(author_perms) > 0


# ==============================================================================
# Test User.has_any_permission - REAL Database Operations
# ==============================================================================

def test_user_has_any_permission():
    """Test has_any_permission method with real database"""
    with db.connection():
        # Create real user
        user_id = db.users.insert(
            email=unique_email('test_any_perm'),
            password='password',
            first_name='Any',
            last_name='Perm'
        )
        db.commit()
        
        user = User.get(user_id)
        author_role = Role.get_by_name('author')
        user_add_role(user_id, author_role)
        
        # Test has_any_permission in real database
        assert user_has_any_permission(user_id, 'post.create', 'user.manage') is True
        assert user_has_any_permission(user_id, 'user.manage', 'role.delete') is False
        
        # Cleanup real database
        db(db.user_roles.user == user_id).delete()
        db(db.users.id == user_id).delete()
        db.commit()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

