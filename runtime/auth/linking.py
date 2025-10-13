# -*- coding: utf-8 -*-
"""
Account linking and unlinking logic for OAuth providers.
"""

from typing import Optional, Dict, Any, List
from emmett import current


def find_existing_user_by_email(email: str):
    """
    Find an existing user by email address.
    
    Args:
        email: Email address to search for
        
    Returns:
        User instance or None
    """
    if not email:
        return None
    
    try:
        from ..models import User
        return User.where(lambda u: u.email == email).first()
    except Exception as e:
        print(f"Error finding user by email: {e}")
        return None


def link_oauth_account(user, provider: str, provider_user_id: str, user_info: Dict) -> bool:
    """
    Link an OAuth provider account to an existing user.
    
    Args:
        user: User instance or user ID
        provider: Provider name (google, github, etc.)
        provider_user_id: User ID from the provider
        user_info: User information from provider
        
    Returns:
        bool: True if linking succeeded
        
    Raises:
        ValueError: If account is already linked to another user
    """
    try:
        from ..models import OAuthAccount
        
        # Get user ID
        user_id = user.id if hasattr(user, 'id') else user
        
        # Check if this OAuth account is already linked to someone else
        existing = OAuthAccount.get_by_provider(provider, provider_user_id)
        if existing:
            if existing.auth_user == user_id:
                # Already linked to this user, just update the data
                existing.update_profile_data(user_info)
                return True
            else:
                raise ValueError(
                    f"This {provider} account is already linked to another user"
                )
        
        # Check if user already has this provider linked
        existing_user_account = OAuthAccount.get_by_user_and_provider(user_id, provider)
        if existing_user_account:
            # User is trying to link a different account from same provider
            # For now, we'll update the existing link
            existing_user_account.update_record(
                provider_user_id=provider_user_id,
                email=user_info.get('email'),
                name=user_info.get('name'),
                picture=user_info.get('picture'),
                profile_data=user_info
            )
            return True
        
        # Create new OAuth account link
        oauth_account = OAuthAccount.create(
            auth_user=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=user_info.get('email'),
            name=user_info.get('name'),
            picture=user_info.get('picture'),
            profile_data=user_info
        )
        
        return oauth_account is not None
        
    except Exception as e:
        print(f"Error linking OAuth account: {e}")
        raise


def unlink_oauth_account(user, provider: str) -> bool:
    """
    Unlink an OAuth provider from a user.
    Ensures user has at least one authentication method remaining.
    
    Args:
        user: User instance or user ID
        provider: Provider name to unlink
        
    Returns:
        bool: True if unlinking succeeded
        
    Raises:
        ValueError: If unlinking would leave user without auth method
    """
    try:
        from ..models import OAuthAccount, User
        
        # Get user ID
        user_id = user.id if hasattr(user, 'id') else user
        
        # Get user instance
        if not hasattr(user, 'password'):
            user = User.get(user_id)
            if not user:
                raise ValueError("User not found")
        
        # Check if user can unlink this provider
        can_unlink, reason = can_unlink_oauth_account(user, provider)
        if not can_unlink:
            raise ValueError(reason)
        
        # Find and delete OAuth account
        oauth_account = OAuthAccount.get_by_user_and_provider(user_id, provider)
        if not oauth_account:
            raise ValueError(f"No {provider} account linked")
        
        # Delete associated token first
        from ..models import OAuthToken
        token = OAuthToken.where(
            lambda t: t.oauth_account == oauth_account.id
        ).first()
        if token:
            # Try to revoke token with provider
            try:
                from .oauth_manager import get_oauth_manager
                oauth_manager = get_oauth_manager()
                provider_instance = oauth_manager.get_provider(provider)
                if provider_instance:
                    access_token = token.get_access_token()
                    provider_instance.revoke_token(access_token)
            except Exception as e:
                print(f"Warning: Failed to revoke token with provider: {e}")
            
            token.delete()
        
        # Delete OAuth account
        oauth_account.delete()
        
        return True
        
    except Exception as e:
        print(f"Error unlinking OAuth account: {e}")
        raise


def can_unlink_oauth_account(user, provider: str) -> tuple[bool, Optional[str]]:
    """
    Check if a user can unlink an OAuth provider.
    User must have at least one other authentication method.
    
    Args:
        user: User instance or user ID
        provider: Provider name to check
        
    Returns:
        Tuple[bool, Optional[str]]: (can_unlink, reason_if_not)
    """
    try:
        from ..models import OAuthAccount, User
        
        # Get user ID
        user_id = user.id if hasattr(user, 'id') else user
        
        # Get user instance
        if not hasattr(user, 'password'):
            user = User.get(user_id)
            if not user:
                return False, "User not found"
        
        # Check if user has a password
        has_password = bool(user.password)
        
        # Get all OAuth accounts for user
        oauth_accounts = OAuthAccount.get_by_user(user_id)
        oauth_count = len(list(oauth_accounts))
        
        # User must have either:
        # 1. A password, OR
        # 2. At least 2 OAuth accounts (so they'll have 1 left after unlinking)
        if has_password:
            return True, None
        elif oauth_count > 1:
            return True, None
        else:
            return False, (
                "Cannot unlink your last login method. "
                "Please set a password or link another provider first."
            )
            
    except Exception as e:
        print(f"Error checking if can unlink: {e}")
        return False, "Error checking authentication methods"


def get_user_oauth_accounts(user):
    """
    Get all OAuth accounts for a user.
    
    Args:
        user: User instance or user ID
        
    Returns:
        List of OAuthAccount instances
    """
    try:
        from ..models import OAuthAccount
        
        user_id = user.id if hasattr(user, 'id') else user
        return list(OAuthAccount.get_by_user(user_id))
        
    except Exception as e:
        print(f"Error getting user OAuth accounts: {e}")
        return []


def get_user_auth_methods(user) -> Dict[str, Any]:
    """
    Get all authentication methods available to a user.
    
    Args:
        user: User instance or user ID
        
    Returns:
        Dict with auth method info:
            - has_password: bool
            - oauth_providers: list of provider names
            - can_unlink: dict of provider -> bool
    """
    try:
        from ..models import User
        
        # Get user instance
        if not hasattr(user, 'password'):
            user_id = user.id if hasattr(user, 'id') else user
            user = User.get(user_id)
            if not user:
                return {
                    'has_password': False,
                    'oauth_providers': [],
                    'can_unlink': {}
                }
        
        # Get OAuth accounts
        oauth_accounts = get_user_oauth_accounts(user)
        providers = [acc.provider for acc in oauth_accounts]
        
        # Check which providers can be unlinked
        can_unlink = {}
        for provider in providers:
            can_unlink[provider], _ = can_unlink_oauth_account(user, provider)
        
        return {
            'has_password': bool(user.password),
            'oauth_providers': providers,
            'can_unlink': can_unlink
        }
        
    except Exception as e:
        print(f"Error getting user auth methods: {e}")
        return {
            'has_password': False,
            'oauth_providers': [],
            'can_unlink': {}
        }

