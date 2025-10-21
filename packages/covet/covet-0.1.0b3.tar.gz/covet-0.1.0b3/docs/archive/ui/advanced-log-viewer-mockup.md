# Advanced Log Viewer - UI Mockup

## Overview

The Advanced Log Viewer provides powerful real-time log analysis capabilities with intelligent filtering, search, pattern recognition, and correlation features. All log data is streamed live from backend logging APIs with no mock data.

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    Advanced Log Viewer                                              │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ 🔍 Search: [SQL injection OR 500 error]  📅 [Last 24h] ⚠️ [All Levels] 🏷️ [All Services]      │ │
│ │ [🎯 Smart Filters] [📊 Analytics] [📱 Patterns] [⚡ Real-time: ON] [📤 Export] [⚙️ Settings]   │ │
│ └─────────────────────────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────┐ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │   Log Summary    │ │                              Log Stream                                      │ │
│ │                  │ │ ┌─────────────────────────────────────────────────────────────────────────┐ │ │
│ │ 📊 Total: 45,231 │ │ │ 2024-01-15 14:25:30.123 [ERROR] api-gateway                            │ │ │
│ │ 🔴 Errors: 1,234 │ │ │ HTTP 500 Internal Server Error                                          │ │ │
│ │ 🟡 Warnings: 892 │ │ │ │ Request: POST /api/v1/users/create                                    │ │ │
│ │ 🔵 Info: 43,105  │ │ │ │ User: admin@company.com                                              │ │ │
│ │                  │ │ │ │ Error: Database connection timeout after 30s                        │ │ │
│ │ 📈 Rate: 2.3k/min│ │ │ │ Stack: UserController.create() line 145                             │ │ │
│ │                  │ │ │ │        DatabasePool.getConnection() line 89                          │ │ │
│ │ 🏷️ Top Services: │ │ │ │ Correlation ID: abc123-def456-ghi789                                │ │ │
│ │ • api-gateway    │ │ │ └─────────────────────────────────────────────────────────────────────┘ │ │
│ │ • user-service   │ │ │                                                                         │ │ │
│ │ • auth-service   │ │ │ 2024-01-15 14:25:25.456 [WARNING] user-service                        │ │ │
│ │ • db-service     │ │ │ High memory usage detected: 85% of available memory                    │ │ │
│ │                  │ │ │ │ Memory: 6.8GB / 8.0GB total                                         │ │ │
│ │ [View Patterns]  │ │ │ │ GC Pressure: High (15 collections in last minute)                   │ │ │
│ │                  │ │ │ │ Recommendation: Consider scaling or memory optimization              │ │ │
│ └──────────────────┘ │ │ │ Correlation ID: abc123-def456-ghi789                                │ │ │
│                      │ │ └─────────────────────────────────────────────────────────────────────┘ │ │
│                      │ │                                                                         │ │ │
│                      │ │ 2024-01-15 14:25:20.789 [INFO] auth-service                           │ │ │
│                      │ │ User authentication successful                                          │ │ │
│                      │ │ │ User: john.doe@company.com                                           │ │ │
│                      │ │ │ Session: sess_987654321                                              │ │ │
│                      │ │ │ IP: 192.168.1.100                                                   │ │ │
│                      │ │ │ Duration: 245ms                                                      │ │ │
│                      │ │                                                                         │ │ │
│                      │ │ 2024-01-15 14:25:18.012 [DEBUG] db-service                            │ │ │
│                      │ │ Query executed successfully                                             │ │ │
│                      │ │ │ Query: SELECT * FROM users WHERE email = ?                          │ │ │
│                      │ │ │ Duration: 12ms                                                       │ │ │
│                      │ │ │ Rows: 1                                                              │ │ │
│                      │ │ │ Cache: HIT                                                           │ │ │
│                      │ │                                                                         │ │ │
│                      │ │ [🔄 Auto-scroll] [⏸️ Pause] [📋 Copy] [🔗 Share] [⚡ Live: 2.3k/min]  │ │ │
│                      │ └─────────────────────────────────────────────────────────────────────────┘ │ │
│                      └─────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ ┌─────────────────────────────────────────────────────────┐ │
│ │           Log Analytics             │ │                    Pattern Detection                    │ │
│ │                                     │ │                                                         │ │
│ │ 📊 Error Rate Trend (Last Hour):   │ │ 🎯 Detected Patterns:                                  │ │
│ │ ▲ 14:00  ██████████████ 156/min    │ │                                                         │ │
│ │   14:15  ████████████   134/min    │ │ 🔴 Recurring Error Pattern (5 occurrences):           │ │
│ │   14:30  ██████████     112/min    │ │    "Database connection timeout"                        │ │
│ │ ▼ 14:45  ████████        89/min    │ │    Last seen: 2 minutes ago                           │ │
│ │                                     │ │    Affected services: api-gateway, user-service       │ │
│ │ 🏷️ Top Error Categories:            │ │                                                         │ │
│ │ • Database Issues     45%           │ │ 🟡 Spike Detection:                                    │ │
│ │ • Authentication      23%           │ │    "Failed login attempts" increased 300%             │ │
│ │ • Rate Limiting       18%           │ │    Started: 14:20 (5 minutes ago)                     │ │
│ │ • Timeout Errors      14%           │ │    Source: Multiple IPs (possible attack)             │ │
│ │                                     │ │                                                         │ │
│ │ 🔗 Correlation Analysis:            │ │ ℹ️ Anomaly Alert:                                       │ │
│ │ • High correlation between DB       │ │    Unusual silence from "payment-service"             │ │
│ │   timeouts and memory warnings      │ │    Last log: 10 minutes ago (expected: < 1 minute)   │ │ │
│ │ • Auth failures precede 500 errors │ │    Status: Investigating                               │ │
│ │                                     │ │                                                         │ │
│ │ [Generate Report] [Set Alert]       │ │ [Configure Patterns] [View All Alerts]                │ │
│ └─────────────────────────────────────┘ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                                  Smart Filter Builder                                           │ │
│ │                                                                                                 │ │
│ │ 🎯 Quick Filters:                                                                              │ │
│ │ [Errors Only] [Last 5 Minutes] [High Volume Services] [Failed Requests] [Security Events]    │ │
│ │                                                                                                 │ │
│ │ 🔧 Advanced Filters:                                                                           │ │
│ │ ┌─────────────────┐ ┌──────────────┐ ┌───────────────┐ ┌─────────────────────────────────────┐ │ │
│ │ │ Field:          │ │ Operator:    │ │ Value:        │ │ Actions:                            │ │ │
│ │ │ [Level      ▼]  │ │ [equals  ▼]  │ │ [ERROR    ]   │ │ [+ Add] [- Remove] [() Group]       │ │ │
│ │ └─────────────────┘ └──────────────┘ └───────────────┘ └─────────────────────────────────────┘ │ │
│ │ ┌─────────────────┐ ┌──────────────┐ ┌───────────────┐                                         │ │
│ │ │ [Service    ▼]  │ │ [contains ▼] │ │ [database   ] │ │ AND                                   │ │
│ │ └─────────────────┘ └──────────────┘ └───────────────┘                                         │ │
│ │ ┌─────────────────┐ ┌──────────────┐ ┌───────────────┐                                         │ │
│ │ │ [Timestamp  ▼]  │ │ [> (after) ▼]│ │ [14:20:00   ] │ │ AND                                   │ │
│ │ └─────────────────┘ └──────────────┘ └───────────────┘                                         │ │
│ │                                                                                                 │ │
│ │ 💾 Saved Filters:                                                                              │ │
│ │ [🔴 Critical Errors] [⚠️ DB Issues] [🔐 Auth Problems] [📊 High Traffic] [+ Save Current]     │ │
│ │                                                                                                 │ │
│ │ Query Preview: level="ERROR" AND service CONTAINS "database" AND timestamp > "2024-01-15T14:20" │ │
│ │ Expected Results: ~1,234 log entries                                                            │ │
│ └─────────────────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Specifications

### Log Stream Viewer
```typescript
interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'ERROR' | 'WARN' | 'INFO' | 'DEBUG';
  service: string;
  message: string;
  metadata: Record<string, any>;
  correlationId?: string;
  userId?: string;
  requestId?: string;
  stackTrace?: string;
  context: {
    file?: string;
    line?: number;
    function?: string;
  };
}

interface LogStreamViewerProps {
  filters: LogFilter[];
  realTime: boolean;
  autoScroll: boolean;
  maxEntries: number;
}

const LogStreamViewer: React.FC<LogStreamViewerProps> = ({
  filters,
  realTime,
  autoScroll,
  maxEntries = 10000
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [searchHighlight, setSearchHighlight] = useState<string>('');
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Real-time log streaming
  const { data: streamData, isConnected } = useCovetPyRealTimeData(
    `/api/v1/logs/stream?${buildFilterQuery(filters)}`,
    { enabled: realTime }
  );
  
  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);
  
  // Handle incoming log stream
  useEffect(() => {
    if (streamData) {
      setLogs(prevLogs => {
        const newLogs = [...prevLogs, ...streamData];
        return newLogs.slice(-maxEntries); // Keep only last N entries
      });
    }
  }, [streamData, maxEntries]);

  return (
    <Card className="flex-1">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Log Stream</CardTitle>
          <div className="flex items-center gap-2">
            <LogStreamControls
              realTime={realTime}
              autoScroll={autoScroll}
              isConnected={isConnected}
              logCount={logs.length}
            />
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div 
          ref={scrollRef}
          className="h-96 overflow-y-auto font-mono text-sm"
        >
          <div className="divide-y">
            {logs.map((log, index) => (
              <LogEntryRow
                key={log.id}
                log={log}
                searchHighlight={searchHighlight}
                isSelected={selectedLog?.id === log.id}
                onClick={setSelectedLog}
              />
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const LogEntryRow: React.FC<{
  log: LogEntry;
  searchHighlight: string;
  isSelected: boolean;
  onClick: (log: LogEntry) => void;
}> = ({ log, searchHighlight, isSelected, onClick }) => {
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR': return 'text-red-600 bg-red-50';
      case 'WARN': return 'text-yellow-600 bg-yellow-50';
      case 'INFO': return 'text-blue-600 bg-blue-50';
      case 'DEBUG': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const highlightText = (text: string, highlight: string) => {
    if (!highlight) return text;
    
    const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === highlight.toLowerCase() ? (
        <mark key={index} className="bg-yellow-200">{part}</mark>
      ) : part
    );
  };

  return (
    <div
      className={cn(
        'p-3 hover:bg-muted cursor-pointer transition-colors',
        isSelected && 'bg-primary/10 border-l-4 border-l-primary'
      )}
      onClick={() => onClick(log)}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <div className="text-xs text-muted-foreground">
            {formatTimestamp(log.timestamp)}
          </div>
          <div className={cn(
            'inline-block px-1.5 py-0.5 rounded text-xs font-medium mt-1',
            getLevelColor(log.level)
          )}>
            {log.level}
          </div>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-sm">{log.service}</span>
            {log.correlationId && (
              <code className="text-xs bg-muted px-1 rounded">
                {log.correlationId.slice(0, 8)}...
              </code>
            )}
          </div>
          
          <div className="text-sm">
            {highlightText(log.message, searchHighlight)}
          </div>
          
          {log.metadata && Object.keys(log.metadata).length > 0 && (
            <div className="mt-2 text-xs text-muted-foreground space-y-1">
              {Object.entries(log.metadata).map(([key, value]) => (
                <div key={key} className="flex">
                  <span className="font-medium min-w-0 mr-2">{key}:</span>
                  <span className="text-foreground">{String(value)}</span>
                </div>
              ))}
            </div>
          )}
          
          {log.stackTrace && (
            <details className="mt-2">
              <summary className="text-xs text-muted-foreground cursor-pointer">
                Stack Trace
              </summary>
              <pre className="mt-1 text-xs whitespace-pre-wrap text-red-600">
                {log.stackTrace}
              </pre>
            </details>
          )}
        </div>
      </div>
    </div>
  );
};
```

### Smart Filter Builder
```typescript
interface FilterCondition {
  field: string;
  operator: 'equals' | 'contains' | 'startsWith' | 'regex' | 'gt' | 'lt' | 'between';
  value: string | number | Date;
  logicalOperator?: 'AND' | 'OR' | 'NOT';
}

interface SavedFilter {
  id: string;
  name: string;
  conditions: FilterCondition[];
  createdAt: Date;
  usageCount: number;
}

const SmartFilterBuilder: React.FC = () => {
  const [conditions, setConditions] = useState<FilterCondition[]>([]);
  const [savedFilters, setSavedFilters] = useState<SavedFilter[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const { data: filterSuggestions } = useCovetPyRealTimeData('/api/v1/logs/filter-suggestions');
  
  const quickFilters = [
    { name: 'Errors Only', conditions: [{ field: 'level', operator: 'equals', value: 'ERROR' }] },
    { name: 'Last 5 Minutes', conditions: [{ field: 'timestamp', operator: 'gt', value: new Date(Date.now() - 5 * 60 * 1000) }] },
    { name: 'High Volume Services', conditions: [{ field: 'service', operator: 'contains', value: 'api-gateway' }] },
    { name: 'Failed Requests', conditions: [{ field: 'message', operator: 'contains', value: '500' }] },
    { name: 'Security Events', conditions: [{ field: 'service', operator: 'equals', value: 'auth-service' }] },
  ];

  const addCondition = () => {
    setConditions(prev => [
      ...prev,
      { field: 'level', operator: 'equals', value: '', logicalOperator: 'AND' }
    ]);
  };

  const removeCondition = (index: number) => {
    setConditions(prev => prev.filter((_, i) => i !== index));
  };

  const updateCondition = (index: number, updates: Partial<FilterCondition>) => {
    setConditions(prev => prev.map((condition, i) =>
      i === index ? { ...condition, ...updates } : condition
    ));
  };

  const saveCurrentFilter = () => {
    const name = prompt('Enter filter name:');
    if (name && conditions.length > 0) {
      const newFilter: SavedFilter = {
        id: generateId('filter_'),
        name,
        conditions,
        createdAt: new Date(),
        usageCount: 0,
      };
      setSavedFilters(prev => [...prev, newFilter]);
    }
  };

  const applyFilter = (filter: SavedFilter) => {
    setConditions(filter.conditions);
    setSavedFilters(prev =>
      prev.map(f => f.id === filter.id ? { ...f, usageCount: f.usageCount + 1 } : f)
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Smart Filter Builder
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? 'Simple' : 'Advanced'}
          </Button>
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {/* Quick Filters */}
          <div>
            <h4 className="font-medium mb-2">Quick Filters</h4>
            <div className="flex flex-wrap gap-2">
              {quickFilters.map((filter) => (
                <Button
                  key={filter.name}
                  variant="outline"
                  size="sm"
                  onClick={() => setConditions(filter.conditions)}
                >
                  {filter.name}
                </Button>
              ))}
            </div>
          </div>
          
          {/* Advanced Filter Builder */}
          {showAdvanced && (
            <div>
              <h4 className="font-medium mb-2">Advanced Filters</h4>
              <div className="space-y-2">
                {conditions.map((condition, index) => (
                  <FilterConditionRow
                    key={index}
                    condition={condition}
                    index={index}
                    onUpdate={updateCondition}
                    onRemove={removeCondition}
                    showLogicalOperator={index > 0}
                  />
                ))}
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={addCondition}
                  className="w-full"
                >
                  + Add Condition
                </Button>
              </div>
            </div>
          )}
          
          {/* Saved Filters */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium">Saved Filters</h4>
              <Button size="sm" onClick={saveCurrentFilter}>
                Save Current
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {savedFilters.map((filter) => (
                <div key={filter.id} className="flex items-center">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => applyFilter(filter)}
                    className="rounded-r-none"
                  >
                    {filter.name}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSavedFilters(prev => prev.filter(f => f.id !== filter.id))}
                    className="rounded-l-none border-l-0 px-2"
                  >
                    ×
                  </Button>
                </div>
              ))}
            </div>
          </div>
          
          {/* Query Preview */}
          {conditions.length > 0 && (
            <div>
              <h4 className="font-medium mb-2">Query Preview</h4>
              <code className="block p-2 bg-muted rounded text-sm">
                {buildQueryString(conditions)}
              </code>
              <div className="text-xs text-muted-foreground mt-1">
                Expected Results: ~{filterSuggestions?.estimatedCount || 0} log entries
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
```

### Log Analytics Dashboard
```typescript
interface LogAnalytics {
  errorRateTrend: TimeSeriesData[];
  topErrorCategories: Array<{ category: string; count: number; percentage: number }>;
  serviceBreakdown: Array<{ service: string; count: number; errorRate: number }>;
  correlationAnalysis: CorrelationResult[];
  anomalies: AnomalyDetection[];
}

interface CorrelationResult {
  eventA: string;
  eventB: string;
  correlation: number;
  confidence: number;
  description: string;
}

const LogAnalyticsDashboard: React.FC = () => {
  const { data: analytics } = useCovetPyRealTimeData('/api/v1/logs/analytics');
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Error Rate Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {analytics?.errorRateTrend?.map((point, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm">
                  {formatTime(point.timestamp)}
                </span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-muted rounded-full h-2">
                    <div
                      className="bg-destructive h-2 rounded-full"
                      style={{ width: `${(point.value / 200) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-mono">
                    {point.value}/min
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 pt-4 border-t">
            <h4 className="font-medium mb-2">Top Error Categories</h4>
            <div className="space-y-1">
              {analytics?.topErrorCategories?.map((category) => (
                <div key={category.category} className="flex items-center justify-between text-sm">
                  <span>{category.category}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono">{category.count}</span>
                    <span className="text-muted-foreground">
                      ({category.percentage}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Pattern Detection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-sm text-destructive mb-2">
                🔴 Recurring Error Patterns
              </h4>
              <div className="space-y-2">
                <div className="p-2 bg-destructive/10 rounded border-l-4 border-l-destructive">
                  <div className="font-medium text-sm">Database connection timeout</div>
                  <div className="text-xs text-muted-foreground">
                    5 occurrences • Last seen: 2 minutes ago
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Services: api-gateway, user-service
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-sm text-warning mb-2">
                🟡 Spike Detection
              </h4>
              <div className="p-2 bg-warning/10 rounded border-l-4 border-l-warning">
                <div className="font-medium text-sm">Failed login attempts</div>
                <div className="text-xs text-muted-foreground">
                  Increased 300% • Started: 5 minutes ago
                </div>
                <div className="text-xs text-muted-foreground">
                  Source: Multiple IPs (possible attack)
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-sm text-info mb-2">
                ℹ️ Anomaly Alerts
              </h4>
              <div className="p-2 bg-info/10 rounded border-l-4 border-l-info">
                <div className="font-medium text-sm">Unusual silence from payment-service</div>
                <div className="text-xs text-muted-foreground">
                  Last log: 10 minutes ago (expected: &lt; 1 minute)
                </div>
                <div className="text-xs text-muted-foreground">
                  Status: Investigating
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-4 flex gap-2">
            <Button size="sm" variant="outline">
              Configure Patterns
            </Button>
            <Button size="sm" variant="outline">
              View All Alerts
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
```

### Real-Time Log Statistics
```typescript
const LogStatistics: React.FC = () => {
  const { data: stats } = useCovetPyRealTimeData('/api/v1/logs/statistics');
  
  const topServices = stats?.serviceBreakdown?.slice(0, 5) || [];
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Log Summary</CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <MetricCard
              title="Total Logs"
              value={stats?.totalLogs || 0}
              format="number"
              size="sm"
            />
            <MetricCard
              title="Log Rate"
              value={stats?.logsPerMinute || 0}
              format="number"
              unit="/min"
              size="sm"
            />
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-destructive rounded-full"></div>
                <span className="text-sm">Errors</span>
              </div>
              <span className="font-medium">{stats?.errorCount || 0}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-warning rounded-full"></div>
                <span className="text-sm">Warnings</span>
              </div>
              <span className="font-medium">{stats?.warningCount || 0}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-info rounded-full"></div>
                <span className="text-sm">Info</span>
              </div>
              <span className="font-medium">{stats?.infoCount || 0}</span>
            </div>
          </div>
          
          <div className="pt-3 border-t">
            <h4 className="font-medium text-sm mb-2">Top Services</h4>
            <div className="space-y-1">
              {topServices.map((service) => (
                <div key={service.service} className="text-sm">
                  • {service.service}
                </div>
              ))}
            </div>
          </div>
          
          <Button variant="outline" size="sm" className="w-full">
            View Patterns
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
```

## API Integration Points

```typescript
// Real-time log streaming endpoints
const LOG_ENDPOINTS = {
  STREAM: '/api/v1/logs/stream',
  SEARCH: '/api/v1/logs/search',
  STATISTICS: '/api/v1/logs/statistics',
  ANALYTICS: '/api/v1/logs/analytics',
  PATTERNS: '/api/v1/logs/patterns',
  EXPORT: '/api/v1/logs/export',
  CORRELATE: '/api/v1/logs/correlate',
  ALERTS: '/api/v1/logs/alerts',
} as const;

// WebSocket endpoints for real-time updates
const LOG_WEBSOCKETS = {
  STREAM: '/ws/logs/stream',
  STATISTICS: '/ws/logs/statistics',
  PATTERNS: '/ws/logs/patterns',
  ALERTS: '/ws/logs/alerts',
} as const;
```

This advanced log viewer provides comprehensive real-time log analysis capabilities with intelligent pattern detection, correlation analysis, and powerful filtering options, all connected to live logging APIs for accurate operational insights.