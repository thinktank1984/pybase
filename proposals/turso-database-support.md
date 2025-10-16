# OpenSpec Change Proposal: Turso Database Backend Support

## Overview

This proposal outlines the addition of Turso Database as a supported backend option for the pybase application framework. Turso is an edge-native SQLite-compatible database that provides distributed, serverless database functionality with built-in replication and global edge deployment capabilities.

## Proposed Change

### 1. Database Backend Support Extension

Add Turso Database as a supported database backend alongside the existing SQLite option in the `DatabaseManager` class (`runtime/database_manager.py`).

### 2. Integration Requirements

#### 2.1 Dependencies
- Add `libsql-client` Python package for Turso connectivity
- Update requirements.txt/pyproject.toml accordingly

#### 2.2 Configuration Support
- Add Turso-specific configuration options in `DatabaseManager.initialize()`
- Support Turso database URL format: `libsql://[token]@[host]`
- Add environment variable support: `TURSO_DATABASE_URL`
- Add authentication token handling: `TURSO_AUTH_TOKEN`

#### 2.3 Connection Management
- Implement Turso connection pooling configuration
- Add retry logic for network-based connections
- Handle connection timeout and error recovery

### 3. Implementation Details

#### 3.1 Database URL Detection
```python
def _detect_database_type(self, database_url: str) -> str:
    """Detect database type from URL pattern"""
    if database_url.startswith('libsql://'):
        return 'turso'
    elif database_url.startswith('sqlite:'):
        return 'sqlite'
    else:
        return 'unknown'
```

#### 3.2 Turso Configuration
```python
def _configure_turso(self, app: Any, database_url: str):
    """Configure Turso-specific settings"""
    # Extract host and token from URL
    # Set connection pooling for distributed nature
    # Configure SSL/TLS settings
    # Set retry and timeout parameters
```

#### 3.3 Connection Factory
```python
def _create_turso_connection(self):
    """Create Turso database connection"""
    # Use libsql-client to establish connection
    # Handle authentication
    # Set connection parameters
```

### 4. Migration Path

#### 4.1 Existing SQLite Compatibility
- Maintain full backward compatibility with existing SQLite deployments
- Allow seamless migration from local SQLite to Turso
- Provide data migration utilities if needed

#### 4.2 Configuration Migration
- Support for `DATABASE_URL` environment variable override
- Automatic detection of Turso vs SQLite based on URL scheme
- Graceful fallback to SQLite if Turso connection fails

### 5. Benefits

#### 5.1 Performance Advantages
- Edge-native deployment reduces latency
- Built-in read replicas improve query performance
- Connection pooling optimized for distributed access

#### 5.2 Scalability
- Horizontal scaling with automatic replication
- Global edge distribution
- Serverless architecture reduces operational overhead

#### 5.3 Developer Experience
- SQLite compatibility ensures minimal code changes
- Same ORM and query patterns work unchanged
- Enhanced debugging and monitoring capabilities

### 6. Considerations

#### 6.1 Network Dependencies
- Turso requires internet connectivity (unlike local SQLite)
- Need to handle network failures gracefully
- Implement appropriate retry mechanisms

#### 6.2 Cost Implications
- Turso is a cloud service with potential costs
- Should be optional, not required
- Clear documentation on when to use Turso vs SQLite

#### 6.3 Data Consistency
- Distributed nature may introduce eventual consistency
- Need to understand replication lag implications
- Test strategies for distributed database behavior

### 7. Testing Strategy

#### 7.1 Unit Tests
- Test database type detection
- Test Turso configuration parsing
- Test connection factory methods

#### 7.2 Integration Tests
- Test with actual Turso database (using test account)
- Test migration from SQLite to Turso
- Test error handling and recovery

#### 7.3 Performance Tests
- Compare query performance between SQLite and Turso
- Test connection pooling efficiency
- Test concurrent access patterns

### 8. Documentation Requirements

#### 8.1 Configuration Guide
- How to set up Turso account and database
- Environment variable configuration
- Connection string formats

#### 8.2 Migration Guide
- Step-by-step migration from SQLite
- Data export/import procedures
- Testing and validation steps

#### 8.3 Best Practices
- When to use Turso vs SQLite
- Performance optimization tips
- Monitoring and debugging

### 9. Implementation Timeline

#### Phase 1: Core Integration (2-3 days)
- Add libsql-client dependency
- Implement database type detection
- Add Turso configuration logic

#### Phase 2: Connection Management (2-3 days)
- Implement Turso connection factory
- Add retry and error handling
- Test basic connectivity

#### Phase 3: Testing & Documentation (2-3 days)
- Write comprehensive tests
- Create migration guide
- Update documentation

### 10. Success Metrics

- Successful connection to Turso databases
- Zero breaking changes to existing SQLite functionality
- Performance benchmarks meet or exceed expectations
- Complete test coverage for new functionality
- Clear documentation enables easy adoption

## Conclusion

Adding Turso Database support will provide pybase users with a scalable, edge-native database option while maintaining full backward compatibility with existing SQLite deployments. The implementation leverages the existing `DatabaseManager` architecture and requires minimal changes to application code.

This change positions pybase to better support modern, distributed applications while preserving its simplicity for local development and small-scale deployments.