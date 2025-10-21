# Examples

This page provides practical examples of using FastAPI Environment Banner in different scenarios.

## Example 1: Minimal Setup

The simplest possible setup with auto-detection:

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()
app.add_middleware(EnvBannerMiddleware, config=EnvBannerConfig.from_env())

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Example 2: Full Customization

Complete customization with all options:

```python
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware,
    setup_swagger_ui
)

app = FastAPI(title="Production API")

config = EnvBannerConfig(
    environment=Environment.STAGING,
    enabled=True,
    custom_text="⚠️ TEST ENVIRONMENT - DO NOT USE IN PRODUCTION ⚠️",
    custom_color="#E91E63",
    position="bottom",
    show_in_swagger=True
)

app.add_middleware(EnvBannerMiddleware, config=config)
setup_swagger_ui(app, config)

@app.get("/")
async def root():
    return {"status": "ok"}
```

## Example 3: Environment-Based Configuration

Different configurations for different environments:

```python
import os
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware,
    setup_swagger_ui
)

app = FastAPI()

# Get environment from variable
env_name = os.getenv("ENVIRONMENT", "local").lower()

# Configure based on environment
if env_name in ["prod", "production"]:
    config = EnvBannerConfig(
        environment=Environment.PRODUCTION,
        enabled=False  # Disabled in production
    )
elif env_name in ["stage", "staging"]:
    config = EnvBannerConfig(
        environment=Environment.STAGING,
        custom_text="🚧 STAGING ENVIRONMENT 🚧",
        position="top"
    )
elif env_name in ["dev", "development"]:
    config = EnvBannerConfig(
        environment=Environment.DEVELOPMENT,
        custom_text="💻 DEVELOPMENT MODE 💻"
    )
else:
    config = EnvBannerConfig(
        environment=Environment.LOCAL,
        custom_text="🏠 LOCAL DEVELOPMENT 🏠"
    )

app.add_middleware(EnvBannerMiddleware, config=config)
setup_swagger_ui(app, config)
```

## Example 4: Disable in Production

Ensure the banner is never shown in production:

```python
import os
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

# Completely disable in production
is_production = os.getenv("ENVIRONMENT", "").lower() in ["prod", "production"]

config = EnvBannerConfig.from_env()
config.enabled = not is_production

app.add_middleware(EnvBannerMiddleware, config=config)
```

## Example 5: Custom Colors for Branding

Use your company's brand colors:

```python
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware,
    setup_swagger_ui
)

app = FastAPI()

config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    custom_text="🎨 ACME Corp - Development",
    custom_color="#6366F1",  # Your brand color
    position="top"
)

app.add_middleware(EnvBannerMiddleware, config=config)
setup_swagger_ui(app, config)
```

## Example 6: Bottom Banner

Place the banner at the bottom of the page:

```python
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware
)

app = FastAPI()

config = EnvBannerConfig(
    environment=Environment.STAGING,
    position="bottom",
    custom_text="⬇️ STAGING ENVIRONMENT ⬇️"
)

app.add_middleware(EnvBannerMiddleware, config=config)
```

## Example 7: Hide from Swagger UI

Show banner on pages but not in API documentation:

```python
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware
)

app = FastAPI()

config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    show_in_swagger=False  # Hide from Swagger UI
)

app.add_middleware(EnvBannerMiddleware, config=config)
```

## Example 8: Multiple Environments with Settings

Using Pydantic settings for configuration:

```python
from fastapi import FastAPI
from pydantic_settings import BaseSettings
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware,
    setup_swagger_ui
)

class Settings(BaseSettings):
    environment: str = "local"
    app_name: str = "My API"
    
    class Config:
        env_file = ".env"

settings = Settings()
app = FastAPI(title=settings.app_name)

# Map string to Environment enum
env_map = {
    "local": Environment.LOCAL,
    "development": Environment.DEVELOPMENT,
    "staging": Environment.STAGING,
    "production": Environment.PRODUCTION,
    "testing": Environment.TESTING,
}

config = EnvBannerConfig(
    environment=env_map.get(settings.environment.lower(), Environment.LOCAL),
    enabled=settings.environment.lower() != "production"
)

app.add_middleware(EnvBannerMiddleware, config=config)
setup_swagger_ui(app, config)
```

## Example 9: Testing Environment

Special configuration for testing:

```python
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware
)

app = FastAPI()

config = EnvBannerConfig(
    environment=Environment.TESTING,
    custom_text="🧪 TESTING ENVIRONMENT - Automated Tests Running 🧪",
    custom_color="#9C27B0",
    position="top"
)

app.add_middleware(EnvBannerMiddleware, config=config)
```

## Example 10: Dynamic Text with Version

Include version information in the banner:

```python
from fastapi import FastAPI
from fastapi_env_banner import (
    Environment,
    EnvBannerConfig,
    EnvBannerMiddleware,
    setup_swagger_ui
)

VERSION = "1.2.3"
app = FastAPI(title="My API", version=VERSION)

config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    custom_text=f"🚀 DEVELOPMENT - v{VERSION} 🚀",
    position="top"
)

app.add_middleware(EnvBannerMiddleware, config=config)
setup_swagger_ui(app, config)
```

## Running the Examples

To run any of these examples:

1. Save the code to a file (e.g., `main.py`)
2. Set the environment variable if needed:
   ```bash
   export ENVIRONMENT=development
   ```
3. Run with uvicorn:
   ```bash
   uvicorn main:app --reload
   ```
4. Visit `http://localhost:8000` to see the banner

## Next Steps

- Learn more about [Configuration](configuration.md) options
- Check the [API Reference](../api/config.md)
- Read the [Contributing Guide](../contributing.md)
