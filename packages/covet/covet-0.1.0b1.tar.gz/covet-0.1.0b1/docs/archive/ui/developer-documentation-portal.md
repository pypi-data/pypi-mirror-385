# Developer Documentation Portal

## Overview

The Developer Documentation Portal provides a comprehensive, interactive platform for developers to explore CovetPy APIs, view real-time system documentation, and test endpoints directly within the interface. This portal integrates with live backend systems to provide accurate, up-to-date information.

## Portal Architecture

### Main Layout Structure
```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Developer Documentation Portal                     │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌─────────────────────────────────────────────────────┐ │
│ │              │ │                                                     │ │
│ │   Navigation │ │                Content Area                        │ │
│ │              │ │                                                     │ │
│ │ • Quick Start│ │ ┌─────────────────┐ ┌─────────────────────────────┐ │ │
│ │ • API Ref    │ │ │                 │ │                             │ │ │
│ │ • Guides     │ │ │   API Explorer  │ │      Live Examples         │ │ │
│ │ • Examples   │ │ │                 │ │                             │ │ │
│ │ • SDKs       │ │ │ GET /api/v1/... │ │  curl -X GET ...            │ │ │
│ │ • Changelog  │ │ │                 │ │  Response: 200 OK           │ │ │
│ │              │ │ │ [Try it now]    │ │  {...}                      │ │ │
│ │              │ │ └─────────────────┘ └─────────────────────────────┘ │ │
│ │              │ │                                                     │ │
│ │              │ │ ┌───────────────────────────────────────────────────┐ │ │
│ │              │ │ │            Interactive Playground               │ │ │
│ │              │ │ │                                                 │ │ │
│ │              │ │ │ [Code Editor]  |  [Live Preview]  |  [Output]  │ │ │
│ │              │ │ └───────────────────────────────────────────────────┘ │ │
│ └──────────────┘ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Interactive API Explorer

### API Explorer Component
```typescript
interface APIExplorerProps {
  apiSpec: OpenAPISpec;
  baseURL: string;
  authToken?: string;
}

const APIExplorer: React.FC<APIExplorerProps> = ({ apiSpec, baseURL, authToken }) => {
  const [selectedEndpoint, setSelectedEndpoint] = useState<APIEndpoint | null>(null);
  const [requestHistory, setRequestHistory] = useState<APIRequest[]>([]);
  const [environments, setEnvironments] = useState<Environment[]>([]);
  
  // Real-time API spec updates
  const { data: liveSpec } = useCovetPyRealTimeData('/api/v1/spec');
  
  return (
    <div className="api-explorer">
      <div className="explorer-header">
        <h2>API Explorer</h2>
        <div className="explorer-controls">
          <EnvironmentSelector 
            environments={environments}
            selected={selectedEnvironment}
            onChange={setSelectedEnvironment}
          />
          <AuthenticationPanel 
            authToken={authToken}
            onAuthChange={setAuthToken}
          />
        </div>
      </div>
      
      <div className="explorer-content">
        <div className="endpoints-sidebar">
          <div className="endpoints-search">
            <SearchInput 
              placeholder="Search endpoints..."
              onChange={handleEndpointSearch}
            />
          </div>
          
          <div className="endpoints-tree">
            {Object.entries(groupEndpointsByTag(liveSpec?.paths)).map(([tag, endpoints]) => (
              <EndpointGroup
                key={tag}
                tag={tag}
                endpoints={endpoints}
                selectedEndpoint={selectedEndpoint}
                onEndpointSelect={setSelectedEndpoint}
              />
            ))}
          </div>
        </div>
        
        <div className="endpoint-details">
          {selectedEndpoint ? (
            <EndpointDetailPanel
              endpoint={selectedEndpoint}
              baseURL={baseURL}
              authToken={authToken}
              onRequestSent={handleRequestSent}
            />
          ) : (
            <div className="no-endpoint-selected">
              <h3>Select an endpoint to explore</h3>
              <p>Choose from the list on the left to see details and test the API</p>
            </div>
          )}
        </div>
        
        <div className="request-history-panel">
          <h3>Request History</h3>
          <RequestHistory 
            requests={requestHistory}
            onRequestReplay={handleRequestReplay}
            onRequestDelete={handleRequestDelete}
          />
        </div>
      </div>
    </div>
  );
};
```

### Endpoint Detail Panel
```typescript
interface EndpointDetailPanelProps {
  endpoint: APIEndpoint;
  baseURL: string;
  authToken?: string;
  onRequestSent: (request: APIRequest, response: APIResponse) => void;
}

const EndpointDetailPanel: React.FC<EndpointDetailPanelProps> = ({ 
  endpoint, 
  baseURL, 
  authToken,
  onRequestSent 
}) => {
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [requestBody, setRequestBody] = useState<string>('');
  const [headers, setHeaders] = useState<Record<string, string>>({});
  const [response, setResponse] = useState<APIResponse | null>(null);
  const [loading, setLoading] = useState(false);
  
  const handleSendRequest = async () => {
    setLoading(true);
    
    try {
      const request: APIRequest = {
        method: endpoint.method,
        url: constructURL(baseURL, endpoint.path, parameters),
        headers: { ...headers, Authorization: authToken ? `Bearer ${authToken}` : undefined },
        body: requestBody || undefined,
        timestamp: new Date()
      };
      
      const response = await sendAPIRequest(request);
      setResponse(response);
      onRequestSent(request, response);
    } catch (error) {
      setResponse({
        status: 0,
        statusText: 'Request Failed',
        data: { error: error.message },
        headers: {},
        timestamp: new Date(),
        duration: 0
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="endpoint-detail-panel">
      <div className="endpoint-header">
        <div className="endpoint-method-path">
          <span className={`method-badge method-${endpoint.method.toLowerCase()}`}>
            {endpoint.method}
          </span>
          <code className="endpoint-path">{endpoint.path}</code>
        </div>
        
        <div className="endpoint-actions">
          <Button 
            onClick={handleSendRequest}
            disabled={loading}
            className="try-it-button"
          >
            {loading ? <Spinner size="sm" /> : 'Try it now'}
          </Button>
          <Button 
            variant="secondary"
            onClick={() => generateCodeSample(endpoint, parameters)}
          >
            Generate Code
          </Button>
        </div>
      </div>
      
      <div className="endpoint-description">
        <h3>{endpoint.summary}</h3>
        <p>{endpoint.description}</p>
        
        {endpoint.deprecated && (
          <Alert variant="warning">
            <WarningIcon /> This endpoint is deprecated. Consider using alternative endpoints.
          </Alert>
        )}
      </div>
      
      <Tabs defaultValue="request">
        <TabsList>
          <TabsTrigger value="request">Request</TabsTrigger>
          <TabsTrigger value="response">Response</TabsTrigger>
          <TabsTrigger value="examples">Examples</TabsTrigger>
          <TabsTrigger value="schema">Schema</TabsTrigger>
        </TabsList>
        
        <TabsContent value="request">
          <div className="request-builder">
            {endpoint.parameters?.length > 0 && (
              <div className="parameters-section">
                <h4>Parameters</h4>
                <ParametersForm 
                  parameters={endpoint.parameters}
                  values={parameters}
                  onChange={setParameters}
                />
              </div>
            )}
            
            {endpoint.requestBody && (
              <div className="request-body-section">
                <h4>Request Body</h4>
                <RequestBodyEditor
                  schema={endpoint.requestBody.schema}
                  value={requestBody}
                  onChange={setRequestBody}
                  contentType="application/json"
                />
              </div>
            )}
            
            <div className="headers-section">
              <h4>Headers</h4>
              <HeadersEditor 
                headers={headers}
                onChange={setHeaders}
                defaultHeaders={getDefaultHeaders(authToken)}
              />
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="response">
          <div className="response-viewer">
            {response ? (
              <ResponsePanel response={response} />
            ) : (
              <div className="no-response">
                <p>Send a request to see the response</p>
              </div>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="examples">
          <ExamplesPanel 
            endpoint={endpoint}
            onExampleSelect={handleExampleSelect}
          />
        </TabsContent>
        
        <TabsContent value="schema">
          <SchemaViewer schema={endpoint.responses} />
        </TabsContent>
      </Tabs>
    </div>
  );
};
```

### Code Generation Panel
```typescript
interface CodeGeneratorProps {
  endpoint: APIEndpoint;
  parameters: Record<string, any>;
  requestBody?: string;
  headers: Record<string, string>;
  authToken?: string;
}

const CodeGenerator: React.FC<CodeGeneratorProps> = ({ 
  endpoint, 
  parameters, 
  requestBody,
  headers,
  authToken 
}) => {
  const [selectedLanguage, setSelectedLanguage] = useState<CodeLanguage>('curl');
  const [generatedCode, setGeneratedCode] = useState<string>('');
  
  const supportedLanguages: CodeLanguage[] = [
    'curl', 'javascript', 'python', 'go', 'java', 'php', 'ruby', 'swift'
  ];
  
  useEffect(() => {
    const code = generateCodeForLanguage({
      language: selectedLanguage,
      endpoint,
      parameters,
      requestBody,
      headers,
      authToken
    });
    setGeneratedCode(code);
  }, [selectedLanguage, endpoint, parameters, requestBody, headers, authToken]);
  
  return (
    <div className="code-generator">
      <div className="code-generator-header">
        <h3>Code Examples</h3>
        <div className="language-selector">
          <LanguageDropdown 
            languages={supportedLanguages}
            selected={selectedLanguage}
            onChange={setSelectedLanguage}
          />
        </div>
      </div>
      
      <div className="code-editor-container">
        <MonacoEditor
          language={getMonacoLanguage(selectedLanguage)}
          value={generatedCode}
          options={{
            readOnly: true,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            theme: 'vs-dark'
          }}
          height="400px"
        />
      </div>
      
      <div className="code-actions">
        <Button onClick={() => copyToClipboard(generatedCode)}>
          <CopyIcon /> Copy Code
        </Button>
        <Button 
          variant="secondary"
          onClick={() => downloadCode(generatedCode, selectedLanguage)}
        >
          <DownloadIcon /> Download
        </Button>
      </div>
    </div>
  );
};

// Code generation functions for different languages
const generateCodeForLanguage = ({
  language,
  endpoint,
  parameters,
  requestBody,
  headers,
  authToken
}: CodeGenParams): string => {
  const url = constructURL('https://api.covet.local', endpoint.path, parameters);
  
  switch (language) {
    case 'curl':
      return generateCurlCode(endpoint.method, url, headers, requestBody, authToken);
    
    case 'javascript':
      return generateJavaScriptCode(endpoint.method, url, headers, requestBody, authToken);
    
    case 'python':
      return generatePythonCode(endpoint.method, url, headers, requestBody, authToken);
    
    case 'go':
      return generateGoCode(endpoint.method, url, headers, requestBody, authToken);
    
    default:
      return '// Code generation not available for this language yet';
  }
};

const generateCurlCode = (
  method: string,
  url: string,
  headers: Record<string, string>,
  body?: string,
  authToken?: string
): string => {
  let code = `curl -X ${method} "${url}"`;
  
  if (authToken) {
    code += ` \\\n  -H "Authorization: Bearer ${authToken}"`;
  }
  
  Object.entries(headers).forEach(([key, value]) => {
    if (key !== 'Authorization') {
      code += ` \\\n  -H "${key}: ${value}"`;
    }
  });
  
  if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
    code += ` \\\n  -d '${body}'`;
  }
  
  return code;
};

const generateJavaScriptCode = (
  method: string,
  url: string,
  headers: Record<string, string>,
  body?: string,
  authToken?: string
): string => {
  const headersObj = { ...headers };
  if (authToken) {
    headersObj['Authorization'] = `Bearer ${authToken}`;
  }
  
  return `fetch('${url}', {
  method: '${method}',
  headers: ${JSON.stringify(headersObj, null, 2)},${body ? `\n  body: ${JSON.stringify(body)}` : ''}
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));`;
};
```

## Interactive Documentation Features

### Live Code Playground
```typescript
interface CodePlaygroundProps {
  initialCode?: string;
  language: 'javascript' | 'python' | 'typescript';
  apiEndpoint: string;
}

const CodePlayground: React.FC<CodePlaygroundProps> = ({ 
  initialCode = '', 
  language,
  apiEndpoint 
}) => {
  const [code, setCode] = useState<string>(initialCode);
  const [output, setOutput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const executeCode = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiEndpoint}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          language,
          runtime: getRuntime(language)
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setOutput(result.output);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(`Execution failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="code-playground">
      <div className="playground-header">
        <h3>Interactive Playground</h3>
        <div className="playground-controls">
          <Button 
            onClick={executeCode}
            disabled={loading}
            className="run-button"
          >
            {loading ? <Spinner size="sm" /> : <PlayIcon />}
            Run Code
          </Button>
          <Button 
            variant="secondary"
            onClick={() => setCode(initialCode)}
          >
            <ResetIcon /> Reset
          </Button>
        </div>
      </div>
      
      <div className="playground-content">
        <div className="code-editor-section">
          <div className="section-header">
            <h4>Code Editor</h4>
            <LanguageBadge language={language} />
          </div>
          <MonacoEditor
            language={language === 'typescript' ? 'typescript' : language}
            value={code}
            onChange={(value) => setCode(value || '')}
            options={{
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              theme: 'vs-dark',
              fontSize: 14,
              lineNumbers: 'on',
              automaticLayout: true
            }}
            height="400px"
          />
        </div>
        
        <div className="output-section">
          <div className="section-header">
            <h4>Output</h4>
            <Button 
              size="sm"
              variant="ghost"
              onClick={() => setOutput('')}
            >
              Clear
            </Button>
          </div>
          <div className="output-container">
            {error ? (
              <div className="error-output">
                <ErrorIcon />
                <pre>{error}</pre>
              </div>
            ) : (
              <pre className="success-output">{output}</pre>
            )}
          </div>
        </div>
      </div>
      
      <div className="playground-footer">
        <div className="tips">
          <h5>Tips:</h5>
          <ul>
            <li>Use console.log() to see output in the console</li>
            <li>All CovetPy APIs are available in the global scope</li>
            <li>Try the examples in the documentation</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
```

### SDK Documentation Generator
```typescript
interface SDKDocumentationProps {
  language: 'python' | 'javascript' | 'go' | 'java' | 'php';
  apiSpec: OpenAPISpec;
}

const SDKDocumentation: React.FC<SDKDocumentationProps> = ({ language, apiSpec }) => {
  const [sdkMethods, setSDKMethods] = useState<SDKMethod[]>([]);
  const [selectedMethod, setSelectedMethod] = useState<SDKMethod | null>(null);
  
  // Generate SDK documentation from OpenAPI spec
  useEffect(() => {
    const methods = generateSDKMethods(apiSpec, language);
    setSDKMethods(methods);
    if (methods.length > 0) {
      setSelectedMethod(methods[0]);
    }
  }, [apiSpec, language]);
  
  return (
    <div className="sdk-documentation">
      <div className="sdk-header">
        <h2>{getLanguageName(language)} SDK Documentation</h2>
        <div className="sdk-actions">
          <Button onClick={() => downloadSDK(language)}>
            <DownloadIcon /> Download SDK
          </Button>
          <Button 
            variant="secondary"
            onClick={() => viewGitHubRepo(language)}
          >
            <GitHubIcon /> View on GitHub
          </Button>
        </div>
      </div>
      
      <div className="sdk-content">
        <div className="methods-sidebar">
          <div className="methods-search">
            <SearchInput 
              placeholder="Search methods..."
              onChange={handleMethodSearch}
            />
          </div>
          
          <div className="methods-list">
            {Object.entries(groupMethodsByService(sdkMethods)).map(([service, methods]) => (
              <MethodGroup
                key={service}
                service={service}
                methods={methods}
                selectedMethod={selectedMethod}
                onMethodSelect={setSelectedMethod}
              />
            ))}
          </div>
        </div>
        
        <div className="method-details">
          {selectedMethod ? (
            <MethodDetailPanel
              method={selectedMethod}
              language={language}
            />
          ) : (
            <div className="no-method-selected">
              <h3>Select a method to view details</h3>
              <p>Choose from the list on the left to see usage examples and documentation</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const MethodDetailPanel: React.FC<{ method: SDKMethod; language: string }> = ({ 
  method, 
  language 
}) => {
  return (
    <div className="method-detail-panel">
      <div className="method-header">
        <h3>{method.name}</h3>
        <code className="method-signature">{method.signature}</code>
      </div>
      
      <div className="method-description">
        <p>{method.description}</p>
        
        {method.deprecated && (
          <Alert variant="warning">
            <WarningIcon /> This method is deprecated. {method.deprecationNotice}
          </Alert>
        )}
      </div>
      
      <Tabs defaultValue="usage">
        <TabsList>
          <TabsTrigger value="usage">Usage</TabsTrigger>
          <TabsTrigger value="parameters">Parameters</TabsTrigger>
          <TabsTrigger value="response">Response</TabsTrigger>
          <TabsTrigger value="examples">Examples</TabsTrigger>
        </TabsList>
        
        <TabsContent value="usage">
          <div className="usage-section">
            <h4>Basic Usage</h4>
            <CodeBlock language={language} code={method.basicUsage} />
            
            <h4>Advanced Usage</h4>
            <CodeBlock language={language} code={method.advancedUsage} />
          </div>
        </TabsContent>
        
        <TabsContent value="parameters">
          <ParametersTable parameters={method.parameters} />
        </TabsContent>
        
        <TabsContent value="response">
          <ResponseSchema schema={method.responseSchema} />
        </TabsContent>
        
        <TabsContent value="examples">
          <ExamplesSection 
            examples={method.examples}
            language={language}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};
```

## Documentation Search and Navigation

### Advanced Search Component
```typescript
interface DocumentationSearchProps {
  onResultSelect: (result: SearchResult) => void;
}

const DocumentationSearch: React.FC<DocumentationSearchProps> = ({ onResultSelect }) => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  
  // Real-time search with debouncing
  const debouncedSearch = useDebounce(query, 300);
  
  useEffect(() => {
    if (debouncedSearch.length > 2) {
      performSearch(debouncedSearch);
    } else {
      setResults([]);
    }
  }, [debouncedSearch]);
  
  const performSearch = async (searchQuery: string) => {
    setLoading(true);
    
    try {
      const response = await fetch(`/api/v1/docs/search?q=${encodeURIComponent(searchQuery)}`);
      const searchResults = await response.json();
      
      setResults(searchResults.map((result: any) => ({
        ...result,
        highlights: highlightSearchTerms(result.content, searchQuery)
      })));
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="documentation-search">
      <div className="search-input-container">
        <SearchIcon className="search-icon" />
        <input
          type="text"
          placeholder="Search documentation..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsOpen(true)}
          className="search-input"
        />
        {loading && <Spinner size="sm" className="search-spinner" />}
      </div>
      
      {isOpen && results.length > 0 && (
        <div className="search-results-dropdown">
          <div className="results-header">
            <span>{results.length} results found</span>
          </div>
          
          <div className="results-list">
            {results.map((result) => (
              <SearchResultItem
                key={result.id}
                result={result}
                onClick={() => {
                  onResultSelect(result);
                  setIsOpen(false);
                  setQuery('');
                }}
              />
            ))}
          </div>
          
          <div className="results-footer">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => openAdvancedSearch(query)}
            >
              Advanced Search
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

const SearchResultItem: React.FC<{ result: SearchResult; onClick: () => void }> = ({ 
  result, 
  onClick 
}) => {
  return (
    <div className="search-result-item" onClick={onClick}>
      <div className="result-header">
        <span className="result-type">{result.type}</span>
        <h4 className="result-title">{result.title}</h4>
      </div>
      
      <div className="result-content">
        <p dangerouslySetInnerHTML={{ __html: result.highlights }} />
      </div>
      
      <div className="result-metadata">
        <span className="result-category">{result.category}</span>
        <span className="result-updated">Updated {formatRelativeTime(result.lastUpdated)}</span>
      </div>
    </div>
  );
};
```

## Real-Time Documentation Updates

### Live Documentation Sync
```typescript
const useLiveDocumentation = (docPath: string) => {
  const [content, setContent] = useState<DocumentationContent | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isOutdated, setIsOutdated] = useState<boolean>(false);
  
  useEffect(() => {
    // Initial content load
    loadDocumentation(docPath);
    
    // WebSocket for real-time updates
    const ws = new WebSocket(`wss://api.covet.local/ws/docs/${docPath}`);
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      
      if (update.type === 'content_updated') {
        setContent(update.content);
        setLastUpdated(new Date(update.timestamp));
        setIsOutdated(false);
      } else if (update.type === 'api_changed') {
        // API spec changed, mark documentation as potentially outdated
        setIsOutdated(true);
      }
    };
    
    return () => ws.close();
  }, [docPath]);
  
  const refreshContent = async () => {
    await loadDocumentation(docPath);
    setIsOutdated(false);
  };
  
  const loadDocumentation = async (path: string) => {
    try {
      const response = await fetch(`/api/v1/docs/${path}`);
      const docContent = await response.json();
      
      setContent(docContent);
      setLastUpdated(new Date(docContent.lastUpdated));
    } catch (error) {
      console.error('Failed to load documentation:', error);
    }
  };
  
  return {
    content,
    lastUpdated,
    isOutdated,
    refreshContent,
    loading: content === null
  };
};

const LiveDocumentationViewer: React.FC<{ docPath: string }> = ({ docPath }) => {
  const { content, lastUpdated, isOutdated, refreshContent, loading } = useLiveDocumentation(docPath);
  
  if (loading) {
    return <DocumentationSkeleton />;
  }
  
  if (!content) {
    return <DocumentationNotFound docPath={docPath} />;
  }
  
  return (
    <div className="live-documentation-viewer">
      {isOutdated && (
        <Alert variant="warning" className="outdated-warning">
          <WarningIcon />
          This documentation may be outdated due to recent API changes.
          <Button size="sm" onClick={refreshContent}>
            Refresh Content
          </Button>
        </Alert>
      )}
      
      <div className="doc-header">
        <h1>{content.title}</h1>
        <div className="doc-metadata">
          <span>Last updated: {formatRelativeTime(lastUpdated)}</span>
          <LiveIndicator isLive={true} />
        </div>
      </div>
      
      <div className="doc-content">
        <MarkdownRenderer 
          content={content.markdown}
          components={{
            CodeBlock: InteractiveCodeBlock,
            APIReference: LiveAPIReference,
            Example: InteractiveExample
          }}
        />
      </div>
    </div>
  );
};
```

This developer documentation portal provides a comprehensive, interactive platform for exploring CovetPy APIs with real-time data integration, live examples, and dynamic content updates. All components connect to actual backend services to ensure accuracy and freshness of the documentation.