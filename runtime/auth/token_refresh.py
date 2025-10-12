# -*- coding: utf-8 -*-
"""
OAuth token refresh logic and background job.
"""

from datetime import timedelta
from emmett import now
import traceback


def refresh_oauth_token(oauth_account):
    """
    Refresh an OAuth access token if needed.
    
    Args:
        oauth_account: OAuthAccount instance
        
    Returns:
        bool: True if refresh succeeded or not needed, False if failed
    """
    try:
        from ..models import OAuthToken
        from .oauth_manager import get_oauth_manager
        
        # Get token
        token = OAuthToken.where(lambda t: t.oauth_account == oauth_account.id).first()
        if not token:
            print(f"No token found for OAuth account {oauth_account.id}")
            return False
        
        # Check if refresh needed
        if not token.needs_refresh():
            return True  # Token is still valid
        
        # Check if we have a refresh token
        refresh_token = token.get_refresh_token()
        if not refresh_token:
            print(f"No refresh token available for OAuth account {oauth_account.id}")
            return False
        
        # Get provider instance
        oauth_manager = get_oauth_manager()
        provider_instance = oauth_manager.get_provider(oauth_account.provider)
        if not provider_instance:
            print(f"Provider {oauth_account.provider} not configured")
            return False
        
        # Refresh the token
        print(f"Refreshing token for {oauth_account.provider} account {oauth_account.id}")
        token_data = provider_instance.refresh_access_token(refresh_token)
        
        # Update stored tokens
        new_access_token = token_data.get('access_token')
        new_refresh_token = token_data.get('refresh_token')  # Some providers rotate refresh tokens
        expires_in = token_data.get('expires_in')
        
        token.update_tokens(
            new_access_token,
            new_refresh_token or refresh_token,  # Use new refresh token if provided
            expires_in
        )
        
        print(f"Successfully refreshed token for OAuth account {oauth_account.id}")
        return True
        
    except Exception as e:
        print(f"Error refreshing OAuth token: {e}")
        traceback.print_exc()
        return False


def refresh_expiring_tokens(hours_threshold=2):
    """
    Refresh all OAuth tokens that are expiring soon.
    
    Args:
        hours_threshold: Refresh tokens expiring within this many hours
        
    Returns:
        dict: Statistics about the refresh operation
    """
    try:
        from ..models import OAuthAccount, OAuthToken
        
        # Find tokens expiring soon
        threshold_time = now() + timedelta(hours=hours_threshold)
        
        expiring_tokens = OAuthToken.where(
            lambda t: (
                (t.access_token_expires_at != None) &
                (t.access_token_expires_at <= threshold_time) &
                (t.refresh_token_encrypted != None)
            )
        ).select()
        
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'no_refresh_token': 0
        }
        
        for token in expiring_tokens:
            stats['total'] += 1
            
            # Get OAuth account
            oauth_account = OAuthAccount.get(token.oauth_account)
            if not oauth_account:
                print(f"OAuth account {token.oauth_account} not found")
                stats['failed'] += 1
                continue
            
            # Attempt refresh
            success = refresh_oauth_token(oauth_account)
            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        print(f"Token refresh job complete: {stats}")
        return stats
        
    except Exception as e:
        print(f"Error in refresh_expiring_tokens: {e}")
        traceback.print_exc()
        return {'error': str(e)}


def cleanup_expired_tokens(days_threshold=90):
    """
    Clean up expired OAuth tokens that haven't been used in a while.
    
    Args:
        days_threshold: Delete tokens older than this many days
        
    Returns:
        int: Number of tokens deleted
    """
    try:
        from ..models import OAuthToken
        
        cutoff_date = now() - timedelta(days=days_threshold)
        
        # Find tokens that are:
        # 1. Expired (access token expired)
        # 2. No refresh token OR refresh token also expired
        # 3. Haven't been updated in days_threshold days
        expired_tokens = OAuthToken.where(
            lambda t: (
                (t.access_token_expires_at != None) &
                (t.access_token_expires_at < now()) &
                (t.updated_at < cutoff_date) &
                (
                    (t.refresh_token_encrypted == None) |
                    (
                        (t.refresh_token_expires_at != None) &
                        (t.refresh_token_expires_at < now())
                    )
                )
            )
        ).select()
        
        count = 0
        for token in expired_tokens:
            try:
                token.delete()
                count += 1
            except Exception as e:
                print(f"Error deleting token {token.id}: {e}")
        
        print(f"Cleaned up {count} expired OAuth tokens")
        return count
        
    except Exception as e:
        print(f"Error in cleanup_expired_tokens: {e}")
        traceback.print_exc()
        return 0


# Emmett CLI command for token refresh
def setup_commands(app):
    """
    Setup Emmett CLI commands for OAuth token management.
    
    Usage:
        emmett oauth:refresh          # Refresh expiring tokens
        emmett oauth:cleanup          # Clean up old tokens
    """
    
    @app.command('oauth:refresh')
    def cli_refresh_tokens():
        """Refresh OAuth tokens that are expiring soon"""
        print("Starting OAuth token refresh job...")
        stats = refresh_expiring_tokens()
        print(f"Token refresh complete: {stats}")
    
    @app.command('oauth:cleanup')
    def cli_cleanup_tokens():
        """Clean up expired OAuth tokens"""
        print("Starting OAuth token cleanup job...")
        count = cleanup_expired_tokens()
        print(f"Cleanup complete: {count} tokens deleted")

