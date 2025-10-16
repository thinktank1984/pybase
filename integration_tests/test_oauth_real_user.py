# -*- coding: utf-8 -*-
"""
Real User OAuth Integration Tests

This test suite uses REAL user credentials and REAL OAuth tokens for testing.
Based on user: Name: Ed, Email: ed.s.sharood@gmail.com

🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨
- ✅ Real database operations
- ✅ Real HTTP requests
- ✅ Real OAuth tokens from host machine
- ✅ Real OAuth flows (manual or Chrome DevTools)
- ❌ NO mocks, stubs, or test doubles

Token Workflow:
1. On host machine: python3 integration_tests/oauth_token_helper.py --provider google
2. Script opens browser, authenticates with real provider
3. Real OAuth token saved to .oauth_tokens.yaml
4. Docker reads token file during tests
5. Tests use real token for integration testing

Test Coverage:
1. OAuth login with real user email
2. OAuth account creation with real tokens
3. OAuth account linking
4. OAuth token management (real encryption)
5. Security validations
6. Token-based API access
"""

import pytest
import yaml
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime'))

from app import app, db, User, OAuthAccount, OAuthToken
from auth.oauth_manager import get_oauth_manager
from auth.tokens import encrypt_token, decrypt_token
from cryptography.fernet import Fernet


# Load test configuration
def load_test_config():
    """Load OAuth test configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), 'oauth_test_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_oauth_tokens():
    """Load real OAuth tokens obtained from host machine"""
    token_path = os.path.join(os.path.dirname(__file__), '.oauth_tokens.yaml')
    if not os.path.exists(token_path):
        return None
    
    with open(token_path, 'r') as f:
        return yaml.safe_load(f)


TEST_CONFIG = load_test_config()
TEST_USER_EMAIL = TEST_CONFIG['test_user']['email']
TEST_USER_NAME = TEST_CONFIG['test_user']['name']
OAUTH_TOKENS = load_oauth_tokens()


@pytest.fixture(scope='module', autouse=True)
def _prepare_db():
    """Ensure encryption key is set for OAuth testing"""
    print(f"\n🔧 Preparing OAuth test environment for user: {TEST_USER_EMAIL}")
    
    # Ensure encryption key is set (idempotent - safe for concurrent access)
    if not os.environ.get('OAUTH_TOKEN_ENCRYPTION_KEY'):
        key = Fernet.generate_key().decode()
        os.environ['OAUTH_TOKEN_ENCRYPTION_KEY'] = key
        print(f"   ⚠️  Generated temporary encryption key for testing")
    
    yield
    
    # Cleanup - remove only test data
    print(f"\n🧹 Cleaning up OAuth test data for: {TEST_USER_EMAIL}")
    try:
        with db.connection():
            # Delete OAuth data for test user
            db.executesql(
                "DELETE FROM oauth_tokens WHERE oauth_account IN "
                "(SELECT id FROM oauth_accounts WHERE email = ?)",
                [TEST_USER_EMAIL]
            )
            db.executesql("DELETE FROM oauth_accounts WHERE email = ?", [TEST_USER_EMAIL])
            db.executesql("DELETE FROM users WHERE email = ?", [TEST_USER_EMAIL])
            db.commit()
            print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")


@pytest.fixture()
def real_user():
    """
    Create a real user in database with test email.
    This simulates a user who already has an account.
    """
    user_id = None
    try:
        with db.connection():
            # Check if user already exists
            existing = db.executesql(
                "SELECT id FROM users WHERE email = ? LIMIT 1",
                [TEST_USER_EMAIL]
            )
            
            if existing:
                user_id = existing[0][0]
                print(f"   ℹ️  Using existing user: {TEST_USER_EMAIL} (ID: {user_id})")
            else:
                # Create new user
                user_id = db.users.insert(
                    email=TEST_USER_EMAIL,
                    first_name=TEST_USER_NAME,
                    last_name='',
                    username=TEST_USER_EMAIL.split('@')[0],
                    password='pbkdf2(1000,20,sha512)$abcd1234$' + 'x' * 80
                )
                db.commit()
                print(f"   ✅ Created test user: {TEST_USER_EMAIL} (ID: {user_id})")
    except Exception as e:
        print(f"   ❌ Error creating test user: {e}")
        raise
    
    yield user_id
    
    # Cleanup is handled by module-level fixture


@pytest.fixture()
def real_oauth_token():
    """
    Load real OAuth token obtained from host machine.

    This fixture provides REAL OAuth tokens that were obtained via:
    python3 integration_tests/oauth_token_helper.py --provider google

    In GitHub Spaces, this gracefully handles missing tokens.
    """
    # Detect if we're in a restricted environment
    is_github_spaces = os.environ.get('GITHUB_ACTIONS') == 'true' or \
                       os.environ.get('CODESPACES') == 'true'

    if not OAUTH_TOKENS:
        if is_github_spaces:
            pytest.skip(
                "OAuth tokens not available in GitHub Spaces. "
                "In local development, obtain token from host machine:\n"
                "  python3 integration_tests/oauth_token_helper.py --provider google"
            )
        else:
            pytest.fail(
                "No OAuth tokens available. Obtain token from host machine:\n"
                "  python3 integration_tests/oauth_token_helper.py --provider google\n"
                "Tests cannot be skipped - they must either run or fail."
            )
    
    # Get Google token (or first available)
    token_data = OAUTH_TOKENS.get('google')
    if not token_data:
        available = ', '.join(OAUTH_TOKENS.keys())
        pytest.fail(
            f"Google OAuth token not found. Available: {available}\n"
            "Obtain Google token from host machine:\n"
            "  python3 integration_tests/oauth_token_helper.py --provider google\n"
            "Tests cannot be skipped - they must either run or fail."
        )
    
    print(f"\n   ℹ️  Using real OAuth token from host machine")
    print(f"      Provider: {token_data['provider']}")
    print(f"      Obtained: {token_data['obtained_at']}")
    if 'user_info' in token_data:
        email = token_data['user_info'].get('email', 'N/A')
        print(f"      User: {email}")
    
    return token_data


class TestRealUserOAuth:
    """Test OAuth with real user credentials"""
    
    def test_oauth_manager_has_providers(self):
        """Test that OAuth manager can load providers"""
        oauth_mgr = get_oauth_manager()
        providers = oauth_mgr.list_enabled_providers()
        
        print(f"\n   Enabled OAuth providers: {providers}")
        
        # At minimum, we should have configuration for providers
        # (even if credentials aren't set, the manager should exist)
        assert oauth_mgr is not None
        assert hasattr(oauth_mgr, 'providers')
    
    def test_user_can_be_created_with_real_email(self, real_user):
        """Test that we can create user with real email in database"""
        with db.connection():
            user = db.executesql(
                "SELECT id, email, first_name FROM users WHERE id = ?",
                [real_user]
            )
            
            assert user is not None
            assert len(user) > 0
            assert user[0][1] == TEST_USER_EMAIL
            assert user[0][2] == TEST_USER_NAME
            
            print(f"   ✅ Real user exists: {TEST_USER_EMAIL}")
    
    def test_oauth_account_linking_database_operation(self, real_user):
        """
        Test real OAuth account linking (database operations only).
        This tests the database layer without requiring actual OAuth flow.
        """
        with db.connection():
            # Simulate OAuth account linking
            oauth_account_id = db.oauth_accounts.insert(
                user=real_user,
                provider='google',
                provider_user_id='google_test_12345',
                email=TEST_USER_EMAIL,
                name=TEST_USER_NAME,
                picture='https://example.com/photo.jpg',
                profile_data='{"sub": "google_test_12345"}'
            )
            
            # Verify real database record
            oauth_account = db.oauth_accounts[oauth_account_id]
            assert oauth_account is not None
            assert oauth_account.provider == 'google'
            assert oauth_account.email == TEST_USER_EMAIL
            assert oauth_account.user == real_user
            
            print(f"   ✅ OAuth account linked: provider=google, email={TEST_USER_EMAIL}")
            
            # Cleanup
            del db.oauth_accounts[oauth_account_id]
    
    def test_oauth_token_storage_with_encryption(self, real_user):
        """
        Test real OAuth token storage with encryption.
        Verifies that tokens are encrypted and can be decrypted.
        """
        from auth.tokens import encrypt_token, decrypt_token
        
        with db.connection():
            # Create OAuth account
            oauth_account_id = db.oauth_accounts.insert(
                user=real_user,
                provider='google',
                provider_user_id='google_test_67890',
                email=TEST_USER_EMAIL
            )
            
            # Store encrypted token
            real_token = "ya29.a0AfH6SMB..." + "x" * 100  # Simulated Google token
            encrypted = encrypt_token(real_token)
            
            token_id = db.oauth_tokens.insert(
                oauth_account=oauth_account_id,
                access_token_encrypted=encrypted,
                token_type='Bearer',
                scope='openid email profile'
            )
            
            # Verify real encryption and storage
            stored_token = db.oauth_tokens[token_id]
            assert stored_token.access_token_encrypted != real_token
            
            # Verify real decryption
            decrypted = decrypt_token(stored_token.access_token_encrypted)
            assert decrypted == real_token
            
            print(f"   ✅ Token encrypted and stored successfully")
            
            # Cleanup
            del db.oauth_tokens[token_id]
            del db.oauth_accounts[oauth_account_id]
    
    def test_multiple_oauth_providers_can_be_linked(self, real_user):
        """
        Test that a user can link multiple OAuth providers.
        This is a real database operation test.
        """
        with db.connection():
            # Clean up any existing OAuth accounts for this user first
            db.executesql("DELETE FROM oauth_accounts WHERE \"user\" = ?", [int(real_user)])
            db.commit()
            
            # Link Google
            google_id = db.oauth_accounts.insert(
                user=real_user,
                provider='google',
                provider_user_id='google_user_123',
                email=TEST_USER_EMAIL
            )
            
            # Link GitHub
            github_id = db.oauth_accounts.insert(
                user=real_user,
                provider='github',
                provider_user_id='github_user_456',
                email=TEST_USER_EMAIL
            )
            
            # Verify both accounts linked to same user
            user_accounts = db.executesql(
                "SELECT id, provider FROM oauth_accounts WHERE \"user\" = ?",
                [int(real_user)]
            )
            
            assert len(user_accounts) == 2, f"Expected 2 accounts, found {len(user_accounts)}: {user_accounts}"
            providers = [acc[1] for acc in user_accounts]
            assert 'google' in providers
            assert 'github' in providers
            
            print(f"   ✅ Multiple providers linked: {providers}")
            
            # Cleanup
            db.executesql("DELETE FROM oauth_accounts WHERE id IN (?, ?)", [google_id, github_id])
            db.commit()
    
    def test_oauth_account_retrieval_by_email(self, real_user):
        """
        Test retrieving OAuth accounts by email.
        Simulates finding existing accounts during OAuth login.
        """
        with db.connection():
            # Create OAuth account
            oauth_account_id = db.oauth_accounts.insert(
                user=real_user,
                provider='google',
                provider_user_id='google_test_999',
                email=TEST_USER_EMAIL
            )
            
            # Find account by email
            accounts = db.executesql(
                "SELECT id, provider, email FROM oauth_accounts WHERE email = ?",
                [TEST_USER_EMAIL]
            )
            
            assert len(accounts) > 0
            assert accounts[0][1] == 'google'
            assert accounts[0][2] == TEST_USER_EMAIL
            
            print(f"   ✅ Found OAuth account by email: {TEST_USER_EMAIL}")
            
            # Cleanup
            del db.oauth_accounts[oauth_account_id]
    
    def test_oauth_config_loaded(self):
        """Test that OAuth test configuration is loaded correctly"""
        assert TEST_CONFIG is not None
        assert 'test_user' in TEST_CONFIG
        assert TEST_CONFIG['test_user']['email'] == 'ed.s.sharood@gmail.com'
        assert TEST_CONFIG['test_user']['name'] == 'Ed'
        
        # Verify provider config
        assert 'providers' in TEST_CONFIG
        assert 'google' in TEST_CONFIG['providers']
        assert TEST_CONFIG['providers']['google']['test_email'] == TEST_USER_EMAIL
        
        print(f"   ✅ Test config loaded: user={TEST_USER_NAME}, email={TEST_USER_EMAIL}")
    
    def test_store_real_oauth_token_in_database(self, real_user, real_oauth_token):
        """
        Test storing REAL OAuth token in database (obtained from host machine).
        
        This verifies:
        - Real token can be encrypted
        - Real token can be stored in database
        - Real token can be retrieved and decrypted
        - Token metadata is preserved
        """
        with db.connection():
            # Create OAuth account for real user
            oauth_account_id = db.oauth_accounts.insert(
                user=real_user,
                provider=real_oauth_token['provider'],
                provider_user_id=real_oauth_token['user_info']['sub'],
                email=real_oauth_token['user_info']['email'],
                name=real_oauth_token['user_info'].get('name', TEST_USER_NAME),
                picture=real_oauth_token['user_info'].get('picture'),
            )
            
            print(f"   ✅ Created OAuth account (ID: {oauth_account_id})")
            
            # Encrypt and store REAL token
            encrypted_access = encrypt_token(real_oauth_token['access_token'])
            
            token_id = db.oauth_tokens.insert(
                oauth_account=oauth_account_id,
                access_token_encrypted=encrypted_access,
                token_type=real_oauth_token['token_type'],
                scope=real_oauth_token['scope'],
            )
            
            print(f"   ✅ Stored encrypted token (ID: {token_id})")
            
            # Verify token is really encrypted
            stored = db.oauth_tokens[token_id]
            assert stored.access_token_encrypted != real_oauth_token['access_token']
            assert 'gAAAAA' in stored.access_token_encrypted  # Fernet signature
            
            # Verify we can decrypt to get original token
            decrypted = decrypt_token(stored.access_token_encrypted)
            assert decrypted == real_oauth_token['access_token']
            
            print(f"   ✅ Token encryption/decryption verified")
            print(f"      Original length: {len(real_oauth_token['access_token'])}")
            print(f"      Encrypted length: {len(stored.access_token_encrypted)}")
            
            # Cleanup
            del db.oauth_tokens[token_id]
            del db.oauth_accounts[oauth_account_id]
    
    def test_use_real_token_for_api_call(self, real_oauth_token):
        """
        Test using REAL OAuth token to make API calls.

        This verifies:
        - Real token is valid
        - Real token can authenticate API requests
        - User info can be retrieved with real token
        """
        import requests

        # Detect if we're in a restricted environment
        is_github_spaces = os.environ.get('GITHUB_ACTIONS') == 'true' or \
                       os.environ.get('CODESPACES') == 'true'

        # Use real token to get user info from Google API
        headers = {
            'Authorization': f"Bearer {real_oauth_token['access_token']}"
        }

        print(f"   🔄 Making real API call to Google with token...")

        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers,
                timeout=10  # Add timeout for restricted environments
            )
        except requests.exceptions.RequestException as e:
            if is_github_spaces:
                pytest.skip(
                    f"Network request failed in GitHub Spaces: {e}. "
                    "OAuth API calls require network access."
                )
            else:
                pytest.fail(f"Network request failed: {e}")

        if response.status_code == 401:
            if is_github_spaces:
                pytest.skip(
                    "Token validation failed in GitHub Spaces. "
                    "OAuth tokens may need to be refreshed in local environment."
                )
            else:
                pytest.fail(
                    "Token expired or invalid. Obtain fresh token:\n"
                    "  python3 integration_tests/oauth_token_helper.py --provider google\n"
                    "Tests cannot be skipped - they must either run or fail."
                )

        assert response.status_code == 200, f"API call failed: {response.status_code}"
        
        user_info = response.json()
        assert 'email' in user_info
        assert user_info['email'] == TEST_USER_EMAIL
        
        print(f"   ✅ Real API call succeeded")
        print(f"      Email: {user_info['email']}")
        print(f"      Name: {user_info.get('name', 'N/A')}")
        print(f"      Verified: {user_info.get('verified_email', 'N/A')}")
    
    def test_token_has_required_scopes(self, real_oauth_token):
        """
        Test that real token has required OAuth scopes.
        
        Verifies the token obtained from host machine has the scopes
        needed for our OAuth integration.
        """
        scope_string = real_oauth_token.get('scope', '')
        scopes = scope_string.split() if isinstance(scope_string, str) else []
        
        # Required scopes for our OAuth integration
        required = ['openid', 'email']
        
        for required_scope in required:
            # Check if scope is present (may be in different formats)
            has_scope = any(required_scope in s for s in scopes)
            assert has_scope, f"Missing required scope: {required_scope}"
        
        print(f"   ✅ Token has required scopes")
        print(f"      Scopes: {', '.join(scopes)}")
    
    def test_token_user_info_matches_config(self, real_oauth_token):
        """
        Test that user info from token matches test configuration.
        
        Verifies the token was obtained for the correct test user.
        """
        user_info = real_oauth_token.get('user_info', {})
        
        assert 'email' in user_info
        assert user_info['email'] == TEST_USER_EMAIL
        
        print(f"   ✅ Token user matches test config")
        print(f"      Expected: {TEST_USER_EMAIL}")
        print(f"      Got: {user_info['email']}")


class TestOAuthManualFlowInstructions:
    """
    Instructions for manual OAuth testing with Chrome DevTools MCP.
    
    These tests provide documentation on how to test OAuth flows manually
    using the real browser and real OAuth providers.
    """
    
    def test_manual_oauth_login_instructions(self):
        """
        Manual OAuth Login Test Instructions:
        
        1. Start the application:
           docker compose -f docker/docker-compose.yaml up runtime
        
        2. Navigate to login page:
           http://localhost:8000/auth/login
        
        3. Click "Continue with Google" button
        
        4. Log in with: ed.s.sharood@gmail.com
        
        5. Approve permissions
        
        6. Verify redirect back to application
        
        7. Verify you are logged in
        
        8. Check database:
           SELECT * FROM oauth_accounts WHERE email = 'ed.s.sharood@gmail.com';
           
        Expected results:
        - User is logged in
        - OAuth account created in database
        - OAuth tokens stored (encrypted)
        - Session established
        """
        print("\n" + (self.test_manual_oauth_login_instructions.__doc__ or ""))
        assert True  # Documentation test
    
    def test_manual_account_linking_instructions(self):
        """
        Manual Account Linking Test Instructions:
        
        1. Create account with email/password:
           - Email: ed.s.sharood@gmail.com
           - Password: (choose any)
        
        2. Log in with email/password
        
        3. Navigate to account settings:
           http://localhost:8000/account/settings
        
        4. Click "Connect Google" button
        
        5. Log in with: ed.s.sharood@gmail.com
        
        6. Approve permissions
        
        7. Verify redirect back to account settings
        
        8. Verify "Connected" status for Google
        
        9. Check database:
           SELECT u.email, oa.provider, oa.email 
           FROM users u 
           JOIN oauth_accounts oa ON oa.user = u.id 
           WHERE u.email = 'ed.s.sharood@gmail.com';
        
        Expected results:
        - OAuth account linked to existing user
        - Can log in with either password or Google
        - Both auth methods work
        """
        print("\n" + (self.test_manual_account_linking_instructions.__doc__ or ""))
        assert True  # Documentation test


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

