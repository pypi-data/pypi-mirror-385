<div align="center">

# FastAPI Environment Banner

<img src="public/logo.svg" alt="FastAPI Environment Banner Logo" width="400">

[![PyPI version](https://badge.fury.io/py/fastapi-env-banner.svg)](https://badge.fury.io/py/fastapi-env-banner)
[![Python Versions](https://img.shields.io/pypi/pyversions/fastapi-env-banner.svg)](https://pypi.org/project/fastapi-env-banner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://pinnlabs.github.io/fastapi-env-banner/)

</div>

<p align="center">
A lightweight and simple library for adding visual environment banners to FastAPI applications.<br>
Inspired by <code>django-env-notice</code>, but specifically designed for FastAPI with a focus on simplicity and ease of integration.
</p>

---

<div align="center">

### See it in action

<img src="public/demo.png" alt="FastAPI Environment Banner Demo" width="800">

*Visual environment indicators help prevent mistakes by clearly showing which environment you're working in*

</div>

---

## Features

- **Simple and Lightweight**: Just a few lines of code to integrate
- **Visual and Intuitive**: Colorful banners that clearly differentiate environments
- **Highly Configurable**: Customize colors, texts, and positions
- **Swagger UI Support**: Banner also appears in API documentation
- **Zero Configuration**: Works out-of-the-box with sensible defaults
- **Secure**: Banner disabled in production by default

## Documentation

Full documentation is available at **[pinnlabs.github.io/fastapi-env-banner](https://pinnlabs.github.io/fastapi-env-banner/)**

## Installation

```bash
pip install fastapi-env-banner
```

or if you are using `uv`:

```bash
uv add fastapi-env-banner
```

### Basic Setup

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

### Manual Configuration

```python
from fastapi_env_banner import Environment, EnvBannerConfig

# Custom configuration
config = EnvBannerConfig(
    environment=Environment.STAGING,
    enabled=True,
    custom_text="STAGING ENVIRONMENT",
    custom_color="#FF6B6B",
    position="top",  # or "bottom"
    show_in_swagger=True
)
```

## Supported Environments

The library supports the following environments with pre-defined colors:

| Environment | Default Color | Default Text |
|----------|------------|-------------|
| **LOCAL** | Green (`#4CAF50`) | LOCAL ENVIRONMENT |
| **DEVELOPMENT** | Blue (`#2196F3`) | DEVELOPMENT ENVIRONMENT |
| **STAGING** | Orange (`#FF9800`) | STAGING ENVIRONMENT |
| **PRODUCTION** | Red (`#F44336`) | PRODUCTION ENVIRONMENT |
| **TESTING** | Purple (`#9C27B0`) | TESTING ENVIRONMENT |

## Detailed Configuration

### Using Environment Variables

Set the `ENVIRONMENT` variable (or another of your choice):

```bash
export ENVIRONMENT=staging
```

Accepted values:
- `local`
- `dev`, `development`
- `stage`, `staging`
- `prod`, `production`
- `test`, `testing`

### Configuration Parameters

```python
EnvBannerConfig(
    environment: Environment = Environment.LOCAL,
    enabled: bool = True,
    custom_text: Optional[str] = None,
    custom_color: Optional[str] = None,
    position: str = "top",  # "top" or "bottom"
    show_in_swagger: bool = True
)
```

## Examples

### Example 1: Minimal Configuration

```python
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()
app.add_middleware(EnvBannerMiddleware, config=EnvBannerConfig.from_env())
```

### Example 2: Full Customization

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
    custom_text="⚠️ TEST ENVIRONMENT - DO NOT USE IN PRODUCTION ⚠️",
    custom_color="#E91E63",
    position="bottom",
    show_in_swagger=True
)

app.add_middleware(EnvBannerMiddleware, config=config)
setup_swagger_ui(app, config)
```

### Example 3: Disable in Production

```python
import os
from fastapi import FastAPI
from fastapi_env_banner import EnvBannerConfig, EnvBannerMiddleware

app = FastAPI()

# Completely disable in production
is_production = os.getenv("ENVIRONMENT") == "production"

config = EnvBannerConfig.from_env()
config.enabled = not is_production

app.add_middleware(EnvBannerMiddleware, config=config)
```

## Security

By default, the banner **is NOT displayed in production environment** as a security measure. This prevents environment information from being accidentally exposed.

To force display in production (not recommended):

```python
config = EnvBannerConfig(
    environment=Environment.PRODUCTION,
    enabled=True  # Force display
)
```

## How It Works

1. **Middleware**: Intercepts HTML responses and automatically injects the banner
2. **Templates**: Clean, pythonic HTML generation using string templates
3. **Swagger UI**: Customizes the documentation page to include the banner
4. **Zero Impact**: Does not affect JSON APIs or other non-HTML responses
5. **Performance**: Minimal overhead, only processes HTML responses

## Contributing

Contributions are welcome! Feel free to:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [django-env-notice](https://github.com/dizballanze/django-admin-env-notice)
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Developed by [PinnLabs](https://github.com/pinnlabs)

## Support

If you encounter any issues or have suggestions, please [open an issue](https://github.com/pinnlabs/fastapi-env-banner/issues).

---

Made with ❤️ by PinnLabs
