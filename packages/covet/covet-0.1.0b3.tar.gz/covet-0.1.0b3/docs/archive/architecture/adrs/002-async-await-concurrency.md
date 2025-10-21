# ADR-002: Async/Await and Concurrency Model

## Status
Accepted

## Context

CovetPy must handle massive concurrency (>100K simultaneous connections) while maintaining low latency and high throughput. The framework needs a concurrency model that:

1. Scales efficiently with increasing load
2. Provides intuitive async/await patterns for Python developers
3. Minimizes context switching overhead
4. Integrates seamlessly with existing Python async libraries
5. Overcomes Python GIL limitations for I/O-bound operations

Traditional threading models don't scale to the required connection counts, and pure Python async frameworks are limited by single-threaded execution and GIL constraints.

## Decision

We will implement a **hybrid multi-threaded async architecture** that combines Rust's high-performance async runtime with Python's async/await syntax.

### 1. Concurrency Architecture

```
┌────────────────────────────────────────────────────────────--┐
│                     Main Process                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Accept Thread (Rust)                      │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │           Connection Acceptor                   │   │  │
│  │  │         (io_uring based)                        │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                               │
│              ┌───────────────┼───────────────┐               │
│              ▼               ▼               ▼               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │  Worker Thread  │ │  Worker Thread  │ │  Worker Thread  │ │
│  │    (Rust)       │ │    (Rust)       │ │    (Rust)       │ │
│  │                 │ │                 │ │                 │ │
│  │ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │ │
│  │ │ Tokio       │ │ │ │ Tokio       │ │ │ │ Tokio       │ │ │
│  │ │ Runtime     │ │ │ │ Runtime     │ │ │ │ Runtime     │ │ │
│  │ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │ │
│  │                 │ │                 │ │                 │ │
│  │ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │ │
│  │ │ Python      │ │ │ │ Python      │ │ │ │ Python      │ │ │
│  │ │ Executor    │ │ │ │ Executor    │ │ │ │ Executor    │ │ │
│  │ │ Pool        │ │ │ │ Pool        │ │ │ │ Pool        │ │ │
│  │ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2. Thread Model

#### Accept Thread (Single)
```rust
// High-performance connection acceptor
pub struct ConnectionAcceptor {
    listener: TcpListener,
    ring: IoUring,
    workers: Vec<WorkerSender>,
    load_balancer: LoadBalancer,
}

impl ConnectionAcceptor {
    pub async fn run(&mut self) -> Result<()> {
        loop {
            // Accept multiple connections in batch
            let connections = self.accept_batch().await?;
            
            // Distribute to workers using least-loaded strategy
            for conn in connections {
                let worker = self.load_balancer.select_worker();
                worker.send(conn).await?;
            }
        }
    }
}
```

#### Worker Threads (N = CPU cores)
```rust
pub struct WorkerThread {
    id: usize,
    runtime: Runtime,
    python_pool: PythonExecutorPool,
    connection_pool: ConnectionPool,
    message_queue: LockFreeQueue<Task>,
}

impl WorkerThread {
    pub async fn run(&mut self) -> Result<()> {
        // CPU affinity for cache efficiency
        set_cpu_affinity(self.id)?;
        
        loop {
            tokio::select! {
                // Handle new connections
                conn = self.receive_connection() => {
                    self.handle_connection(conn?).await?;
                }
                
                // Process existing connections
                _ = self.process_connections() => {}
                
                // Execute Python handlers
                task = self.message_queue.pop() => {
                    if let Some(task) = task {
                        self.execute_python_handler(task).await?;
                    }
                }
            }
        }
    }
}
```

### 3. Python Async Integration

#### Seamless Async/Await Support
```python
from covet import CovetPy, Request, Response
import asyncio
import aiohttp
import asyncpg

app = CovetPy()

# Native async support
@app.get("/users/{user_id}")
async def get_user(request: Request) -> Response:
    user_id = request.path_params["user_id"]
    
    # Async database query
    async with app.db.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )
    
    # Async HTTP client
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://api.example.com/user/{user_id}") as resp:
            external_data = await resp.json()
    
    return Response({
        "user": dict(user),
        "external_data": external_data
    })

# Background task support
@app.post("/process")
async def process_data(request: Request, background_tasks):
    data = await request.json()
    
    # Add background task
    background_tasks.add_task(heavy_computation, data)
    
    return Response({"status": "processing"})

async def heavy_computation(data):
    # CPU-intensive work runs in thread pool
    result = await app.run_in_executor(cpu_intensive_task, data)
    await save_result(result)
```

#### Python Executor Pool
```rust
use pyo3::prelude::*;
use tokio::sync::mpsc;

pub struct PythonExecutorPool {
    interpreters: Vec<PyInterpreter>,
    task_queue: mpsc::Receiver<PythonTask>,
    result_sender: mpsc::Sender<TaskResult>,
}

impl PythonExecutorPool {
    pub async fn execute_handler(&mut self, task: PythonTask) -> Result<Response> {
        // Select least busy interpreter
        let interpreter = self.select_interpreter();
        
        // Execute Python handler
        let result = tokio::task::spawn_blocking(move || {
            Python::with_gil(|py| {
                let handler = task.handler;
                let request = task.request.into_py(py);
                
                // Call Python async function
                let coroutine = handler.call1(py, (request,))?;
                
                // Run until complete
                let runtime = py.import("asyncio")?;
                let result = runtime
                    .getattr("run")?
                    .call1((coroutine,))?;
                
                Ok(result)
            })
        }).await??;
        
        Ok(result.extract()?)
    }
}
```

### 4. Load Balancing Strategy

```rust
pub enum LoadBalancingStrategy {
    RoundRobin,
    LeastConnections,
    LeastLatency,
    CpuAware,
}

pub struct LoadBalancer {
    strategy: LoadBalancingStrategy,
    workers: Vec<WorkerStats>,
    current_index: AtomicUsize,
}

impl LoadBalancer {
    pub fn select_worker(&self) -> usize {
        match self.strategy {
            LoadBalancingStrategy::RoundRobin => {
                self.current_index.fetch_add(1, Ordering::Relaxed) % self.workers.len()
            }
            
            LoadBalancingStrategy::LeastConnections => {
                self.workers.iter()
                    .enumerate()
                    .min_by_key(|(_, stats)| stats.active_connections.load(Ordering::Relaxed))
                    .map(|(idx, _)| idx)
                    .unwrap_or(0)
            }
            
            LoadBalancingStrategy::LeastLatency => {
                self.workers.iter()
                    .enumerate()
                    .min_by_key(|(_, stats)| stats.avg_latency.load(Ordering::Relaxed))
                    .map(|(idx, _)| idx)
                    .unwrap_or(0)
            }
            
            LoadBalancingStrategy::CpuAware => {
                // Select worker based on CPU usage
                self.select_least_cpu_worker()
            }
        }
    }
}
```

### 5. Async Context Management

```python
# Application lifecycle management
@app.on_startup
async def startup():
    # Initialize database pool
    app.db = await asyncpg.create_pool(DATABASE_URL)
    
    # Initialize Redis connection
    app.redis = await aioredis.from_url(REDIS_URL)
    
    # Initialize HTTP client session
    app.http_client = aiohttp.ClientSession()

@app.on_shutdown
async def shutdown():
    # Graceful shutdown
    await app.db.close()
    await app.redis.close()
    await app.http_client.close()

# Request context
@app.middleware("request_context")
async def request_context_middleware(request: Request, call_next):
    # Set request ID for tracing
    request.state.request_id = generate_request_id()
    
    # Set correlation context
    with correlation_context(request.state.request_id):
        response = await call_next(request)
    
    return response
```

### 6. Backpressure and Flow Control

```rust
pub struct BackpressureController {
    max_queue_size: usize,
    current_queue_size: AtomicUsize,
    admission_controller: AdmissionController,
}

impl BackpressureController {
    pub fn should_accept_request(&self) -> bool {
        let current_size = self.current_queue_size.load(Ordering::Relaxed);
        
        if current_size >= self.max_queue_size {
            // Queue is full, apply admission control
            self.admission_controller.should_admit()
        } else {
            true
        }
    }
    
    pub async fn wait_for_capacity(&self) {
        while self.current_queue_size.load(Ordering::Relaxed) >= self.max_queue_size {
            tokio::time::sleep(Duration::from_micros(100)).await;
        }
    }
}
```

## Consequences

### Positive
1. **High Concurrency**: Handle 100K+ simultaneous connections
2. **Low Latency**: Sub-millisecond response times for simple operations
3. **Familiar API**: Standard Python async/await patterns
4. **Efficiency**: CPU-optimal thread-per-core model
5. **Scalability**: Linear performance scaling with CPU cores
6. **Integration**: Seamless with existing Python async libraries

### Negative
1. **Complexity**: Multi-threaded debugging challenges
2. **Memory Usage**: Multiple Python interpreters increase overhead
3. **Startup Time**: Interpreter initialization delay
4. **GIL Impact**: Python code still limited by GIL per interpreter

### Risk Mitigation

| Risk | Mitigation Strategy |
|------|-------------------|
| Thread Deadlocks | Lock-free data structures, careful ordering |
| Memory Leaks | RAII patterns, comprehensive testing |
| GIL Contention | Minimize Python execution time, use thread pools |
| Context Switching | CPU affinity, work stealing optimization |

## Performance Characteristics

### Benchmark Results (Projected)

| Metric | Target | Comparison |
|--------|--------|------------|
| Concurrent Connections | 100K+ | FastAPI: ~1K |
| Requests/Second | 1M+ | FastAPI: ~25K |
| Latency P99 | <1ms | FastAPI: ~5ms |
| Memory per Connection | <10KB | FastAPI: ~50KB |
| CPU Efficiency | >90% | FastAPI: ~60% |

### Scalability Model

```
Connections = Workers × Connections_per_Worker
Throughput = Workers × Worker_Throughput
Latency = Base_Latency + Queue_Delay + GIL_Delay

Where:
- Workers = CPU_Cores (typically)
- Connections_per_Worker = 10K-50K (depending on workload)
- Worker_Throughput = 100K-500K RPS (depending on handler complexity)
```

## Implementation Details

### Configuration

```python
from covet import CovetPy, ConcurrencyConfig

config = ConcurrencyConfig(
    # Worker configuration
    workers="auto",  # or specific number
    worker_connections=25000,
    
    # Load balancing
    load_balancing="least_connections",
    
    # Backpressure
    max_queue_size=10000,
    queue_timeout=5.0,
    
    # Python executor
    python_interpreters_per_worker=4,
    max_blocking_threads=100,
    
    # Performance tuning
    cpu_affinity=True,
    numa_aware=True,
)

app = CovetPy(concurrency=config)
```

### Monitoring and Observability

```python
@app.middleware("metrics")
async def metrics_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    worker_id = get_current_worker_id()
    
    # Track active requests
    active_requests_gauge.labels(worker=worker_id).inc()
    
    try:
        response = await call_next(request)
        
        # Record success metrics
        request_duration_histogram.labels(
            worker=worker_id,
            status="success"
        ).observe(time.perf_counter() - start_time)
        
        return response
        
    except Exception as e:
        # Record error metrics
        error_counter.labels(
            worker=worker_id,
            error_type=type(e).__name__
        ).inc()
        raise
        
    finally:
        active_requests_gauge.labels(worker=worker_id).dec()
```

## Testing Strategy

### Load Testing
```python
# Simulated load test
async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Create 100K concurrent requests
        for i in range(100_000):
            task = session.get(f"http://localhost:8000/api/users/{i}")
            tasks.append(task)
        
        # Execute all requests
        responses = await asyncio.gather(*tasks)
        
        # Verify all responses
        assert all(r.status == 200 for r in responses)
```

### Concurrency Testing
```rust
#[tokio::test]
async fn test_concurrent_connections() {
    let app = create_test_app();
    let mut handles = vec![];
    
    // Spawn 10K concurrent connections
    for _ in 0..10_000 {
        let handle = tokio::spawn(async {
            let client = TestClient::new();
            client.get("/health").await
        });
        handles.push(handle);
    }
    
    // Wait for all to complete
    let results = futures::future::join_all(handles).await;
    
    // Verify all succeeded
    assert!(results.iter().all(|r| r.is_ok()));
}
```

## Migration Guide

### From Traditional Async Frameworks

```python
# FastAPI style (before)
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

# CovetPy style (after)
from covet import CovetPy, Request
app = CovetPy()

@app.get("/users/{user_id}")
async def get_user(request: Request) -> dict:
    user_id = request.path_params["user_id"]
    return {"user_id": int(user_id)}
```

## Future Enhancements

1. **Work Stealing**: Implement work-stealing between workers
2. **Dynamic Scaling**: Auto-scale workers based on load
3. **NUMA Optimization**: NUMA-aware memory allocation
4. **Green Threads**: Explore user-space threading for Python
5. **Async Generators**: Support for streaming responses

## References

- [Tokio Runtime Documentation](https://docs.rs/tokio/latest/tokio/runtime/)
- [Python Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [io_uring and async I/O](https://lwn.net/Articles/810414/)
- [The C10K Problem](http://www.kegel.com/c10k.html)
- [Lock-free Programming](https://preshing.com/20120612/an-introduction-to-lock-free-programming/)