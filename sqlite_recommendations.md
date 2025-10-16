# SQLite Performance and Concurrency Recommendations

This document provides comprehensive recommendations for optimizing SQLite database performance and concurrency in production environments.

## Overview

SQLite is a powerful, serverless database engine that can handle high-performance workloads when properly configured. The enhanced concurrency implementation in this project provides enterprise-grade database connection management while maintaining SQLite's simplicity and reliability.

## Key Enhancements Implemented

### 1. Connection Pooling
- **Purpose**: Reduces connection overhead and improves performance
- **Configuration**: `DB_POOL_SIZE` environment variable (default: 10)
- **Recommendations**:
  - **Development**: 5-10 connections
  - **Production**: 10-50 connections based on traffic
  - **High-traffic**: 50-100+ connections with monitoring

### 2. Write-Ahead Logging (WAL) Mode
- **Purpose**: Allows concurrent reads during writes for better performance
- **Configuration**: `DB_ENABLE_WAL=true` (recommended: true)
- **Benefits**:
  - Multiple readers can access database during writes
  - Reduced contention in read-heavy workloads
  - Better crash recovery
- **Considerations**:
  - Slightly increased disk usage
  - Requires periodic checkpointing

### 3. Separate Read/Write Connections
- **Purpose**: Optimizes different operations for their specific use cases
- **Configuration**: `DB_SEPARATE_READ_WRITE=true`
- **Read Connection Optimization**:
  - Larger connection pools (2x base pool size)
  - Optimized cache settings
  - Reduced memory mapping size
- **Write Connection Optimization**:
  - Smaller, focused connection pools (base pool size ÷ 2)
  - Stronger synchronization settings
  - Enhanced durability settings

## Performance Tuning Recommendations

### Database Configuration

#### Connection Pool Settings
```yaml
# Development
DB_POOL_SIZE: 5
DB_SEPARATE_READ_WRITE: false

# Production (moderate traffic)
DB_POOL_SIZE: 15
DB_SEPARATE_READ_WRITE: true

# High-traffic production
DB_POOL_SIZE: 50
DB_SEPARATE_READ_WRITE: true
```

#### WAL Mode Optimization
```yaml
# Enable WAL for better concurrency
DB_ENABLE_WAL: true

# Configure WAL checkpointing (in adapter_args)
wal_autocheckpoint: 1000  # Checkpoint every 1000 pages
wal_checkpoint_mode: PASSIVE  # Background checkpointing
```

#### Memory and Cache Settings
```python
adapter_args = {
    'cache_size': 2000,        # 2MB cache (adjust based on available memory)
    'temp_store': 'memory',    # Store temporary tables in memory
    'mmap_size': 268435456,    # 256MB memory-mapped I/O
}
```

### Application-Level Optimizations

#### 1. Transaction Management
```python
# Use connection context for proper transaction handling
with db_manager.connection():
    # Multiple operations here
    user = User.create(...)
    post = Post.create(...)
    # Automatic commit/rollback
```

#### 2. Batch Operations
```python
# Use batch_insert for multiple records
users_data = [
    {'name': 'User 1', 'email': 'user1@example.com'},
    {'name': 'User 2', 'email': 'user2@example.com'},
]
db_manager.batch_insert(User, users_data)
```

#### 3. Query Optimization
```python
# Use specific queries instead of loading all data
users = User.where(lambda u: u.active == True).select(limit=100)

# Use read connection for read-heavy operations
with db_manager.read_connection():
    reports = generate_heavy_reports()
```

## Production Deployment Guidelines

### 1. Database File Management
- **Location**: Use dedicated storage directory
- **Backup Strategy**: Regular backup of `main.db` file
- **Monitoring**: Monitor database file size and growth

### 2. Monitoring and Metrics
```python
# Monitor connection statistics
stats = db_manager.get_connection_stats()
print(f"Active connections: {stats['active_connections']}")
print(f"Pool utilization: {stats['pool_utilization']}%")
```

### 3. Health Checks
- Monitor database response times
- Track connection pool utilization
- Monitor WAL file size and checkpointing

## Scaling Considerations

### Vertical Scaling
- Increase `DB_POOL_SIZE` based on available memory
- Optimize `cache_size` and `mmap_size` for available RAM
- Monitor memory usage with increased connections

### Horizontal Scaling
- SQLite is inherently single-server
- For read-heavy workloads, consider read replicas
- For write-heavy workloads, consider sharding or migration to PostgreSQL

## Troubleshooting

### Common Issues

#### 1. Database Locked Errors
- **Solution**: Enable WAL mode (`DB_ENABLE_WAL=true`)
- **Alternative**: Increase connection pool timeout

#### 2. Slow Performance
- **Check**: Connection pool utilization
- **Solution**: Increase `DB_POOL_SIZE` or optimize queries
- **Monitor**: Cache hit rates

#### 3. High Memory Usage
- **Cause**: Large connection pools or excessive caching
- **Solution**: Reduce `DB_POOL_SIZE` or `cache_size`

### Performance Monitoring
```bash
# Monitor database connections
docker compose logs runtime | grep "Database"

# Monitor performance metrics
curl http://localhost:8081/metrics
```

## Migration from Other Databases

### from PostgreSQL
- **Pros**: Simplified deployment, reduced overhead
- **Cons**: Single-server limitation
- **Migration Strategy**: Export/import data, update connection strings

### from MySQL
- **Pros**: Reduced complexity, better performance for read-heavy workloads
- **Cons**: Limited concurrent write performance
- **Migration Strategy**: Schema conversion, data export/import

### from Turso
- **Seamless Migration**: Compatible with libsql protocol
- **Benefits**: Local control, no external dependencies
- **Configuration**: Update `DATABASE_URL` from `libsql://` to `sqlite://`

## Best Practices

### 1. Connection Management
- Always use connection contexts
- Close connections properly
- Monitor pool utilization

### 2. Query Optimization
- Use specific queries with limits
- Implement proper indexing
- Cache frequently accessed data

### 3. Error Handling
- Implement proper error handling
- Use transaction rollbacks
- Monitor and log database errors

### 4. Security
- Set appropriate file permissions
- Use connection encryption if needed
- Implement access controls

## Conclusion

SQLite with the enhanced concurrency implementation provides excellent performance for most web applications. The key optimizations include connection pooling, WAL mode, and separate read/write connections. Proper configuration and monitoring ensure reliable operation in production environments.

For very high-traffic or multi-region deployments, consider scaling strategies or migrating to distributed databases. However, for most applications, this SQLite implementation provides excellent performance with minimal complexity.