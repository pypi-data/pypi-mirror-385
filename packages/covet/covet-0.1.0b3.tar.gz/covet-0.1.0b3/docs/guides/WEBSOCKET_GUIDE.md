# CovetPy WebSocket Guide

Complete guide to building production-grade WebSocket applications with CovetPy.

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Connection Management](#connection-management)
4. [Room/Channel Architecture](#roomchannel-architecture)
5. [Message Routing](#message-routing)
6. [Authentication](#authentication)
7. [Compression](#compression)
8. [Redis Pub/Sub for Scaling](#redis-pubsub-for-scaling)
9. [Production Deployment](#production-deployment)
10. [Performance Optimization](#performance-optimization)

## Introduction

CovetPy provides production-grade WebSocket support with:

- **Connection Management**: Lifecycle management, heartbeat, automatic reconnection
- **Room/Channel System**: Group connections for targeted broadcasting
- **Event-Based Routing**: Clean message routing with decorators
- **Authentication**: JWT, cookie, and API key authentication
- **Compression**: RFC 7692 compliant per-message deflate
- **Horizontal Scaling**: Redis-backed pub/sub for multi-server deployments
- **Rate Limiting**: Per-connection and per-IP rate limiting
- **Monitoring**: Built-in metrics and statistics

## Quick Start

### Basic WebSocket Server

```python
from covet import CovetPy

app = CovetPy()

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    # Accept connection
    await websocket.accept()

    # Send welcome message
    await websocket.send_json({"message": "Connected!"})

    # Message loop
    while True:
        # Receive message
        message = await websocket.receive_text()

        # Echo back
        await websocket.send_text(f"Echo: {message}")
```

### Using Connection Manager

```python
from covet.websocket.connection_manager import ProductionConnectionManager

# Create connection manager
connection_manager = ProductionConnectionManager(
    max_connections=10000,
    max_connections_per_ip=100,
)

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    # Add connection with management features
    connection = await connection_manager.add_connection(
        websocket=websocket,
        user_id="user-123",
        ip_address="192.168.1.1",
    )

    try:
        await connection.accept()

        # Use managed connection (includes rate limiting)
        await connection.send_text("Hello!")

        # Message loop
        while connection.is_connected:
            message = await connection.receive()
            # Handle message

    finally:
        await connection_manager.close_connection(connection.id)
```

## Connection Management

### Features

- **Automatic Cleanup**: Stale connections automatically cleaned up
- **Rate Limiting**: Per-connection message and byte rate limits
- **Heartbeat**: Automatic ping/pong to detect dead connections
- **Reconnection**: Support for reconnection with state preservation
- **Per-IP Limits**: Prevent abuse with IP-based connection limits

### Configuration

```python
from covet.websocket.connection_manager import (
    ProductionConnectionManager,
    RateLimitConfig,
    ReconnectionConfig,
)

# Configure rate limiting
rate_limit_config = RateLimitConfig(
    enabled=True,
    max_messages_per_second=10,
    max_messages_per_minute=300,
    max_bytes_per_second=1024 * 1024,  # 1MB/s
    burst_size=20,
    ban_duration_seconds=60,
)

# Configure reconnection
reconnect_config = ReconnectionConfig(
    enabled=True,
    max_attempts=5,
    initial_delay_seconds=1.0,
    max_delay_seconds=60.0,
    backoff_multiplier=2.0,
)

# Create manager
manager = ProductionConnectionManager(
    max_connections=10000,
    max_connections_per_ip=100,
    rate_limit_config=rate_limit_config,
    reconnect_config=reconnect_config,
)
```

### Connection Statistics

```python
# Get statistics
stats = manager.get_statistics()
print(f"Active connections: {stats['current_connections']}")
print(f"Messages sent: {stats['total_messages_sent']}")
print(f"Avg latency: {stats['average_ping_latency_ms']}ms")
```

## Room/Channel Architecture

### Creating and Managing Rooms

```python
from covet.websocket.room_manager import (
    RoomManager,
    RoomType,
    RoomPermission,
    RoomConfig,
)

# Create room manager
room_manager = RoomManager(connection_manager)

# Create a public room
room = room_manager.create_room(
    name="general",
    room_type=RoomType.PUBLIC,
    config=RoomConfig(
        max_members=1000,
        auto_delete_when_empty=True,
    ),
)

# Join room
await room_manager.join_room(
    connection_id="conn-123",
    room_name="general",
    user_id="user-123",
    permission=RoomPermission.MEMBER,
)

# Broadcast to room
await room_manager.broadcast_to_room(
    "general",
    {"type": "announcement", "message": "Welcome!"},
)

# Leave room
await room_manager.leave_room("conn-123", "general")
```

### Private Rooms

```python
# Create invite-only room
private_room = room_manager.create_room(
    name="team-alpha",
    room_type=RoomType.INVITE_ONLY,
    owner_id="user-admin",
)

# Invite users
private_room.invite_user("user-123")
private_room.invite_user("user-456")

# Only invited users can join
await room_manager.join_room("conn-123", "team-alpha", user_id="user-123")
```

### Room Permissions

```python
# Set member permission
private_room.set_permission("conn-123", RoomPermission.MODERATOR)

# Mute member
private_room.mute_member("conn-456")

# Ban user from room
private_room.ban_user("user-789")
```

## Message Routing

### Event-Based Routing

```python
from covet.websocket.message_router import MessageRouter

router = MessageRouter()

# Register event handlers
@router.on("chat_message")
async def handle_chat(connection, message):
    room = message.data.get("room")
    text = message.data.get("text")

    await room_manager.broadcast_to_room(
        room,
        {
            "type": "chat_message",
            "user": connection.info.user_id,
            "text": text,
        },
    )

@router.on("join_room")
async def handle_join(connection, message):
    room_name = message.data.get("room")
    await room_manager.join_room(connection.id, room_name)

    await connection.send_json({
        "type": "joined",
        "room": room_name,
    })
```

### Request/Response Pattern

```python
# Send request and wait for response
response = await router.send_request(
    connection,
    event_type="get_user_info",
    data={"user_id": "user-123"},
    timeout=5.0,
)

print(f"User info: {response}")
```

### Input Validation

```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    room: str
    text: str

    class Config:
        extra = "forbid"

# Register with validation
@router.on("chat_message", schema=ChatMessage)
async def handle_chat(connection, message):
    # message.data is validated ChatMessage instance
    validated_data = message.data
    print(f"Room: {validated_data.room}")
    print(f"Text: {validated_data.text}")
```

## Authentication

### JWT Authentication

```python
from covet.websocket.auth import (
    WebSocketAuthenticator,
    AuthConfig,
    AuthStrategy,
)

# Configure JWT authentication
auth_config = AuthConfig(
    strategy=AuthStrategy.JWT_QUERY,
    jwt_secret="your-secret-key",
    jwt_query_param="token",
    required=True,
    auto_disconnect_on_failure=True,
)

authenticator = WebSocketAuthenticator(auth_config)

# Authenticate connection
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    connection = await connection_manager.add_connection(websocket=websocket)

    # Authenticate
    user = await authenticator.authenticate_connection(
        connection,
        websocket.scope,
    )

    if not user:
        await connection.close(reason="Authentication failed")
        return

    # Connection is authenticated
    print(f"User {user.user_id} authenticated")
```

### Cookie-Based Authentication

```python
auth_config = AuthConfig(
    strategy=AuthStrategy.COOKIE,
    cookie_name="session",
    cookie_secret="your-cookie-secret",
)
```

### Permission Checking

```python
# Check permission
if authenticator.check_permission(connection.id, "admin"):
    # Allow admin action
    pass

# Require permission decorator
@authenticator.require_permission("broadcast")
async def broadcast_handler(connection, message):
    # Only users with broadcast permission can call this
    pass
```

## Compression

### Per-Message Deflate

```python
from covet.websocket.compression import (
    CompressionManager,
    CompressionConfig,
    CompressionLevel,
)

# Configure compression
compression_config = CompressionConfig(
    enabled=True,
    level=CompressionLevel.DEFAULT,  # 6
    min_size_bytes=1024,  # Only compress >1KB
    max_window_bits=15,
)

compression_manager = CompressionManager(compression_config)

# Create context for connection
ctx = compression_manager.create_context("conn-123")

# Compress message
compressed, was_compressed = ctx.compress(b"large message data...")

# Decompress
decompressed = ctx.decompress(compressed)

# Get statistics
stats = ctx.get_statistics()
print(f"Compression ratio: {stats['avg_compression_ratio']:.2f}")
print(f"Bytes saved: {stats['bytes_saved']}")
```

## Redis Pub/Sub for Scaling

### Multi-Server Deployment

```python
from covet.websocket.pubsub_redis import RedisWebSocketPubSub, RedisConfig

# Configure Redis
redis_config = RedisConfig(
    host="localhost",
    port=6379,
    password="your-redis-password",
)

# Create Redis pub/sub
pubsub = RedisWebSocketPubSub(connection_manager, redis_config)
await pubsub.connect()

# Subscribe to channels
await pubsub.subscribe("chat:*")  # Pattern subscription
await pubsub.subscribe("notifications")

# Publish message (broadcasts to all servers)
await pubsub.publish("chat:general", {
    "type": "message",
    "text": "Hello from server 1!",
})

# Broadcast to both Redis and local connections
await pubsub.broadcast_to_channel("chat:general", {
    "type": "announcement",
    "text": "New feature released!",
})
```

### Custom Message Handlers

```python
async def handle_chat_message(channel, data):
    print(f"Received message on {channel}: {data}")

await pubsub.subscribe("chat:general", handler=handle_chat_message)
```

## Production Deployment

### Deployment Checklist

1. **Security**:
   - Use TLS/SSL (wss://)
   - Enable authentication
   - Set strong JWT secrets
   - Configure CORS properly
   - Enable rate limiting

2. **Performance**:
   - Enable compression
   - Configure connection limits
   - Set up Redis for scaling
   - Use multiple worker processes

3. **Monitoring**:
   - Track connection counts
   - Monitor message rates
   - Track latency metrics
   - Set up alerts

4. **Reliability**:
   - Configure automatic reconnection
   - Enable heartbeat/ping-pong
   - Handle graceful shutdown
   - Set up health checks

### Example Production Configuration

```python
from covet import CovetPy
from covet.websocket.connection_manager import ProductionConnectionManager
from covet.websocket.room_manager import RoomManager
from covet.websocket.message_router import MessageRouter
from covet.websocket.auth import WebSocketAuthenticator, AuthConfig, AuthStrategy
from covet.websocket.compression import CompressionManager
from covet.websocket.pubsub_redis import RedisWebSocketPubSub

# Create app
app = CovetPy()

# Production connection manager
connection_manager = ProductionConnectionManager(
    max_connections=50000,
    max_connections_per_ip=100,
)

# Room manager
room_manager = RoomManager(connection_manager)

# Message router
router = MessageRouter()

# Authentication
auth = WebSocketAuthenticator(AuthConfig(
    strategy=AuthStrategy.JWT_QUERY,
    jwt_secret=os.getenv("JWT_SECRET"),
    required=True,
))

# Compression
compression = CompressionManager()

# Redis pub/sub for scaling
redis_pubsub = RedisWebSocketPubSub(
    connection_manager,
    redis_host=os.getenv("REDIS_HOST", "localhost"),
    redis_password=os.getenv("REDIS_PASSWORD"),
)
await redis_pubsub.connect()

# Health check
@app.get("/health")
async def health():
    stats = connection_manager.get_statistics()
    return {
        "status": "healthy",
        "connections": stats["current_connections"],
        "uptime": stats.get("uptime_seconds", 0),
    }

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info",
    )
```

### Load Balancing

Use a load balancer (nginx, HAProxy) with sticky sessions:

```nginx
upstream websocket_backends {
    ip_hash;  # Sticky sessions
    server 10.0.1.1:8000;
    server 10.0.1.2:8000;
    server 10.0.1.3:8000;
}

server {
    listen 443 ssl http2;
    server_name ws.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /ws {
        proxy_pass http://websocket_backends;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

## Performance Optimization

### Tips for Maximum Performance

1. **Use Redis for Multi-Server**: Essential for horizontal scaling
2. **Enable Compression**: Reduces bandwidth by 60-80%
3. **Optimize Message Size**: Keep messages small
4. **Use Binary When Possible**: Binary messages are faster
5. **Batch Messages**: Send multiple updates in one message
6. **Connection Pooling**: Reuse connections
7. **Async All the Way**: Use async/await throughout
8. **Monitor and Profile**: Track metrics continuously

### Performance Targets

- **Latency**: <10ms internal processing
- **Throughput**: 100,000+ messages/sec per server
- **Concurrent Connections**: 10,000+ per server
- **Memory**: <10KB per connection

### Example Optimization

```python
# Batch messages for efficiency
messages = []
for i in range(100):
    messages.append({"id": i, "data": f"message {i}"})

# Send as single JSON array
await connection.send_json({
    "type": "batch",
    "messages": messages,
})

# Use binary for large data
import struct
import msgpack

# Serialize with msgpack (faster than JSON)
data = msgpack.packb({"user": "john", "action": "move", "x": 100, "y": 200})
await connection.send_bytes(data)
```

## Conclusion

CovetPy provides everything needed for production-grade WebSocket applications:

- Industrial-strength connection management
- Flexible room/channel system
- Clean event-based routing
- Multiple authentication strategies
- Efficient compression
- Horizontal scaling with Redis
- Built-in rate limiting and security

For more examples, see the `examples/websocket/` directory.

For API reference, see the module documentation in each component.
