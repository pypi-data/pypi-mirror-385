# ADR-005: Service Mesh Capabilities

## Status
Accepted

## Context

CovetPy applications need to operate effectively in modern microservices architectures where:

1. Services communicate across network boundaries with varying reliability
2. Traffic management, load balancing, and routing require sophisticated control
3. Security policies (mTLS, authentication, authorization) must be enforced consistently
4. Observability (metrics, tracing, logging) needs to be automatic and comprehensive
5. Service discovery and configuration management must be dynamic
6. Circuit breaking, retries, and timeouts are essential for resilience
7. A/B testing, canary deployments, and traffic splitting are operational requirements
8. Integration with existing service mesh solutions (Istio, Linkerd, Consul Connect) is necessary

Traditional application-level implementations of these features result in code duplication, inconsistent behavior, and maintenance overhead across services.

## Decision

We will implement **native service mesh capabilities** within CovetPy that can operate both as a standalone service mesh and integrate with existing mesh solutions.

### 1. Service Mesh Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Control Plane                            │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │   Service   │ │    Policy    │ │    Configuration   │   │
│  │  Discovery  │ │   Engine     │ │     Manager        │   │
│  └─────────────┘ └──────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│     Sidecar     │ │   Gateway    │ │   Load Balancer │
│     Proxy       │ │    Proxy     │ │     Proxy       │
│                 │ │              │ │                 │
│ ┌─────────────┐ │ │┌─────────────┐│ │ ┌─────────────┐ │
│ │  Traffic    │ │ ││   Ingress   ││ │ │  Service    │ │
│ │   Proxy     │ │ ││   Traffic   ││ │ │   Registry  │ │
│ └─────────────┘ │ │└─────────────┘│ │ └─────────────┘ │
│ ┌─────────────┐ │ │┌─────────────┐│ │ ┌─────────────┐ │
│ │   mTLS      │ │ ││    Rate     ││ │ │  Health     │ │
│ │ Termination │ │ ││  Limiting   ││ │ │   Checks    │ │
│ └─────────────┘ │ │└─────────────┘│ │ └─────────────┘ │
└─────────────────┘ └──────────────┐ └─────────────────┘
         │                         │           │
         ▼                         ▼           ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  CovetPy          │ │ External     │ │  CovetPy          │
│  Service A      │ │ Services     │ │  Service B      │
└─────────────────┘ └──────────────┘ └─────────────────┘
```

### 2. Sidecar Proxy Implementation

#### High-Performance Proxy Core

```rust
use tokio::net::{TcpListener, TcpStream};
use hyper::{Body, Request, Response, Server};
use tower::{Service, ServiceBuilder, make::Shared};
use tower_http::{trace::TraceLayer, compression::CompressionLayer};

pub struct SidecarProxy {
    // Network configuration
    bind_address: SocketAddr,
    upstream_services: Arc<RwLock<ServiceRegistry>>,
    
    // Traffic management
    load_balancer: Arc<dyn LoadBalancer>,
    circuit_breaker: Arc<CircuitBreakerRegistry>,
    rate_limiter: Arc<RateLimiterRegistry>,
    
    // Security
    tls_config: Option<TlsConfig>,
    auth_policy: Arc<AuthPolicy>,
    
    // Observability
    metrics_collector: Arc<MetricsCollector>,
    tracer: Arc<dyn Tracer>,
    
    // Configuration
    config: ProxyConfig,
}

impl SidecarProxy {
    pub async fn new(config: ProxyConfig) -> Result<Self> {
        let upstream_services = Arc::new(RwLock::new(ServiceRegistry::new()));
        let load_balancer = Arc::new(RoundRobinBalancer::new());
        let circuit_breaker = Arc::new(CircuitBreakerRegistry::new());
        let rate_limiter = Arc::new(RateLimiterRegistry::new());
        
        Ok(Self {
            bind_address: config.bind_address,
            upstream_services,
            load_balancer,
            circuit_breaker,
            rate_limiter,
            tls_config: config.tls_config,
            auth_policy: Arc::new(AuthPolicy::from_config(&config.auth)),
            metrics_collector: Arc::new(MetricsCollector::new()),
            tracer: Arc::new(JaegerTracer::new(config.tracing)),
            config,
        })
    }
    
    pub async fn start(&self) -> Result<()> {
        let listener = TcpListener::bind(self.bind_address).await?;
        log::info!("Sidecar proxy listening on {}", self.bind_address);
        
        while let Ok((stream, addr)) = listener.accept().await {
            let proxy = self.clone();
            tokio::spawn(async move {
                if let Err(e) = proxy.handle_connection(stream, addr).await {
                    log::error!("Failed to handle connection from {}: {}", addr, e);
                }
            });
        }
        
        Ok(())
    }
    
    async fn handle_connection(&self, stream: TcpStream, client_addr: SocketAddr) -> Result<()> {
        // Configure TLS if required
        let stream = if let Some(tls_config) = &self.tls_config {
            self.configure_tls(stream, tls_config).await?
        } else {
            Box::new(stream) as Box<dyn AsyncRead + AsyncWrite + Unpin + Send>
        };
        
        // Create HTTP service
        let service = ServiceBuilder::new()
            .layer(TraceLayer::new_for_http())
            .layer(CompressionLayer::new())
            .service(ProxyService {
                proxy: self.clone(),
                client_addr,
            });
        
        // Serve HTTP
        hyper::server::conn::http1::Builder::new()
            .serve_connection(stream, service)
            .await?;
        
        Ok(())
    }
}

#[derive(Clone)]
struct ProxyService {
    proxy: SidecarProxy,
    client_addr: SocketAddr,
}

impl Service<Request<Body>> for ProxyService {
    type Response = Response<Body>;
    type Error = hyper::Error;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;
    
    fn poll_ready(&mut self, _cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        Poll::Ready(Ok(()))
    }
    
    fn call(&mut self, req: Request<Body>) -> Self::Future {
        let proxy = self.proxy.clone();
        let client_addr = self.client_addr;
        
        Box::pin(async move {
            proxy.proxy_request(req, client_addr).await
        })
    }
}

impl SidecarProxy {
    async fn proxy_request(
        &self,
        mut req: Request<Body>,
        client_addr: SocketAddr,
    ) -> Result<Response<Body>, hyper::Error> {
        let start_time = Instant::now();
        let trace_id = self.generate_trace_id();
        
        // Start distributed trace
        let span = self.tracer.start_span("proxy_request")
            .with_tag("trace_id", &trace_id)
            .with_tag("client_addr", &client_addr.to_string())
            .with_tag("method", req.method().as_str())
            .with_tag("path", req.uri().path());
        
        // Extract service from request
        let service_name = self.extract_service_name(&req)?;
        
        // Apply authentication policy
        if let Err(e) = self.auth_policy.authenticate(&req, client_addr).await {
            span.set_tag("auth_result", "failed");
            span.set_tag("auth_error", &e.to_string());
            return Ok(self.create_auth_error_response(e));
        }
        
        // Apply rate limiting
        if let Err(e) = self.rate_limiter.check_rate_limit(&service_name, client_addr).await {
            span.set_tag("rate_limit_result", "exceeded");
            return Ok(self.create_rate_limit_response());
        }
        
        // Check circuit breaker
        if self.circuit_breaker.is_open(&service_name).await {
            span.set_tag("circuit_breaker", "open");
            return Ok(self.create_circuit_breaker_response());
        }
        
        // Select upstream service
        let upstream = match self.load_balancer.select_upstream(&service_name).await {
            Some(upstream) => upstream,
            None => {
                span.set_tag("upstream_selection", "failed");
                return Ok(self.create_service_unavailable_response());
            }
        };
        
        // Add proxy headers
        self.add_proxy_headers(&mut req, &trace_id, client_addr);
        
        // Proxy to upstream
        let result = self.forward_request(req, &upstream).await;
        
        // Record metrics
        let duration = start_time.elapsed();
        self.metrics_collector.record_request(
            &service_name,
            &upstream.address,
            duration,
            result.is_ok(),
        );
        
        // Update circuit breaker
        match &result {
            Ok(_) => self.circuit_breaker.record_success(&service_name).await,
            Err(_) => self.circuit_breaker.record_failure(&service_name).await,
        }
        
        // Finish trace
        span.set_tag("duration_ms", duration.as_millis() as i64);
        span.set_tag("upstream", &upstream.address);
        span.finish();
        
        result
    }
    
    async fn forward_request(
        &self,
        req: Request<Body>,
        upstream: &UpstreamService,
    ) -> Result<Response<Body>, hyper::Error> {
        let client = &upstream.client;
        
        // Configure request URI for upstream
        let mut uri_parts = req.uri().clone().into_parts();
        uri_parts.scheme = Some(upstream.scheme.clone());
        uri_parts.authority = Some(upstream.authority.clone());
        
        let new_uri = hyper::Uri::from_parts(uri_parts)
            .map_err(|e| hyper::Error::from(e))?;
        
        let (mut parts, body) = req.into_parts();
        parts.uri = new_uri;
        let new_req = Request::from_parts(parts, body);
        
        // Forward request with timeout
        let response = tokio::time::timeout(
            self.config.upstream_timeout,
            client.request(new_req)
        ).await;
        
        match response {
            Ok(Ok(resp)) => Ok(resp),
            Ok(Err(e)) => Err(e),
            Err(_) => Ok(self.create_timeout_response()),
        }
    }
}
```

### 3. Service Discovery Integration

```rust
use consul::Consul;
use k8s_openapi::api::core::v1::Service;
use kube::{Api, Client};

#[async_trait]
pub trait ServiceDiscovery: Send + Sync {
    async fn register_service(&self, service: ServiceRegistration) -> Result<()>;
    async fn deregister_service(&self, service_id: &str) -> Result<()>;
    async fn discover_services(&self, service_name: &str) -> Result<Vec<ServiceInstance>>;
    async fn watch_services(&self, callback: Box<dyn ServiceWatcher>) -> Result<()>;
}

pub struct ConsulServiceDiscovery {
    client: Consul,
    config: ConsulConfig,
}

impl ConsulServiceDiscovery {
    pub fn new(config: ConsulConfig) -> Self {
        let client = Consul::new(config.address.clone())
            .with_token(config.token.clone());
        
        Self { client, config }
    }
}

#[async_trait]
impl ServiceDiscovery for ConsulServiceDiscovery {
    async fn register_service(&self, service: ServiceRegistration) -> Result<()> {
        let registration = consul::ServiceRegistration {
            id: service.id,
            name: service.name,
            tags: service.tags,
            address: service.address,
            port: service.port,
            check: Some(consul::HealthCheck {
                http: Some(format!("http://{}:{}/health", service.address, service.port)),
                interval: "10s".to_string(),
                timeout: "3s".to_string(),
            }),
        };
        
        self.client.register_service(registration).await?;
        Ok(())
    }
    
    async fn discover_services(&self, service_name: &str) -> Result<Vec<ServiceInstance>> {
        let services = self.client.get_healthy_services(service_name).await?;
        
        let instances = services.into_iter().map(|s| ServiceInstance {
            id: s.service.id,
            name: s.service.service,
            address: s.service.address,
            port: s.service.port,
            tags: s.service.tags,
            metadata: s.service.meta,
            health_status: HealthStatus::Healthy,
        }).collect();
        
        Ok(instances)
    }
    
    async fn watch_services(&self, callback: Box<dyn ServiceWatcher>) -> Result<()> {
        let mut watcher = self.client.watch_services().await?;
        
        while let Some(event) = watcher.next().await {
            match event? {
                ServiceEvent::Added(service) => {
                    callback.on_service_added(service).await;
                }
                ServiceEvent::Modified(service) => {
                    callback.on_service_modified(service).await;
                }
                ServiceEvent::Deleted(service_id) => {
                    callback.on_service_deleted(&service_id).await;
                }
            }
        }
        
        Ok(())
    }
}

pub struct KubernetesServiceDiscovery {
    client: Client,
    namespace: String,
}

impl KubernetesServiceDiscovery {
    pub async fn new(namespace: String) -> Result<Self> {
        let client = Client::try_default().await?;
        Ok(Self { client, namespace })
    }
}

#[async_trait]
impl ServiceDiscovery for KubernetesServiceDiscovery {
    async fn discover_services(&self, service_name: &str) -> Result<Vec<ServiceInstance>> {
        let services: Api<Service> = Api::namespaced(self.client.clone(), &self.namespace);
        let service_list = services.list(&Default::default()).await?;
        
        let instances = service_list.items.into_iter()
            .filter(|s| s.metadata.name.as_ref() == Some(&service_name.to_string()))
            .filter_map(|s| self.service_to_instance(s))
            .collect();
        
        Ok(instances)
    }
    
    fn service_to_instance(&self, service: Service) -> Option<ServiceInstance> {
        let metadata = service.metadata;
        let spec = service.spec?;
        
        let name = metadata.name?;
        let cluster_ip = spec.cluster_ip?;
        let port = spec.ports?.get(0)?.port?;
        
        Some(ServiceInstance {
            id: format!("{}:{}", name, port),
            name,
            address: cluster_ip,
            port: port as u16,
            tags: vec![],
            metadata: metadata.labels.unwrap_or_default(),
            health_status: HealthStatus::Unknown,
        })
    }
}
```

### 4. Traffic Management

#### Load Balancing Strategies

```rust
use std::sync::atomic::{AtomicUsize, Ordering};
use std::collections::HashMap;
use std::time::{Duration, Instant};

#[async_trait]
pub trait LoadBalancer: Send + Sync {
    async fn select_upstream(&self, service_name: &str) -> Option<UpstreamService>;
    async fn update_upstreams(&self, service_name: &str, upstreams: Vec<UpstreamService>);
    async fn record_response(&self, upstream: &UpstreamService, latency: Duration, success: bool);
}

pub struct WeightedRoundRobinBalancer {
    upstreams: RwLock<HashMap<String, Vec<WeightedUpstream>>>,
    counters: RwLock<HashMap<String, AtomicUsize>>,
}

struct WeightedUpstream {
    service: UpstreamService,
    weight: u32,
    current_weight: AtomicUsize,
    effective_weight: AtomicUsize,
}

impl WeightedRoundRobinBalancer {
    pub fn new() -> Self {
        Self {
            upstreams: RwLock::new(HashMap::new()),
            counters: RwLock::new(HashMap::new()),
        }
    }
}

#[async_trait]
impl LoadBalancer for WeightedRoundRobinBalancer {
    async fn select_upstream(&self, service_name: &str) -> Option<UpstreamService> {
        let upstreams = self.upstreams.read().await;
        let upstreams = upstreams.get(service_name)?;
        
        if upstreams.is_empty() {
            return None;
        }
        
        // Weighted round-robin algorithm
        let mut total_weight = 0;
        let mut selected: Option<&WeightedUpstream> = None;
        
        for upstream in upstreams {
            let current = upstream.current_weight.fetch_add(
                upstream.effective_weight.load(Ordering::Relaxed),
                Ordering::Relaxed
            );
            total_weight += upstream.effective_weight.load(Ordering::Relaxed);
            
            if selected.is_none() || current > selected.unwrap().current_weight.load(Ordering::Relaxed) {
                selected = Some(upstream);
            }
        }
        
        if let Some(selected_upstream) = selected {
            selected_upstream.current_weight.fetch_sub(total_weight, Ordering::Relaxed);
            Some(selected_upstream.service.clone())
        } else {
            None
        }
    }
    
    async fn record_response(&self, upstream: &UpstreamService, latency: Duration, success: bool) {
        // Adjust effective weight based on response success/failure
        let upstreams = self.upstreams.read().await;
        if let Some(service_upstreams) = upstreams.get(&upstream.service_name) {
            for weighted_upstream in service_upstreams {
                if weighted_upstream.service.address == upstream.address {
                    let current_weight = weighted_upstream.effective_weight.load(Ordering::Relaxed);
                    
                    if success {
                        // Increase weight for successful responses
                        if current_weight < weighted_upstream.weight as usize {
                            weighted_upstream.effective_weight.fetch_add(1, Ordering::Relaxed);
                        }
                    } else {
                        // Decrease weight for failed responses
                        if current_weight > 1 {
                            weighted_upstream.effective_weight.fetch_sub(1, Ordering::Relaxed);
                        }
                    }
                    break;
                }
            }
        }
    }
}

pub struct LeastConnectionsBalancer {
    upstreams: RwLock<HashMap<String, Vec<ConnectionCountingUpstream>>>,
}

struct ConnectionCountingUpstream {
    service: UpstreamService,
    active_connections: AtomicUsize,
}

#[async_trait]
impl LoadBalancer for LeastConnectionsBalancer {
    async fn select_upstream(&self, service_name: &str) -> Option<UpstreamService> {
        let upstreams = self.upstreams.read().await;
        let upstreams = upstreams.get(service_name)?;
        
        // Select upstream with least active connections
        let selected = upstreams.iter()
            .min_by_key(|u| u.active_connections.load(Ordering::Relaxed))?;
        
        selected.active_connections.fetch_add(1, Ordering::Relaxed);
        Some(selected.service.clone())
    }
}
```

#### Circuit Breaker Implementation

```rust
use std::sync::atomic::{AtomicU64, AtomicBool, Ordering};
use std::time::{Duration, Instant};

pub struct CircuitBreaker {
    state: AtomicU8, // 0: Closed, 1: Open, 2: Half-Open
    failure_count: AtomicU64,
    success_count: AtomicU64,
    last_failure_time: AtomicU64,
    config: CircuitBreakerConfig,
}

#[derive(Clone)]
pub struct CircuitBreakerConfig {
    pub failure_threshold: u64,
    pub success_threshold: u64,
    pub timeout: Duration,
    pub recovery_timeout: Duration,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum CircuitBreakerState {
    Closed = 0,
    Open = 1,
    HalfOpen = 2,
}

impl CircuitBreaker {
    pub fn new(config: CircuitBreakerConfig) -> Self {
        Self {
            state: AtomicU8::new(CircuitBreakerState::Closed as u8),
            failure_count: AtomicU64::new(0),
            success_count: AtomicU64::new(0),
            last_failure_time: AtomicU64::new(0),
            config,
        }
    }
    
    pub fn is_open(&self) -> bool {
        let state = self.get_state();
        
        match state {
            CircuitBreakerState::Open => {
                // Check if recovery timeout has passed
                let last_failure = self.last_failure_time.load(Ordering::Relaxed);
                let now = Instant::now().elapsed().as_millis() as u64;
                
                if now - last_failure > self.config.recovery_timeout.as_millis() as u64 {
                    // Transition to half-open
                    self.state.store(CircuitBreakerState::HalfOpen as u8, Ordering::Relaxed);
                    self.success_count.store(0, Ordering::Relaxed);
                    false
                } else {
                    true
                }
            }
            CircuitBreakerState::HalfOpen => false,
            CircuitBreakerState::Closed => false,
        }
    }
    
    pub fn record_success(&self) {
        let state = self.get_state();
        
        match state {
            CircuitBreakerState::Closed => {
                self.failure_count.store(0, Ordering::Relaxed);
            }
            CircuitBreakerState::HalfOpen => {
                let successes = self.success_count.fetch_add(1, Ordering::Relaxed) + 1;
                if successes >= self.config.success_threshold {
                    // Transition to closed
                    self.state.store(CircuitBreakerState::Closed as u8, Ordering::Relaxed);
                    self.failure_count.store(0, Ordering::Relaxed);
                    self.success_count.store(0, Ordering::Relaxed);
                }
            }
            CircuitBreakerState::Open => {
                // Should not happen if is_open() is called first
            }
        }
    }
    
    pub fn record_failure(&self) {
        let failures = self.failure_count.fetch_add(1, Ordering::Relaxed) + 1;
        self.last_failure_time.store(
            Instant::now().elapsed().as_millis() as u64,
            Ordering::Relaxed
        );
        
        let state = self.get_state();
        
        match state {
            CircuitBreakerState::Closed => {
                if failures >= self.config.failure_threshold {
                    // Transition to open
                    self.state.store(CircuitBreakerState::Open as u8, Ordering::Relaxed);
                }
            }
            CircuitBreakerState::HalfOpen => {
                // Transition back to open
                self.state.store(CircuitBreakerState::Open as u8, Ordering::Relaxed);
                self.success_count.store(0, Ordering::Relaxed);
            }
            CircuitBreakerState::Open => {
                // Already open
            }
        }
    }
    
    fn get_state(&self) -> CircuitBreakerState {
        match self.state.load(Ordering::Relaxed) {
            0 => CircuitBreakerState::Closed,
            1 => CircuitBreakerState::Open,
            2 => CircuitBreakerState::HalfOpen,
            _ => CircuitBreakerState::Closed, // Default fallback
        }
    }
}
```

### 5. Python Service Mesh API

```python
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"

@dataclass
class ServiceMeshConfig:
    service_name: str
    service_version: str
    listen_port: int
    
    # Service discovery
    discovery_backend: str = "consul"  # consul, kubernetes, etcd
    discovery_config: Dict[str, Any] = None
    
    # Traffic management
    load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    circuit_breaker_enabled: bool = True
    rate_limiting_enabled: bool = True
    
    # Security
    mtls_enabled: bool = True
    auth_policy: Optional[str] = None
    
    # Observability
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    logging_level: str = "INFO"

class ServiceMesh:
    """CovetPy Service Mesh integration"""
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self._service_registry = {}
        self._circuit_breakers = {}
        self._rate_limiters = {}
        self._load_balancers = {}
    
    async def register_service(self, service_info: Dict[str, Any]) -> None:
        """Register this service with the mesh"""
        registration = {
            "id": f"{self.config.service_name}-{self.config.service_version}",
            "name": self.config.service_name,
            "version": self.config.service_version,
            "address": service_info.get("address", "localhost"),
            "port": self.config.listen_port,
            "tags": service_info.get("tags", []),
            "metadata": service_info.get("metadata", {}),
            "health_check": service_info.get("health_check", f"/health"),
        }
        
        # Register with discovery backend
        await self._register_with_discovery(registration)
    
    async def discover_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Discover instances of a service"""
        return await self._discover_from_backend(service_name)
    
    async def call_service(
        self,
        service_name: str,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make a service-to-service call through the mesh"""
        
        # Service discovery
        instances = await self.discover_service(service_name)
        if not instances:
            raise ServiceUnavailableError(f"No instances found for service: {service_name}")
        
        # Load balancing
        instance = await self._select_instance(service_name, instances)
        
        # Circuit breaker check
        if await self._is_circuit_breaker_open(service_name):
            raise CircuitBreakerOpenError(f"Circuit breaker open for service: {service_name}")
        
        # Rate limiting check
        if not await self._check_rate_limit(service_name):
            raise RateLimitExceededError(f"Rate limit exceeded for service: {service_name}")
        
        # Make the call
        try:
            response = await self._make_http_call(
                instance, method, path, data, headers, timeout
            )
            
            # Record success
            await self._record_success(service_name, instance)
            
            return response
            
        except Exception as e:
            # Record failure
            await self._record_failure(service_name, instance)
            raise
    
    def middleware(self, app):
        """Service mesh middleware for automatic sidecar functionality"""
        
        @app.middleware("service_mesh")
        async def service_mesh_middleware(request, call_next):
            # Extract trace headers
            trace_id = request.headers.get("x-trace-id")
            span_id = request.headers.get("x-span-id")
            
            # Start new span
            with self.tracer.start_span("http_request") as span:
                span.set_tag("service", self.config.service_name)
                span.set_tag("method", request.method)
                span.set_tag("path", request.url.path)
                
                if trace_id:
                    span.set_tag("trace_id", trace_id)
                
                # Add mesh headers
                request.state.mesh_context = {
                    "trace_id": trace_id or generate_trace_id(),
                    "span_id": span.span_id,
                    "service_name": self.config.service_name,
                }
                
                try:
                    # Process request
                    response = await call_next(request)
                    
                    # Add mesh response headers
                    response.headers["x-service-name"] = self.config.service_name
                    response.headers["x-service-version"] = self.config.service_version
                    
                    return response
                    
                except Exception as e:
                    span.set_tag("error", True)
                    span.set_tag("error_message", str(e))
                    raise
        
        return app

# Example usage
from covet import CovetPy
from covet.mesh import ServiceMesh, ServiceMeshConfig

# Configure service mesh
mesh_config = ServiceMeshConfig(
    service_name="user-service",
    service_version="v1.0.0",
    listen_port=8000,
    discovery_backend="consul",
    discovery_config={
        "consul_host": "localhost",
        "consul_port": 8500,
    },
    mtls_enabled=True,
    circuit_breaker_enabled=True,
    rate_limiting_enabled=True,
)

app = CovetPy()
mesh = ServiceMesh(mesh_config)

# Apply service mesh middleware
app = mesh.middleware(app)

# Service endpoints
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    # Call another service through the mesh
    profile = await mesh.call_service(
        "profile-service",
        "GET",
        f"/profiles/{user_id}"
    )
    
    return {
        "user_id": user_id,
        "profile": profile
    }

@app.post("/users")
async def create_user(request):
    user_data = await request.json()
    
    # Create user
    user = await db.create_user(user_data)
    
    # Notify other services
    await mesh.call_service(
        "notification-service",
        "POST",
        "/notifications",
        {
            "type": "user_created",
            "user_id": user.id,
            "email": user.email
        }
    )
    
    return {"user_id": user.id}

# Health check endpoint for service mesh
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": mesh_config.service_name,
        "version": mesh_config.service_version,
        "timestamp": datetime.utcnow().isoformat()
    }

# Startup event to register with mesh
@app.on_startup
async def startup():
    await mesh.register_service({
        "address": "10.0.1.100",
        "tags": ["api", "user-management"],
        "metadata": {
            "version": "v1.0.0",
            "environment": "production"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## Consequences

### Positive
1. **Zero-Code Mesh**: Automatic service mesh capabilities
2. **Performance**: Native performance without sidecar overhead
3. **Integration**: Seamless with existing mesh solutions
4. **Observability**: Built-in metrics, tracing, and logging
5. **Security**: mTLS and policy enforcement by default
6. **Resilience**: Circuit breakers, retries, and timeouts

### Negative
1. **Complexity**: Additional operational complexity
2. **Network Overhead**: Extra network hops for some patterns
3. **Debugging**: Distributed debugging challenges
4. **Configuration**: Complex mesh configuration management

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Service Discovery Failures | Multiple discovery backends, caching |
| Network Partitions | Circuit breakers, graceful degradation |
| Configuration Drift | Centralized config management |
| Performance Overhead | Optimized proxy implementation |

## Implementation Roadmap

### Phase 1: Core Mesh (Weeks 1-2)
- Sidecar proxy implementation
- Basic service discovery
- Load balancing strategies
- Circuit breaker implementation

### Phase 2: Advanced Features (Weeks 3-4)
- mTLS implementation
- Rate limiting
- Traffic splitting
- Policy engine

### Phase 3: Integration (Weeks 5-6)
- Consul/Kubernetes integration
- Istio/Linkerd compatibility
- Observability integration
- Python API development

### Phase 4: Production (Weeks 7-8)
- Performance optimization
- Comprehensive testing
- Documentation
- Deployment tooling

## References

- [Istio Architecture](https://istio.io/latest/docs/ops/deployment/architecture/)
- [Linkerd Architecture](https://linkerd.io/2.11/architecture/)
- [Envoy Proxy](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/arch_overview)
- [Service Mesh Patterns](https://www.nginx.com/blog/what-is-a-service-mesh/)
- [Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)