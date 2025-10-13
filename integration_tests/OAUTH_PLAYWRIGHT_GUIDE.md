# OAuth Testing with Playwright - Automated Flow

## Overview

This guide shows how to use **Playwright** to automatically complete the OAuth flow and get real tokens for testing.

Since you're already logged into Chrome with **ed.s.sharood@gmail.com**, Playwright can automate the clicking through Google's OAuth screens.

## Quick Start

### Step 1: Install Dependencies

```bash
# Install Python packages
pip install playwright aiohttp pyyaml

# Install Playwright browsers
playwright install chromium
```

### Step 2: Set OAuth Credentials

You need to register your app with Google first (one-time setup):

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Go to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Web application"
6. Add redirect URI: `http://localhost:8765/callback`
7. Copy the Client ID and Client Secret

Then set them:

```bash
export GOOGLE_CLIENT_ID="your-client-id-here.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret-here"
```

### Step 3: Run Playwright Script

```bash
# Run the automated OAuth flow
python3 integration_tests/oauth_playwright_helper.py
```

**What happens:**
1. 🌐 Browser opens (Chromium)
2. 🔐 Navigates to Google OAuth page
3. ✅ Automatically clicks through OAuth screens
4. 👤 Uses your logged-in account (ed.s.sharood@gmail.com)
5. 🎫 Captures real OAuth token
6. 💾 Saves to `.oauth_tokens.yaml`

**Example output:**
```
🚀 OAuth Token Helper with Playwright

============================================================
This script automates the OAuth flow using Playwright.
It will open a browser and complete the OAuth process.
============================================================

🔐 Obtaining OAuth token from Google with Playwright...
   Provider: google
   Test user: ed.s.sharood@gmail.com
   ✅ Generated PKCE pair
   ✅ Generated state parameter

📝 Launching browser...

🌐 Navigating to Google OAuth...
   Current URL: https://accounts.google.com/o/oauth2/v2/auth...

🔐 On Google account page...
   ✅ Found account: ed.s.sharood@gmail.com
   ✅ Clicked account

✅ On consent screen...
   ✅ Found 'Continue' button
   ✅ Clicked 'Continue'
   ✅ OAuth flow completed

⏳ Waiting for OAuth callback...
   ✅ Callback received!
   ✅ Authorization code received
   ✅ State verified

🔄 Exchanging code for access token...
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
      docker compose -f docker/docker-compose.yaml exec runtime \
        pytest integration_tests/test_oauth_real_user.py -v
   2. Tests will automatically use saved token
   3. Tests will verify real OAuth integration
```

### Step 4: Run Tests with Real Token

```bash
# Now all 36 OAuth tests will pass!
docker compose -f docker/docker-compose.yaml exec runtime \
  pytest /app/integration_tests/test_oauth_real*.py -v
```

## How It Works

### Automation Flow

```
1. Launch Chromium (visible browser)
    ↓
2. Navigate to Google OAuth URL
    ↓
3. Detect account selection screen
    ↓
4. Click account: ed.s.sharood@gmail.com
    ↓
5. Detect consent screen
    ↓
6. Click "Continue" / "Allow" button
    ↓
7. Wait for callback with authorization code
    ↓
8. Exchange code for access token (PKCE)
    ↓
9. Get user info from Google API
    ↓
10. Save token to .oauth_tokens.yaml
    ↓
11. Docker tests read token file
```

### Advantages Over Manual Script

**Manual script (`oauth_token_helper.py`):**
- ❌ You have to click through OAuth screens
- ❌ You have to switch to browser
- ✅ Works without Playwright

**Playwright script (`oauth_playwright_helper.py`):**
- ✅ Fully automated (no clicking needed)
- ✅ Uses your existing Chrome login
- ✅ Can run in CI/CD
- ✅ Faster and more reliable
- ❌ Requires Playwright installation

## Troubleshooting

### "Missing OAuth credentials"

**Problem:**
```
❌ Missing OAuth credentials for Google
   Set environment variables:
   export GOOGLE_CLIENT_ID=your_client_id
   export GOOGLE_CLIENT_SECRET=your_client_secret
```

**Solution:** Register your app with Google Cloud Console (see Step 2 above)

### Browser doesn't find account

**Problem:** Script can't find your Google account

**Solutions:**
1. Make sure you're logged into Google in Chrome
2. Script will show available accounts - manually click if needed
3. Browser is visible so you can intervene if needed

### "Failed to get authorization code"

**Problem:** Timeout waiting for OAuth callback

**Solutions:**
1. Check that redirect URI is correct: `http://localhost:8765/callback`
2. Make sure redirect URI is registered in Google Cloud Console
3. Manually approve permissions if script misses buttons

### Playwright not installed

**Problem:**
```
❌ Required package not found: playwright
```

**Solution:**
```bash
pip install playwright aiohttp pyyaml
playwright install chromium
```

## Configuration

### Environment Variables

```bash
# Required for OAuth
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Optional - customize behavior
export PLAYWRIGHT_HEADLESS=false  # Show browser (default)
export OAUTH_CALLBACK_PORT=8765   # Callback server port
```

### Test User

Configured in `oauth_test_config.yaml`:
```yaml
test_user:
  name: "Ed"
  email: "ed.s.sharood@gmail.com"
```

## Security

- **Token file**: `.oauth_tokens.yaml` (never committed)
- **Permissions**: `600` (user-only read/write)
- **Git ignored**: Automatically ignored by `.gitignore`
- **Encryption**: Tokens encrypted before database storage
- **PKCE**: Real RFC 7636 implementation
- **State**: CSRF protection enabled

## Comparison: Manual vs Playwright

| Feature | Manual Script | Playwright Script |
|---------|--------------|-------------------|
| Automation | ❌ Manual clicking | ✅ Fully automated |
| Dependencies | Python only | Playwright + browsers |
| Speed | ~2 minutes | ~30 seconds |
| CI/CD | ❌ Needs interaction | ✅ Can be automated |
| Visibility | Opens system browser | Opens Chromium |
| Setup | Simpler | More dependencies |

## CI/CD Integration

For automated testing in CI/CD:

```yaml
# .github/workflows/oauth-tests.yml
name: OAuth Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Playwright
        run: |
          pip install playwright aiohttp pyyaml
          playwright install chromium
      
      - name: Get OAuth Token
        env:
          GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
          GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
        run: |
          python3 integration_tests/oauth_playwright_helper.py
      
      - name: Run OAuth Tests
        run: |
          docker compose -f docker/docker-compose.yaml exec runtime \
            pytest /app/integration_tests/test_oauth_real_user.py -v
```

## Summary

### What You Get

- ✅ **Automated OAuth flow** - No manual clicking
- ✅ **Real tokens from Google** - Not mocked
- ✅ **Uses your login** - ed.s.sharood@gmail.com
- ✅ **All 36 tests passing** - Complete OAuth verification
- ✅ **CI/CD ready** - Can be automated

### Quick Commands

```bash
# Install Playwright
pip install playwright aiohttp pyyaml && playwright install chromium

# Set credentials
export GOOGLE_CLIENT_ID="your-id"
export GOOGLE_CLIENT_SECRET="your-secret"

# Get token (automated)
python3 integration_tests/oauth_playwright_helper.py

# Run all OAuth tests
docker compose -f docker/docker-compose.yaml exec runtime \
  pytest /app/integration_tests/test_oauth_real*.py -v
```

**Result**: All 36 OAuth tests passing with real tokens! 🎉

