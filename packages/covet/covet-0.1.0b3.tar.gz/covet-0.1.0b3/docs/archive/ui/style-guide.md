# CovetPy UI Style Guide

## Overview

This style guide provides comprehensive documentation for the CovetPy Admin UI component library. All components are designed to connect to real backend APIs, ensuring accurate and live data representation in enterprise environments.

## Design Principles

### 1. Real Data Integration
- **No Mock Data**: All components must connect to actual backend APIs
- **Live Updates**: Real-time data via WebSocket connections
- **Error Handling**: Graceful degradation when APIs are unavailable
- **Performance**: Optimized for high-frequency data updates

### 2. Enterprise Focus
- **Information Density**: Power users need comprehensive data views
- **Keyboard Navigation**: Full accessibility via keyboard shortcuts
- **Dark Mode**: Optimized for 24/7 monitoring environments
- **Responsive Design**: Desktop-first, mobile-capable

### 3. Consistency
- **Design Tokens**: Standardized colors, spacing, and typography
- **Component Patterns**: Reusable, predictable interface elements
- **Interaction Models**: Consistent behavior across all components

## Color System

### Primary Colors
```css
:root {
  /* Brand Colors */
  --covet-primary: #1565C0;
  --covet-primary-foreground: #FFFFFF;
  --covet-primary-dark: #0D47A1;
  --covet-primary-light: #E3F2FD;
  
  /* Status Colors */
  --covet-success: #2E7D32;
  --covet-success-foreground: #FFFFFF;
  --covet-warning: #F57C00;
  --covet-warning-foreground: #FFFFFF;
  --covet-error: #C62828;
  --covet-error-foreground: #FFFFFF;
  --covet-info: #1976D2;
  --covet-info-foreground: #FFFFFF;
  
  /* Performance Indicators */
  --covet-perf-excellent: #00C853;
  --covet-perf-good: #64DD17;
  --covet-perf-fair: #FFAB00;
  --covet-perf-poor: #FF3D00;
}
```

### Neutral Colors
```css
:root {
  /* Light Theme */
  --covet-background: #FFFFFF;
  --covet-foreground: #212121;
  --covet-muted: #F5F5F5;
  --covet-muted-foreground: #757575;
  --covet-border: #E0E0E0;
  --covet-input: #FFFFFF;
  --covet-ring: #1565C0;
  
  /* Dark Theme */
  --covet-dark-background: #121212;
  --covet-dark-foreground: #F0F0F0;
  --covet-dark-muted: #1E1E1E;
  --covet-dark-muted-foreground: #A0A0A0;
  --covet-dark-border: #2C2C2C;
  --covet-dark-input: #1E1E1E;
  --covet-dark-ring: #64B5F6;
}
```

## Typography

### Font System
```css
:root {
  --covet-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --covet-font-mono: 'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', monospace;
}
```

### Type Scale
```css
:root {
  --covet-text-xs: 0.75rem;    /* 12px */
  --covet-text-sm: 0.875rem;   /* 14px */
  --covet-text-base: 1rem;     /* 16px */
  --covet-text-lg: 1.125rem;   /* 18px */
  --covet-text-xl: 1.25rem;    /* 20px */
  --covet-text-2xl: 1.5rem;    /* 24px */
  --covet-text-3xl: 1.875rem;  /* 30px */
  --covet-text-4xl: 2.25rem;   /* 36px */
}
```

## Component Library

### Button Component

#### Usage
```tsx
import { Button } from '@covet/admin-ui';

// Basic button
<Button>Click me</Button>

// Button variants
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>

// Button sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>

// With icons and loading
<Button leftIcon={<PlusIcon />} loading={isLoading}>
  Create New
</Button>
```

#### Props
```typescript
interface ButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}
```

### Card Component

#### Usage
```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@covet/admin-ui';

<Card>
  <CardHeader>
    <CardTitle>System Metrics</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
</Card>

// Card variants
<Card variant="elevated" hover clickable>
  Interactive card content
</Card>
```

#### Props
```typescript
interface CardProps {
  variant?: 'default' | 'elevated' | 'outline' | 'filled' | 'gradient';
  padding?: 'none' | 'sm' | 'default' | 'lg';
  hover?: boolean;
  clickable?: boolean;
  children: React.ReactNode;
}
```

### MetricCard Component

#### Usage
```tsx
import { MetricCard } from '@covet/admin-ui';

<MetricCard
  title="Requests/Second"
  value={5234567}
  format="number"
  trend={{
    direction: 'up',
    percentage: 12.5,
    isPositive: true
  }}
  threshold={{
    warning: 4000000,
    critical: 3000000
  }}
  realTimeEndpoint="/ws/metrics/rps"
  subMetrics={[
    { label: 'Peak', value: 6000000 },
    { label: 'Avg', value: 4500000 }
  ]}
/>
```

#### Props
```typescript
interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  format?: 'number' | 'percentage' | 'bytes' | 'duration' | 'currency';
  trend?: TrendData;
  threshold?: { warning: number; critical: number };
  realTimeEndpoint?: string;
  subMetrics?: Array<{ label: string; value: number | string; unit?: string }>;
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  error?: string;
}
```

### DataTable Component

#### Usage
```tsx
import { DataTable } from '@covet/admin-ui';

const columns = [
  {
    key: 'name',
    title: 'Name',
    dataIndex: 'name',
    sortable: true,
  },
  {
    key: 'status',
    title: 'Status',
    render: (_, record) => (
      <StatusBadge status={record.status} />
    ),
  },
];

<DataTable
  data={routes}
  columns={columns}
  realTimeUpdates={true}
  pagination={{ enabled: true, pageSize: 25 }}
  selection={{ enabled: true }}
  exportOptions={{ csv: true, json: true }}
  onRowClick={handleRowClick}
/>
```

#### Props
```typescript
interface DataTableProps<T> {
  data: T[];
  columns: ColumnDefinition<T>[];
  loading?: boolean;
  pagination?: PaginationConfig;
  sorting?: { defaultSort?: SortConfig };
  filtering?: FilterConfig;
  selection?: SelectionConfig;
  realTimeUpdates?: boolean;
  exportOptions?: ExportConfig;
  onRowClick?: (row: T, index: number) => void;
  onBulkAction?: (action: string, rows: T[]) => void;
}
```

### PerformanceDashboard Component

#### Usage
```tsx
import { PerformanceDashboard } from '@covet/admin-ui';

<PerformanceDashboard
  timeRange="1h"
  autoRefresh={true}
  className="performance-overview"
/>
```

This dashboard automatically connects to multiple real-time endpoints:
- `/api/v1/metrics/system` - System metrics
- `/api/v1/alerts/performance` - Performance alerts
- `/ws/metrics/rps` - Real-time RPS updates
- `/ws/metrics/latency` - Real-time latency updates
- `/ws/connections/metrics` - Connection metrics
- `/ws/metrics/memory` - Memory utilization

### APIManagementInterface Component

#### Usage
```tsx
import { APIManagementInterface } from '@covet/admin-ui';

<APIManagementInterface />
```

This interface connects to:
- `/api/v1/routes` - Route definitions
- `/api/v1/routes/metrics` - Route performance metrics
- `/api/v1/health/routes` - Route health status
- `/ws/routes/*` - Real-time route updates

## Real-Time Data Integration

### WebSocket Connection Pattern
All components that display live data follow this pattern:

```tsx
import { useCovetPyRealTimeData } from '@covet/admin-ui';

const MyComponent: React.FC = () => {
  const { data, loading, error, isConnected } = useCovetPyRealTimeData('/api/v1/metrics');
  
  if (loading) return <ComponentSkeleton />;
  if (error) return <ErrorFallback error={error} />;
  
  return (
    <div>
      {isConnected && <LiveIndicator />}
      <ComponentContent data={data} />
    </div>
  );
};
```

### API Error Handling
```tsx
const ComponentWithErrorHandling: React.FC = () => {
  const { data, error } = useCovetPyRealTimeData('/api/v1/data');
  
  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent>
          <div className="flex items-center gap-2 text-destructive">
            <ErrorIcon />
            <span>Failed to load data: {error}</span>
          </div>
          <Button onClick={refresh} className="mt-2">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }
  
  return <NormalComponent data={data} />;
};
```

## Layout Patterns

### Dashboard Grid
```tsx
const DashboardLayout: React.FC = () => (
  <div className="covet-dashboard-grid">
    <MetricCard className="col-span-3" title="RPS" value={rps} />
    <MetricCard className="col-span-3" title="Latency" value={latency} />
    <MetricCard className="col-span-3" title="Memory" value={memory} />
    <MetricCard className="col-span-3" title="CPU" value={cpu} />
    
    <Card className="col-span-8">
      <PerformanceChart />
    </Card>
    <Card className="col-span-4">
      <SystemHealth />
    </Card>
    
    <Card className="col-span-12">
      <APIRoutes />
    </Card>
  </div>
);
```

### Responsive Breakpoints
```css
/* Mobile First Approach */
.covet-dashboard-grid {
  display: grid;
  gap: 1rem;
  padding: 1rem;
  
  /* Mobile: Single column */
  grid-template-columns: 1fr;
  
  /* Tablet: Two columns */
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    padding: 1.5rem;
  }
  
  /* Desktop: Twelve columns */
  @media (min-width: 1024px) {
    grid-template-columns: repeat(12, 1fr);
    max-width: 1440px;
    margin: 0 auto;
  }
  
  /* Large screens: Expanded */
  @media (min-width: 1680px) {
    grid-template-columns: repeat(16, 1fr);
    max-width: 1920px;
  }
}
```

## Accessibility Guidelines

### WCAG 2.1 AA Compliance

#### Color Contrast
- Normal text: 4.5:1 minimum ratio
- Large text (18pt+): 3:1 minimum ratio
- UI components: 3:1 minimum ratio

#### Keyboard Navigation
```tsx
const AccessibleComponent: React.FC = () => {
  return (
    <div
      role="region"
      aria-label="System metrics"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleActivate();
        }
      }}
    >
      <Button
        aria-label="Refresh system metrics"
        aria-describedby="refresh-help"
      >
        Refresh
      </Button>
      <div id="refresh-help" className="sr-only">
        Updates all system metrics from the server
      </div>
    </div>
  );
};
```

#### Screen Reader Support
```tsx
const MetricCardAccessible: React.FC = ({ title, value, trend }) => (
  <div role="region" aria-labelledby="metric-title">
    <h3 id="metric-title">{title}</h3>
    <div aria-live="polite" aria-atomic="true">
      <span className="sr-only">Current value:</span>
      {value}
      {trend && (
        <span className="sr-only">
          , trending {trend.direction} by {trend.percentage} percent
        </span>
      )}
    </div>
  </div>
);
```

### Focus Management
```tsx
const useKeyboardNavigation = () => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Tab navigation
      if (e.key === 'Tab') {
        // Custom tab order logic
      }
      
      // Arrow key navigation for grids
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        // Grid navigation logic
      }
      
      // Escape to close modals
      if (e.key === 'Escape') {
        // Close active modals
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
};
```

## Performance Optimization

### Component Loading States
```tsx
const PerformantComponent: React.FC = () => {
  const { data, loading } = useCovetPyRealTimeData('/api/v1/data');
  
  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-muted rounded w-1/4"></div>
        <div className="h-32 bg-muted rounded"></div>
        <div className="h-4 bg-muted rounded w-1/2"></div>
      </div>
    );
  }
  
  return <ActualComponent data={data} />;
};
```

### Virtualization for Large Lists
```tsx
import { FixedSizeList as List } from 'react-window';

const VirtualizedTable: React.FC<{ items: any[] }> = ({ items }) => (
  <List
    height={600}
    itemCount={items.length}
    itemSize={50}
    itemData={items}
  >
    {({ index, style, data }) => (
      <div style={style}>
        <TableRow data={data[index]} />
      </div>
    )}
  </List>
);
```

### Memoization Patterns
```tsx
const OptimizedComponent: React.FC<Props> = memo(({ data, config }) => {
  const processedData = useMemo(() => {
    return expensiveDataProcessing(data);
  }, [data]);
  
  const memoizedCallback = useCallback((id: string) => {
    // Expensive operation
  }, [dependencies]);
  
  return <ComponentContent data={processedData} onAction={memoizedCallback} />;
});
```

## Testing Guidelines

### Component Testing
```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { MetricCard } from '../MetricCard';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.get('/api/v1/metrics/rps', (req, res, ctx) => {
    return res(ctx.json({ value: 5000, timestamp: Date.now() }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('MetricCard displays real-time data', async () => {
  render(
    <MetricCard
      title="RPS"
      value={5000}
      realTimeEndpoint="/api/v1/metrics/rps"
    />
  );
  
  expect(screen.getByText('RPS')).toBeInTheDocument();
  expect(screen.getByText('5,000')).toBeInTheDocument();
  
  // Test real-time updates
  await waitFor(() => {
    expect(screen.getByText('Live')).toBeInTheDocument();
  });
});
```

### Accessibility Testing
```tsx
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('Component has no accessibility violations', async () => {
  const { container } = render(<PerformanceDashboard />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Progressive Enhancement
```tsx
const ProgressiveComponent: React.FC = () => {
  const [supportsWebSocket, setSupportsWebSocket] = useState(
    typeof WebSocket !== 'undefined'
  );
  
  return (
    <div>
      {supportsWebSocket ? (
        <RealTimeComponent />
      ) : (
        <PollingFallbackComponent />
      )}
    </div>
  );
};
```

## Development Workflow

### Component Development
1. Design component with real API integration in mind
2. Create TypeScript interfaces matching API responses
3. Implement with accessibility from the start
4. Add comprehensive error handling
5. Include loading and empty states
6. Write tests with real API mocking
7. Document usage patterns

### Code Review Checklist
- [ ] Component connects to real backend APIs
- [ ] No mock or placeholder data used
- [ ] Proper error handling implemented
- [ ] Loading states provided
- [ ] Accessibility attributes included
- [ ] Performance optimized (memoization, virtualization)
- [ ] Tests cover real-time data scenarios
- [ ] Documentation updated

This style guide ensures consistent, accessible, and performant components that provide real value in enterprise monitoring environments.