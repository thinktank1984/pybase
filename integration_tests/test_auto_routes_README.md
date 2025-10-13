# Integration Tests for Automatic Route Generation

## Overview

This test suite verifies the automatic route generation feature (`auto_routes`) for BaseModel subclasses. All tests follow the repository's **STRICT NO MOCKING POLICY**.

## Test Coverage

### 1. Basic Route Generation (6 tests)
- ✅ List view route generation
- ✅ Detail view route generation
- ✅ Create routes (form + submission)
- ✅ Update routes (form + submission)
- ✅ Delete routes (confirmation + submission)
- ✅ Real database state verification

### 2. REST API Generation (5 tests)
- ✅ REST list endpoint (`GET /api/model`)
- ✅ REST detail endpoint (`GET /api/model/:id`)
- ✅ REST create endpoint (`POST /api/model`)
- ✅ REST update endpoint (`PUT /api/model/:id`)
- ✅ REST delete endpoint (`DELETE /api/model/:id`)

### 3. Configuration Options (3 tests)
- ✅ Custom `url_prefix` configuration
- ✅ `enabled_actions` filtering
- ✅ Disabled models (`auto_routes=False`)

### 4. Permission Integration (2 tests)
- ✅ Permission enforcement on protected routes
- ✅ Public routes work without authentication

### 5. Error Handling (2 tests)
- ✅ 404 for non-existent records
- ✅ Validation error handling

### 6. Backwards Compatibility (2 tests)
- ✅ Manual `setup()` takes precedence
- ✅ Models without `auto_routes` still work

### 7. Integration Features (3 tests)
- ✅ Model validation integration
- ✅ Default values integration
- ✅ OpenAPI registration

### 8. Complete Workflow (1 test)
- ✅ End-to-end CRUD workflow with real HTTP + database

**Total: 25+ integration tests**

## Test Models

The test suite uses dedicated test models to avoid interfering with production models:

- **TestProduct**: Simple model with `auto_routes = True`
- **TestCategory**: Configured model with custom URL prefix and limited actions
- **TestArticle**: Model with permission configuration
- **TestPrivateData**: Model with `auto_routes = False` (should have no routes)

## NO MOCKING POLICY Compliance

### ✅ What We Do (Legal)
- **Real database operations**: SQLite in-memory database
- **Real HTTP requests**: Via `app.test_client()`
- **Real state verification**: Query database after operations
- **Real validation**: Emmett form validation system
- **Real sessions**: Test client session management

### ❌ What We Don't Do (Illegal)
- ❌ **No mocks**: No `unittest.mock`, `Mock()`, `MagicMock()`
- ❌ **No stubs**: No fake database responses
- ❌ **No test doubles**: No simulated HTTP responses
- ❌ **No in-memory fakes**: We use real SQLite, not fake storage

## Running the Tests

```bash
# Run all auto_routes tests
./run_tests.sh integration_tests/test_auto_routes.py

# Run with verbose output
./run_tests.sh integration_tests/test_auto_routes.py -v

# Run specific test
./run_tests.sh integration_tests/test_auto_routes.py -k test_auto_routes_generates_list_route

# Run with coverage
./run_tests.sh integration_tests/test_auto_routes.py --cov=runtime --cov-report=term-missing

# In Docker (recommended)
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_auto_routes.py -v
```

## Test Pattern

Every test follows this pattern:

```python
def test_something(test_client, test_db):
    """Test description."""
    
    # 1. Setup - Create real database records
    with test_db.connection():
        record = TestModel.create(field='value')
        record_id = record.id
        test_db.commit()
    
    # 2. Action - Make real HTTP request
    response = test_client.get(f'/path/{record_id}')
    
    # 3. Assert - Verify real response
    assert response.status == 200
    assert b'expected content' in response.data
    
    # 4. Verify - Check real database state
    with test_db.connection():
        record = TestModel.get(record_id)
        assert record.field == 'value'
```

## Fixtures

- **test_app**: Fresh Emmett app with test models and auto_routes enabled
- **test_client**: HTTP test client for making requests
- **test_db**: Database connection for verification
- **setup_test_db**: Auto-run fixture that creates/drops tables per test

## Validation

The test file is validated for NO MOCKING compliance:

```bash
# Validate no mocking is used
python integration_tests/validate_no_mocking.py integration_tests/test_auto_routes.py
```

Expected output: `✅ No mocking detected`

## Success Criteria

All tests must:
- ✅ Use real database operations
- ✅ Use real HTTP requests
- ✅ Verify actual database state changes
- ✅ Pass without any mocks, stubs, or fakes
- ✅ Test complete request/response cycle
- ✅ Achieve >90% code coverage

## Integration with CI/CD

These tests should be run:
- ✅ Before every commit
- ✅ In CI/CD pipeline
- ✅ Before merging PRs
- ✅ As part of test suite coverage

## Troubleshooting

### Test Failures

**Import errors**: Ensure `base_model.py` has `auto_routes` implementation
**Route not found (404)**: Check model discovery is running in test_app fixture
**Database errors**: Verify test database setup/teardown in fixtures
**Permission errors**: Check test authentication helpers

### Adding New Tests

1. Follow the NO MOCKING policy
2. Use real database operations
3. Use real HTTP requests via test_client
4. Verify database state after operations
5. Add descriptive docstrings
6. Group related tests in sections

## Related Documentation

- `/documentation/NO_MOCKING_ENFORCEMENT.md` - Repository policy
- `/openspec/changes/add-automatic-model-routes/` - Feature specification
- `/documentation/base_model_guide.md` - BaseModel usage guide
- `/runtime/models/README.md` - Model organization patterns

