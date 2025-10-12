# Implementation Tasks

## 1. Database Models (12 tasks)

- [ ] 1.1 Create OAuthAccount model
  - [ ] 1.1.1 Add OAuthAccount class inheriting from Model and ActiveRecord
  - [ ] 1.1.2 Define fields: user (reference), provider, provider_user_id, email, created_at
  - [ ] 1.1.3 Add profile_data JSON field for provider-specific data
  - [ ] 1.1.4 Add unique constraint on (provider, provider_user_id)
  - [ ] 1.1.5 Add belongs_to relationship to User
  - [ ] 1.1.6 Add get_by_provider() method

- [ ] 1.2 Create OAuthToken model
  - [ ] 1.2.1 Add OAuthToken class inheriting from Model and ActiveRecord
  - [ ] 1.2.2 Define fields: oauth_account (reference), access_token_encrypted, refresh_token_encrypted
  - [ ] 1.2.3 Add expiry fields: access_token_expires_at, refresh_token_expires_at
  - [ ] 1.2.4 Add token_type, scope fields
  - [ ] 1.2.5 Add encryption/decryption methods
  - [ ] 1.2.6 Add is_expired() and needs_refresh() methods

## 2. OAuth Core Implementation (15 tasks)

- [ ] 2.1 Create base OAuth provider class
  - [ ] 2.1.1 Create runtime/auth/providers/base.py
  - [ ] 2.1.2 Define BaseOAuthProvider abstract class
  - [ ] 2.1.3 Implement generate_pkce_pair() method
  - [ ] 2.1.4 Implement generate_state() method
  - [ ] 2.1.5 Implement build_authorization_url() method
  - [ ] 2.1.6 Implement exchange_code_for_tokens() method
  - [ ] 2.1.7 Implement validate_state() method
  - [ ] 2.1.8 Implement get_user_info() abstract method

- [ ] 2.2 Create OAuth manager
  - [ ] 2.2.1 Create runtime/auth/oauth.py
  - [ ] 2.2.2 Create OAuthManager class
  - [ ] 2.2.3 Implement provider registration system
  - [ ] 2.2.4 Implement get_provider() method
  - [ ] 2.2.5 Implement list_enabled_providers() method
  - [ ] 2.2.6 Add provider configuration loading

- [ ] 2.3 Implement token encryption
  - [ ] 2.3.1 Create runtime/auth/tokens.py
  - [ ] 2.3.2 Initialize Fernet encryption key
  - [ ] 2.3.3 Implement encrypt_token() function
  - [ ] 2.3.4 Implement decrypt_token() function
  - [ ] 2.3.5 Add key rotation support

## 3. Google OAuth Provider (8 tasks)

- [ ] 3.1 Implement Google OAuth provider
  - [ ] 3.1.1 Create runtime/auth/providers/google.py
  - [ ] 3.1.2 Extend BaseOAuthProvider
  - [ ] 3.1.3 Configure Google endpoints (authorize, token, userinfo)
  - [ ] 3.1.4 Implement get_user_info() with Google-specific logic
  - [ ] 3.1.5 Handle Google-specific profile fields
  - [ ] 3.1.6 Add Google One Tap support (optional)
  - [ ] 3.1.7 Handle Google token refresh
  - [ ] 3.1.8 Add error handling for Google-specific errors

## 4. GitHub OAuth Provider (8 tasks)

- [ ] 4.1 Implement GitHub OAuth provider
  - [ ] 4.1.1 Create runtime/auth/providers/github.py
  - [ ] 4.1.2 Extend BaseOAuthProvider
  - [ ] 4.1.3 Configure GitHub endpoints
  - [ ] 4.1.4 Implement get_user_info() for GitHub API
  - [ ] 4.1.5 Handle multiple email addresses from GitHub
  - [ ] 4.1.6 Select primary/verified email
  - [ ] 4.1.7 Handle GitHub token refresh
  - [ ] 4.1.8 Add error handling for GitHub-specific errors

## 5. Microsoft OAuth Provider (8 tasks)

- [ ] 5.1 Implement Microsoft OAuth provider
  - [ ] 5.1.1 Create runtime/auth/providers/microsoft.py
  - [ ] 5.1.2 Extend BaseOAuthProvider
  - [ ] 5.1.3 Configure Microsoft Identity Platform endpoints
  - [ ] 5.1.4 Implement get_user_info() using Microsoft Graph
  - [ ] 5.1.5 Handle personal vs work/school accounts
  - [ ] 5.1.6 Support tenant-specific configurations
  - [ ] 5.1.7 Handle Microsoft token refresh
  - [ ] 5.1.8 Add error handling for Microsoft-specific errors

## 6. Facebook OAuth Provider (8 tasks)

- [ ] 6.1 Implement Facebook OAuth provider
  - [ ] 6.1.1 Create runtime/auth/providers/facebook.py
  - [ ] 6.1.2 Extend BaseOAuthProvider
  - [ ] 6.1.3 Configure Facebook Login endpoints
  - [ ] 6.1.4 Implement get_user_info() for Facebook Graph API
  - [ ] 6.1.5 Handle users without email addresses
  - [ ] 6.1.6 Comply with Facebook Platform policies
  - [ ] 6.1.7 Handle Facebook token refresh
  - [ ] 6.1.8 Add error handling for Facebook-specific errors

## 7. Account Linking Logic (10 tasks)

- [ ] 7.1 Implement account linking
  - [ ] 7.1.1 Create runtime/auth/linking.py
  - [ ] 7.1.2 Implement find_existing_user_by_email() function
  - [ ] 7.1.3 Implement link_oauth_account() function
  - [ ] 7.1.4 Implement unlink_oauth_account() function
  - [ ] 7.1.5 Add validation to prevent disconnecting last auth method
  - [ ] 7.1.6 Implement email conflict detection
  - [ ] 7.1.7 Create link_accounts_workflow() for guided linking
  - [ ] 7.1.8 Add prevent_duplicate_links() validation
  - [ ] 7.1.9 Implement get_user_oauth_accounts() query
  - [ ] 7.1.10 Add audit logging for linking events

## 8. OAuth Routes and Handlers (12 tasks)

- [ ] 8.1 Create OAuth authorization routes
  - [ ] 8.1.1 Add route /auth/oauth/<provider>/login
  - [ ] 8.1.2 Generate and store state in session
  - [ ] 8.1.3 Generate PKCE code_verifier and code_challenge
  - [ ] 8.1.4 Store code_verifier in session
  - [ ] 8.1.5 Build authorization URL with correct parameters
  - [ ] 8.1.6 Redirect user to provider

- [ ] 8.2 Create OAuth callback handler
  - [ ] 8.2.1 Add route /auth/oauth/<provider>/callback
  - [ ] 8.2.2 Validate state parameter
  - [ ] 8.2.3 Handle authorization errors from provider
  - [ ] 8.2.4 Exchange authorization code for tokens
  - [ ] 8.2.5 Retrieve user info from provider
  - [ ] 8.2.6 Create or update user account
  - [ ] 8.2.7 Store encrypted tokens
  - [ ] 8.2.8 Create user session
  - [ ] 8.2.9 Redirect to intended destination
  - [ ] 8.2.10 Handle email conflicts
  - [ ] 8.2.11 Log successful authentication
  - [ ] 8.2.12 Handle errors gracefully

## 9. User Model Extensions (8 tasks)

- [ ] 9.1 Add OAuth methods to User model
  - [ ] 9.1.1 Add get_oauth_accounts() method
  - [ ] 9.1.2 Add has_oauth_account(provider) method
  - [ ] 9.1.3 Add get_oauth_account(provider) method
  - [ ] 9.1.4 Add link_oauth_account(oauth_account) method
  - [ ] 9.1.5 Add unlink_oauth_account(provider) method
  - [ ] 9.1.6 Add can_unlink_oauth(provider) validation method
  - [ ] 9.1.7 Add get_auth_methods() method returning all auth types
  - [ ] 9.1.8 Add last_oauth_login_provider field

## 10. UI Templates - Login/Signup (12 tasks)

- [ ] 10.1 Update login template
  - [ ] 10.1.1 Add social login buttons section
  - [ ] 10.1.2 Create social_login_buttons.html partial
  - [ ] 10.1.3 Add visual separator between OAuth and password login
  - [ ] 10.1.4 Style OAuth buttons with provider colors
  - [ ] 10.1.5 Add provider logos to buttons
  - [ ] 10.1.6 Make responsive for mobile

- [ ] 10.2 Update signup template
  - [ ] 10.2.1 Add social signup buttons at top
  - [ ] 10.2.2 Reuse social_login_buttons.html partial
  - [ ] 10.2.3 Add "or sign up with email" text
  - [ ] 10.2.4 Ensure Terms of Service applies to both methods
  - [ ] 10.2.5 Make responsive for mobile
  - [ ] 10.2.6 Add loading states for OAuth buttons

## 11. UI Templates - Account Management (10 tasks)

- [ ] 11.1 Create account settings template
  - [ ] 11.1.1 Create templates/auth/account_settings.html
  - [ ] 11.1.2 Add "Connected Accounts" section
  - [ ] 11.1.3 Display list of linked OAuth providers
  - [ ] 11.1.4 Show connection status and dates
  - [ ] 11.1.5 Add "Connect" buttons for unlinked providers
  - [ ] 11.1.6 Add "Disconnect" buttons for linked providers
  - [ ] 11.1.7 Disable disconnect for last auth method
  - [ ] 11.1.8 Add tooltips explaining requirements
  - [ ] 11.1.9 Show last used timestamp per provider
  - [ ] 11.1.10 Add section for password management

## 12. UI Templates - OAuth Callback (6 tasks)

- [ ] 12.1 Create OAuth callback templates
  - [ ] 12.1.1 Create templates/auth/oauth_callback.html
  - [ ] 12.1.2 Add loading spinner with "Completing sign in..."
  - [ ] 12.1.3 Create templates/auth/oauth_error.html
  - [ ] 12.1.4 Display user-friendly error messages
  - [ ] 12.1.5 Offer options to retry or use different method
  - [ ] 12.1.6 Create templates/auth/link_accounts.html for conflicts

## 13. Static Assets (8 tasks)

- [ ] 13.1 Add OAuth provider assets
  - [ ] 13.1.1 Add Google logo SVG to static/images/oauth/
  - [ ] 13.1.2 Add GitHub logo SVG
  - [ ] 13.1.3 Add Microsoft logo SVG
  - [ ] 13.1.4 Add Facebook logo SVG
  - [ ] 13.1.5 Create CSS for OAuth buttons (static/css/oauth.css)
  - [ ] 13.1.6 Add loading animations
  - [ ] 13.1.7 Ensure proper licensing for all logos
  - [ ] 13.1.8 Optimize assets for web delivery

## 14. Configuration (10 tasks)

- [ ] 14.1 Add OAuth configuration system
  - [ ] 14.1.1 Create OAuth configuration dictionary in app.py
  - [ ] 14.1.2 Load OAuth settings from environment variables
  - [ ] 14.1.3 Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
  - [ ] 14.1.4 Add GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET
  - [ ] 14.1.5 Add MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET
  - [ ] 14.1.6 Add FACEBOOK_APP_ID and FACEBOOK_APP_SECRET
  - [ ] 14.1.7 Add OAUTH_ENCRYPTION_KEY for token encryption
  - [ ] 14.1.8 Add per-provider enable/disable flags
  - [ ] 14.1.9 Configure redirect URLs per environment
  - [ ] 14.1.10 Create .env.example with OAuth settings

## 15. Security Implementation (12 tasks)

- [ ] 15.1 Implement PKCE
  - [ ] 15.1.1 Generate cryptographically secure code_verifier
  - [ ] 15.1.2 Generate code_challenge using SHA-256
  - [ ] 15.1.3 Store code_verifier securely in session
  - [ ] 15.1.4 Send code_challenge in authorization request
  - [ ] 15.1.5 Send code_verifier in token exchange
  - [ ] 15.1.6 Validate PKCE flow completion

- [ ] 15.2 Implement state validation
  - [ ] 15.2.1 Generate random state parameter
  - [ ] 15.2.2 Store state in session with timestamp
  - [ ] 15.2.3 Include state in authorization URL
  - [ ] 15.2.4 Validate state matches on callback
  - [ ] 15.2.5 Expire old state values (5 minutes)
  - [ ] 15.2.6 Log CSRF attempts

## 16. Rate Limiting (8 tasks)

- [ ] 16.1 Add OAuth rate limiting
  - [ ] 16.1.1 Install rate limiting library if needed
  - [ ] 16.1.2 Add rate limit to authorization endpoint (10/minute per IP)
  - [ ] 16.1.3 Add rate limit to callback endpoint (20/minute per session)
  - [ ] 16.1.4 Add rate limit to account linking (5/minute per user)
  - [ ] 16.1.5 Return 429 Too Many Requests on limit
  - [ ] 16.1.6 Add user-friendly rate limit messages
  - [ ] 16.1.7 Log rate limit violations
  - [ ] 16.1.8 Add rate limit metrics to monitoring

## 17. Token Management (10 tasks)

- [ ] 17.1 Implement token refresh
  - [ ] 17.1.1 Create refresh_oauth_token() function
  - [ ] 17.1.2 Check token expiry before use
  - [ ] 17.1.3 Use refresh token to get new access token
  - [ ] 17.1.4 Update stored tokens with new values
  - [ ] 17.1.5 Handle refresh token expiry (re-auth required)
  - [ ] 17.1.6 Log token refresh events

- [ ] 17.2 Token cleanup
  - [ ] 17.2.1 Create cleanup job for expired tokens
  - [ ] 17.2.2 Delete tokens older than retention period
  - [ ] 17.2.3 Revoke tokens with provider on deletion (optional)
  - [ ] 17.2.4 Schedule cleanup to run daily

## 18. Error Handling and Logging (12 tasks)

- [ ] 18.1 Add OAuth error handling
  - [ ] 18.1.1 Handle "access_denied" error from provider
  - [ ] 18.1.2 Handle invalid authorization code
  - [ ] 18.1.3 Handle token exchange failures
  - [ ] 18.1.4 Handle user info retrieval failures
  - [ ] 18.1.5 Handle provider API unavailability
  - [ ] 18.1.6 Handle timeout errors
  - [ ] 18.1.7 Display user-friendly error messages
  - [ ] 18.1.8 Log all errors with context

- [ ] 18.2 Add OAuth audit logging
  - [ ] 18.2.1 Log OAuth authorization initiations
  - [ ] 18.2.2 Log successful authentications
  - [ ] 18.2.3 Log failed authentications
  - [ ] 18.2.4 Log account linking/unlinking events
  - [ ] 18.2.5 Log CSRF/security events

## 19. Testing (20 tasks)

- [ ] 19.1 Unit tests for OAuth core
  - [ ] 19.1.1 Test PKCE generation and validation
  - [ ] 19.1.2 Test state generation and validation
  - [ ] 19.1.3 Test authorization URL building
  - [ ] 19.1.4 Test token encryption/decryption
  - [ ] 19.1.5 Test provider base class

- [ ] 19.2 Unit tests for providers
  - [ ] 19.2.1 Test Google provider implementation
  - [ ] 19.2.2 Test GitHub provider implementation
  - [ ] 19.2.3 Test Microsoft provider implementation
  - [ ] 19.2.4 Test Facebook provider implementation

- [ ] 19.3 Integration tests
  - [ ] 19.3.1 Test full OAuth flow (mocked providers)
  - [ ] 19.3.2 Test account creation via OAuth
  - [ ] 19.3.3 Test account linking flow
  - [ ] 19.3.4 Test email conflict resolution
  - [ ] 19.3.5 Test disconnecting OAuth accounts
  - [ ] 19.3.6 Test token refresh flow
  - [ ] 19.3.7 Test rate limiting
  - [ ] 19.3.8 Test error handling

- [ ] 19.4 Security tests
  - [ ] 19.4.1 Test CSRF protection (state validation)
  - [ ] 19.4.2 Test PKCE validation
  - [ ] 19.4.3 Test authorization code reuse prevention
  - [ ] 19.4.4 Test token encryption
  - [ ] 19.4.5 Test redirect URL validation

- [ ] 19.5 UI tests
  - [ ] 19.5.1 Test social login buttons display
  - [ ] 19.5.2 Test account settings page
  - [ ] 19.5.3 Test OAuth callback processing UI

## 20. Documentation and Deployment (13 tasks)

- [ ] 20.1 Write documentation
  - [ ] 20.1.1 Document OAuth setup for developers
  - [ ] 20.1.2 Document how to configure each provider
  - [ ] 20.1.3 Document obtaining OAuth credentials
  - [ ] 20.1.4 Document security considerations
  - [ ] 20.1.5 Document account linking for users
  - [ ] 20.1.6 Create troubleshooting guide
  - [ ] 20.1.7 Document environment variables

- [ ] 20.2 Create deployment artifacts
  - [ ] 20.2.1 Update requirements.txt with OAuth dependencies
  - [ ] 20.2.2 Create database migration for new models
  - [ ] 20.2.3 Update .env.example with OAuth config
  - [ ] 20.2.4 Create setup script for OAuth initialization

- [ ] 20.3 Deploy and monitor
  - [ ] 20.3.1 Deploy to staging environment
  - [ ] 20.3.2 Test each provider in staging
  - [ ] 20.3.3 Monitor OAuth metrics
  - [ ] 20.3.4 Deploy to production with feature flag
  - [ ] 20.3.5 Gradually enable OAuth for users
  - [ ] 20.3.6 Monitor for issues and iterate

---

**Total Tasks: 170 across 20 sections**

**Estimated Timeline:**
- Full-time: 6-8 weeks
- Part-time: 12-16 weeks

**Dependencies:**
- cryptography library (for Fernet token encryption)
- requests library (for API calls to providers)
- OAuth provider applications registered and configured
