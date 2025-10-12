# -*- coding: utf-8 -*-
"""
OAuth tables migration - creates oauth_accounts and oauth_tokens tables.

Run with: emmett migrations up
"""

from emmett.orm import migrations


class Migration(migrations.Migration):
    migration_id = 'oauth_001'
    depends_on = []  # Add dependency on your latest migration if needed

    def up(self):
        self.create_table(
            'oauth_accounts',
            migrations.Column('id', 'id'),
            migrations.Column('user', 'reference users', notnull=True),
            migrations.Column('provider', 'string', length=50, notnull=True),
            migrations.Column('provider_user_id', 'string', length=255, notnull=True),
            migrations.Column('email', 'string', length=255),
            migrations.Column('name', 'string', length=255),
            migrations.Column('picture', 'string', length=512),
            migrations.Column('profile_data', 'json'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('last_login_at', 'datetime')
        )
        
        # Create unique index on (provider, provider_user_id)
        self.create_index('oauth_accounts', 'provider', 'provider_user_id', unique=True)
        
        # Create index on (user, provider)
        self.create_index('oauth_accounts', 'user', 'provider')
        
        self.create_table(
            'oauth_tokens',
            migrations.Column('id', 'id'),
            migrations.Column('oauth_account', 'reference oauth_accounts', notnull=True),
            migrations.Column('access_token_encrypted', 'text', notnull=True),
            migrations.Column('refresh_token_encrypted', 'text'),
            migrations.Column('token_type', 'string', length=50, default='Bearer'),
            migrations.Column('scope', 'string', length=512),
            migrations.Column('access_token_expires_at', 'datetime'),
            migrations.Column('refresh_token_expires_at', 'datetime'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime')
        )
        
        # Create index on oauth_account
        self.create_index('oauth_tokens', 'oauth_account')
        
        # Create index on access_token_expires_at for cleanup queries
        self.create_index('oauth_tokens', 'access_token_expires_at')

    def down(self):
        self.drop_table('oauth_tokens')
        self.drop_table('oauth_accounts')

