# HTTP Objects API Reference

Complete reference for CovetPy's Request and Response objects.

## Table of Contents

- [Request](#request)
- [Response](#response)
- [StreamingResponse](#streamingresponse)
- [Cookie](#cookie)
- [Response Helpers](#response-helpers)

## Request

The Request object represents an incoming HTTP request with lazy parsing and zero-copy optimizations.

### Class: `Request`

```python
class Request:
    def __init__(
        self,
        method: str = None,
        url: str = None,
        headers: Dict[str, str] = None,
        body: Union[bytes, StreamingBody] = None,
        query_string: str = "",
        path_params: Dict[str, Any] = None,
        remote_addr: str = "",
        scheme: str = "http",
        server_name: str = "",
        server_port: int = 80,
        scope: dict = None,
        receive: Callable = None,
    ) -> None
```

**Description**: Ultra-high-performance HTTP request with lazy parsing and caching.

**Attributes**:
- `method` (str): HTTP method (GET, POST, PUT, DELETE, etc.)
- `url` (str): Request URL path
- `headers` (CaseInsensitiveDict): Request headers
- `scheme` (str): URL scheme (http, https)
- `server_name` (str): Server hostname
- `server_port` (int): Server port
- `remote_addr` (str): Client IP address
- `path_params` (dict): Path parameters from routing
- `context` (dict): Request context for middleware/DI
- `scope` (dict): ASGI scope dictionary
-`_receive` (Callable): ASGI receive function

### Properties

#### `request.path`

```python
@property
def path(self) -> str
```

**Description**: Get request path (lazy parsed from URL).

**Example**:
```python
@app.get("/users/{user_id}")
async def handler(request):
    print(request.path)  # "/users/123"
```

#### `request.query`

```python
@property
def query(self) -> LazyQueryParser
```

**Description**: Get query parameters with lazy parsing.

**Returns**: LazyQueryParser object supporting dict-like access.

**Example**:
```python
# URL: /search?q=python&limit=10

@app.get("/search")
async def search(request):
    q = request.query.get("q")  # "python"
    limit = request.query.get("limit", "20")  # "10"
    all_params = request.query.parsed  # {"q": ["python"], "limit": ["10"]}

    # Check if parameter exists
    if "q" in request.query:
        # Process search
        pass
```

#### `request.body`

```python
@property
def body(self) -> StreamingBody
```

**Description**: Get request body as streaming object.

**Returns**: StreamingBody object for reading request data.

**Example**:
```python
@app.post("/upload")
async def upload(request):
    # Read all at once
    data = await request.body.read()

    # Read line by line
    line = await request.body.read_line()
```

#### `request.content_type`

```python
@property
def content_type(self) -> str
```

**Description**: Get Content-Type header value.

**Example**:
```python
@app.post("/data")
async def handle_data(request):
    if request.content_type == "application/json":
        data = await request.json()
    elif request.content_type == "application/x-www-form-urlencoded":
        data = await request.form()
```

#### `request.content_length`

```python
@property
def content_length(self) -> Optional[int]
```

**Description**: Get Content-Length header value.

**Example**:
```python
@app.post("/upload")
async def upload(request):
    if request.content_length > 10_000_000:  # 10MB
        return {"error": "File too large"}, 413
```

### Methods

#### `request.json()`

```python
async def json(self) -> Any
```

**Description**: Parse request body as JSON (cached after first call).

**Returns**: Parsed JSON data (dict, list, etc.)

**Example**:
```python
@app.post("/users")
async def create_user(request):
    data = await request.json()
    name = data["name"]
    email = data["email"]
    return {"user": data}, 201
```

#### `request.form()`

```python
async def form(self) -> Dict[str, List[str]]
```

**Description**: Parse request body as form data (cached).

**Returns**: Dictionary mapping field names to lists of values.

**Example**:
```python
@app.post("/login")
async def login(request):
    form_data = await request.form()
    username = form_data.get("username", [""])[0]
    password = form_data.get("password", [""])[0]

    # Validate credentials
    return {"status": "ok"}
```

#### `request.cookies()`

```python
def cookies(self) -> Dict[str, str]
```

**Description**: Get cookies from request headers (cached).

**Returns**: Dictionary of cookie name-value pairs.

**Example**:
```python
@app.get("/profile")
async def profile(request):
    session_id = request.cookies().get("session_id")
    if not session_id:
        return {"error": "Not authenticated"}, 401

    # Load user from session
    return {"user": "data"}
```

#### `request.get_header()`

```python
def get_header(self, name: str, default: str = None) -> Optional[str]
```

**Description**: Get header value with default.

**Example**:
```python
@app.get("/api/data")
async def get_data(request):
    auth_token = request.get_header("authorization")
    user_agent = request.get_header("user-agent", "unknown")

    return {"token": auth_token, "ua": user_agent}
```

#### `request.has_header()`

```python
def has_header(self, name: str) -> bool
```

**Description**: Check if header exists.

**Example**:
```python
@app.post("/webhook")
async def webhook(request):
    if not request.has_header("x-webhook-signature"):
        return {"error": "Missing signature"}, 401

    signature = request.get_header("x-webhook-signature")
    # Verify signature
```

### Content Type Checks

#### `request.is_json()`

```python
def is_json(self) -> bool
```

**Description**: Check if request has JSON content type.

**Example**:
```python
@app.post("/data")
async def handle_data(request):
    if request.is_json():
        data = await request.json()
    else:
        return {"error": "JSON expected"}, 400
```

#### `request.is_form()`

```python
def is_form(self) -> bool
```

**Description**: Check if request is form data.

#### `request.is_multipart()`

```python
def is_multipart(self) -> bool
```

**Description**: Check if request is multipart form data.

#### `request.is_websocket()`

```python
def is_websocket(self) -> bool
```

**Description**: Check if this is a WebSocket upgrade request.

#### `request.accepts()`

```python
def accepts(self, content_type: str) -> bool
```

**Description**: Check if client accepts content type.

**Example**:
```python
@app.get("/data")
async def get_data(request):
    if request.accepts("application/json"):
        return {"data": "json"}
    elif request.accepts("text/html"):
        return "<html>...</html>"
    else:
        return {"data": "plain"}, 406
```

### Path Parameters

Path parameters are automatically extracted from URL patterns and available in `request.path_params`:

```python
@app.get("/users/{user_id}/posts/{post_id}")
async def get_post(request):
    user_id = request.path_params["user_id"]
    post_id = request.path_params["post_id"]
    return {"user": user_id, "post": post_id}

# Or use function parameters (if supported by router)
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # user_id is automatically extracted and converted
    return {"user_id": user_id}
```

## Response

The Response object represents an HTTP response with zero-copy optimizations.

### Class: `Response`

```python
class Response:
    def __init__(
        self,
        content: Any = "",
        status_code: int = 200,
        headers: Dict[str, str] = None,
        media_type: str = None,
        charset: str = "utf-8",
    ) -> None
```

**Description**: Ultra-high-performance HTTP response with caching and zero-copy serialization.

**Parameters**:
- `content` (Any): Response body (str, bytes, dict, list)
- `status_code` (int): HTTP status code (default: 200)
- `headers` (dict, optional): Response headers
- `media_type` (str, optional): Content-Type (auto-detected if None)
- `charset` (str): Character encoding (default: "utf-8")

**Example**:
```python
from covet.core.http import Response

# String content
response = Response("Hello, World!")

# JSON content (auto-detected)
response = Response({"message": "Hello"})

# Custom status and headers
response = Response(
    content={"error": "Not found"},
    status_code=404,
    headers={"X-Custom": "Value"}
)

# Binary content
response = Response(
    content=b"\x89PNG...",
    media_type="image/png"
)
```

### Methods

#### `response.set_cookie()`

```python
def set_cookie(
    self,
    name: str,
    value: str,
    max_age: Optional[int] = None,
    expires: Optional[str] = None,
    path: str = "/",
    domain: Optional[str] = None,
    secure: bool = False,
    http_only: bool = False,
    same_site: Optional[str] = None,
) -> None
```

**Description**: Set a cookie in the response.

**Parameters**:
- `name` (str): Cookie name
- `value` (str): Cookie value
- `max_age` (int, optional): Max age in seconds
- `expires` (str, optional): Expiration date string
- `path` (str): Cookie path (default: "/")
- `domain` (str, optional): Cookie domain
- `secure` (bool): Secure flag (HTTPS only)
- `http_only` (bool): HttpOnly flag (no JavaScript access)
- `same_site` (str, optional): SameSite policy ("Strict", "Lax", "None")

**Example**:
```python
@app.post("/login")
async def login(request):
    # Authenticate user
    response = Response({"status": "logged in"})

    # Set session cookie
    response.set_cookie(
        name="session_id",
        value="abc123",
        max_age=3600,  # 1 hour
        http_only=True,
        secure=True,
        same_site="Strict"
    )

    return response
```

#### `response.delete_cookie()`

```python
def delete_cookie(
    self,
    name: str,
    path: str = "/",
    domain: Optional[str] = None
) -> None
```

**Description**: Delete a cookie by setting it to expire.

**Example**:
```python
@app.post("/logout")
async def logout(request):
    response = Response({"status": "logged out"})
    response.delete_cookie("session_id")
    return response
```

## StreamingResponse

For large responses or streaming data.

### Class: `StreamingResponse`

```python
class StreamingResponse:
    def __init__(
        self,
        content: Union[str, bytes, AsyncGenerator, Generator] = "",
        status_code: int = 200,
        headers: Dict[str, str] = None,
        media_type: str = "text/plain",
        charset: str = "utf-8",
    ) -> None
```

**Description**: Streaming HTTP response for efficient data transfer.

**Example**:
```python
from covet.core.http import StreamingResponse
import asyncio

@app.get("/stream")
async def stream_data():
    async def generate():
        for i in range(100):
            await asyncio.sleep(0.1)
            yield f"data: {i}\n\n"

    return StreamingResponse(
        content=generate(),
        media_type="text/event-stream"
    )

@app.get("/download")
async def download_file():
    def file_chunks():
        with open("large_file.dat", "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    return StreamingResponse(
        content=file_chunks(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=large_file.dat"
        }
    )
```

## Cookie

Cookie object for detailed cookie management.

### Class: `Cookie`

```python
class Cookie:
    def __init__(
        self,
        name: str,
        value: str,
        max_age: Optional[int] = None,
        expires: Optional[str] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[str] = None,
    ) -> None
```

**Description**: HTTP Cookie with security attributes.

**Example**:
```python
from covet.core.http import Cookie, Response

@app.post("/login")
async def login(request):
    response = Response({"status": "ok"})

    # Create cookie manually
    cookie = Cookie(
        name="session",
        value="token123",
        max_age=86400,  # 1 day
        secure=True,
        http_only=True,
        same_site="Strict"
    )

    response.cookies["session"] = cookie
    return response
```

## Response Helpers

Convenience functions for common response types.

### `json_response()`

```python
def json_response(
    data: Any,
    status_code: int = 200,
    headers: Dict[str, str] = None
) -> Response
```

**Description**: Create JSON response.

**Example**:
```python
from covet.core.http import json_response

@app.get("/users")
async def get_users():
    users = [{"id": 1, "name": "Alice"}]
    return json_response(users)

@app.post("/users")
async def create_user(request):
    data = await request.json()
    return json_response(
        {"user": data, "status": "created"},
        status_code=201
    )
```

### `html_response()`

```python
def html_response(
    content: str,
    status_code: int = 200,
    headers: Dict[str, str] = None
) -> Response
```

**Description**: Create HTML response.

**Example**:
```python
from covet.core.http import html_response

@app.get("/")
async def home():
    html = """
    <!DOCTYPE html>
    <html>
        <head><title>Home</title></head>
        <body><h1>Welcome!</h1></body>
    </html>
    """
    return html_response(html)
```

### `text_response()`

```python
def text_response(
    content: str,
    status_code: int = 200,
    headers: Dict[str, str] = None
) -> Response
```

**Description**: Create plain text response.

**Example**:
```python
from covet.core.http import text_response

@app.get("/health")
async def health():
    return text_response("OK")
```

### `redirect_response()`

```python
def redirect_response(
    url: str,
    status_code: int = 302,
    headers: Dict[str, str] = None
) -> Response
```

**Description**: Create redirect response.

**Example**:
```python
from covet.core.http import redirect_response

@app.get("/old-path")
async def old_endpoint():
    return redirect_response("/new-path", status_code=301)

@app.post("/submit")
async def submit_form(request):
    # Process form
    return redirect_response("/success")
```

### `error_response()`

```python
def error_response(
    message: str,
    status_code: int = 500,
    headers: Dict[str, str] = None
) -> Response
```

**Description**: Create error response with JSON body.

**Example**:
```python
from covet.core.http import error_response

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id < 1:
        return error_response("Invalid user ID", status_code=400)

    # ... fetch user
```

## Complete Examples

### File Upload

```python
@app.post("/upload")
async def upload_file(request):
    # Check content type
    if not request.is_multipart():
        return error_response("Multipart form data required", 400)

    # Check file size
    if request.content_length > 10_000_000:
        return error_response("File too large (max 10MB)", 413)

    # Process upload (simplified)
    data = await request.body.read()

    return json_response({
        "uploaded": True,
        "size": len(data)
    })
```

### API with Cookies

```python
@app.post("/api/login")
async def api_login(request):
    data = await request.json()

    # Authenticate
    if authenticate(data["username"], data["password"]):
        response = json_response({"status": "authenticated"})
        response.set_cookie(
            name="api_token",
            value=generate_token(),
            max_age=3600,
            http_only=True,
            secure=True
        )
        return response

    return error_response("Invalid credentials", 401)

@app.get("/api/profile")
async def api_profile(request):
    token = request.cookies().get("api_token")
    if not token:
        return error_response("Not authenticated", 401)

    # Load user from token
    user = get_user_from_token(token)
    return json_response({"user": user})
```

### Content Negotiation

```python
@app.get("/data")
async def get_data(request):
    data = {"items": [1, 2, 3]}

    if request.accepts("application/json"):
        return json_response(data)
    elif request.accepts("text/html"):
        html = f"<ul>{''.join(f'<li>{i}</li>' for i in data['items'])}</ul>"
        return html_response(html)
    elif request.accepts("text/plain"):
        text = "\n".join(str(i) for i in data["items"])
        return text_response(text)
    else:
        return error_response("Unsupported media type", 406)
```

## See Also

- [Core Application API](01-core-application.md)
- [Routing API](03-routing.md)
- [Middleware API](04-middleware.md)
