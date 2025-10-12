# -*- coding: utf-8 -*-
"""
OAuth authentication module for social login support.
"""

from .tokens import encrypt_token, decrypt_token, generate_encryption_key
from .oauth_manager import OAuthManager, get_oauth_manager
from .linking import (
    find_existing_user_by_email,
    link_oauth_account,
    unlink_oauth_account,
    can_unlink_oauth_account
)

__all__ = [
    'encrypt_token',
    'decrypt_token',
    'generate_encryption_key',
    'OAuthManager',
    'get_oauth_manager',
    'find_existing_user_by_email',
    'link_oauth_account',
    'unlink_oauth_account',
    'can_unlink_oauth_account'
]

