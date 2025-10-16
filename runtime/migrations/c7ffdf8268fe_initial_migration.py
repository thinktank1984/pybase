"""Initial migration

Migration ID: c7ffdf8268fe
Revises: 
Creation Date: 2025-10-16 02:30:53.369901

"""

from emmett.orm import migrations


class Migration(migrations.Migration):
    revision = 'c7ffdf8268fe'
    revises = None

    def up(self):
        self.create_table(
            'users',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('email', 'string', length=255),
            migrations.Column('password', 'password', length=512),
            migrations.Column('registration_key', 'string', default='', length=512),
            migrations.Column('reset_password_key', 'string', default='', length=512),
            migrations.Column('registration_id', 'string', default='', length=512),
            migrations.Column('first_name', 'string', notnull=True, length=128),
            migrations.Column('last_name', 'string', notnull=True, length=128),
            primary_keys=['id'])
        self.create_index('users_widx__email_unique', 'users', ['email'], expressions=[], unique=True)
        self.create_table(
            'auth_groups',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('role', 'string', default='', length=255),
            migrations.Column('description', 'text'),
            primary_keys=['id'])
        self.create_index('auth_groups_widx__role_unique', 'auth_groups', ['role'], expressions=[], unique=True)
        self.create_table(
            'auth_memberships',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            migrations.Column('auth_group', 'reference auth_groups', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'auth_permissions',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('name', 'string', default='default', notnull=True, length=512),
            migrations.Column('table_name', 'string', length=512),
            migrations.Column('record_id', 'integer', default=0),
            migrations.Column('auth_group', 'reference auth_groups', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'auth_events',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('client_ip', 'string', length=512),
            migrations.Column('origin', 'string', default='auth', notnull=True, length=512),
            migrations.Column('description', 'text', default='', notnull=True),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'posts',
            migrations.Column('id', 'id'),
            migrations.Column('title', 'string', length=512),
            migrations.Column('text', 'text'),
            migrations.Column('date', 'datetime'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'comments',
            migrations.Column('id', 'id'),
            migrations.Column('text', 'text'),
            migrations.Column('date', 'datetime'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            migrations.Column('post', 'reference posts', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'roles',
            migrations.Column('id', 'id'),
            migrations.Column('name', 'string', notnull=True, length=80),
            migrations.Column('description', 'text'),
            migrations.Column('created_at', 'datetime'),
            primary_keys=['id'])
        self.create_index('roles_widx__name_unique', 'roles', ['name'], expressions=[], unique=True)
        self.create_table(
            'permissions',
            migrations.Column('id', 'id'),
            migrations.Column('name', 'string', length=120),
            migrations.Column('resource', 'string', notnull=True, length=40),
            migrations.Column('action', 'string', notnull=True, length=40),
            migrations.Column('scope', 'string', length=20),
            migrations.Column('description', 'text'),
            migrations.Column('created_at', 'datetime'),
            primary_keys=['id'])
        self.create_index('permissions_widx__name_unique', 'permissions', ['name'], expressions=[], unique=True)
        self.create_table(
            'user_roles',
            migrations.Column('id', 'id'),
            migrations.Column('assigned_at', 'datetime'),
            migrations.Column('assigned_by', 'integer'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            migrations.Column('role', 'reference roles', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'role_permissions',
            migrations.Column('id', 'id'),
            migrations.Column('granted_at', 'datetime'),
            migrations.Column('granted_by', 'integer'),
            migrations.Column('role', 'reference roles', ondelete='CASCADE'),
            migrations.Column('permission', 'reference permissions', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'oauth_accounts',
            migrations.Column('id', 'id'),
            migrations.Column('provider', 'string', notnull=True, length=50),
            migrations.Column('provider_user_id', 'string', notnull=True, length=255),
            migrations.Column('email', 'string', length=255),
            migrations.Column('name', 'string', length=255),
            migrations.Column('picture', 'string', length=512),
            migrations.Column('profile_data', 'json'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('last_login_at', 'datetime'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'oauth_tokens',
            migrations.Column('id', 'id'),
            migrations.Column('access_token_encrypted', 'text', notnull=True),
            migrations.Column('refresh_token_encrypted', 'text'),
            migrations.Column('token_type', 'string', default='Bearer', length=50),
            migrations.Column('scope', 'string', length=512),
            migrations.Column('access_token_expires_at', 'datetime'),
            migrations.Column('refresh_token_expires_at', 'datetime'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('oauth_account', 'reference oauth_accounts', ondelete='CASCADE'),
            primary_keys=['id'])

    def down(self):
        self.drop_table('oauth_tokens')
        self.drop_table('oauth_accounts')
        self.drop_table('role_permissions')
        self.drop_table('user_roles')
        self.drop_index('permissions_widx__name_unique', 'permissions')
        self.drop_table('permissions')
        self.drop_index('roles_widx__name_unique', 'roles')
        self.drop_table('roles')
        self.drop_table('comments')
        self.drop_table('posts')
        self.drop_table('auth_events')
        self.drop_table('auth_permissions')
        self.drop_table('auth_memberships')
        self.drop_index('auth_groups_widx__role_unique', 'auth_groups')
        self.drop_table('auth_groups')
        self.drop_index('users_widx__email_unique', 'users')
        self.drop_table('users')
