# Installation

## Requirements

- Python 3.12 or higher
- FastAPI 0.119.0 or higher
- Starlette 0.48.0 or higher

## Install from PyPI

The easiest way to install FastAPI Environment Banner is using pip:

```bash
pip install fastapi-env-banner
```

## Install with uv

If you're using [uv](https://github.com/astral-sh/uv) for faster package management:

```bash
uv add fastapi-env-banner
```

## Install from Source

To install the latest development version from GitHub:

```bash
pip install git+https://github.com/pinnlabs/fastapi-env-banner.git
```

Or clone the repository and install locally:

```bash
git clone https://github.com/pinnlabs/fastapi-env-banner.git
cd fastapi-env-banner
pip install -e .
```

## Verify Installation

After installation, verify that the package is correctly installed:

```python
import fastapi_env_banner

print(fastapi_env_banner.__version__)
```

## Development Installation

If you want to contribute to the project, install it with development dependencies:

```bash
# Clone the repository
git clone https://github.com/pinnlabs/fastapi-env-banner.git
cd fastapi-env-banner

# Install with dev dependencies
pip install -e ".[dev]"
```

This will install additional packages for testing and development:

- pytest
- pytest-asyncio
- pytest-cov
- httpx
- uvicorn

## Next Steps

Once installed, head over to the [Quick Start](usage/quick-start.md) guide to learn how to integrate FastAPI Environment Banner into your application.
