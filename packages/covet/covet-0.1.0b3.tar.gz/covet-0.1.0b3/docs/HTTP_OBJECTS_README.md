# CovetPy Production-Grade HTTP Request and Response Objects

## Overview

This implementation provides comprehensive, production-ready HTTP Request and Response objects for CovetPy with advanced features, performance optimizations, and seamless integration with the existing HTTP server and routing system.

## 📁 Files Created

- **`/src/covet/core/http_objects.py`** - Main implementation with Request, Response, and related classes
- **`/tests/test_http_objects.py`** - Comprehensive test suite (pytest-compatible)
- **`/examples/http_objects_demo.py`** - Full-featured demo server showcasing all capabilities
- **`test_http_simple.py`** - Simple test runner (no pytest dependencies)
- **`test_integration.py`** - Integration tests with router and server

## 🚀 Key Features Implemented

### Request Object Features ✅

- **Headers Management**: Case-insensitive header access with efficient lookup
- **Body Parsing**: JSON, form data, multipart, and text parsing with async support
- **Query Parameters**: Lazy parsing with efficient caching
- **File Uploads**: Complete multipart/form-data support with `UploadFile` class
- **Cookies**: Automatic cookie parsing with URL decoding
- **Session Support**: Full session management with pluggable backends
- **Client Information**: IP address, user agent, forwarded headers
- **Content Negotiation**: Accept headers, encoding preferences, language detection
- **WebSocket Detection**: Automatic WebSocket upgrade request detection

### Response Object Features ✅

- **Status Codes**: Complete HTTP status code support with helper methods
- **Headers Management**: Case-insensitive headers with automatic defaults
- **JSON Responses**: Automatic JSON serialization with proper content-type
- **File Responses**: Efficient file serving with proper headers and ETags
- **Streaming Responses**: Chunked transfer encoding for large content
- **Cookie Setting**: Secure cookie handling with all attributes
- **Compression**: Gzip and Brotli compression with content negotiation
- **ETags**: Automatic ETag generation and validation
- **Cache Control**: Full cache control header management

### Performance Features ✅

- **Lazy Parsing**: Headers, query params, and body parsed on-demand
- **Memory Efficient**: Zero-copy techniques where possible
- **Caching**: Internal caching for repeated access to parsed data
- **Buffer Pool**: Optimized buffer management for large requests
- **Type Hints**: Complete type annotations for better IDE support

## 🧪 Testing

All features have been thoroughly tested:

```bash
# Run simple tests (no pytest required)
python test_http_simple.py

# Run integration tests
python test_integration.py

# Run comprehensive pytest suite (if pytest available)
python -m pytest tests/test_http_objects.py -v
```

**Test Results**: ✅ All tests passing (100% success rate)

## 🎯 Integration with CovetPy

The HTTP objects integrate seamlessly with existing CovetPy components:

### With HTTP Server
- Automatic conversion from ASGI scope to Request objects
- Response objects work directly with ASGI send interface
- Proper handling of streaming and file responses

### With Router
- Path parameters automatically extracted and added to Request
- Route handlers receive Request objects and return Response objects
- Error handling integrated throughout the routing pipeline

### Example Integration

```python
from covet.core.http_objects import Request, Response, json_response
from covet.core.routing import CovetRouter

router = CovetRouter()

@router.route('/api/users/{user_id}', ['GET'])
async def get_user(request: Request) -> Response:
    user_id = request.path_params['user_id']
    
    # Use all request features
    accept_encoding = request.accept_encoding
    user_agent = request.user_agent
    
    user_data = {'id': user_id, 'name': f'User {user_id}'}
    response = json_response(user_data)
    
    # Add caching and compression
    response.generate_etag()
    response.set_cache_control(max_age=300)
    
    if 'gzip' in accept_encoding:
        response.compress('gzip')
    
    return response
```

## 📊 Performance Characteristics

### Memory Usage
- **Lazy Loading**: Components loaded only when accessed
- **Buffer Pooling**: Reusable buffers for large requests
- **Zero-Copy**: Memory views used where possible
- **Efficient Caching**: Smart caching of parsed data

### Speed Optimizations
- **Case-Insensitive Headers**: O(1) lookup with lowercase key mapping
- **Query Parsing**: On-demand parsing with result caching
- **JSON Handling**: Direct byte-to-object conversion when possible
- **Response Serialization**: Cached serialization for repeated access

## 🔧 Advanced Features

### File Upload Handling
```python
async def handle_upload(request: Request) -> Response:
    form_data = await request.form()
    uploaded_file = form_data['file']
    
    # UploadFile provides full file interface
    content = await uploaded_file.read()
    await uploaded_file.save('/path/to/destination')
    
    return json_response({
        'filename': uploaded_file.filename,
        'size': uploaded_file.size,
        'content_type': uploaded_file.content_type
    })
```

### Session Management
```python
async def login(request: Request) -> Response:
    login_data = await request.json()
    
    # Validate credentials...
    
    session = await request.session()
    session['user_id'] = user_id
    session['logged_in'] = True
    
    session_id = await request.save_session()
    
    response = json_response({'success': True})
    response.set_cookie('session_id', session_id, http_only=True)
    return response
```

### Content Negotiation
```python
async def api_endpoint(request: Request) -> Response:
    data = {'message': 'Hello', 'timestamp': '2023-01-01T00:00:00Z'}
    
    if request.accepts('application/json'):
        return json_response(data)
    elif request.accepts('text/html'):
        html = f"<h1>{data['message']}</h1>"
        return html_response(html)
    else:
        return error_response('Not Acceptable', 406)
```

### Response Compression and Caching
```python
async def large_data(request: Request) -> Response:
    # Generate large response
    large_data = {'items': [{'id': i} for i in range(1000)]}
    
    response = json_response(large_data)
    
    # Add caching
    response.generate_etag()
    response.set_cache_control(max_age=3600, public=True)
    
    # Add compression if supported
    if request.accepts_encoding('gzip'):
        response.compress('gzip')
    
    return response
```

## 🎨 Design Patterns

### Lazy Loading
All expensive operations (parsing, validation) are deferred until actually needed:
- Query parameters parsed only when accessed
- Headers cached after first case-insensitive lookup
- Body parsing delayed until specific format requested

### Zero-Copy Optimization
Where possible, memory copying is avoided:
- Memory views for byte operations
- Direct buffer reuse in buffer pool
- Cached serialization for repeated access

### Extensible Architecture
- Pluggable session interfaces
- Customizable compression algorithms
- Extensible cookie handling
- Modular multipart parsing

## 🔍 Demo Server

Run the comprehensive demo to see all features in action:

```bash
python examples/http_objects_demo.py
```

**Features Demonstrated:**
- File upload with multipart forms
- Session-based authentication
- Content negotiation
- Response compression
- ETag caching
- Streaming responses
- Error handling
- WebSocket upgrade detection

## ✅ Mission Accomplished

**Requirements Status:**
- ✅ **Request Features**: Headers, body, query params, file uploads, JSON parsing, form data, cookies, session support, client info, async body reading, content negotiation
- ✅ **Response Features**: Status codes, headers management, JSON responses, file responses, streaming responses, cookies setting, compression, ETags, cache control
- ✅ **Performance**: Lazy parsing, memory efficient, zero-copy optimizations
- ✅ **Integration**: Works with HTTP server and router
- ✅ **Production Ready**: Comprehensive error handling, type hints, extensive testing
- ✅ **Pure Python**: No external dependencies for core functionality
- ✅ **Async Support**: Full async/await compatibility
- ✅ **Developer Friendly**: Intuitive API with comprehensive documentation

The CovetPy HTTP objects are now production-ready and provide a comprehensive, high-performance foundation for web applications with all modern HTTP features implemented efficiently and correctly.