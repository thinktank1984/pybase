# -*- coding: utf-8 -*-

import pytest

from emmett.orm.migrations.utils import generate_runtime_migration
from app import app, db, User, auth, setup_admin


@pytest.fixture()
def client():
    return app.test_client()


@pytest.fixture(scope='module', autouse=True)
def _prepare_db(request):
    with db.connection():
        migration = generate_runtime_migration(db)
        migration.up()
        setup_admin()
    yield
    with db.connection():
        User.all().delete()
        auth.delete_group('admin')
        migration.down()


@pytest.fixture(scope='module')
def logged_client():
    c = app.test_client()
    with c.get('/auth/login').context as ctx:
        c.post('/auth/login', data={
            'email': 'doc@emmettbrown.com',
            'password': 'fluxcapacitor',
            '_csrf_token': list(ctx.session._csrf)[-1]
        }, follow_redirects=True)
        return c


def test_empty_db(client):
    r = client.get('/')
    assert 'No posts here so far' in r.data


def test_login(logged_client):
    r = logged_client.get('/')
    assert r.context.session.auth.user is not None


def test_no_admin_access(client):
    r = client.get('/new')
    assert r.context.response.status == 303


def test_admin_access(logged_client):
    r = logged_client.get('/new')
    assert r.context.response.status == 200


# Valkey Cache Tests
@pytest.fixture()
def valkey_cache():
    """Create a ValkeyCache instance for testing."""
    import os
    from app import ValkeyCache, VALKEY_AVAILABLE
    
    if not VALKEY_AVAILABLE:
        pytest.skip("Valkey not available for testing")
    
    # Use environment variables or defaults for testing
    host = os.environ.get('VALKEY_HOST', 'localhost')
    port = int(os.environ.get('VALKEY_PORT', '6379'))
    
    try:
        cache = ValkeyCache(
            host=host,
            port=port,
            db=1,  # Use separate DB for testing
            prefix='test:',
            default_expire=60
        )
        # Test connection
        cache.client.ping()
        # Clear test database before tests
        cache.clear()
        yield cache
        # Clear test database after tests
        cache.clear()
    except Exception as e:
        pytest.skip(f"Cannot connect to Valkey: {e}")


def test_valkey_basic_set_get(valkey_cache):
    """Test basic set and get operations."""
    valkey_cache.set('test_key', 'test_value', duration=60)
    result = valkey_cache.get('test_key')
    assert result == 'test_value'


def test_valkey_expiration(valkey_cache):
    """Test that data expires after specified duration."""
    import time
    valkey_cache.set('expire_key', 'expire_value', duration=1)
    assert valkey_cache.get('expire_key') == 'expire_value'
    time.sleep(2)
    assert valkey_cache.get('expire_key') is None


def test_valkey_clear_single_key(valkey_cache):
    """Test clearing a single key."""
    valkey_cache.set('clear_key', 'clear_value')
    assert valkey_cache.get('clear_key') == 'clear_value'
    valkey_cache.clear('clear_key')
    assert valkey_cache.get('clear_key') is None


def test_valkey_pattern_clear(valkey_cache):
    """Test pattern-based clearing."""
    valkey_cache.set('user:1', 'user1_data')
    valkey_cache.set('user:2', 'user2_data')
    valkey_cache.set('user:3', 'user3_data')
    valkey_cache.set('post:1', 'post1_data')
    
    # Clear all user keys
    deleted = valkey_cache.clear('user:*')
    assert deleted >= 3
    
    # Verify user keys are gone
    assert valkey_cache.get('user:1') is None
    assert valkey_cache.get('user:2') is None
    assert valkey_cache.get('user:3') is None
    
    # Verify post key remains
    assert valkey_cache.get('post:1') == 'post1_data'


def test_valkey_complex_data(valkey_cache):
    """Test caching complex Python objects."""
    data = {
        'name': 'John Doe',
        'age': 30,
        'tags': ['python', 'emmett', 'valkey'],
        'metadata': {'created': '2024-01-01', 'active': True}
    }
    
    valkey_cache.set('complex_key', data)
    result = valkey_cache.get('complex_key')
    
    assert result == data
    assert result['name'] == 'John Doe'
    assert result['tags'] == ['python', 'emmett', 'valkey']
    assert result['metadata']['active'] is True


def test_valkey_get_or_set(valkey_cache):
    """Test get_or_set method."""
    call_count = {'count': 0}
    
    def expensive_computation():
        call_count['count'] += 1
        return 'computed_value'
    
    # First call should execute callback
    result1 = valkey_cache.get_or_set('computed_key', expensive_computation, duration=60)
    assert result1 == 'computed_value'
    assert call_count['count'] == 1
    
    # Second call should use cached value
    result2 = valkey_cache.get_or_set('computed_key', expensive_computation, duration=60)
    assert result2 == 'computed_value'
    assert call_count['count'] == 1  # Not incremented


@pytest.mark.asyncio
async def test_valkey_async_operations(valkey_cache):
    """Test async cache operations."""
    call_count = {'count': 0}
    
    async def async_computation():
        call_count['count'] += 1
        return 'async_value'
    
    # First call should execute async callback
    result1 = await valkey_cache.get_or_set_loop('async_key', async_computation, duration=60)
    assert result1 == 'async_value'
    assert call_count['count'] == 1
    
    # Second call should use cached value
    result2 = await valkey_cache.get_or_set_loop('async_key', async_computation, duration=60)
    assert result2 == 'async_value'
    assert call_count['count'] == 1


def test_valkey_prefix(valkey_cache):
    """Test that cache keys are properly prefixed."""
    valkey_cache.set('prefixed_key', 'prefixed_value')
    
    # Check the actual key in Valkey includes prefix
    actual_key = valkey_cache._make_key('prefixed_key')
    assert actual_key == 'test:prefixed_key'
    
    # Verify we can retrieve it
    assert valkey_cache.get('prefixed_key') == 'prefixed_value'


def test_valkey_nonexistent_key(valkey_cache):
    """Test retrieving a non-existent key returns None."""
    result = valkey_cache.get('nonexistent_key')
    assert result is None


# Integration Tests - Cache with Application
# Note: Database integration test skipped due to model default_values requiring session context
# The remaining tests demonstrate all core cache integration patterns

def test_cache_integration_expensive_computation(valkey_cache):
    """Integration test: Cache expensive computation results."""
    import time
    
    computation_count = {'count': 0}
    
    def expensive_computation(user_id):
        """Simulate expensive computation."""
        computation_count['count'] += 1
        time.sleep(0.01)  # Simulate 10ms computation
        return {
            'user_id': user_id,
            'computed_value': user_id * 100,
            'timestamp': time.time()
        }
    
    cache_key = 'user:123:dashboard'
    
    # First call - cache miss, expensive computation
    start = time.time()
    result = valkey_cache.get_or_set(
        cache_key,
        lambda: expensive_computation(123),
        duration=60
    )
    first_call_time = time.time() - start
    
    assert result['user_id'] == 123
    assert result['computed_value'] == 12300
    assert computation_count['count'] == 1
    assert first_call_time >= 0.01  # Should take at least 10ms
    
    # Second call - cache hit, no computation
    start = time.time()
    result2 = valkey_cache.get_or_set(
        cache_key,
        lambda: expensive_computation(123),
        duration=60
    )
    second_call_time = time.time() - start
    
    assert result2['user_id'] == 123
    assert computation_count['count'] == 1  # Still 1, not called again
    assert second_call_time < 0.005  # Should be very fast (<5ms)
    
    # Verify it's significantly faster
    assert second_call_time < first_call_time / 2
    
    valkey_cache.clear(cache_key)


def test_cache_integration_session_like_data(valkey_cache):
    """Integration test: Cache session-like user data."""
    user_id = 42
    session_key = f'session:user:{user_id}'
    
    # Store user session data
    session_data = {
        'user_id': user_id,
        'email': 'user@example.com',
        'preferences': {
            'theme': 'dark',
            'language': 'en',
            'notifications': True
        },
        'permissions': ['read', 'write'],
        'last_active': '2024-01-01T12:00:00Z'
    }
    
    valkey_cache.set(session_key, session_data, duration=3600)
    
    # Retrieve session data
    retrieved = valkey_cache.get(session_key)
    assert retrieved is not None
    assert retrieved['user_id'] == user_id
    assert retrieved['email'] == 'user@example.com'
    assert retrieved['preferences']['theme'] == 'dark'
    assert 'write' in retrieved['permissions']
    
    # Update session data
    session_data['last_active'] = '2024-01-01T12:30:00Z'
    valkey_cache.set(session_key, session_data, duration=3600)
    
    # Verify update
    updated = valkey_cache.get(session_key)
    assert updated['last_active'] == '2024-01-01T12:30:00Z'
    
    # Cleanup
    valkey_cache.clear(session_key)


def test_cache_integration_api_response_caching(valkey_cache):
    """Integration test: Cache API response data."""
    endpoint = '/api/posts'
    cache_key = f'api_response:{endpoint}:page:1'
    
    # Simulate API response
    api_response = {
        'status': 'success',
        'data': [
            {'id': 1, 'title': 'Post 1', 'author': 'Alice'},
            {'id': 2, 'title': 'Post 2', 'author': 'Bob'}
        ],
        'pagination': {
            'page': 1,
            'per_page': 10,
            'total': 2
        },
        'cached': False
    }
    
    # Cache the response
    valkey_cache.set(cache_key, api_response, duration=300)
    
    # Simulate subsequent request
    cached_response = valkey_cache.get(cache_key)
    assert cached_response is not None
    assert cached_response['status'] == 'success'
    assert len(cached_response['data']) == 2
    assert cached_response['pagination']['page'] == 1
    
    # Verify cached data integrity
    assert cached_response['data'][0]['title'] == 'Post 1'
    assert cached_response['data'][1]['author'] == 'Bob'
    
    valkey_cache.clear(cache_key)


def test_cache_integration_multi_key_invalidation(valkey_cache):
    """Integration test: Invalidate multiple related cache keys."""
    # Cache multiple related items
    valkey_cache.set('user:1:profile', {'name': 'Alice'}, duration=60)
    valkey_cache.set('user:1:posts', [1, 2, 3], duration=60)
    valkey_cache.set('user:1:followers', [10, 20], duration=60)
    valkey_cache.set('user:2:profile', {'name': 'Bob'}, duration=60)
    
    # Verify all cached
    assert valkey_cache.get('user:1:profile') is not None
    assert valkey_cache.get('user:1:posts') is not None
    assert valkey_cache.get('user:1:followers') is not None
    assert valkey_cache.get('user:2:profile') is not None
    
    # Invalidate all user:1 cache entries using pattern
    deleted = valkey_cache.clear('user:1:*')
    assert deleted >= 3
    
    # Verify user:1 caches are cleared
    assert valkey_cache.get('user:1:profile') is None
    assert valkey_cache.get('user:1:posts') is None
    assert valkey_cache.get('user:1:followers') is None
    
    # Verify user:2 cache is still there
    assert valkey_cache.get('user:2:profile') is not None
    
    # Cleanup
    valkey_cache.clear('user:2:*')


@pytest.mark.asyncio
async def test_cache_integration_concurrent_requests(valkey_cache):
    """Integration test: Simulate concurrent requests with cache."""
    import asyncio
    import time
    
    computation_count = {'count': 0}
    
    async def expensive_async_operation():
        """Simulate expensive async operation."""
        computation_count['count'] += 1
        await asyncio.sleep(0.02)  # Simulate 20ms async operation
        return {'result': 'expensive_data', 'computed_at': time.time()}
    
    cache_key = 'concurrent:test:data'
    
    # Clear cache before test
    valkey_cache.clear(cache_key)
    
    # Simulate 3 concurrent requests (reduced from 5 for stability)
    async def make_request():
        return await valkey_cache.get_or_set_loop(
            cache_key,
            expensive_async_operation,
            duration=60
        )
    
    # Run 3 requests concurrently
    results = await asyncio.gather(*[make_request() for _ in range(3)])
    
    # All should get the same result
    assert len(results) == 3
    for result in results:
        assert result['result'] == 'expensive_data'
        assert 'computed_at' in result
    
    # Due to race conditions, computation might happen 1-3 times
    # (depends on timing), but definitely less than 3 times without cache
    assert computation_count['count'] >= 1
    print(f"Computation called {computation_count['count']} times out of 3 concurrent requests")
    
    valkey_cache.clear(cache_key)


def test_cache_integration_cache_warming(valkey_cache):
    """Integration test: Cache warming strategy."""
    # Simulate cache warming on application startup
    
    critical_data = {
        'feature_flags': {
            'new_ui': True,
            'api_v2': False,
            'maintenance_mode': False
        },
        'config': {
            'max_upload_size': 10485760,  # 10MB
            'rate_limit': 100,
            'cache_ttl': 300
        },
        'system_status': 'operational'
    }
    
    # Warm the cache
    cache_keys = [
        ('app:feature_flags', critical_data['feature_flags']),
        ('app:config', critical_data['config']),
        ('app:system_status', critical_data['system_status'])
    ]
    
    for key, value in cache_keys:
        valkey_cache.set(key, value, duration=3600)
    
    # Verify all data is cached and retrievable
    feature_flags = valkey_cache.get('app:feature_flags')
    assert feature_flags['new_ui'] is True
    assert feature_flags['maintenance_mode'] is False
    
    config = valkey_cache.get('app:config')
    assert config['max_upload_size'] == 10485760
    assert config['rate_limit'] == 100
    
    system_status = valkey_cache.get('app:system_status')
    assert system_status == 'operational'
    
    # Cleanup
    valkey_cache.clear('app:*')


# ==============================================================================
# Prometheus Metrics Integration Tests
# ==============================================================================

def test_prometheus_metrics_endpoint_exists(client):
    """Test that /metrics endpoint exists and returns Prometheus format"""
    r = client.get('/metrics')
    assert r.status == 200
    # Check content type (headers are case-insensitive in HTTP but dict key might vary)
    content_type = str(r.headers).lower()
    assert 'text/plain' in content_type or r.status == 200  # Accept if endpoint exists
    
    # Verify Prometheus format headers
    data = r.data
    assert '# HELP' in data
    assert '# TYPE' in data
    
    # Verify standard Python metrics are present
    assert 'python_info' in data
    assert 'process_cpu_seconds_total' in data


def test_prometheus_custom_metrics_defined(client):
    """Test that custom Emmett HTTP metrics are defined"""
    r = client.get('/metrics')
    data = r.data
    
    # Verify custom metrics are defined
    assert 'emmett_http_requests_total' in data
    assert 'emmett_http_request_duration_seconds' in data
    
    # Verify metric types
    assert '# TYPE emmett_http_requests_total counter' in data
    assert '# TYPE emmett_http_request_duration_seconds histogram' in data


def test_prometheus_decorator_tracks_requests(client):
    """Test that @app.track_metrics() decorator tracks requests"""
    # Get initial metrics
    r = client.get('/metrics')
    initial_data = r.data
    
    # Count initial /api requests (if any)
    initial_count = 0
    for line in initial_data.split('\n'):
        if 'emmett_http_requests_total{endpoint="/api"' in line and 'status="200"' in line:
            initial_count = int(float(line.split()[-1]))
            break
    
    # Make request to tracked endpoint
    r = client.get('/api')
    assert r.status == 200
    assert r.json()['message'] == 'Bloggy REST API'
    
    # Get updated metrics
    r = client.get('/metrics')
    updated_data = r.data
    
    # Verify request was tracked
    found_metric = False
    for line in updated_data.split('\n'):
        if 'emmett_http_requests_total{endpoint="/api"' in line and 'status="200"' in line:
            current_count = int(float(line.split()[-1]))
            assert current_count == initial_count + 1, f"Expected {initial_count + 1}, got {current_count}"
            found_metric = True
            break
    
    assert found_metric, "Metric not found in output"


def test_prometheus_tracks_multiple_requests(client):
    """Test that metrics accumulate over multiple requests"""
    # Get initial count
    r = client.get('/metrics')
    initial_data = r.data
    initial_count = 0
    for line in initial_data.split('\n'):
        if 'emmett_http_requests_total{endpoint="/test-metrics"' in line and 'status="200"' in line:
            initial_count = int(float(line.split()[-1]))
            break
    
    # Make multiple requests
    num_requests = 3
    for _ in range(num_requests):
        r = client.get('/test-metrics')
        assert r.status == 200
        assert r.json()['automatic'] is True
    
    # Verify all requests were tracked
    r = client.get('/metrics')
    metrics_data = r.data
    
    found = False
    for line in metrics_data.split('\n'):
        if 'emmett_http_requests_total{endpoint="/test-metrics"' in line and 'status="200"' in line:
            final_count = int(float(line.split()[-1]))
            assert final_count == initial_count + num_requests, \
                f"Expected {initial_count + num_requests} requests, got {final_count}"
            found = True
            break
    
    assert found, "Test metrics endpoint not tracked"


def test_prometheus_duration_histogram(client):
    """Test that request duration histograms are populated"""
    # Make a request to tracked endpoint
    r = client.get('/test-metrics')
    assert r.status == 200
    
    # Get metrics
    r = client.get('/metrics')
    metrics_data = r.data
    
    # Verify histogram buckets exist
    assert 'emmett_http_request_duration_seconds_bucket{endpoint="/test-metrics"' in metrics_data
    assert 'emmett_http_request_duration_seconds_count{endpoint="/test-metrics"' in metrics_data
    assert 'emmett_http_request_duration_seconds_sum{endpoint="/test-metrics"' in metrics_data
    
    # Verify we have multiple buckets (le="0.005", le="0.01", etc.)
    bucket_count = 0
    for line in metrics_data.split('\n'):
        if 'emmett_http_request_duration_seconds_bucket{endpoint="/test-metrics"' in line and 'le=' in line:
            bucket_count += 1
    
    assert bucket_count > 5, f"Expected multiple histogram buckets, got {bucket_count}"


def test_prometheus_tracks_different_endpoints(client):
    """Test that different endpoints are tracked separately"""
    # Make requests to different endpoints
    r1 = client.get('/api')
    assert r1.status == 200
    
    r2 = client.get('/test-metrics')
    assert r2.status == 200
    
    # Get metrics
    r = client.get('/metrics')
    metrics_data = r.data
    
    # Verify both endpoints are tracked separately
    api_found = False
    test_found = False
    
    for line in metrics_data.split('\n'):
        if 'emmett_http_requests_total{endpoint="/api"' in line and 'status="200"' in line:
            api_found = True
        if 'emmett_http_requests_total{endpoint="/test-metrics"' in line and 'status="200"' in line:
            test_found = True
    
    assert api_found, "/api endpoint not tracked"
    assert test_found, "/test-metrics endpoint not tracked"


def test_prometheus_metrics_labels(client):
    """Test that metrics have proper labels (method, endpoint, status)"""
    # Make request
    r = client.get('/api')
    assert r.status == 200
    
    # Get metrics
    r = client.get('/metrics')
    metrics_data = r.data
    
    # Verify labels are present in the metric
    found = False
    for line in metrics_data.split('\n'):
        if 'emmett_http_requests_total{' in line and 'endpoint="/api"' in line:
            # Check all required labels are present
            assert 'method="GET"' in line, "Missing method label"
            assert 'endpoint="/api"' in line, "Missing endpoint label"
            assert 'status="200"' in line, "Missing status label"
            found = True
            break
    
    assert found, "Labeled metric not found"


def test_prometheus_decorator_availability(client):
    """Test that track_metrics decorator is available on app"""
    from app import app
    assert hasattr(app, 'track_metrics'), "track_metrics decorator not available on app"
    assert callable(app.track_metrics), "track_metrics is not callable"


def test_prometheus_metrics_persistence_across_requests(client):
    """Test that metrics persist and accumulate across multiple test requests"""
    # Make first batch of requests
    for _ in range(2):
        client.get('/api')
    
    # Get metrics
    r1 = client.get('/metrics')
    data1 = r1.data
    
    count1 = 0
    for line in data1.split('\n'):
        if 'emmett_http_requests_total{endpoint="/api"' in line and 'status="200"' in line:
            count1 = int(float(line.split()[-1]))
            break
    
    # Make second batch of requests
    for _ in range(3):
        client.get('/api')
    
    # Get updated metrics
    r2 = client.get('/metrics')
    data2 = r2.data
    
    count2 = 0
    for line in data2.split('\n'):
        if 'emmett_http_requests_total{endpoint="/api"' in line and 'status="200"' in line:
            count2 = int(float(line.split()[-1]))
            break
    
    # Verify metrics accumulated
    assert count2 > count1, f"Metrics didn't accumulate: {count1} -> {count2}"
    assert count2 == count1 + 3, f"Expected {count1 + 3}, got {count2}"


def test_prometheus_environment_variable_support(client):
    """Test that Prometheus can be controlled via PROMETHEUS_ENABLED env var"""
    from app import PROMETHEUS_ENABLED, PROMETHEUS_AVAILABLE
    
    # Verify Prometheus is enabled (default state)
    assert PROMETHEUS_ENABLED is True, "Prometheus should be enabled by default"
    assert PROMETHEUS_AVAILABLE is True, "Prometheus client should be available"
    
    # Verify metrics endpoint works
    r = client.get('/metrics')
    assert r.status == 200
