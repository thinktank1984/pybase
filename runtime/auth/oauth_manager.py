# -*- coding: utf-8 -*-
"""
OAuth manager for registering and managing OAuth providers.
"""

import os
from typing import Dict, Optional, List
from .providers import (
    GoogleOAuthProvider,
    GitHubOAuthProvider,
    MicrosoftOAuthProvider,
    FacebookOAuthProvider
)


class OAuthManager:
    """Manages OAuth provider registration and configuration."""
    
    def __init__(self):
        """Initialize OAuth manager."""
        self.providers: Dict[str, any] = {}
        self._load_providers_from_env()
    
    def _load_providers_from_env(self):
        """Load OAuth providers from environment variables."""
        # Google OAuth
        if os.environ.get('GOOGLE_CLIENT_ID') and os.environ.get('GOOGLE_CLIENT_SECRET'):
            self.register_provider(
                GoogleOAuthProvider(
                    client_id=os.environ['GOOGLE_CLIENT_ID'],
                    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
                    redirect_uri=self._get_redirect_uri('google')
                )
            )
        
        # GitHub OAuth
        if os.environ.get('GITHUB_CLIENT_ID') and os.environ.get('GITHUB_CLIENT_SECRET'):
            self.register_provider(
                GitHubOAuthProvider(
                    client_id=os.environ['GITHUB_CLIENT_ID'],
                    client_secret=os.environ['GITHUB_CLIENT_SECRET'],
                    redirect_uri=self._get_redirect_uri('github')
                )
            )
        
        # Microsoft OAuth
        if os.environ.get('MICROSOFT_CLIENT_ID') and os.environ.get('MICROSOFT_CLIENT_SECRET'):
            tenant = os.environ.get('MICROSOFT_TENANT', 'common')
            self.register_provider(
                MicrosoftOAuthProvider(
                    client_id=os.environ['MICROSOFT_CLIENT_ID'],
                    client_secret=os.environ['MICROSOFT_CLIENT_SECRET'],
                    redirect_uri=self._get_redirect_uri('microsoft'),
                    tenant=tenant
                )
            )
        
        # Facebook OAuth
        if os.environ.get('FACEBOOK_APP_ID') and os.environ.get('FACEBOOK_APP_SECRET'):
            self.register_provider(
                FacebookOAuthProvider(
                    client_id=os.environ['FACEBOOK_APP_ID'],
                    client_secret=os.environ['FACEBOOK_APP_SECRET'],
                    redirect_uri=self._get_redirect_uri('facebook')
                )
            )
    
    def _get_redirect_uri(self, provider: str) -> str:
        """
        Build redirect URI for OAuth callback.
        
        Args:
            provider: Provider name (google, github, etc.)
            
        Returns:
            str: Full redirect URI
        """
        base_url = os.environ.get('OAUTH_BASE_URL', 'http://localhost:8081')
        return f"{base_url}/auth/oauth/{provider}/callback"
    
    def register_provider(self, provider) -> None:
        """
        Register an OAuth provider.
        
        Args:
            provider: Provider instance (must have provider_name attribute)
        """
        if not hasattr(provider, 'provider_name'):
            raise ValueError("Provider must have provider_name attribute")
        
        self.providers[provider.provider_name] = provider
    
    def get_provider(self, provider_name: str):
        """
        Get a registered OAuth provider.
        
        Args:
            provider_name: Name of the provider (google, github, etc.)
            
        Returns:
            Provider instance or None if not registered
        """
        return self.providers.get(provider_name)
    
    def list_enabled_providers(self) -> List[str]:
        """
        Get list of enabled provider names.
        
        Returns:
            List[str]: List of provider names
        """
        return list(self.providers.keys())
    
    def is_provider_enabled(self, provider_name: str) -> bool:
        """
        Check if a provider is enabled.
        
        Args:
            provider_name: Provider name
            
        Returns:
            bool: True if provider is enabled
        """
        return provider_name in self.providers


# Global OAuth manager instance
_oauth_manager = None


def get_oauth_manager() -> OAuthManager:
    """
    Get the global OAuth manager instance.
    
    Returns:
        OAuthManager: Global OAuth manager
    """
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthManager()
    return _oauth_manager

