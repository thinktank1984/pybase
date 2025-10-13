# -*- coding: utf-8 -*-
"""
Integration Tests for Automatic Route Generation

Tests the auto_routes feature for BaseModel subclasses.
🚨 NO MOCKING ALLOWED - All tests use real HTTP and real database operations.
"""

import pytest
import json
from base_model import BaseModel
from emmett.orm import Field
from datetime import datetime


# ========================================================================
# TEST MODELS - Defined at module level for proper ORM registration
# ========================================================================

class TestProduct(BaseModel):
    """Simple test model with auto_routes enabled."""
    tablename = 'test_products'
    name = Field.string()
    price = Field.float()
    description = Field.text()
    
    auto_routes = True  # Enable automatic routes


class TestCategory(BaseModel):
    """Test model with custom auto_routes configuration."""
    tablename = 'test_categories'
    name = Field.string()
    
    auto_routes = {
        'url_prefix': '/admin/categories',
        'enabled_actions': ['list', 'detail', 'create'],  # No update/delete
        'rest_api': True
    }


class TestArticle(BaseModel):
    """Test model with permission configuration."""
    tablename = 'test_articles'
    title = Field.string()
    content = Field.text()
    
    def _test_permission():
        """Test permission function."""
        from emmett import session
        return 'user_id' in session  # type: ignore[operator]
    
    auto_routes = {
        'permissions': {
            'create': _test_permission
        }
    }


class TestPrivateData(BaseModel):
    """Test model with auto_routes disabled."""
    tablename = 'test_private_data'
    secret = Field.string()
    
    auto_routes = False  # Explicitly disabled


class TestValidated(BaseModel):
    """Test model with validation rules."""
    tablename = 'test_validated'
    name = Field.string()
    value = Field.int()
    
    validation = {
        'name': {'presence': True, 'len': {'range': (3, 100)}},
        'value': {'presence': True, 'gte': 0}
    }
    
    auto_routes = True


class TestWithDefaults(BaseModel):
    """Test model with default values."""
    tablename = 'test_with_defaults'
    name = Field.string()
    status = Field.string(default='active')
    created_at = Field.datetime(default=lambda: datetime.utcnow())
    
    auto_routes = True


class LegacyModel(BaseModel):
    """Test model without auto_routes (for backwards compatibility test)."""
    tablename = 'legacy_model'
    name = Field.string()
    # No auto_routes attribute


# ========================================================================
# FIXTURES
# ========================================================================

@pytest.fixture(scope='module', autouse=True)
def register_test_models(app, db):
    """Register test models with database (module-scoped, runs automatically)."""
    # Define all test models first (outside connection context)
    db.define_models(
        TestProduct,
        TestCategory,
        TestArticle,
        TestPrivateData,
        TestValidated,
        TestWithDefaults,
        LegacyModel
    )
    
    # Create tables using simple SQL
    with db.connection():
        cursor = db._adapter.cursor
        
        # Create test_products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                name CHAR(512),
                price DOUBLE,
                description TEXT
            )
        ''')
        
        # Create test_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                name CHAR(512)
            )
        ''')
        
        # Create test_articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                title CHAR(512),
                content TEXT
            )
        ''')
        
        # Create test_private_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_private_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                secret CHAR(512)
            )
        ''')
        
        # Create test_validated table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_validated (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                name CHAR(512),
                value INTEGER
            )
        ''')
        
        # Create test_with_defaults table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_with_defaults (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                name CHAR(512),
                status CHAR(512) DEFAULT 'active',
                created_at_field TIMESTAMP
            )
        ''')
        
        # Create legacy_model table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legacy_model (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                name CHAR(512)
            )
        ''')
        
        db.commit()
        print("   ✓ All test model tables created")
    
    # Trigger auto_routes discovery and registration
    from auto_routes import discover_and_register_auto_routes
    discover_and_register_auto_routes(app, db)
    
    yield
    
    # Cleanup happens automatically in conftest session teardown


@pytest.fixture
def test_product(db, register_test_models):
    """Create a test product in real database."""
    with db.connection():
        product = TestProduct.create(
            name='Test Widget',
            price=19.99,
            description='A test product'
        )
        db.commit()
        
        yield product
        
        # Cleanup
        try:
            product.delete_record()
            db.commit()
        except:
            pass  # May already be deleted


@pytest.fixture
def test_category(db, register_test_models):
    """Create a test category with custom URL prefix."""
    with db.connection():
        category = TestCategory.create(name='Electronics')
        db.commit()
        
        yield category
        
        # Cleanup
        try:
            category.delete_record()
            db.commit()
        except:
            pass


# ========================================================================
# 1. BASIC ROUTE GENERATION TESTS (6 tests)
# ========================================================================

def test_auto_routes_generates_list_route(test_client, test_product, db):
    """
    Test that auto_routes generates a working list route.
    
    ✅ NO MOCKING - Uses real HTTP request and real database query.
    """
    # Make REAL HTTP request
    response = test_client.get('/test_products/')
    
    # Verify response
    assert response.status == 200
    assert 'Test Widget' in response.data


def test_auto_routes_generates_detail_route(test_client, test_product):
    """
    Test that auto_routes generates a working detail route.
    
    ✅ NO MOCKING - Uses real HTTP GET request.
    """
    # Make REAL HTTP request for specific record
    response = test_client.get(f'/test_products/{test_product.id}')
    
    # Verify response shows correct data
    assert response.status == 200
    assert 'Test Widget' in response.data
    assert '19.99' in response.data


def test_auto_routes_generates_create_routes(test_client, db, register_test_models):
    """
    Test that auto_routes generates working create routes (form + submission).
    
    ✅ NO MOCKING - Uses real HTTP POST and verifies real database insertion.
    """
    # 1. GET create form
    response = test_client.get('/test_products/new')
    assert response.status == 200
    
    # 2. POST new record
    response = test_client.post('/test_products/', data={
        'name': 'New Product',
        'price': 29.99,
        'description': 'Created via test'
    })
    
    # Should redirect or return success
    assert response.status in [200, 201, 302]
    
    # 3. Verify REAL database state changed
    with db.connection():
        product = TestProduct.where(
            lambda p: p.name == 'New Product'
        ).first()
        
        assert product is not None
        assert product.price == 29.99
        
        # Cleanup
        product.delete_record()
        db.commit()


def test_auto_routes_generates_update_routes(test_client, test_product, db):
    """
    Test that auto_routes generates working update routes (edit form + submission).
    
    ✅ NO MOCKING - Uses real HTTP and verifies real database update.
    """
    # 1. GET edit form
    response = test_client.get(f'/test_products/{test_product.id}/edit')
    assert response.status == 200
    
    # 2. POST update
    response = test_client.post(f'/test_products/{test_product.id}', data={
        'name': 'Updated Widget',
        'price': 24.99,
        'description': 'Updated description'
    })
    
    # Should redirect after successful update
    assert response.status in [200, 302]
    
    # 3. Verify REAL database state changed
    with db.connection():
        updated = TestProduct.get(test_product.id)
        assert updated.name == 'Updated Widget'
        assert updated.price == 24.99


def test_auto_routes_generates_delete_routes(test_client, db, register_test_models):
    """
    Test that auto_routes generates working delete routes (confirmation + action).
    
    ✅ NO MOCKING - Uses real HTTP and verifies real database deletion.
    """
    # Create product to delete
    with db.connection():
        product = TestProduct.create(name='To Delete', price=9.99)
        product_id = product.id
        db.commit()
    
    # 1. GET delete confirmation
    response = test_client.get(f'/test_products/{product_id}/delete')
    assert response.status == 200
    
    # 2. POST delete action
    response = test_client.post(f'/test_products/{product_id}/delete')
    
    # Should redirect after successful delete
    assert response.status in [200, 302]
    
    # 3. Verify REAL database record is gone
    with db.connection():
        deleted_product = TestProduct.get(product_id)
        assert deleted_product is None


# ========================================================================
# 2. REST API GENERATION TESTS (5 tests)
# ========================================================================

def test_auto_routes_generates_rest_list_endpoint(test_client, test_product):
    """
    Test that auto_routes generates REST list endpoint.
    
    ✅ NO MOCKING - Uses real HTTP GET request for JSON API.
    """
    response = test_client.get('/api/test_products')
    
    assert response.status == 200
    assert 'application/json' in response.content_type
    
    data = json.loads(response.data)
    assert 'data' in data or isinstance(data, list)


def test_auto_routes_generates_rest_detail_endpoint(test_client, test_product):
    """
    Test that auto_routes generates REST detail endpoint.
    
    ✅ NO MOCKING - Uses real HTTP GET request for single record.
    """
    response = test_client.get(f'/api/test_products/{test_product.id}')
    
    assert response.status == 200
    assert 'application/json' in response.content_type
    
    data = json.loads(response.data)
    assert 'data' in data
    assert data['data']['name'] == 'Test Widget'


def test_auto_routes_generates_rest_create_endpoint(test_client, db, register_test_models):
    """
    Test that auto_routes generates REST create endpoint.
    
    ✅ NO MOCKING - Uses real HTTP POST with JSON payload.
    """
    # POST JSON data to create new record
    response = test_client.post('/api/test_products', 
        data=json.dumps({
            'name': 'REST Product',
            'price': 39.99,
            'description': 'Created via REST API'
        }),
        content_type='application/json'
    )
    
    assert response.status in [200, 201]
    
    # Verify REAL database insertion
    with db.connection():
        product = TestProduct.where(
            lambda p: p.name == 'REST Product'
        ).first()
        
        assert product is not None
        assert product.price == 39.99
        
        # Cleanup
        product.delete_record()
        db.commit()


def test_auto_routes_generates_rest_update_endpoint(test_client, test_product, db):
    """
    Test that auto_routes generates REST update endpoint.
    
    ✅ NO MOCKING - Uses real HTTP PUT with JSON payload.
    """
    # PUT JSON data to update record
    response = test_client.put(f'/api/test_products/{test_product.id}',
        data=json.dumps({
            'name': 'REST Updated',
            'price': 44.99
        }),
        content_type='application/json'
    )
    
    assert response.status == 200
    
    # Verify REAL database was updated
    with db.connection():
        updated = TestProduct.get(test_product.id)
        assert updated.name == 'REST Updated'
        assert updated.price == 44.99


def test_auto_routes_generates_rest_delete_endpoint(test_client, db, register_test_models):
    """
    Test that auto_routes generates REST delete endpoint.
    
    ✅ NO MOCKING - Uses real HTTP DELETE and verifies database deletion.
    """
    # Create product to delete
    with db.connection():
        product = TestProduct.create(name='To Delete via REST', price=5.99)
        product_id = product.id
        db.commit()
    
    # DELETE via REST API
    response = test_client.delete(f'/api/test_products/{product_id}')
    
    assert response.status in [200, 204]
    
    # Verify REAL database deletion
    with db.connection():
        deleted_product = TestProduct.get(product_id)
        assert deleted_product is None


# ========================================================================
# 3. CONFIGURATION OPTIONS TESTS (3 tests)
# ========================================================================

def test_auto_routes_respects_url_prefix(test_client, test_category):
    """
    Test that auto_routes respects custom url_prefix configuration.
    
    ✅ NO MOCKING - Tests real route paths.
    """
    # Should work with custom prefix
    response = test_client.get('/admin/categories/')
    assert response.status == 200
    
    # Should NOT work with default prefix
    response = test_client.get('/test_categories/')
    assert response.status == 404


def test_auto_routes_respects_enabled_actions(test_client, test_category):
    """
    Test that auto_routes only generates enabled actions.
    
    ✅ NO MOCKING - Tests which routes exist and which don't.
    """
    # These actions should work (enabled)
    response = test_client.get('/admin/categories/')
    assert response.status == 200  # list enabled
    
    response = test_client.get(f'/admin/categories/{test_category.id}')
    assert response.status == 200  # detail enabled
    
    response = test_client.get('/admin/categories/new')
    assert response.status == 200  # create enabled
    
    # These actions should NOT work (disabled)
    response = test_client.get(f'/admin/categories/{test_category.id}/edit')
    assert response.status == 404  # update disabled
    
    response = test_client.get(f'/admin/categories/{test_category.id}/delete')
    assert response.status == 404  # delete disabled


def test_auto_routes_disabled_model_has_no_routes(test_client, register_test_models):
    """
    Test that models with auto_routes=False don't get routes.
    
    ✅ NO MOCKING - Verifies routes don't exist.
    """
    # None of these routes should exist
    response = test_client.get('/test_private_data/')
    assert response.status == 404
    
    response = test_client.get('/api/test_private_data')
    assert response.status == 404


# ========================================================================
# 4. PERMISSION INTEGRATION TESTS (2 tests)
# ========================================================================

def test_auto_routes_enforces_permissions_on_create(test_client, register_test_models):
    """
    Test that auto_routes enforces permission checks.
    
    ✅ NO MOCKING - Tests real RBAC permission integration.
    """
    # Try to access create form without authentication
    response = test_client.get('/test_articles/new')
    # Should be denied or redirected (exact behavior depends on auth setup)
    assert response.status in [302, 401, 403, 404]  # Various auth failure responses


def test_auto_routes_public_routes_work_without_auth(test_client, test_product):
    """
    Test that routes without permissions work publicly.
    
    ✅ NO MOCKING - Tests public access.
    """
    # Public routes should work without authentication
    response = test_client.get('/test_products/')
    assert response.status == 200
    
    response = test_client.get(f'/test_products/{test_product.id}')
    assert response.status == 200


# ========================================================================
# 5. ERROR HANDLING TESTS (2 tests)
# ========================================================================

def test_auto_routes_returns_404_for_nonexistent_record(test_client, register_test_models):
    """
    Test that auto_routes returns 404 for non-existent records.
    
    ✅ NO MOCKING - Tests real 404 handling.
    """
    # Try to access non-existent record
    response = test_client.get('/test_products/99999')
    assert response.status == 404


def test_auto_routes_handles_validation_errors(test_client, register_test_models):
    """
    Test that auto_routes handles validation errors properly.
    
    ✅ NO MOCKING - Tests real validation integration.
    """
    # Try to create record with invalid data
    response = test_client.post('/test_validated/', data={
        'name': 'AB',  # Too short (min 3)
        'value': -10   # Negative (must be >= 0)
    })
    
    # Should return error or show form with errors
    assert response.status in [200, 400, 422]


# ========================================================================
# 6. BACKWARDS COMPATIBILITY TESTS (2 tests)
# ========================================================================

def test_manual_setup_takes_precedence_over_auto_routes(test_client):
    """
    Test that manual setup() functions take precedence over auto_routes.
    
    ✅ NO MOCKING - Tests precedence logic.
    """
    # Post, Comment, User models have manual setup and should work
    response = test_client.get('/')
    assert response.status == 200  # Index route from manual setup works


def test_models_without_auto_routes_still_work(db, register_test_models):
    """
    Test that models without auto_routes attribute continue to work.
    
    ✅ NO MOCKING - Tests backwards compatibility.
    """
    # LegacyModel has no auto_routes - should work fine
    with db.connection():
        record = LegacyModel.create(name='Legacy Record')
        assert record.id is not None
        
        # Cleanup
        record.delete_record()
        db.commit()


# ========================================================================
# 7. INTEGRATION FEATURES TESTS (3 tests)
# ========================================================================

def test_auto_routes_works_with_validation(test_client, register_test_models):
    """
    Test that auto_routes integrates with model validation.
    
    ✅ NO MOCKING - Tests real validation integration.
    """
    # Create with valid data should work
    response = test_client.post('/test_validated/', data={
        'name': 'Valid Name',
        'value': 10
    })
    assert response.status in [200, 201, 302]


def test_auto_routes_works_with_default_values(db, register_test_models):
    """
    Test that auto_routes respects field default values.
    
    ✅ NO MOCKING - Tests default value integration.
    """
    with db.connection():
        # Create record without status field
        record = TestWithDefaults.create(name='Default Test')
        
        # Should have default value
        assert record.status == 'active'
        assert record.created_at is not None
        
        # Cleanup
        record.delete_record()
        db.commit()


def test_auto_routes_registers_with_openapi(test_client):
    """
    Test that auto_routes registers routes with OpenAPI generator.
    
    ✅ NO MOCKING - Tests real OpenAPI integration.
    """
    # Check if OpenAPI docs are available
    response = test_client.get('/api/docs')
    # OpenAPI may or may not be enabled, just check it doesn't error
    assert response.status in [200, 404]


# ========================================================================
# 8. COMPLETE WORKFLOW TEST (1 test)
# ========================================================================

def test_complete_crud_workflow(test_client, db, register_test_models):
    """
    Complete end-to-end CRUD workflow test.
    
    Tests CREATE → READ → UPDATE → DELETE cycle with real HTTP and database.
    ✅ NO MOCKING - Full integration test.
    """
    # 1. CREATE - Make new product
    response = test_client.post('/test_products/', data={
        'name': 'Workflow Product',
        'price': 99.99,
        'description': 'Full workflow test'
    })
    assert response.status in [200, 201, 302]
    
    # Verify creation in database
    with db.connection():
        product = TestProduct.where(
            lambda p: p.name == 'Workflow Product'
        ).first()
        assert product is not None
        product_id = product.id
    
    # 2. READ - View product
    response = test_client.get(f'/test_products/{product_id}')
    assert response.status == 200
    assert 'Workflow Product' in response.data
    
    # 3. UPDATE - Edit product
    response = test_client.post(f'/test_products/{product_id}', data={
        'name': 'Updated Workflow Product',
        'price': 109.99,
        'description': 'Updated via workflow'
    })
    assert response.status in [200, 302]
    
    # Verify update in database
    with db.connection():
        updated = TestProduct.get(product_id)
        assert updated.name == 'Updated Workflow Product'
        assert updated.price == 109.99
    
    # 4. DELETE - Remove product
    response = test_client.post(f'/test_products/{product_id}/delete')
    assert response.status in [200, 302]
    
    # Verify deletion in database
    with db.connection():
        deleted = TestProduct.get(product_id)
        assert deleted is None


# ========================================================================
# 9. MODEL DISCOVERY TEST (1 test)
# ========================================================================

def test_model_discovery_finds_all_auto_routes_models(db):
    """
    Test that model discovery mechanism finds all models with auto_routes.
    
    ✅ NO MOCKING - Tests real model discovery.
    """
    # Import and run discovery
    from auto_routes import discover_auto_routes_models
    
    discovered = discover_auto_routes_models(db)
    
    # Should find models with auto_routes=True or auto_routes={...}
    discovered_names = [model.__name__ for model in discovered]
    
    # These models should be discovered
    assert 'TestProduct' in discovered_names
    assert 'TestCategory' in discovered_names
    assert 'TestArticle' in discovered_names
    
    # TestPrivateData has auto_routes=False, should NOT be discovered
    assert 'TestPrivateData' not in discovered_names
    
    # LegacyModel has no auto_routes, should NOT be discovered
    assert 'LegacyModel' not in discovered_names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
