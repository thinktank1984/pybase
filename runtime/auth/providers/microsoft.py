# -*- coding: utf-8 -*-
"""
Microsoft OAuth 2.0 provider implementation (Azure AD / Microsoft Identity Platform).
"""

from typing import Dict
import requests
from .base import BaseOAuthProvider


class MicrosoftOAuthProvider(BaseOAuthProvider):
    """Microsoft OAuth 2.0 provider (Azure AD / Microsoft Account)."""
    
    provider_name = 'microsoft'
    # Use 'common' tenant to support both personal and work/school accounts
    authorize_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    userinfo_url = 'https://graph.microsoft.com/v1.0/me'
    scopes = ['openid', 'email', 'profile', 'User.Read']
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant: str = 'common'):
        """
        Initialize Microsoft OAuth provider.
        
        Args:
            client_id: Azure AD application (client) ID
            client_secret: Azure AD client secret
            redirect_uri: Callback URL
            tenant: Azure AD tenant ID or 'common' for multi-tenant
        """
        super().__init__(client_id, client_secret, redirect_uri)
        
        # Allow custom tenant configuration
        self.tenant = tenant
        self.authorize_url = f'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize'
        self.token_url = f'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token'
    
    def get_additional_auth_params(self) -> Dict[str, str]:
        """Add Microsoft-specific parameters."""
        return {
            'response_mode': 'query'
        }
    
    def get_user_info(self, access_token: str) -> Dict[str, any]:
        """
        Fetch user information from Microsoft Graph API.
        
        Args:
            access_token: Valid Microsoft access token
            
        Returns:
            Dict with normalized user data
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            self.userinfo_url,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Normalize Microsoft's response to our standard format
        return {
            'id': data.get('id'),
            'email': data.get('mail') or data.get('userPrincipalName'),
            'email_verified': True,  # Microsoft emails are considered verified
            'name': data.get('displayName'),
            'given_name': data.get('givenName'),
            'family_name': data.get('surname'),
            'picture': None,  # Would require additional Graph API call
            'locale': data.get('preferredLanguage')
        }

