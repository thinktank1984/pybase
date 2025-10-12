# Proposal: Add Realtime Pub/Sub Support

## Why

The application currently lacks realtime event notification capabilities, requiring clients to poll for data changes. Users need immediate notification of data changes (record create/update/delete operations) and custom events to build responsive, collaborative applications. This feature would enable use cases like live dashboards, chat features, collaborative editing, and real-time notifications.

## What Changes

- Add WebSocket-based pub/sub system for broadcasting data change events to subscribed clients
- Implement subscription management allowing clients to subscribe to specific collections or records
- Add ORM hooks to automatically broadcast record lifecycle events (create, update, delete)
- Provide API for sending custom realtime events to connected clients
- Implement client connection tracking with authentication context
- Add subscription filtering by collection name and optional record ID wildcard matching
- Provide JavaScript client library or examples for subscribing to realtime events

## Impact

### Affected Specs
- **NEW**: `realtime-pub-sub` - New capability

### Affected Code
- `runtime/app.py` - Add WebSocket routes and subscription broker initialization
- `runtime/base_model.py` - Add ORM hooks for automatic event broadcasting
- `runtime/models/` - Update models to emit realtime events on CRUD operations
- New file: `runtime/realtime_broker.py` - Core pub/sub subscription management
- New file: `runtime/static/realtime-client.js` - JavaScript client library (optional)
- `docker/docker-compose.yaml` - May need Redis for distributed pub/sub (optional)

### Dependencies
- May require Redis or similar message broker for multi-process/distributed deployment
- No changes to database schema required initially
- Emmett already includes WebSocket support via `emmett.websockets`

### Breaking Changes
- None - This is purely additive functionality

