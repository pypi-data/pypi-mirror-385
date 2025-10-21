# Configuration

FastAPI Environment Banner offers flexible configuration options to customize the appearance and behavior of environment banners.

## Configuration Methods

### Auto-Detection from Environment Variable

The easiest way to configure the banner:

```python
from fastapi_env_banner import EnvBannerConfig

# Reads from ENVIRONMENT variable
config = EnvBannerConfig.from_env()

# Or specify a custom variable name
config = EnvBannerConfig.from_env(env_var="APP_ENV")
```

### Manual Configuration

Create a configuration object with specific settings:

```python
from fastapi_env_banner import Environment, EnvBannerConfig

config = EnvBannerConfig(
    environment=Environment.STAGING,
    enabled=True,
    custom_text="⚠️ STAGING ENVIRONMENT ⚠️",
    custom_color="#FF9800",
    position="top",
    show_in_swagger=True
)
```

## Configuration Parameters

### `environment`

**Type:** `Environment` enum  
**Default:** `Environment.LOCAL`

The environment type. Available options:

- `Environment.LOCAL`
- `Environment.DEVELOPMENT`
- `Environment.STAGING`
- `Environment.PRODUCTION`
- `Environment.TESTING`

```python
config = EnvBannerConfig(environment=Environment.DEVELOPMENT)
```

### `enabled`

**Type:** `bool`  
**Default:** `True` (except for production)

Controls whether the banner is displayed. By default, banners are disabled in production for security.

```python
config = EnvBannerConfig(
    environment=Environment.PRODUCTION,
    enabled=True  # Force enable in production (not recommended)
)
```

### `custom_text`

**Type:** `Optional[str]`  
**Default:** `None`

Override the default environment text with custom text.

```python
config = EnvBannerConfig(
    environment=Environment.STAGING,
    custom_text="⚠️ TEST ENVIRONMENT - DO NOT USE IN PRODUCTION ⚠️"
)
```

### `custom_color`

**Type:** `Optional[str]`  
**Default:** `None`

Override the default environment color with a custom hex color.

```python
config = EnvBannerConfig(
    environment=Environment.STAGING,
    custom_color="#E91E63"  # Pink
)
```

### `position`

**Type:** `str`  
**Default:** `"top"`

Position of the banner. Options: `"top"` or `"bottom"`.

```python
config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    position="bottom"
)
```

### `show_in_swagger`

**Type:** `bool`  
**Default:** `True`

Controls whether the banner appears in Swagger UI documentation.

```python
config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    show_in_swagger=False  # Hide banner in Swagger UI
)
```

## Default Colors and Texts

Each environment has predefined colors and texts:

| Environment | Color | Text |
|-------------|-------|------|
| LOCAL | `#4CAF50` (Green) | LOCAL ENVIRONMENT |
| DEVELOPMENT | `#2196F3` (Blue) | DEVELOPMENT ENVIRONMENT |
| STAGING | `#FF9800` (Orange) | STAGING ENVIRONMENT |
| PRODUCTION | `#F44336` (Red) | PRODUCTION ENVIRONMENT |
| TESTING | `#9C27B0` (Purple) | TESTING ENVIRONMENT |

## Complete Example

```python
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware,
    setup_swagger_ui
)

app = FastAPI(title="My API")

# Full configuration
config = EnvBannerConfig(
    environment=Environment.STAGING,
    enabled=True,
    custom_text="🚧 STAGING - Testing in Progress 🚧",
    custom_color="#FF6B6B",
    position="top",
    show_in_swagger=True
)

app.add_middleware(EnvBannerMiddleware, config=config)
setup_swagger_ui(app, config)
```

## Environment-Specific Configuration

You can create different configurations based on the environment:

```python
import os
from fastapi import FastAPI
from fastapi_env_banner import Environment, EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

env = os.getenv("ENVIRONMENT", "local")

if env == "production":
    config = EnvBannerConfig(
        environment=Environment.PRODUCTION,
        enabled=False  # Disabled in production
    )
elif env == "staging":
    config = EnvBannerConfig(
        environment=Environment.STAGING,
        custom_text="⚠️ STAGING - BE CAREFUL ⚠️",
        position="top"
    )
else:
    config = EnvBannerConfig.from_env()

app.add_middleware(EnvBannerMiddleware, config=config)
```

## Security Considerations

!!! warning "Production Environment"
    By default, banners are **disabled in production** to prevent exposing environment information. Only enable them in production if you have a specific reason and understand the security implications.

```python
# Safe: Banner disabled in production by default
config = EnvBannerConfig(environment=Environment.PRODUCTION)

# Unsafe: Forcing banner in production
config = EnvBannerConfig(
    environment=Environment.PRODUCTION,
    enabled=True  # Not recommended!
)
```

## Next Steps

- See more [Examples](examples.md)
- Check the [API Reference](../api/config.md)
