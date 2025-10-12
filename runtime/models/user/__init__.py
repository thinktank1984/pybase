# -*- coding: utf-8 -*-
"""User model package."""

from .model import User, is_admin, get_current_user, is_authenticated, setup

__all__ = ['User', 'is_admin', 'get_current_user', 'is_authenticated', 'setup']
