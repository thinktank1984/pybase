"""Add OAuth authentication tables

Migration ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Creation Date: 2025-10-13 14:00:00.000000

"""

from emmett.orm import migrations


class Migration(migrations.Migration):
    revision = 'b2c3d4e5f6g7'
    revises = 'a1b2c3d4e5f6'

    def up(self):
        # Create oauth_accounts table
        self.create_table(
            'oauth_accounts',
            migrations.Column('id', 'id'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            migrations.Column('provider', 'string', length=50, notnull=True),
            migrations.Column('provider_user_id', 'string', length=255, notnull=True),
            migrations.Column('email', 'string', length=255),
            migrations.Column('name', 'string', length=255),
            migrations.Column('picture', 'string', length=512),
            migrations.Column('profile_data', 'text'),  # JSON stored as text
            migrations.Column('created_at', 'datetime'),
            migrations.Column('last_login_at', 'datetime'))
        
        # Create oauth_tokens table
        self.create_table(
            'oauth_tokens',
            migrations.Column('id', 'id'),
            migrations.Column('oauth_account', 'reference oauth_accounts', ondelete='CASCADE'),
            migrations.Column('access_token_encrypted', 'text', notnull=True),
            migrations.Column('refresh_token_encrypted', 'text'),
            migrations.Column('token_type', 'string', length=50),
            migrations.Column('scope', 'string', length=512),
            migrations.Column('access_token_expires_at', 'datetime'),
            migrations.Column('refresh_token_expires_at', 'datetime'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'))

    def down(self):
        # Drop tables in reverse order
        self.drop_table('oauth_tokens')
        self.drop_table('oauth_accounts')

