# ADR-006: Observability and Monitoring Architecture

## Status
Accepted

## Context

CovetPy requires comprehensive observability to support production deployments at scale where:

1. Distributed systems need end-to-end visibility across service boundaries
2. Performance monitoring must detect sub-millisecond anomalies
3. Business metrics and technical metrics must be correlated
4. Root cause analysis requires detailed context and correlation
5. Alerting must be actionable and minimize false positives
6. Compliance and audit requirements need detailed logging
7. Real-time monitoring dashboards are essential for operations
8. Historical analysis enables capacity planning and optimization
9. Integration with existing monitoring stacks (Prometheus, Grafana, ELK, Jaeger) is required
10. Overhead of observability must not impact application performance

Traditional application-level monitoring lacks the depth and performance required for high-throughput systems.

## Decision

We will implement a **multi-dimensional observability architecture** with native instrumentation, distributed tracing, structured logging, and comprehensive metrics collection.

### 1. Observability Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │  Business   │ │    Custom    │ │     Manual         │   │
│  │  Metrics    │ │   Metrics    │ │   Instrumentation  │   │
│  └─────────────┘ └──────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│   Automatic     │ │  Structured  │ │   Distributed   │
│   Metrics       │ │   Logging    │ │    Tracing      │
│   Collection    │ │              │ │                 │
│                 │ │              │ │                 │
│ ┌─────────────┐ │ │┌─────────────┐│ │ ┌─────────────┐ │
│ │  RED/USE    │ │ ││   JSON      ││ │ │   OpenTel   │ │
│ │  Metrics    │ │ ││   Logs      ││ │ │   Traces    │ │
│ └─────────────┘ │ │└─────────────┘│ │ └─────────────┘ │
│ ┌─────────────┐ │ │┌─────────────┐│ │ ┌─────────────┐ │
│ │ Performance │ │ ││ Correlation ││ │ │    Span     │ │
│ │   Metrics   │ │ ││    IDs      ││ │ │  Context    │ │
│ └─────────────┘ │ │└─────────────┘│ │ └─────────────┘ │
└─────────────────┘ └──────────────┘ └─────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│   Prometheus    │ │     ELK      │ │     Jaeger      │
│    Grafana      │ │   Fluentd    │ │   Zipkin        │
│   AlertManager  │ │   Kibana     │ │   DataDog APM   │
└─────────────────┘ └──────────────┘ └─────────────────┘
```

### 2. Metrics Collection System

#### High-Performance Metrics Core

```rust
use std::sync::atomic::{AtomicU64, AtomicI64, Ordering};
use std::collections::HashMap;
use parking_lot::RwLock;
use prometheus::{Counter, Histogram, Gauge, Registry};

pub struct MetricsCollector {
    // Core metrics
    request_counter: Counter,
    request_duration: Histogram,
    active_connections: Gauge,
    memory_usage: Gauge,
    
    // Custom metrics registry
    custom_counters: RwLock<HashMap<String, Counter>>,
    custom_histograms: RwLock<HashMap<String, Histogram>>,
    custom_gauges: RwLock<HashMap<String, Gauge>>,
    
    // High-frequency metrics (lock-free)
    fast_counters: RwLock<HashMap<String, AtomicU64>>,
    fast_gauges: RwLock<HashMap<String, AtomicI64>>,
    
    // Configuration
    config: MetricsConfig,
    registry: Registry,
}

#[derive(Clone)]
pub struct MetricsConfig {
    pub enabled: bool,
    pub collection_interval: Duration,
    pub batch_size: usize,
    pub max_cardinality: usize,
    pub namespace: String,
    pub default_buckets: Vec<f64>,
}

impl MetricsCollector {
    pub fn new(config: MetricsConfig) -> Self {
        let registry = Registry::new();
        
        // Create core metrics
        let request_counter = Counter::new("requests_total", "Total HTTP requests")
            .expect("Failed to create request counter");
        let request_duration = Histogram::with_opts(
            prometheus::HistogramOpts::new("request_duration_seconds", "Request duration")
                .buckets(config.default_buckets.clone())
        ).expect("Failed to create request duration histogram");
        let active_connections = Gauge::new("active_connections", "Active connections")
            .expect("Failed to create active connections gauge");
        let memory_usage = Gauge::new("memory_usage_bytes", "Memory usage in bytes")
            .expect("Failed to create memory usage gauge");
        
        // Register core metrics
        registry.register(Box::new(request_counter.clone())).unwrap();
        registry.register(Box::new(request_duration.clone())).unwrap();
        registry.register(Box::new(active_connections.clone())).unwrap();
        registry.register(Box::new(memory_usage.clone())).unwrap();
        
        Self {
            request_counter,
            request_duration,
            active_connections,
            memory_usage,
            custom_counters: RwLock::new(HashMap::new()),
            custom_histograms: RwLock::new(HashMap::new()),
            custom_gauges: RwLock::new(HashMap::new()),
            fast_counters: RwLock::new(HashMap::new()),
            fast_gauges: RwLock::new(HashMap::new()),
            config,
            registry,
        }
    }
    
    #[inline(always)]
    pub fn increment_requests(&self, labels: &[(&str, &str)]) {
        self.request_counter.with_label_values(
            &labels.iter().map(|(_, v)| *v).collect::<Vec<_>>()
        ).inc();
    }
    
    #[inline(always)]
    pub fn record_request_duration(&self, duration: Duration, labels: &[(&str, &str)]) {
        self.request_duration.with_label_values(
            &labels.iter().map(|(_, v)| *v).collect::<Vec<_>>()
        ).observe(duration.as_secs_f64());
    }
    
    #[inline(always)]
    pub fn set_active_connections(&self, count: i64) {
        self.active_connections.set(count as f64);
    }
    
    #[inline(always)]
    pub fn set_memory_usage(&self, bytes: u64) {
        self.memory_usage.set(bytes as f64);
    }
    
    // Fast metrics for high-frequency operations
    #[inline(always)]
    pub fn increment_fast_counter(&self, name: &str) {
        if let Some(counter) = self.fast_counters.read().get(name) {
            counter.fetch_add(1, Ordering::Relaxed);
        }
    }
    
    #[inline(always)]
    pub fn set_fast_gauge(&self, name: &str, value: i64) {
        if let Some(gauge) = self.fast_gauges.read().get(name) {
            gauge.store(value, Ordering::Relaxed);
        }
    }
    
    pub async fn create_custom_counter(&self, name: &str, help: &str, labels: Vec<String>) -> Result<()> {
        let opts = prometheus::Opts::new(name, help)
            .namespace(self.config.namespace.clone());
        
        let counter = if labels.is_empty() {
            Counter::with_opts(opts)?
        } else {
            prometheus::CounterVec::new(opts, &labels)?.into()
        };
        
        self.registry.register(Box::new(counter.clone()))?;
        self.custom_counters.write().insert(name.to_string(), counter);
        
        Ok(())
    }
    
    pub async fn create_custom_histogram(
        &self,
        name: &str,
        help: &str,
        buckets: Option<Vec<f64>>,
        labels: Vec<String>
    ) -> Result<()> {
        let buckets = buckets.unwrap_or_else(|| self.config.default_buckets.clone());
        let opts = prometheus::HistogramOpts::new(name, help)
            .namespace(self.config.namespace.clone())
            .buckets(buckets);
        
        let histogram = if labels.is_empty() {
            Histogram::with_opts(opts)?
        } else {
            prometheus::HistogramVec::new(opts, &labels)?.into()
        };
        
        self.registry.register(Box::new(histogram.clone()))?;
        self.custom_histograms.write().insert(name.to_string(), histogram);
        
        Ok(())
    }
    
    // Batch metric updates for efficiency
    pub async fn flush_fast_metrics(&self) {
        let fast_counters = self.fast_counters.read();
        let fast_gauges = self.fast_gauges.read();
        
        // Update Prometheus metrics from fast metrics
        for (name, atomic_counter) in fast_counters.iter() {
            let value = atomic_counter.swap(0, Ordering::Relaxed);
            if value > 0 {
                if let Some(counter) = self.custom_counters.read().get(name) {
                    counter.inc_by(value as f64);
                }
            }
        }
        
        for (name, atomic_gauge) in fast_gauges.iter() {
            let value = atomic_gauge.load(Ordering::Relaxed);
            if let Some(gauge) = self.custom_gauges.read().get(name) {
                gauge.set(value as f64);
            }
        }
    }
    
    pub fn export_metrics(&self) -> String {
        let encoder = prometheus::TextEncoder::new();
        let metric_families = self.registry.gather();
        encoder.encode_to_string(&metric_families).unwrap_or_default()
    }
}
```

#### Business Metrics Integration

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BusinessMetric {
    pub name: String,
    pub value: f64,
    pub unit: String,
    pub tags: HashMap<String, String>,
    pub timestamp: DateTime<Utc>,
}

pub struct BusinessMetricsCollector {
    metrics_buffer: RwLock<Vec<BusinessMetric>>,
    config: BusinessMetricsConfig,
    exporters: Vec<Box<dyn MetricsExporter>>,
}

#[async_trait]
pub trait MetricsExporter: Send + Sync {
    async fn export(&self, metrics: Vec<BusinessMetric>) -> Result<()>;
}

pub struct StatsDExporter {
    client: statsd::Client,
}

#[async_trait]
impl MetricsExporter for StatsDExporter {
    async fn export(&self, metrics: Vec<BusinessMetric>) -> Result<()> {
        for metric in metrics {
            let tags: Vec<String> = metric.tags.iter()
                .map(|(k, v)| format!("{}:{}", k, v))
                .collect();
            
            match metric.unit.as_str() {
                "count" => {
                    self.client.count_with_tags(&metric.name, metric.value as i64, &tags)?;
                }
                "gauge" => {
                    self.client.gauge_with_tags(&metric.name, metric.value, &tags)?;
                }
                "histogram" => {
                    self.client.histogram_with_tags(&metric.name, metric.value, &tags)?;
                }
                _ => {
                    self.client.gauge_with_tags(&metric.name, metric.value, &tags)?;
                }
            }
        }
        Ok(())
    }
}

impl BusinessMetricsCollector {
    pub fn record_metric(&self, metric: BusinessMetric) {
        let mut buffer = self.metrics_buffer.write();
        buffer.push(metric);
        
        // Flush if buffer is full
        if buffer.len() >= self.config.batch_size {
            let metrics = buffer.drain(..).collect();
            let exporters = self.exporters.clone();
            
            tokio::spawn(async move {
                for exporter in exporters {
                    if let Err(e) = exporter.export(metrics.clone()).await {
                        log::error!("Failed to export business metrics: {}", e);
                    }
                }
            });
        }
    }
}
```

### 3. Distributed Tracing Implementation

#### OpenTelemetry Integration

```rust
use opentelemetry::{
    trace::{Tracer, TracerProvider, Span, SpanKind, Status},
    Context, KeyValue,
};
use opentelemetry_jaeger::JaegerPropagator;
use opentelemetry_sdk::trace::{TracerProvider as SdkTracerProvider, Config};

pub struct TracingSystem {
    tracer: Box<dyn Tracer + Send + Sync>,
    propagator: JaegerPropagator,
    config: TracingConfig,
}

#[derive(Clone)]
pub struct TracingConfig {
    pub enabled: bool,
    pub service_name: String,
    pub service_version: String,
    pub jaeger_endpoint: Option<String>,
    pub sampling_ratio: f64,
    pub max_span_attributes: usize,
    pub max_span_events: usize,
}

impl TracingSystem {
    pub fn new(config: TracingConfig) -> Result<Self> {
        let tracer_provider = SdkTracerProvider::builder()
            .with_config(Config {
                default_sampler: Box::new(
                    opentelemetry_sdk::trace::Sampler::TraceIdRatioBased(config.sampling_ratio)
                ),
                ..Default::default()
            })
            .with_batch_exporter(
                opentelemetry_jaeger::new_agent_pipeline()
                    .with_service_name(&config.service_name)
                    .with_endpoint(&config.jaeger_endpoint.clone().unwrap_or_default())
                    .build_batch_exporter()?,
                opentelemetry_sdk::runtime::Tokio,
            )
            .build();
        
        let tracer = tracer_provider.tracer(&config.service_name);
        let propagator = JaegerPropagator::new();
        
        Ok(Self {
            tracer: Box::new(tracer),
            propagator,
            config,
        })
    }
    
    pub fn start_span(&self, name: &str) -> SpanContext {
        let span = self.tracer.start(name);
        SpanContext::new(span, self)
    }
    
    pub fn start_span_with_parent(&self, name: &str, parent_context: &Context) -> SpanContext {
        let span = self.tracer.start_with_context(name, parent_context);
        SpanContext::new(span, self)
    }
    
    pub fn extract_context(&self, headers: &HashMap<String, String>) -> Context {
        let mut carrier = HashMap::new();
        for (key, value) in headers {
            carrier.insert(key.clone(), value.clone());
        }
        
        self.propagator.extract(&carrier)
    }
    
    pub fn inject_context(&self, context: &Context, headers: &mut HashMap<String, String>) {
        let mut carrier = HashMap::new();
        self.propagator.inject_context(context, &mut carrier);
        
        for (key, value) in carrier {
            headers.insert(key, value);
        }
    }
}

pub struct SpanContext<'a> {
    span: Box<dyn Span + Send + Sync>,
    tracing_system: &'a TracingSystem,
}

impl<'a> SpanContext<'a> {
    fn new(span: Box<dyn Span + Send + Sync>, tracing_system: &'a TracingSystem) -> Self {
        Self { span, tracing_system }
    }
    
    pub fn set_attribute(&mut self, key: &str, value: &str) {
        self.span.set_attribute(KeyValue::new(key, value.to_string()));
    }
    
    pub fn set_status(&mut self, status: SpanStatus) {
        match status {
            SpanStatus::Ok => self.span.set_status(Status::Ok),
            SpanStatus::Error(message) => self.span.set_status(Status::error(message)),
        }
    }
    
    pub fn add_event(&mut self, name: &str, attributes: Vec<(&str, &str)>) {
        let attrs: Vec<KeyValue> = attributes.into_iter()
            .map(|(k, v)| KeyValue::new(k, v.to_string()))
            .collect();
        
        self.span.add_event(name, attrs);
    }
    
    pub fn context(&self) -> Context {
        Context::current_with_span(self.span.as_ref())
    }
}

impl<'a> Drop for SpanContext<'a> {
    fn drop(&mut self) {
        self.span.end();
    }
}

#[derive(Debug)]
pub enum SpanStatus {
    Ok,
    Error(String),
}
```

### 4. Structured Logging System

```rust
use serde_json::{json, Value};
use chrono::{DateTime, Utc};

pub struct StructuredLogger {
    config: LoggingConfig,
    correlation_context: Arc<RwLock<HashMap<String, String>>>,
    appenders: Vec<Box<dyn LogAppender>>,
}

#[derive(Clone)]
pub struct LoggingConfig {
    pub level: LogLevel,
    pub format: LogFormat,
    pub include_caller: bool,
    pub include_timestamp: bool,
    pub max_message_size: usize,
    pub correlation_fields: Vec<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LogLevel {
    Trace = 0,
    Debug = 1,
    Info = 2,
    Warn = 3,
    Error = 4,
    Fatal = 5,
}

#[derive(Debug, Clone)]
pub enum LogFormat {
    Json,
    Structured,
    Plain,
}

#[derive(Debug, Clone)]
pub struct LogEntry {
    pub timestamp: DateTime<Utc>,
    pub level: LogLevel,
    pub message: String,
    pub fields: HashMap<String, Value>,
    pub caller: Option<String>,
    pub correlation_id: Option<String>,
    pub trace_id: Option<String>,
    pub span_id: Option<String>,
}

#[async_trait]
pub trait LogAppender: Send + Sync {
    async fn append(&self, entry: LogEntry) -> Result<()>;
}

pub struct FileAppender {
    file: Arc<Mutex<File>>,
    rotation_config: Option<RotationConfig>,
}

pub struct ElasticsearchAppender {
    client: elasticsearch::Elasticsearch,
    index_pattern: String,
}

#[async_trait]
impl LogAppender for ElasticsearchAppender {
    async fn append(&self, entry: LogEntry) -> Result<()> {
        let index = format!("{}-{}", 
            self.index_pattern, 
            entry.timestamp.format("%Y.%m.%d")
        );
        
        let document = json!({
            "@timestamp": entry.timestamp,
            "level": format!("{:?}", entry.level),
            "message": entry.message,
            "fields": entry.fields,
            "caller": entry.caller,
            "correlation_id": entry.correlation_id,
            "trace_id": entry.trace_id,
            "span_id": entry.span_id,
        });
        
        self.client
            .index(elasticsearch::IndexParts::Index(&index))
            .body(document)
            .send()
            .await?;
        
        Ok(())
    }
}

impl StructuredLogger {
    pub fn new(config: LoggingConfig) -> Self {
        Self {
            config,
            correlation_context: Arc::new(RwLock::new(HashMap::new())),
            appenders: Vec::new(),
        }
    }
    
    pub fn add_appender(&mut self, appender: Box<dyn LogAppender>) {
        self.appenders.push(appender);
    }
    
    pub async fn log(&self, level: LogLevel, message: &str, fields: HashMap<String, Value>) {
        if level < self.config.level {
            return;
        }
        
        let correlation_context = self.correlation_context.read();
        
        let entry = LogEntry {
            timestamp: Utc::now(),
            level,
            message: message.to_string(),
            fields,
            caller: if self.config.include_caller {
                Some(self.get_caller())
            } else {
                None
            },
            correlation_id: correlation_context.get("correlation_id").cloned(),
            trace_id: correlation_context.get("trace_id").cloned(),
            span_id: correlation_context.get("span_id").cloned(),
        };
        
        // Send to all appenders
        for appender in &self.appenders {
            if let Err(e) = appender.append(entry.clone()).await {
                eprintln!("Failed to append log entry: {}", e);
            }
        }
    }
    
    pub fn set_correlation_context(&self, fields: HashMap<String, String>) {
        let mut context = self.correlation_context.write();
        context.extend(fields);
    }
    
    pub fn clear_correlation_context(&self) {
        self.correlation_context.write().clear();
    }
    
    fn get_caller(&self) -> String {
        // Implementation to get file:line information
        "unknown".to_string()
    }
}

// Convenient logging macros
#[macro_export]
macro_rules! log_info {
    ($logger:expr, $msg:expr) => {
        $logger.log(LogLevel::Info, $msg, HashMap::new()).await
    };
    ($logger:expr, $msg:expr, $($field:expr => $value:expr),+) => {
        {
            let mut fields = HashMap::new();
            $(
                fields.insert($field.to_string(), serde_json::to_value($value).unwrap());
            )+
            $logger.log(LogLevel::Info, $msg, fields).await
        }
    };
}
```

### 5. Python Observability API

```python
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
import asyncio
import contextvars

class LogLevel(Enum):
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5

@dataclass
class MetricConfig:
    namespace: str = "covet"
    enabled: bool = True
    collection_interval: float = 10.0
    batch_size: int = 100
    max_cardinality: int = 10000

@dataclass
class TracingConfig:
    enabled: bool = True
    service_name: str = "covet-service"
    service_version: str = "1.0.0"
    jaeger_endpoint: Optional[str] = None
    sampling_ratio: float = 0.1
    max_span_attributes: int = 32

@dataclass
class LoggingConfig:
    level: LogLevel = LogLevel.INFO
    format: str = "json"
    include_caller: bool = False
    correlation_fields: List[str] = field(default_factory=lambda: ["correlation_id", "trace_id"])

# Context variables for correlation
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id')
trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('trace_id')
span_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('span_id')

class Observability:
    """High-level observability interface for CovetPy applications"""
    
    def __init__(
        self,
        metrics_config: Optional[MetricConfig] = None,
        tracing_config: Optional[TracingConfig] = None,
        logging_config: Optional[LoggingConfig] = None,
    ):
        self.metrics_config = metrics_config or MetricConfig()
        self.tracing_config = tracing_config or TracingConfig()
        self.logging_config = logging_config or LoggingConfig()
        
        self._metrics = {}
        self._business_metrics = []
        self._active_spans = {}
    
    # Metrics API
    def counter(self, name: str, help: str = "", labels: List[str] = None) -> 'Counter':
        """Create or get a counter metric"""
        if name not in self._metrics:
            self._metrics[name] = Counter(name, help, labels or [])
        return self._metrics[name]
    
    def histogram(self, name: str, help: str = "", buckets: List[float] = None, labels: List[str] = None) -> 'Histogram':
        """Create or get a histogram metric"""
        if name not in self._metrics:
            self._metrics[name] = Histogram(name, help, buckets, labels or [])
        return self._metrics[name]
    
    def gauge(self, name: str, help: str = "", labels: List[str] = None) -> 'Gauge':
        """Create or get a gauge metric"""
        if name not in self._metrics:
            self._metrics[name] = Gauge(name, help, labels or [])
        return self._metrics[name]
    
    def business_metric(self, name: str, value: float, unit: str = "count", tags: Dict[str, str] = None):
        """Record a business metric"""
        metric = {
            "name": name,
            "value": value,
            "unit": unit,
            "tags": tags or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._business_metrics.append(metric)
    
    # Tracing API
    def start_span(self, name: str, parent: Optional['Span'] = None) -> 'Span':
        """Start a new trace span"""
        return Span(name, parent, self)
    
    def current_span(self) -> Optional['Span']:
        """Get the current active span"""
        span_id = span_id_var.get(None)
        return self._active_spans.get(span_id) if span_id else None
    
    # Logging API
    def log(self, level: LogLevel, message: str, **fields):
        """Log a structured message"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.name,
            "message": message,
            "fields": fields,
            "correlation_id": correlation_id_var.get(None),
            "trace_id": trace_id_var.get(None),
            "span_id": span_id_var.get(None),
        }
        
        # Send to Rust logging system
        self._log_entry(entry)
    
    def info(self, message: str, **fields):
        self.log(LogLevel.INFO, message, **fields)
    
    def warn(self, message: str, **fields):
        self.log(LogLevel.WARN, message, **fields)
    
    def error(self, message: str, **fields):
        self.log(LogLevel.ERROR, message, **fields)
    
    def debug(self, message: str, **fields):
        self.log(LogLevel.DEBUG, message, **fields)
    
    # Context management
    def set_correlation_id(self, correlation_id: str):
        correlation_id_var.set(correlation_id)
    
    def set_trace_context(self, trace_id: str, span_id: str):
        trace_id_var.set(trace_id)
        span_id_var.set(span_id)

class Counter:
    def __init__(self, name: str, help: str, labels: List[str]):
        self.name = name
        self.help = help
        self.labels = labels
        self._value = 0
    
    def inc(self, amount: float = 1.0):
        """Increment the counter"""
        self._value += amount
        # Call Rust implementation
    
    def labels(self, **label_values) -> 'Counter':
        """Return counter with specific label values"""
        # Implementation for labeled metrics
        return self

class Histogram:
    def __init__(self, name: str, help: str, buckets: Optional[List[float]], labels: List[str]):
        self.name = name
        self.help = help
        self.buckets = buckets or [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        self.labels = labels
    
    def observe(self, value: float):
        """Record a value in the histogram"""
        # Call Rust implementation
        pass
    
    def time(self) -> 'Timer':
        """Return a timer context manager"""
        return Timer(self)

class Timer:
    def __init__(self, histogram: Histogram):
        self.histogram = histogram
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.perf_counter() - self.start_time
            self.histogram.observe(duration)

class Gauge:
    def __init__(self, name: str, help: str, labels: List[str]):
        self.name = name
        self.help = help
        self.labels = labels
        self._value = 0
    
    def set(self, value: float):
        """Set the gauge value"""
        self._value = value
        # Call Rust implementation
    
    def inc(self, amount: float = 1.0):
        """Increment the gauge"""
        self._value += amount
        # Call Rust implementation
    
    def dec(self, amount: float = 1.0):
        """Decrement the gauge"""
        self._value -= amount
        # Call Rust implementation

class Span:
    def __init__(self, name: str, parent: Optional['Span'], observability: Observability):
        self.name = name
        self.parent = parent
        self.observability = observability
        self.span_id = self._generate_span_id()
        self.trace_id = parent.trace_id if parent else self._generate_trace_id()
        self.start_time = time.perf_counter()
        self.attributes = {}
        self.events = []
        self.finished = False
    
    def set_attribute(self, key: str, value: Any):
        """Set a span attribute"""
        self.attributes[key] = value
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add an event to the span"""
        event = {
            "name": name,
            "timestamp": time.perf_counter(),
            "attributes": attributes or {},
        }
        self.events.append(event)
    
    def set_status(self, status: str, description: str = ""):
        """Set span status"""
        self.set_attribute("status", status)
        if description:
            self.set_attribute("status_description", description)
    
    def finish(self):
        """Finish the span"""
        if not self.finished:
            self.finished = True
            duration = time.perf_counter() - self.start_time
            self.set_attribute("duration_ms", duration * 1000)
            
            # Remove from active spans
            if self.span_id in self.observability._active_spans:
                del self.observability._active_spans[self.span_id]
    
    def __enter__(self):
        # Set context variables
        span_id_var.set(self.span_id)
        trace_id_var.set(self.trace_id)
        
        # Add to active spans
        self.observability._active_spans[self.span_id] = self
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.set_status("error", str(exc_val))
        else:
            self.set_status("ok")
        
        self.finish()

# Integration with CovetPy
from covet import CovetPy

def setup_observability(app: CovetPy, config: Dict[str, Any] = None) -> Observability:
    """Setup observability for a CovetPy application"""
    
    config = config or {}
    
    observability = Observability(
        metrics_config=MetricConfig(**config.get("metrics", {})),
        tracing_config=TracingConfig(**config.get("tracing", {})),
        logging_config=LoggingConfig(**config.get("logging", {})),
    )
    
    # Add observability middleware
    @app.middleware("observability")
    async def observability_middleware(request, call_next):
        # Extract trace context from headers
        trace_id = request.headers.get("x-trace-id")
        span_id = request.headers.get("x-span-id")
        correlation_id = request.headers.get("x-correlation-id") or generate_correlation_id()
        
        # Set context
        observability.set_correlation_id(correlation_id)
        if trace_id and span_id:
            observability.set_trace_context(trace_id, span_id)
        
        # Start request span
        with observability.start_span("http_request") as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.user_agent", request.headers.get("user-agent", ""))
            
            start_time = time.perf_counter()
            
            try:
                response = await call_next(request)
                
                # Record metrics
                duration = time.perf_counter() - start_time
                observability.histogram("http_request_duration").observe(duration)
                observability.counter("http_requests_total").inc()
                
                # Set span attributes
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.response_size", len(response.body) if hasattr(response, 'body') else 0)
                
                # Add response headers
                response.headers["x-correlation-id"] = correlation_id
                if trace_id:
                    response.headers["x-trace-id"] = trace_id
                
                return response
                
            except Exception as e:
                # Record error metrics
                observability.counter("http_requests_errors_total").inc()
                
                # Log error
                observability.error("Request failed", 
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                
                raise
    
    # Add metrics endpoint
    @app.get("/_metrics")
    async def metrics_endpoint():
        return observability._export_metrics()
    
    # Add health check endpoint
    @app.get("/_health")
    async def health_endpoint():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": observability.tracing_config.service_name,
            "version": observability.tracing_config.service_version,
        }
    
    return observability

# Example usage
app = CovetPy()
obs = setup_observability(app, {
    "metrics": {"namespace": "my_service"},
    "tracing": {"service_name": "my-service", "sampling_ratio": 0.2},
    "logging": {"level": "INFO"}
})

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    # Custom metrics
    obs.counter("user_requests_total").inc()
    obs.business_metric("user_lookup", 1, "count", {"user_type": "premium"})
    
    # Custom tracing
    with obs.start_span("database_query") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("query", "SELECT * FROM users WHERE id = ?")
        
        user = await db.get_user(user_id)
        
        span.set_attribute("rows_returned", 1 if user else 0)
    
    # Custom logging
    obs.info("User retrieved", user_id=user_id, found=bool(user))
    
    if not user:
        obs.warn("User not found", user_id=user_id)
        return {"error": "User not found"}, 404
    
    return {"user": user}
```

## Consequences

### Positive
1. **Comprehensive Visibility**: Full observability across all system layers
2. **Performance**: Minimal overhead through native instrumentation
3. **Correlation**: Automatic correlation across metrics, traces, and logs
4. **Integration**: Seamless integration with existing monitoring stacks
5. **Actionable**: Rich context for troubleshooting and optimization
6. **Compliance**: Detailed audit trails and compliance reporting

### Negative
1. **Complexity**: Additional operational complexity
2. **Storage**: High volume of observability data
3. **Cost**: Infrastructure costs for observability stack
4. **Performance**: Overhead from comprehensive instrumentation

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Performance Impact | Async processing, sampling, batching |
| Data Volume | Retention policies, aggregation, sampling |
| Privacy/Security | PII scrubbing, access controls |
| Alert Fatigue | Intelligent alerting, SLO-based alerts |

## Performance Characteristics

| Metric | Target | Implementation |
|--------|--------|---------------|
| Metrics Overhead | <1% CPU | Lock-free counters, batching |
| Trace Overhead | <5% latency | Sampling, async export |
| Log Overhead | <2% CPU | Async appenders, structured format |
| Memory Usage | <100MB | Bounded buffers, rotation |

## Implementation Roadmap

### Phase 1: Core Observability (Weeks 1-2)
- Metrics collection system
- Basic tracing implementation
- Structured logging
- Python API development

### Phase 2: Integration (Weeks 3-4)
- Prometheus/Grafana integration
- Jaeger/Zipkin integration
- Elasticsearch/Kibana integration
- Business metrics support

### Phase 3: Advanced Features (Weeks 5-6)
- Correlation and context propagation
- SLO/SLI monitoring
- Custom dashboards
- Alert management

### Phase 4: Production (Weeks 7-8)
- Performance optimization
- Comprehensive testing
- Documentation
- Monitoring runbooks

## References

- [OpenTelemetry Specification](https://opentelemetry.io/docs/reference/specification/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Distributed Tracing](https://microservices.io/patterns/observability/distributed-tracing.html)
- [Structured Logging](https://stackify.com/what-is-structured-logging-and-why-developers-need-it/)
- [SRE Observability](https://sre.google/sre-book/monitoring-distributed-systems/)