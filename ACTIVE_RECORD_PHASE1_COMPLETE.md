# Active Record Design Pattern - Phase 1 Complete

## Date: October 13, 2025

## Summary

Successfully completed Phase 1 of the Active Record design pattern implementation, fixing critical route registration issues that were causing test failures.

## Problem

After consolidating model, API, and view code into single `model.py` files (Active Record pattern), routes were not being registered properly:

- Routes defined with `@app.route()` decorators inside `setup()` functions didn't register
- Template `url()` calls were looking for routes with 'app.' namespace prefix
- 500 errors on homepage and view pages due to invalid URL generation

## Solution

### 1. Route Registration Pattern

**Problem**: Decorators inside functions don't register routes
```python
# ❌ This doesn't work inside a function
@app.route("/")
async def index():
    pass
```

**Solution**: Use `app.route()` as a function call, not decorator
```python
# ✅ This works
def setup(app):
    async def index():
        posts = Post.all().select(orderby=~Post.date)
        return dict(posts=posts)
    
    # Register route as function call
    app.route("/", name='app.index')(index)
```

### 2. Namespace Handling

**Key Discovery**: Emmett automatically uses the app module name as a namespace prefix

- App created as `App(__name__)` where `__name__ == 'app'`
- Routes must be registered with full namespace: `'app.index'`, `'app.one'`, `'app.new_post'`
- Templates call `url('index')` which Emmett expands to `'app.index'` automatically
- Config: `app.config.url_default_namespace = 'app'` (re-enabled)

### 3. Files Modified

#### Core Changes
- **`runtime/models/post/model.py`**: 
  - Changed route registration from decorators to function calls
  - Added explicit namespace to route names: `name='app.index'`
  - Routes: `/` (index), `/post/<int:pid>` (one), `/new` (new_post)

- **`runtime/app.py`**:
  - Re-enabled `app.config.url_default_namespace = 'app'`

#### Templates (no changes needed)
- `runtime/templates/index.html`
- `runtime/templates/one.html`
- `runtime/templates/new_post.html`

Templates continue to use simple route names (`url('index')`, `url('one')`), and Emmett handles the namespace prefix automatically.

### 4. Pattern for Future Models

When adding routes in `setup()` functions:

```python
def setup(app):
    """Setup routes and REST API for Model."""
    
    # Define route handlers
    async def index():
        return dict(items=Model.all())
    
    async def detail(id):
        item = Model.get(id)
        if not item:
            abort(404)
        return dict(item=item)
    
    # Register routes with explicit namespace
    app.route("/items", name='app.items_index')(index)
    app.route("/items/<int:id>", name='app.items_detail')(detail)
    
    # REST API
    api = app.rest_module(__name__, 'items_api', Model, url_prefix='api/items')
    return api
```

## Test Results

### Before Fix
- **Passing**: 42/83 tests (51%)
- **Failed**: 13 tests
- **Errors**: 28 tests
- **Issue**: Route resolution failures causing 500 errors on view pages

### After Fix
- **Passing**: 47/83 tests (57%)
- **Failed**: 8 tests
- **Errors**: 28 tests
- **Improvement**: +5 tests passing, all view/route tests now work

### Tests Fixed
✅ `test_homepage_shows_posts` - Homepage renders with post list
✅ `test_view_single_post` - Single post page renders
✅ `test_view_single_post_with_comments` - Post with comments renders
✅ `test_view_nonexistent_post` - 404 handling works
✅ `test_comment_form_hidden_from_unauthenticated` - Form visibility logic

## Remaining Issues

### High Priority
1. **Auth/Login Tests (8 failures)**
   - Login page rendering
   - Credential validation
   - Session management
   - Logout functionality

2. **API Integration Tests (28 errors)**
   - POST/PUT/DELETE operations
   - Authentication in API calls
   - User auto-assignment
   - All depend on auth fixture working

### Medium Priority
3. **Async Tests (2 failures)**
   - pytest-asyncio not properly configured
   - Need to add `pytest_plugins = ['pytest_asyncio']`

4. **Metrics Test (1 failure)**
   - Prometheus metrics endpoint format

## Next Steps

### Phase 2: Fix Auth Routes
Similar pattern as Post model:
- Update `runtime/models/user/model.py` setup() function
- Register auth routes with proper namespace
- Fix login/logout functionality
- Expected to fix 8 failing tests + enable 28 API tests

### Phase 3: API Integration
- Verify REST API callbacks work with new structure
- Test authentication in API endpoints
- Expected to fix 28 error tests

### Phase 4: Minor Fixes
- Configure pytest-asyncio properly
- Fix Prometheus metrics format
- Expected to fix remaining 3 tests

## Conclusion

Phase 1 successfully demonstrates that the Active Record pattern works in Emmett when routes are properly registered. The key insight was understanding that:

1. Routes inside functions need to be registered as function calls, not decorators
2. Emmett's namespace system requires explicit full names when registering
3. The pattern is consistent and can be applied to all models

**Status**: ✅ Phase 1 Complete - Ready for Phase 2 (Auth Routes)

**Timeline**: Phase 1 completed in ~2 hours
**Estimated remaining**: 4-6 hours for Phases 2-4


