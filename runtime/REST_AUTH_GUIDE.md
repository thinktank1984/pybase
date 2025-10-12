# REST API Authentication Guide for Emmett

## Authentication Flow Options

### Option 1: Session-Based Authentication (Cookie-Based)

This is what you're currently trying to use. The flow is:

```
1. POST /auth/login with credentials
2. Receive session cookie
3. Include cookie in subsequent API requests
4. Session validates user automatically
```

**Issue:** The `fields_rw` restriction in your models prevents the REST module from setting the `user` field, even when using `db.posts.insert()` directly.

### Option 2: JWT Token Authentication (Recommended for APIs)

Better for REST APIs because:
- Stateless (no session storage needed)
- Works across domains/services
- Explicit authorization header
- Better for mobile/SPA clients

### Option 3: API Key Authentication

Simple authentication using API keys in headers.

---

## Current Problem

Your models have `fields_rw` restrictions:

```python
fields_rw = {
    'user': False,  # This prevents ANY write to user field
    'date': False
}
```

Even `db.posts.insert(user=2, ...)` will fail because `fields_rw` is enforced at the **table level**, not just the model level.

---

## Solutions

### Solution 1: Remove fields_rw Restriction (Simplest)

**Change the models to allow user field writes:**

```python
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
    # Remove or modify fields_rw
    # fields_rw = {
    #     'date': False  # Keep date read-only if needed
    # }
```

### Solution 2: Use Computed Fields

Make `user` a computed field that's set automatically:

```python
class Post(Model):
    # Don't use belongs_to, use a regular field
    user = Field.int()
    has_many('comments')

    title = Field()
    text = Field.text()
    date = Field.datetime()

    default_values = {
        'user': lambda: session.auth.user.id if session.auth else None,
        'date': now
    }
```

### Solution 3: Bypass REST and Use Custom Endpoints

Create custom endpoints that handle the logic:

```python
from emmett.tools import service

@app.route('/api/posts', methods=['POST'])
@service.json
async def create_post():
    if not session.auth:
        abort(401, "Authentication required")
    
    data = await request.body_params
    post_id = Post.create(
        title=data.title,
        text=data.text,
        user=session.auth.user.id
    )
    
    if post_id.errors:
        response.status = 422
        return {'errors': post_id.errors}
    
    return Post.get(post_id.id).as_dict()
```

---

## Recommended Implementation

Here's a complete working solution using **Session Authentication + Modified Models**:

### Step 1: Update Models (Remove fields_rw)

```python
class Post(Model):
    belongs_to('user')
    has_many('comments')

    title = Field()
    text = Field.text()
    date = Field.datetime()

    default_values = {
        'date': now
    }
    validation = {
        'title': {'presence': True},
        'text': {'presence': True},
        'user': {'presence': True}  # Require user
    }

class Comment(Model):
    belongs_to('user', 'post')

    text = Field.text()
    date = Field.datetime()

    default_values = {
        'date': now
    }
    validation = {
        'text': {'presence': True},
        'user': {'presence': True},
        'post': {'presence': True}
    }
```

### Step 2: Create Custom REST Modules

```python
from emmett_rest import RESTModule
from emmett import response

class AuthenticatedRESTModule(RESTModule):
    """Base REST module that requires authentication"""
    
    def _check_auth(self):
        """Check if user is authenticated"""
        if not session.auth:
            abort(401, "Authentication required")
        return session.auth.user.id

class PostsRESTModule(AuthenticatedRESTModule):
    """REST module for Posts with automatic user assignment"""
    
    async def create(self):
        """Create a post with authenticated user"""
        user_id = self._check_auth()
        attrs = await self.parse_params()
        attrs['user'] = user_id
        
        # Create using model's create method
        result = self.model.create(**attrs)
        
        if result.errors:
            response.status = 422
            return {'errors': result.errors}
        
        response.status = 201
        return self.serialize_one(self.model.get(result.id))
    
    async def update(self, rid):
        """Update - only owner or admin can update"""
        user_id = self._check_auth()
        post = self.model.get(rid)
        
        if not post:
            abort(404)
        
        if post.user != user_id:
            abort(403, "You can only update your own posts")
        
        return await super().update(rid)
    
    async def delete(self, rid):
        """Delete - only owner or admin can delete"""
        user_id = self._check_auth()
        post = self.model.get(rid)
        
        if not post:
            abort(404)
        
        if post.user != user_id:
            abort(403, "You can only delete your own posts")
        
        return await super().delete(rid)

class CommentsRESTModule(AuthenticatedRESTModule):
    """REST module for Comments with automatic user assignment"""
    
    async def create(self):
        """Create a comment with authenticated user"""
        user_id = self._check_auth()
        attrs = await self.parse_params()
        attrs['user'] = user_id
        
        result = self.model.create(**attrs)
        
        if result.errors:
            response.status = 422
            return {'errors': result.errors}
        
        response.status = 201
        return self.serialize_one(self.model.get(result.id))
```

### Step 3: Register REST Modules

```python
posts_api = app.rest_module(
    __name__, 
    'posts_api', 
    Post, 
    url_prefix='api/posts',
    module_class=PostsRESTModule
)

comments_api = app.rest_module(
    __name__, 
    'comments_api', 
    Comment, 
    url_prefix='api/comments',
    module_class=CommentsRESTModule
)
```

---

## Testing the API

### 1. Login and Get Session Cookie

```bash
curl -v -X POST http://localhost:8081/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=a@a.com&password=1234567890" \
  -c cookies.txt
```

### 2. Create Post with Authentication

```bash
curl -b cookies.txt \
  -X POST http://localhost:8081/api/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"My Post","text":"Post content"}' | jq
```

### 3. Create Comment

```bash
curl -b cookies.txt \
  -X POST http://localhost:8081/api/comments \
  -H "Content-Type: application/json" \
  -d '{"text":"Great post!","post":1}' | jq
```

### 4. Update Post

```bash
curl -b cookies.txt \
  -X PUT http://localhost:8081/api/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","text":"Updated content"}' | jq
```

### 5. Delete Post

```bash
curl -b cookies.txt \
  -X DELETE http://localhost:8081/api/posts/1
```

---

## Using Python requests Library

```python
import requests

# Create session to maintain cookies
session = requests.Session()

# Login
login_data = {
    'email': 'a@a.com',
    'password': '1234567890'
}
response = session.post(
    'http://localhost:8081/auth/login',
    data=login_data
)
print(f"Login status: {response.status_code}")

# Create post (session automatically includes cookies)
post_data = {
    'title': 'My API Post',
    'text': 'Created via Python requests'
}
response = session.post(
    'http://localhost:8081/api/posts',
    json=post_data
)
print(f"Create post: {response.json()}")

# List all posts
response = session.get('http://localhost:8081/api/posts')
posts = response.json()
print(f"Posts: {posts}")
```

---

## JWT Token Authentication (Alternative)

For a more robust API, consider implementing JWT:

```python
from emmett import request
import jwt
import datetime

class JWTAuth:
    SECRET = "your-secret-key"
    
    @staticmethod
    def create_token(user_id):
        """Create JWT token for user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, JWTAuth.SECRET, algorithm='HS256')
    
    @staticmethod
    def verify_token():
        """Verify JWT token from Authorization header"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            abort(401, "Missing or invalid authorization header")
        
        token = auth_header.replace('Bearer ', '')
        try:
            payload = jwt.decode(token, JWTAuth.SECRET, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            abort(401, "Token expired")
        except jwt.InvalidTokenError:
            abort(401, "Invalid token")

# Login endpoint that returns JWT
@app.route('/api/auth/login', methods=['POST'])
@service.json
async def api_login():
    data = await request.body_params
    user = User.get(email=data.email)
    
    if user and auth.verify_password(user.password, data.password):
        token = JWTAuth.create_token(user.id)
        return {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }
    
    abort(401, "Invalid credentials")

# Use in REST modules
class JWTAuthRESTModule(RESTModule):
    def _check_auth(self):
        return JWTAuth.verify_token()
```

### Using JWT with curl:

```bash
# Login and get token
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"a@a.com","password":"1234567890"}' | jq -r '.token')

# Use token in requests
curl -H "Authorization: Bearer $TOKEN" \
  -X POST http://localhost:8081/api/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"My Post","text":"Content"}' | jq
```

---

## Summary

**Your current issue:** `fields_rw = {'user': False}` prevents ALL writes to the user field.

**Quick fix:** Remove `fields_rw` for the user field in your models.

**Best practices:**
1. Use session authentication for web apps
2. Use JWT for APIs, mobile apps, SPAs
3. Validate user ownership before update/delete
4. Return appropriate HTTP status codes (401, 403, 422)
5. Don't expose password hashes in API responses

Choose the solution that fits your needs!

