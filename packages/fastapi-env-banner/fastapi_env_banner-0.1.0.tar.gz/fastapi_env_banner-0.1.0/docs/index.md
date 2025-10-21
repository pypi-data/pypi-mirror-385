# Get Started here

## About

**FastAPI Environment Banner** is a lightweight and simple library for adding visual environment banners to FastAPI applications — inspired by `django-env-notice`, but specifically designed for FastAPI with a focus on simplicity and ease of integration.

It helps you prevent mistakes by clearly showing which environment you're working in with colorful, visual banners.

## Why FastAPI Environment Banner?

FastAPI Environment Banner was designed with Python developers in mind, offering a modern, clean, and extensible API to handle environment indicators. It stands out from other libraries by:

- ✅ **Simple and Lightweight**: Just a few lines of code to integrate
- ✅ **Visual and Intuitive**: Colorful banners that clearly differentiate environments
- ✅ **Highly Configurable**: Customize colors, texts, and positions
- ✅ **Swagger UI Support**: Banner also appears in API documentation
- ✅ **Zero Configuration**: Works out-of-the-box with sensible defaults
- ✅ **Secure**: Banner disabled in production by default

## Installation

```bash
pip install fastapi-env-banner
```

or if you are using `uv`:

```bash
uv add fastapi-env-banner
```

## Quick Example

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware, setup_swagger_ui

# Create FastAPI application
app = FastAPI(title="My API")

# Configure banner (auto-detects from ENVIRONMENT variable)
config = EnvBannerConfig.from_env()

# Add middleware
app.add_middleware(EnvBannerMiddleware, config=config)

# Setup Swagger UI with banner
setup_swagger_ui(app, config)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Usage

You can use FastAPI Environment Banner to add visual indicators before mounting the app:

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware, setup_swagger_ui

# Create FastAPI application
app = FastAPI(title="My API")

# Configure banner
config = EnvBannerConfig.from_env()

# Add middleware
app.add_middleware(EnvBannerMiddleware, config=config)

# Setup Swagger UI with banner
setup_swagger_ui(app, config)

@app.get("/")
async def root():
    return {
        "env": config.environment.value,
        "message": "Hello World"
    }
```

## Supported Environments

The library supports the following environments with pre-defined colors:

| Environment | Default Color | Default Text |
|-------------|---------------|--------------|
| **LOCAL** | Green (`#4CAF50`) | LOCAL ENVIRONMENT |
| **DEVELOPMENT** | Blue (`#2196F3`) | DEVELOPMENT ENVIRONMENT |
| **STAGING** | Orange (`#FF9800`) | STAGING ENVIRONMENT |
| **PRODUCTION** | Red (`#F44336`) | PRODUCTION ENVIRONMENT |
| **TESTING** | Purple (`#9C27B0`) | TESTING ENVIRONMENT |

## Advanced Options

```python
from fastapi_env_banner import Environment, EnvBannerConfig

config = EnvBannerConfig(
    environment=Environment.STAGING,
    enabled=True,
    custom_text="⚠️ STAGING ENVIRONMENT ⚠️",
    custom_color="#FF9800",
    position="top",  # or "bottom"
    show_in_swagger=True
)
```

If any configuration is invalid, the library will use sensible defaults and continue working.

## Environment Detection

The library can automatically detect your environment from environment variables:

```python
from fastapi_env_banner import EnvBannerConfig

# Reads from ENVIRONMENT variable
config = EnvBannerConfig.from_env()

# Or specify a custom variable name
config = EnvBannerConfig.from_env(env_var="APP_ENV")
```

Accepted values:
- `local`
- `dev`, `development`
- `stage`, `staging`
- `prod`, `production`
- `test`, `testing`
