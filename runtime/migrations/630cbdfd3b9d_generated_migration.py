"""Generated migration

Migration ID: 630cbdfd3b9d
Revises: c7ffdf8268fe
Creation Date: 2025-10-16 22:30:35.517860

"""

from emmett.orm import migrations


class Migration(migrations.Migration):
    revision = '630cbdfd3b9d'
    revises = 'c7ffdf8268fe'

    def up(self):
        self.drop_index('auth_groups_widx__role_unique', 'auth_groups')
        self.drop_table('auth_groups')
        self.drop_table('auth_memberships')
        self.drop_table('auth_permissions')
        self.drop_table('auth_events')
        self.alter_column('users', 'email',
            existing_type='string',
            existing_length=255,
            length=512,
            existing_notnull=False)
        self.alter_column('users', 'password',
            existing_type='password',
            existing_length=512,
            type='string',
            existing_notnull=False)
        self.alter_column('users', 'registration_key',
            existing_type='string',
            existing_length=512,
            default=None,
            existing_notnull=False)
        self.alter_column('users', 'reset_password_key',
            existing_type='string',
            existing_length=512,
            default=None,
            existing_notnull=False)
        self.alter_column('users', 'registration_id',
            existing_type='string',
            existing_length=512,
            default=None,
            existing_notnull=False)
        self.alter_column('users', 'first_name',
            existing_type='string',
            existing_length=128,
            length=512,
            notnull=False)
        self.alter_column('users', 'last_name',
            existing_type='string',
            existing_length=128,
            length=512,
            notnull=False)
        self.alter_column('users', 'username',
            existing_type='string',
            existing_length=255,
            length=512,
            existing_notnull=False)
        self.drop_column('users', 'created_at')
        self.drop_column('users', 'updated_at')
        self.drop_index('users_widx__email_unique', 'users')

    def down(self):
        self.create_index('users_widx__email_unique', 'users', ['email'], expressions=[], unique=True)
        self.add_column('users', migrations.Column('updated_at', 'datetime'))
        self.add_column('users', migrations.Column('created_at', 'datetime'))
        self.alter_column('users', 'username',
            existing_type='string',
            existing_length=512,
            length=255,
            existing_notnull=False)
        self.alter_column('users', 'last_name',
            existing_type='string',
            existing_length=512,
            length=128,
            notnull=True)
        self.alter_column('users', 'first_name',
            existing_type='string',
            existing_length=512,
            length=128,
            notnull=True)
        self.alter_column('users', 'registration_id',
            existing_type='string',
            existing_length=512,
            default='',
            existing_notnull=False)
        self.alter_column('users', 'reset_password_key',
            existing_type='string',
            existing_length=512,
            default='',
            existing_notnull=False)
        self.alter_column('users', 'registration_key',
            existing_type='string',
            existing_length=512,
            default='',
            existing_notnull=False)
        self.alter_column('users', 'password',
            existing_type='string',
            existing_length=512,
            type='password',
            existing_notnull=False)
        self.alter_column('users', 'email',
            existing_type='string',
            existing_length=512,
            length=255,
            existing_notnull=False)
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
            'auth_memberships',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            migrations.Column('auth_group', 'reference auth_groups', ondelete='CASCADE'),
            primary_keys=['id'])
        self.create_table(
            'auth_groups',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('role', 'string', default='', length=255),
            migrations.Column('description', 'text'),
            primary_keys=['id'])
        self.create_index('auth_groups_widx__role_unique', 'auth_groups', ['role'], expressions=[], unique=True)
