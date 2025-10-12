
/proposal add-realtime-pub-sub-support
<>
    / subscribe to changes in any record from the 'example' collection
    pb.collection('example').subscribe('*', function (e) {
        console.log(e.record);
    });
y default PocketBase sends realtime events only for Record create/update/delete operations (and for the OAuth2 auth redirect), but you are free to send custom realtime messages to the connected clients via the $app.subscriptionsBroker() instance.

$app.subscriptionsBroker().clients() returns all connected subscriptions.Client indexed by their unique connection id.

The current auth record associated with a client could be accessed through client.get("auth")    
<>
/proposal create a celery task that spawn agent
---

## OAuth Testing with Real User (ed.s.sharood@gmail.com)

✅ **COMPLETED** - OAuth testing configured for real user: Ed (ed.s.sharood@gmail.com)

Files created:
- integration_tests/oauth_test_config.yaml - Test user configuration
- integration_tests/test_oauth_real_user.py - Real user OAuth integration tests
- documentation/OAUTH_TESTING_GUIDE.md - Complete testing guide
- documentation/OAUTH_QUICK_START.md - Quick start guide
- test_oauth_real_user.sh - Quick test script

Quick test:
```bash
./test_oauth_real_user.sh
```

These tests verify:
- ✅ OAuth database operations (create, link, unlink accounts)
- ✅ Token encryption/decryption with real Fernet
- ✅ Multiple provider support
- ✅ User account creation with real email
- ✅ Security features (PKCE, state validation)

**No OAuth provider credentials required for basic tests!**
Tests use REAL database operations (no mocking) per repository policy.

For full end-to-end OAuth testing with real providers:
1. See: runtime/documentation/OAUTH_SETUP.md
2. Configure Google/GitHub/Microsoft/Facebook OAuth
3. Test manual login at: http://localhost:8081/auth/login
4. Log in with: ed.s.sharood@gmail.com

---

