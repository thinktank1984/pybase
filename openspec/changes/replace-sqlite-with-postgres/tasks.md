# Implementation Tasks

## 1. Docker Infrastructure
- [ ] 1.1 Add PostgreSQL service to docker-compose.yaml
- [ ] 1.2 Configure PostgreSQL environment variables (database name, user, password)
- [ ] 1.3 Add PostgreSQL health check
- [ ] 1.4 Add named volume for PostgreSQL data persistence
- [ ] 1.5 Configure runtime service to depend on PostgreSQL health

## 2. Database Configuration
- [ ] 2.1 Update app.py database URI to use PostgreSQL connection string
- [ ] 2.2 Remove SQLite-specific adapter_args (check_same_thread, timeout)
- [ ] 2.3 Add PostgreSQL-specific configuration (pool size, SSL mode)
- [ ] 2.4 Update environment variable support for database credentials
- [ ] 2.5 Add database URI construction with environment variable fallback

## 3. Migration Strategy
- [ ] 3.1 Document SQLite data export process
- [ ] 3.2 Create PostgreSQL database initialization script
- [ ] 3.3 Run existing Emmett migrations against PostgreSQL
- [ ] 3.4 Verify all models work with PostgreSQL
- [ ] 3.5 Test relationships and constraints in PostgreSQL

## 4. Testing Updates
- [ ] 4.1 Update conftest.py to use PostgreSQL test database
- [ ] 4.2 Add test database cleanup fixtures
- [ ] 4.3 Verify all integration tests pass with PostgreSQL
- [ ] 4.4 Add connection pool tests
- [ ] 4.5 Test concurrent database operations

## 5. Documentation
- [ ] 5.1 Update AGENTS.md with PostgreSQL requirements
- [ ] 5.2 Update project.md tech stack section
- [ ] 5.3 Add migration guide from SQLite to PostgreSQL
- [ ] 5.4 Document PostgreSQL connection string format
- [ ] 5.5 Update development setup instructions

## 6. Cleanup
- [ ] 6.1 Remove SQLite database files from runtime/databases/
- [ ] 6.2 Update .gitignore for PostgreSQL-related files
- [ ] 6.3 Remove SQLite-specific comments and configuration

