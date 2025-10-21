# Database Query Analyzer Interface

## Overview

The Database Query Analyzer Interface provides comprehensive database performance monitoring, query optimization, and analytics capabilities for CovetPy applications. This interface enables developers and database administrators to analyze query performance, identify bottlenecks, and optimize database operations in real-time.

## Interface Architecture

### Query Analyzer Dashboard Layout
```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Database Query Analyzer                           │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │   Active    │ │   Slow      │ │   Total     │ │    Connection       │ │
│ │  Queries:   │ │  Queries:   │ │  Queries:   │ │      Pool           │ │
│ │     247     │ │     12      │ │   45.2K     │ │  Active: 45/100     │ │
│ │ 🟢 Normal   │ │ 🔴 +3 new   │ │ ▲ +12.5%    │ │  ████████████░░░░   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                         Query Explorer                              │ │
│ │ ┌───────────────────────────────────────────────────────────────────┐ │ │
│ │ │ 📊 [Live Queries] [Slow Queries] [Query History] [Explain Plans] │ │ │
│ │ │ 🔍 Search: [query text...] 📅 Last: [1h ▼] 🏷️ DB: [all ▼]    │ │ │
│ │ └───────────────────────────────────────────────────────────────────┘ │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │                         Query List                             │ │ │
│ │ │ ┌─────────────────────────────────────────────────────────────┐ │ │ │
│ │ │ │ ID    Query                     Duration  Rows  Database   │ │ │ │
│ │ │ │ 1247  SELECT * FROM users       1.2s     5.2K  covet   │ │ │ │
│ │ │ │       WHERE age > ?                                       │ │ │ │
│ │ │ │ 1248  UPDATE orders SET         890ms    1     orders     │ │ │ │
│ │ │ │       status = ? WHERE id = ?                              │ │ │ │
│ │ │ │ 1249  SELECT o.*, u.name        2.1s     890   analytics  │ │ │ │
│ │ │ │       FROM orders o JOIN...     🔴 SLOW                    │ │ │ │
│ │ │ └─────────────────────────────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │        Query Analysis           │ │        Performance Metrics      │ │
│ │ ┌─────────────────────────────┐ │ │ ┌─────────────────────────────┐ │ │
│ │ │ SELECT o.*, u.name FROM     │ │ │ │     Query Duration Trend    │ │ │
│ │ │ orders o JOIN users u       │ │ │ │ ▲ Duration (ms)             │ │ │
│ │ │ ON o.user_id = u.id         │ │ │ │ │ 3000 ┤                    │ │ │
│ │ │ WHERE o.status = 'pending'  │ │ │ │ │ 2500 ┤      ●●●           │ │ │
│ │ │                             │ │ │ │ │ 2000 ┤    ●●●●●●          │ │ │
│ │ │ Execution Plan:             │ │ │ │ │ 1500 ┤  ●●●●●●●●●         │ │ │
│ │ │ 1. Seq Scan on orders       │ │ │ │ │ 1000 ┤●●●●●●●●●●●●        │ │ │
│ │ │    (cost=0..1000)          │ │ │ │ │  500 └─────────────────────→ │ │ │
│ │ │ 2. Hash Join               │ │ │ │ │      15:30  15:45  16:00   │ │ │
│ │ │    (cost=1000..2500)       │ │ │ │ └─────────────────────────────┘ │ │
│ │ │                             │ │ │ │                                 │ │
│ │ │ [Optimize] [Explain] [Save] │ │ │ │ Avg: 1.8s | P95: 2.5s         │ │
│ │ └─────────────────────────────┘ │ │ │ Peak: 3.2s | Executions: 1.2K  │ │
│ └─────────────────────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Live Query Monitor

#### Real-Time Query Stream
```typescript
interface DatabaseQuery {
  id: string;
  sessionId: string;
  database: string;
  schema?: string;
  query: string;
  parameters?: any[];
  startTime: Date;
  endTime?: Date;
  duration?: number;
  rowsAffected: number;
  bytesTransferred: number;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  errorMessage?: string;
  executionPlan?: ExecutionPlan;
  connectionInfo: ConnectionInfo;
  metrics: QueryMetrics;
}

interface QueryMetrics {
  cpuTime: number;
  ioReads: number;
  ioWrites: number;
  memoryUsage: number;
  diskSpills: number;
  locksHeld: number;
  blockedBy?: string[];
}

const LiveQueryMonitor: React.FC = () => {
  const [queries, setQueries] = useState<DatabaseQuery[]>([]);
  const [filters, setFilters] = useState<QueryFilters>({
    database: 'all',
    status: 'all',
    minDuration: 0,
    showOnlySlow: false
  });
  const [isConnected, setIsConnected] = useState(false);
  
  // Real-time WebSocket connection for live queries
  useEffect(() => {
    const ws = new WebSocket('wss://api.covet.local/ws/database/queries');
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Database query stream connected');
    };
    
    ws.onmessage = (event) => {
      const queryUpdate: DatabaseQuery = JSON.parse(event.data);
      
      setQueries(prevQueries => {
        const existingIndex = prevQueries.findIndex(q => q.id === queryUpdate.id);
        
        if (existingIndex >= 0) {
          // Update existing query
          const updated = [...prevQueries];
          updated[existingIndex] = queryUpdate;
          return updated;
        } else {
          // Add new query
          return [queryUpdate, ...prevQueries.slice(0, 999)]; // Keep last 1000 queries
        }
      });
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('Database query stream disconnected');
    };
    
    return () => ws.close();
  }, []);
  
  const filteredQueries = useMemo(() => {
    return queries.filter(query => {
      if (filters.database !== 'all' && query.database !== filters.database) return false;
      if (filters.status !== 'all' && query.status !== filters.status) return false;
      if (query.duration && query.duration < filters.minDuration) return false;
      if (filters.showOnlySlow && (!query.duration || query.duration < 1000)) return false;
      return true;
    });
  }, [queries, filters]);
  
  return (
    <div className="live-query-monitor">
      <div className="monitor-header">
        <div className="connection-status">
          <ConnectionIndicator connected={isConnected} />
          <span className="query-count">{filteredQueries.length} queries</span>
        </div>
        
        <QueryFilters
          filters={filters}
          onChange={setFilters}
        />
      </div>
      
      <div className="query-stream">
        <VirtualizedList
          items={filteredQueries}
          itemHeight={120}
          renderItem={({ item: query }) => (
            <QueryCard
              key={query.id}
              query={query}
              onClick={() => {/* Open query details */}}
            />
          )}
        />
      </div>
    </div>
  );
};

const QueryCard: React.FC<{
  query: DatabaseQuery;
  onClick: () => void;
}> = ({ query, onClick }) => {
  const statusColors = {
    running: '#2563EB',
    completed: '#16A34A',
    failed: '#DC2626',
    cancelled: '#9CA3AF'
  };
  
  const formatQuery = (sql: string) => {
    return sql.length > 100 ? sql.substring(0, 100) + '...' : sql;
  };
  
  return (
    <div 
      className={`query-card status-${query.status}`}
      onClick={onClick}
    >
      <div className="query-header">
        <div className="query-id">#{query.id}</div>
        <div className="query-database">
          <DatabaseIcon />
          {query.database}
        </div>
        <div className="query-status">
          <StatusBadge 
            status={query.status}
            color={statusColors[query.status]}
          />
        </div>
        <div className="query-duration">
          {query.duration ? (
            <span className={query.duration > 1000 ? 'slow-query' : ''}>
              {formatDuration(query.duration)}
            </span>
          ) : (
            <span className="running-indicator">Running...</span>
          )}
        </div>
      </div>
      
      <div className="query-sql">
        <CodeBlock
          code={formatQuery(query.query)}
          language="sql"
          compact
        />
      </div>
      
      <div className="query-metrics">
        <QueryMetric
          label="Rows"
          value={query.rowsAffected}
          format="number"
        />
        <QueryMetric
          label="CPU"
          value={query.metrics.cpuTime}
          format="duration"
        />
        <QueryMetric
          label="I/O Reads"
          value={query.metrics.ioReads}
          format="number"
        />
        <QueryMetric
          label="Memory"
          value={query.metrics.memoryUsage}
          format="bytes"
        />
        {query.metrics.blockedBy && query.metrics.blockedBy.length > 0 && (
          <div className="blocked-indicator">
            <LockIcon />
            Blocked by {query.metrics.blockedBy.length} queries
          </div>
        )}
      </div>
    </div>
  );
};
```

### 2. Query Performance Analyzer

#### Query Details and Optimization
```typescript
const QueryAnalyzer: React.FC<{
  queryId: string;
  onClose: () => void;
}> = ({ queryId, onClose }) => {
  const { data: queryDetails } = useCovetPyRealTimeData(`/api/v1/database/queries/${queryId}`);
  const { data: executionPlan } = useCovetPyRealTimeData(`/api/v1/database/queries/${queryId}/plan`);
  const { data: optimizationSuggestions } = useCovetPyRealTimeData(`/api/v1/database/queries/${queryId}/optimize`);
  
  const [activeTab, setActiveTab] = useState('details');
  
  if (!queryDetails) {
    return <QueryAnalyzerSkeleton />;
  }
  
  return (
    <Modal isOpen onClose={onClose} size="xl">
      <div className="query-analyzer">
        <div className="analyzer-header">
          <h3>Query Analysis #{queryDetails.id}</h3>
          <div className="analyzer-actions">
            <button className="btn btn-secondary">
              <ExplainIcon /> Explain Plan
            </button>
            <button className="btn btn-secondary">
              <OptimizeIcon /> Optimize
            </button>
            <button className="btn btn-primary">
              <SaveIcon /> Save Analysis
            </button>
          </div>
        </div>
        
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="details">Query Details</TabsTrigger>
            <TabsTrigger value="execution">Execution Plan</TabsTrigger>
            <TabsTrigger value="optimization">Optimization</TabsTrigger>
            <TabsTrigger value="history">Execution History</TabsTrigger>
          </TabsList>
          
          <TabsContent value="details">
            <QueryDetailsTab query={queryDetails} />
          </TabsContent>
          
          <TabsContent value="execution">
            <ExecutionPlanTab plan={executionPlan} />
          </TabsContent>
          
          <TabsContent value="optimization">
            <OptimizationTab 
              suggestions={optimizationSuggestions}
              query={queryDetails}
            />
          </TabsContent>
          
          <TabsContent value="history">
            <QueryHistoryTab queryHash={queryDetails.hash} />
          </TabsContent>
        </Tabs>
      </div>
    </Modal>
  );
};

const QueryDetailsTab: React.FC<{
  query: DatabaseQuery;
}> = ({ query }) => {
  return (
    <div className="query-details-tab">
      <div className="details-grid">
        <div className="query-section">
          <h4>SQL Query</h4>
          <SQLEditor
            value={query.query}
            readOnly
            showLineNumbers
            highlightSyntax
          />
          
          {query.parameters && query.parameters.length > 0 && (
            <div className="query-parameters">
              <h5>Parameters</h5>
              <ParametersTable parameters={query.parameters} />
            </div>
          )}
        </div>
        
        <div className="execution-section">
          <h4>Execution Details</h4>
          <div className="execution-metrics">
            <MetricCard
              title="Duration"
              value={query.duration}
              format="duration"
              status={query.duration > 1000 ? 'warning' : 'success'}
            />
            <MetricCard
              title="Rows Affected"
              value={query.rowsAffected}
              format="number"
            />
            <MetricCard
              title="Bytes Transferred"
              value={query.bytesTransferred}
              format="bytes"
            />
            <MetricCard
              title="CPU Time"
              value={query.metrics.cpuTime}
              format="duration"
            />
          </div>
          
          <div className="resource-usage">
            <h5>Resource Usage</h5>
            <ResourceUsageChart metrics={query.metrics} />
          </div>
        </div>
        
        <div className="connection-section">
          <h4>Connection Info</h4>
          <ConnectionDetails connection={query.connectionInfo} />
        </div>
      </div>
    </div>
  );
};

const ExecutionPlanTab: React.FC<{
  plan: ExecutionPlan;
}> = ({ plan }) => {
  const [viewMode, setViewMode] = useState<'tree' | 'table' | 'graph'>('tree');
  
  return (
    <div className="execution-plan-tab">
      <div className="plan-header">
        <h4>Execution Plan</h4>
        <div className="plan-controls">
          <ViewModeToggle
            modes={['tree', 'table', 'graph']}
            current={viewMode}
            onChange={setViewMode}
          />
          <button className="btn btn-secondary">
            <ExportIcon /> Export Plan
          </button>
        </div>
      </div>
      
      <div className="plan-content">
        {viewMode === 'tree' && (
          <ExecutionPlanTree plan={plan} />
        )}
        
        {viewMode === 'table' && (
          <ExecutionPlanTable plan={plan} />
        )}
        
        {viewMode === 'graph' && (
          <ExecutionPlanGraph plan={plan} />
        )}
      </div>
      
      <div className="plan-analysis">
        <PlanAnalysis plan={plan} />
      </div>
    </div>
  );
};

const ExecutionPlanTree: React.FC<{
  plan: ExecutionPlan;
}> = ({ plan }) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  
  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };
  
  const renderPlanNode = (node: PlanNode, level: number = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const hasChildren = node.children && node.children.length > 0;
    
    return (
      <div key={node.id} className="plan-node" style={{ marginLeft: `${level * 20}px` }}>
        <div className="node-header" onClick={() => hasChildren && toggleNode(node.id)}>
          {hasChildren && (
            <ChevronIcon direction={isExpanded ? 'down' : 'right'} />
          )}
          <PlanNodeIcon type={node.type} />
          <span className="node-name">{node.operation}</span>
          <span className="node-cost">{node.cost}</span>
          <span className="node-rows">{node.actualRows} rows</span>
          <span className="node-time">{formatDuration(node.actualTime)}</span>
        </div>
        
        {isExpanded && node.details && (
          <div className="node-details">
            <PlanNodeDetails details={node.details} />
          </div>
        )}
        
        {isExpanded && hasChildren && (
          <div className="node-children">
            {node.children.map(child => renderPlanNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="execution-plan-tree">
      {plan.nodes.map(node => renderPlanNode(node))}
    </div>
  );
};
```

### 3. Query Optimization Engine

#### Optimization Suggestions
```typescript
interface OptimizationSuggestion {
  id: string;
  type: 'index' | 'rewrite' | 'parameter' | 'schema' | 'configuration';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  expectedImprovement: {
    durationReduction: number;
    costReduction: number;
    confidence: number;
  };
  implementation: {
    sql?: string;
    steps: string[];
    effort: 'low' | 'medium' | 'high';
    risk: 'low' | 'medium' | 'high';
  };
  examples?: {
    before: string;
    after: string;
  };
}

const OptimizationTab: React.FC<{
  suggestions: OptimizationSuggestion[];
  query: DatabaseQuery;
}> = ({ suggestions, query }) => {
  const [selectedSuggestion, setSelectedSuggestion] = useState<OptimizationSuggestion | null>(null);
  const [implementationProgress, setImplementationProgress] = useState<Map<string, 'pending' | 'implementing' | 'completed' | 'failed'>>(new Map());
  
  const handleImplementSuggestion = async (suggestion: OptimizationSuggestion) => {
    setImplementationProgress(prev => new Map(prev).set(suggestion.id, 'implementing'));
    
    try {
      const response = await fetch('/api/v1/database/optimize/implement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          queryId: query.id,
          suggestionId: suggestion.id
        })
      });
      
      if (response.ok) {
        setImplementationProgress(prev => new Map(prev).set(suggestion.id, 'completed'));
      } else {
        throw new Error('Implementation failed');
      }
    } catch (error) {
      setImplementationProgress(prev => new Map(prev).set(suggestion.id, 'failed'));
      console.error('Failed to implement optimization:', error);
    }
  };
  
  return (
    <div className="optimization-tab">
      <div className="optimization-overview">
        <h4>Optimization Opportunities</h4>
        <div className="optimization-stats">
          <OptimizationStatCard
            title="Total Suggestions"
            value={suggestions.length}
            icon={<LightbulbIcon />}
          />
          <OptimizationStatCard
            title="Potential Improvement"
            value={calculateTotalImprovement(suggestions)}
            format="percentage"
            icon={<SpeedIcon />}
          />
          <OptimizationStatCard
            title="High Priority"
            value={suggestions.filter(s => s.severity === 'high' || s.severity === 'critical').length}
            icon={<WarningIcon />}
            status="warning"
          />
        </div>
      </div>
      
      <div className="suggestions-list">
        {suggestions.map((suggestion) => (
          <OptimizationSuggestionCard
            key={suggestion.id}
            suggestion={suggestion}
            selected={selectedSuggestion?.id === suggestion.id}
            implementationStatus={implementationProgress.get(suggestion.id)}
            onSelect={() => setSelectedSuggestion(suggestion)}
            onImplement={() => handleImplementSuggestion(suggestion)}
          />
        ))}
      </div>
      
      {selectedSuggestion && (
        <OptimizationDetails
          suggestion={selectedSuggestion}
          query={query}
          onClose={() => setSelectedSuggestion(null)}
        />
      )}
    </div>
  );
};

const OptimizationSuggestionCard: React.FC<{
  suggestion: OptimizationSuggestion;
  selected: boolean;
  implementationStatus?: 'pending' | 'implementing' | 'completed' | 'failed';
  onSelect: () => void;
  onImplement: () => void;
}> = ({ suggestion, selected, implementationStatus, onSelect, onImplement }) => {
  const severityColors = {
    low: '#16A34A',
    medium: '#D97706',
    high: '#DC2626',
    critical: '#7C2D12'
  };
  
  return (
    <div 
      className={`optimization-suggestion-card ${selected ? 'selected' : ''} severity-${suggestion.severity}`}
      onClick={onSelect}
    >
      <div className="suggestion-header">
        <div className="suggestion-type">
          <OptimizationTypeIcon type={suggestion.type} />
          <span className="type-label">{suggestion.type}</span>
        </div>
        
        <SeverityBadge
          severity={suggestion.severity}
          color={severityColors[suggestion.severity]}
        />
        
        <div className="improvement-score">
          <span className="score">
            {suggestion.expectedImprovement.durationReduction}% faster
          </span>
          <span className="confidence">
            {suggestion.expectedImprovement.confidence}% confidence
          </span>
        </div>
      </div>
      
      <div className="suggestion-content">
        <h5 className="suggestion-title">{suggestion.title}</h5>
        <p className="suggestion-description">{suggestion.description}</p>
        
        <div className="implementation-info">
          <div className="effort-risk">
            <span className="effort">Effort: {suggestion.implementation.effort}</span>
            <span className="risk">Risk: {suggestion.implementation.risk}</span>
          </div>
          
          <button
            className="btn btn-sm btn-primary"
            onClick={(e) => {
              e.stopPropagation();
              onImplement();
            }}
            disabled={implementationStatus === 'implementing' || implementationStatus === 'completed'}
          >
            {implementationStatus === 'implementing' && <LoadingIcon />}
            {implementationStatus === 'completed' && <CheckIcon />}
            {implementationStatus === 'failed' && <ErrorIcon />}
            {!implementationStatus && 'Implement'}
            {implementationStatus === 'implementing' && 'Implementing...'}
            {implementationStatus === 'completed' && 'Implemented'}
            {implementationStatus === 'failed' && 'Failed'}
          </button>
        </div>
      </div>
    </div>
  );
};
```

### 4. Query Performance Analytics

#### Historical Performance Analysis
```typescript
const QueryPerformanceAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [selectedDatabase, setSelectedDatabase] = useState('all');
  const [analysisType, setAnalysisType] = useState<'performance' | 'frequency' | 'resources'>('performance');
  
  const { data: analyticsData } = useCovetPyRealTimeData(
    `/api/v1/database/analytics?range=${timeRange}&database=${selectedDatabase}&type=${analysisType}`
  );
  
  return (
    <div className="query-performance-analytics">
      <div className="analytics-header">
        <h3>Query Performance Analytics</h3>
        <div className="analytics-controls">
          <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
          <DatabaseSelector value={selectedDatabase} onChange={setSelectedDatabase} />
          <AnalysisTypeSelector value={analysisType} onChange={setAnalysisType} />
        </div>
      </div>
      
      <div className="analytics-overview">
        <AnalyticsCard
          title="Total Queries"
          value={analyticsData?.totalQueries}
          trend={analyticsData?.queryTrend}
          format="number"
        />
        <AnalyticsCard
          title="Avg Duration"
          value={analyticsData?.avgDuration}
          trend={analyticsData?.durationTrend}
          format="duration"
        />
        <AnalyticsCard
          title="Slow Queries"
          value={analyticsData?.slowQueries}
          trend={analyticsData?.slowQueryTrend}
          format="number"
          threshold={{ warning: 50, critical: 100 }}
        />
        <AnalyticsCard
          title="Query Errors"
          value={analyticsData?.errorRate}
          trend={analyticsData?.errorTrend}
          format="percentage"
          threshold={{ warning: 1, critical: 5 }}
        />
      </div>
      
      <div className="analytics-charts">
        {analysisType === 'performance' && (
          <PerformanceChartsGroup data={analyticsData} timeRange={timeRange} />
        )}
        
        {analysisType === 'frequency' && (
          <FrequencyChartsGroup data={analyticsData} timeRange={timeRange} />
        )}
        
        {analysisType === 'resources' && (
          <ResourceChartsGroup data={analyticsData} timeRange={timeRange} />
        )}
      </div>
      
      <div className="top-queries-section">
        <TopQueriesTable
          queries={analyticsData?.topQueries || []}
          sortBy={analysisType}
        />
      </div>
    </div>
  );
};

const PerformanceChartsGroup: React.FC<{
  data: QueryAnalyticsData;
  timeRange: string;
}> = ({ data, timeRange }) => {
  return (
    <div className="performance-charts-group">
      <div className="chart-container">
        <QueryDurationTrend
          data={data.durationTrend}
          timeRange={timeRange}
        />
      </div>
      
      <div className="chart-container">
        <QueryVolumeChart
          data={data.volumeData}
          timeRange={timeRange}
        />
      </div>
      
      <div className="chart-container">
        <SlowQueryDistribution
          data={data.slowQueryDistribution}
        />
      </div>
      
      <div className="chart-container">
        <DatabasePerformanceComparison
          data={data.databasePerformance}
        />
      </div>
    </div>
  );
};
```

## Real-Time Data Integration

### Database Monitoring API
```typescript
// Database query analyzer API endpoints - NO MOCK DATA
const DATABASE_API_ENDPOINTS = {
  // Live query monitoring
  LIVE_QUERIES: '/ws/database/queries',
  QUERY_DETAILS: '/api/v1/database/queries/:id',
  KILL_QUERY: '/api/v1/database/queries/:id/kill',
  
  // Execution plans and optimization
  EXECUTION_PLAN: '/api/v1/database/queries/:id/plan',
  OPTIMIZATION_SUGGESTIONS: '/api/v1/database/queries/:id/optimize',
  IMPLEMENT_OPTIMIZATION: '/api/v1/database/optimize/implement',
  
  // Analytics and reporting
  QUERY_ANALYTICS: '/api/v1/database/analytics',
  SLOW_QUERY_LOG: '/api/v1/database/slow-queries',
  QUERY_HISTORY: '/api/v1/database/queries/history',
  
  // Database status and metrics
  DATABASE_STATUS: '/api/v1/database/status',
  CONNECTION_POOL: '/api/v1/database/connections',
  INDEX_USAGE: '/api/v1/database/indexes',
  
  // Configuration and tuning
  DATABASE_CONFIG: '/api/v1/database/config',
  PERFORMANCE_TUNING: '/api/v1/database/tuning'
} as const;

// Database monitoring WebSocket client
class DatabaseMonitoringService {
  private ws: WebSocket | null = null;
  
  connectToQueryStream(onQueryUpdate: (query: DatabaseQuery) => void) {
    this.ws = new WebSocket('wss://api.covet.local/ws/database/queries');
    
    this.ws.onopen = () => {
      console.log('Database query monitoring connected');
    };
    
    this.ws.onmessage = (event) => {
      const queryData = JSON.parse(event.data);
      onQueryUpdate(queryData);
    };
    
    this.ws.onclose = () => {
      console.log('Database query monitoring disconnected');
      // Implement reconnection logic
    };
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
```

### Type Definitions
```typescript
interface DatabaseQuery {
  id: string;
  sessionId: string;
  database: string;
  schema?: string;
  query: string;
  hash: string;
  parameters?: any[];
  startTime: Date;
  endTime?: Date;
  duration?: number;
  rowsAffected: number;
  bytesTransferred: number;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  errorMessage?: string;
  executionPlan?: ExecutionPlan;
  connectionInfo: ConnectionInfo;
  metrics: QueryMetrics;
}

interface ExecutionPlan {
  planId: string;
  totalCost: number;
  actualTime: number;
  nodes: PlanNode[];
  statistics: PlanStatistics;
}

interface QueryAnalyticsData {
  totalQueries: number;
  avgDuration: number;
  slowQueries: number;
  errorRate: number;
  durationTrend: TimeSeriesData[];
  volumeData: TimeSeriesData[];
  slowQueryDistribution: DistributionData[];
  databasePerformance: DatabasePerformanceData[];
  topQueries: TopQueryData[];
}
```

This Database Query Analyzer Interface provides comprehensive database performance monitoring and optimization capabilities for CovetPy applications, enabling efficient database management and query performance tuning.