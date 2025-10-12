# OAuth Social Login Setup Guide

This guide will help you set up OAuth social login with Google, GitHub, Microsoft, and Facebook.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Generate Encryption Key](#generate-encryption-key)
3. [Google OAuth Setup](#google-oauth-setup)
4. [GitHub OAuth Setup](#github-oauth-setup)
5. [Microsoft OAuth Setup](#microsoft-oauth-setup)
6. [Facebook OAuth Setup](#facebook-oauth-setup)
7. [Configuration](#configuration)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.9+
- OAuth dependencies installed: `authlib`, `cryptography`, `requests`
- A publicly accessible URL for OAuth callbacks (or ngrok for local development)

## Generate Encryption Key

OAuth tokens are encrypted at rest. Generate an encryption key:

```bash
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

Add this key to your `.env` file:

```bash
OAUTH_TOKEN_ENCRYPTION_KEY=your-generated-key-here
```

## Google OAuth Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"

### 2. Configure OAuth Consent Screen

1. Click "OAuth consent screen" in the sidebar
2. Select "External" user type (or "Internal" for Google Workspace)
3. Fill in the required fields:
   - App name: Your application name
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes: `openid`, `email`, `profile`
5. Add test users (if in testing mode)

### 3. Create OAuth 2.0 Credentials

1. Click "Credentials" > "Create Credentials" > "OAuth client ID"
2. Select "Web application"
3. Add authorized redirect URIs:
   - Development: `http://localhost:8081/auth/oauth/google/callback`
   - Production: `https://yourdomain.com/auth/oauth/google/callback`
4. Save and copy the Client ID and Client Secret

### 4. Add to Environment Variables

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

## GitHub OAuth Setup

### 1. Register OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the application details:
   - Application name: Your app name
   - Homepage URL: Your website URL
   - Authorization callback URL:
     - Development: `http://localhost:8081/auth/oauth/github/callback`
     - Production: `https://yourdomain.com/auth/oauth/github/callback`

### 2. Get Credentials

1. After creating the app, note the Client ID
2. Generate a new client secret
3. Copy both values

### 3. Add to Environment Variables

```bash
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## Microsoft OAuth Setup

### 1. Register Application

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Fill in the details:
   - Name: Your application name
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: Web > `http://localhost:8081/auth/oauth/microsoft/callback`

### 2. Configure Authentication

1. Go to "Authentication" in your app
2. Add platform > Web
3. Add redirect URIs:
   - `http://localhost:8081/auth/oauth/microsoft/callback`
   - `https://yourdomain.com/auth/oauth/microsoft/callback`
4. Enable "Access tokens" and "ID tokens"

### 3. Add API Permissions

1. Go to "API permissions"
2. Add permissions: Microsoft Graph
   - `openid`
   - `email`
   - `profile`
   - `User.Read`

### 4. Create Client Secret

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Add description and set expiration
4. Copy the secret value immediately (it won't be shown again)

### 5. Add to Environment Variables

```bash
MICROSOFT_CLIENT_ID=your-application-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_TENANT=common  # For multi-tenant support
```

## Facebook OAuth Setup

### 1. Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" > "Create App"
3. Select "Consumer" as app type
4. Fill in app name and contact email

### 2. Configure Facebook Login

1. In your app dashboard, click "Add Product"
2. Find "Facebook Login" and click "Set Up"
3. Select "Web" as platform
4. Enter your site URL

### 3. Configure OAuth Settings

1. Go to "Facebook Login" > "Settings"
2. Add Valid OAuth Redirect URIs:
   - `http://localhost:8081/auth/oauth/facebook/callback`
   - `https://yourdomain.com/auth/oauth/facebook/callback`
3. Save changes

### 4. Get App Credentials

1. Go to "Settings" > "Basic"
2. Copy your App ID and App Secret

### 5. Add to Environment Variables

```bash
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

## Configuration

### Complete .env File

Create or update your `.env` file in the project root:

```bash
# OAuth Token Encryption
OAUTH_TOKEN_ENCRYPTION_KEY=your-encryption-key-here

# OAuth Base URL
OAUTH_BASE_URL=http://localhost:8081

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT=common

# Facebook OAuth
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

### Database Migrations

Run migrations to create OAuth tables:

```bash
cd runtime
emmett migrations up
```

## Testing

### Local Development

1. Start your application:
   ```bash
   cd runtime
   emmett develop
   ```

2. Navigate to the login page: `http://localhost:8081/auth/login`

3. Click on any "Continue with [Provider]" button

4. Complete the OAuth flow with the provider

5. You should be redirected back and logged in

### Testing Account Linking

1. Create an account with email/password
2. Log in
3. Go to Account Settings: `http://localhost:8081/account/settings`
4. Click "Connect" on any OAuth provider
5. Complete the OAuth flow
6. The provider will be linked to your account

### Testing OAuth-Only Accounts

1. Log out if logged in
2. Click "Continue with [Provider]" on the login page
3. Use an email that doesn't have an existing account
4. A new account will be created automatically

## Troubleshooting

### "OAuth provider not available"

**Cause**: Provider credentials not configured

**Solution**: 
- Ensure CLIENT_ID and CLIENT_SECRET are set in `.env`
- Restart the application to load new environment variables

### "Security validation failed"

**Cause**: State parameter mismatch (CSRF protection)

**Solution**:
- Clear browser cookies
- Try again with a fresh session
- Ensure your application is using consistent session storage

### "Email not verified" or "Could not retrieve email"

**Cause**: Provider didn't return a verified email

**Solution**:
- Verify your email with the OAuth provider
- For GitHub: Ensure you have at least one verified email
- For Facebook: Grant email permission when requested

### "This account is already linked to another user"

**Cause**: OAuth account is already connected to a different user

**Solution**:
- Log in as the user who owns the OAuth account
- Or create a new account with a different email

### "Cannot unlink your last login method"

**Cause**: Attempting to remove the only authentication method

**Solution**:
- Set a password before unlinking: Go to Account Settings > Set Password
- Or link another OAuth provider before unlinking

### Redirect URI Mismatch

**Cause**: Callback URL doesn't match registered URI

**Solution**:
- Check that `OAUTH_BASE_URL` in `.env` matches your actual URL
- Verify redirect URIs in provider console match exactly:
  - `{OAUTH_BASE_URL}/auth/oauth/{provider}/callback`
  - Include or exclude trailing slashes consistently
- For local development, use `http://localhost:8081` (not `127.0.0.1`)

### Token Encryption Errors

**Cause**: Missing or invalid encryption key

**Solution**:
- Generate a new key: `python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`
- Set in `.env`: `OAUTH_TOKEN_ENCRYPTION_KEY=your-key-here`
- **Important**: Don't change this key once you have encrypted tokens in the database

## Production Deployment

### Security Checklist

- [ ] Use HTTPS for all OAuth callbacks
- [ ] Set `OAUTH_BASE_URL` to your production domain
- [ ] Update all provider redirect URIs to production URLs
- [ ] Rotate encryption key if exposed
- [ ] Enable rate limiting on OAuth endpoints
- [ ] Monitor OAuth error logs
- [ ] Set up alerts for OAuth failures
- [ ] Review and minimize requested OAuth scopes
- [ ] Implement token refresh background job
- [ ] Configure proper session security (secure cookies, HTTPS-only)

### Environment Variables for Production

```bash
EMMETT_ENV=production
OAUTH_BASE_URL=https://yourdomain.com
OAUTH_TOKEN_ENCRYPTION_KEY=your-production-encryption-key

# Provider credentials (from production apps)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
# ... etc
```

## Support

For additional help:
- Check the [Emmett documentation](https://emmett.sh/)
- Review provider-specific OAuth documentation
- Check application logs in `runtime/logs/`
- Contact support: support@yourdomain.com

## Security Considerations

1. **Never commit OAuth secrets to version control**
2. **Use environment variables for all credentials**
3. **Rotate secrets regularly**
4. **Monitor for suspicious OAuth activity**
5. **Keep encryption key secure and backed up**
6. **Implement rate limiting on OAuth endpoints**
7. **Log all authentication events for audit**
8. **Use HTTPS in production**
9. **Validate all OAuth callbacks**
10. **Implement token expiration and refresh**

