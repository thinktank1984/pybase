# -*- coding: utf-8 -*-

from emmett import App, session, now, url, redirect, abort
from emmett.orm import Database, Model, Field, belongs_to, has_many
from emmett.tools import requires
from emmett.tools.auth import Auth, AuthUser
from emmett.tools import Mailer
from emmett.sessions import SessionManager
from emmett_rest import REST


app = App(__name__, template_folder='templates')
app.config.url_default_namespace = 'app'

#: mailer configuration
app.config.mailer.sender = "bloggy@emmett.local"
app.config.mailer.suppress = True  # Set to False in production with real SMTP

#: auth configuration
app.config.auth.single_template = True
app.config.auth.registration_verification = False
app.config.auth.hmac_key = "november.5.1955"

#: database configuration
import os
app.config.db.uri = f"sqlite://{os.path.join(os.path.dirname(__file__), 'databases', 'bloggy.db')}"


#: define models
class User(AuthUser):
    # will create "auth_user" table and groups/permissions ones
    has_many('posts', 'comments')


class Post(Model):
    belongs_to('user')
    has_many('comments')

    title = Field()
    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: session.auth.user.id if session.auth else None,
        'date': now
    }
    validation = {
        'title': {'presence': True},
        'text': {'presence': True}
    }
    fields_rw = {
        'user': False,
        'date': False
    }


class Comment(Model):
    belongs_to('user', 'post')

    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: session.auth.user.id if session.auth else None,
        'date': now
    }
    validation = {
        'text': {'presence': True}
    }
    fields_rw = {
        'user': False,
        'post': False,
        'date': False
    }


#: init db, mailer and auth
db = Database(app)
mailer = Mailer(app)
auth = Auth(app, db, user_model=User)
db.define_models(Post, Comment)

#: init REST extension
app.use_extension(REST)
rest_ext = app.ext.REST


#: setup helping function
def setup_admin():
    with db.connection():
        # Check if user already exists
        existing_user = User.where(lambda u: u.email == "doc@emmettbrown.com").select().first()
        if existing_user:
            print("Admin user already exists!")
            return
        
        # create the user
        user = User.create(
            email="doc@emmettbrown.com",
            first_name="Emmett",
            last_name="Brown",
            password="fluxcapacitor"
        )
        
        # create an admin group using raw database access
        existing_group = db(db.auth_groups.role == "admin").select().first()
        if existing_group:
            group_id = existing_group.id
        else:
            group_id = db.auth_groups.insert(role="admin", description="Administrators")
        
        # add user to admins group
        db.auth_memberships.insert(user=user.id, auth_group=group_id)
        db.commit()
        print("Admin user created: doc@emmettbrown.com")


@app.command('setup')
def setup():
    setup_admin()


#: pipeline
app.pipeline = [
    SessionManager.cookies('GreatScott'),
    db.pipe,
    auth.pipe
]


#: exposing functions
@app.route("/")
async def index():
    posts = Post.all().select(orderby=~Post.date)
    return dict(posts=posts)


@app.route("/post/<int:pid>")
async def one(pid):
    def _validate_comment(form):
        # manually set post id in comment form
        form.params.post = pid
    # get post and return 404 if doesn't exist
    post = Post.get(pid)
    if not post:
        abort(404)
    # get comments
    comments = post.comments(orderby=~Comment.date)
    # and create a form for commenting if the user is logged in
    if session.auth:
        form = await Comment.form(onvalidation=_validate_comment)
        if form.accepted:
            redirect(url('one', pid))
    return locals()


@app.route("/new")
@requires(lambda: session.auth, '/')
async def new_post():
    form = await Post.form()
    if form.accepted:
        redirect(url('one', form.params.id))
    return dict(form=form)


auth_routes = auth.module(__name__)


#: REST API configuration
# Create custom REST module for Posts with proper user handling
from emmett_rest import RESTModule

class PostsRESTModule(RESTModule):
    """Custom REST module for Posts that handles user assignment"""
    
    async def create(self):
        """Override create to automatically set user from session"""
        from emmett import request, response
        attrs = await self.parse_params()
        
        # Validate user-provided fields only (without user field)
        errors = self.model.validate(attrs)
        if errors.errors:
            response.status = 422
            return self.error_422(errors.errors, to_dict=False)
        
        # Add user from session after validation
        if session.auth:
            attrs['user'] = session.auth.user.id
        else:
            attrs['user'] = None
        
        for callback in self._before_create_callbacks:
            callback(attrs)
        
        # Use direct insert to bypass fields_rw restrictions
        record_id = db.posts.insert(**attrs)
        r = Post.get(record_id)
        
        for callback in self._after_create_callbacks:
            callback(r)
        
        response.status = 201
        return self.serialize_one(r)

class CommentsRESTModule(RESTModule):
    """Custom REST module for Comments that handles user assignment"""
    
    async def create(self):
        """Override create to automatically set user from session"""
        from emmett import request, response
        attrs = await self.parse_params()
        
        # Validate user-provided fields only (without user field)
        errors = self.model.validate(attrs)
        if errors.errors:
            response.status = 422
            return self.error_422(errors.errors, to_dict=False)
        
        # Add user from session after validation
        if session.auth:
            attrs['user'] = session.auth.user.id
        else:
            attrs['user'] = None
        
        for callback in self._before_create_callbacks:
            callback(attrs)
        
        # Use direct insert to bypass fields_rw restrictions
        record_id = db.comments.insert(**attrs)
        r = Comment.get(record_id)
        
        for callback in self._after_create_callbacks:
            callback(r)
        
        response.status = 201
        return self.serialize_one(r)

# REST endpoints for Posts
# Endpoints:
# - GET /api/posts - List all posts
# - GET /api/posts/:id - Get single post
# - POST /api/posts - Create post (user auto-set from session)
# - PUT /api/posts/:id - Update post
# - PATCH /api/posts/:id - Partial update post
# - DELETE /api/posts/:id - Delete post
posts_api = app.rest_module(
    __name__, 
    'posts_api', 
    Post, 
    url_prefix='api/posts',
    module_class=PostsRESTModule
)

# REST endpoints for Comments
# Endpoints:
# - GET /api/comments - List all comments
# - GET /api/comments/:id - Get single comment
# - POST /api/comments - Create comment (user auto-set from session)
# - PUT /api/comments/:id - Update comment
# - PATCH /api/comments/:id - Partial update comment
# - DELETE /api/comments/:id - Delete comment
comments_api = app.rest_module(
    __name__, 
    'comments_api', 
    Comment, 
    url_prefix='api/comments',
    module_class=CommentsRESTModule
)

# REST endpoints for Users
# Endpoints:
# - GET /api/users - List all users
# - GET /api/users/:id - Get single user
users_api = app.rest_module(
    __name__, 
    'users_api', 
    User, 
    url_prefix='api/users'
)
