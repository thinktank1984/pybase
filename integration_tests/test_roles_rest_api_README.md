# REST API Integration Tests for Role System

## Overview

This test suite provides comprehensive REST API integration tests for the User Role System. All tests follow the **NO MOCKING** policy and use real HTTP requests, real database operations, and real authorization checks.

## Test File

**File**: `integration_tests/test_roles_rest_api.py`

## What is Tested

### Role REST API (`/api/roles`)

1. **List Roles** (`GET /api/roles`)
   - Admin can list all roles
   - Regular users may have limited access
   - Unauthenticated requests may be denied

2. **Get Role** (`GET /api/roles/<id>`)
   - Admin can view specific role details
   - Returns role with ID, name, description

3. **Create Role** (`POST /api/roles`)
   - Admin can create new roles via JSON payload
   - Validates required fields
   - Returns created role with ID

4. **Update Role** (`PUT /api/roles/<id>`)
   - Admin can update role description
   - Changes persist in real database

5. **Delete Role** (`DELETE /api/roles/<id>`)
   - Admin can delete roles
   - Verifies deletion in database

### Permission REST API (`/api/permissions`)

1. **List Permissions** (`GET /api/permissions`)
   - Admin can list all permissions
   - Returns seeded permissions (post.create, user.manage, etc.)

2. **Get Permission** (`GET /api/permissions/<id>`)
   - Admin can view specific permission details
   - Returns resource, action, scope fields

3. **Create Permission** (`POST /api/permissions`)
   - Admin can create custom permissions
   - Auto-generates permission name from resource.action

4. **Delete Permission** (`DELETE /api/permissions/<id>`)
   - DISABLED for safety (returns 403/405)
   - Permissions should be managed via seeding

### Role-Permission Association

1. **Assign Permission to Role**
   - Tests direct database assignment
   - Verifies associations persist

2. **User Inherits Permissions**
   - Tests user with role gets role's permissions
   - Verifies permission checking works

### Authorization Tests

1. **Unauthenticated Access**
   - Tests accessing APIs without login
   - Verifies proper 401/403 responses

2. **Regular User Access**
   - Tests non-admin user accessing role APIs
   - Verifies permission restrictions

3. **Admin User Access**
   - Tests admin user has full CRUD access
   - All operations succeed

### Bulk Operations

1. **Multiple Roles CRUD**
   - Creates multiple roles via API
   - Updates all roles
   - Deletes all roles
   - Verifies each step in database

## Test Fixtures

### Database Setup

- **`_prepare_db`**: Module-scoped fixture that:
  - Drops all existing tables
  - Runs migrations to create tables
  - Seeds default roles and permissions
  - Cleans up after all tests

### User Fixtures

- **`admin_user`**: Creates user with admin role
- **`regular_user`**: Creates user with no special roles
- **`logged_admin_client`**: Test client logged in as admin
- **`logged_regular_client`**: Test client logged in as regular user

### Client Fixture

- **`client`**: Unauthenticated test client for HTTP requests

## Running the Tests

### Using Docker (Recommended)

```bash
# Run all REST API tests
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_roles_rest_api.py -v

# Run specific test
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_roles_rest_api.py -k test_rest_api_create_role -v

# Run with coverage
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_roles_rest_api.py --cov=runtime --cov-report=term-missing -v
```

### Using Local Environment

```bash
# From project root
uv run pytest integration_tests/test_roles_rest_api.py -v

# With coverage
uv run pytest integration_tests/test_roles_rest_api.py --cov=runtime -v
```

## Test Coverage

These tests cover:

- ✅ All CRUD operations on roles via REST API
- ✅ All CRUD operations on permissions via REST API
- ✅ Role-permission associations
- ✅ User-role assignments
- ✅ Permission inheritance
- ✅ Authorization checks (admin vs regular user vs unauthenticated)
- ✅ Validation errors
- ✅ Bulk operations
- ✅ Database state verification after each operation

## Expected Results

**Roles API:**
- Admin users: Full CRUD access (200/201 responses)
- Regular users: Limited or no access (403 responses for write operations)
- Unauthenticated: No access (401/403 responses)

**Permissions API:**
- Admin users: Read + Create + Update (200/201 responses)
- Delete operations: Disabled for safety (403/405 responses)

## NO MOCKING Policy

🚨 **CRITICAL**: All tests in this file follow the **NO MOCKING** policy:

- ❌ NO `unittest.mock` or `pytest-mock`
- ❌ NO fake responses or simulated data
- ✅ ONLY real HTTP requests via test client
- ✅ ONLY real database operations
- ✅ ONLY actual state verification

Every test makes real HTTP requests to REST API endpoints and verifies actual database changes.

## Integration with Existing Tests

This test suite complements:

- **`test_roles_integration.py`**: Direct database and model testing
- **`test_roles.py`**: Import and validation tests
- **`test_auto_ui.py`**: Auto-generated UI testing

Together, these provide complete coverage of:
1. Database layer (test_roles_integration.py)
2. REST API layer (test_roles_rest_api.py) ← **This file**
3. UI layer (test_auto_ui.py)

## API Endpoints Reference

### Roles API

| Method | Endpoint | Description | Admin Only |
|--------|----------|-------------|------------|
| GET | `/api/roles` | List all roles | ✓ |
| GET | `/api/roles/<id>` | Get role by ID | ✓ |
| POST | `/api/roles` | Create new role | ✓ |
| PUT | `/api/roles/<id>` | Update role | ✓ |
| DELETE | `/api/roles/<id>` | Delete role | ✓ |

### Permissions API

| Method | Endpoint | Description | Admin Only |
|--------|----------|-------------|------------|
| GET | `/api/permissions` | List all permissions | ✓ |
| GET | `/api/permissions/<id>` | Get permission by ID | ✓ |
| POST | `/api/permissions` | Create permission | ✓ |
| PUT | `/api/permissions/<id>` | Update permission | ✓ |
| DELETE | `/api/permissions/<id>` | ❌ Disabled | N/A |

## Example Test Output

```
integration_tests/test_roles_rest_api.py::test_rest_api_list_roles_as_admin PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_get_role_by_id PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_create_role PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_update_role PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_delete_role PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_role_validation_error PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_list_permissions PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_get_permission_by_id PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_create_permission PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_delete_permission_forbidden PASSED
integration_tests/test_roles_rest_api.py::test_assign_permission_to_role PASSED
integration_tests/test_roles_rest_api.py::test_user_inherits_permissions_from_role_via_api PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_roles_unauthorized_without_login PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_roles_forbidden_for_regular_user PASSED
integration_tests/test_roles_rest_api.py::test_rest_api_create_role_forbidden_for_regular_user PASSED
integration_tests/test_roles_rest_api.py::test_role_with_permissions_list PASSED
integration_tests/test_roles_rest_api.py::test_multiple_roles_crud_operations PASSED

========================= 17 passed in 3.45s =========================
```

## Troubleshooting

### Tests Fail with "404 Not Found"

**Cause**: REST APIs may not be registered in `models/__init__.py`

**Fix**: Ensure `setup_all()` calls role and permission API setup:

```python
def setup_all(app):
    from .role.api import setup_rest_api as role_api_setup
    from .permission.api import setup_rest_api as perm_api_setup
    
    apis = {
        'roles_api': role_api_setup(app),
        'permissions_api': perm_api_setup(app),
        # ... other APIs
    }
    return apis
```

### Tests Fail with "401 Unauthorized"

**Cause**: Authentication not working in test client

**Fix**: Ensure `logged_admin_client` fixture properly logs in via POST request

### Tests Fail with "UNIQUE constraint failed"

**Cause**: Test data not properly cleaned up

**Fix**: Tests use `unique_email()` and `unique_name()` helpers to avoid conflicts

## See Also

- [Role System Implementation Guide](../openspec/changes/add-user-role-system/proposal.md)
- [Integration Testing Philosophy](../agents.md#integration-testing-philosophy)
- [NO MOCKING Policy](../documentation/NO_MOCKING_ENFORCEMENT.md)

