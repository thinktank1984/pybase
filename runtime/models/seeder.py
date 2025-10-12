# -*- coding: utf-8 -*-
"""
Seeding system for default roles and permissions.
"""

from emmett import current


def seed_permissions(db):
    """
    Create default permissions for the application.
    
    Args:
        db: Database instance
        
    Returns:
        dict: Dictionary mapping permission names to permission IDs
    """
    print("🌱 Seeding permissions...")
    
    permissions = {}
    
    # Define default permissions
    permission_definitions = [
        # User permissions
        ('user', 'read', '', 'View user profiles'),
        ('user', 'create', '', 'Create new users'),
        ('user', 'edit', 'own', 'Edit own user profile'),
        ('user', 'edit', 'any', 'Edit any user profile'),
        ('user', 'delete', 'own', 'Delete own user account'),
        ('user', 'delete', 'any', 'Delete any user account'),
        ('user', 'manage', '', 'Full user management access'),
        
        # Post permissions
        ('post', 'read', '', 'View posts'),
        ('post', 'create', '', 'Create new posts'),
        ('post', 'edit', 'own', 'Edit own posts'),
        ('post', 'edit', 'any', 'Edit any post'),
        ('post', 'delete', 'own', 'Delete own posts'),
        ('post', 'delete', 'any', 'Delete any post'),
        ('post', 'publish', '', 'Publish posts'),
        
        # Comment permissions
        ('comment', 'read', '', 'View comments'),
        ('comment', 'create', '', 'Create comments'),
        ('comment', 'edit', 'own', 'Edit own comments'),
        ('comment', 'edit', 'any', 'Edit any comment'),
        ('comment', 'delete', 'own', 'Delete own comments'),
        ('comment', 'delete', 'any', 'Delete any comment'),
        ('comment', 'moderate', '', 'Moderate comments'),
        
        # Role permissions
        ('role', 'read', '', 'View roles'),
        ('role', 'create', '', 'Create new roles'),
        ('role', 'edit', '', 'Edit roles'),
        ('role', 'delete', '', 'Delete roles'),
        ('role', 'assign', '', 'Assign roles to users'),
        
        # Permission permissions
        ('permission', 'read', '', 'View permissions'),
        ('permission', 'create', '', 'Create permissions'),
        ('permission', 'edit', '', 'Edit permissions'),
        ('permission', 'delete', '', 'Delete permissions'),
        ('permission', 'assign', '', 'Assign permissions to roles'),
    ]
    
    for resource, action, scope, description in permission_definitions:
        # Generate permission name
        if scope:
            name = f"{resource}.{action}.{scope}"
        else:
            name = f"{resource}.{action}"
        
        # Check if permission already exists
        existing = db(db.permissions.name == name).select().first()
        
        if existing:
            permissions[name] = existing.id
            print(f"  ✓ Permission exists: {name}")
        else:
            # Create permission
            perm_id = db.permissions.insert(
                name=name,
                resource=resource,
                action=action,
                scope=scope,
                description=description
            )
            permissions[name] = perm_id
            print(f"  ✨ Created permission: {name}")
    
    db.commit()
    print(f"✅ Seeded {len(permissions)} permissions")
    return permissions


def seed_roles(db, permissions):
    """
    Create default roles with associated permissions.
    
    Args:
        db: Database instance
        permissions (dict): Dictionary of permission names to IDs
        
    Returns:
        dict: Dictionary mapping role names to role IDs
    """
    print("\n🌱 Seeding roles...")
    
    roles = {}
    
    # Define default roles and their permissions
    role_definitions = {
        'Admin': {
            'description': 'Full system access with all permissions',
            'permissions': 'ALL'  # Special marker for all permissions
        },
        'Moderator': {
            'description': 'Content moderation and management',
            'permissions': [
                # Can manage all posts and comments
                'post.read', 'post.create', 'post.edit.any', 'post.delete.any', 'post.publish',
                'comment.read', 'comment.create', 'comment.edit.any', 'comment.delete.any', 'comment.moderate',
                # Can view users but not manage
                'user.read',
                # Can view roles and permissions but not manage
                'role.read',
                'permission.read',
            ]
        },
        'Author': {
            'description': 'Content creation and management of own content',
            'permissions': [
                # Can manage own posts and comments
                'post.read', 'post.create', 'post.edit.own', 'post.delete.own', 'post.publish',
                'comment.read', 'comment.create', 'comment.edit.own', 'comment.delete.own',
                # Can view own user profile
                'user.read', 'user.edit.own',
            ]
        },
        'Viewer': {
            'description': 'Read-only access to public content',
            'permissions': [
                # Can only read content
                'post.read',
                'comment.read',
                'user.read',
            ]
        }
    }
    
    for role_name, role_data in role_definitions.items():
        # Check if role already exists
        existing_role = db(db.roles.name == role_name).select().first()
        
        if existing_role:
            role_id = existing_role.id
            roles[role_name] = role_id
            print(f"  ✓ Role exists: {role_name}")
        else:
            # Create role
            role_id = db.roles.insert(
                name=role_name,
                description=role_data['description']
            )
            roles[role_name] = role_id
            print(f"  ✨ Created role: {role_name}")
        
        # Assign permissions to role
        if role_data['permissions'] == 'ALL':
            # Assign all permissions (for Admin)
            for perm_name, perm_id in permissions.items():
                # Check if association exists
                existing_assoc = db(
                    (db.role_permissions.role == role_id) &
                    (db.role_permissions.permission == perm_id)
                ).select().first()
                
                if not existing_assoc:
                    db.role_permissions.insert(
                        role=role_id,
                        permission=perm_id
                    )
            print(f"    → Assigned ALL permissions to {role_name}")
        else:
            # Assign specific permissions
            assigned_count = 0
            for perm_name in role_data['permissions']:
                if perm_name in permissions:
                    perm_id = permissions[perm_name]
                    
                    # Check if association exists
                    existing_assoc = db(
                        (db.role_permissions.role == role_id) &
                        (db.role_permissions.permission == perm_id)
                    ).select().first()
                    
                    if not existing_assoc:
                        db.role_permissions.insert(
                            role=role_id,
                            permission=perm_id
                        )
                        assigned_count += 1
            
            if assigned_count > 0:
                print(f"    → Assigned {assigned_count} permissions to {role_name}")
    
    db.commit()
    print(f"✅ Seeded {len(roles)} roles")
    return roles


def assign_admin_role_to_user(db, user_id, roles):
    """
    Assign the Admin role to a user (typically the setup admin).
    
    Args:
        db: Database instance
        user_id (int): User ID to assign admin role
        roles (dict): Dictionary of role names to IDs
        
    Returns:
        bool: True if successful
    """
    if 'Admin' not in roles:
        print("⚠️  Admin role not found")
        return False
    
    admin_role_id = roles['Admin']
    
    # Check if user already has admin role
    existing = db(
        (db.user_roles.user == user_id) &
        (db.user_roles.role == admin_role_id)
    ).select().first()
    
    if existing:
        print(f"✓ User {user_id} already has Admin role")
        return True
    
    # Assign admin role
    db.user_roles.insert(
        user=user_id,
        role=admin_role_id
    )
    db.commit()
    
    print(f"✨ Assigned Admin role to user {user_id}")
    return True


def seed_all(db, admin_user_id=None):
    """
    Seed all default roles and permissions.
    
    Args:
        db: Database instance
        admin_user_id (int): Optional user ID to assign Admin role
        
    Returns:
        tuple: (permissions dict, roles dict)
    """
    print("\n" + "="*60)
    print("🌱 SEEDING ROLE-BASED ACCESS CONTROL SYSTEM")
    print("="*60)
    
    # Seed permissions first
    permissions = seed_permissions(db)
    
    # Seed roles and assign permissions
    roles = seed_roles(db, permissions)
    
    # Assign admin role to specified user if provided
    if admin_user_id:
        assign_admin_role_to_user(db, admin_user_id, roles)
    
    print("\n" + "="*60)
    print("✅ ROLE SYSTEM SEEDING COMPLETE")
    print("="*60 + "\n")
    
    return permissions, roles


def ensure_permissions_exist(db):
    """
    Ensure all required permissions exist (idempotent).
    Can be called at app startup.
    
    Args:
        db: Database instance
        
    Returns:
        int: Number of permissions created
    """
    permissions = seed_permissions(db)
    return len(permissions)


def ensure_roles_exist(db):
    """
    Ensure all required roles exist (idempotent).
    Can be called at app startup.
    
    Args:
        db: Database instance
        
    Returns:
        int: Number of roles created/updated
    """
    # First ensure permissions exist
    permissions = seed_permissions(db)
    
    # Then ensure roles exist
    roles = seed_roles(db, permissions)
    
    return len(roles)

