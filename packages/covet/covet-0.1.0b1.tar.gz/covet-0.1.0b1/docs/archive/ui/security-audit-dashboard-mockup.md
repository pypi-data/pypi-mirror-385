# Security Audit Dashboard - UI Mockup

## Overview

The Security Audit Dashboard provides real-time monitoring of security events, threat detection, vulnerability scanning, and access control monitoring for the CovetPy system. All data is sourced from live security APIs with no mock data.

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           Security Audit Dashboard                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│ │ Threat Level │ │ Active Alerts│ │Failed Logins │ │ Blocked IPs  │ │ Scan Status │ │
│ │              │ │              │ │              │ │              │ │             │ │
│ │   🔴 HIGH    │ │      23      │ │     156      │ │     89       │ │ ✅ Clean    │ │
│ │              │ │   ▲ +5 new   │ │  ▲ +12/hr    │ │  ▲ +3 new    │ │ 99.7% Safe │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ ┌─────────────────────────────────────────┐ │
│ │         Security Events Timeline    │ │           Threat Analysis               │ │
│ │                                     │ │                                         │ │
│ │ 🔴 CRITICAL: SQL Injection Attempt │ │ ┌─────────────────────────────────────┐ │ │
│ │    Source: 192.168.1.100           │ │ │         Top Threat Types            │ │ │
│ │    Time: 14:23:45                  │ │ │                                     │ │ │
│ │                                     │ │ │ • Brute Force     ████████  45%    │ │ │
│ │ 🟡 WARNING: Multiple Failed Logins  │ │ │ • SQL Injection   █████     25%    │ │ │
│ │    User: admin@company.com          │ │ │ • XSS Attempts    ███       15%    │ │ │
│ │    Time: 14:20:12                  │ │ │ • CSRF            ██        10%    │ │ │
│ │                                     │ │ │ • Other           █         5%    │ │ │
│ │ 🟢 INFO: User Session Created       │ │ │                                     │ │ │
│ │    User: john.doe@company.com       │ │ └─────────────────────────────────────┘ │ │
│ │    Time: 14:15:30                  │ │                                         │ │
│ │                                     │ │ ┌─────────────────────────────────────┐ │ │
│ │ [Live Stream] 🔴 ●                  │ │ │        Attack Sources               │ │ │
│ │                                     │ │ │                                     │ │ │
│ └─────────────────────────────────────┘ │ │ 🌍 Geographic Distribution          │ │ │
│                                         │ │    Russia:      23 attacks         │ │ │
│                                         │ │    China:       18 attacks         │ │ │
│                                         │ │    USA:         12 attacks         │ │ │
│                                         │ │    Unknown:      8 attacks         │ │ │
│                                         │ └─────────────────────────────────────┘ │ │
│                                         └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ ┌─────────────────────────────────────────┐ │
│ │         Access Control Monitor      │ │        Vulnerability Scanner            │ │
│ │                                     │ │                                         │ │
│ │ 👤 Active Sessions: 234             │ │ 🔍 Last Scan: 2 hours ago              │ │
│ │ 🔑 Failed Authentications: 89       │ │                                         │ │
│ │ 🚫 Blocked Attempts: 156            │ │ Severity Distribution:                  │ │
│ │ ⏰ Avg Session Duration: 2h 15m     │ │                                         │ │
│ │                                     │ │ Critical:  ⚠️  2 vulnerabilities      │ │
│ │ Recent Activity:                    │ │ High:      🟡  7 vulnerabilities      │ │
│ │                                     │ │ Medium:    🔵 15 vulnerabilities      │ │
│ │ ✅ john.doe logged in              │ │ Low:       🟢 23 vulnerabilities      │ │
│ │ ❌ admin login failed (3rd attempt) │ │ Info:      ℹ️  12 informational       │ │
│ │ 🚫 192.168.1.50 blocked            │ │                                         │ │
│ │ ✅ API key validated                │ │ 📊 Trend: ▼ 12% fewer since last week │ │
│ │                                     │ │                                         │ │
│ │ [View All Sessions]                 │ │ [Start New Scan] [View Report]         │ │
│ └─────────────────────────────────────┘ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│ │                            Security Audit Log Viewer                           │ │
│ │                                                                                 │ │
│ │ [🔍 Search] [📅 Time Range: Last 24h] [⚠️ Severity: All] [🏷️ Category: All]  │ │
│ │                                                                                 │ │
│ │ 2024-01-15 14:23:45 [CRITICAL] SQL injection attempt blocked                  │ │
│ │ │ Source: 192.168.1.100:45231 → Target: /api/v1/users                        │ │
│ │ │ Pattern: UNION SELECT * FROM users WHERE 1=1--                             │ │
│ │ │ Action: Request blocked, IP temporarily banned                              │ │
│ │                                                                                 │ │
│ │ 2024-01-15 14:20:12 [WARNING] Repeated authentication failures                │ │
│ │ │ User: admin@company.com                                                     │ │
│ │ │ Attempts: 5 failed logins in 10 minutes                                    │ │
│ │ │ Action: Account temporarily locked                                          │ │
│ │                                                                                 │ │
│ │ 2024-01-15 14:18:30 [INFO] Rate limiting activated                           │ │
│ │ │ Endpoint: /api/v1/data                                                      │ │
│ │ │ Client: 10.0.1.23                                                          │ │
│ │ │ Rate: 1000 requests/minute exceeded                                         │ │
│ │                                                                                 │ │
│ │ 2024-01-15 14:15:45 [INFO] Certificate validation successful                 │ │
│ │ │ Certificate: *.covet.local                                              │ │
│ │ │ Expiry: 2024-12-31 23:59:59                                               │ │
│ │ │ Status: Valid, 351 days remaining                                          │ │
│ │                                                                                 │ │
│ │ [📥 Export Logs] [⚙️ Configure Alerts] [🔄 Auto-Refresh: ON]                │ │
│ └─────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Specifications

### Threat Level Indicator
```typescript
interface ThreatLevelIndicatorProps {
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score: number; // 0-100
  lastUpdated: Date;
  endpoint: '/api/v1/security/threat-level';
}

// Real-time connection to threat assessment API
const ThreatLevelIndicator: React.FC<ThreatLevelIndicatorProps> = ({ endpoint }) => {
  const { data: threatData } = useCovetPyRealTimeData(endpoint);
  
  const getColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'text-success';
      case 'MEDIUM': return 'text-warning';
      case 'HIGH': return 'text-destructive';
      case 'CRITICAL': return 'text-red-600 animate-pulse';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <MetricCard
      title="Threat Level"
      value={threatData?.level || 'UNKNOWN'}
      className={cn(
        'border-l-4',
        threatData?.level === 'CRITICAL' && 'border-l-red-600',
        threatData?.level === 'HIGH' && 'border-l-destructive',
        threatData?.level === 'MEDIUM' && 'border-l-warning',
        threatData?.level === 'LOW' && 'border-l-success'
      )}
      subMetrics={[
        { label: 'Score', value: threatData?.score || 0, unit: '/100' },
        { label: 'Updated', value: formatRelativeTime(threatData?.lastUpdated) }
      ]}
      realTimeEndpoint="/ws/security/threat-level"
    />
  );
};
```

### Security Events Timeline
```typescript
interface SecurityEvent {
  id: string;
  timestamp: Date;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  type: string;
  message: string;
  source?: string;
  target?: string;
  user?: string;
  metadata: Record<string, any>;
}

const SecurityEventsTimeline: React.FC = () => {
  const { data: events } = useCovetPyRealTimeData('/api/v1/security/events');
  const [autoScroll, setAutoScroll] = useState(true);
  
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Security Events</CardTitle>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm">Live Stream</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAutoScroll(!autoScroll)}
            >
              Auto-scroll: {autoScroll ? 'ON' : 'OFF'}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {events?.map((event: SecurityEvent) => (
            <SecurityEventItem key={event.id} event={event} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

const SecurityEventItem: React.FC<{ event: SecurityEvent }> = ({ event }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return '🔴';
      case 'WARNING': return '🟡';
      case 'INFO': return '🟢';
      default: return '⚪';
    }
  };

  return (
    <div className={cn(
      'p-3 rounded-lg border-l-4',
      event.severity === 'CRITICAL' && 'border-l-red-600 bg-red-50',
      event.severity === 'WARNING' && 'border-l-warning bg-warning-50',
      event.severity === 'INFO' && 'border-l-success bg-success-50'
    )}>
      <div className="flex items-start gap-3">
        <span className="text-lg">{getSeverityIcon(event.severity)}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium">{event.severity}:</span>
            <span>{event.message}</span>
          </div>
          
          {(event.source || event.user) && (
            <div className="text-sm text-muted-foreground space-x-4">
              {event.source && <span>Source: {event.source}</span>}
              {event.user && <span>User: {event.user}</span>}
            </div>
          )}
          
          <div className="text-xs text-muted-foreground mt-1">
            {formatTimestamp(event.timestamp)}
          </div>
        </div>
      </div>
    </div>
  );
};
```

### Vulnerability Scanner Dashboard
```typescript
interface VulnerabilityReport {
  lastScan: Date;
  nextScan: Date;
  status: 'SCANNING' | 'COMPLETED' | 'FAILED';
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  trend: {
    change: number;
    direction: 'up' | 'down' | 'stable';
  };
}

const VulnerabilityScanner: React.FC = () => {
  const { data: scanReport } = useCovetPyRealTimeData('/api/v1/security/vulnerabilities');
  const [scanning, setScanning] = useState(false);
  
  const startScan = async () => {
    setScanning(true);
    try {
      await fetch('/api/v1/security/scan', { method: 'POST' });
    } catch (error) {
      console.error('Failed to start scan:', error);
    } finally {
      setScanning(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Vulnerability Scanner
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={startScan}
              disabled={scanning}
              loading={scanning}
            >
              Start Scan
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open('/security/report', '_blank')}
            >
              View Report
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          <div className="flex justify-between text-sm">
            <span>Last Scan:</span>
            <span>{formatRelativeTime(scanReport?.lastScan)}</span>
          </div>
          
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Severity Distribution</h4>
            
            {Object.entries(scanReport?.summary || {}).map(([severity, count]) => (
              <div key={severity} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <SeverityIcon severity={severity} />
                  <span className="text-sm capitalize">{severity}:</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{count}</span>
                  <span className="text-xs text-muted-foreground">
                    vulnerabilities
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          {scanReport?.trend && (
            <div className="pt-3 border-t">
              <div className="flex items-center justify-between text-sm">
                <span>Trend:</span>
                <div className="flex items-center gap-1">
                  <TrendIcon direction={scanReport.trend.direction} />
                  <span className={cn(
                    scanReport.trend.direction === 'down' && 'text-success',
                    scanReport.trend.direction === 'up' && 'text-destructive'
                  )}>
                    {scanReport.trend.change}% since last week
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
```

### Access Control Monitor
```typescript
interface AccessMetrics {
  activeSessions: number;
  failedAuthentications: number;
  blockedAttempts: number;
  averageSessionDuration: number;
  recentActivity: AccessEvent[];
}

interface AccessEvent {
  id: string;
  type: 'LOGIN' | 'LOGOUT' | 'FAILED_LOGIN' | 'BLOCKED' | 'API_VALIDATION';
  user?: string;
  source?: string;
  timestamp: Date;
  success: boolean;
}

const AccessControlMonitor: React.FC = () => {
  const { data: accessMetrics } = useCovetPyRealTimeData('/api/v1/security/access');
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Access Control Monitor</CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <MetricCard
              title="Active Sessions"
              value={accessMetrics?.activeSessions || 0}
              format="number"
              size="sm"
              className="col-span-1"
            />
            <MetricCard
              title="Failed Logins"
              value={accessMetrics?.failedAuthentications || 0}
              format="number"
              size="sm"
              threshold={{ warning: 50, critical: 100 }}
              className="col-span-1"
            />
          </div>
          
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span>Blocked Attempts:</span>
              <span className="font-medium">{accessMetrics?.blockedAttempts || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Avg Session Duration:</span>
              <span className="font-medium">
                {formatDuration((accessMetrics?.averageSessionDuration || 0) * 1000)}
              </span>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-sm mb-2">Recent Activity</h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {accessMetrics?.recentActivity?.map((activity: AccessEvent) => (
                <AccessActivityItem key={activity.id} activity={activity} />
              ))}
            </div>
          </div>
          
          <Button variant="outline" size="sm" className="w-full">
            View All Sessions
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
```

### Security Audit Log Viewer
```typescript
interface SecurityLogEntry {
  id: string;
  timestamp: Date;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  category: string;
  message: string;
  details: Record<string, any>;
  source?: string;
  target?: string;
  user?: string;
}

const SecurityAuditLogViewer: React.FC = () => {
  const [filters, setFilters] = useState({
    search: '',
    timeRange: '24h',
    severity: 'ALL',
    category: 'ALL'
  });
  
  const { data: logs } = useCovetPyRealTimeData(
    `/api/v1/security/logs?${new URLSearchParams(filters)}`
  );
  
  const columns: ColumnDefinition<SecurityLogEntry>[] = [
    {
      key: 'timestamp',
      title: 'Time',
      render: (_, record) => formatTimestamp(record.timestamp),
      width: 150,
    },
    {
      key: 'severity',
      title: 'Severity',
      render: (severity) => (
        <SeverityBadge severity={severity} />
      ),
      width: 100,
    },
    {
      key: 'message',
      title: 'Event',
      render: (message, record) => (
        <div>
          <div className="font-medium">{message}</div>
          {record.details && (
            <div className="text-sm text-muted-foreground mt-1">
              {Object.entries(record.details).map(([key, value]) => (
                <div key={key}>
                  <strong>{key}:</strong> {String(value)}
                </div>
              ))}
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'source',
      title: 'Source',
      render: (source) => (
        <code className="text-xs bg-muted px-1 rounded">
          {source || 'N/A'}
        </code>
      ),
      width: 150,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Security Audit Log
          <div className="flex gap-2">
            <Button size="sm" variant="outline">
              Export Logs
            </Button>
            <Button size="sm" variant="outline">
              Configure Alerts
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="p-4 border-b">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Search logs..."
              className="flex-1 px-3 py-1 border rounded"
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            />
            
            <select
              className="px-3 py-1 border rounded"
              value={filters.timeRange}
              onChange={(e) => setFilters(prev => ({ ...prev, timeRange: e.target.value }))}
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
            
            <select
              className="px-3 py-1 border rounded"
              value={filters.severity}
              onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="WARNING">Warning</option>
              <option value="INFO">Info</option>
            </select>
          </div>
        </div>
        
        <DataTable
          data={logs || []}
          columns={columns}
          pagination={{ enabled: true, pageSize: 50 }}
          realTimeUpdates={true}
          className="border-0"
        />
      </CardContent>
    </Card>
  );
};
```

## API Integration Points

### Real-Time Security Data Endpoints
```typescript
// WebSocket connections for live security monitoring
const SECURITY_WEBSOCKET_ENDPOINTS = {
  THREAT_LEVEL: '/ws/security/threat-level',
  SECURITY_EVENTS: '/ws/security/events',
  ACCESS_CONTROL: '/ws/security/access',
  VULNERABILITY_SCAN: '/ws/security/vulnerabilities',
  AUDIT_LOGS: '/ws/security/logs',
} as const;

// REST API endpoints for security data
const SECURITY_API_ENDPOINTS = {
  THREAT_ASSESSMENT: '/api/v1/security/threat-level',
  SECURITY_EVENTS: '/api/v1/security/events',
  ACCESS_METRICS: '/api/v1/security/access',
  VULNERABILITY_REPORT: '/api/v1/security/vulnerabilities',
  AUDIT_LOGS: '/api/v1/security/logs',
  START_SCAN: '/api/v1/security/scan',
  BLOCK_IP: '/api/v1/security/block',
  UNBLOCK_IP: '/api/v1/security/unblock',
} as const;
```

### Data Models
```typescript
interface SecurityDashboardData {
  threatLevel: ThreatAssessment;
  activeAlerts: SecurityAlert[];
  recentEvents: SecurityEvent[];
  accessMetrics: AccessMetrics;
  vulnerabilityReport: VulnerabilityReport;
  auditLogs: SecurityLogEntry[];
}

interface ThreatAssessment {
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score: number;
  factors: string[];
  lastUpdated: Date;
  recommendations: string[];
}
```

This security audit dashboard design provides comprehensive real-time security monitoring with all components connected to live backend security APIs, ensuring accurate threat detection and incident response capabilities.