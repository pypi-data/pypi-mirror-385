# EnvBannerConfig

The `EnvBannerConfig` class is the main configuration object for FastAPI Environment Banner.

## Class Definition

```python
@dataclass
class EnvBannerConfig:
    environment: Environment = Environment.LOCAL
    enabled: bool = True
    custom_text: Optional[str] = None
    custom_color: Optional[str] = None
    position: str = "top"
    show_in_swagger: bool = True
```

## Parameters

### `environment`

**Type:** `Environment`  
**Default:** `Environment.LOCAL`

The current environment. Must be one of:

- `Environment.LOCAL`
- `Environment.DEVELOPMENT`
- `Environment.STAGING`
- `Environment.PRODUCTION`
- `Environment.TESTING`

**Example:**

```python
config = EnvBannerConfig(environment=Environment.DEVELOPMENT)
```

### `enabled`

**Type:** `bool`  
**Default:** `True`

Controls whether the banner is displayed. When set to `False`, the banner will not appear on any pages.

**Example:**

```python
config = EnvBannerConfig(
    environment=Environment.PRODUCTION,
    enabled=False
)
```

### `custom_text`

**Type:** `Optional[str]`  
**Default:** `None`

Custom text to display in the banner. If not provided, default text based on the environment will be used.

**Example:**

```python
config = EnvBannerConfig(
    environment=Environment.STAGING,
    custom_text="⚠️ STAGING - BE CAREFUL ⚠️"
)
```

### `custom_color`

**Type:** `Optional[str]`  
**Default:** `None`

Custom background color for the banner in hex format. If not provided, default color based on the environment will be used.

**Example:**

```python
config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    custom_color="#6366F1"
)
```

### `position`

**Type:** `str`  
**Default:** `"top"`

Position of the banner on the page. Valid values are `"top"` or `"bottom"`.

**Example:**

```python
config = EnvBannerConfig(
    environment=Environment.STAGING,
    position="bottom"
)
```

### `show_in_swagger`

**Type:** `bool`  
**Default:** `True`

Controls whether the banner appears in Swagger UI documentation.

**Example:**

```python
config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    show_in_swagger=False
)
```

## Class Methods

### `from_env()`

Creates a configuration object by reading from an environment variable.

**Signature:**

```python
@classmethod
def from_env(cls, env_var: str = "ENVIRONMENT") -> "EnvBannerConfig"
```

**Parameters:**

- `env_var` (str, optional): Name of the environment variable to read. Default: `"ENVIRONMENT"`

**Returns:** `EnvBannerConfig` instance

**Example:**

```python
# Reads from ENVIRONMENT variable
config = EnvBannerConfig.from_env()

# Reads from custom variable
config = EnvBannerConfig.from_env(env_var="APP_ENV")
```

**Recognized Values:**

The method recognizes the following environment variable values (case-insensitive):

- `"local"` → `Environment.LOCAL`
- `"dev"`, `"development"` → `Environment.DEVELOPMENT`
- `"stage"`, `"staging"` → `Environment.STAGING`
- `"prod"`, `"production"` → `Environment.PRODUCTION`
- `"test"`, `"testing"` → `Environment.TESTING`

### `get_banner_color()`

Returns the banner color, either custom or default based on environment.

**Signature:**

```python
def get_banner_color(self) -> str
```

**Returns:** Hex color string (e.g., `"#4CAF50"`)

**Example:**

```python
config = EnvBannerConfig(environment=Environment.DEVELOPMENT)
color = config.get_banner_color()  # Returns "#2196F3"
```

**Default Colors:**

| Environment | Color | Hex Code |
|-------------|-------|----------|
| LOCAL | Green | `#4CAF50` |
| DEVELOPMENT | Blue | `#2196F3` |
| STAGING | Orange | `#FF9800` |
| PRODUCTION | Red | `#F44336` |
| TESTING | Purple | `#9C27B0` |

### `get_banner_text()`

Returns the banner text, either custom or default based on environment.

**Signature:**

```python
def get_banner_text(self) -> str
```

**Returns:** Banner text string

**Example:**

```python
config = EnvBannerConfig(environment=Environment.STAGING)
text = config.get_banner_text()  # Returns "STAGING ENVIRONMENT"
```

**Default Texts:**

| Environment | Text |
|-------------|------|
| LOCAL | `LOCAL ENVIRONMENT` |
| DEVELOPMENT | `DEVELOPMENT ENVIRONMENT` |
| STAGING | `STAGING ENVIRONMENT` |
| PRODUCTION | `PRODUCTION ENVIRONMENT` |
| TESTING | `TESTING ENVIRONMENT` |

## Environment Enum

The `Environment` enum defines the available environment types.

```python
class Environment(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
```

## Complete Example

```python
from fastapi import FastAPI
from fastapi_env_banner import Environment, EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

# Create configuration
config = EnvBannerConfig(
    environment=Environment.STAGING,
    enabled=True,
    custom_text="🚧 STAGING ENVIRONMENT 🚧",
    custom_color="#FF9800",
    position="top",
    show_in_swagger=True
)

# Get computed values
print(config.get_banner_color())  # "#FF9800"
print(config.get_banner_text())   # "🚧 STAGING ENVIRONMENT 🚧"

# Add to app
app.add_middleware(EnvBannerMiddleware, config=config)
```

## See Also

- [EnvBannerMiddleware](middleware.md) - Middleware that uses this configuration
- [setup_swagger_ui](swagger.md) - Swagger UI setup function
- [Configuration Guide](../usage/configuration.md) - Detailed configuration guide
