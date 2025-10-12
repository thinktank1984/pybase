# OAuth Social Login - Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd /Users/ed.sharood2/code/pybase
pip install authlib cryptography requests
```

### Step 2: Generate Encryption Key

```bash
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

Copy the output (something like `3NJ8z9xK...`)

### Step 3: Create Environment File

Create a file `.env` in the project root:

```bash
# OAuth Token Encryption (use the key from Step 2)
OAUTH_TOKEN_ENCRYPTION_KEY=YOUR_KEY_FROM_STEP_2

# OAuth Base URL
OAUTH_BASE_URL=http://localhost:8081

# Google OAuth (optional - see below for setup)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth (optional - see below for setup)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Step 4: Run Database Migrations

```bash
cd runtime
emmett migrations up
```

### Step 5: Start the Application

```bash
cd runtime
emmett develop
```

### Step 6: Test It!

1. Open browser: `http://localhost:8081/auth/login`
2. You should see OAuth buttons (if configured)
3. If no providers configured, the buttons won't show (normal behavior)

## Setting Up OAuth Providers

### Quick Setup: GitHub (Easiest for Testing)

GitHub is the easiest to set up for local testing:

1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - Application name: `My Local App`
   - Homepage URL: `http://localhost:8081`
   - Authorization callback URL: `http://localhost:8081/auth/oauth/github/callback`
4. Click "Register application"
5. Copy the **Client ID**
6. Click "Generate a new client secret" and copy the **Client Secret**
7. Add to your `.env`:
   ```bash
   GITHUB_CLIENT_ID=your-client-id-here
   GITHUB_CLIENT_SECRET=your-client-secret-here
   ```
8. Restart your app: `emmett develop`
9. Go to login page - you should see "Continue with GitHub" button!

### Quick Setup: Google

1. Go to: https://console.cloud.google.com/
2. Create new project (or use existing)
3. Go to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. If prompted, configure OAuth consent screen first:
   - User Type: External
   - App name: Your app name
   - User support email: Your email
   - Developer contact: Your email
   - Save
6. Create OAuth Client ID:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8081/auth/oauth/google/callback`
   - Create
7. Copy Client ID and Client Secret
8. Add to `.env`:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```
9. Restart app

## Testing the OAuth Flow

### Test New User Signup

1. Clear cookies or use incognito mode
2. Go to: `http://localhost:8081/auth/login`
3. Click "Continue with GitHub" (or Google)
4. Approve the authorization
5. You should be logged in automatically!
6. Check: `http://localhost:8081/account/settings` - you should see the connected account

### Test Account Linking

1. Create a regular account (if you don't have one):
   - Go to: `http://localhost:8081/auth/register`
   - Fill in email, username, password
   - Register
2. Go to: `http://localhost:8081/account/settings`
3. Click "Connect" next to a provider (e.g., Google)
4. Complete OAuth flow
5. Now you can log in with EITHER password OR OAuth!

### Test Account Unlinking

1. Go to: `http://localhost:8081/account/settings`
2. Click "Disconnect" next to a connected provider
3. Note: You can't disconnect if it's your only login method!
4. To disconnect, first:
   - Set a password (if using OAuth-only account), OR
   - Connect another OAuth provider

## Common Issues

### Issue: "OAuth provider not available"

**Solution**: Provider credentials not configured in `.env` file. Set CLIENT_ID and CLIENT_SECRET for the provider, then restart the app.

### Issue: "Redirect URI mismatch"

**Solution**: 
- Check that callback URL in provider settings exactly matches: `http://localhost:8081/auth/oauth/{provider}/callback`
- Make sure to use `localhost` not `127.0.0.1`
- Restart app after changing configuration

### Issue: OAuth buttons don't show up

**Solutions**:
1. Check that provider credentials are in `.env`
2. Restart the application
3. Check console for errors
4. Verify `.env` file is in the correct location

### Issue: "Security validation failed"

**Solution**: Clear browser cookies and try again. This happens if session state doesn't match.

## What's Working Now

✅ OAuth login with 4 providers (Google, GitHub, Microsoft, Facebook)
✅ New user signup via OAuth
✅ Account linking (connect OAuth to existing account)
✅ Account unlinking (disconnect OAuth providers)
✅ Token encryption and secure storage
✅ PKCE and state validation (CSRF protection)
✅ Rate limiting
✅ Audit logging
✅ Account settings UI
✅ Error handling
✅ Token refresh (background job)

## CLI Commands

```bash
# Refresh expiring OAuth tokens
emmett oauth:refresh

# Clean up old expired tokens  
emmett oauth:cleanup
```

## Next Steps

1. **Production Setup**: See `runtime/documentation/OAUTH_SETUP.md` for production deployment
2. **Add More Providers**: Microsoft and Facebook (see setup guide)
3. **Customize UI**: Modify templates in `runtime/templates/auth/`
4. **Add Tests**: Create integration tests for OAuth flows
5. **Monitor**: Check logs in `runtime/logs/` for OAuth events

## File Locations

- **Configuration**: `.env` in project root
- **Templates**: `runtime/templates/auth/`
- **Models**: `runtime/models/oauth_account/` and `runtime/models/oauth_token/`
- **OAuth Logic**: `runtime/auth/`
- **Documentation**: `runtime/documentation/OAUTH_SETUP.md`

## Need Help?

- **Detailed Setup**: See `runtime/documentation/OAUTH_SETUP.md`
- **Implementation Details**: See `OAUTH_IMPLEMENTATION_SUMMARY.md`
- **Check Logs**: Look in console output for OAuth events
- **Test Mode**: Start with GitHub - it's the easiest to set up!

## Quick Reference

| Provider | Setup Difficulty | Features |
|----------|------------------|----------|
| GitHub | ⭐ Easy | Good for testing |
| Google | ⭐⭐ Medium | Most popular |
| Microsoft | ⭐⭐⭐ Advanced | Enterprise users |
| Facebook | ⭐⭐ Medium | Social users |

Start with **GitHub** for quick testing, then add others as needed!

---

**You're all set!** OAuth social login is now ready to use. 🎉

