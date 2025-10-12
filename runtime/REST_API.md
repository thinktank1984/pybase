# REST API Documentation

## Overview

This application now includes a complete REST API powered by the `emmett-rest` extension. The API provides full CRUD operations for Posts, Comments, and Users.

## Base URL

```
http://localhost:8081/api
```

## Authentication

Currently, the API endpoints are accessible without authentication. For production use, consider adding authentication middleware to protect sensitive operations.

---

## Posts API

### List All Posts

**Endpoint:** `GET /api/posts`

**Response:**
```json
{
  "data": [
    {
      "title": "Post Title",
      "text": "Post content"
    }
  ],
  "meta": {
    "object": "list",
    "has_more": false,
    "total_objects": 2
  }
}
```

### Get Single Post

**Endpoint:** `GET /api/posts/:id`

**Example:** `GET /api/posts/1`

**Response:**
```json
{
  "title": "Post Title",
  "text": "Post content"
}
```

### Create Post

**Endpoint:** `POST /api/posts`

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "New Post",
  "text": "Post content"
}
```

**Note:** Due to model field restrictions (`fields_rw`), the `user` field is automatically set from the session. For API-only access, you may need to adjust the model configuration.

### Update Post (Full)

**Endpoint:** `PUT /api/posts/:id`

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "Updated Title",
  "text": "Updated content"
}
```

**Response:**
```json
{
  "title": "Updated Title",
  "text": "Updated content"
}
```

### Update Post (Partial)

**Endpoint:** `PATCH /api/posts/:id`

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "New Title Only"
}
```

**Response:**
```json
{
  "title": "New Title Only",
  "text": "Original content"
}
```

### Delete Post

**Endpoint:** `DELETE /api/posts/:id`

**Response:** 204 No Content

---

## Comments API

### List All Comments

**Endpoint:** `GET /api/comments`

**Response:**
```json
{
  "data": [
    {
      "text": "Comment text"
    }
  ],
  "meta": {
    "object": "list",
    "has_more": false,
    "total_objects": 1
  }
}
```

### Get Single Comment

**Endpoint:** `GET /api/comments/:id`

**Example:** `GET /api/comments/1`

### Create Comment

**Endpoint:** `POST /api/comments`

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{
  "text": "New comment",
  "post": 1
}
```

### Update Comment

**Endpoint:** `PUT /api/comments/:id` or `PATCH /api/comments/:id`

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{
  "text": "Updated comment"
}
```

### Delete Comment

**Endpoint:** `DELETE /api/comments/:id`

---

## Users API

### List All Users

**Endpoint:** `GET /api/users`

**Response:**
```json
{
  "data": [
    {
      "email": "doc@emmettbrown.com",
      "password": "pbkdf2(2000,20,sha512)$...",
      "first_name": "Emmett",
      "last_name": "Brown"
    }
  ],
  "meta": {
    "object": "list",
    "has_more": false,
    "total_objects": 2
  }
}
```

**⚠️ Security Note:** The password hashes are currently exposed. For production, create a custom serializer that excludes sensitive fields.

### Get Single User

**Endpoint:** `GET /api/users/:id`

**Example:** `GET /api/users/1`

**Response:**
```json
{
  "email": "doc@emmettbrown.com",
  "password": "pbkdf2(2000,20,sha512)$...",
  "first_name": "Emmett",
  "last_name": "Brown"
}
```

**Note:** The Users API is read-only for security. Create/Update/Delete operations are disabled.

---

## Testing the API

### Using cURL

```bash
# List posts
curl http://localhost:8081/api/posts

# Get single post
curl http://localhost:8081/api/posts/1

# Update post
curl -X PUT http://localhost:8081/api/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title","text":"New content"}'

# Partial update
curl -X PATCH http://localhost:8081/api/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Just the title"}'

# Delete post
curl -X DELETE http://localhost:8081/api/posts/1
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8081/api"

# List all posts
response = requests.get(f"{base_url}/posts")
posts = response.json()

# Get single post
response = requests.get(f"{base_url}/posts/1")
post = response.json()

# Update post
response = requests.put(
    f"{base_url}/posts/1",
    json={"title": "Updated", "text": "Content"}
)

# Create comment
response = requests.post(
    f"{base_url}/comments",
    json={"text": "Great post!", "post": 1}
)
```

### Using httpx (async)

```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # List posts
        response = await client.get("http://localhost:8081/api/posts")
        print(response.json())
        
        # Update post
        response = await client.put(
            "http://localhost:8081/api/posts/1",
            json={"title": "Updated", "text": "Content"}
        )
        print(response.json())

asyncio.run(test_api())
```

---

## Response Format

All list endpoints follow this format:

```json
{
  "data": [...],
  "meta": {
    "object": "list",
    "has_more": false,
    "total_objects": 10
  }
}
```

Single resource endpoints return just the object:

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

Error responses include an `errors` object:

```json
{
  "errors": {
    "field": "Error message"
  }
}
```

---

## Known Issues & Improvements

### 1. POST Operations Require User Field

Due to model `fields_rw` restrictions, creating new posts/comments via API requires the user field to be writable. Consider:

**Option A:** Make user field writable for API
```python
# In app.py, modify fields_rw:
fields_rw = {
    'user': True,  # Allow API to set user
    'date': False
}
```

**Option B:** Use custom REST module methods to handle user assignment

### 2. Password Hashes Exposed in User API

The Users API currently exposes password hashes. Fix by creating a custom serializer:

```python
# TODO: Add custom serializer for User model
users_api = app.rest_module(
    __name__, 
    'users_api', 
    User, 
    url_prefix='api/users'
)

# Override to exclude password field
```

### 3. No Authentication on API Endpoints

Consider adding authentication middleware for production:

```python
from emmett.tools import requires

# Add to REST modules pipeline
api.pipeline = [RequireAuth()]
```

### 4. No Rate Limiting

For production APIs, implement rate limiting to prevent abuse.

---

## Implementation Details

### Extension Used

- **emmett-rest** version 1.6.0
- Provides automatic CRUD endpoint generation
- Handles JSON serialization/deserialization
- Validates input against model validations

### Code Location

REST API configuration is in `/runtime/app.py` starting at line ~169:

```python
posts_api = app.rest_module(__name__, 'posts_api', Post, url_prefix='api/posts')
comments_api = app.rest_module(__name__, 'comments_api', Comment, url_prefix='api/comments')
users_api = app.rest_module(__name__, 'users_api', User, url_prefix='api/users')
```

### Models

The API uses the existing Emmett ORM models:
- `Post` - Blog posts
- `Comment` - Comments on posts
- `User` - Application users (AuthUser)

All models support Active Record patterns as of Emmett 2.4+.

---

## Next Steps

1. **Add Authentication:** Implement JWT or session-based auth for API
2. **Custom Serializers:** Hide sensitive fields (passwords, internal IDs)
3. **Add Pagination:** Implement proper pagination for large datasets
4. **API Versioning:** Consider `/api/v1/` prefix for future compatibility
5. **CORS Support:** Add CORS headers for frontend consumption
6. **API Documentation:** Consider adding Swagger/OpenAPI documentation
7. **Rate Limiting:** Implement request throttling
8. **API Testing:** Create comprehensive test suite for API endpoints

---

## Resources

- [emmett-rest GitHub](https://github.com/emmett-framework/rest)
- [Emmett Framework Documentation](https://emmett.sh/docs)
- [Emmett ORM Documentation](../emmett_documentation/docs/orm/)

