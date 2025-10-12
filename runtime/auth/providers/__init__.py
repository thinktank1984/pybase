# -*- coding: utf-8 -*-
"""
OAuth provider implementations.
"""

from .base import BaseOAuthProvider
from .google import GoogleOAuthProvider
from .github import GitHubOAuthProvider
from .microsoft import MicrosoftOAuthProvider
from .facebook import FacebookOAuthProvider

__all__ = [
    'BaseOAuthProvider',
    'GoogleOAuthProvider',
    'GitHubOAuthProvider',
    'MicrosoftOAuthProvider',
    'FacebookOAuthProvider'
]

