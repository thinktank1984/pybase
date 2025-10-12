# -*- coding: utf-8 -*-
"""
Comment model package.
"""

from .model import Comment
from . import views
from . import api

__all__ = ['Comment', 'views', 'api']
