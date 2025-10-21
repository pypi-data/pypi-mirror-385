# Configuration Management UI

## Overview

The Configuration Management UI provides a comprehensive interface for managing CovetPy system settings, runtime configurations, and environment variables. This interface enables administrators to modify configurations safely with validation, rollback capabilities, and real-time impact assessment.

## Interface Architecture

### Configuration Dashboard Layout
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Configuration Management                             │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │   Config    │ │   Pending   │ │  Last       │ │    Environment      │ │
│ │ Sections:   │ │  Changes:   │ │  Deploy:    │ │  Production         │ │
│ │     12      │ │      3      │ │  2h ago     │ │  ████████████░░░░   │ │
│ │ ✓ Valid     │ │ ⚠ Review    │ │ ✓ Success   │ │  Config Health: 92% │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                     Configuration Explorer                          │ │
│ │ ┌─────────────────┐ ┌─────────────────────────────────────────────┐ │ │
│ │ │  Config Tree    │ │            Configuration Editor             │ │ │
│ │ │                 │ │                                             │ │ │
│ │ │ 📁 Core         │ │ server:                                     │ │ │
│ │ │ ├── ⚡ Server   │ │   host: "0.0.0.0"                          │ │ │
│ │ │ ├── 🔒 Security │ │   port: 8080                                │ │ │
│ │ │ ├── 📊 Metrics  │ │   workers: 8                                │ │ │
│ │ │ └── 🌐 Network  │ │   timeout: 30s                              │ │ │
│ │ │ 📁 Database     │ │                                             │ │ │
│ │ │ ├── 🔗 Pool     │ │ database:                                   │ │ │
│ │ │ ├── 🚀 Cache    │ │   host: "postgresql://..."                 │ │ │
│ │ │ └── 📈 Perf     │ │   pool_size: 20                             │ │ │
│ │ │ 📁 Logging      │ │   max_connections: 100                     │ │ │
│ │ │ ├── 📝 Levels   │ │                                             │ │ │
│ │ │ └── 📤 Output   │ │ ┌─ Validation ──────────────────────────┐  │ │ │
│ │ │                 │ │ │ ✓ Configuration is valid              │  │ │ │
│ │ │ [New Section]   │ │ │ ✓ All required fields present         │  │ │ │
│ │ └─────────────────┘ │ │ ⚠ Port 8080 may conflict with...     │  │ │ │
│ │                     │ │ └───────────────────────────────────────┘  │ │ │
│ │                     │ [Save Draft] [Validate] [Deploy]            │ │ │
│ │                     └─────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │      Deployment History         │ │        Change Impact            │ │
│ │                                 │ │                                 │ │
│ │ 🟢 v1.2.3 - 2h ago             │ │ Services Affected: 4            │ │
│ │ 🟢 v1.2.2 - 1d ago             │ │ ┌─────────────────────────────┐ │ │
│ │ 🔴 v1.2.1 - 3d ago (rolled back)│ │ │ • covet-core ⚠ restart  │ │ │
│ │ 🟢 v1.2.0 - 1w ago             │ │ │ • covet-db   ℹ reload   │ │ │
│ │                                 │ │ │ • covet-cache ✓ none    │ │ │
│ │ [View Full History]             │ │ │ • external-api   ⚠ restart │ │ │
│ │                                 │ │ └─────────────────────────────┘ │ │
│ │                                 │ │ Estimated Downtime: 15-30s     │ │ │
│ └─────────────────────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Configuration Explorer

#### Main Configuration Interface
```typescript
interface ConfigurationSection {
  id: string;
  name: string;
  description: string;
  icon: string;
  path: string[];
  settings: ConfigurationSetting[];
  validation: ValidationRule[];
  lastModified: Date;
  modifiedBy: string;
  version: string;
}

interface ConfigurationSetting {
  key: string;
  value: any;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'secret';
  description: string;
  required: boolean;
  validation: ValidationRule[];
  defaultValue?: any;
  environmentVariable?: string;
  restartRequired: boolean;
  securityLevel: 'public' | 'internal' | 'secret';
}

const ConfigurationExplorer: React.FC = () => {
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [pendingChanges, setPendingChanges] = useState<Map<string, any>>(new Map());
  const [validationResults, setValidationResults] = useState<ValidationResults>({});
  
  const { data: configData, loading } = useCovetPyRealTimeData('/api/v1/config');
  const { data: configSchema } = useCovetPyRealTimeData('/api/v1/config/schema');
  
  const handleConfigChange = (key: string, value: any) => {
    const newChanges = new Map(pendingChanges);
    newChanges.set(key, value);
    setPendingChanges(newChanges);
    
    // Real-time validation
    validateConfiguration(newChanges);
  };
  
  const validateConfiguration = async (changes: Map<string, any>) => {
    try {
      const changesObject = Object.fromEntries(changes);
      const response = await fetch('/api/v1/config/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(changesObject)
      });
      
      const results = await response.json();
      setValidationResults(results);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };
  
  return (
    <div className="configuration-explorer">
      <div className="config-header">
        <h2>Configuration Management</h2>
        <div className="config-actions">
          <EnvironmentSelector />
          <button
            className="btn btn-secondary"
            disabled={pendingChanges.size === 0}
            onClick={() => saveDraft(pendingChanges)}
          >
            <SaveIcon /> Save Draft
          </button>
          <button
            className="btn btn-primary"
            disabled={!isValidConfiguration(validationResults)}
            onClick={() => deployConfiguration(pendingChanges)}
          >
            <DeployIcon /> Deploy Changes
          </button>
        </div>
      </div>
      
      <div className="config-content">
        <div className="config-tree">
          <ConfigurationTree
            sections={configData?.sections || []}
            selectedSection={selectedSection}
            onSectionSelect={setSelectedSection}
            pendingChanges={pendingChanges}
            loading={loading}
          />
        </div>
        
        <div className="config-editor">
          {selectedSection ? (
            <ConfigurationEditor
              section={configData?.sections?.find(s => s.id === selectedSection)}
              schema={configSchema?.sections?.[selectedSection]}
              pendingChanges={pendingChanges}
              validationResults={validationResults}
              onChange={handleConfigChange}
            />
          ) : (
            <ConfigurationOverview
              sections={configData?.sections || []}
              pendingChanges={pendingChanges}
              validationResults={validationResults}
            />
          )}
        </div>
      </div>
    </div>
  );
};
```

#### Configuration Tree Component
```typescript
const ConfigurationTree: React.FC<{
  sections: ConfigurationSection[];
  selectedSection: string | null;
  onSectionSelect: (sectionId: string) => void;
  pendingChanges: Map<string, any>;
  loading: boolean;
}> = ({ sections, selectedSection, onSectionSelect, pendingChanges, loading }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  
  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };
  
  const hasChanges = (sectionId: string) => {
    return Array.from(pendingChanges.keys()).some(key => key.startsWith(`${sectionId}.`));
  };
  
  if (loading) {
    return <ConfigurationTreeSkeleton />;
  }
  
  const groupedSections = groupSectionsByCategory(sections);
  
  return (
    <div className="configuration-tree">
      <div className="tree-header">
        <h3>Configuration Sections</h3>
        <SearchInput
          placeholder="Search configurations..."
          onChange={(term) => {/* Filter sections */}}
        />
      </div>
      
      <div className="tree-content">
        {Object.entries(groupedSections).map(([category, categorySections]) => (
          <div key={category} className="config-category">
            <div
              className="category-header"
              onClick={() => toggleSection(category)}
            >
              <ChevronIcon 
                direction={expandedSections.has(category) ? 'down' : 'right'} 
              />
              <CategoryIcon category={category} />
              <span className="category-name">{category}</span>
              {categorySections.some(s => hasChanges(s.id)) && (
                <ChangeIndicator count={getChangeCount(categorySections, pendingChanges)} />
              )}
            </div>
            
            {expandedSections.has(category) && (
              <div className="category-sections">
                {categorySections.map((section) => (
                  <div
                    key={section.id}
                    className={`section-item ${selectedSection === section.id ? 'selected' : ''}`}
                    onClick={() => onSectionSelect(section.id)}
                  >
                    <SectionIcon icon={section.icon} />
                    <div className="section-info">
                      <span className="section-name">{section.name}</span>
                      <span className="section-description">{section.description}</span>
                    </div>
                    <div className="section-status">
                      {hasChanges(section.id) && <ChangesBadge />}
                      <LastModified timestamp={section.lastModified} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 2. Configuration Editor

#### Dynamic Configuration Form
```typescript
const ConfigurationEditor: React.FC<{
  section: ConfigurationSection;
  schema: ConfigurationSchema;
  pendingChanges: Map<string, any>;
  validationResults: ValidationResults;
  onChange: (key: string, value: any) => void;
}> = ({ section, schema, pendingChanges, validationResults, onChange }) => {
  const [editMode, setEditMode] = useState<'form' | 'yaml' | 'json'>('form');
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredSettings = useMemo(() => {
    return section.settings.filter(setting => 
      setting.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      setting.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [section.settings, searchTerm]);
  
  const currentValue = (key: string) => {
    const fullKey = `${section.id}.${key}`;
    return pendingChanges.has(fullKey) ? pendingChanges.get(fullKey) : getSetting(section, key)?.value;
  };
  
  const hasError = (key: string) => {
    const fullKey = `${section.id}.${key}`;
    return validationResults.errors?.[fullKey]?.length > 0;
  };
  
  const getErrors = (key: string) => {
    const fullKey = `${section.id}.${key}`;
    return validationResults.errors?.[fullKey] || [];
  };
  
  return (
    <div className="configuration-editor">
      <div className="editor-header">
        <div className="section-info">
          <SectionIcon icon={section.icon} size="lg" />
          <div>
            <h3>{section.name}</h3>
            <p className="section-description">{section.description}</p>
          </div>
        </div>
        
        <div className="editor-controls">
          <SearchInput
            placeholder="Search settings..."
            value={searchTerm}
            onChange={setSearchTerm}
          />
          <EditModeToggle
            mode={editMode}
            onChange={setEditMode}
          />
          <button className="btn btn-secondary">
            <HistoryIcon /> View History
          </button>
        </div>
      </div>
      
      <div className="editor-content">
        {editMode === 'form' ? (
          <ConfigurationForm
            settings={filteredSettings}
            schema={schema}
            currentValue={currentValue}
            hasError={hasError}
            getErrors={getErrors}
            onChange={(key, value) => onChange(`${section.id}.${key}`, value)}
          />
        ) : editMode === 'yaml' ? (
          <YAMLEditor
            value={convertToYAML(section)}
            onChange={(yaml) => handleYAMLChange(section.id, yaml)}
          />
        ) : (
          <JSONEditor
            value={convertToJSON(section)}
            onChange={(json) => handleJSONChange(section.id, json)}
          />
        )}
      </div>
      
      <div className="editor-footer">
        <ValidationSummary
          results={validationResults}
          sectionId={section.id}
        />
      </div>
    </div>
  );
};

const ConfigurationForm: React.FC<{
  settings: ConfigurationSetting[];
  schema: ConfigurationSchema;
  currentValue: (key: string) => any;
  hasError: (key: string) => boolean;
  getErrors: (key: string) => string[];
  onChange: (key: string, value: any) => void;
}> = ({ settings, schema, currentValue, hasError, getErrors, onChange }) => {
  const groupedSettings = groupSettingsByCategory(settings);
  
  return (
    <div className="configuration-form">
      {Object.entries(groupedSettings).map(([category, categorySettings]) => (
        <div key={category} className="settings-group">
          <h4 className="group-title">{category}</h4>
          
          <div className="settings-grid">
            {categorySettings.map((setting) => (
              <ConfigurationField
                key={setting.key}
                setting={setting}
                schema={schema?.properties?.[setting.key]}
                value={currentValue(setting.key)}
                error={hasError(setting.key)}
                errors={getErrors(setting.key)}
                onChange={(value) => onChange(setting.key, value)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

const ConfigurationField: React.FC<{
  setting: ConfigurationSetting;
  schema: PropertySchema;
  value: any;
  error: boolean;
  errors: string[];
  onChange: (value: any) => void;
}> = ({ setting, schema, value, error, errors, onChange }) => {
  const renderField = () => {
    switch (setting.type) {
      case 'string':
        return setting.securityLevel === 'secret' ? (
          <SecretInput
            value={value}
            onChange={onChange}
            placeholder={setting.description}
          />
        ) : (
          <TextInput
            value={value}
            onChange={onChange}
            placeholder={setting.description}
            validation={setting.validation}
          />
        );
        
      case 'number':
        return (
          <NumberInput
            value={value}
            onChange={onChange}
            min={schema?.minimum}
            max={schema?.maximum}
            step={schema?.step}
          />
        );
        
      case 'boolean':
        return (
          <Switch
            checked={value}
            onChange={onChange}
            label={setting.description}
          />
        );
        
      case 'array':
        return (
          <ArrayInput
            value={value}
            onChange={onChange}
            itemType={schema?.items?.type}
            addButtonText={`Add ${schema?.items?.title || 'Item'}`}
          />
        );
        
      case 'object':
        return (
          <ObjectInput
            value={value}
            onChange={onChange}
            schema={schema}
          />
        );
        
      default:
        return (
          <TextInput
            value={value}
            onChange={onChange}
            placeholder={setting.description}
          />
        );
    }
  };
  
  return (
    <div className={`configuration-field ${error ? 'error' : ''}`}>
      <label className="field-label">
        <span className="label-text">
          {setting.key}
          {setting.required && <RequiredIndicator />}
        </span>
        {setting.restartRequired && (
          <RestartRequiredBadge />
        )}
        {setting.environmentVariable && (
          <EnvironmentVariableBadge variable={setting.environmentVariable} />
        )}
      </label>
      
      <div className="field-input">
        {renderField()}
      </div>
      
      {setting.description && (
        <div className="field-description">
          {setting.description}
        </div>
      )}
      
      {setting.defaultValue !== undefined && (
        <div className="field-default">
          Default: <code>{JSON.stringify(setting.defaultValue)}</code>
        </div>
      )}
      
      {errors.length > 0 && (
        <div className="field-errors">
          {errors.map((error, index) => (
            <div key={index} className="error-message">
              <ErrorIcon />
              {error}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### 3. Change Management

#### Change Review and Deployment
```typescript
const ChangeManagementPanel: React.FC<{
  pendingChanges: Map<string, any>;
  validationResults: ValidationResults;
  onDeploy: () => void;
  onRollback: (version: string) => void;
}> = ({ pendingChanges, validationResults, onDeploy, onRollback }) => {
  const [deploymentMode, setDeploymentMode] = useState<'immediate' | 'scheduled'>('immediate');
  const [scheduledTime, setScheduledTime] = useState<Date | null>(null);
  const [confirmationRequired, setConfirmationRequired] = useState(false);
  
  const { data: impactAnalysis } = useCovetPyRealTimeData(
    '/api/v1/config/impact-analysis',
    {
      method: 'POST',
      body: JSON.stringify(Object.fromEntries(pendingChanges))
    }
  );
  
  const { data: deploymentHistory } = useCovetPyRealTimeData('/api/v1/config/deployments');
  
  return (
    <div className="change-management-panel">
      <Tabs defaultValue="changes">
        <TabsList>
          <TabsTrigger value="changes">Pending Changes</TabsTrigger>
          <TabsTrigger value="impact">Impact Analysis</TabsTrigger>
          <TabsTrigger value="history">Deployment History</TabsTrigger>
        </TabsList>
        
        <TabsContent value="changes">
          <PendingChangesView
            changes={pendingChanges}
            validationResults={validationResults}
          />
        </TabsContent>
        
        <TabsContent value="impact">
          <ImpactAnalysisView
            analysis={impactAnalysis}
            changes={pendingChanges}
          />
        </TabsContent>
        
        <TabsContent value="history">
          <DeploymentHistoryView
            history={deploymentHistory}
            onRollback={onRollback}
          />
        </TabsContent>
      </Tabs>
      
      <div className="deployment-controls">
        <div className="deployment-options">
          <RadioGroup
            value={deploymentMode}
            onValueChange={setDeploymentMode}
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="immediate" id="immediate" />
              <label htmlFor="immediate">Deploy Immediately</label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="scheduled" id="scheduled" />
              <label htmlFor="scheduled">Schedule Deployment</label>
            </div>
          </RadioGroup>
          
          {deploymentMode === 'scheduled' && (
            <DateTimePicker
              value={scheduledTime}
              onChange={setScheduledTime}
              minDate={new Date()}
            />
          )}
        </div>
        
        <div className="deployment-actions">
          <Checkbox
            id="confirmation"
            checked={confirmationRequired}
            onCheckedChange={setConfirmationRequired}
          />
          <label htmlFor="confirmation">
            I confirm that I have reviewed the impact analysis and am ready to deploy
          </label>
          
          <button
            className="btn btn-primary"
            disabled={!confirmationRequired || pendingChanges.size === 0}
            onClick={onDeploy}
          >
            <DeployIcon />
            {deploymentMode === 'immediate' ? 'Deploy Now' : 'Schedule Deployment'}
          </button>
        </div>
      </div>
    </div>
  );
};

const PendingChangesView: React.FC<{
  changes: Map<string, any>;
  validationResults: ValidationResults;
}> = ({ changes, validationResults }) => {
  return (
    <div className="pending-changes-view">
      <div className="changes-summary">
        <h4>Changes Summary</h4>
        <div className="summary-stats">
          <StatCard
            title="Total Changes"
            value={changes.size}
            icon={<EditIcon />}
          />
          <StatCard
            title="Validation Errors"
            value={Object.keys(validationResults.errors || {}).length}
            icon={<ErrorIcon />}
            color="error"
          />
          <StatCard
            title="Warnings"
            value={Object.keys(validationResults.warnings || {}).length}
            icon={<WarningIcon />}
            color="warning"
          />
        </div>
      </div>
      
      <div className="changes-list">
        {Array.from(changes.entries()).map(([key, value]) => (
          <ChangeItem
            key={key}
            configKey={key}
            newValue={value}
            originalValue={getOriginalValue(key)}
            validationResult={validationResults}
          />
        ))}
      </div>
    </div>
  );
};

const ImpactAnalysisView: React.FC<{
  analysis: ImpactAnalysis;
  changes: Map<string, any>;
}> = ({ analysis }) => {
  return (
    <div className="impact-analysis-view">
      <div className="impact-summary">
        <h4>Impact Analysis</h4>
        <div className="impact-metrics">
          <ImpactMetric
            title="Services Affected"
            value={analysis?.affectedServices?.length || 0}
            details={analysis?.affectedServices?.map(s => s.name)}
          />
          <ImpactMetric
            title="Restart Required"
            value={analysis?.servicesRequiringRestart?.length || 0}
            details={analysis?.servicesRequiringRestart}
            severity="warning"
          />
          <ImpactMetric
            title="Estimated Downtime"
            value={analysis?.estimatedDowntime || '0s'}
            severity={analysis?.estimatedDowntime > 0 ? 'error' : 'success'}
          />
        </div>
      </div>
      
      <div className="affected-services">
        <h5>Affected Services</h5>
        <ServiceImpactTable services={analysis?.serviceImpacts || []} />
      </div>
      
      <div className="deployment-risks">
        <h5>Deployment Risks</h5>
        <RiskAssessment risks={analysis?.risks || []} />
      </div>
    </div>
  );
};
```

### 4. Environment Management

#### Multi-Environment Configuration
```typescript
const EnvironmentManager: React.FC = () => {
  const [currentEnvironment, setCurrentEnvironment] = useState('production');
  const { data: environments } = useCovetPyRealTimeData('/api/v1/config/environments');
  const { data: environmentDiffs } = useCovetPyRealTimeData(
    `/api/v1/config/environments/${currentEnvironment}/diff`
  );
  
  return (
    <div className="environment-manager">
      <div className="environment-header">
        <h3>Environment Configuration</h3>
        <EnvironmentSelector
          environments={environments}
          current={currentEnvironment}
          onChange={setCurrentEnvironment}
        />
      </div>
      
      <div className="environment-content">
        <div className="environment-overview">
          <EnvironmentStatusCard
            environment={environments?.find(e => e.name === currentEnvironment)}
          />
        </div>
        
        <div className="environment-comparison">
          <h4>Configuration Differences</h4>
          <EnvironmentDiffView
            diffs={environmentDiffs}
            baseEnvironment="staging"
            targetEnvironment={currentEnvironment}
          />
        </div>
      </div>
    </div>
  );
};
```

## Real-Time Data Integration

### Configuration API Endpoints
```typescript
// Configuration management API endpoints - NO MOCK DATA
const CONFIG_API_ENDPOINTS = {
  // Core configuration
  GET_CONFIG: '/api/v1/config',
  UPDATE_CONFIG: '/api/v1/config',
  GET_SCHEMA: '/api/v1/config/schema',
  VALIDATE_CONFIG: '/api/v1/config/validate',
  
  // Environment management
  LIST_ENVIRONMENTS: '/api/v1/config/environments',
  GET_ENVIRONMENT: '/api/v1/config/environments/:env',
  ENVIRONMENT_DIFF: '/api/v1/config/environments/:env/diff',
  
  // Change management
  IMPACT_ANALYSIS: '/api/v1/config/impact-analysis',
  DEPLOYMENT_HISTORY: '/api/v1/config/deployments',
  DEPLOY_CONFIG: '/api/v1/config/deploy',
  ROLLBACK_CONFIG: '/api/v1/config/rollback/:version',
  
  // Drafts and versions
  SAVE_DRAFT: '/api/v1/config/drafts',
  LIST_DRAFTS: '/api/v1/config/drafts',
  GET_VERSION: '/api/v1/config/versions/:version'
} as const;

// WebSocket endpoints for real-time updates
const CONFIG_WEBSOCKET_ENDPOINTS = {
  CONFIG_CHANGES: '/ws/config/changes',
  VALIDATION_RESULTS: '/ws/config/validation',
  DEPLOYMENT_STATUS: '/ws/config/deployment'
} as const;
```

### Type Definitions
```typescript
interface Configuration {
  version: string;
  environment: string;
  sections: ConfigurationSection[];
  metadata: ConfigurationMetadata;
  lastModified: Date;
  modifiedBy: string;
}

interface ValidationResults {
  valid: boolean;
  errors: Record<string, string[]>;
  warnings: Record<string, string[]>;
  suggestions: Record<string, string[]>;
}

interface ImpactAnalysis {
  affectedServices: ServiceImpact[];
  servicesRequiringRestart: string[];
  estimatedDowntime: number;
  risks: DeploymentRisk[];
  rollbackPlan: RollbackStep[];
}

interface DeploymentHistory {
  deployments: Deployment[];
  totalCount: number;
  currentVersion: string;
}
```

This Configuration Management UI provides comprehensive tools for safely managing CovetPy system configurations with real-time validation, impact analysis, and deployment management capabilities.