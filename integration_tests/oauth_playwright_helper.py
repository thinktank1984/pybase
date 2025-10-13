#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OAuth Token Helper with Playwright - Automated OAuth Flow

This script uses Playwright to automate the OAuth flow with Google.
Since you're already logged into Chrome, it will:
1. Navigate to Google OAuth page
2. Click "Continue" (you're already logged in)
3. Approve permissions
4. Capture the real OAuth token
5. Save it for Docker tests

🚨 NO MOCKING - This gets REAL tokens from REAL Google OAuth

Usage:
    python3 integration_tests/oauth_playwright_helper.py

Requirements:
    - Playwright installed: pip install playwright
    - Browsers installed: playwright install chromium
    - Google OAuth credentials in environment
    - Already logged into Google in your browser (or will prompt)
"""

import os
import sys
import yaml
import asyncio
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
from playwright.async_api import async_playwright, Page, BrowserContext
import json

# OAuth provider configurations
PROVIDERS = {
    'google': {
        'name': 'Google',
        'authorize_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
        'scopes': ['openid', 'email', 'profile'],
        'client_id_env': 'GOOGLE_CLIENT_ID',
        'client_secret_env': 'GOOGLE_CLIENT_SECRET',
    },
}

# Token storage
TOKEN_FILE = os.path.join(os.path.dirname(__file__), '.oauth_tokens.yaml')

# Test user configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'oauth_test_config.yaml')


def load_test_config():
    """Load test configuration"""
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)


def generate_pkce_pair():
    """Generate PKCE code verifier and challenge (real cryptography)"""
    # Generate verifier (RFC 7636)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Generate challenge (SHA256)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, challenge


def generate_state():
    """Generate state parameter (CSRF protection)"""
    return secrets.token_urlsafe(32)


async def exchange_code_for_token(provider_config, code, code_verifier, redirect_uri):
    """Exchange authorization code for access token (real OAuth flow)"""
    import aiohttp
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': provider_config['client_id'],
        'client_secret': provider_config['client_secret'],
        'code_verifier': code_verifier,
    }
    
    print(f"   🔄 Exchanging authorization code for access token...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            provider_config['token_url'],
            data=data,
            headers={'Accept': 'application/json'}
        ) as response:
            if response.status != 200:
                text = await response.text()
                print(f"   ❌ Token exchange failed: {response.status}")
                print(f"      Response: {text}")
                return None
            
            token_data = await response.json()
            print(f"   ✅ Token received!")
            return token_data


async def get_user_info(provider_name, access_token):
    """Get user info from OAuth provider (real API call)"""
    import aiohttp
    
    provider_config = PROVIDERS[provider_name]
    headers = {'Authorization': f'Bearer {access_token}'}
    
    print(f"   🔄 Fetching user info...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(provider_config['user_info_url'], headers=headers) as response:
            if response.status != 200:
                print(f"   ⚠️  Could not fetch user info: {response.status}")
                return None
            
            user_info = await response.json()
            print(f"   ✅ User info retrieved!")
            return user_info


async def wait_for_oauth_callback(page: Page, state: str, timeout: int = 120000):
    """
    Wait for OAuth callback URL with authorization code.
    
    This waits for Google to redirect back with the authorization code.
    """
    print(f"\n⏳ Waiting for OAuth callback...")
    
    try:
        # Wait for navigation to callback URL or localhost (if using local server)
        await page.wait_for_url(
            lambda url: 'code=' in url or 'localhost' in url,
            timeout=timeout
        )
        
        current_url = page.url
        print(f"   ✅ Callback received!")
        print(f"      URL: {current_url[:100]}...")
        
        # Parse authorization code from URL
        parsed = urlparse(current_url)
        params = parse_qs(parsed.query)
        
        if 'error' in params:
            error = params['error'][0]
            error_desc = params.get('error_description', ['Unknown'])[0]
            print(f"   ❌ OAuth error: {error}")
            print(f"      Description: {error_desc}")
            return None, None
        
        if 'code' not in params:
            print(f"   ❌ No authorization code in callback URL")
            return None, None
        
        code = params['code'][0]
        state_received = params.get('state', [None])[0]
        
        # Verify state (CSRF protection)
        if state_received != state:
            print(f"   ❌ State mismatch! Possible CSRF attack.")
            print(f"      Expected: {state}")
            print(f"      Received: {state_received}")
            return None, None
        
        print(f"   ✅ Authorization code received")
        print(f"   ✅ State verified")
        
        return code, current_url
        
    except Exception as e:
        print(f"   ❌ Timeout or error waiting for callback: {e}")
        return None, None


async def automate_google_oauth(page: Page, auth_url: str, test_email: str):
    """
    Automate Google OAuth flow with Playwright.
    
    This handles:
    - Navigating to OAuth URL
    - Selecting account (if multiple)
    - Approving permissions
    - Waiting for callback
    """
    print(f"\n🌐 Navigating to Google OAuth...")
    print(f"   URL: {auth_url[:100]}...")
    
    await page.goto(auth_url, wait_until='networkidle')
    
    # Wait a moment for page to load
    await asyncio.sleep(2)
    
    # Check if we're on Google login page
    current_url = page.url
    print(f"   Current URL: {current_url[:100]}...")
    
    # Handle account selection (if multiple accounts)
    if 'accounts.google.com' in current_url:
        print(f"\n🔐 On Google account page...")
        
        # Look for account with test email
        try:
            # Try to find the account button with the test email
            account_selector = f'[data-email="{test_email}"]'
            account_element = page.locator(account_selector)
            
            if await account_element.count() > 0:
                print(f"   ✅ Found account: {test_email}")
                await account_element.click()
                print(f"   ✅ Clicked account")
                await page.wait_for_load_state('networkidle')
            else:
                # Try alternative selectors
                print(f"   Looking for account with different selector...")
                
                # Try clicking any account div
                account_divs = page.locator('div[data-identifier]')
                count = await account_divs.count()
                
                if count > 0:
                    print(f"   Found {count} accounts")
                    # Click first one (assuming you're already logged in)
                    await account_divs.first.click()
                    print(f"   ✅ Clicked first account")
                    await page.wait_for_load_state('networkidle')
                else:
                    print(f"   ℹ️  No account selection needed - already logged in")
        
        except Exception as e:
            print(f"   ℹ️  Account selection: {e}")
            # Continue anyway - might already be logged in
    
    # Wait a moment for any redirects
    await asyncio.sleep(2)
    
    # Check for consent screen
    current_url = page.url
    print(f"   Current URL: {current_url[:100]}...")
    
    if 'consent' in current_url or 'oauth2' in current_url:
        print(f"\n✅ On consent screen...")
        
        # Look for "Continue" or "Allow" button
        try:
            # Try various button texts
            button_texts = ['Continue', 'Allow', 'Accept', 'Consent']
            
            for button_text in button_texts:
                try:
                    button = page.locator(f'button:has-text("{button_text}")')
                    if await button.count() > 0:
                        print(f"   ✅ Found '{button_text}' button")
                        await button.click()
                        print(f"   ✅ Clicked '{button_text}'")
                        break
                except:
                    continue
            
            # Wait for navigation
            await page.wait_for_load_state('networkidle')
            
        except Exception as e:
            print(f"   ℹ️  Consent handling: {e}")
            # Continue - might auto-approve
    
    print(f"   ✅ OAuth flow completed")


async def obtain_token_with_playwright(provider_name: str):
    """
    Obtain real OAuth token using Playwright automation.
    
    This opens a real browser, navigates through OAuth flow, and captures token.
    NO MOCKING - complete real OAuth 2.0 PKCE flow.
    """
    if provider_name not in PROVIDERS:
        print(f"❌ Unknown provider: {provider_name}")
        print(f"   Available providers: {', '.join(PROVIDERS.keys())}")
        return None
    
    provider_config = PROVIDERS[provider_name].copy()
    
    # Get credentials from environment
    client_id = os.environ.get(provider_config['client_id_env'])
    client_secret = os.environ.get(provider_config['client_secret_env'])
    
    if not client_id or not client_secret:
        print(f"❌ Missing OAuth credentials for {provider_config['name']}")
        print(f"   Set environment variables:")
        print(f"   export {provider_config['client_id_env']}=your_client_id")
        print(f"   export {provider_config['client_secret_env']}=your_client_secret")
        return None
    
    provider_config['client_id'] = client_id
    provider_config['client_secret'] = client_secret
    
    # Load test configuration for user email
    test_config = load_test_config()
    test_email = test_config['test_user']['email']
    
    print(f"\n🔐 Obtaining OAuth token from {provider_config['name']} with Playwright...")
    print(f"   Provider: {provider_name}")
    print(f"   Test user: {test_email}")
    
    # Generate PKCE pair (real cryptography)
    code_verifier, code_challenge = generate_pkce_pair()
    print(f"   ✅ Generated PKCE pair")
    
    # Generate state (CSRF protection)
    state = generate_state()
    print(f"   ✅ Generated state parameter")
    
    # Use a special redirect URI that we can detect
    redirect_uri = 'http://localhost:8765/callback'
    
    # Build authorization URL
    auth_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(provider_config['scopes']),
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    
    auth_url = f"{provider_config['authorize_url']}?{urlencode(auth_params)}"
    
    # Launch Playwright
    async with async_playwright() as p:
        print(f"\n📝 Launching browser...")
        
        # Launch browser (visible so you can see what's happening)
        browser = await p.chromium.launch(
            headless=False,  # Visible browser
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        # Create context (use existing login if available)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
        )
        
        page = await context.new_page()
        
        try:
            # Automate OAuth flow
            await automate_google_oauth(page, auth_url, test_email)
            
            # Wait for OAuth callback with authorization code
            code, callback_url = await wait_for_oauth_callback(page, state, timeout=120000)
            
            if not code:
                print(f"❌ Failed to get authorization code")
                await browser.close()
                return None
            
            # Close browser
            await browser.close()
            
            # Exchange code for token (real OAuth flow)
            print(f"\n🔄 Exchanging code for access token...")
            token_data = await exchange_code_for_token(
                provider_config,
                code,
                code_verifier,
                redirect_uri
            )
            
            if not token_data:
                print(f"❌ Failed to obtain access token")
                return None
            
            # Get user info (optional but useful for testing)
            user_info = await get_user_info(provider_name, token_data['access_token'])
            
            # Prepare token data for storage
            result = {
                'provider': provider_name,
                'access_token': token_data['access_token'],
                'token_type': token_data.get('token_type', 'Bearer'),
                'scope': token_data.get('scope', ' '.join(provider_config['scopes'])),
                'obtained_at': datetime.now().isoformat(),
            }
            
            if 'refresh_token' in token_data:
                result['refresh_token'] = token_data['refresh_token']
            
            if 'expires_in' in token_data:
                expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
                result['expires_at'] = expires_at.isoformat()
            
            if user_info:
                result['user_info'] = user_info
            
            print(f"\n✅ Token obtained successfully!")
            if user_info:
                email = user_info.get('email', 'N/A')
                name = user_info.get('name', 'N/A')
                print(f"   User: {name}")
                print(f"   Email: {email}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during OAuth flow: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()
            return None


def save_token(provider_name: str, token_data: dict):
    """Save token to file for Docker to read"""
    # Load existing tokens
    tokens = {}
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            tokens = yaml.safe_load(f) or {}
    
    # Add/update token
    tokens[provider_name] = token_data
    
    # Save to file
    with open(TOKEN_FILE, 'w') as f:
        yaml.dump(tokens, f, default_flow_style=False)
    
    print(f"\n💾 Token saved to: {TOKEN_FILE}")
    print(f"   Docker will read this file during tests")
    
    # Set file permissions (readable by user only)
    os.chmod(TOKEN_FILE, 0o600)
    print(f"   ✅ File permissions set to 600 (user-only)")


async def main():
    """Main entry point"""
    print(f"🚀 OAuth Token Helper with Playwright\n")
    print(f"=" * 60)
    print(f"This script automates the OAuth flow using Playwright.")
    print(f"It will open a browser and complete the OAuth process.")
    print(f"=" * 60)
    
    # Check for required packages
    try:
        from playwright.async_api import async_playwright
        import aiohttp
    except ImportError as e:
        print(f"❌ Required package not found: {e}")
        print(f"   Install with:")
        print(f"   pip install playwright aiohttp pyyaml")
        print(f"   playwright install chromium")
        return 1
    
    provider_name = 'google'
    
    # Obtain token
    token_data = await obtain_token_with_playwright(provider_name)
    
    if token_data:
        save_token(provider_name, token_data)
        print(f"\n🎉 Done! Token ready for Docker testing.")
        print(f"\n📖 Next steps:")
        print(f"   1. Run tests in Docker:")
        print(f"      docker compose -f docker/docker-compose.yaml exec runtime \\")
        print(f"        pytest integration_tests/test_oauth_real_user.py -v")
        print(f"   2. Tests will automatically use saved token")
        print(f"   3. Tests will verify real OAuth integration")
        return 0
    else:
        print(f"\n❌ Failed to obtain token. Check error messages above.")
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))

