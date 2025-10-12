"""Add role-based access control system

Migration ID: a1b2c3d4e5f6
Revises: 9d6518b3cdc2
Creation Date: 2025-10-12 12:00:00.000000

"""

from emmett.orm import migrations


class Migration(migrations.Migration):
    revision = 'a1b2c3d4e5f6'
    revises = '9d6518b3cdc2'

    def up(self):
        # Create roles table
        self.create_table(
            'roles',
            migrations.Column('id', 'id'),
            migrations.Column('name', 'string', length=80, unique=True, notnull=True),
            migrations.Column('description', 'text'),
            migrations.Column('created_at', 'datetime'))
        
        # Create permissions table
        self.create_table(
            'permissions',
            migrations.Column('id', 'id'),
            migrations.Column('name', 'string', length=120, unique=True, notnull=True),
            migrations.Column('resource', 'string', length=40, notnull=True),
            migrations.Column('action', 'string', length=40, notnull=True),
            migrations.Column('scope', 'string', length=20),
            migrations.Column('description', 'text'),
            migrations.Column('created_at', 'datetime'))
        
        # Create user_roles association table
        self.create_table(
            'user_roles',
            migrations.Column('id', 'id'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            migrations.Column('role', 'reference roles', ondelete='CASCADE'),
            migrations.Column('assigned_at', 'datetime'),
            migrations.Column('assigned_by', 'integer'))
        
        # Create role_permissions association table
        self.create_table(
            'role_permissions',
            migrations.Column('id', 'id'),
            migrations.Column('role', 'reference roles', ondelete='CASCADE'),
            migrations.Column('permission', 'reference permissions', ondelete='CASCADE'),
            migrations.Column('granted_at', 'datetime'),
            migrations.Column('granted_by', 'integer'))

    def down(self):
        # Drop tables in reverse order
        self.drop_table('role_permissions')
        self.drop_table('user_roles')
        self.drop_table('permissions')
        self.drop_table('roles')

