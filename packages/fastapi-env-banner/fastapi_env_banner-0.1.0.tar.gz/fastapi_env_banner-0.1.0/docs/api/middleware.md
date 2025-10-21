# EnvBannerMiddleware

The `EnvBannerMiddleware` class is a Starlette middleware that automatically injects environment banners into HTML responses.

## Class Definition

```python
class EnvBannerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, config: EnvBannerConfig):
        super().__init__(app)
        self.config = config
```

## Overview

This middleware intercepts all HTTP responses and automatically adds a visual banner to HTML pages. It:

- Only processes HTML responses (skips JSON, images, etc.)
- Respects the `enabled` flag in configuration
- Automatically disables in production environment
- Injects the banner after the `<body>` tag
- Preserves all other response characteristics

## Parameters

### `app`

**Type:** `ASGIApp`

The ASGI application instance (typically your FastAPI app).

### `config`

**Type:** `EnvBannerConfig`

The configuration object that controls banner appearance and behavior.

## Usage

### Basic Usage

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

config = EnvBannerConfig.from_env()
app.add_middleware(EnvBannerMiddleware, config=config)
```

### With Custom Configuration

```python
from fastapi import FastAPI
from fastapi_env_banner import Environment, EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

config = EnvBannerConfig(
    environment=Environment.STAGING,
    custom_text="⚠️ STAGING ENVIRONMENT ⚠️",
    custom_color="#FF9800"
)

app.add_middleware(EnvBannerMiddleware, config=config)
```

## How It Works

### 1. Request Processing

When a request comes in, the middleware:

1. Checks if the banner is enabled
2. Checks if the environment is production (disabled by default)
3. Passes the request to the next handler

### 2. Response Processing

When a response is received, the middleware:

1. Checks the `Content-Type` header
2. Only processes responses with `text/html` content type
3. Skips streaming responses
4. Reads the response body
5. Injects the banner HTML after the `<body>` tag
6. Returns the modified response

### 3. Banner Injection

The banner is injected using the following logic:

```python
if "<body" in html_content:
    # Find the closing > of the <body> tag
    body_match = re.search(r"<body[^>]*>", html_content, re.IGNORECASE)
    if body_match:
        insert_pos = body_match.end()
        html_content = (
            html_content[:insert_pos] +
            banner_html +
            html_content[insert_pos:]
        )
else:
    # If no body tag, prepend the banner
    html_content = banner_html + html_content
```

## Behavior

### Enabled/Disabled

The middleware respects the `enabled` flag:

```python
config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    enabled=False  # Banner will not appear
)
```

### Production Environment

By default, the banner is **never shown in production**, even if `enabled=True`:

```python
config = EnvBannerConfig(
    environment=Environment.PRODUCTION,
    enabled=True  # Still won't show in production
)
```

This is a security feature to prevent exposing environment information.

### Content Type Filtering

The middleware only processes HTML responses:

- ✅ `text/html` - Processed
- ❌ `application/json` - Skipped
- ❌ `image/png` - Skipped
- ❌ `text/plain` - Skipped

### Streaming Responses

Streaming responses are not modified to avoid buffering issues:

```python
if isinstance(response, StreamingResponse):
    return response  # Skip streaming responses
```

## Methods

### `dispatch()`

The main middleware method that processes requests and responses.

**Signature:**

```python
async def dispatch(self, request: Request, call_next: Callable) -> Response
```

**Parameters:**

- `request` (Request): The incoming HTTP request
- `call_next` (Callable): Function to call the next middleware/handler

**Returns:** `Response` - The (possibly modified) HTTP response

## Complete Example

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_env_banner import Environment, EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    custom_text="💻 DEVELOPMENT MODE 💻",
    position="top"
)

app.add_middleware(EnvBannerMiddleware, config=config)

@app.get("/", response_class=HTMLResponse)
async def html_page():
    return """
    <!DOCTYPE html>
    <html>
        <head><title>My App</title></head>
        <body>
            <h1>Hello World</h1>
        </body>
    </html>
    """
    # Banner will be injected after <body>

@app.get("/api/data")
async def api_endpoint():
    return {"message": "Hello"}
    # Banner will NOT be injected (JSON response)
```

## Error Handling

The middleware includes error handling for edge cases:

### Unicode Decode Errors

If the response body cannot be decoded as UTF-8, the original response is returned unchanged:

```python
try:
    html_content = body.decode("utf-8")
    # ... process banner injection
except UnicodeDecodeError:
    return response  # Return original response
```

### Missing Body Tag

If no `<body>` tag is found, the banner is prepended to the content:

```python
if "<body" in html_content:
    # Inject after body tag
else:
    html_content = banner_html + html_content
```

## Performance Considerations

- **Minimal Overhead**: Only processes HTML responses
- **No Buffering**: Skips streaming responses to avoid memory issues
- **Efficient Regex**: Uses simple regex for body tag detection
- **Early Exit**: Returns immediately if banner is disabled

## See Also

- [EnvBannerConfig](config.md) - Configuration options
- [setup_swagger_ui](swagger.md) - Swagger UI integration
- [Quick Start](../usage/quick-start.md) - Getting started guide
