# -*- coding: utf-8 -*-
"""
OAuthToken model for encrypted token storage.
"""

from emmett.orm import Model, Field, belongs_to
from emmett import now
from datetime import timedelta


class OAuthToken(Model):
    """
    Stores encrypted OAuth access and refresh tokens.
    Tokens are encrypted at rest using Fernet symmetric encryption.
    """
    
    tablename = "oauth_tokens"
    
    belongs_to('oauth_account')
    
    # Encrypted token fields (stored as text to accommodate encryption overhead)
    access_token_encrypted = Field.text(
        notnull=True,
        comment="Encrypted OAuth access token"
    )
    
    refresh_token_encrypted = Field.text(
        comment="Encrypted OAuth refresh token (if available)"
    )
    
    # Token metadata
    token_type = Field.string(
        length=50,
        default='Bearer',
        comment="Token type (usually Bearer)"
    )
    
    scope = Field.string(
        length=512,
        comment="Granted OAuth scopes (space-separated)"
    )
    
    # Expiration tracking
    access_token_expires_at = Field.datetime(
        comment="When access token expires"
    )
    
    refresh_token_expires_at = Field.datetime(
        comment="When refresh token expires (if known)"
    )
    
    # Timestamps
    created_at = Field.datetime(
        default=lambda: now(),
        comment="When tokens were first stored"
    )
    
    updated_at = Field.datetime(
        default=lambda: now(),
        update=lambda: now(),
        comment="When tokens were last updated"
    )
    
    def is_access_token_expired(self):
        """
        Check if access token is expired.
        
        Returns:
            bool: True if expired
        """
        if not self.access_token_expires_at:
            return False
        return now() >= self.access_token_expires_at
    
    def needs_refresh(self, buffer_minutes=5):
        """
        Check if access token needs refresh (expired or expiring soon).
        
        Args:
            buffer_minutes: Refresh if expiring within this many minutes
            
        Returns:
            bool: True if refresh needed
        """
        if not self.access_token_expires_at:
            return False
        
        threshold = now() + timedelta(minutes=buffer_minutes)
        return self.access_token_expires_at <= threshold
    
    def get_access_token(self):
        """
        Get decrypted access token.
        
        Returns:
            str: Decrypted access token
        """
        from ...auth.tokens import decrypt_token
        return decrypt_token(self.access_token_encrypted)
    
    def get_refresh_token(self):
        """
        Get decrypted refresh token.
        
        Returns:
            str: Decrypted refresh token or None
        """
        if not self.refresh_token_encrypted:
            return None
        
        from ...auth.tokens import decrypt_token
        return decrypt_token(self.refresh_token_encrypted)
    
    def set_access_token(self, token, expires_in=None):
        """
        Set encrypted access token.
        
        Args:
            token: Plaintext access token
            expires_in: Seconds until expiration (optional)
        """
        from ...auth.tokens import encrypt_token
        
        update_data = {
            'access_token_encrypted': encrypt_token(token),
            'updated_at': now()
        }
        
        if expires_in:
            update_data['access_token_expires_at'] = now() + timedelta(seconds=expires_in)
        
        self.update_record(**update_data)
    
    def set_refresh_token(self, token, expires_in=None):
        """
        Set encrypted refresh token.
        
        Args:
            token: Plaintext refresh token
            expires_in: Seconds until expiration (optional)
        """
        from ...auth.tokens import encrypt_token
        
        update_data = {
            'refresh_token_encrypted': encrypt_token(token) if token else None,
            'updated_at': now()
        }
        
        if expires_in:
            update_data['refresh_token_expires_at'] = now() + timedelta(seconds=expires_in)
        
        self.update_record(**update_data)
    
    def update_tokens(self, access_token, refresh_token=None, expires_in=None, scope=None):
        """
        Update both access and refresh tokens.
        
        Args:
            access_token: New access token
            refresh_token: New refresh token (optional)
            expires_in: Seconds until access token expiration
            scope: New scope string
        """
        from ...auth.tokens import encrypt_token
        
        update_data = {
            'access_token_encrypted': encrypt_token(access_token),
            'updated_at': now()
        }
        
        if refresh_token:
            update_data['refresh_token_encrypted'] = encrypt_token(refresh_token)
        
        if expires_in:
            update_data['access_token_expires_at'] = now() + timedelta(seconds=expires_in)
        
        if scope:
            update_data['scope'] = scope
        
        self.update_record(**update_data)
    
    @classmethod
    def create_for_oauth_account(cls, oauth_account_id, access_token, refresh_token=None, 
                                 expires_in=None, token_type='Bearer', scope=None):
        """
        Create a new token record for an OAuth account.
        
        Args:
            oauth_account_id: OAuthAccount ID
            access_token: Access token (plaintext)
            refresh_token: Refresh token (plaintext, optional)
            expires_in: Seconds until expiration
            token_type: Token type (default: Bearer)
            scope: Granted scopes
            
        Returns:
            OAuthToken instance
        """
        from ...auth.tokens import encrypt_token
        
        token_data = {
            'oauth_account': oauth_account_id,
            'access_token_encrypted': encrypt_token(access_token),
            'token_type': token_type,
            'scope': scope
        }
        
        if refresh_token:
            token_data['refresh_token_encrypted'] = encrypt_token(refresh_token)
        
        if expires_in:
            token_data['access_token_expires_at'] = now() + timedelta(seconds=expires_in)
        
        return cls.create(**token_data)

