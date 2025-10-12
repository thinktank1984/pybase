# -*- coding: utf-8 -*-
"""
Token encryption and management utilities for OAuth tokens.
"""

import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode


def generate_encryption_key():
    """
    Generate a new Fernet encryption key.
    This should be called once and the key stored securely in environment variables.
    
    Returns:
        str: Base64-encoded encryption key
    """
    return Fernet.generate_key().decode('utf-8')


def get_encryption_key():
    """
    Get the encryption key from environment variable.
    If not set, generate a new one (for development only).
    
    Returns:
        bytes: Encryption key
    """
    key = os.environ.get('OAUTH_TOKEN_ENCRYPTION_KEY')
    
    if not key:
        # In development, generate a key if not set
        # In production, this should be a fatal error
        if os.environ.get('EMMETT_ENV', 'development') == 'production':
            raise ValueError(
                "OAUTH_TOKEN_ENCRYPTION_KEY must be set in production environment. "
                "Generate a key using: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )
        else:
            # Generate and cache a dev key
            print("⚠️  Warning: No OAUTH_TOKEN_ENCRYPTION_KEY set, using generated key (development only)")
            key = Fernet.generate_key().decode('utf-8')
            os.environ['OAUTH_TOKEN_ENCRYPTION_KEY'] = key
    
    return key.encode('utf-8') if isinstance(key, str) else key


# Initialize cipher with the encryption key
_cipher = None


def _get_cipher():
    """Get or create the Fernet cipher instance."""
    global _cipher
    if _cipher is None:
        _cipher = Fernet(get_encryption_key())
    return _cipher


def encrypt_token(token: str) -> str:
    """
    Encrypt an OAuth token for storage.
    
    Args:
        token: The plaintext token to encrypt
        
    Returns:
        str: The encrypted token (base64 encoded)
        
    Raises:
        ValueError: If token is empty
    """
    if not token:
        raise ValueError("Cannot encrypt empty token")
    
    cipher = _get_cipher()
    encrypted = cipher.encrypt(token.encode('utf-8'))
    return encrypted.decode('utf-8')


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt an OAuth token from storage.
    
    Args:
        encrypted_token: The encrypted token (base64 encoded)
        
    Returns:
        str: The decrypted plaintext token
        
    Raises:
        ValueError: If encrypted_token is empty
        cryptography.fernet.InvalidToken: If token cannot be decrypted
    """
    if not encrypted_token:
        raise ValueError("Cannot decrypt empty token")
    
    cipher = _get_cipher()
    decrypted = cipher.decrypt(encrypted_token.encode('utf-8'))
    return decrypted.decode('utf-8')

