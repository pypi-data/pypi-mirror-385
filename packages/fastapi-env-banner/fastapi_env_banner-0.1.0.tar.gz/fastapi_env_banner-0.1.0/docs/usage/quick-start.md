# Quick Start

This guide will help you get started with FastAPI Environment Banner in just a few minutes.

## Basic Setup

The simplest way to add environment banners to your FastAPI application:

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware, setup_swagger_ui

# Create your FastAPI app
app = FastAPI(title="My API")

# Configure the banner (auto-detects from ENVIRONMENT variable)
config = EnvBannerConfig.from_env()

# Add the middleware
app.add_middleware(EnvBannerMiddleware, config=config)

# Setup Swagger UI with banner
setup_swagger_ui(app, config)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

That's it! Your application now has environment banners.

## Setting the Environment

Set the `ENVIRONMENT` variable before running your application:

```bash
export ENVIRONMENT=development
uvicorn main:app --reload
```

Or create a `.env` file:

```env
ENVIRONMENT=development
```

## Supported Environment Values

The library recognizes these environment values:

- `local` → Green banner
- `dev`, `development` → Blue banner
- `stage`, `staging` → Orange banner
- `prod`, `production` → Red banner (disabled by default)
- `test`, `testing` → Purple banner

## Manual Configuration

If you prefer to configure the banner manually:

```python
from fastapi import FastAPI
from fastapi_env_banner import Environment, EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

config = EnvBannerConfig(
    environment=Environment.DEVELOPMENT,
    enabled=True
)

app.add_middleware(EnvBannerMiddleware, config=config)
```

## Minimal Example

The absolute minimum code needed:

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()
app.add_middleware(EnvBannerMiddleware, config=EnvBannerConfig.from_env())
```

## Running the Application

Start your FastAPI application:

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` to see the banner in action!

## What's Next?

- Learn about [Configuration](configuration.md) options
- Check out more [Examples](examples.md)
- Explore the [API Reference](../api/config.md)
