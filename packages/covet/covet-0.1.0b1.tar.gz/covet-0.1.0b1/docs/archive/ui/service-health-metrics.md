# Service Health and Metrics Visualization

## Overview

The Service Health and Metrics Visualization provides comprehensive monitoring and visualization of CovetPy's distributed services, components, and infrastructure health. This system offers real-time insights into service performance, dependency relationships, and system-wide health indicators.

## Architecture Overview

### Health Monitoring Dashboard Layout
```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Service Health Dashboard                          │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │   System    │ │  Critical   │ │   Active    │ │    Service Map      │ │
│ │   Health    │ │   Alerts    │ │  Services   │ │   🟢 Core: 4/4      │ │
│ │    98.7%    │ │      3      │ │     47      │ │   🟡 Support: 2/3   │ │
│ │ 🟢 Healthy  │ │ 🔴 Action   │ │ 🟢 Online   │ │   🔴 External: 1/4  │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                      Service Topology Map                          │ │
│ │                                                                     │ │
│ │     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │ │
│ │     │   Gateway   │────▶│  Core API   │────▶│  Database   │       │ │
│ │     │  🟢 Healthy │     │ 🟢 Healthy  │     │ 🟢 Healthy  │       │ │
│ │     │   2.1ms     │     │    8.3ms    │     │    1.2ms    │       │ │
│ │     └─────────────┘     └─────────────┘     └─────────────┘       │ │
│ │            │                    │                    │             │ │
│ │            ▼                    ▼                    ▼             │ │
│ │     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │ │
│ │     │   Auth      │     │   Cache     │     │   Storage   │       │ │
│ │     │ 🟡 Warning  │     │ 🟢 Healthy  │     │ 🟢 Healthy  │       │ │
│ │     │   125ms     │     │    0.8ms    │     │    15ms     │       │ │
│ │     └─────────────┘     └─────────────┘     └─────────────┘       │ │
│ │                                                                     │ │
│ │ [Real-time] [Last 15min] [Zoom In] [Export]                        │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │         Service Status          │ │        Health Trends            │ │
│ │                                 │ │                                 │ │
│ │ 🟢 covet-core     99.8%      │ │ ▲ Health Score                  │ │
│ │ 🟢 covet-gateway  99.9%      │ │ │ 100% ┤                        │ │
│ │ 🟡 covet-auth     97.2%      │ │ │  95% ┤     ████████████       │ │
│ │ 🟢 covet-cache    99.5%      │ │ │  90% ┤  ███████████████       │ │
│ │ 🟢 covet-db       99.7%      │ │ │  85% ┤ ████████████████       │ │
│ │ 🔴 external-api      89.1%      │ │ │  80% └────────────────────→   │ │
│ │                                 │ │        1h   6h   24h   7d      │ │
│ │ [View Details] [Health Report]  │ │                                 │ │
│ └─────────────────────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. System Health Overview

#### Health Score Component
```typescript
interface SystemHealthProps {
  services: ServiceHealth[];
  overallHealth: number;
  criticalAlerts: Alert[];
  trends: HealthTrend[];
}

const SystemHealthOverview: React.FC = () => {
  const { data: healthData, loading } = useCovetPyRealTimeData('/api/v1/health/system');
  const { data: alertsData } = useCovetPyRealTimeData('/api/v1/alerts/critical');
  
  const healthScore = useMemo(() => {
    if (!healthData?.services) return 0;
    const totalScore = healthData.services.reduce((sum, service) => sum + service.healthScore, 0);
    return totalScore / healthData.services.length;
  }, [healthData]);
  
  const healthStatus = getHealthStatus(healthScore);
  
  return (
    <div className="system-health-overview">
      <div className="health-grid">
        <HealthScoreCard
          score={healthScore}
          status={healthStatus}
          trend={healthData?.trend}
          loading={loading}
        />
        
        <CriticalAlertsCard
          alerts={alertsData?.alerts || []}
          totalCount={alertsData?.totalCount || 0}
        />
        
        <ActiveServicesCard
          total={healthData?.services?.length || 0}
          healthy={healthData?.services?.filter(s => s.status === 'healthy').length || 0}
          warning={healthData?.services?.filter(s => s.status === 'warning').length || 0}
          critical={healthData?.services?.filter(s => s.status === 'critical').length || 0}
        />
        
        <ServiceMapSummary
          services={healthData?.services || []}
        />
      </div>
    </div>
  );
};

const HealthScoreCard: React.FC<{
  score: number;
  status: HealthStatus;
  trend: HealthTrend;
  loading: boolean;
}> = ({ score, status, trend, loading }) => {
  if (loading) {
    return <HealthScoreCardSkeleton />;
  }
  
  return (
    <div className={`health-score-card status-${status}`}>
      <div className="score-header">
        <h3>System Health</h3>
        <StatusIndicator status={status} size="lg" animated />
      </div>
      
      <div className="score-display">
        <CircularProgress
          value={score}
          size="xl"
          color={getHealthColor(status)}
          strokeWidth={8}
        />
        <div className="score-value">
          <span className="percentage">{score.toFixed(1)}%</span>
          <span className="status-label">{status}</span>
        </div>
      </div>
      
      <div className="score-trend">
        <TrendIndicator
          value={trend?.change}
          period={trend?.period}
          format="percentage"
        />
        <span className="trend-text">vs {trend?.period}</span>
      </div>
    </div>
  );
};
```

### 2. Service Topology Map

#### Interactive Service Map
```typescript
interface ServiceNode {
  id: string;
  name: string;
  type: 'core' | 'support' | 'external';
  status: HealthStatus;
  metrics: ServiceMetrics;
  position: { x: number; y: number };
  dependencies: string[];
}

interface ServiceConnection {
  from: string;
  to: string;
  status: 'healthy' | 'degraded' | 'failed';
  latency: number;
  throughput: number;
}

const ServiceTopologyMap: React.FC = () => {
  const { data: topologyData } = useCovetPyRealTimeData('/api/v1/topology');
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  
  // Real-time updates for service status
  useEffect(() => {
    const ws = new WebSocket('wss://api.covet.local/ws/topology');
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      handleServiceUpdate(update);
    };
    
    return () => ws.close();
  }, []);
  
  return (
    <div className="service-topology-map">
      <div className="topology-controls">
        <h3>Service Topology</h3>
        <div className="control-group">
          <ZoomControls
            zoomLevel={zoomLevel}
            onZoomIn={() => setZoomLevel(Math.min(zoomLevel * 1.2, 3))}
            onZoomOut={() => setZoomLevel(Math.max(zoomLevel / 1.2, 0.3))}
            onReset={() => setZoomLevel(1)}
          />
          <ViewModeSelector />
          <RefreshToggle />
        </div>
      </div>
      
      <div className="topology-canvas" style={{ transform: `scale(${zoomLevel})` }}>
        <ServiceGraph
          nodes={topologyData?.nodes || []}
          connections={topologyData?.connections || []}
          selectedService={selectedService}
          onServiceSelect={setSelectedService}
        />
      </div>
      
      {selectedService && (
        <ServiceDetailsPanel
          serviceId={selectedService}
          onClose={() => setSelectedService(null)}
        />
      )}
    </div>
  );
};

const ServiceGraph: React.FC<{
  nodes: ServiceNode[];
  connections: ServiceConnection[];
  selectedService: string | null;
  onServiceSelect: (serviceId: string) => void;
}> = ({ nodes, connections, selectedService, onServiceSelect }) => {
  return (
    <svg className="service-graph" width="100%" height="400">
      {/* Render connections first (background) */}
      {connections.map((connection) => {
        const fromNode = nodes.find(n => n.id === connection.from);
        const toNode = nodes.find(n => n.id === connection.to);
        
        if (!fromNode || !toNode) return null;
        
        return (
          <ServiceConnection
            key={`${connection.from}-${connection.to}`}
            from={fromNode.position}
            to={toNode.position}
            status={connection.status}
            latency={connection.latency}
            throughput={connection.throughput}
          />
        );
      })}
      
      {/* Render nodes on top */}
      {nodes.map((node) => (
        <ServiceNode
          key={node.id}
          node={node}
          selected={selectedService === node.id}
          onClick={() => onServiceSelect(node.id)}
        />
      ))}
    </svg>
  );
};

const ServiceNode: React.FC<{
  node: ServiceNode;
  selected: boolean;
  onClick: () => void;
}> = ({ node, selected, onClick }) => {
  const statusColor = getStatusColor(node.status);
  const nodeRadius = 40;
  
  return (
    <g
      className={`service-node ${selected ? 'selected' : ''}`}
      transform={`translate(${node.position.x}, ${node.position.y})`}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Service circle */}
      <circle
        cx={0}
        cy={0}
        r={nodeRadius}
        fill={statusColor}
        stroke={selected ? '#1565C0' : '#E0E0E0'}
        strokeWidth={selected ? 3 : 1}
        className="service-circle"
      />
      
      {/* Service icon */}
      <ServiceIcon
        type={node.type}
        x={-12}
        y={-12}
        width={24}
        height={24}
      />
      
      {/* Service name */}
      <text
        x={0}
        y={nodeRadius + 20}
        textAnchor="middle"
        className="service-name"
        fontSize="12"
        fill="#666"
      >
        {node.name}
      </text>
      
      {/* Status indicator */}
      <circle
        cx={nodeRadius - 8}
        cy={-nodeRadius + 8}
        r={6}
        fill={statusColor}
        stroke="white"
        strokeWidth={2}
        className="status-indicator"
      />
      
      {/* Performance metrics tooltip */}
      <title>
        {`${node.name}\nStatus: ${node.status}\nLatency: ${node.metrics.avgLatency}ms\nCPU: ${node.metrics.cpuUsage}%\nMemory: ${node.metrics.memoryUsage}%`}
      </title>
    </g>
  );
};

const ServiceConnection: React.FC<{
  from: { x: number; y: number };
  to: { x: number; y: number };
  status: 'healthy' | 'degraded' | 'failed';
  latency: number;
  throughput: number;
}> = ({ from, to, status, latency, throughput }) => {
  const strokeColor = {
    healthy: '#4CAF50',
    degraded: '#FF9800',
    failed: '#F44336'
  }[status];
  
  const strokeWidth = Math.max(1, Math.min(throughput / 1000, 5));
  
  return (
    <g className="service-connection">
      <line
        x1={from.x}
        y1={from.y}
        x2={to.x}
        y2={to.y}
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeDasharray={status === 'degraded' ? '5,5' : status === 'failed' ? '2,2' : 'none'}
        markerEnd="url(#arrowhead)"
      />
      
      {/* Connection metrics */}
      <text
        x={(from.x + to.x) / 2}
        y={(from.y + to.y) / 2 - 10}
        textAnchor="middle"
        fontSize="10"
        fill="#666"
        className="connection-metric"
      >
        {latency}ms
      </text>
      
      {/* Arrow marker definition */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill={strokeColor}
          />
        </marker>
      </defs>
    </g>
  );
};
```

### 3. Service Health Table

#### Comprehensive Service Listing
```typescript
interface ServiceHealthTableProps {
  services: ServiceHealth[];
  onServiceSelect: (service: ServiceHealth) => void;
  onBulkAction: (action: string, serviceIds: string[]) => void;
}

const ServiceHealthTable: React.FC<ServiceHealthTableProps> = ({
  services,
  onServiceSelect,
  onBulkAction
}) => {
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'healthScore', direction: 'desc' });
  const [filterConfig, setFilterConfig] = useState<FilterConfig>({
    status: 'all',
    type: 'all',
    healthThreshold: 0
  });
  
  const filteredAndSortedServices = useMemo(() => {
    let filtered = services.filter(service => {
      if (filterConfig.status !== 'all' && service.status !== filterConfig.status) return false;
      if (filterConfig.type !== 'all' && service.type !== filterConfig.type) return false;
      if (service.healthScore < filterConfig.healthThreshold) return false;
      return true;
    });
    
    return filtered.sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      const multiplier = sortConfig.direction === 'asc' ? 1 : -1;
      return (aValue > bValue ? 1 : -1) * multiplier;
    });
  }, [services, sortConfig, filterConfig]);
  
  return (
    <div className="service-health-table">
      <div className="table-header">
        <h3>Service Health Status</h3>
        <div className="table-controls">
          <ServiceFilter
            config={filterConfig}
            onChange={setFilterConfig}
          />
          {selectedServices.length > 0 && (
            <BulkActionMenu
              selectedCount={selectedServices.length}
              onAction={(action) => onBulkAction(action, selectedServices)}
            />
          )}
          <button className="btn btn-secondary">
            <ExportIcon /> Export Report
          </button>
        </div>
      </div>
      
      <div className="table-container">
        <table className="service-table">
          <thead>
            <tr>
              <th>
                <Checkbox
                  checked={selectedServices.length === services.length}
                  indeterminate={selectedServices.length > 0 && selectedServices.length < services.length}
                  onChange={(checked) => setSelectedServices(checked ? services.map(s => s.id) : [])}
                />
              </th>
              <th>
                <SortableHeader
                  label="Service"
                  sortKey="name"
                  sortConfig={sortConfig}
                  onSort={setSortConfig}
                />
              </th>
              <th>
                <SortableHeader
                  label="Status"
                  sortKey="status"
                  sortConfig={sortConfig}
                  onSort={setSortConfig}
                />
              </th>
              <th>
                <SortableHeader
                  label="Health Score"
                  sortKey="healthScore"
                  sortConfig={sortConfig}
                  onSort={setSortConfig}
                />
              </th>
              <th>
                <SortableHeader
                  label="Uptime"
                  sortKey="uptime"
                  sortConfig={sortConfig}
                  onSort={setSortConfig}
                />
              </th>
              <th>Response Time</th>
              <th>CPU Usage</th>
              <th>Memory Usage</th>
              <th>Last Check</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedServices.map((service) => (
              <ServiceTableRow
                key={service.id}
                service={service}
                selected={selectedServices.includes(service.id)}
                onSelect={(selected) => {
                  if (selected) {
                    setSelectedServices([...selectedServices, service.id]);
                  } else {
                    setSelectedServices(selectedServices.filter(id => id !== service.id));
                  }
                }}
                onClick={() => onServiceSelect(service)}
              />
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="table-footer">
        <TablePagination
          total={filteredAndSortedServices.length}
          pageSize={50}
          currentPage={1}
          onPageChange={() => {}}
        />
      </div>
    </div>
  );
};

const ServiceTableRow: React.FC<{
  service: ServiceHealth;
  selected: boolean;
  onSelect: (selected: boolean) => void;
  onClick: () => void;
}> = ({ service, selected, onSelect, onClick }) => {
  return (
    <tr
      className={`service-row status-${service.status} ${selected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <td onClick={(e) => e.stopPropagation()}>
        <Checkbox
          checked={selected}
          onChange={onSelect}
        />
      </td>
      <td>
        <div className="service-info">
          <ServiceIcon type={service.type} size="sm" />
          <div className="service-details">
            <span className="service-name">{service.name}</span>
            <span className="service-id">{service.id}</span>
          </div>
        </div>
      </td>
      <td>
        <StatusBadge status={service.status} />
      </td>
      <td>
        <HealthScoreDisplay
          score={service.healthScore}
          trend={service.trend}
        />
      </td>
      <td>
        <UptimeDisplay
          uptime={service.uptime}
          availability={service.availability}
        />
      </td>
      <td>
        <MetricDisplay
          value={service.metrics.avgResponseTime}
          unit="ms"
          threshold={{ warning: 100, critical: 500 }}
        />
      </td>
      <td>
        <ProgressBar
          value={service.metrics.cpuUsage}
          color={getUsageColor(service.metrics.cpuUsage)}
          showLabel
        />
      </td>
      <td>
        <ProgressBar
          value={service.metrics.memoryUsage}
          color={getUsageColor(service.metrics.memoryUsage)}
          showLabel
        />
      </td>
      <td>
        <RelativeTime timestamp={service.lastHealthCheck} />
      </td>
      <td onClick={(e) => e.stopPropagation()}>
        <ServiceActionsMenu service={service} />
      </td>
    </tr>
  );
};
```

### 4. Health Trends and Analytics

#### Historical Health Analysis
```typescript
const HealthTrendsWidget: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  
  const { data: trendsData } = useCovetPyRealTimeData(
    `/api/v1/health/trends?range=${timeRange}&services=${selectedServices.join(',')}`
  );
  
  return (
    <div className="health-trends-widget">
      <div className="trends-header">
        <h3>Health Trends</h3>
        <div className="trends-controls">
          <ServiceSelector
            selectedServices={selectedServices}
            onChange={setSelectedServices}
          />
          <TimeRangeSelector
            value={timeRange}
            onChange={setTimeRange}
          />
        </div>
      </div>
      
      <div className="trends-content">
        <div className="trends-summary">
          <TrendSummaryCard
            title="Overall Health"
            current={trendsData?.overallHealth?.current}
            previous={trendsData?.overallHealth?.previous}
            trend={trendsData?.overallHealth?.trend}
          />
          <TrendSummaryCard
            title="Avg Response Time"
            current={trendsData?.avgResponseTime?.current}
            previous={trendsData?.avgResponseTime?.previous}
            trend={trendsData?.avgResponseTime?.trend}
            format="duration"
          />
          <TrendSummaryCard
            title="Incident Count"
            current={trendsData?.incidents?.current}
            previous={trendsData?.incidents?.previous}
            trend={trendsData?.incidents?.trend}
            format="number"
          />
          <TrendSummaryCard
            title="MTTR"
            current={trendsData?.mttr?.current}
            previous={trendsData?.mttr?.previous}
            trend={trendsData?.mttr?.trend}
            format="duration"
          />
        </div>
        
        <div className="trends-chart">
          <HealthTrendsChart
            data={trendsData?.timeSeries}
            services={selectedServices}
            timeRange={timeRange}
          />
        </div>
        
        <div className="incidents-timeline">
          <h4>Recent Incidents</h4>
          <IncidentsTimeline
            incidents={trendsData?.incidents}
            timeRange={timeRange}
          />
        </div>
      </div>
    </div>
  );
};

const HealthTrendsChart: React.FC<{
  data: HealthTimeSeriesData[];
  services: string[];
  timeRange: string;
}> = ({ data, services, timeRange }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={(value) => formatTime(value, timeRange)}
        />
        <YAxis
          domain={[0, 100]}
          tickFormatter={(value) => `${value}%`}
          label={{ value: 'Health Score %', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip
          labelFormatter={(value) => formatTimestamp(value)}
          formatter={(value, name) => [`${value}%`, name]}
        />
        <Legend />
        
        {services.map((serviceId, index) => (
          <Line
            key={serviceId}
            type="monotone"
            dataKey={`service_${serviceId}`}
            stroke={getServiceColor(serviceId, index)}
            strokeWidth={2}
            name={getServiceName(serviceId)}
            connectNulls={false}
            dot={{ r: 2 }}
            activeDot={{ r: 4 }}
          />
        ))}
        
        <Line
          type="monotone"
          dataKey="overall_health"
          stroke="#1565C0"
          strokeWidth={3}
          name="Overall Health"
          strokeDasharray="5,5"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

### 5. Service Dependencies

#### Dependency Graph Visualization
```typescript
const ServiceDependencyGraph: React.FC<{ serviceId: string }> = ({ serviceId }) => {
  const { data: dependencyData } = useCovetPyRealTimeData(
    `/api/v1/services/${serviceId}/dependencies`
  );
  
  return (
    <div className="service-dependency-graph">
      <div className="dependency-header">
        <h3>Service Dependencies</h3>
        <div className="dependency-controls">
          <DepthSelector />
          <DirectionToggle />
        </div>
      </div>
      
      <div className="dependency-visualization">
        <DependencyTreeView
          rootService={serviceId}
          dependencies={dependencyData?.dependencies}
          upstreams={dependencyData?.upstreams}
          downstreams={dependencyData?.downstreams}
        />
      </div>
      
      <div className="dependency-details">
        <DependencyHealthTable
          dependencies={dependencyData?.dependencies}
        />
      </div>
    </div>
  );
};
```

## Data Sources and API Integration

### Real-Time WebSocket Endpoints
```typescript
const HEALTH_WEBSOCKET_ENDPOINTS = {
  SYSTEM_HEALTH: '/ws/health/system',
  SERVICE_HEALTH: '/ws/health/services',
  TOPOLOGY: '/ws/topology',
  ALERTS: '/ws/alerts',
  METRICS: '/ws/metrics/health',
  INCIDENTS: '/ws/incidents'
} as const;

// Health monitoring API client
class HealthMonitoringAPI {
  async getSystemHealth(): Promise<SystemHealth> {
    const response = await fetch('/api/v1/health/system');
    if (!response.ok) throw new Error('Failed to fetch system health');
    return response.json();
  }
  
  async getServiceHealth(serviceId: string): Promise<ServiceHealth> {
    const response = await fetch(`/api/v1/health/services/${serviceId}`);
    if (!response.ok) throw new Error('Failed to fetch service health');
    return response.json();
  }
  
  async getServiceTopology(): Promise<ServiceTopology> {
    const response = await fetch('/api/v1/topology');
    if (!response.ok) throw new Error('Failed to fetch service topology');
    return response.json();
  }
  
  async getHealthTrends(params: HealthTrendsParams): Promise<HealthTrends> {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`/api/v1/health/trends?${query}`);
    if (!response.ok) throw new Error('Failed to fetch health trends');
    return response.json();
  }
}
```

### Data Models
```typescript
interface ServiceHealth {
  id: string;
  name: string;
  type: 'core' | 'support' | 'external';
  status: 'healthy' | 'warning' | 'critical' | 'unknown';
  healthScore: number;
  uptime: number;
  availability: number;
  metrics: ServiceMetrics;
  dependencies: ServiceDependency[];
  lastHealthCheck: Date;
  trend: HealthTrend;
}

interface ServiceMetrics {
  avgResponseTime: number;
  p95ResponseTime: number;
  p99ResponseTime: number;
  cpuUsage: number;
  memoryUsage: number;
  requestRate: number;
  errorRate: number;
  throughput: number;
}

interface HealthTrend {
  change: number;
  period: string;
  direction: 'up' | 'down' | 'stable';
}
```

This Service Health and Metrics Visualization provides comprehensive monitoring capabilities for CovetPy's distributed architecture, enabling administrators to maintain system reliability and quickly identify and resolve issues.