# -*- coding: utf-8 -*-
"""
Google OAuth 2.0 provider implementation.
"""

from typing import Dict
import requests
from .base import BaseOAuthProvider


class GoogleOAuthProvider(BaseOAuthProvider):
    """Google OAuth 2.0 provider with OpenID Connect support."""
    
    provider_name = 'google'
    authorize_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    token_url = 'https://oauth2.googleapis.com/token'
    userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    revoke_url = 'https://oauth2.googleapis.com/revoke'
    scopes = ['openid', 'email', 'profile']
    
    def get_additional_auth_params(self) -> Dict[str, str]:
        """Add Google-specific parameters."""
        return {
            'access_type': 'offline',  # Request refresh token
            'prompt': 'select_account'  # Allow user to select account
        }
    
    def get_user_info(self, access_token: str) -> Dict[str, any]:
        """
        Fetch user information from Google.
        
        Args:
            access_token: Valid Google access token
            
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
        
        # Normalize Google's response to our standard format
        return {
            'id': data.get('id'),
            'email': data.get('email'),
            'email_verified': data.get('verified_email', False),
            'name': data.get('name'),
            'given_name': data.get('given_name'),
            'family_name': data.get('family_name'),
            'picture': data.get('picture'),
            'locale': data.get('locale')
        }
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a Google access or refresh token.
        
        Args:
            token: Token to revoke
            
        Returns:
            bool: True if revocation succeeded
        """
        try:
            response = requests.post(
                self.revoke_url,
                data={'token': token},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

