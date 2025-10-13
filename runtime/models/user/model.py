# -*- coding: utf-8 -*-
"""
User model with authentication utilities and API.
"""

from emmett.orm import has_many
from emmett.tools.auth import AuthUser
from emmett import current, session


class User(AuthUser):
    """User model extending Emmett's AuthUser with role-based permissions."""
    
    has_many('posts', 'comments', 'user_roles', 'oauth_accounts')
    
    rest_rw = {
        'id': (True, False),
        'email': (True, False),
        'first_name': (True, False),
        'last_name': (True, False)
    }
    
    def get_roles(self):
        """
        Get all roles assigned to this user.
        
        Returns:
            list: List of Role instances
        """
        try:
            from ..user_role import UserRole
            return UserRole.get_user_roles(self.id)  # type: ignore[attr-defined]
        except Exception as e:
            print(f"Error getting roles for user {self.id}: {e}")  # type: ignore[attr-defined]
            return []
    
    def has_role(self, role_name):
        """
        Check if user has a specific role.
        
        Args:
            role_name (str): Role name (e.g., 'admin', 'moderator')
            
        Returns:
            bool: True if user has the role
        """
        try:
            roles = self.get_roles()
            return any(role.name.lower() == role_name.lower() for role in roles)
        except:
            return False
    
    def has_any_role(self, *role_names):
        """
        Check if user has any of the specified roles.
        
        Args:
            *role_names: Variable number of role names
            
        Returns:
            bool: True if user has at least one of the roles
        """
        try:
            user_roles = {role.name.lower() for role in self.get_roles()}
            return any(role_name.lower() in user_roles for role_name in role_names)
        except:
            return False
    
    def has_all_roles(self, *role_names):
        """
        Check if user has all of the specified roles.
        
        Args:
            *role_names: Variable number of role names
            
        Returns:
            bool: True if user has all of the roles
        """
        try:
            user_roles = {role.name.lower() for role in self.get_roles()}
            return all(role_name.lower() in user_roles for role_name in role_names)
        except:
            return False
    
    def get_permissions(self, use_cache=True):
        """
        Get all permissions granted to this user through their roles.
        
        Args:
            use_cache (bool): Whether to use session cache
            
        Returns:
            set: Set of permission names
        """
        # Check cache first
        if use_cache and hasattr(session, 'user_permissions') and session.user_permissions:  # type: ignore[union-attr]
            if session.get('user_permissions_id') == self.id:  # type: ignore[attr-defined, union-attr]
                return session.user_permissions  # type: ignore[union-attr]
        
        try:
            permissions = set()
            roles = self.get_roles()
            
            for role in roles:
                # Handle both Model instances and Row objects
                if hasattr(role, 'get_permissions') and callable(role.get_permissions):
                    # Model instance or patched Row with method
                    role_permissions = role.get_permissions()
                else:
                    # Row object without method - get permissions directly from database
                    from app import db
                    role_id = role.id if hasattr(role, 'id') else role['id']
                    
                    # Query permissions through role_permissions association
                    perm_rows = db(
                        (db.role_permissions.role == role_id) &
                        (db.role_permissions.permission == db.permissions.id)
                    ).select(db.permissions.ALL)
                    role_permissions = [row for row in perm_rows]
                
                for perm in role_permissions:
                    permissions.add(perm.name)
            
            # Cache in session
            if use_cache:
                session.user_permissions = permissions  # type: ignore[union-attr]
                session.user_permissions_id = self.id  # type: ignore[attr-defined, union-attr]
            
            return permissions
        except Exception as e:
            print(f"Error getting permissions for user {self.id}: {e}")  # type: ignore[attr-defined]
            import traceback
            traceback.print_exc()
            return set()
    
    def has_permission(self, permission_name):
        """
        Check if user has a specific permission.
        
        Args:
            permission_name (str): Permission name (e.g., 'post.create')
            
        Returns:
            bool: True if user has the permission
        """
        # Admin role has all permissions
        if self.has_role('admin'):
            return True
        
        try:
            permissions = self.get_permissions()
            return permission_name in permissions
        except:
            return False
    
    def has_any_permission(self, *permission_names):
        """
        Check if user has any of the specified permissions.
        
        Args:
            *permission_names: Variable number of permission names
            
        Returns:
            bool: True if user has at least one permission
        """
        # Admin role has all permissions
        if self.has_role('admin'):
            return True
        
        try:
            permissions = self.get_permissions()
            return any(perm in permissions for perm in permission_names)
        except:
            return False
    
    def can_access_resource(self, resource, action, instance=None, scope='any'):
        """
        Check if user can access a resource with a specific action.
        Supports ownership-based permissions.
        
        Args:
            resource (str): Resource name (e.g., 'post')
            action (str): Action name (e.g., 'edit', 'delete')
            instance: Optional resource instance to check ownership
            scope (str): 'own', 'any', or 'both'
            
        Returns:
            bool: True if user can access the resource
        """
        # Admin role has all permissions
        if self.has_role('admin'):
            return True
        
        try:
            permissions = self.get_permissions()
            
            # Check for 'any' scope permission
            any_perm = f"{resource}.{action}.any"
            if any_perm in permissions:
                return True
            
            # Check for 'own' scope permission with ownership
            own_perm = f"{resource}.{action}.own"
            if own_perm in permissions:
                if instance is None:
                    # No instance provided, grant access
                    return True
                
                # Check ownership
                owner_field = getattr(instance, 'user', None) or getattr(instance, 'owner', None)
                if owner_field:
                    owner_id = owner_field.id if hasattr(owner_field, 'id') else owner_field  # type: ignore[attr-defined]
                    return owner_id == self.id  # type: ignore[attr-defined]
            
            # Check for permission without scope
            base_perm = f"{resource}.{action}"
            return base_perm in permissions
            
        except Exception as e:
            print(f"Error checking resource access: {e}")
            return False
    
    def add_role(self, role):
        """
        Add a role to this user.
        
        Args:
            role: Role instance or role ID
            
        Returns:
            bool: True if added successfully
        """
        try:
            from ..user_role import UserRole
            role_id = role.id if hasattr(role, 'id') else role  # type: ignore[attr-defined]
            
            result = UserRole.assign_role(self.id, role_id)  # type: ignore[attr-defined]
            
            # Invalidate permission cache
            self.refresh_permissions()
            
            return result is not None
        except Exception as e:
            print(f"Error adding role to user: {e}")
            return False
    
    def remove_role(self, role):
        """
        Remove a role from this user.
        
        Args:
            role: Role instance or role ID
            
        Returns:
            bool: True if removed successfully
        """
        try:
            from ..user_role import UserRole
            role_id = role.id if hasattr(role, 'id') else role  # type: ignore[attr-defined]
            
            result = UserRole.remove_role(self.id, role_id)  # type: ignore[attr-defined]
            
            # Invalidate permission cache
            self.refresh_permissions()
            
            return result
        except Exception as e:
            print(f"Error removing role from user: {e}")
            return False
    
    def refresh_permissions(self):
        """
        Refresh the cached permissions for this user.
        """
        try:
            if hasattr(session, 'user_permissions'):
                del session.user_permissions  # type: ignore[union-attr]
            if hasattr(session, 'user_permissions_id'):
                del session.user_permissions_id  # type: ignore[union-attr]
            
            # Reload permissions
            self.get_permissions(use_cache=True)
        except:
            pass
    
    # ========================================================================
    # OAuth Methods
    # ========================================================================
    
    def get_oauth_accounts(self):
        """
        Get all OAuth accounts linked to this user.
        
        Returns:
            list: List of OAuthAccount instances
        """
        try:
            from ..oauth_account import OAuthAccount
            return list(OAuthAccount.get_by_user(self.id))  # type: ignore[attr-defined]
        except Exception as e:
            print(f"Error getting OAuth accounts: {e}")
            return []
    
    def has_oauth_account(self, provider):
        """
        Check if user has a specific OAuth provider linked.
        
        Args:
            provider (str): Provider name (google, github, etc.)
            
        Returns:
            bool: True if provider is linked
        """
        try:
            from ..oauth_account import OAuthAccount
            account = OAuthAccount.get_by_user_and_provider(self.id, provider)  # type: ignore[attr-defined]
            return account is not None
        except:
            return False
    
    def get_oauth_account(self, provider):
        """
        Get a specific OAuth account for this user.
        
        Args:
            provider (str): Provider name
            
        Returns:
            OAuthAccount instance or None
        """
        try:
            from ..oauth_account import OAuthAccount
            return OAuthAccount.get_by_user_and_provider(self.id, provider)  # type: ignore[attr-defined]
        except:
            return None
    
    def link_oauth_account(self, provider, provider_user_id, user_info):
        """
        Link an OAuth provider to this user.
        
        Args:
            provider: Provider name
            provider_user_id: User ID from provider
            user_info: User info from provider
            
        Returns:
            bool: True if linked successfully
        """
        try:
            from ...auth.linking import link_oauth_account as link_fn
            return link_fn(self, provider, provider_user_id, user_info)
        except Exception as e:
            print(f"Error linking OAuth account: {e}")
            return False
    
    def unlink_oauth_account(self, provider):
        """
        Unlink an OAuth provider from this user.
        
        Args:
            provider: Provider name
            
        Returns:
            bool: True if unlinked successfully
        """
        try:
            from ...auth.linking import unlink_oauth_account as unlink_fn
            return unlink_fn(self, provider)
        except Exception as e:
            print(f"Error unlinking OAuth account: {e}")
            return False
    
    def can_unlink_oauth(self, provider):
        """
        Check if user can unlink an OAuth provider.
        
        Args:
            provider: Provider name
            
        Returns:
            tuple: (can_unlink, reason_if_not)
        """
        try:
            from ...auth.linking import can_unlink_oauth_account
            return can_unlink_oauth_account(self, provider)
        except:
            return False, "Error checking authentication methods"
    
    def get_auth_methods(self):
        """
        Get all authentication methods available to this user.
        
        Returns:
            dict: Dictionary with has_password, oauth_providers, can_unlink
        """
        try:
            from ...auth.linking import get_user_auth_methods
            return get_user_auth_methods(self)
        except:
            return {
                'has_password': bool(self.password),
                'oauth_providers': [],
                'can_unlink': {}
            }


def get_current_user():
    """Get currently authenticated user."""
    try:
        if hasattr(current, 'session') and hasattr(current.session, 'auth') and current.session.auth:
            return current.session.auth.user  # type: ignore[union-attr]
        elif hasattr(session, 'auth') and session.auth:  # type: ignore[union-attr]
            return session.auth.user  # type: ignore[union-attr]
    except:
        pass
    return None


def is_authenticated():
    """Check if user is authenticated."""
    return get_current_user() is not None


def is_admin():
    """Check if current user has admin role."""
    if not session.auth:  # type: ignore[union-attr]
        return False
    
    user = session.auth.user  # type: ignore[union-attr]
    if not user:
        return False
    
    try:
        db = current.app.ext.db
        try:
            membership = db(
                (db.auth_memberships.user == user.id) &
                (db.auth_memberships.auth_group == db.auth_groups.id) &
                (db.auth_groups.role == 'admin')
            ).select().first()
        except AttributeError:
            membership = db(
                (db.auth_memberships.auth_user == user.id) &
                (db.auth_memberships.auth_group == db.auth_groups.id) &
                (db.auth_groups.role == 'admin')
            ).select().first()
        
        return membership is not None
    except Exception as e:
        print(f"is_admin error: {e}")
        return False


def setup(app):
    """Setup REST API for User model (read-only)."""
    users_api = app.rest_module(
        __name__, 
        'users_api', 
        User, 
        url_prefix='api/users',
        disabled_methods=['create', 'update', 'delete']
    )
    return users_api
