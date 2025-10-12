/proposal active_record_design_pattern ✅ COMPLETED
    add active record design pattern
        - Models should include only these
        - attributes
        - attributes decorators
        - UI element mapping decorator default override
        - methods
        - methods decorator
        - Should automatically create:
            - REST API endpoints (CRUD)
            - Swagger/OpenAPI documentation
            - CRUD pages (list, detail, create, edit)
            - Permission system (auth, ownership, roles)
    
    📁 Location: openspec/changes/add-active-record-design-pattern/
    📊 Status: Proposal complete, ready for review
    ⏱️ Estimated: 18 hours (4-5 days part-time) 
/proposal add_user_role_system 📋 NEW
    Add comprehensive role-based access control (RBAC) system
        - Role and Permission models with Active Record pattern
        - User-role and role-permission many-to-many relationships
        - Decorators: @requires_role, @requires_permission, @requires_any_role
        - Auto-generated management UIs for roles, permissions, and assignments
        - Permission caching in sessions for performance
        - Default roles: Admin, Moderator, Author, Viewer
        - Permission naming: {resource}.{action} (e.g., post.create)
        - Ownership-based permissions: {resource}.{action}.{own|any}
        - Template helpers for permission checks
        - REST API integration with permission enforcement
        - OpenAPI documentation for security requirements
        - Migration from existing group-based system
    
    📁 Location: openspec/changes/add-user-role-system/
    📊 Status: Proposal complete, ready for review
    ⏱️ Estimated: 24 hours (6-7 days part-time)
/proposal add-oauth-social-login ✅ COMPLETED
    Add OAuth2 support and social login (Google, GitHub, Microsoft, Facebook)
        - OAuth2 authorization code flow with PKCE
        - Multiple provider support (Google, GitHub, Microsoft, Facebook)
        - New user registration via OAuth
        - Account linking (connect OAuth to existing accounts)
        - Secure token storage with encryption at rest
        - Token refresh automation
        - PKCE and state validation for security
        - Email conflict resolution
        - Rate limiting on OAuth endpoints
        - Account management UI (connect/disconnect providers)
        - Backward compatible with password authentication
        - Comprehensive monitoring and logging
    
    📁 Location: openspec/changes/add-oauth-social-login/
    📊 Status: Proposal complete, ready for review
    ⏱️ Estimated: 6-8 weeks (full-time) or 12-16 weeks (part-time)
    📝 Tasks: 170 tasks across 20 sections
/proposal create a celery task that spawn agent
---

