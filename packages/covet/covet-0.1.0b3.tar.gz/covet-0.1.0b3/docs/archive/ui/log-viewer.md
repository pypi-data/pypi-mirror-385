# Real-Time Log Viewer with Search and Filtering

## Overview

The Real-Time Log Viewer provides comprehensive log analysis capabilities for CovetPy applications, featuring advanced search, filtering, real-time streaming, and intelligent log parsing. This interface enables developers and administrators to quickly diagnose issues, monitor system behavior, and analyze performance patterns.

## Interface Architecture

### Log Viewer Dashboard Layout
```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Log Viewer Dashboard                          │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │   Total     │ │   Errors    │ │   Warnings  │ │    Live Stream      │ │
│ │   Logs:     │ │   Today:    │ │   Today:    │ │  🟢 Connected       │ │
│ │  2.4M       │ │    1,247    │ │    3,891    │ │  📊 125 logs/sec    │ │
│ │ ▲ +12.5%    │ │ 🔴 +15%     │ │ 🟡 +8%      │ │  🔄 Auto-refresh    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                        Search & Filters                            │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │ 🔍 [Search logs...] [Advanced] ⚡ Regex □ Case   📅 Last 1h  │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Level: [ALL] [ERROR] [WARN] [INFO] [DEBUG]                     │ │ │
│ │ │ Service: [covet-core ▼] Source: [application ▼]           │ │ │
│ │ │ [+ Custom Filter] [Save Filter] [Load Preset]                  │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                           Log Stream                                │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │ 2024-01-15 14:23:45.123 [ERROR] covet-core request.rs:42   │ │ │
│ │ │ Failed to process request: timeout after 30s                   │ │ │
│ │ │ {                                                               │ │ │
│ │ │   "request_id": "req_abc123",                                   │ │ │
│ │ │   "user_id": "user_456",                                        │ │ │
│ │ │   "endpoint": "/api/v1/users/profile",                          │ │ │
│ │ │   "duration_ms": 30000,                                         │ │ │
│ │ │   "error": "DatabaseTimeout"                                    │ │ │
│ │ │ }                                                               │ │ │
│ │ │ ───────────────────────────────────────────────────────────────│ │ │
│ │ │ 2024-01-15 14:23:44.891 [WARN] covet-db connection.rs:128   │ │ │
│ │ │ Connection pool exhausted, queueing request                     │ │ │
│ │ │ ───────────────────────────────────────────────────────────────│ │ │
│ │ │ 2024-01-15 14:23:44.234 [INFO] covet-core server.rs:89      │ │ │
│ │ │ Processing request GET /api/v1/users/profile                    │ │ │
│ │ │ ───────────────────────────────────────────────────────────────│ │ │
│ │ │                                                                 │ │ │
│ │ │ [Pause] [Clear] [Export] [Follow Tail] Showing 1-50 of 1.2M   │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │           Log Analytics         │ │          Quick Actions          │ │
│ │ ┌─────────────────────────────┐ │ │ [🔍 Find Related Logs]          │ │
│ │ │     Error Rate Trend        │ │ │ [📊 Create Alert Rule]          │ │
│ │ │ ▲ Errors/min                │ │ │ [📋 Copy Log Context]           │ │
│ │ │ │ 50 ┤                      │ │ │ [🔗 Share Log Permalink]        │ │
│ │ │ │ 40 ┤   ●●●                │ │ │ [📁 Open in Full View]          │ │
│ │ │ │ 30 ┤  ●●●●●               │ │ │ [⚠ Report Issue]                │ │
│ │ │ │ 20 ┤ ●●●●●●●              │ │ │                                 │ │
│ │ │ │ 10 ┤●●●●●●●●●             │ │ │ Recent Searches:                │ │
│ │ │ └─────────────────────────→ │ │ │ • "error timeout"               │ │
│ │ │   Last 15min                │ │ │ • "user_id:user_456"            │ │
│ │ └─────────────────────────────┘ │ │ • "level:ERROR database"        │ │
│ └─────────────────────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Real-Time Log Stream

#### Log Stream Component
```typescript
interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL';
  service: string;
  source: string;
  message: string;
  metadata?: Record<string, any>;
  traceId?: string;
  spanId?: string;
  userId?: string;
  requestId?: string;
  tags: string[];
}

interface LogStreamProps {
  filters: LogFilter[];
  searchQuery: string;
  realTime: boolean;
  maxEntries: number;
  onLogSelect: (log: LogEntry) => void;
}

const LogStream: React.FC<LogStreamProps> = ({
  filters,
  searchQuery,
  realTime,
  maxEntries = 1000,
  onLogSelect
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [logRate, setLogRate] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  
  const logStreamRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  
  // Real-time WebSocket connection for log streaming
  useEffect(() => {
    if (!realTime || isPaused) return;
    
    const wsUrl = new URL('/ws/logs', 'wss://api.covet.local');
    
    // Add filters and search query to WebSocket URL
    if (searchQuery) wsUrl.searchParams.set('search', searchQuery);
    if (filters.length > 0) {
      wsUrl.searchParams.set('filters', JSON.stringify(filters));
    }
    
    const ws = new WebSocket(wsUrl.toString());
    wsRef.current = ws;
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Log stream connected');
    };
    
    ws.onmessage = (event) => {
      const logEntry: LogEntry = JSON.parse(event.data);
      
      setLogs(prevLogs => {
        const newLogs = [logEntry, ...prevLogs];
        return newLogs.slice(0, maxEntries);
      });
      
      // Update log rate
      setLogRate(prev => prev + 1);
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('Log stream disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('Log stream error:', error);
      setIsConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, [realTime, isPaused, searchQuery, filters, maxEntries]);
  
  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logStreamRef.current) {
      logStreamRef.current.scrollTop = 0;
    }
  }, [logs, autoScroll]);
  
  // Calculate log rate per second
  useEffect(() => {
    const interval = setInterval(() => {
      setLogRate(0);
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="log-stream">
      <div className="log-stream-header">
        <div className="stream-status">
          <ConnectionIndicator connected={isConnected} />
          <span className="log-rate">{logRate} logs/sec</span>
        </div>
        
        <div className="stream-controls">
          <button
            className={`btn btn-sm ${isPaused ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setIsPaused(!isPaused)}
          >
            {isPaused ? <PlayIcon /> : <PauseIcon />}
            {isPaused ? 'Resume' : 'Pause'}
          </button>
          
          <button
            className="btn btn-sm btn-secondary"
            onClick={() => setLogs([])}
          >
            <ClearIcon /> Clear
          </button>
          
          <button
            className={`btn btn-sm ${autoScroll ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setAutoScroll(!autoScroll)}
          >
            <ScrollIcon /> Follow
          </button>
          
          <DropdownMenu
            trigger={
              <button className="btn btn-sm btn-secondary">
                <ExportIcon /> Export
              </button>
            }
            items={[
              { label: 'Export as JSON', onClick: () => exportLogs('json') },
              { label: 'Export as CSV', onClick: () => exportLogs('csv') },
              { label: 'Export as TXT', onClick: () => exportLogs('txt') }
            ]}
          />
        </div>
      </div>
      
      <div
        ref={logStreamRef}
        className="log-entries"
        style={{ height: '500px', overflow: 'auto' }}
      >
        <VirtualizedList
          items={logs}
          itemHeight={80}
          renderItem={({ item, index }) => (
            <LogEntry
              key={item.id}
              log={item}
              onClick={() => onLogSelect(item)}
              searchQuery={searchQuery}
            />
          )}
        />
        
        {logs.length === 0 && (
          <div className="empty-logs">
            <EmptyLogsIcon />
            <h3>No logs found</h3>
            <p>Try adjusting your search criteria or filters</p>
          </div>
        )}
      </div>
      
      <div className="log-stream-footer">
        <span className="log-count">
          Showing {Math.min(logs.length, maxEntries)} of {logs.length} logs
        </span>
        
        {logs.length >= maxEntries && (
          <span className="buffer-warning">
            <WarningIcon />
            Buffer limit reached. Older logs are being discarded.
          </span>
        )}
      </div>
    </div>
  );
};
```

#### Individual Log Entry Component
```typescript
const LogEntry: React.FC<{
  log: LogEntry;
  onClick: () => void;
  searchQuery: string;
}> = ({ log, onClick, searchQuery }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const levelColors = {
    DEBUG: '#6B7280',
    INFO: '#2563EB',
    WARN: '#D97706',
    ERROR: '#DC2626',
    FATAL: '#7C2D12'
  };
  
  const highlightText = (text: string, query: string) => {
    if (!query) return text;
    
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) =>
      regex.test(part) ? (
        <mark key={index} className="search-highlight">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };
  
  return (
    <div
      className={`log-entry level-${log.level.toLowerCase()}`}
      onClick={onClick}
    >
      <div className="log-entry-header">
        <div className="log-timestamp">
          {formatTimestamp(log.timestamp)}
        </div>
        
        <LogLevelBadge
          level={log.level}
          color={levelColors[log.level]}
        />
        
        <div className="log-service">
          <ServiceIcon service={log.service} />
          {log.service}
        </div>
        
        <div className="log-source">
          {log.source}
        </div>
        
        <div className="log-actions">
          {log.traceId && (
            <TraceButton traceId={log.traceId} />
          )}
          
          <button
            className="btn btn-ghost btn-xs"
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            <ChevronIcon direction={isExpanded ? 'up' : 'down'} />
          </button>
        </div>
      </div>
      
      <div className="log-message">
        {highlightText(log.message, searchQuery)}
      </div>
      
      {log.tags.length > 0 && (
        <div className="log-tags">
          {log.tags.map((tag) => (
            <TagBadge key={tag} tag={tag} />
          ))}
        </div>
      )}
      
      {isExpanded && log.metadata && (
        <div className="log-metadata">
          <h5>Metadata</h5>
          <JSONViewer data={log.metadata} collapsed={false} />
        </div>
      )}
    </div>
  );
};
```

### 2. Advanced Search and Filtering

#### Search Interface
```typescript
interface LogFilter {
  field: string;
  operator: 'equals' | 'contains' | 'regex' | 'range' | 'exists';
  value: any;
  label: string;
}

const AdvancedLogSearch: React.FC<{
  onSearch: (query: string, filters: LogFilter[]) => void;
  onSaveFilter: (name: string, filters: LogFilter[]) => void;
}> = ({ onSearch, onSaveFilter }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isRegexMode, setIsRegexMode] = useState(false);
  const [isCaseSensitive, setIsCaseSensitive] = useState(false);
  const [activeFilters, setActiveFilters] = useState<LogFilter[]>([]);
  const [timeRange, setTimeRange] = useState('1h');
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const { data: savedFilters } = useCovetPyRealTimeData('/api/v1/logs/filters');
  const { data: searchSuggestions } = useCovetPyRealTimeData(
    `/api/v1/logs/suggest?q=${searchQuery}`
  );
  
  const handleSearch = () => {
    onSearch(searchQuery, activeFilters);
  };
  
  const addFilter = (filter: LogFilter) => {
    setActiveFilters([...activeFilters, filter]);
  };
  
  const removeFilter = (index: number) => {
    setActiveFilters(activeFilters.filter((_, i) => i !== index));
  };
  
  return (
    <div className="advanced-log-search">
      <div className="search-bar">
        <div className="search-input-group">
          <SearchIcon />
          <input
            type="text"
            className="search-input"
            placeholder="Search logs... (e.g., error timeout, user_id:123, level:ERROR)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          
          <div className="search-options">
            <Checkbox
              id="regex"
              checked={isRegexMode}
              onChange={setIsRegexMode}
              label="Regex"
            />
            <Checkbox
              id="case"
              checked={isCaseSensitive}
              onChange={setIsCaseSensitive}
              label="Case"
            />
          </div>
          
          <TimeRangePicker
            value={timeRange}
            onChange={setTimeRange}
          />
          
          <button
            className="btn btn-secondary"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            Advanced
          </button>
          
          <button
            className="btn btn-primary"
            onClick={handleSearch}
          >
            Search
          </button>
        </div>
        
        {searchSuggestions && searchSuggestions.length > 0 && (
          <SearchSuggestions
            suggestions={searchSuggestions}
            onSelect={(suggestion) => setSearchQuery(suggestion)}
          />
        )}
      </div>
      
      {showAdvanced && (
        <div className="advanced-filters">
          <div className="filter-builder">
            <h4>Filters</h4>
            <FilterBuilder onAddFilter={addFilter} />
          </div>
          
          <div className="saved-filters">
            <h4>Saved Filters</h4>
            <SavedFiltersList
              filters={savedFilters}
              onLoadFilter={(filters) => setActiveFilters(filters)}
            />
          </div>
        </div>
      )}
      
      {activeFilters.length > 0 && (
        <div className="active-filters">
          <h5>Active Filters:</h5>
          <div className="filter-chips">
            {activeFilters.map((filter, index) => (
              <FilterChip
                key={index}
                filter={filter}
                onRemove={() => removeFilter(index)}
              />
            ))}
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => onSaveFilter('Custom Filter', activeFilters)}
            >
              Save Filter Set
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const FilterBuilder: React.FC<{
  onAddFilter: (filter: LogFilter) => void;
}> = ({ onAddFilter }) => {
  const [field, setField] = useState('level');
  const [operator, setOperator] = useState<LogFilter['operator']>('equals');
  const [value, setValue] = useState('');
  
  const filterFields = [
    { value: 'level', label: 'Log Level' },
    { value: 'service', label: 'Service' },
    { value: 'source', label: 'Source' },
    { value: 'message', label: 'Message' },
    { value: 'user_id', label: 'User ID' },
    { value: 'request_id', label: 'Request ID' },
    { value: 'trace_id', label: 'Trace ID' },
    { value: 'tags', label: 'Tags' }
  ];
  
  const operators = [
    { value: 'equals', label: 'Equals' },
    { value: 'contains', label: 'Contains' },
    { value: 'regex', label: 'Regex' },
    { value: 'range', label: 'Range' },
    { value: 'exists', label: 'Exists' }
  ];
  
  const handleAddFilter = () => {
    if (!field || !value) return;
    
    const filter: LogFilter = {
      field,
      operator,
      value,
      label: `${field} ${operator} ${value}`
    };
    
    onAddFilter(filter);
    setValue('');
  };
  
  return (
    <div className="filter-builder">
      <div className="filter-form">
        <Select
          value={field}
          onValueChange={setField}
          placeholder="Select field"
        >
          {filterFields.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </Select>
        
        <Select
          value={operator}
          onValueChange={setOperator}
          placeholder="Select operator"
        >
          {operators.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </Select>
        
        <input
          type="text"
          className="filter-value-input"
          placeholder="Filter value"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAddFilter()}
        />
        
        <button
          className="btn btn-sm btn-primary"
          onClick={handleAddFilter}
          disabled={!field || !value}
        >
          Add Filter
        </button>
      </div>
    </div>
  );
};
```

### 3. Log Analytics and Insights

#### Analytics Dashboard
```typescript
const LogAnalytics: React.FC<{
  timeRange: string;
  filters: LogFilter[];
}> = ({ timeRange, filters }) => {
  const { data: analyticsData } = useCovetPyRealTimeData(
    `/api/v1/logs/analytics?range=${timeRange}&filters=${JSON.stringify(filters)}`
  );
  
  return (
    <div className="log-analytics">
      <div className="analytics-overview">
        <AnalyticsCard
          title="Total Logs"
          value={analyticsData?.totalLogs}
          trend={analyticsData?.logsTrend}
          format="number"
        />
        
        <AnalyticsCard
          title="Error Rate"
          value={analyticsData?.errorRate}
          trend={analyticsData?.errorTrend}
          format="percentage"
          threshold={{ warning: 5, critical: 10 }}
        />
        
        <AnalyticsCard
          title="Top Error"
          value={analyticsData?.topError?.message}
          subValue={`${analyticsData?.topError?.count} occurrences`}
          format="text"
        />
        
        <AnalyticsCard
          title="Avg Log Rate"
          value={analyticsData?.avgLogRate}
          unit="logs/sec"
          trend={analyticsData?.rateTrend}
          format="number"
        />
      </div>
      
      <div className="analytics-charts">
        <div className="chart-container">
          <LogVolumeChart
            data={analyticsData?.volumeData}
            timeRange={timeRange}
          />
        </div>
        
        <div className="chart-container">
          <ErrorDistributionChart
            data={analyticsData?.errorDistribution}
          />
        </div>
        
        <div className="chart-container">
          <ServiceLogDistribution
            data={analyticsData?.serviceDistribution}
          />
        </div>
        
        <div className="chart-container">
          <LogLevelBreakdown
            data={analyticsData?.levelBreakdown}
          />
        </div>
      </div>
      
      <div className="insights-section">
        <h4>Log Insights</h4>
        <LogInsights insights={analyticsData?.insights || []} />
      </div>
    </div>
  );
};

const LogInsights: React.FC<{
  insights: LogInsight[];
}> = ({ insights }) => {
  return (
    <div className="log-insights">
      {insights.map((insight, index) => (
        <div key={index} className={`insight insight-${insight.type}`}>
          <div className="insight-header">
            <InsightIcon type={insight.type} />
            <span className="insight-title">{insight.title}</span>
            <span className="insight-confidence">{insight.confidence}% confidence</span>
          </div>
          
          <div className="insight-description">
            {insight.description}
          </div>
          
          {insight.actions && (
            <div className="insight-actions">
              {insight.actions.map((action, actionIndex) => (
                <button
                  key={actionIndex}
                  className="btn btn-sm btn-secondary"
                  onClick={() => action.handler()}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
```

### 4. Log Context and Correlation

#### Log Context Viewer
```typescript
const LogContextViewer: React.FC<{
  selectedLog: LogEntry | null;
  onClose: () => void;
}> = ({ selectedLog, onClose }) => {
  const [contextRange, setContextRange] = useState('5m');
  const [correlationMode, setCorrelationMode] = useState<'trace' | 'request' | 'user'>('trace');
  
  const { data: contextLogs } = useCovetPyRealTimeData(
    selectedLog 
      ? `/api/v1/logs/${selectedLog.id}/context?range=${contextRange}&mode=${correlationMode}`
      : null
  );
  
  if (!selectedLog) return null;
  
  return (
    <Modal isOpen={!!selectedLog} onClose={onClose} size="xl">
      <div className="log-context-viewer">
        <div className="context-header">
          <h3>Log Context</h3>
          <div className="context-controls">
            <Select value={contextRange} onValueChange={setContextRange}>
              <SelectItem value="1m">1 minute</SelectItem>
              <SelectItem value="5m">5 minutes</SelectItem>
              <SelectItem value="15m">15 minutes</SelectItem>
              <SelectItem value="1h">1 hour</SelectItem>
            </Select>
            
            <Select value={correlationMode} onValueChange={setCorrelationMode}>
              <SelectItem value="trace">By Trace ID</SelectItem>
              <SelectItem value="request">By Request ID</SelectItem>
              <SelectItem value="user">By User ID</SelectItem>
            </Select>
          </div>
        </div>
        
        <div className="context-content">
          <div className="selected-log">
            <h4>Selected Log</h4>
            <LogEntry
              log={selectedLog}
              onClick={() => {}}
              searchQuery=""
            />
          </div>
          
          <div className="context-timeline">
            <h4>Related Logs</h4>
            <LogTimeline
              logs={contextLogs?.relatedLogs || []}
              selectedLog={selectedLog}
              correlationMode={correlationMode}
            />
          </div>
          
          <div className="correlation-analysis">
            <h4>Correlation Analysis</h4>
            <CorrelationInsights
              selectedLog={selectedLog}
              relatedLogs={contextLogs?.relatedLogs || []}
              correlationMode={correlationMode}
            />
          </div>
        </div>
      </div>
    </Modal>
  );
};
```

## Real-Time Data Integration

### Log Streaming API
```typescript
// Log viewer API endpoints - NO MOCK DATA
const LOG_API_ENDPOINTS = {
  // Log streaming and search
  STREAM_LOGS: '/ws/logs',
  SEARCH_LOGS: '/api/v1/logs/search',
  GET_LOG_CONTEXT: '/api/v1/logs/:id/context',
  
  // Analytics and insights
  LOG_ANALYTICS: '/api/v1/logs/analytics',
  LOG_INSIGHTS: '/api/v1/logs/insights',
  
  // Filters and saved searches
  SAVED_FILTERS: '/api/v1/logs/filters',
  SAVE_FILTER: '/api/v1/logs/filters',
  SEARCH_SUGGESTIONS: '/api/v1/logs/suggest',
  
  // Export and utilities
  EXPORT_LOGS: '/api/v1/logs/export',
  LOG_FIELDS: '/api/v1/logs/fields'
} as const;

// Log streaming WebSocket implementation
class LogStreamingService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect(filters: LogFilter[], searchQuery: string, onMessage: (log: LogEntry) => void) {
    const wsUrl = new URL('/ws/logs', 'wss://api.covet.local');
    
    if (searchQuery) wsUrl.searchParams.set('search', searchQuery);
    if (filters.length > 0) {
      wsUrl.searchParams.set('filters', JSON.stringify(filters));
    }
    
    this.ws = new WebSocket(wsUrl.toString());
    
    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      console.log('Log stream connected');
    };
    
    this.ws.onmessage = (event) => {
      const logEntry = JSON.parse(event.data);
      onMessage(logEntry);
    };
    
    this.ws.onclose = () => {
      this.handleReconnect(filters, searchQuery, onMessage);
    };
  }
  
  private handleReconnect(filters: LogFilter[], searchQuery: string, onMessage: (log: LogEntry) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        this.connect(filters, searchQuery, onMessage);
      }, Math.pow(2, this.reconnectAttempts) * 1000);
    }
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
interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL';
  service: string;
  source: string;
  message: string;
  metadata?: Record<string, any>;
  traceId?: string;
  spanId?: string;
  userId?: string;
  requestId?: string;
  tags: string[];
}

interface LogAnalytics {
  totalLogs: number;
  errorRate: number;
  avgLogRate: number;
  topError: {
    message: string;
    count: number;
  };
  volumeData: TimeSeriesData[];
  errorDistribution: DistributionData[];
  serviceDistribution: DistributionData[];
  levelBreakdown: DistributionData[];
  insights: LogInsight[];
}

interface LogInsight {
  type: 'error_spike' | 'new_error' | 'performance_degradation' | 'unusual_pattern';
  title: string;
  description: string;
  confidence: number;
  actions?: Array<{
    label: string;
    handler: () => void;
  }>;
}
```

This Real-Time Log Viewer provides comprehensive log analysis capabilities for CovetPy applications, enabling efficient debugging, monitoring, and system analysis through advanced search, filtering, and real-time streaming capabilities.