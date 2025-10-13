#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OAuth Token Helper - Get Real OAuth Tokens for Testing

This script helps obtain REAL OAuth tokens from the host machine for use in
Docker-based integration tests.

🚨 CRITICAL: NO MOCKING - This obtains REAL tokens from REAL OAuth providers

Usage:
    # On host machine (Mac/Linux):
    python3 integration_tests/oauth_token_helper.py --provider google
    
    # Token will be saved to: integration_tests/.oauth_tokens.yaml
    
    # Docker container will automatically read this file during tests

Workflow:
    1. Run this script on host machine
    2. Browser opens for OAuth authentication
    3. You authenticate with real provider
    4. Script receives real token and saves to file
    5. Docker reads token file during tests
    6. Tests use real token for integration testing

Supported Providers:
    - google
    - github
    - microsoft
    - facebook
"""

import os
import sys
import json
import yaml
import argparse
import webbrowser
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# OAuth provider configurations
PROVIDERS = {
    'google': {
        'name': 'Google',
        'authorize_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'scopes': ['openid', 'email', 'profile'],
        'client_id_env': 'GOOGLE_CLIENT_ID',
        'client_secret_env': 'GOOGLE_CLIENT_SECRET',
    },
    'github': {
        'name': 'GitHub',
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'scopes': ['user:email'],
        'client_id_env': 'GITHUB_CLIENT_ID',
        'client_secret_env': 'GITHUB_CLIENT_SECRET',
    },
    'microsoft': {
        'name': 'Microsoft',
        'authorize_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'scopes': ['openid', 'email', 'profile'],
        'client_id_env': 'MICROSOFT_CLIENT_ID',
        'client_secret_env': 'MICROSOFT_CLIENT_SECRET',
    },
}

# Local callback server
CALLBACK_HOST = 'localhost'
CALLBACK_PORT = 8765
REDIRECT_URI = f'http://{CALLBACK_HOST}:{CALLBACK_PORT}/callback'

# Token storage
TOKEN_FILE = os.path.join(os.path.dirname(__file__), '.oauth_tokens.yaml')


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


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to receive OAuth callback"""
    
    authorization_code = None
    state_received = None
    error = None
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass
    
    def do_GET(self):
        """Handle OAuth callback"""
        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Check for error
        if 'error' in params:
            OAuthCallbackHandler.error = params['error'][0]
            error_desc = params.get('error_description', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body>
                    <h1>❌ OAuth Error</h1>
                    <p><strong>Error:</strong> {OAuthCallbackHandler.error}</p>
                    <p><strong>Description:</strong> {error_desc}</p>
                    <p>You can close this window.</p>
                </body>
                </html>
            """.encode())
            return
        
        # Get authorization code
        if 'code' in params:
            OAuthCallbackHandler.authorization_code = params['code'][0]
            OAuthCallbackHandler.state_received = params.get('state', [None])[0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1 style="color: green;">&#x2705; OAuth Success!</h1>
                    <p>Authorization received. You can close this window.</p>
                    <script>window.close();</script>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>&#x274c; Missing Authorization Code</h1>
                    <p>No authorization code received. You can close this window.</p>
                </body>
                </html>
            """)


def exchange_code_for_token(provider_config, code, code_verifier):
    """Exchange authorization code for access token (real OAuth flow)"""
    import requests
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': provider_config['client_id'],
        'client_secret': provider_config['client_secret'],
        'code_verifier': code_verifier,
    }
    
    # Some providers need different headers
    headers = {'Accept': 'application/json'}
    
    print(f"   🔄 Exchanging authorization code for access token...")
    response = requests.post(
        provider_config['token_url'],
        data=data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"   ❌ Token exchange failed: {response.status_code}")
        print(f"      Response: {response.text}")
        return None
    
    token_data = response.json()
    print(f"   ✅ Token received!")
    return token_data


def get_user_info(provider_name, access_token):
    """Get user info from OAuth provider (real API call)"""
    import requests
    
    # Provider-specific user info endpoints
    user_info_urls = {
        'google': 'https://www.googleapis.com/oauth2/v2/userinfo',
        'github': 'https://api.github.com/user',
        'microsoft': 'https://graph.microsoft.com/v1.0/me',
    }
    
    if provider_name not in user_info_urls:
        return None
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    print(f"   🔄 Fetching user info...")
    response = requests.get(user_info_urls[provider_name], headers=headers)
    
    if response.status_code != 200:
        print(f"   ⚠️  Could not fetch user info: {response.status_code}")
        return None
    
    user_info = response.json()
    print(f"   ✅ User info retrieved!")
    return user_info


def obtain_token(provider_name):
    """
    Obtain real OAuth token from provider (real OAuth flow)
    
    This opens a browser, authenticates with real provider, and receives real token.
    NO MOCKING - this is a complete real OAuth 2.0 PKCE flow.
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
    
    print(f"\n🔐 Obtaining OAuth token from {provider_config['name']}...")
    print(f"   Provider: {provider_name}")
    print(f"   Redirect URI: {REDIRECT_URI}")
    
    # Generate PKCE pair (real cryptography)
    code_verifier, code_challenge = generate_pkce_pair()
    print(f"   ✅ Generated PKCE pair")
    
    # Generate state (CSRF protection)
    state = generate_state()
    print(f"   ✅ Generated state parameter")
    
    # Build authorization URL
    auth_params = {
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(provider_config['scopes']),
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
    }
    
    # Provider-specific parameters
    if provider_name == 'google':
        auth_params['access_type'] = 'offline'
        auth_params['prompt'] = 'consent'
    
    auth_url = f"{provider_config['authorize_url']}?{urlencode(auth_params)}"
    
    print(f"\n📝 Step 1: Starting local callback server on {CALLBACK_HOST}:{CALLBACK_PORT}")
    
    # Start local HTTP server to receive callback
    server = HTTPServer((CALLBACK_HOST, CALLBACK_PORT), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.daemon = True
    server_thread.start()
    
    print(f"   ✅ Callback server started")
    
    print(f"\n🌐 Step 2: Opening browser for authentication...")
    print(f"   If browser doesn't open, visit this URL:")
    print(f"   {auth_url}")
    
    # Open browser
    webbrowser.open(auth_url)
    
    print(f"\n⏳ Step 3: Waiting for authentication...")
    print(f"   Please complete authentication in your browser...")
    
    # Wait for callback
    server_thread.join(timeout=120)  # 2 minute timeout
    server.server_close()
    
    # Check for errors
    if OAuthCallbackHandler.error:
        print(f"❌ OAuth error: {OAuthCallbackHandler.error}")
        return None
    
    if not OAuthCallbackHandler.authorization_code:
        print(f"❌ No authorization code received. Authentication may have timed out.")
        return None
    
    # Verify state (CSRF protection)
    if OAuthCallbackHandler.state_received != state:
        print(f"❌ State mismatch! Possible CSRF attack.")
        print(f"   Expected: {state}")
        print(f"   Received: {OAuthCallbackHandler.state_received}")
        return None
    
    print(f"   ✅ Authorization code received")
    print(f"   ✅ State verified")
    
    # Exchange code for token (real OAuth flow)
    print(f"\n🔄 Step 4: Exchanging code for access token...")
    token_data = exchange_code_for_token(
        provider_config,
        OAuthCallbackHandler.authorization_code,
        code_verifier
    )
    
    if not token_data:
        print(f"❌ Failed to obtain access token")
        return None
    
    # Get user info (optional but useful for testing)
    user_info = get_user_info(provider_name, token_data['access_token'])
    
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
        email = user_info.get('email', user_info.get('login', 'N/A'))
        name = user_info.get('name', user_info.get('login', 'N/A'))
        print(f"   User: {name}")
        print(f"   Email: {email}")
    
    return result


def save_token(provider_name, token_data):
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


def main():
    parser = argparse.ArgumentParser(
        description='Obtain real OAuth tokens for Docker testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get Google OAuth token
  python3 integration_tests/oauth_token_helper.py --provider google
  
  # Get GitHub OAuth token  
  python3 integration_tests/oauth_token_helper.py --provider github
  
  # Show saved tokens
  python3 integration_tests/oauth_token_helper.py --show

Required Environment Variables:
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET       (for Google)
  GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET       (for GitHub)
  MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET (for Microsoft)
  
Workflow:
  1. Run this script on host machine (Mac/Linux)
  2. Browser opens for OAuth authentication
  3. Complete authentication with real provider
  4. Script saves token to .oauth_tokens.yaml
  5. Docker reads this file during integration tests
  6. Tests use real token for integration testing
        """
    )
    
    parser.add_argument(
        '--provider',
        choices=list(PROVIDERS.keys()),
        help='OAuth provider to authenticate with'
    )
    
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show saved tokens'
    )
    
    args = parser.parse_args()
    
    if args.show:
        if not os.path.exists(TOKEN_FILE):
            print(f"No tokens saved yet.")
            print(f"Run with --provider to obtain tokens.")
            return
        
        with open(TOKEN_FILE, 'r') as f:
            tokens = yaml.safe_load(f) or {}
        
        print(f"\n📋 Saved OAuth Tokens ({TOKEN_FILE}):\n")
        for provider, data in tokens.items():
            print(f"  {provider}:")
            print(f"    Obtained: {data.get('obtained_at', 'N/A')}")
            print(f"    Expires: {data.get('expires_at', 'N/A')}")
            if 'user_info' in data:
                email = data['user_info'].get('email', data['user_info'].get('login', 'N/A'))
                print(f"    User: {email}")
            print()
        return
    
    if not args.provider:
        parser.print_help()
        return
    
    # Check for required packages
    try:
        import requests
    except ImportError:
        print(f"❌ Required package not found: requests")
        print(f"   Install with: pip install requests")
        return
    
    # Obtain token
    token_data = obtain_token(args.provider)
    
    if token_data:
        save_token(args.provider, token_data)
        print(f"\n🎉 Done! Token ready for Docker testing.")
        print(f"\n📖 Next steps:")
        print(f"   1. Run tests in Docker:")
        print(f"      docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_oauth_real_user.py -v")
        print(f"   2. Tests will automatically use saved token")
        print(f"   3. Tests will verify real OAuth integration")
    else:
        print(f"\n❌ Failed to obtain token. Check error messages above.")
        return 1


if __name__ == '__main__':
    sys.exit(main() or 0)

