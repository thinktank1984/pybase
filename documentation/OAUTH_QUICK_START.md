# OAuth Quick Start - Testing with Real User

**Test User:** Ed (ed.s.sharood@gmail.com)

This quick start guide gets you testing OAuth functionality in under 5 minutes.

## TL;DR - Run Tests Now

```bash
# Quick test (no OAuth credentials needed)
./test_oauth_real_user.sh

# Or with Docker
docker compose -f docker/docker-compose.yaml exec runtime /workspace/test_oauth_real_user.sh
```

These tests verify:
- ✅ OAuth database operations work
- ✅ Token encryption works
- ✅ Account linking works
- ✅ Security features work

**No OAuth provider credentials required for basic tests!**

## What Gets Tested

### Without OAuth Credentials (Works Immediately)

```bash
./test_oauth_real_user.sh
```

Tests:
- ✅ Database schema (oauth_accounts, oauth_tokens tables)
- ✅ User creation with email: ed.s.sharood@gmail.com
- ✅ OAuth account linking (database operations)
- ✅ Token encryption/decryption
- ✅ Multiple provider support
- ✅ Account retrieval by email

**These tests use REAL database operations, no mocking!**

### With OAuth Credentials (Full End-to-End)

```bash
# Set up Google OAuth (example)
export GOOGLE_CLIENT_ID=your-id
export GOOGLE_CLIENT_SECRET=your-secret
export OAUTH_BASE_URL=http://localhost:8081

# Generate encryption key
export OAUTH_TOKEN_ENCRYPTION_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')

# Start application
docker compose -f docker/docker-compose.yaml up runtime

# Test manually:
# 1. Go to: http://localhost:8081/auth/login
# 2. Click "Continue with Google"
# 3. Log in with: ed.s.sharood@gmail.com
# 4. Verify login successful
```

## File Structure

```
integration_tests/
├── oauth_test_config.yaml      # Test user configuration
├── test_oauth_real_user.py     # Real user OAuth tests
└── test_oauth_real.py          # Core OAuth tests

documentation/
├── OAUTH_TESTING_GUIDE.md      # Complete testing guide
└── OAUTH_QUICK_START.md        # This file

runtime/documentation/
└── OAUTH_SETUP.md              # OAuth provider setup

test_oauth_real_user.sh         # Quick test script
```

## Configuration

Test user config: `integration_tests/oauth_test_config.yaml`

```yaml
test_user:
  name: "Ed"
  email: "ed.s.sharood@gmail.com"

providers:
  google:
    enabled: true
    test_email: "ed.s.sharood@gmail.com"
```

## Database Verification

Check if OAuth account was created:

```bash
docker compose -f docker/docker-compose.yaml exec runtime \
  python -c "
from app import db
with db.connection():
    accounts = db.executesql(
        'SELECT provider, email FROM oauth_accounts WHERE email = ?',
        ['ed.s.sharood@gmail.com']
    )
    print('OAuth accounts:', accounts if accounts else 'None')
"
```

## Common Tasks

### Run specific test

```bash
./test_oauth_real_user.sh -k test_oauth_account_linking
```

### Run with verbose output

```bash
./test_oauth_real_user.sh -vv
```

### Clean up test data

```bash
docker compose -f docker/docker-compose.yaml exec runtime \
  python -c "
from app import db
with db.connection():
    db.executesql('DELETE FROM oauth_tokens WHERE oauth_account IN (SELECT id FROM oauth_accounts WHERE email = ?)', ['ed.s.sharood@gmail.com'])
    db.executesql('DELETE FROM oauth_accounts WHERE email = ?', ['ed.s.sharood@gmail.com'])
    db.executesql('DELETE FROM users WHERE email = ?', ['ed.s.sharood@gmail.com'])
    db.commit()
    print('✅ Test data cleaned')
"
```

## Test Scenarios

### Scenario 1: Database-Only Testing (No Credentials Needed)

```bash
./test_oauth_real_user.sh
```

✅ Tests pass without any OAuth provider setup
✅ Verifies database layer works
✅ Verifies encryption works
✅ Verifies data integrity

### Scenario 2: Manual OAuth Flow (Requires Credentials)

1. **Setup OAuth provider** (see `runtime/documentation/OAUTH_SETUP.md`)

2. **Start app:**
   ```bash
   docker compose -f docker/docker-compose.yaml up runtime
   ```

3. **Test login:**
   - Go to: http://localhost:8081/auth/login
   - Click: "Continue with Google"
   - Login: ed.s.sharood@gmail.com
   - Verify: Successful login

4. **Check database:**
   ```bash
   ./test_oauth_real_user.sh -k test_oauth_account_retrieval
   ```

### Scenario 3: Account Linking (Requires Credentials)

1. **Create password account:**
   - Go to: http://localhost:8081/auth/register
   - Email: ed.s.sharood@gmail.com
   - Password: (choose any)

2. **Link OAuth:**
   - Login with password
   - Go to: http://localhost:8081/account/settings
   - Click: "Connect Google"
   - Login: ed.s.sharood@gmail.com

3. **Verify:**
   ```bash
   docker compose -f docker/docker-compose.yaml exec runtime \
     python -c "
   from app import db
   with db.connection():
       result = db.executesql('''
           SELECT u.email, oa.provider, oa.email
           FROM users u
           JOIN oauth_accounts oa ON oa.user = u.id
           WHERE u.email = ?
       ''', ['ed.s.sharood@gmail.com'])
       for row in result:
           print(f'User: {row[0]}, Provider: {row[1]}, OAuth Email: {row[2]}')
   "
   ```

## What Makes This Different

### ✅ REAL Integration Tests

- ✅ Real database operations (SQLite)
- ✅ Real encryption (Fernet)
- ✅ Real HTTP requests (test client)
- ✅ Real token management
- ✅ Real security validations

### ❌ NO Mocking (Repository Policy)

- ❌ No mocks
- ❌ No stubs
- ❌ No test doubles
- ❌ No fake data
- ❌ No simulated responses

**Why?** Mocking creates false confidence. Real tests catch real bugs.

## Troubleshooting

### Tests fail with "oauth_accounts table does not exist"

**Solution:**
```bash
docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up
```

### Tests fail with "encryption key not set"

**Solution:**
```bash
export OAUTH_TOKEN_ENCRYPTION_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
./test_oauth_real_user.sh
```

### Want to test with real OAuth flow

**Solution:** See `runtime/documentation/OAUTH_SETUP.md` for provider setup

### Tests pass but want to verify database

**Solution:**
```bash
docker compose -f docker/docker-compose.yaml exec runtime emmett shell
>>> from app import db
>>> with db.connection():
...     accounts = db.executesql("SELECT * FROM oauth_accounts WHERE email = 'ed.s.sharood@gmail.com'")
...     print(accounts)
```

## Next Steps

1. **Run basic tests:** `./test_oauth_real_user.sh` ✅ (works now)
2. **Setup OAuth provider:** See `runtime/documentation/OAUTH_SETUP.md`
3. **Test manual flow:** Follow Scenario 2 above
4. **Test account linking:** Follow Scenario 3 above
5. **Read full guide:** See `documentation/OAUTH_TESTING_GUIDE.md`

## Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `./test_oauth_real_user.sh` |
| Run specific test | `./test_oauth_real_user.sh -k test_name` |
| Check database | See "Database Verification" above |
| Clean test data | See "Clean up test data" above |
| Setup OAuth | See `runtime/documentation/OAUTH_SETUP.md` |
| Full testing guide | See `documentation/OAUTH_TESTING_GUIDE.md` |

## Support

For issues:
1. Check logs: `docker compose -f docker/docker-compose.yaml logs runtime`
2. Check database: `docker compose -f docker/docker-compose.yaml exec runtime emmett shell`
3. Review config: `cat integration_tests/oauth_test_config.yaml`
4. Read docs: `documentation/OAUTH_TESTING_GUIDE.md`

