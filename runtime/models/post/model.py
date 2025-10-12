# -*- coding: utf-8 -*-
"""
Post model with integrated routes and API.
"""

from emmett import now, session, redirect, url, abort
from emmett.orm import Model, Field, belongs_to, has_many
from emmett.tools import requires


class Post(Model):
    """Blog post model with title, content, author, and timestamp."""
    
    belongs_to('user')
    has_many('comments')

    title = Field()
    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: _get_current_user_id(),
        'date': now
    }
    validation = {
        'title': {'presence': True},
        'text': {'presence': True},
        'user': {'allow': 'empty'}
    }
    fields_rw = {
        'user': False,
        'date': False
    }
    rest_rw = {
        'id': (True, False),
        'user': (False, True),
        'date': (True, False)
    }
    
    # Permission configuration
    class Meta:
        permissions = {
            'create': 'post.create',
            'read': None,  # Public
            'update.own': 'post.edit.own',
            'update.any': 'post.edit.any',
            'delete.own': 'post.delete.own',
            'delete.any': 'post.delete.any',
        }
        ownership_field = 'user'
    
    def can_edit(self, user=None):
        """
        Check if user can edit this post using role-based permissions.
        
        Args:
            user: User instance (defaults to current user)
            
        Returns:
            bool: True if user can edit this post
        """
        if user is None:
            from ..user import get_current_user
            user = get_current_user()
        
        if not user:
            return False
        
        # Check if user has permission to edit this post
        return user.can_access_resource('post', 'edit', self)
    
    def can_delete(self, user=None):
        """
        Check if user can delete this post using role-based permissions.
        
        Args:
            user: User instance (defaults to current user)
            
        Returns:
            bool: True if user can delete this post
        """
        if user is None:
            from ..user import get_current_user
            user = get_current_user()
        
        if not user:
            return False
        
        # Check if user has permission to delete this post
        return user.can_access_resource('post', 'delete', self)


def _get_current_user_id():
    """Get current user ID for default values."""
    try:
        from emmett import current
        if hasattr(current, 'session') and hasattr(current.session, 'auth') and current.session.auth:
            return current.session.auth.user.id
    except:
        pass
    return None


def _is_admin():
    """Check if current user has admin role."""
    from emmett import session
    from models.utils import user_has_role
    
    if not session.auth:
        return False
    
    user = session.auth.user
    if not user:
        return False
    
    try:
        # Use the helper function from utils
        return user_has_role(user.id, 'admin')
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False


def setup(app):
    """Setup routes and REST API for Post model."""
    from models.comment import Comment
    from models.user import is_authenticated
    from emmett.routing.urls import url as _url
    
    # Define route handlers as async functions
    async def index():
        """Homepage showing all blog posts."""
        posts = Post.all().select(orderby=~Post.date)
        return dict(posts=posts)

    async def one(pid):
        """View single post with comments."""
        def _validate_comment(form):
            form.params.post = pid
        
        # Get post directly without helper
        post = Post.get(pid)
        if not post:
            abort(404)
        
        comments = post.comments(orderby=~Comment.date)
        
        form = None
        if is_authenticated():
            form = await Comment.form(onvalidation=_validate_comment)
            if form.accepted:
                redirect(url('one', pid))
        
        return dict(post=post, comments=comments, form=form)

    async def new_post():
        """Create a new blog post (admin only)."""
        form = await Post.form()
        if form.accepted:
            redirect(url('one', form.params.id))
        return dict(form=form)
    
    # Register routes using route() as a function (not decorator)
    # Register with full namespace to match url() helper expectations
    app.route("/", name='app.index')(index)
    app.route("/post/<int:pid>", name='app.one', methods=['get', 'post'])(one)
    app.route("/new", name='app.new_post', methods=['get', 'post'])(
        requires(_is_admin, '/')(new_post)
    )
    
    # REST API
    posts_api = app.rest_module(__name__, 'posts_api', Post, url_prefix='api/posts')
    
    @posts_api.before_create
    def set_post_user(attrs):
        """Automatically set user from session if authenticated."""
        if session.auth and session.auth.user:
            if 'user' not in attrs:
                attrs['user'] = session.auth.user.id
    
    return posts_api
