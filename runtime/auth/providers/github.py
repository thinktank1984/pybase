# -*- coding: utf-8 -*-
"""
GitHub OAuth 2.0 provider implementation.
"""

from typing import Dict
import requests
from .base import BaseOAuthProvider


class GitHubOAuthProvider(BaseOAuthProvider):
    """GitHub OAuth 2.0 provider."""
    
    provider_name = 'github'
    authorize_url = 'https://github.com/login/oauth/authorize'
    token_url = 'https://github.com/login/oauth/access_token'
    userinfo_url = 'https://api.github.com/user'
    emails_url = 'https://api.github.com/user/emails'
    scopes = ['user:email', 'read:user']
    
    def get_user_info(self, access_token: str) -> Dict[str, any]:
        """
        Fetch user information from GitHub.
        
        Args:
            access_token: Valid GitHub access token
            
        Returns:
            Dict with normalized user data
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'User-Agent': 'Emmett-OAuth-App'  # GitHub requires User-Agent
        }
        
        # Get user profile
        response = requests.get(
            self.userinfo_url,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        user_data = response.json()
        
        # Get email addresses (GitHub may not include email in user profile)
        email = user_data.get('email')
        email_verified = False
        
        if not email:
            # Fetch email from emails endpoint
            email_response = requests.get(
                self.emails_url,
                headers=headers,
                timeout=10
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                # Find primary verified email
                for e in emails:
                    if e.get('primary') and e.get('verified'):
                        email = e.get('email')
                        email_verified = True
                        break
                # If no primary verified email, use first verified email
                if not email:
                    for e in emails:
                        if e.get('verified'):
                            email = e.get('email')
                            email_verified = True
                            break
                # Last resort: use any email
                if not email and emails:
                    email = emails[0].get('email')
        else:
            # Email from profile is considered verified by GitHub
            email_verified = True
        
        # Normalize GitHub's response to our standard format
        return {
            'id': str(user_data.get('id')),
            'email': email,
            'email_verified': email_verified,
            'name': user_data.get('name') or user_data.get('login'),
            'given_name': None,  # GitHub doesn't provide separate name fields
            'family_name': None,
            'picture': user_data.get('avatar_url'),
            'locale': None  # GitHub doesn't provide locale
        }

