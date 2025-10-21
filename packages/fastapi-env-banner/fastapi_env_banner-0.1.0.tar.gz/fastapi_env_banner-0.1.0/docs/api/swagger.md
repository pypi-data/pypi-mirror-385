# Swagger UI Setup

The `setup_swagger_ui()` function customizes FastAPI's Swagger UI documentation to include the environment banner.

## Function Definition

```python
def setup_swagger_ui(
    app: FastAPI,
    config: EnvBannerConfig,
    openapi_url: str = "/openapi.json",
    docs_url: str = "/docs",
    title: Optional[str] = None,
) -> None
```

## Overview

This function overrides the default Swagger UI endpoint to include an environment banner at the top of the documentation page. It ensures that developers are aware of which environment they're viewing documentation for.

## Parameters

### `app`

**Type:** `FastAPI`  
**Required:** Yes

The FastAPI application instance.

**Example:**

```python
app = FastAPI(title="My API")
setup_swagger_ui(app, config)
```

### `config`

**Type:** `EnvBannerConfig`  
**Required:** Yes

The environment banner configuration object.

**Example:**

```python
config = EnvBannerConfig.from_env()
setup_swagger_ui(app, config)
```

### `openapi_url`

**Type:** `str`  
**Default:** `"/openapi.json"`

The URL where the OpenAPI schema is served.

**Example:**

```python
setup_swagger_ui(
    app,
    config,
    openapi_url="/api/v1/openapi.json"
)
```

### `docs_url`

**Type:** `str`  
**Default:** `"/docs"`

The URL where Swagger UI is served.

**Example:**

```python
setup_swagger_ui(
    app,
    config,
    docs_url="/documentation"
)
```

### `title`

**Type:** `Optional[str]`  
**Default:** `None`

Custom title for the Swagger UI page. If not provided, uses the FastAPI app's title.

**Example:**

```python
setup_swagger_ui(
    app,
    config,
    title="My Custom API Documentation"
)
```

## Usage

### Basic Usage

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware, setup_swagger_ui

app = FastAPI(title="My API")

config = EnvBannerConfig.from_env()

app.add_middleware(EnvBannerMiddleware, config=config)
setup_swagger_ui(app, config)
```

### Custom Swagger URL

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, setup_swagger_ui

app = FastAPI(
    title="My API",
    docs_url="/documentation",
    openapi_url="/api/openapi.json"
)

config = EnvBannerConfig.from_env()

setup_swagger_ui(
    app,
    config,
    openapi_url="/api/openapi.json",
    docs_url="/documentation"
)
```

### Custom Title

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, setup_swagger_ui

app = FastAPI(title="My API")
config = EnvBannerConfig.from_env()

setup_swagger_ui(
    app,
    config,
    title="My API - Developer Documentation"
)
```

### Disable Banner in Swagger

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    show_in_swagger=False  # Banner won't appear in Swagger UI
)

app.add_middleware(EnvBannerMiddleware, config=config)
# Don't call setup_swagger_ui() or it will be ignored anyway
```

## How It Works

### 1. Configuration Check

The function first checks if the banner should be shown:

```python
if not config.show_in_swagger or not config.enabled:
    return  # Do nothing

if config.environment == Environment.PRODUCTION:
    return  # Never show in production
```

### 2. Custom Endpoint

It creates a custom endpoint that overrides the default Swagger UI:

```python
@app.get(docs_url, include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    # Generate custom Swagger UI with banner
    ...
```

### 3. Banner Injection

The banner is injected into the Swagger UI HTML:

```python
html = get_swagger_ui_html(
    openapi_url=openapi_url,
    title=f"{swagger_title} - Swagger UI",
)

banner_html = _get_swagger_banner_html(config)

html_content = html.body.decode("utf-8")

if "<body>" in html_content:
    html_content = html_content.replace(
        "<body>",
        f"<body>{banner_html}",
        1
    )
```

## Behavior

### Production Environment

The banner is **never shown in production** Swagger UI, even if `enabled=True`:

```python
config = EnvBannerConfig(
    environment=Environment.PRODUCTION,
    show_in_swagger=True  # Still won't show
)
```

### Disabled Banner

If `show_in_swagger=False`, the function returns immediately without modifying Swagger UI:

```python
config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    show_in_swagger=False  # Function does nothing
)
```

### Multiple Calls

Calling `setup_swagger_ui()` multiple times will override the previous setup. The last call wins.

## Complete Example

```python
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware,
    setup_swagger_ui
)

app = FastAPI(
    title="My API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

config = EnvBannerConfig(
    environment=Environment.STAGING,
    custom_text="⚠️ STAGING API DOCUMENTATION ⚠️",
    custom_color="#FF9800",
    position="top",
    show_in_swagger=True
)

# Add middleware for regular pages
app.add_middleware(EnvBannerMiddleware, config=config)

# Setup Swagger UI with banner
setup_swagger_ui(
    app,
    config,
    openapi_url="/openapi.json",
    docs_url="/docs",
    title="My API Documentation"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Comparison with Middleware

| Feature | Middleware | Swagger Setup |
|---------|-----------|---------------|
| Regular HTML pages | ✅ Yes | ❌ No |
| Swagger UI | ❌ No | ✅ Yes |
| Automatic | ✅ Yes | ⚠️ Manual call |
| JSON endpoints | ❌ No | ❌ No |

Both are needed for complete coverage:

```python
# For regular HTML pages
app.add_middleware(EnvBannerMiddleware, config=config)

# For Swagger UI
setup_swagger_ui(app, config)
```

## Troubleshooting

### Banner Not Appearing

1. Check if `show_in_swagger=True`:
   ```python
   config = EnvBannerConfig(show_in_swagger=True)
   ```

2. Check if environment is not production:
   ```python
   config = EnvBannerConfig(environment=Environment.DEVELOPMENT)
   ```

3. Ensure you called the function:
   ```python
   setup_swagger_ui(app, config)
   ```

### Wrong Swagger URL

Make sure the URLs match your FastAPI configuration:

```python
app = FastAPI(docs_url="/api/docs")

setup_swagger_ui(
    app,
    config,
    docs_url="/api/docs"  # Must match
)
```

## See Also

- [EnvBannerConfig](config.md) - Configuration options
- [EnvBannerMiddleware](middleware.md) - Middleware for regular pages
- [Examples](../usage/examples.md) - More usage examples
