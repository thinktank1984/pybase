# -*- coding: utf-8 -*-
"""
Facebook OAuth 2.0 provider implementation.
"""

from typing import Dict
import requests
from .base import BaseOAuthProvider


class FacebookOAuthProvider(BaseOAuthProvider):
    """Facebook OAuth 2.0 provider (Facebook Login)."""
    
    provider_name = 'facebook'
    authorize_url = 'https://www.facebook.com/v18.0/dialog/oauth'
    token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
    userinfo_url = 'https://graph.facebook.com/v18.0/me'
    scopes = ['email', 'public_profile']
    
    def get_user_info(self, access_token: str) -> Dict[str, any]:
        """
        Fetch user information from Facebook Graph API.
        
        Args:
            access_token: Valid Facebook access token
            
        Returns:
            Dict with normalized user data
        """
        # Request specific fields from Facebook
        params = {
            'fields': 'id,email,name,first_name,last_name,picture.type(large)',
            'access_token': access_token
        }
        
        response = requests.get(
            self.userinfo_url,
            params=params,
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract picture URL from nested structure
        picture_url = None
        if 'picture' in data and 'data' in data['picture']:
            picture_url = data['picture']['data'].get('url')
        
        # Normalize Facebook's response to our standard format
        return {
            'id': data.get('id'),
            'email': data.get('email'),  # May be None if user denied email permission
            'email_verified': bool(data.get('email')),  # Facebook only returns verified emails
            'name': data.get('name'),
            'given_name': data.get('first_name'),
            'family_name': data.get('last_name'),
            'picture': picture_url,
            'locale': None  # Facebook doesn't provide locale in this endpoint
        }

