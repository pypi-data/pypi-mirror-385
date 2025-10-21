# API Endpoint Management Interface

## Overview

The API Endpoint Management Interface provides comprehensive tools for configuring, monitoring, and managing CovetPy routes, middleware, and API configurations. This interface enables developers and administrators to manage the entire API lifecycle through an intuitive web-based interface.

## Interface Architecture

### Main Layout
```
┌─────────────────────────────────────────────────────────────────────────┐
│                        API Management Interface                         │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │   Active    │ │  Response   │ │   Error     │ │     Middleware      │ │
│ │  Routes:    │ │   Time:     │ │   Rate:     │ │    Active: 12       │ │
│ │    247      │ │   12.4ms    │ │   0.02%     │ │  ████████████░░░░   │ │
│ │ ▲ +3 new    │ │ ▼ -2.1ms    │ │ ▼ -0.01%    │ │    Coverage: 85%    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                          Route Explorer                             │ │
│ │ ┌─────────────────┐ ┌─────────────────────────────────────────────┐ │ │
│ │ │   Route Tree    │ │              Route Details              │ │ │
│ │ │                 │ │                                         │ │ │
│ │ │ 📁 /api         │ │ GET /api/v1/users/{id}                  │ │ │
│ │ │ ├── 📁 v1       │ │ ┌─────────────────────────────────────┐ │ │ │
│ │ │ │   ├── 👥 users│ │ │ Handler: getUserById                │ │ │ │
│ │ │ │   │   ├── GET │ │ │ Middleware: [auth, rateLimit]       │ │ │ │
│ │ │ │   │   ├── POST│ │ │ Cache: 5min                         │ │ │ │
│ │ │ │   │   └── PUT │ │ │ Timeout: 30s                        │ │ │ │
│ │ │ │   └── 📊 stats│ │ │                                     │ │ │ │
│ │ │ └── 📁 v2       │ │ │ ┌─ Metrics (Last 24h) ──────────┐  │ │ │ │
│ │ │     └── ...     │ │ │ │ Requests: 1.2M                │  │ │ │ │
│ │ │                 │ │ │ │ Avg Response: 8.3ms           │  │ │ │ │
│ │ │                 │ │ │ │ Error Rate: 0.01%             │  │ │ │ │
│ │ │                 │ │ │ │ P95 Latency: 15.2ms           │  │ │ │ │
│ │ │ [New Route]     │ │ │ └───────────────────────────────┘  │ │ │ │
│ │ └─────────────────┘ │ └─────────────────────────────────────┘ │ │ │
│ │                     │  [Edit] [Test] [Clone] [Delete]      │ │ │
│ │                     └─────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────┐ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Route Management

#### Route Explorer Component
```typescript
interface Route {
  id: string;
  path: string;
  method: HTTPMethod;
  handler: string;
  middleware: string[];
  parameters: RouteParameter[];
  metadata: RouteMetadata;
  metrics: RouteMetrics;
  isActive: boolean;
  lastModified: Date;
}

interface RouteExplorerProps {
  routes: Route[];
  selectedRoute?: Route;
  onRouteSelect: (route: Route) => void;
  onRouteCreate: () => void;
  onRouteEdit: (route: Route) => void;
  onRouteDelete: (routeId: string) => void;
}

const RouteExplorer: React.FC<RouteExplorerProps> = ({
  routes,
  selectedRoute,
  onRouteSelect,
  onRouteCreate,
  onRouteEdit,
  onRouteDelete
}) => {
  const [filteredRoutes, setFilteredRoutes] = useState<Route[]>(routes);
  const [searchTerm, setSearchTerm] = useState('');
  const [methodFilter, setMethodFilter] = useState<HTTPMethod[]>([]);
  
  // Real-time route data from API
  const { data: liveRoutes, loading } = useCovetPyRealTimeData('/api/v1/routes');
  
  useEffect(() => {
    if (liveRoutes) {
      setFilteredRoutes(filterRoutes(liveRoutes, searchTerm, methodFilter));
    }
  }, [liveRoutes, searchTerm, methodFilter]);
  
  return (
    <div className="route-explorer">
      <div className="route-explorer-header">
        <h2>API Routes</h2>
        <div className="route-controls">
          <SearchInput
            placeholder="Search routes..."
            value={searchTerm}
            onChange={setSearchTerm}
          />
          <MethodFilter
            methods={methodFilter}
            onChange={setMethodFilter}
          />
          <button 
            className="btn btn-primary"
            onClick={onRouteCreate}
          >
            <PlusIcon /> New Route
          </button>
        </div>
      </div>
      
      <div className="route-explorer-content">
        <div className="route-tree">
          <RouteTree
            routes={filteredRoutes}
            selectedRoute={selectedRoute}
            onRouteSelect={onRouteSelect}
            loading={loading}
          />
        </div>
        
        <div className="route-details">
          {selectedRoute ? (
            <RouteDetailsPanel
              route={selectedRoute}
              onEdit={() => onRouteEdit(selectedRoute)}
              onDelete={() => onRouteDelete(selectedRoute.id)}
            />
          ) : (
            <EmptyState
              title="Select a Route"
              description="Choose a route from the tree to view details and metrics"
              icon={<RouteIcon />}
            />
          )}
        </div>
      </div>
    </div>
  );
};
```

#### Route Tree Component
```typescript
interface RouteTreeNode {
  path: string;
  children: RouteTreeNode[];
  routes: Route[];
  isExpanded: boolean;
}

const RouteTree: React.FC<{
  routes: Route[];
  selectedRoute?: Route;
  onRouteSelect: (route: Route) => void;
  loading: boolean;
}> = ({ routes, selectedRoute, onRouteSelect, loading }) => {
  const [treeData, setTreeData] = useState<RouteTreeNode[]>([]);
  
  useEffect(() => {
    const tree = buildRouteTree(routes);
    setTreeData(tree);
  }, [routes]);
  
  if (loading) {
    return <RouteTreeSkeleton />;
  }
  
  return (
    <div className="route-tree">
      {treeData.map((node, index) => (
        <RouteTreeNode
          key={index}
          node={node}
          selectedRoute={selectedRoute}
          onRouteSelect={onRouteSelect}
          level={0}
        />
      ))}
    </div>
  );
};

const RouteTreeNode: React.FC<{
  node: RouteTreeNode;
  selectedRoute?: Route;
  onRouteSelect: (route: Route) => void;
  level: number;
}> = ({ node, selectedRoute, onRouteSelect, level }) => {
  const [isExpanded, setIsExpanded] = useState(node.isExpanded);
  
  return (
    <div className="route-tree-node" style={{ paddingLeft: `${level * 20}px` }}>
      <div className="node-header" onClick={() => setIsExpanded(!isExpanded)}>
        <ChevronIcon direction={isExpanded ? 'down' : 'right'} />
        <FolderIcon isOpen={isExpanded} />
        <span className="node-path">{node.path}</span>
        {node.routes.length > 0 && (
          <span className="route-count">{node.routes.length}</span>
        )}
      </div>
      
      {isExpanded && (
        <>
          {node.routes.map((route) => (
            <div
              key={route.id}
              className={`route-item ${selectedRoute?.id === route.id ? 'selected' : ''}`}
              onClick={() => onRouteSelect(route)}
            >
              <MethodBadge method={route.method} />
              <span className="route-path">{route.path}</span>
              <RouteStatusIndicator route={route} />
            </div>
          ))}
          
          {node.children.map((child, index) => (
            <RouteTreeNode
              key={index}
              node={child}
              selectedRoute={selectedRoute}
              onRouteSelect={onRouteSelect}
              level={level + 1}
            />
          ))}
        </>
      )}
    </div>
  );
};
```

### 2. Route Details Panel

#### Route Information
```typescript
const RouteDetailsPanel: React.FC<{
  route: Route;
  onEdit: () => void;
  onDelete: () => void;
}> = ({ route, onEdit, onDelete }) => {
  const { data: routeMetrics } = useCovetPyRealTimeData(
    `/api/v1/routes/${route.id}/metrics`
  );
  const { data: routeHealth } = useCovetPyRealTimeData(
    `/api/v1/routes/${route.id}/health`
  );
  
  return (
    <div className="route-details-panel">
      <div className="route-header">
        <div className="route-title">
          <MethodBadge method={route.method} size="lg" />
          <h3>{route.path}</h3>
          <RouteStatusIndicator route={route} size="lg" />
        </div>
        <div className="route-actions">
          <button className="btn btn-secondary" onClick={onEdit}>
            <EditIcon /> Edit
          </button>
          <button className="btn btn-primary">
            <TestIcon /> Test
          </button>
          <DropdownMenu
            trigger={<button className="btn btn-ghost"><MoreIcon /></button>}
            items={[
              { label: 'Clone Route', onClick: () => {} },
              { label: 'Export Config', onClick: () => {} },
              { label: 'View Logs', onClick: () => {} },
              { label: 'Delete', onClick: onDelete, danger: true }
            ]}
          />
        </div>
      </div>
      
      <div className="route-content">
        <Tabs defaultValue="overview">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="middleware">Middleware</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="testing">Testing</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview">
            <RouteOverviewTab route={route} health={routeHealth} />
          </TabsContent>
          
          <TabsContent value="metrics">
            <RouteMetricsTab route={route} metrics={routeMetrics} />
          </TabsContent>
          
          <TabsContent value="middleware">
            <MiddlewareTab route={route} />
          </TabsContent>
          
          <TabsContent value="security">
            <SecurityTab route={route} />
          </TabsContent>
          
          <TabsContent value="testing">
            <TestingTab route={route} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
```

#### Route Overview Tab
```typescript
const RouteOverviewTab: React.FC<{
  route: Route;
  health: RouteHealth;
}> = ({ route, health }) => {
  return (
    <div className="route-overview-tab">
      <div className="overview-grid">
        <div className="overview-section">
          <h4>Route Configuration</h4>
          <div className="config-grid">
            <div className="config-item">
              <label>Handler Function</label>
              <code className="handler-name">{route.handler}</code>
            </div>
            <div className="config-item">
              <label>Timeout</label>
              <span>{route.metadata.timeout}ms</span>
            </div>
            <div className="config-item">
              <label>Cache TTL</label>
              <span>{route.metadata.cacheTTL || 'None'}</span>
            </div>
            <div className="config-item">
              <label>Rate Limit</label>
              <span>{route.metadata.rateLimit || 'None'}</span>
            </div>
          </div>
        </div>
        
        <div className="overview-section">
          <h4>Request Parameters</h4>
          {route.parameters.length > 0 ? (
            <div className="parameters-list">
              {route.parameters.map((param) => (
                <div key={param.name} className="parameter-item">
                  <div className="param-header">
                    <span className="param-name">{param.name}</span>
                    <ParameterTypeBadge type={param.type} />
                    {param.required && <RequiredBadge />}
                  </div>
                  <div className="param-description">{param.description}</div>
                  {param.validation && (
                    <div className="param-validation">
                      <ValidationRules rules={param.validation} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No Parameters"
              description="This route doesn't accept any parameters"
            />
          )}
        </div>
        
        <div className="overview-section">
          <h4>Health Status</h4>
          <div className="health-grid">
            <HealthMetric
              label="Availability"
              value={health?.availability}
              format="percentage"
              threshold={{ warning: 95, critical: 90 }}
            />
            <HealthMetric
              label="Success Rate"
              value={health?.successRate}
              format="percentage"
              threshold={{ warning: 95, critical: 90 }}
            />
            <HealthMetric
              label="Avg Response Time"
              value={health?.avgResponseTime}
              format="duration"
              threshold={{ warning: 100, critical: 500 }}
            />
            <HealthMetric
              label="Error Rate"
              value={health?.errorRate}
              format="percentage"
              threshold={{ warning: 5, critical: 10 }}
              invertThreshold
            />
          </div>
        </div>
      </div>
    </div>
  );
};
```

### 3. Route Metrics Dashboard

#### Real-Time Metrics
```typescript
const RouteMetricsTab: React.FC<{
  route: Route;
  metrics: RouteMetrics;
}> = ({ route, metrics }) => {
  const [timeRange, setTimeRange] = useState('1h');
  
  return (
    <div className="route-metrics-tab">
      <div className="metrics-controls">
        <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
        <button className="btn btn-secondary">
          <ExportIcon /> Export Metrics
        </button>
      </div>
      
      <div className="metrics-dashboard">
        <div className="metrics-overview">
          <MetricCard
            title="Requests/Second"
            value={metrics?.rps}
            trend={metrics?.rpsTrend}
            sparklineData={metrics?.rpsHistory}
          />
          <MetricCard
            title="Response Time"
            value={metrics?.avgResponseTime}
            unit="ms"
            trend={metrics?.responseTrend}
            sparklineData={metrics?.responseTimeHistory}
          />
          <MetricCard
            title="Error Rate"
            value={metrics?.errorRate}
            format="percentage"
            trend={metrics?.errorTrend}
            sparklineData={metrics?.errorHistory}
          />
          <MetricCard
            title="Throughput"
            value={metrics?.throughput}
            unit="MB/s"
            trend={metrics?.throughputTrend}
            sparklineData={metrics?.throughputHistory}
          />
        </div>
        
        <div className="metrics-charts">
          <div className="chart-container">
            <RoutePerformanceChart
              routeId={route.id}
              timeRange={timeRange}
              metrics={['response_time', 'rps', 'error_rate']}
            />
          </div>
          
          <div className="chart-container">
            <ResponseTimeDistribution
              routeId={route.id}
              timeRange={timeRange}
            />
          </div>
        </div>
        
        <div className="metrics-table">
          <h4>Detailed Metrics</h4>
          <DataTable
            columns={[
              { key: 'timestamp', label: 'Time', format: 'datetime' },
              { key: 'requests', label: 'Requests', format: 'number' },
              { key: 'responseTime', label: 'Avg Response', format: 'duration' },
              { key: 'p95', label: 'P95', format: 'duration' },
              { key: 'p99', label: 'P99', format: 'duration' },
              { key: 'errors', label: 'Errors', format: 'number' },
              { key: 'bytes', label: 'Bytes', format: 'bytes' }
            ]}
            data={metrics?.detailedMetrics || []}
            pagination={{ pageSize: 50 }}
            realTimeUpdates
          />
        </div>
      </div>
    </div>
  );
};
```

### 4. Middleware Management

#### Middleware Configuration
```typescript
interface Middleware {
  id: string;
  name: string;
  type: 'auth' | 'cors' | 'rateLimit' | 'cache' | 'compression' | 'custom';
  order: number;
  enabled: boolean;
  configuration: Record<string, any>;
  appliedToRoutes: string[];
  performance: MiddlewarePerformance;
}

const MiddlewareTab: React.FC<{ route: Route }> = ({ route }) => {
  const { data: routeMiddleware } = useCovetPyRealTimeData(
    `/api/v1/routes/${route.id}/middleware`
  );
  const { data: availableMiddleware } = useCovetPyRealTimeData(
    '/api/v1/middleware/available'
  );
  
  return (
    <div className="middleware-tab">
      <div className="middleware-header">
        <h4>Applied Middleware</h4>
        <button className="btn btn-primary">
          <PlusIcon /> Add Middleware
        </button>
      </div>
      
      <div className="middleware-pipeline">
        <DragDropContext onDragEnd={handleMiddlewareReorder}>
          <Droppable droppableId="middleware-pipeline">
            {(provided) => (
              <div
                {...provided.droppableProps}
                ref={provided.innerRef}
                className="middleware-list"
              >
                {routeMiddleware?.map((middleware, index) => (
                  <Draggable
                    key={middleware.id}
                    draggableId={middleware.id}
                    index={index}
                  >
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        className={`middleware-item ${snapshot.isDragging ? 'dragging' : ''}`}
                      >
                        <div
                          {...provided.dragHandleProps}
                          className="drag-handle"
                        >
                          <DragIcon />
                        </div>
                        
                        <MiddlewareCard
                          middleware={middleware}
                          routeId={route.id}
                        />
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      </div>
      
      <div className="middleware-performance">
        <h4>Middleware Performance Impact</h4>
        <MiddlewarePerformanceChart
          routeId={route.id}
          middleware={routeMiddleware}
        />
      </div>
    </div>
  );
};

const MiddlewareCard: React.FC<{
  middleware: Middleware;
  routeId: string;
}> = ({ middleware, routeId }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="middleware-card">
      <div className="middleware-header">
        <div className="middleware-info">
          <MiddlewareTypeIcon type={middleware.type} />
          <span className="middleware-name">{middleware.name}</span>
          <StatusToggle
            enabled={middleware.enabled}
            onChange={(enabled) => updateMiddleware(middleware.id, { enabled })}
          />
        </div>
        <div className="middleware-actions">
          <PerformanceIndicator performance={middleware.performance} />
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <ChevronIcon direction={isExpanded ? 'up' : 'down'} />
          </button>
          <DropdownMenu
            trigger={<button className="btn btn-ghost btn-sm"><MoreIcon /></button>}
            items={[
              { label: 'Configure', onClick: () => {} },
              { label: 'View Logs', onClick: () => {} },
              { label: 'Remove', onClick: () => {}, danger: true }
            ]}
          />
        </div>
      </div>
      
      {isExpanded && (
        <div className="middleware-details">
          <div className="middleware-config">
            <h5>Configuration</h5>
            <CodeEditor
              value={JSON.stringify(middleware.configuration, null, 2)}
              language="json"
              readOnly
            />
          </div>
          
          <div className="middleware-metrics">
            <h5>Performance Metrics</h5>
            <div className="metrics-grid">
              <div className="metric">
                <label>Processing Time</label>
                <span>{middleware.performance.avgProcessingTime}ms</span>
              </div>
              <div className="metric">
                <label>Success Rate</label>
                <span>{middleware.performance.successRate}%</span>
              </div>
              <div className="metric">
                <label>Cache Hit Rate</label>
                <span>{middleware.performance.cacheHitRate || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

### 5. Route Testing Interface

#### Integrated API Testing
```typescript
const TestingTab: React.FC<{ route: Route }> = ({ route }) => {
  const [testRequest, setTestRequest] = useState<TestRequest>({
    method: route.method,
    path: route.path,
    headers: {},
    body: '',
    parameters: {}
  });
  const [testHistory, setTestHistory] = useState<TestResult[]>([]);
  
  return (
    <div className="testing-tab">
      <div className="testing-interface">
        <div className="request-builder">
          <h4>Request Builder</h4>
          
          <div className="request-line">
            <MethodSelector
              value={testRequest.method}
              onChange={(method) => setTestRequest({ ...testRequest, method })}
              disabled
            />
            <PathInput
              value={testRequest.path}
              onChange={(path) => setTestRequest({ ...testRequest, path })}
              parameters={route.parameters}
            />
            <button
              className="btn btn-primary"
              onClick={() => executeTest(testRequest)}
            >
              Send Request
            </button>
          </div>
          
          <Tabs defaultValue="parameters">
            <TabsList>
              <TabsTrigger value="parameters">Parameters</TabsTrigger>
              <TabsTrigger value="headers">Headers</TabsTrigger>
              <TabsTrigger value="body">Body</TabsTrigger>
              <TabsTrigger value="auth">Auth</TabsTrigger>
            </TabsList>
            
            <TabsContent value="parameters">
              <ParametersEditor
                parameters={route.parameters}
                values={testRequest.parameters}
                onChange={(parameters) => setTestRequest({ ...testRequest, parameters })}
              />
            </TabsContent>
            
            <TabsContent value="headers">
              <HeadersEditor
                headers={testRequest.headers}
                onChange={(headers) => setTestRequest({ ...testRequest, headers })}
              />
            </TabsContent>
            
            <TabsContent value="body">
              <BodyEditor
                body={testRequest.body}
                contentType={testRequest.headers['Content-Type']}
                onChange={(body) => setTestRequest({ ...testRequest, body })}
              />
            </TabsContent>
            
            <TabsContent value="auth">
              <AuthEditor
                auth={testRequest.auth}
                onChange={(auth) => setTestRequest({ ...testRequest, auth })}
              />
            </TabsContent>
          </Tabs>
        </div>
        
        <div className="response-viewer">
          <h4>Response</h4>
          <ResponseViewer lastResponse={testHistory[0]} />
        </div>
      </div>
      
      <div className="test-history">
        <h4>Test History</h4>
        <TestHistoryTable
          tests={testHistory}
          onRerunTest={(test) => executeTest(test.request)}
          onDeleteTest={(testId) => deleteTest(testId)}
        />
      </div>
    </div>
  );
};
```

## Data Integration

### Real-Time API Endpoints
```typescript
// API endpoints for route management - NO MOCK DATA
const ROUTE_API_ENDPOINTS = {
  // Core route operations
  LIST_ROUTES: '/api/v1/routes',
  GET_ROUTE: '/api/v1/routes/:id',
  CREATE_ROUTE: '/api/v1/routes',
  UPDATE_ROUTE: '/api/v1/routes/:id',
  DELETE_ROUTE: '/api/v1/routes/:id',
  
  // Route metrics and monitoring
  ROUTE_METRICS: '/api/v1/routes/:id/metrics',
  ROUTE_HEALTH: '/api/v1/routes/:id/health',
  ROUTE_LOGS: '/api/v1/routes/:id/logs',
  
  // Middleware management
  ROUTE_MIDDLEWARE: '/api/v1/routes/:id/middleware',
  AVAILABLE_MIDDLEWARE: '/api/v1/middleware/available',
  UPDATE_MIDDLEWARE: '/api/v1/routes/:id/middleware/:middlewareId',
  
  // Testing and validation
  TEST_ROUTE: '/api/v1/routes/:id/test',
  VALIDATE_ROUTE: '/api/v1/routes/validate',
  
  // Configuration
  ROUTE_CONFIG: '/api/v1/routes/:id/config',
  BULK_UPDATE: '/api/v1/routes/bulk-update'
} as const;

// WebSocket endpoints for real-time updates
const ROUTE_WEBSOCKET_ENDPOINTS = {
  ROUTE_METRICS: '/ws/routes/:id/metrics',
  ROUTE_HEALTH: '/ws/routes/:id/health',
  ROUTE_EVENTS: '/ws/routes/:id/events',
  ALL_ROUTES: '/ws/routes'
} as const;
```

### Type Definitions
```typescript
interface Route {
  id: string;
  path: string;
  method: HTTPMethod;
  handler: string;
  middleware: string[];
  parameters: RouteParameter[];
  metadata: RouteMetadata;
  metrics: RouteMetrics;
  isActive: boolean;
  createdAt: Date;
  lastModified: Date;
}

interface RouteMetrics {
  rps: number;
  avgResponseTime: number;
  p95ResponseTime: number;
  p99ResponseTime: number;
  errorRate: number;
  throughput: number;
  totalRequests: number;
  totalErrors: number;
}

interface RouteHealth {
  availability: number;
  successRate: number;
  avgResponseTime: number;
  errorRate: number;
  lastError?: Error;
  healthScore: number;
}
```

This API Management Interface provides comprehensive tools for managing CovetPy routes with real-time monitoring, testing capabilities, and middleware management, all connected to live backend APIs for accurate system management.