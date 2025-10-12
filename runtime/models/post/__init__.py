# -*- coding: utf-8 -*-
"""
Post model package.
"""

from .model import Post
from . import views
from . import api

__all__ = ['Post', 'views', 'api']
