# CovetPy WebSocket API Specification

## Overview

The CovetPy WebSocket API provides real-time bidirectional communication for high-performance applications. It supports authentication, message routing, room-based communication, and automatic reconnection.

## Connection Endpoint

```
ws://localhost:8000/ws
wss://api.covetpy.com/ws
```

## Authentication

### Token-based Authentication

Include the JWT token in the connection query parameters:

```javascript
const socket = new WebSocket('ws://localhost:8000/ws?token=your_jwt_token');
```

### API Key Authentication

Alternative authentication using API key:

```javascript
const socket = new WebSocket('ws://localhost:8000/ws?api_key=your_api_key');
```

## Message Format

All messages use JSON format with a standardized structure:

```json
{
  "type": "message_type",
  "id": "unique_message_id",
  "timestamp": "2025-09-10T12:00:00Z",
  "data": {
    // Message-specific data
  },
  "metadata": {
    "correlation_id": "optional_correlation_id",
    "priority": "normal|high|low",
    "ttl": 30000
  }
}
```

## Message Types

### Connection Management

#### connection_ack
Sent by server after successful connection:

```json
{
  "type": "connection_ack",
  "id": "conn_12345",
  "timestamp": "2025-09-10T12:00:00Z",
  "data": {
    "session_id": "sess_abcdef",
    "user_id": "user_123",
    "capabilities": ["rooms", "streaming", "rpc"],
    "heartbeat_interval": 30000
  }
}
```

#### heartbeat
Bidirectional heartbeat messages:

```json
{
  "type": "heartbeat",
  "id": "hb_12345",
  "timestamp": "2025-09-10T12:00:00Z",
  "data": {
    "sequence": 42
  }
}
```

### Room Management

#### join_room
Client request to join a room:

```json
{
  "type": "join_room",
  "id": "jr_12345",
  "data": {
    "room_id": "project_123",
    "options": {
      "subscribe_to_metrics": true,
      "filter": {
        "event_types": ["data_update", "user_activity"]
      }
    }
  }
}
```

#### leave_room
Client request to leave a room:

```json
{
  "type": "leave_room",
  "id": "lr_12345",
  "data": {
    "room_id": "project_123"
  }
}
```

#### room_joined
Server confirmation of room join:

```json
{
  "type": "room_joined",
  "id": "rj_12345",
  "data": {
    "room_id": "project_123",
    "member_count": 15,
    "permissions": ["read", "write"],
    "room_metadata": {
      "name": "Project Alpha",
      "created_at": "2025-09-01T10:00:00Z"
    }
  }
}
```

### Data Streaming

#### subscribe
Subscribe to data streams:

```json
{
  "type": "subscribe",
  "id": "sub_12345",
  "data": {
    "stream_type": "metrics|logs|events|database_changes",
    "resource_id": "db_conn_123",
    "filters": {
      "min_severity": "warning",
      "tags": ["performance", "database"]
    },
    "options": {
      "buffer_size": 100,
      "batch_interval": 1000
    }
  }
}
```

#### unsubscribe
Unsubscribe from data streams:

```json
{
  "type": "unsubscribe",
  "id": "unsub_12345",
  "data": {
    "subscription_id": "sub_12345"
  }
}
```

#### stream_data
Server-sent streaming data:

```json
{
  "type": "stream_data",
  "id": "sd_12345",
  "data": {
    "subscription_id": "sub_12345",
    "stream_type": "metrics",
    "resource_id": "db_conn_123",
    "batch": [
      {
        "timestamp": "2025-09-10T12:00:00Z",
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "active_connections": 12
      },
      {
        "timestamp": "2025-09-10T12:00:01Z",
        "cpu_usage": 47.1,
        "memory_usage": 68.2,
        "active_connections": 13
      }
    ]
  }
}
```

### Remote Procedure Calls (RPC)

#### rpc_call
Client RPC request:

```json
{
  "type": "rpc_call",
  "id": "rpc_12345",
  "data": {
    "method": "database.test_connection",
    "params": {
      "connection_id": "db_conn_123"
    },
    "timeout": 10000
  }
}
```

#### rpc_response
Server RPC response:

```json
{
  "type": "rpc_response",
  "id": "rpc_12345",
  "data": {
    "result": {
      "success": true,
      "latency_ms": 23.4,
      "connection_info": {
        "host": "db.example.com",
        "port": 5432,
        "database": "production"
      }
    }
  }
}
```

#### rpc_error
Server RPC error response:

```json
{
  "type": "rpc_error",
  "id": "rpc_12345",
  "data": {
    "error": {
      "code": "CONNECTION_FAILED",
      "message": "Failed to connect to database",
      "details": {
        "host": "db.example.com",
        "port": 5432,
        "error": "Connection timeout after 10 seconds"
      }
    }
  }
}
```

### Notifications

#### notification
Server-sent notifications:

```json
{
  "type": "notification",
  "id": "notif_12345",
  "data": {
    "notification_type": "info|warning|error|success",
    "title": "Database Connection Restored",
    "message": "Connection to production database has been restored",
    "category": "database",
    "actions": [
      {
        "label": "View Details",
        "action": "show_details",
        "params": {
          "resource_id": "db_conn_123"
        }
      }
    ],
    "auto_dismiss": true,
    "dismiss_after": 5000
  }
}
```

### File Operations

#### file_upload_start
Initiate file upload:

```json
{
  "type": "file_upload_start",
  "id": "upload_12345",
  "data": {
    "filename": "data.csv",
    "size": 1048576,
    "mimetype": "text/csv",
    "chunk_size": 64000,
    "metadata": {
      "project_id": "proj_123",
      "description": "Customer data import"
    }
  }
}
```

#### file_chunk
File chunk data:

```json
{
  "type": "file_chunk",
  "id": "chunk_12345",
  "data": {
    "upload_id": "upload_12345",
    "chunk_index": 0,
    "total_chunks": 16,
    "data": "base64_encoded_chunk_data",
    "checksum": "sha256_checksum"
  }
}
```

#### file_upload_complete
File upload completion:

```json
{
  "type": "file_upload_complete",
  "id": "complete_12345",
  "data": {
    "upload_id": "upload_12345",
    "file_id": "file_abcdef",
    "url": "https://files.covetpy.com/file_abcdef",
    "processing_status": "queued|processing|completed|failed"
  }
}
```

## Error Handling

### error
Generic error message:

```json
{
  "type": "error",
  "id": "error_12345",
  "data": {
    "error_code": "INVALID_MESSAGE_FORMAT",
    "error_message": "Message format is invalid",
    "original_message_id": "invalid_msg_123",
    "details": {
      "field": "data.resource_id",
      "expected": "string",
      "received": "null"
    },
    "recoverable": false
  }
}
```

### Connection Errors

Common error codes:
- `AUTH_FAILED`: Authentication failed
- `AUTH_EXPIRED`: Token expired
- `RATE_LIMITED`: Rate limit exceeded
- `PERMISSION_DENIED`: Insufficient permissions
- `ROOM_NOT_FOUND`: Requested room doesn't exist
- `SUBSCRIPTION_FAILED`: Failed to create subscription
- `RPC_TIMEOUT`: RPC call timed out
- `INVALID_MESSAGE_FORMAT`: Message format error

## Rate Limiting

Default rate limits:
- Connection attempts: 10 per minute
- Messages per connection: 100 per minute
- RPC calls: 50 per minute
- File uploads: 10 per hour

Rate limit headers in error responses:
```json
{
  "rate_limit": {
    "limit": 100,
    "remaining": 0,
    "reset": "2025-09-10T12:01:00Z"
  }
}
```

## Client Libraries

### JavaScript/Node.js

```javascript
import { CovetPyWebSocketClient } from '@covetpy/client';

const client = new CovetPyWebSocketClient({
  url: 'ws://localhost:8000/ws',
  token: 'your_jwt_token',
  reconnect: {
    enabled: true,
    maxAttempts: 10,
    delay: 1000
  }
});

// Connect
await client.connect();

// Join room
await client.joinRoom('project_123', {
  subscribe_to_metrics: true
});

// Subscribe to data stream
const subscription = await client.subscribe('metrics', 'db_conn_123', {
  min_severity: 'warning'
});

subscription.on('data', (data) => {
  console.log('Received metrics:', data);
});

// RPC call
const result = await client.call('database.test_connection', {
  connection_id: 'db_conn_123'
});
```

### Python

```python
import asyncio
from covetpy.client import WebSocketClient

async def main():
    client = WebSocketClient(
        url='ws://localhost:8000/ws',
        token='your_jwt_token'
    )
    
    await client.connect()
    
    # Join room
    await client.join_room('project_123')
    
    # Subscribe to metrics
    async def on_metrics(data):
        print(f"Received metrics: {data}")
    
    await client.subscribe('metrics', 'db_conn_123', callback=on_metrics)
    
    # RPC call
    result = await client.call('database.test_connection', {
        'connection_id': 'db_conn_123'
    })
    print(f"Connection test result: {result}")

asyncio.run(main())
```

## Performance Considerations

### Connection Pooling
- Maximum 1000 concurrent connections per server instance
- Connection reuse recommended for multiple operations
- Automatic load balancing across server instances

### Message Batching
- Stream data is automatically batched for efficiency
- Configurable batch size and interval
- Compression for large message payloads

### Memory Management
- Automatic cleanup of inactive subscriptions
- Configurable message buffer sizes
- Memory usage monitoring and alerts

## Security Features

### Authentication & Authorization
- JWT token validation
- Role-based access control
- Per-room permission checking
- API key authentication for service accounts

### Data Protection
- TLS encryption for all connections
- Message payload encryption for sensitive data
- Audit logging for all connections and operations
- IP-based connection filtering

### DoS Protection
- Rate limiting at multiple levels
- Connection throttling
- Message size limits
- Automatic bad client detection and blocking