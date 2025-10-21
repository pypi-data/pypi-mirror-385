# ADR-003: Plugin Architecture Design

## Status
Accepted

## Context

CovetPy needs a robust extensibility mechanism to support diverse enterprise requirements without bloating the core framework. The plugin system must:

1. Enable third-party extensions for protocols, middleware, authentication, etc.
2. Maintain high performance with minimal runtime overhead
3. Provide type safety and compile-time validation
4. Support both Python and Rust plugin development
5. Allow hot-loading/unloading of plugins for zero-downtime updates
6. Ensure security isolation between plugins
7. Provide a rich ecosystem for community contributions

Traditional plugin systems often sacrifice performance for flexibility, while high-performance systems lack extensibility.

## Decision

We will implement a **multi-tier plugin architecture** that combines compile-time optimization with runtime flexibility.

### 1. Plugin Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Plugin Management Layer                   │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │   Plugin    │ │    Plugin    │ │       Plugin       │   │
│  │  Registry   │ │   Loader     │ │     Sandboxing     │   │
│  └─────────────┘ └──────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  Static Plugins │ │Dynamic Plugins│ │  Native Plugins │
│   (Rust Core)   │ │   (Python)    │ │   (Rust FFI)    │
│                 │ │               │ │                 │
│ ┌─────────────┐ │ │┌─────────────┐│ │ ┌─────────────┐ │
│ │  Protocol   │ │ ││ Middleware  ││ │ │   Custom    │ │
│ │  Handlers   │ │ ││   Stack     ││ │ │  Protocols  │ │
│ └─────────────┘ │ │└─────────────┘│ │ └─────────────┘ │
│ ┌─────────────┐ │ │┌─────────────┐│ │ ┌─────────────┐ │
│ │   Auth      │ │ ││   Filters   ││ │ │   Storage   │ │
│ │ Providers   │ │ ││             ││ │ │   Engines   │ │
│ └─────────────┘ │ │└─────────────┘│ │ └─────────────┘ │
└─────────────────┘ └──────────────┘ └─────────────────┘
```

### 2. Plugin Types and Interfaces

#### Core Plugin Traits (Rust)

```rust
use async_trait::async_trait;
use serde::{Deserialize, Serialize};

// Base plugin trait
#[async_trait]
pub trait Plugin: Send + Sync {
    fn name(&self) -> &str;
    fn version(&self) -> &str;
    fn dependencies(&self) -> Vec<String> { vec![] }
    
    async fn initialize(&mut self, ctx: &PluginContext) -> Result<()>;
    async fn shutdown(&mut self) -> Result<()>;
    
    fn metadata(&self) -> PluginMetadata;
}

// Middleware plugin
#[async_trait]
pub trait MiddlewarePlugin: Plugin {
    async fn process_request(
        &self,
        request: &mut Request,
        ctx: &RequestContext,
    ) -> Result<MiddlewareAction>;
    
    async fn process_response(
        &self,
        response: &mut Response,
        ctx: &ResponseContext,
    ) -> Result<()>;
}

// Protocol plugin
#[async_trait]
pub trait ProtocolPlugin: Plugin {
    fn supported_protocols(&self) -> Vec<ProtocolType>;
    
    async fn handle_connection(
        &self,
        stream: TcpStream,
        protocol: ProtocolType,
    ) -> Result<Connection>;
    
    async fn parse_request(&self, data: &[u8]) -> Result<Request>;
    async fn serialize_response(&self, response: &Response) -> Result<Vec<u8>>;
}

// Authentication plugin
#[async_trait]
pub trait AuthPlugin: Plugin {
    async fn authenticate(
        &self,
        credentials: &AuthCredentials,
    ) -> Result<AuthResult>;
    
    async fn authorize(
        &self,
        principal: &Principal,
        resource: &Resource,
        action: &Action,
    ) -> Result<bool>;
}

// Storage plugin
#[async_trait]
pub trait StoragePlugin: Plugin {
    async fn get(&self, key: &str) -> Result<Option<Vec<u8>>>;
    async fn set(&self, key: &str, value: &[u8], ttl: Option<Duration>) -> Result<()>;
    async fn delete(&self, key: &str) -> Result<bool>;
    async fn exists(&self, key: &str) -> Result<bool>;
}
```

#### Python Plugin Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from covet.types import Request, Response, PluginContext

class Plugin(ABC):
    """Base plugin interface for Python plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """Plugin dependencies"""
        return []
    
    async def initialize(self, ctx: PluginContext) -> None:
        """Initialize plugin"""
        pass
    
    async def shutdown(self) -> None:
        """Shutdown plugin"""
        pass

class MiddlewarePlugin(Plugin):
    """Middleware plugin interface"""
    
    @abstractmethod
    async def process_request(
        self, 
        request: Request, 
        call_next: Callable
    ) -> Response:
        """Process incoming request"""
        pass

class AuthPlugin(Plugin):
    """Authentication plugin interface"""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate user"""
        pass
    
    @abstractmethod
    async def authorize(self, user: Dict[str, Any], resource: str, action: str) -> bool:
        """Authorize user action"""
        pass

# Example plugin implementation
class JWTAuthPlugin(AuthPlugin):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    @property
    def name(self) -> str:
        return "jwt_auth"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    async def initialize(self, ctx: PluginContext) -> None:
        self.jwt_handler = ctx.get_service("jwt_handler")
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        token = credentials.get("token")
        if not token:
            return None
        
        try:
            payload = self.jwt_handler.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except Exception:
            return None
    
    async def authorize(self, user: Dict[str, Any], resource: str, action: str) -> bool:
        roles = user.get("roles", [])
        permissions = user.get("permissions", [])
        
        # Check role-based access
        if f"{resource}:{action}" in permissions:
            return True
        
        # Check role permissions
        return any(role in ["admin", "superuser"] for role in roles)
```

### 3. Plugin Registry and Discovery

```rust
use std::collections::HashMap;
use async_trait::async_trait;

pub struct PluginRegistry {
    plugins: HashMap<String, Box<dyn Plugin>>,
    middleware_chain: Vec<Box<dyn MiddlewarePlugin>>,
    protocol_handlers: HashMap<ProtocolType, Box<dyn ProtocolPlugin>>,
    auth_providers: HashMap<String, Box<dyn AuthPlugin>>,
    storage_engines: HashMap<String, Box<dyn StoragePlugin>>,
    dependency_graph: DependencyGraph,
}

impl PluginRegistry {
    pub fn new() -> Self {
        Self {
            plugins: HashMap::new(),
            middleware_chain: Vec::new(),
            protocol_handlers: HashMap::new(),
            auth_providers: HashMap::new(),
            storage_engines: HashMap::new(),
            dependency_graph: DependencyGraph::new(),
        }
    }
    
    pub async fn register_plugin(&mut self, plugin: Box<dyn Plugin>) -> Result<()> {
        let name = plugin.name().to_string();
        let dependencies = plugin.dependencies();
        
        // Validate dependencies
        self.validate_dependencies(&dependencies)?;
        
        // Add to dependency graph
        self.dependency_graph.add_plugin(&name, dependencies);
        
        // Initialize plugin
        let ctx = self.create_plugin_context(&name).await?;
        plugin.initialize(&ctx).await?;
        
        // Register by type
        match plugin.as_any().downcast_ref::<dyn MiddlewarePlugin>() {
            Some(middleware) => {
                self.middleware_chain.push(middleware);
                self.middleware_chain.sort_by_key(|p| p.priority());
            }
            None => {}
        }
        
        self.plugins.insert(name, plugin);
        Ok(())
    }
    
    pub async fn discover_plugins(&mut self, path: &str) -> Result<()> {
        let entries = std::fs::read_dir(path)?;
        
        for entry in entries {
            let entry = entry?;
            let path = entry.path();
            
            if path.extension() == Some(std::ffi::OsStr::new("so")) {
                // Load native plugin
                self.load_native_plugin(&path).await?;
            } else if path.extension() == Some(std::ffi::OsStr::new("py")) {
                // Load Python plugin
                self.load_python_plugin(&path).await?;
            }
        }
        
        Ok(())
    }
    
    async fn load_native_plugin(&mut self, path: &std::path::Path) -> Result<()> {
        unsafe {
            let lib = libloading::Library::new(path)?;
            
            // Get plugin factory function
            let factory: libloading::Symbol<unsafe extern "C" fn() -> *mut dyn Plugin> =
                lib.get(b"create_plugin")?;
            
            let plugin = Box::from_raw(factory());
            self.register_plugin(plugin).await?;
        }
        
        Ok(())
    }
    
    async fn load_python_plugin(&mut self, path: &std::path::Path) -> Result<()> {
        let python_loader = self.get_python_loader();
        let plugin = python_loader.load_plugin(path).await?;
        self.register_plugin(plugin).await?;
        Ok(())
    }
}
```

### 4. Hot Loading and Plugin Management

```rust
use notify::{Watcher, RecommendedWatcher, RecursiveMode, Event};
use tokio::sync::mpsc;

pub struct PluginManager {
    registry: Arc<RwLock<PluginRegistry>>,
    watcher: RecommendedWatcher,
    reload_tx: mpsc::Sender<PluginEvent>,
    config: PluginConfig,
}

impl PluginManager {
    pub async fn new(config: PluginConfig) -> Result<Self> {
        let (reload_tx, mut reload_rx) = mpsc::channel(100);
        let registry = Arc::new(RwLock::new(PluginRegistry::new()));
        
        // Setup file watcher for hot reloading
        let watcher = notify::recommended_watcher({
            let tx = reload_tx.clone();
            move |res: Result<Event, notify::Error>| {
                if let Ok(event) = res {
                    let _ = tx.try_send(PluginEvent::FileChanged(event));
                }
            }
        })?;
        
        let manager = Self {
            registry,
            watcher,
            reload_tx,
            config,
        };
        
        // Start hot reload handler
        tokio::spawn(manager.clone().handle_reload_events(reload_rx));
        
        Ok(manager)
    }
    
    pub async fn load_plugins(&mut self) -> Result<()> {
        let mut registry = self.registry.write().await;
        
        // Discover and load plugins from configured paths
        for path in &self.config.plugin_paths {
            registry.discover_plugins(path).await?;
        }
        
        // Watch directories for changes
        for path in &self.config.plugin_paths {
            self.watcher.watch(path.as_ref(), RecursiveMode::Recursive)?;
        }
        
        Ok(())
    }
    
    async fn handle_reload_events(self, mut reload_rx: mpsc::Receiver<PluginEvent>) {
        while let Some(event) = reload_rx.recv().await {
            match event {
                PluginEvent::FileChanged(file_event) => {
                    if let Err(e) = self.handle_file_change(file_event).await {
                        log::error!("Failed to handle plugin file change: {}", e);
                    }
                }
                PluginEvent::UnloadPlugin(name) => {
                    if let Err(e) = self.unload_plugin(&name).await {
                        log::error!("Failed to unload plugin {}: {}", name, e);
                    }
                }
                PluginEvent::LoadPlugin(path) => {
                    if let Err(e) = self.load_plugin_from_path(&path).await {
                        log::error!("Failed to load plugin from {}: {}", path.display(), e);
                    }
                }
            }
        }
    }
    
    async fn unload_plugin(&self, name: &str) -> Result<()> {
        let mut registry = self.registry.write().await;
        
        if let Some(mut plugin) = registry.plugins.remove(name) {
            // Graceful shutdown
            plugin.shutdown().await?;
            
            // Remove from specialized collections
            registry.middleware_chain.retain(|p| p.name() != name);
            registry.protocol_handlers.retain(|_, p| p.name() != name);
            registry.auth_providers.retain(|_, p| p.name() != name);
            registry.storage_engines.retain(|_, p| p.name() != name);
            
            log::info!("Plugin {} unloaded successfully", name);
        }
        
        Ok(())
    }
    
    pub async fn reload_plugin(&self, name: &str) -> Result<()> {
        // Graceful reload without dropping connections
        let plugin_path = self.find_plugin_path(name).await?;
        
        // Load new version
        let new_plugin = self.load_plugin_from_path(&plugin_path).await?;
        
        // Hot swap
        {
            let mut registry = self.registry.write().await;
            
            // Shutdown old version
            if let Some(mut old_plugin) = registry.plugins.remove(name) {
                old_plugin.shutdown().await?;
            }
            
            // Register new version
            registry.register_plugin(new_plugin).await?;
        }
        
        log::info!("Plugin {} reloaded successfully", name);
        Ok(())
    }
}
```

### 5. Plugin Security and Sandboxing

```rust
use std::collections::HashSet;

pub struct PluginSandbox {
    allowed_syscalls: HashSet<u64>,
    allowed_files: HashSet<String>,
    allowed_networks: HashSet<String>,
    memory_limit: usize,
    cpu_limit: f64,
}

impl PluginSandbox {
    pub fn new(config: SandboxConfig) -> Self {
        Self {
            allowed_syscalls: config.allowed_syscalls,
            allowed_files: config.allowed_files,
            allowed_networks: config.allowed_networks,
            memory_limit: config.memory_limit,
            cpu_limit: config.cpu_limit,
        }
    }
    
    pub async fn execute_in_sandbox<F, R>(&self, plugin_name: &str, f: F) -> Result<R>
    where
        F: FnOnce() -> R + Send + 'static,
        R: Send + 'static,
    {
        // Create isolated execution context
        let sandbox = self.create_sandbox_context(plugin_name)?;
        
        // Execute with resource limits
        let result = tokio::task::spawn_blocking(move || {
            // Apply seccomp filter
            sandbox.apply_seccomp_filter()?;
            
            // Apply resource limits
            sandbox.apply_resource_limits()?;
            
            // Execute plugin code
            Ok(f())
        }).await??;
        
        Ok(result)
    }
    
    fn create_sandbox_context(&self, plugin_name: &str) -> Result<SandboxContext> {
        // Create namespace isolation
        let namespace = Namespace::new(plugin_name)?;
        
        // Setup file system restrictions
        let fs_jail = FilesystemJail::new(&self.allowed_files)?;
        
        // Setup network restrictions
        let net_filter = NetworkFilter::new(&self.allowed_networks)?;
        
        Ok(SandboxContext {
            namespace,
            fs_jail,
            net_filter,
            memory_limit: self.memory_limit,
            cpu_limit: self.cpu_limit,
        })
    }
}

// Plugin security wrapper
pub struct SecurePlugin {
    inner: Box<dyn Plugin>,
    sandbox: PluginSandbox,
    permissions: PluginPermissions,
}

impl SecurePlugin {
    pub fn new(
        plugin: Box<dyn Plugin>,
        sandbox: PluginSandbox,
        permissions: PluginPermissions,
    ) -> Self {
        Self {
            inner: plugin,
            sandbox,
            permissions,
        }
    }
}

#[async_trait]
impl Plugin for SecurePlugin {
    fn name(&self) -> &str {
        self.inner.name()
    }
    
    fn version(&self) -> &str {
        self.inner.version()
    }
    
    async fn initialize(&mut self, ctx: &PluginContext) -> Result<()> {
        // Check initialization permissions
        self.permissions.check_permission(Permission::Initialize)?;
        
        // Execute in sandbox
        let plugin = &mut self.inner;
        self.sandbox.execute_in_sandbox(plugin.name(), move || {
            plugin.initialize(ctx)
        }).await?
    }
}
```

### 6. Plugin Configuration and Management

```python
from covet import CovetPy
from covet.plugins import PluginManager, PluginConfig

# Plugin configuration
plugin_config = PluginConfig(
    # Plugin discovery paths
    plugin_paths=[
        "/opt/covet/plugins",
        "./plugins",
        "~/.covet/plugins"
    ],
    
    # Security settings
    sandbox_enabled=True,
    allowed_syscalls=["read", "write", "socket"],
    memory_limit="100MB",
    cpu_limit=0.8,
    
    # Hot reload settings
    hot_reload=True,
    reload_on_change=True,
    
    # Dependency management
    auto_resolve_dependencies=True,
    allow_circular_dependencies=False,
)

app = CovetPy()

# Initialize plugin manager
plugin_manager = PluginManager(plugin_config)

# Register plugins programmatically
plugin_manager.register(JWTAuthPlugin(secret_key="secret"))
plugin_manager.register(CORSMiddleware(allow_origins=["*"]))
plugin_manager.register(PrometheusMetricsPlugin())

# Load plugins from discovery paths
await plugin_manager.load_plugins()

# Configure plugin chains
app.middleware_stack = plugin_manager.get_middleware_chain()
app.auth_provider = plugin_manager.get_auth_provider("jwt_auth")
app.storage_engine = plugin_manager.get_storage_engine("redis")

# Plugin lifecycle management
@app.on_startup
async def startup():
    await plugin_manager.initialize_all()

@app.on_shutdown
async def shutdown():
    await plugin_manager.shutdown_all()

# Plugin health monitoring
@app.get("/_plugins/health")
async def plugin_health():
    return await plugin_manager.get_health_status()

# Plugin management endpoints
@app.post("/_plugins/{plugin_name}/reload")
async def reload_plugin(plugin_name: str):
    await plugin_manager.reload_plugin(plugin_name)
    return {"status": "reloaded"}

@app.get("/_plugins")
async def list_plugins():
    return plugin_manager.list_plugins()
```

## Consequences

### Positive
1. **Extensibility**: Rich ecosystem of third-party plugins
2. **Performance**: Compile-time optimization for static plugins
3. **Flexibility**: Runtime loading/unloading for dynamic updates
4. **Security**: Sandboxed execution prevents malicious plugins
5. **Type Safety**: Compile-time validation for Rust plugins
6. **Hot Reload**: Zero-downtime plugin updates

### Negative
1. **Complexity**: Multiple plugin types and loading mechanisms
2. **Security Overhead**: Sandboxing adds runtime cost
3. **Dependency Management**: Complex dependency resolution
4. **Debugging**: Harder to debug across plugin boundaries

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Plugin Crashes | Isolation, graceful error handling |
| Security Vulnerabilities | Sandboxing, permission system |
| Performance Degradation | Profiling, resource limits |
| Dependency Conflicts | Version management, isolation |

## Implementation Roadmap

### Phase 1: Core Infrastructure (Weeks 1-2)
- Plugin trait definitions
- Basic registry implementation
- Python plugin interface
- Security framework

### Phase 2: Advanced Features (Weeks 3-4)
- Hot loading/unloading
- Dependency management
- Sandboxing implementation
- Configuration system

### Phase 3: Ecosystem (Weeks 5-6)
- Built-in plugin collection
- Documentation and examples
- Testing framework
- Performance optimization

### Phase 4: Tooling (Weeks 7-8)
- Plugin CLI tools
- Development SDK
- Marketplace integration
- Monitoring dashboard

## References

- [WebAssembly Component Model](https://github.com/WebAssembly/component-model)
- [Rust Plugin Systems](https://nullderef.com/blog/plugin-tech/)
- [Seccomp Sandboxing](https://www.kernel.org/doc/Documentation/prctl/seccomp_filter.txt)
- [Python Import System](https://docs.python.org/3/reference/import.html)
- [Dynamic Library Loading](https://doc.rust-lang.org/std/ptr/fn.read.html)