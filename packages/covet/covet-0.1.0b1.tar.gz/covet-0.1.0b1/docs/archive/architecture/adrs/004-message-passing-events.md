# ADR-004: Message Passing and Event-Driven Architecture

## Status
Accepted

## Context

CovetPy requires a robust event-driven architecture to support:

1. Microservices communication with loose coupling
2. Real-time event streaming and processing
3. Asynchronous task processing and job queues
4. Service-to-service messaging patterns
5. Event sourcing and CQRS implementations
6. High-throughput message processing (>1M messages/sec)
7. Reliable message delivery with at-least-once semantics
8. Dead letter queues and error handling
9. Message ordering and partitioning
10. Integration with external message brokers (Kafka, RabbitMQ, Redis)

Traditional message systems often have high latency or limited throughput, while high-performance systems lack reliability guarantees.

## Decision

We will implement a **multi-tier event-driven architecture** with embedded message queues, external broker integration, and event streaming capabilities.

### 1. Event-Driven Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │   Event     │ │    Event     │ │     Event Bus      │   │
│  │ Publishers  │ │ Subscribers  │ │   (Local/Remote)   │   │
│  └─────────────┘ └──────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  Local Message  │ │   Message    │ │External Message │
│     Queue       │ │   Router     │ │    Brokers      │
│  (Lock-free)    │ │ (Topology)   │ │ (Kafka/RabbitMQ)│
│                 │ │              │ │                 │
│ ┌─────────────┐ │ │┌─────────────┐│ │ ┌─────────────┐ │
│ │   MPSC      │ │ ││   Routing   ││ │ │   Kafka     │ │
│ │   Queue     │ │ ││   Rules     ││ │ │  Producer   │ │
│ └─────────────┘ │ │└─────────────┘│ │ └─────────────┘ │
│ ┌─────────────┐ │ │┌─────────────┐│ │ ┌─────────────┐ │
│ │   Ring      │ │ ││   Dead      ││ │ │  RabbitMQ   │ │
│ │   Buffer    │ │ ││   Letter    ││ │ │   Client    │ │
│ └─────────────┘ │ │└─────────────┘│ │ └─────────────┘ │
└─────────────────┘ └──────────────┘ └─────────────────┘
```

### 2. Core Message System

#### Message Structure

```rust
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    // Core message identification
    pub id: Uuid,
    pub correlation_id: Option<Uuid>,
    pub causation_id: Option<Uuid>,
    
    // Message metadata
    pub event_type: String,
    pub version: u32,
    pub timestamp: DateTime<Utc>,
    pub source: String,
    pub destination: Option<String>,
    
    // Message content
    pub headers: HashMap<String, String>,
    pub payload: serde_json::Value,
    
    // Delivery metadata
    pub delivery_count: u32,
    pub max_retries: u32,
    pub ttl: Option<Duration>,
    pub priority: MessagePriority,
    
    // Routing information
    pub topic: String,
    pub partition_key: Option<String>,
    pub routing_key: Option<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum MessagePriority {
    Low = 0,
    Normal = 1,
    High = 2,
    Critical = 3,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageMetadata {
    pub produced_at: DateTime<Utc>,
    pub consumed_at: Option<DateTime<Utc>>,
    pub processing_time: Option<Duration>,
    pub error_count: u32,
    pub last_error: Option<String>,
}
```

#### High-Performance Local Message Queue

```rust
use crossbeam::queue::SegQueue;
use parking_lot::RwLock;
use std::sync::atomic::{AtomicU64, AtomicBool, Ordering};

pub struct LocalMessageQueue {
    // Lock-free queue for high throughput
    queue: SegQueue<Arc<Message>>,
    
    // Queue statistics
    size: AtomicU64,
    max_size: u64,
    total_messages: AtomicU64,
    dropped_messages: AtomicU64,
    
    // Flow control
    backpressure_enabled: AtomicBool,
    overflow_strategy: OverflowStrategy,
    
    // Monitoring
    metrics: Arc<QueueMetrics>,
}

#[derive(Debug, Clone, Copy)]
pub enum OverflowStrategy {
    Block,          // Block until space available
    DropOldest,     // Drop oldest message
    DropNewest,     // Drop newest message
    DropRandom,     // Drop random message
}

impl LocalMessageQueue {
    pub fn new(config: QueueConfig) -> Self {
        Self {
            queue: SegQueue::new(),
            size: AtomicU64::new(0),
            max_size: config.max_size,
            total_messages: AtomicU64::new(0),
            dropped_messages: AtomicU64::new(0),
            backpressure_enabled: AtomicBool::new(config.backpressure_enabled),
            overflow_strategy: config.overflow_strategy,
            metrics: Arc::new(QueueMetrics::new()),
        }
    }
    
    pub async fn enqueue(&self, message: Arc<Message>) -> Result<(), QueueError> {
        let current_size = self.size.load(Ordering::Relaxed);
        
        // Check capacity
        if current_size >= self.max_size {
            match self.overflow_strategy {
                OverflowStrategy::Block => {
                    // Wait for space (with timeout)
                    self.wait_for_space().await?;
                }
                OverflowStrategy::DropOldest => {
                    if let Some(_) = self.queue.pop() {
                        self.size.fetch_sub(1, Ordering::Relaxed);
                        self.dropped_messages.fetch_add(1, Ordering::Relaxed);
                    }
                }
                OverflowStrategy::DropNewest => {
                    self.dropped_messages.fetch_add(1, Ordering::Relaxed);
                    return Err(QueueError::QueueFull);
                }
                OverflowStrategy::DropRandom => {
                    // Implementation specific to ring buffer
                    self.drop_random_message();
                }
            }
        }
        
        // Enqueue message
        self.queue.push(message);
        self.size.fetch_add(1, Ordering::Relaxed);
        self.total_messages.fetch_add(1, Ordering::Relaxed);
        
        // Update metrics
        self.metrics.messages_enqueued.inc();
        
        Ok(())
    }
    
    pub fn dequeue(&self) -> Option<Arc<Message>> {
        if let Some(message) = self.queue.pop() {
            self.size.fetch_sub(1, Ordering::Relaxed);
            self.metrics.messages_dequeued.inc();
            Some(message)
        } else {
            None
        }
    }
    
    pub async fn dequeue_batch(&self, max_count: usize) -> Vec<Arc<Message>> {
        let mut batch = Vec::with_capacity(max_count);
        
        for _ in 0..max_count {
            if let Some(message) = self.dequeue() {
                batch.push(message);
            } else {
                break;
            }
        }
        
        batch
    }
}
```

### 3. Event Bus Implementation

#### Publisher-Subscriber Pattern

```rust
use async_trait::async_trait;
use tokio::sync::{broadcast, mpsc};

#[async_trait]
pub trait EventPublisher: Send + Sync {
    async fn publish(&self, event: Event) -> Result<(), PublishError>;
    async fn publish_batch(&self, events: Vec<Event>) -> Result<(), PublishError>;
}

#[async_trait]
pub trait EventSubscriber: Send + Sync {
    async fn handle_event(&self, event: Event) -> Result<(), ProcessingError>;
    fn event_types(&self) -> Vec<String>;
    fn subscriber_id(&self) -> String;
}

pub struct EventBus {
    // Topic-based routing
    topics: RwLock<HashMap<String, TopicChannel>>,
    
    // Subscriber management
    subscribers: RwLock<HashMap<String, Box<dyn EventSubscriber>>>,
    subscriber_topics: RwLock<HashMap<String, Vec<String>>>,
    
    // Message persistence
    message_store: Option<Arc<dyn MessageStore>>,
    
    // Configuration
    config: EventBusConfig,
    
    // Metrics
    metrics: Arc<EventBusMetrics>,
}

struct TopicChannel {
    sender: broadcast::Sender<Arc<Event>>,
    subscriber_count: AtomicU64,
    message_count: AtomicU64,
}

impl EventBus {
    pub fn new(config: EventBusConfig) -> Self {
        Self {
            topics: RwLock::new(HashMap::new()),
            subscribers: RwLock::new(HashMap::new()),
            subscriber_topics: RwLock::new(HashMap::new()),
            message_store: config.message_store,
            config,
            metrics: Arc::new(EventBusMetrics::new()),
        }
    }
    
    pub async fn register_subscriber(&self, subscriber: Box<dyn EventSubscriber>) -> Result<()> {
        let subscriber_id = subscriber.subscriber_id();
        let event_types = subscriber.event_types();
        
        // Register subscriber
        {
            let mut subscribers = self.subscribers.write();
            subscribers.insert(subscriber_id.clone(), subscriber);
        }
        
        // Subscribe to topics
        for event_type in &event_types {
            self.subscribe_to_topic(&subscriber_id, event_type).await?;
        }
        
        // Track subscriber topics
        {
            let mut subscriber_topics = self.subscriber_topics.write();
            subscriber_topics.insert(subscriber_id, event_types);
        }
        
        Ok(())
    }
    
    async fn subscribe_to_topic(&self, subscriber_id: &str, topic: &str) -> Result<()> {
        let channel = {
            let mut topics = self.topics.write();
            topics.entry(topic.to_string())
                .or_insert_with(|| TopicChannel {
                    sender: broadcast::channel(self.config.channel_capacity).0,
                    subscriber_count: AtomicU64::new(0),
                    message_count: AtomicU64::new(0),
                })
                .clone()
        };
        
        // Create receiver for subscriber
        let mut receiver = channel.sender.subscribe();
        let subscriber_id = subscriber_id.to_string();
        let subscribers = Arc::clone(&self.subscribers);
        
        // Spawn message handler
        tokio::spawn(async move {
            while let Ok(event) = receiver.recv().await {
                if let Some(subscriber) = subscribers.read().get(&subscriber_id) {
                    if let Err(e) = subscriber.handle_event((*event).clone()).await {
                        log::error!("Subscriber {} failed to handle event: {}", subscriber_id, e);
                    }
                }
            }
        });
        
        channel.subscriber_count.fetch_add(1, Ordering::Relaxed);
        Ok(())
    }
}

#[async_trait]
impl EventPublisher for EventBus {
    async fn publish(&self, event: Event) -> Result<(), PublishError> {
        // Persist event if store is configured
        if let Some(store) = &self.message_store {
            store.store_event(&event).await?;
        }
        
        // Publish to topic
        let topic = &event.event_type;
        if let Some(channel) = self.topics.read().get(topic) {
            if let Err(_) = channel.sender.send(Arc::new(event)) {
                return Err(PublishError::NoSubscribers);
            }
            
            channel.message_count.fetch_add(1, Ordering::Relaxed);
            self.metrics.events_published.inc();
        }
        
        Ok(())
    }
    
    async fn publish_batch(&self, events: Vec<Event>) -> Result<(), PublishError> {
        for event in events {
            self.publish(event).await?;
        }
        Ok(())
    }
}
```

### 4. Python Event API

```python
from typing import Callable, Dict, Any, List, Optional, AsyncIterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class Event:
    """Core event structure"""
    id: str
    event_type: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

class EventHandler(ABC):
    """Base event handler interface"""
    
    @property
    @abstractmethod
    def handled_events(self) -> List[str]:
        """List of event types this handler processes"""
        pass
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle an event"""
        pass

class EventBus:
    """High-level event bus interface"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe to events with a function"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def register_handler(self, handler: EventHandler) -> None:
        """Register an event handler"""
        for event_type in handler.handled_events:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
    
    async def publish(self, event: Event) -> None:
        """Publish an event"""
        # Call function subscribers
        if event.event_type in self._subscribers:
            tasks = []
            for handler in self._subscribers[event.event_type]:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    # Run sync handlers in thread pool
                    tasks.append(asyncio.get_event_loop().run_in_executor(
                        None, handler, event
                    ))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        # Call registered handlers
        if event.event_type in self._handlers:
            tasks = []
            for handler in self._handlers[event.event_type]:
                tasks.append(handler.handle(event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def publish_batch(self, events: List[Event]) -> None:
        """Publish multiple events"""
        tasks = [self.publish(event) for event in events]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def stream(self, event_type: str) -> AsyncIterator[Event]:
        """Stream events of a specific type"""
        # Implementation depends on backend
        pass

# Example usage
from covet import CovetPy
from covet.events import EventBus, Event, EventHandler

app = CovetPy()

# Initialize event bus
event_bus = EventBus({
    "backend": "embedded",  # or "kafka", "rabbitmq"
    "max_queue_size": 10000,
    "batch_size": 100,
})

# Function-based event handling
@event_bus.subscribe("user.created")
async def send_welcome_email(event: Event):
    user_data = event.data
    await send_email(user_data["email"], "Welcome!")

@event_bus.subscribe("user.created")
async def update_analytics(event: Event):
    await analytics.track("user_signup", event.data)

# Class-based event handling
class OrderEventHandler(EventHandler):
    @property
    def handled_events(self) -> List[str]:
        return ["order.created", "order.cancelled", "order.fulfilled"]
    
    async def handle(self, event: Event) -> None:
        if event.event_type == "order.created":
            await self.process_new_order(event.data)
        elif event.event_type == "order.cancelled":
            await self.process_cancellation(event.data)
        elif event.event_type == "order.fulfilled":
            await self.process_fulfillment(event.data)
    
    async def process_new_order(self, order_data: Dict[str, Any]):
        # Business logic for new orders
        await inventory.reserve_items(order_data["items"])
        await payment.charge(order_data["payment_info"])
    
    async def process_cancellation(self, order_data: Dict[str, Any]):
        # Business logic for cancellations
        await inventory.release_items(order_data["items"])
        await payment.refund(order_data["payment_info"])
    
    async def process_fulfillment(self, order_data: Dict[str, Any]):
        # Business logic for fulfillment
        await shipping.create_label(order_data)
        await notifications.send_tracking_info(order_data["customer"])

# Register handler
event_bus.register_handler(OrderEventHandler())

# API endpoints that publish events
@app.post("/users")
async def create_user(request):
    user_data = await request.json()
    
    # Create user in database
    user = await db.create_user(user_data)
    
    # Publish event
    event = Event(
        id=generate_uuid(),
        event_type="user.created",
        data={"user_id": user.id, "email": user.email},
        correlation_id=request.headers.get("X-Correlation-ID")
    )
    await event_bus.publish(event)
    
    return {"user_id": user.id}

@app.post("/orders")
async def create_order(request):
    order_data = await request.json()
    
    # Create order in database
    order = await db.create_order(order_data)
    
    # Publish event
    event = Event(
        id=generate_uuid(),
        event_type="order.created",
        data=order.to_dict(),
        correlation_id=request.headers.get("X-Correlation-ID")
    )
    await event_bus.publish(event)
    
    return {"order_id": order.id}
```

### 5. External Message Broker Integration

#### Kafka Integration

```rust
use kafka::producer::{Producer, Record, RequiredAcks};
use kafka::consumer::{Consumer, FetchOffset, GroupOffsetStorage};

pub struct KafkaEventBus {
    producer: Producer,
    consumer: Consumer,
    config: KafkaConfig,
    serializer: Box<dyn MessageSerializer>,
}

impl KafkaEventBus {
    pub fn new(config: KafkaConfig) -> Result<Self> {
        let producer = Producer::from_hosts(config.brokers.clone())
            .with_ack_timeout(Duration::from_secs(1))
            .with_required_acks(RequiredAcks::One)
            .create()?;
        
        let consumer = Consumer::from_hosts(config.brokers.clone())
            .with_topic_partitions(config.topics.clone())
            .with_fallback_offset(FetchOffset::Earliest)
            .with_group(config.consumer_group.clone())
            .create()?;
        
        Ok(Self {
            producer,
            consumer,
            config,
            serializer: Box::new(JsonSerializer::new()),
        })
    }
    
    pub async fn consume_events(&mut self) -> Result<()> {
        loop {
            let message_sets = self.consumer.poll()?;
            
            for ms in message_sets.iter() {
                for m in ms.messages() {
                    let event = self.serializer.deserialize(m.value)?;
                    
                    // Process event through local event bus
                    if let Err(e) = self.process_external_event(event).await {
                        log::error!("Failed to process Kafka event: {}", e);
                    }
                }
                
                // Commit offset
                let _ = self.consumer.consume_messageset(ms);
            }
            
            if let Err(e) = self.consumer.commit_consumed() {
                log::error!("Failed to commit Kafka offset: {}", e);
            }
        }
    }
}

#[async_trait]
impl EventPublisher for KafkaEventBus {
    async fn publish(&self, event: Event) -> Result<(), PublishError> {
        let topic = self.get_topic_for_event(&event)?;
        let key = event.partition_key.as_deref().unwrap_or("");
        let value = self.serializer.serialize(&event)?;
        
        let record = Record::from_key_value(&topic, key, &value);
        
        self.producer.send(&record)?;
        Ok(())
    }
}
```

#### RabbitMQ Integration

```rust
use lapin::{Connection, ConnectionProperties, Channel, Queue, Exchange};
use lapin::options::*;
use lapin::types::FieldTable;

pub struct RabbitMQEventBus {
    connection: Connection,
    channel: Channel,
    exchange: String,
    config: RabbitMQConfig,
}

impl RabbitMQEventBus {
    pub async fn new(config: RabbitMQConfig) -> Result<Self> {
        let connection = Connection::connect(
            &config.url,
            ConnectionProperties::default()
        ).await?;
        
        let channel = connection.create_channel().await?;
        
        // Declare exchange
        channel.exchange_declare(
            &config.exchange,
            lapin::ExchangeKind::Topic,
            ExchangeDeclareOptions::default(),
            FieldTable::default(),
        ).await?;
        
        Ok(Self {
            connection,
            channel,
            exchange: config.exchange,
            config,
        })
    }
    
    pub async fn setup_consumer(&self, queue_name: &str, routing_keys: Vec<String>) -> Result<()> {
        // Declare queue
        let queue = self.channel.queue_declare(
            queue_name,
            QueueDeclareOptions::default(),
            FieldTable::default(),
        ).await?;
        
        // Bind to routing keys
        for routing_key in routing_keys {
            self.channel.queue_bind(
                queue_name,
                &self.exchange,
                &routing_key,
                QueueBindOptions::default(),
                FieldTable::default(),
            ).await?;
        }
        
        // Start consuming
        let consumer = self.channel.basic_consume(
            queue_name,
            "covet_consumer",
            BasicConsumeOptions::default(),
            FieldTable::default(),
        ).await?;
        
        // Spawn message handler
        tokio::spawn(async move {
            consumer.for_each(move |delivery| async move {
                if let Ok((channel, delivery)) = delivery {
                    // Process message
                    if let Err(e) = self.process_rabbitmq_message(&delivery.data).await {
                        log::error!("Failed to process RabbitMQ message: {}", e);
                        // NACK message
                        let _ = channel.basic_nack(
                            delivery.delivery_tag,
                            BasicNackOptions::default()
                        ).await;
                    } else {
                        // ACK message
                        let _ = channel.basic_ack(
                            delivery.delivery_tag,
                            BasicAckOptions::default()
                        ).await;
                    }
                }
            }).await;
        });
        
        Ok(())
    }
}
```

### 6. Event Sourcing Support

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventStore {
    pub aggregate_id: Uuid,
    pub version: u64,
    pub event_type: String,
    pub event_data: serde_json::Value,
    pub metadata: HashMap<String, String>,
    pub timestamp: DateTime<Utc>,
}

#[async_trait]
pub trait EventStorage: Send + Sync {
    async fn append_events(
        &self,
        aggregate_id: Uuid,
        expected_version: u64,
        events: Vec<Event>,
    ) -> Result<u64, EventStoreError>;
    
    async fn load_events(
        &self,
        aggregate_id: Uuid,
        from_version: u64,
    ) -> Result<Vec<EventStore>, EventStoreError>;
    
    async fn load_events_by_type(
        &self,
        event_type: &str,
        from_timestamp: Option<DateTime<Utc>>,
    ) -> Result<Vec<EventStore>, EventStoreError>;
}

pub struct PostgresEventStorage {
    pool: Arc<sqlx::PgPool>,
}

impl PostgresEventStorage {
    pub fn new(pool: Arc<sqlx::PgPool>) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl EventStorage for PostgresEventStorage {
    async fn append_events(
        &self,
        aggregate_id: Uuid,
        expected_version: u64,
        events: Vec<Event>,
    ) -> Result<u64, EventStoreError> {
        let mut tx = self.pool.begin().await?;
        
        // Check current version
        let current_version: Option<i64> = sqlx::query_scalar(
            "SELECT MAX(version) FROM events WHERE aggregate_id = $1"
        )
        .bind(aggregate_id)
        .fetch_optional(&mut *tx)
        .await?;
        
        let current_version = current_version.unwrap_or(0) as u64;
        
        if current_version != expected_version {
            return Err(EventStoreError::VersionConflict {
                expected: expected_version,
                actual: current_version,
            });
        }
        
        // Insert events
        let mut new_version = expected_version;
        for event in events {
            new_version += 1;
            
            sqlx::query(
                r#"
                INSERT INTO events (aggregate_id, version, event_type, event_data, metadata, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
                "#
            )
            .bind(aggregate_id)
            .bind(new_version as i64)
            .bind(&event.event_type)
            .bind(&event.payload)
            .bind(serde_json::to_value(&event.headers)?)
            .bind(event.timestamp)
            .execute(&mut *tx)
            .await?;
        }
        
        tx.commit().await?;
        Ok(new_version)
    }
    
    async fn load_events(
        &self,
        aggregate_id: Uuid,
        from_version: u64,
    ) -> Result<Vec<EventStore>, EventStoreError> {
        let events = sqlx::query_as!(
            EventStore,
            r#"
            SELECT aggregate_id, version, event_type, event_data, metadata, timestamp
            FROM events
            WHERE aggregate_id = $1 AND version > $2
            ORDER BY version ASC
            "#,
            aggregate_id,
            from_version as i64
        )
        .fetch_all(&*self.pool)
        .await?;
        
        Ok(events)
    }
}
```

## Consequences

### Positive
1. **Scalability**: Handle millions of messages per second
2. **Reliability**: At-least-once delivery guarantees
3. **Flexibility**: Support for multiple messaging patterns
4. **Integration**: Seamless external broker integration
5. **Performance**: Lock-free queues for low latency
6. **Monitoring**: Built-in metrics and observability

### Negative
1. **Complexity**: Multiple message transport mechanisms
2. **Consistency**: Eventual consistency challenges
3. **Debugging**: Distributed event flow complexity
4. **Memory Usage**: In-memory queues require careful sizing

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Message Loss | Persistent storage, acknowledgments |
| Infinite Loops | Circuit breakers, retry limits |
| Memory Exhaustion | Backpressure, overflow strategies |
| Ordering Issues | Partition keys, single-threaded consumers |

## Performance Characteristics

| Metric | Target | Implementation |
|--------|--------|---------------|
| Throughput | 1M+ msg/sec | Lock-free queues, batching |
| Latency | <1ms P99 | In-memory processing |
| Memory Usage | <100MB base | Ring buffers, object pooling |
| Reliability | 99.9% delivery | Persistence, retries |

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Event Sourcing Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
- [CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Lock-free Programming](https://preshing.com/20120612/an-introduction-to-lock-free-programming/)