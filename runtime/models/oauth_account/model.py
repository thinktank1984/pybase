# -*- coding: utf-8 -*-
"""
OAuthAccount model for tracking OAuth provider linkages.
"""

from emmett.orm import Model, Field, belongs_to, has_one
from emmett import now


class OAuthAccount(Model):
    """
    Represents a linked OAuth provider account.
    Links a user to an OAuth provider (Google, GitHub, etc.)
    """
    
    tablename = "oauth_accounts"
    
    belongs_to({'user': 'User'})  # Link to User model
    has_one({'oauth_token': 'OAuthToken'})
    
    # Fields
    provider = Field.string(
        length=50,
        notnull=True,
        comment="OAuth provider name (google, github, microsoft, facebook)"
    )
    
    provider_user_id = Field.string(
        length=255,
        notnull=True,
        comment="User ID from the OAuth provider"
    )
    
    email = Field.string(
        length=255,
        comment="Email address from OAuth provider"
    )
    
    name = Field.string(
        length=255,
        comment="Display name from OAuth provider"
    )
    
    picture = Field.string(
        length=512,
        comment="Avatar/profile picture URL from provider"
    )
    
    profile_data = Field.json(
        comment="Additional profile data from provider (JSON)"
    )
    
    created_at = Field.datetime(
        default=lambda: now(),
        comment="When this OAuth account was first linked"
    )
    
    last_login_at = Field.datetime(
        comment="Last time user logged in via this provider"
    )
    
    # Validation
    validation = {
        'provider': {'in': ['google', 'github', 'microsoft', 'facebook']},
        'email': {'format': 'email', 'allow_empty': True}
    }
    
    # Indexes and constraints
    # Note: Emmett doesn't have direct unique constraint syntax in Field
    # These will be added in migrations
    
    @classmethod
    def get_by_provider(cls, provider, provider_user_id):
        """
        Get an OAuth account by provider and provider user ID.
        
        Args:
            provider: Provider name (google, github, etc.)
            provider_user_id: User ID from the provider
            
        Returns:
            OAuthAccount instance or None
        """
        return cls.where(
            lambda account: (
                (account.provider == provider) & 
                (account.provider_user_id == provider_user_id)
            )
        ).first()
    
    @classmethod
    def get_by_user_and_provider(cls, user_id, provider):
        """
        Get an OAuth account for a specific user and provider.
        
        Args:
            user_id: User ID
            provider: Provider name
            
        Returns:
            OAuthAccount instance or None
        """
        return cls.where(
            lambda account: (
                (account.auth_user == user_id) & 
                (account.provider == provider)
            )
        ).first()
    
    @classmethod
    def get_by_user(cls, user_id):
        """
        Get all OAuth accounts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of OAuthAccount instances
        """
        return cls.where(lambda account: account.auth_user == user_id).select()
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.update_record(last_login_at=now())
    
    def update_profile_data(self, user_info):
        """
        Update profile data from OAuth provider.
        
        Args:
            user_info: Dictionary of user info from provider
        """
        update_data = {
            'last_login_at': now()
        }
        
        if 'email' in user_info and user_info['email']:
            update_data['email'] = user_info['email']
        
        if 'name' in user_info and user_info['name']:
            update_data['name'] = user_info['name']
        
        if 'picture' in user_info and user_info['picture']:
            update_data['picture'] = user_info['picture']
        
        # Store full profile data
        update_data['profile_data'] = user_info
        
        self.update_record(**update_data)

