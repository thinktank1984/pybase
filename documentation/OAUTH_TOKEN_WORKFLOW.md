# OAuth Token Testing Workflow

## Overview

This document describes how to test OAuth integration using **REAL tokens** obtained from the host machine and used in Docker-based integration tests.

🚨 **CRITICAL**: This follows our NO MOCKING policy - all tests use REAL OAuth tokens from REAL providers.

## Workflow Summary

```
┌──────────────────┐
│  Host Machine    │
│  (Mac/Linux)     │
│                  │
│  1. Run helper   │
│     script       │
│  2. Browser      │
│     opens        │
│  3. Authenticate │
│  4. Token saved  │
│     to file      │
└────────┬─────────┘
         │
         │ .oauth_tokens.yaml
         │ (shared volume)
         ↓
┌────────────────────┐
│  Docker Container  │
│                    │
│  5. Tests read     │
│     token file     │
│  6. Use real token │
│  7. Verify OAuth   │
│     integration    │
└────────────────────┘
```

## Why This Approach?

### Problem

OAuth requires browser-based authentication:
- User must log in via browser
- User must approve permissions
- OAuth provider redirects with authorization code
- Code must be exchanged for access token

**In Docker**: Browser authentication is difficult
**On Host**: Browser authentication is easy

### Solution

**Get tokens on host machine (where browser works), use tokens in Docker (where tests run).**

This provides:
- ✅ Real OAuth tokens from real providers
- ✅ Real token encryption/decryption
- ✅ Real database operations with tokens
- ✅ Real API calls with tokens
- ✅ Consistent test environment in Docker
- ❌ NO mocking required

## Step-by-Step Guide

### Prerequisites

1. **OAuth Provider Credentials**

   Set environment variables for your OAuth provider:

   ```bash
   # Google OAuth
   export GOOGLE_CLIENT_ID="your-client-id"
   export GOOGLE_CLIENT_SECRET="your-client-secret"
   
   # GitHub OAuth (optional)
   export GITHUB_CLIENT_ID="your-client-id"
   export GITHUB_CLIENT_SECRET="your-client-secret"
   
   # Microsoft OAuth (optional)
   export MICROSOFT_CLIENT_ID="your-client-id"
   export MICROSOFT_CLIENT_SECRET="your-client-secret"
   ```

2. **Python Dependencies**

   On host machine:
   ```bash
   pip install requests pyyaml cryptography
   ```

### Step 1: Obtain Real OAuth Token (Host Machine)

Run the helper script on your host machine (Mac/Linux):

```bash
# Get Google OAuth token
python3 integration_tests/oauth_token_helper.py --provider google
```

**What happens:**
1. Script starts local HTTP server on `localhost:8765`
2. Browser opens to OAuth provider's login page
3. You log in with real credentials (ed.s.sharood@gmail.com)
4. You approve permissions
5. Provider redirects to local server with authorization code
6. Script exchanges code for access token (real OAuth PKCE flow)
7. Script saves token to `.oauth_tokens.yaml`

**Example output:**
```
🔐 Obtaining OAuth token from Google...
   Provider: google
   Redirect URI: http://localhost:8765/callback
   ✅ Generated PKCE pair
   ✅ Generated state parameter

📝 Step 1: Starting local callback server on localhost:8765
   ✅ Callback server started

🌐 Step 2: Opening browser for authentication...
   If browser doesn't open, visit this URL:
   https://accounts.google.com/o/oauth2/v2/auth?...

⏳ Step 3: Waiting for authentication...
   Please complete authentication in your browser...
   ✅ Authorization code received
   ✅ State verified

🔄 Step 4: Exchanging code for access token...
   ✅ Token received!
   ✅ User info retrieved!
   User: Ed
   Email: ed.s.sharood@gmail.com

💾 Token saved to: integration_tests/.oauth_tokens.yaml
   Docker will read this file during tests
   ✅ File permissions set to 600 (user-only)

🎉 Done! Token ready for Docker testing.

📖 Next steps:
   1. Run tests in Docker:
      docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_oauth_real_user.py -v
   2. Tests will automatically use saved token
   3. Tests will verify real OAuth integration
```

### Step 2: Verify Token Saved

Check that token file exists:

```bash
cat integration_tests/.oauth_tokens.yaml
```

**Example content:**
```yaml
google:
  provider: google
  access_token: ya29.a0AfH6SMBXXx...very_long_token...
  token_type: Bearer
  scope: openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile
  obtained_at: '2025-10-12T10:30:45.123456'
  expires_at: '2025-10-12T11:30:45.123456'
  refresh_token: 1//0gXXXxxxxx...  # If available
  user_info:
    sub: '123456789012345678901'
    email: ed.s.sharood@gmail.com
    email_verified: true
    name: Ed
    picture: https://lh3.googleusercontent.com/...
```

### Step 3: Run Tests in Docker

The token file is shared with Docker via volume mount. Tests automatically read it:

```bash
# Run all OAuth tests with real token
docker compose -f docker/docker-compose.yaml exec runtime \
  pytest integration_tests/test_oauth_real_user.py -v

# Run specific test
docker compose -f docker/docker-compose.yaml exec runtime \
  pytest integration_tests/test_oauth_real_user.py::TestRealUserOAuth::test_use_real_token_for_api_call -v
```

**What happens in tests:**
1. Test fixture loads `.oauth_tokens.yaml`
2. Test retrieves real token
3. Test stores token in database (with real encryption)
4. Test makes real API call to Google with token
5. Test verifies user info matches expected user
6. Test cleans up database

**Example test output:**
```
test_oauth_real_user.py::TestRealUserOAuth::test_use_real_token_for_api_call 

   ℹ️  Using real OAuth token from host machine
      Provider: google
      Obtained: 2025-10-12T10:30:45.123456
      User: ed.s.sharood@gmail.com

   🔄 Making real API call to Google with token...
   ✅ Real API call succeeded
      Email: ed.s.sharood@gmail.com
      Name: Ed
      Verified: True

PASSED
```

### Step 4: Token Expiration

OAuth tokens typically expire after 1 hour. If tests fail with 401 errors:

```bash
# Obtain fresh token
python3 integration_tests/oauth_token_helper.py --provider google

# Re-run tests
docker compose -f docker/docker-compose.yaml exec runtime \
  pytest integration_tests/test_oauth_real_user.py -v
```

## Security

### Token Storage

- **File**: `.oauth_tokens.yaml` in `integration_tests/`
- **Permissions**: `600` (user-only read/write)
- **Git**: Added to `.gitignore` (never commit tokens!)
- **Encryption**: Tokens encrypted before storing in database

### Token Protection

```bash
# Verify file permissions
ls -la integration_tests/.oauth_tokens.yaml
# Should show: -rw------- (600)

# Verify not in git
git status integration_tests/.oauth_tokens.yaml
# Should show: ignored
```

### Token Cleanup

```bash
# Remove tokens after testing
rm integration_tests/.oauth_tokens.yaml
```

## Test Coverage

### Tests Using Real Tokens

1. **test_store_real_oauth_token_in_database**
   - Stores real token in database
   - Verifies real encryption
   - Verifies real decryption
   - Verifies metadata preserved

2. **test_use_real_token_for_api_call**
   - Makes real API call to Google
   - Uses real OAuth token
   - Verifies response
   - Verifies user info

3. **test_token_has_required_scopes**
   - Verifies token has required OAuth scopes
   - Checks openid, email, profile

4. **test_token_user_info_matches_config**
   - Verifies token is for correct user
   - Matches ed.s.sharood@gmail.com

### Tests Without Real Tokens

Some tests don't require real tokens from OAuth providers:
- Token encryption/decryption tests
- PKCE generation tests  
- State generation tests
- Database operations tests

These tests use generated test data but still test REAL operations (no mocking).

## Troubleshooting

### Token Helper Script Fails

**Problem**: Browser doesn't open
```bash
# Manually open URL shown in script output
# Look for: "If browser doesn't open, visit this URL:"
```

**Problem**: Callback server port in use
```bash
# Check what's using port 8765
lsof -i :8765

# Kill process or modify CALLBACK_PORT in script
```

**Problem**: Missing OAuth credentials
```bash
# Set environment variables
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET="..."
```

### Tests Fail with 401

**Problem**: Token expired

OAuth tokens typically expire after 1 hour.

**Solution**: Obtain fresh token
```bash
python3 integration_tests/oauth_token_helper.py --provider google
```

### Tests Fail: No Token File

**Problem**: `.oauth_tokens.yaml` not found

**Solution**: Obtain token first
```bash
python3 integration_tests/oauth_token_helper.py --provider google
```

**Check**: File exists
```bash
ls -la integration_tests/.oauth_tokens.yaml
```

### Docker Volume Not Mounted

**Problem**: Docker can't see token file

**Solution**: Check docker-compose.yaml has volume mount
```yaml
volumes:
  - ../integration_tests:/app/integration_tests
```

**Verify**: File exists in container
```bash
docker compose -f docker/docker-compose.yaml exec runtime \
  ls -la integration_tests/.oauth_tokens.yaml
```

## Advanced Usage

### Multiple Providers

Obtain tokens from multiple providers:

```bash
# Get Google token
python3 integration_tests/oauth_token_helper.py --provider google

# Get GitHub token
python3 integration_tests/oauth_token_helper.py --provider github

# Get Microsoft token
python3 integration_tests/oauth_token_helper.py --provider microsoft
```

Token file will contain all tokens:

```yaml
google:
  provider: google
  access_token: ya29...
  # ...

github:
  provider: github
  access_token: gho_...
  # ...

microsoft:
  provider: microsoft
  access_token: EwB...
  # ...
```

### Show Saved Tokens

```bash
# Display saved tokens (without sensitive data)
python3 integration_tests/oauth_token_helper.py --show
```

Output:
```
📋 Saved OAuth Tokens (integration_tests/.oauth_tokens.yaml):

  google:
    Obtained: 2025-10-12T10:30:45.123456
    Expires: 2025-10-12T11:30:45.123456
    User: ed.s.sharood@gmail.com

  github:
    Obtained: 2025-10-12T10:35:22.789012
    Expires: N/A
    User: ed.s.sharood
```

### CI/CD Integration

For CI/CD pipelines, obtain tokens once and store as secrets:

```yaml
# .github/workflows/test.yml
env:
  GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
  GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}

steps:
  - name: Obtain OAuth Token
    run: |
      python3 integration_tests/oauth_token_helper.py --provider google
  
  - name: Run OAuth Tests
    run: |
      docker compose -f docker/docker-compose.yaml exec runtime \
        pytest integration_tests/test_oauth_real_user.py -v
```

**Note**: In CI/CD, you may need headless browser or pre-generated tokens.

## Architecture

### Token Helper Script

**Purpose**: Obtain real OAuth tokens from host machine

**Technology**:
- Python 3
- HTTP server for OAuth callback
- Real PKCE (RFC 7636) implementation
- Real OAuth 2.0 authorization code flow
- Browser automation via webbrowser module

**Security**:
- PKCE prevents code interception
- State parameter prevents CSRF
- Tokens stored with 600 permissions
- Never committed to git

### Test Fixtures

**`real_oauth_token` fixture**:
- Loads `.oauth_tokens.yaml`
- Validates token exists
- Fails test if token missing (no skipping!)
- Provides real token to tests

**`real_user` fixture**:
- Creates real database user
- Matches token user email
- Cleans up after tests

### Test Flow

```
Test Start
    ↓
Load token from .oauth_tokens.yaml
    ↓
Create real user in database (if needed)
    ↓
Create OAuth account in database
    ↓
Encrypt real token with Fernet
    ↓
Store encrypted token in database
    ↓
Make real API call with token
    ↓
Verify response
    ↓
Cleanup database
    ↓
Test Complete
```

## No Mocking Policy

This workflow strictly adheres to our **NO MOCKING** policy:

### ✅ What We Use (REAL)

- Real OAuth tokens from real providers
- Real OAuth 2.0 PKCE flow
- Real browser authentication
- Real HTTP requests to OAuth providers
- Real token encryption with Fernet
- Real database operations
- Real API calls with tokens
- Real state/PKCE security

### ❌ What We Don't Use (FORBIDDEN)

- Mock OAuth providers
- Mock tokens
- Mock HTTP responses
- Mock browser authentication
- Mock encryption
- Mock database
- Test doubles
- Stubs

### Why Real Tokens?

**Mocked tests don't catch real bugs:**
- ✗ Token format changes
- ✗ Scope requirement changes
- ✗ API endpoint changes
- ✗ Encryption issues
- ✗ Database schema issues

**Real tokens catch everything:**
- ✓ Token works with real provider
- ✓ Token has correct scopes
- ✓ Token can be encrypted/decrypted
- ✓ Token can authenticate API calls
- ✓ Complete integration verified

## References

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [PKCE RFC 7636](https://tools.ietf.org/html/rfc7636)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [No Mocking Policy](NO_MOCKING_ENFORCEMENT.md)

## Summary

1. **On host machine**: Run `oauth_token_helper.py` to obtain real token
2. **Browser opens**: Authenticate with real OAuth provider
3. **Token saved**: Real token saved to `.oauth_tokens.yaml`
4. **In Docker**: Tests read token file and use real token
5. **Tests verify**: Real OAuth integration with real API calls

This workflow provides **complete real OAuth testing** while maintaining our **NO MOCKING** policy.

All tests use REAL tokens, REAL encryption, REAL database operations, and REAL API calls.

NO MOCKS. ONLY REAL INTEGRATION TESTS.

