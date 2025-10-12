# OAuth Testing Guide with Real User

This guide explains how to test OAuth social login functionality using real user credentials.

## Test User Information

Based on the provided user image:

- **Name:** Ed
- **Email:** ed.s.sharood@gmail.com

This user will be used for OAuth integration testing.

## Prerequisites

### 1. OAuth Provider Setup

Before testing, you need to configure at least one OAuth provider. See `runtime/documentation/OAUTH_SETUP.md` for detailed setup instructions.

**Quick Setup:**

```bash
# Generate encryption key
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# Set environment variables (add to .env)
OAUTH_TOKEN_ENCRYPTION_KEY=<generated-key>
OAUTH_BASE_URL=http://localhost:8081

# Google OAuth (example)
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>
```

### 2. Database Setup

Ensure OAuth tables are created:

```bash
cd runtime
uv run emmett migrations up
```

Or use Docker:

```bash
docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up
```

## Test Configuration

The OAuth test configuration is stored in `integration_tests/oauth_test_config.yaml`:

```yaml
test_user:
  name: "Ed"
  email: "ed.s.sharood@gmail.com"

providers:
  google:
    enabled: true
    test_email: "ed.s.sharood@gmail.com"
    scopes:
      - "openid"
      - "email"
      - "profile"
```

## Running OAuth Tests

### Automated Tests (No Manual OAuth Flow)

These tests verify OAuth functionality without requiring actual OAuth flow:

```bash
# Run OAuth integration tests
pytest integration_tests/test_oauth_real_user.py -v

# Or with Docker
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_oauth_real_user.py -v
```

**What these tests verify:**
- ✅ OAuth database operations (create, link, unlink)
- ✅ Token encryption and decryption
- ✅ Multiple provider linking
- ✅ User account creation
- ✅ Security features (PKCE, state validation)

**What these tests DON'T require:**
- ❌ Real OAuth provider credentials
- ❌ Browser interactions
- ❌ Manual login steps

### Manual OAuth Flow Testing

For end-to-end OAuth testing with real providers:

#### Test 1: OAuth Login (New User)

1. **Start the application:**
   ```bash
   docker compose -f docker/docker-compose.yaml up runtime
   ```

2. **Navigate to login page:**
   ```
   http://localhost:8081/auth/login
   ```

3. **Click "Continue with Google"**

4. **Log in with:** `ed.s.sharood@gmail.com`

5. **Approve permissions**

6. **Verify:**
   - Redirected back to application
   - Logged in successfully
   - Welcome message displayed

7. **Check database:**
   ```bash
   docker compose -f docker/docker-compose.yaml exec runtime \
     emmett shell -c "
   from app import db
   with db.connection():
       accounts = db.executesql(
           'SELECT user, provider, email FROM oauth_accounts WHERE email = ?',
           ['ed.s.sharood@gmail.com']
       )
       print('OAuth accounts:', accounts)
   "
   ```

**Expected Results:**
- ✅ New user created with email: ed.s.sharood@gmail.com
- ✅ OAuth account linked to user
- ✅ OAuth tokens stored (encrypted)
- ✅ User logged in automatically

#### Test 2: OAuth Account Linking (Existing User)

1. **Create email/password account first:**
   ```
   http://localhost:8081/auth/register
   Email: ed.s.sharood@gmail.com
   Password: TestPassword123!
   ```

2. **Log in with email/password**

3. **Navigate to account settings:**
   ```
   http://localhost:8081/account/settings
   ```

4. **Click "Connect Google" button**

5. **Log in with:** `ed.s.sharood@gmail.com`

6. **Approve permissions**

7. **Verify:**
   - Redirected back to account settings
   - "Connected" status shown for Google
   - Can log out and log back in with Google

**Expected Results:**
- ✅ OAuth account linked to existing user
- ✅ Can log in with either password or Google
- ✅ Both authentication methods work

#### Test 3: Multiple Provider Linking

1. **Log in with email/password or one OAuth provider**

2. **Go to account settings**

3. **Connect multiple providers:**
   - Click "Connect Google"
   - Click "Connect GitHub"
   - Click "Connect Microsoft"

4. **Verify all are connected**

5. **Test logging in with each provider**

**Expected Results:**
- ✅ Multiple OAuth providers linked to same user
- ✅ Can log in with any linked provider
- ✅ All providers show "Connected" status

#### Test 4: OAuth Account Unlinking

1. **Log in to account with multiple auth methods**

2. **Go to account settings**

3. **Click "Disconnect" for one provider**

4. **Verify:**
   - Provider disconnected
   - Still logged in
   - Other auth methods still work

5. **Try unlinking last auth method:**
   - Should show error
   - Must keep at least one auth method

**Expected Results:**
- ✅ Can unlink OAuth providers
- ✅ Cannot unlink last auth method (safety check)
- ✅ Other auth methods remain functional

## UI Testing with Chrome DevTools MCP

For automated UI testing of OAuth flows:

```bash
# Run Chrome UI tests
./run_tests.sh --chrome

# Or specific OAuth UI test
HAS_CHROME_MCP=true pytest integration_tests/test_ui_chrome_real.py::test_oauth_login_flow -v
```

**Note:** Chrome DevTools MCP can automate browser interactions but still requires real OAuth provider credentials.

## Database Verification

### Check OAuth Accounts

```bash
docker compose -f docker/docker-compose.yaml exec runtime \
  emmett shell -c "
from app import db
with db.connection():
    accounts = db.executesql('''
        SELECT u.email, oa.provider, oa.provider_user_id, oa.created_at
        FROM users u
        JOIN oauth_accounts oa ON oa.user = u.id
        WHERE u.email = ?
    ''', ['ed.s.sharood@gmail.com'])
    for acc in accounts:
        print(f'Email: {acc[0]}, Provider: {acc[1]}, ID: {acc[2]}, Created: {acc[3]}')
"
```

### Check OAuth Tokens

```bash
docker compose -f docker/docker-compose.yaml exec runtime \
  emmett shell -c "
from app import db
with db.connection():
    tokens = db.executesql('''
        SELECT oa.provider, ot.token_type, ot.scope, ot.created_at
        FROM oauth_tokens ot
        JOIN oauth_accounts oa ON oa.id = ot.oauth_account
        JOIN users u ON u.id = oa.user
        WHERE u.email = ?
    ''', ['ed.s.sharood@gmail.com'])
    for tok in tokens:
        print(f'Provider: {tok[0]}, Type: {tok[1]}, Scope: {tok[2]}, Created: {tok[3]}')
"
```

### Verify Token Encryption

```bash
docker compose -f docker/docker-compose.yaml exec runtime \
  python -c "
from app import db
from auth.tokens import decrypt_token

with db.connection():
    tokens = db.executesql('''
        SELECT access_token_encrypted 
        FROM oauth_tokens 
        LIMIT 1
    ''')
    
    if tokens:
        encrypted = tokens[0][0]
        print('Encrypted token (first 50 chars):', encrypted[:50])
        
        # Verify it's encrypted (should not be readable)
        print('Token is encrypted:', 'ya29' not in encrypted)
        
        # Decrypt to verify encryption is working
        decrypted = decrypt_token(encrypted)
        print('Decryption successful:', len(decrypted) > 0)
    else:
        print('No tokens found')
"
```

## Security Testing

### Test CSRF Protection (State Parameter)

1. **Get authorization URL:**
   ```bash
   curl http://localhost:8081/auth/oauth/google/login
   ```

2. **Note the state parameter in URL**

3. **Try callback with wrong state:**
   ```bash
   curl "http://localhost:8081/auth/oauth/google/callback?code=fake&state=wrong"
   ```

4. **Verify error:** "Security validation failed"

**Expected Result:**
- ✅ Invalid state rejected
- ✅ CSRF attack prevented

### Test PKCE Security

1. **Intercept authorization code (simulated)**

2. **Try token exchange without code_verifier:**
   - Should fail at provider level
   - Provider validates code_challenge vs code_verifier

**Expected Result:**
- ✅ Token exchange fails without correct verifier
- ✅ Authorization code interception prevented

## Troubleshooting

### "OAuth provider not available"

**Cause:** Provider credentials not set

**Solution:**
```bash
# Check environment variables
docker compose -f docker/docker-compose.yaml exec runtime env | grep GOOGLE

# Set if missing
export GOOGLE_CLIENT_ID=your-id
export GOOGLE_CLIENT_SECRET=your-secret

# Restart application
docker compose -f docker/docker-compose.yaml restart runtime
```

### "Redirect URI mismatch"

**Cause:** Callback URL doesn't match provider configuration

**Solution:**
1. Check `OAUTH_BASE_URL` in .env
2. Verify redirect URI in provider console:
   - Should be: `http://localhost:8081/auth/oauth/google/callback`
3. Update provider console if needed
4. Restart application

### "Email not verified"

**Cause:** OAuth provider requires verified email

**Solution:**
1. Verify email with provider (Google, GitHub, etc.)
2. Try again after verification
3. For GitHub: Go to Settings > Emails and verify

### "Token decryption failed"

**Cause:** Encryption key changed or not set

**Solution:**
```bash
# Check encryption key is set
echo $OAUTH_TOKEN_ENCRYPTION_KEY

# If missing, generate and set
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# IMPORTANT: Don't change key if you have existing encrypted tokens
# Changing the key will break existing tokens
```

### Database Tables Don't Exist

**Cause:** Migrations not run

**Solution:**
```bash
# Run migrations
docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up

# Or manually create tables (see test_oauth_real_user.py for SQL)
```

## Test Coverage

### What's Tested

✅ **Database Operations:**
- User creation with OAuth
- OAuth account linking/unlinking
- Token storage and retrieval
- Multiple provider support

✅ **Security Features:**
- Token encryption/decryption
- PKCE generation and validation
- State parameter validation
- CSRF protection

✅ **Integration:**
- OAuth flow with real providers (manual)
- Account linking to existing users
- Multiple auth method support
- Session management

### What's NOT Tested (by design)

❌ **Mocked OAuth Responses:**
- No fake provider responses
- No simulated tokens
- No mock authentication

❌ **Unit Tests in Isolation:**
- Tests verify complete flows
- Database changes are real
- HTTP requests are real

## Next Steps

1. **Set up OAuth providers** (see `runtime/documentation/OAUTH_SETUP.md`)
2. **Configure environment variables** (see `.env.example`)
3. **Run automated tests** (`pytest integration_tests/test_oauth_real_user.py`)
4. **Test manual flows** (follow instructions above)
5. **Verify database state** (use SQL queries above)

## Related Documentation

- `runtime/documentation/OAUTH_SETUP.md` - OAuth provider setup
- `integration_tests/oauth_test_config.yaml` - Test configuration
- `integration_tests/test_oauth_real.py` - Core OAuth tests
- `integration_tests/test_oauth_real_user.py` - Real user tests
- `documentation/README_UI_TESTING.md` - Chrome DevTools UI testing

## Support

If you encounter issues:

1. **Check logs:**
   ```bash
   docker compose -f docker/docker-compose.yaml logs runtime
   ```

2. **Check database:**
   ```bash
   docker compose -f docker/docker-compose.yaml exec runtime emmett shell
   ```

3. **Review configuration:**
   - Environment variables
   - OAuth provider console settings
   - Database migrations

4. **Test connectivity:**
   ```bash
   curl -I http://localhost:8081/auth/login
   ```

