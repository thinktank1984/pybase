# -*- coding: utf-8 -*-
"""
Base OAuth provider class with PKCE support.
"""

import hashlib
import secrets
import base64
from abc import ABC, abstractmethod
from typing import Dict, Tuple, List
import requests
from urllib.parse import urlencode


class BaseOAuthProvider(ABC):
    """
    Abstract base class for OAuth 2.0 providers.
    Implements OAuth 2.0 authorization code flow with PKCE.
    """
    
    # Subclasses must define these
    provider_name: str = None  # type: ignore[assignment]
    authorize_url: str = None  # type: ignore[assignment]
    token_url: str = None  # type: ignore[assignment]
    userinfo_url: str = None  # type: ignore[assignment]
    scopes: List[str] = []
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize OAuth provider.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Callback URL for OAuth redirects
        """
        if not self.provider_name:
            raise ValueError("provider_name must be defined")
        if not self.authorize_url:
            raise ValueError("authorize_url must be defined")
        if not self.token_url:
            raise ValueError("token_url must be defined")
            
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    @staticmethod
    def generate_state() -> str:
        """
        Generate a random state parameter for CSRF protection.
        
        Returns:
            str: Random state string (32 bytes, URL-safe base64)
        """
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    @staticmethod
    def generate_pkce_pair() -> Tuple[str, str]:
        """
        Generate PKCE code verifier and challenge.
        
        Returns:
            Tuple[str, str]: (code_verifier, code_challenge)
        """
        # Generate code_verifier (43-128 characters, URL-safe)
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')
        
        # Generate code_challenge (SHA256 hash of verifier)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def build_authorization_url(self, state: str, code_challenge: str) -> str:
        """
        Build the OAuth authorization URL with PKCE.
        
        Args:
            state: State parameter for CSRF protection
            code_challenge: PKCE code challenge
            
        Returns:
            str: Complete authorization URL
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        # Allow subclasses to add provider-specific parameters
        params.update(self.get_additional_auth_params())
        
        return f"{self.authorize_url}?{urlencode(params)}"
    
    def get_additional_auth_params(self) -> Dict[str, str]:
        """
        Override to add provider-specific authorization parameters.
        
        Returns:
            Dict[str, str]: Additional parameters for authorization URL
        """
        return {}
    
    def exchange_code_for_tokens(
        self, 
        code: str, 
        code_verifier: str
    ) -> Dict[str, object]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            code_verifier: PKCE code verifier
            
        Returns:
            Dict containing:
                - access_token: Access token
                - token_type: Token type (usually 'Bearer')
                - expires_in: Expiration time in seconds (optional)
                - refresh_token: Refresh token (optional)
                - scope: Granted scopes (optional)
                
        Raises:
            requests.HTTPError: If token exchange fails
            ValueError: If response is invalid
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'code_verifier': code_verifier,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(
            self.token_url,
            data=data,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        if 'access_token' not in token_data:
            raise ValueError(f"No access_token in response from {self.provider_name}")
        
        return token_data
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, object]:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict containing new token data
            
        Raises:
            requests.HTTPError: If refresh fails
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(
            self.token_url,
            data=data,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        return response.json()
    
    @abstractmethod
    def get_user_info(self, access_token: str) -> Dict[str, object]:
        """
        Fetch user information from the provider.
        Must be implemented by subclasses.
        
        Args:
            access_token: Valid access token
            
        Returns:
            Dict containing normalized user data:
                - id: Provider's unique user ID (required)
                - email: User's email (required if available)
                - email_verified: Whether email is verified (bool)
                - name: User's display name (optional)
                - given_name: First name (optional)
                - family_name: Last name (optional)
                - picture: Avatar URL (optional)
                - locale: User's locale (optional)
                
        Raises:
            requests.HTTPError: If API call fails
        """
        pass
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token.
        Override if provider supports token revocation.
        
        Args:
            token: Token to revoke
            
        Returns:
            bool: True if revocation succeeded
        """
        # Not all providers support revocation
        # Subclasses can override if supported
        return False
    
    def __repr__(self):
        return f"<{self.__class__.__name__} client_id={self.client_id[:10]}...>"

