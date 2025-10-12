# -*- coding: utf-8 -*-
"""
Post views/routes.
"""

from emmett import redirect, url
from emmett.tools import requires
from emmett.orm import get_or_404

from .model import Post


def setup_routes(app):
    """
    Setup all post-related routes.
    
    Args:
        app: Emmett application instance
    """
    from models.comment import Comment
    from models.user import is_admin, is_authenticated
    
    @app.route("/")
    async def index():
        """Homepage showing all blog posts."""
        posts = Post.all().select(orderby=~Post.date)
        return dict(posts=posts)

    @app.route("/post/<int:pid>", methods=['get', 'post'])
    async def one(pid):
        """View single post with comments."""
        def _validate_comment(form):
            # manually set post id in comment form
            form.params.post = pid
        
        # get post and return 404 if doesn't exist
        post = get_or_404(Post, pid)
        
        # get comments
        comments = post.comments(orderby=~Comment.date)
        
        # and create a form for commenting if the user is logged in
        if is_authenticated():
            form = await Comment.form(onvalidation=_validate_comment)
            if form.accepted:
                redirect(url('one', pid))
        
        return locals()

    @app.route("/new", methods=['get', 'post'])
    @requires(is_admin, url('index'))
    async def new_post():
        """Create a new blog post (admin only)."""
        form = await Post.form()
        if form.accepted:
            redirect(url('one', form.params.id))
        return dict(form=form)

