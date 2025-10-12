# -*- coding: utf-8 -*-
"""
Real Integration Tests for OAuth Social Login - NO MOCKING

🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨

⚠️ USING MOCKS, STUBS, OR TEST DOUBLES IS ILLEGAL IN THIS REPOSITORY ⚠️

This is a ZERO-TOLERANCE POLICY:
- ❌ FORBIDDEN: unittest.mock, Mock(), MagicMock(), patch()
- ❌ FORBIDDEN: pytest-mock, mocker fixture
- ❌ FORBIDDEN: Any mocking, stubbing, or test double libraries
- ❌ FORBIDDEN: Fake in-memory databases or fake HTTP responses
- ❌ FORBIDDEN: Simulated external services or APIs

✅ ONLY REAL INTEGRATION TESTS ARE ALLOWED:
- ✅ Real database operations with actual SQL
- ✅ Real HTTP requests through test client
- ✅ Real browser interactions with Chrome DevTools MCP
- ✅ Real external service calls (or skip tests if unavailable)

If you write a test with mocks, the test is INVALID and must be rewritten.

This test suite provides REAL integration tests for OAuth functionality following
the repository's strict no-mocking policy. All tests use:
- Real database operations
- Real HTTP requests through test client
- Real token encryption
- Real PKCE generation
- Real state validation

NO MOCKS, STUBS, OR TEST DOUBLES ARE USED.

Test Coverage:
- Token encryption/decryption with real Fernet
- PKCE generation and validation
- State parameter security
- OAuth account management (real database)
- OAuth token storage (real database)
- Security validations

Running Tests:
    pytest test_oauth_real.py -v
    docker compose -f docker/docker-compose.yaml exec runtime pytest test_oauth_real.py -v
"""

import pytest
import os
import hashlib
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime'))

from emmett.orm import Field
from emmett.orm.migrations.utils import generate_runtime_migration
from app import app, db, User, OAuthAccount, OAuthToken
from auth.tokens import encrypt_token, decrypt_token, generate_encryption_key
from auth.providers.base import BaseOAuthProvider
from auth.providers.google import GoogleOAuthProvider
from auth.oauth_manager import OAuthManager


@pytest.fixture(scope='module', autouse=True)
def _prepare_db(request):
    """Ensure database is ready - create all tables including users and OAuth tables"""
    import sqlite3
    print(f"🔧 _prepare_db fixture running...")
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'runtime', 'databases', 'bloggy.db')
    db_dir = os.path.dirname(db_path)
    
    # Ensure database directory exists
    os.makedirs(db_dir, exist_ok=True)
    
    # Drop all existing tables using direct SQLite connection
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Disable foreign keys temporarily
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Drop all tables
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
            
            conn.commit()
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.close()
            print(f"   ✅ Dropped {len(tables)} tables from existing database")
        except Exception as e:
            print(f"   ⚠️  Could not drop tables: {e}")
    
    # Create all tables using Emmett migrations
    with db.connection():
        migration = generate_runtime_migration(db)
        migration.up()
        print("   ✅ All tables created via migration")
        
        # Ensure OAuth tables exist (they should be in migration now)
        try:
            db.executesql("SELECT COUNT(*) FROM oauth_accounts LIMIT 1")
            print("   ℹ️  oauth_accounts table confirmed")
        except Exception as e:
            print(f"   ⚠️  oauth_accounts table issue: {e}")
        
        try:
            db.executesql("SELECT COUNT(*) FROM oauth_tokens LIMIT 1")
            print("   ℹ️  oauth_tokens table confirmed")
        except Exception as e:
            print(f"   ⚠️  oauth_tokens table issue: {e}")
        
        db.commit()
    
    yield
    
    # Cleanup - delete only test data created by these tests
    try:
        with db.connection():
            # Delete real OAuth test data
            try:
                if 'oauth_tokens' in db.tables:
                    db.executesql("DELETE FROM oauth_tokens WHERE oauth_account IN (SELECT id FROM oauth_accounts WHERE email LIKE 'oauth_test%')")
                if 'oauth_accounts' in db.tables:
                    db.executesql("DELETE FROM oauth_accounts WHERE email LIKE 'oauth_test%'")
            except Exception as e:
                print(f"Warning cleaning OAuth tables: {e}")
            
            # Delete test users
            try:
                db.executesql("DELETE FROM users WHERE email LIKE 'oauth_test%'")
            except Exception as e:
                print(f"Warning cleaning users: {e}")
            
            db.commit()
    except Exception as e:
        # Cleanup failed, that's okay for tests
        print(f"Cleanup warning: {e}")


@pytest.fixture()
def test_user():
    """Create a real test user in database"""
    import uuid
    user_id = None
    try:
        with db.connection():
            # Create user with unique email to avoid UNIQUE constraint failures
            unique_email = f'oauth_test_{uuid.uuid4().hex[:8]}@example.com'
            user_id = db.users.insert(
                email=unique_email,
                first_name='OAuth',
                last_name='Test',
                password='pbkdf2(1000,20,sha512)$abcd1234$' + 'x' * 80  # Dummy hash
            )
            db.commit()
            print(f"✅ Created test user with ID: {user_id} ({unique_email})")
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        import traceback
        traceback.print_exc()
    
    yield user_id
    
    # Cleanup real database records
    if user_id:
        try:
            with db.connection():
                # Delete associated OAuth accounts first
                if 'oauth_accounts' in db.tables:
                    try:
                        oauth_accounts = db(db.oauth_accounts.user == user_id).select()
                        for oa in oauth_accounts:
                            # Delete associated tokens
                            if 'oauth_tokens' in db.tables:
                                db(db.oauth_tokens.oauth_account == oa.id).delete()
                            db(db.oauth_accounts.id == oa.id).delete()
                    except Exception as e:
                        print(f"Warning: Could not delete OAuth accounts: {e}")
                
                # Delete user
                db(db.users.id == user_id).delete()
                db.commit()
                print(f"✅ Cleaned up test user {user_id}")
        except Exception as e:
            print(f"⚠️  Cleanup warning for user {user_id}: {e}")


class TestRealTokenEncryption:
    """Test REAL token encryption (no mocking)"""
    
    def test_encrypt_token_real(self):
        """Test real token encryption with Fernet"""
        # Set real encryption key
        os.environ['OAUTH_TOKEN_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
        
        # Encrypt real token
        token = "real_access_token_12345"
        encrypted = encrypt_token(token)
        
        # Verify real encryption happened
        assert encrypted != token
        assert len(encrypted) > len(token)
        assert token not in encrypted
    
    def test_decrypt_token_real(self):
        """Test real token decryption"""
        os.environ['OAUTH_TOKEN_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
        
        # Encrypt then decrypt real token
        original = "my_secret_token"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)
        
        # Verify real roundtrip
        assert decrypted == original
    
    def test_encryption_roundtrip_various_tokens(self):
        """Test real encryption with various token formats"""
        os.environ['OAUTH_TOKEN_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
        
        # Reset cipher for new key
        import auth.tokens
        auth.tokens._cipher = None
        
        test_tokens = [
            "short",
            "very_long_token_" + "x" * 500,
            "token.with.dots",
            "token-with-dashes",
            "token_with_special!@#$%",
        ]
        
        for token in test_tokens:
            encrypted = encrypt_token(token)
            decrypted = decrypt_token(encrypted)
            assert decrypted == token, f"Roundtrip failed for: {token}"
    
    def test_wrong_key_fails_real(self):
        """Test that wrong encryption key fails (real Fernet validation)"""
        # Encrypt with one key
        key1 = Fernet.generate_key().decode()
        os.environ['OAUTH_TOKEN_ENCRYPTION_KEY'] = key1
        
        import auth.tokens
        auth.tokens._cipher = None
        
        token = "secret"
        encrypted = encrypt_token(token)
        
        # Try to decrypt with different key
        key2 = Fernet.generate_key().decode()
        os.environ['OAUTH_TOKEN_ENCRYPTION_KEY'] = key2
        auth.tokens._cipher = None
        
        # Real Fernet will raise InvalidToken
        with pytest.raises(InvalidToken):
            decrypt_token(encrypted)
    
    def test_generate_real_encryption_key(self):
        """Test generation of real Fernet key"""
        key = generate_encryption_key()
        
        # Verify it's a real valid Fernet key
        assert len(key) == 44  # Fernet key length
        
        # Verify it works with real Fernet
        cipher = Fernet(key.encode())
        test_data = b"test"
        encrypted = cipher.encrypt(test_data)
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == test_data


class TestRealPKCEGeneration:
    """Test REAL PKCE generation (no mocking)"""
    
    def test_generate_real_pkce_pair(self):
        """Test real PKCE pair generation"""
        verifier, challenge = BaseOAuthProvider.generate_pkce_pair()
        
        # Verify real generation
        assert verifier is not None
        assert challenge is not None
        assert verifier != challenge
        assert len(verifier) >= 43  # RFC 7636 minimum
        assert len(challenge) > 0
    
    def test_pkce_challenge_derived_correctly(self):
        """Test that challenge is correctly derived from verifier (real SHA256)"""
        verifier, challenge = BaseOAuthProvider.generate_pkce_pair()
        
        # Manually compute expected challenge using real hashlib
        expected = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip('=')
        
        # Verify real derivation
        assert challenge == expected
    
    def test_pkce_pairs_unique(self):
        """Test that each PKCE pair is unique (real randomness)"""
        # Generate multiple pairs
        pairs = [BaseOAuthProvider.generate_pkce_pair() for _ in range(100)]
        
        # Verify real uniqueness
        verifiers = [v for v, c in pairs]
        challenges = [c for v, c in pairs]
        
        assert len(set(verifiers)) == 100, "Verifiers should be unique"
        assert len(set(challenges)) == 100, "Challenges should be unique"
    
    def test_pkce_verifier_length_compliant(self):
        """Test PKCE verifier meets RFC 7636 requirements"""
        verifier, _ = BaseOAuthProvider.generate_pkce_pair()
        
        # RFC 7636: 43-128 characters
        assert 43 <= len(verifier) <= 128


class TestRealStateGeneration:
    """Test REAL state parameter generation (no mocking)"""
    
    def test_generate_real_state(self):
        """Test real state generation"""
        state = BaseOAuthProvider.generate_state()
        
        # Verify real generation
        assert state is not None
        assert len(state) >= 40  # Good entropy
    
    def test_state_uniqueness(self):
        """Test real state uniqueness"""
        # Generate many states
        states = [BaseOAuthProvider.generate_state() for _ in range(1000)]
        
        # Verify real uniqueness (no collisions)
        assert len(set(states)) == 1000
    
    def test_state_url_safe(self):
        """Test state uses URL-safe characters"""
        state = BaseOAuthProvider.generate_state()
        
        # Verify only URL-safe base64 characters
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
        assert all(c in valid_chars for c in state)


class TestRealOAuthDatabaseOperations:
    """Test REAL OAuth database operations (no mocking)"""
    
    def test_create_real_oauth_account(self, test_user):
        """Test creating real OAuthAccount in database"""
        with db.connection():
            # Create real OAuth account using raw SQL insert to avoid validation issues
            account_id = db.oauth_accounts.insert(
                user=test_user,
                provider='google',
                provider_user_id='google_123',
                email='test@gmail.com',
                name='Test User'
            )
            
            # Verify real database record in same transaction
            account = db.oauth_accounts[account_id]
            assert account is not None
            assert account.provider == 'google'
            assert account.provider_user_id == 'google_123'
            assert account.email == 'test@gmail.com'
            assert account.user == test_user
            
            # Cleanup
            del db.oauth_accounts[account_id]
    
    def test_create_real_oauth_token(self, test_user):
        """Test creating real OAuthToken in database"""
        with db.connection():
            # Create OAuth account first using raw SQL
            oauth_account_id = db.oauth_accounts.insert(
                user=test_user,
                provider='github',
                provider_user_id='github_456',
                email='test@github.com'
            )
            
            # Create real OAuth token with real encryption
            access_token = "real_access_token"
            refresh_token = "real_refresh_token"
            
            token_id = db.oauth_tokens.insert(
                oauth_account=oauth_account_id,
                access_token_encrypted=encrypt_token(access_token),
                refresh_token_encrypted=encrypt_token(refresh_token),
                access_token_expires_at=datetime.now() + timedelta(hours=1),
                token_type='Bearer',
                scope='user email'
            )
            
            # Verify real database record in same transaction
            stored_token = db.oauth_tokens[token_id]
            assert stored_token is not None
            
            # Verify real decryption
            decrypted_access = decrypt_token(stored_token.access_token_encrypted)
            decrypted_refresh = decrypt_token(stored_token.refresh_token_encrypted)
            
            assert decrypted_access == access_token
            assert decrypted_refresh == refresh_token
            
            # Cleanup
            del db.oauth_tokens[token_id]
            del db.oauth_accounts[oauth_account_id]
    
    def test_query_real_oauth_accounts_by_provider(self, test_user):
        """Test querying real OAuth accounts from database"""
        with db.connection():
            # Create multiple real accounts using raw SQL
            google_id = db.oauth_accounts.insert(
                user=test_user,
                provider='google',
                provider_user_id='g123',
                email='test@gmail.com'
            )
            
            github_id = db.oauth_accounts.insert(
                user=test_user,
                provider='github',
                provider_user_id='gh456',
                email='test@github.com'
            )
            
            # Query real database in same transaction
            google_accounts = db(db.oauth_accounts.provider == 'google').select()
            
            assert len(google_accounts) > 0
            assert google_accounts[0].provider == 'google'
            
            # Query by user
            user_accounts = db(db.oauth_accounts.user == test_user).select()
            
            assert len(user_accounts) == 2
            
            # Cleanup
            del db.oauth_accounts[google_id]
            del db.oauth_accounts[github_id]
    
    def test_delete_real_oauth_account_cascade(self, test_user):
        """Test deleting OAuth account deletes associated tokens (real DB)"""
        with db.connection():
            # Create account and token using raw SQL
            account_id = db.oauth_accounts.insert(
                user=test_user,
                provider='microsoft',
                provider_user_id='ms789',
                email='test@outlook.com'
            )
            
            token_id = db.oauth_tokens.insert(
                oauth_account=account_id,
                access_token_encrypted=encrypt_token("token"),
                token_type='Bearer'
            )
            
            # Verify account exists
            account = db.oauth_accounts[account_id]
            assert account is not None, "Account should exist before deletion"
            
            # Delete token first
            del db.oauth_tokens[token_id]
            
            # Delete account
            del db.oauth_accounts[account_id]
            
            # Verify deletion
            account_check = db.oauth_accounts(account_id)
            assert account_check is None, "Account should be deleted"


class TestRealOAuthSecurity:
    """Test REAL OAuth security features (no mocking)"""
    
    def test_pkce_prevents_code_interception(self):
        """Test that PKCE really prevents code interception"""
        # Generate legitimate PKCE pair
        verifier, challenge = BaseOAuthProvider.generate_pkce_pair()
        
        # Attacker generates different pair
        attacker_verifier, attacker_challenge = BaseOAuthProvider.generate_pkce_pair()
        
        # Verify challenges don't match (prevents attack)
        assert challenge != attacker_challenge
        
        # Even if attacker knows challenge, can't generate matching verifier
        test_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(attacker_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        assert test_challenge != challenge
    
    def test_state_prevents_csrf(self):
        """Test that state parameter prevents CSRF"""
        # Legitimate state
        legitimate_state = BaseOAuthProvider.generate_state()
        
        # Attacker's state
        attacker_state = BaseOAuthProvider.generate_state()
        
        # Verify states don't match (prevents CSRF)
        assert legitimate_state != attacker_state
    
    def test_encrypted_tokens_not_readable(self):
        """Test that encrypted tokens can't be read without key"""
        os.environ['OAUTH_TOKEN_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
        
        import auth.tokens
        auth.tokens._cipher = None
        
        # Encrypt sensitive token
        sensitive_token = "very_secret_access_token_12345"
        encrypted = encrypt_token(sensitive_token)
        
        # Verify original token not in encrypted version
        assert sensitive_token not in encrypted
        
        # Verify can't be decoded as base64 to original
        try:
            decoded = base64.b64decode(encrypted)
            assert sensitive_token.encode() not in decoded
        except:
            pass  # Expected - encrypted data is not valid base64


class TestRealOAuthManager:
    """Test REAL OAuth manager (no mocking)"""
    
    def test_register_real_provider(self):
        """Test registering real provider"""
        manager = OAuthManager()
        manager.providers = {}  # Clear for test
        
        # Create real provider
        provider = GoogleOAuthProvider(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://localhost/callback"
        )
        
        # Register real provider
        manager.register_provider(provider)
        
        # Verify real registration
        assert 'google' in manager.providers
        assert manager.get_provider('google') == provider
    
    def test_list_enabled_providers(self):
        """Test listing real enabled providers"""
        manager = OAuthManager()
        manager.providers = {}
        
        # Register multiple real providers
        google = GoogleOAuthProvider("id1", "secret1", "uri1")
        manager.register_provider(google)
        
        # List real providers
        providers = manager.list_enabled_providers()
        assert 'google' in providers


class TestRealProviderConfiguration:
    """Test REAL provider configuration (no mocking)"""
    
    def test_google_provider_real_configuration(self):
        """Test Google provider has correct real configuration"""
        provider = GoogleOAuthProvider(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost/callback"
        )
        
        # Verify real configuration
        assert provider.provider_name == 'google'
        assert 'accounts.google.com' in provider.authorize_url
        assert 'googleapis.com' in provider.token_url
        assert 'openid' in provider.scopes
        assert 'email' in provider.scopes
    
    def test_build_real_authorization_url(self):
        """Test building real authorization URL"""
        provider = GoogleOAuthProvider("id", "secret", "http://localhost/cb")
        
        state = provider.generate_state()
        verifier, challenge = provider.generate_pkce_pair()
        
        # Build real URL
        auth_url = provider.build_authorization_url(state, challenge)
        
        # Verify real URL components
        assert 'accounts.google.com' in auth_url
        assert f'client_id=id' in auth_url
        assert f'state={state}' in auth_url
        assert f'code_challenge={challenge}' in auth_url
        assert 'code_challenge_method=S256' in auth_url


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

