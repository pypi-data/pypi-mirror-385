# Usage Examples

This folder contains practical examples of how to use the `fastapi-env-banner` library.

## 📁 Files

### 1. `basic_example.py`
Basic example showing the simplest possible configuration.

**Features:**
- Automatic environment detection via `ENVIRONMENT` variable
- Default banner with pre-defined colors
- Swagger UI integration
- HTML demonstration page

**How to run:**
```bash
# Install dependencies
pip install fastapi uvicorn

# Run with local environment (default)
python basic_example.py

# Or set a specific environment
ENVIRONMENT=staging python basic_example.py
```

Access: http://localhost:8000

### 2. `custom_example.py`
Advanced example with fully customized configuration.

**Features:**
- Manual environment configuration
- Custom banner text
- Custom color
- Banner positioned at the bottom
- Modern visual interface

**How to run:**
```bash
python custom_example.py
```

Access: http://localhost:8001

## 🎯 Testing Different Environments

### Local (Green)
```bash
ENVIRONMENT=local python basic_example.py
```

### Development (Blue)
```bash
ENVIRONMENT=development python basic_example.py
```

### Staging (Orange)
```bash
ENVIRONMENT=staging python basic_example.py
```

### Testing (Purple)
```bash
ENVIRONMENT=testing python basic_example.py
```

### Production (Red - Banner disabled by default)
```bash
ENVIRONMENT=production python basic_example.py
```

## 📝 Notes

- The banner only appears on HTML pages, not in JSON responses
- By default, the banner is not displayed in production environment
- You can customize colors, texts, and positions as needed
- The banner also appears in Swagger UI documentation

## 🔗 Useful Links

- [Main Documentation](../README.md)
- [Source Code](../fastapi_env_banner/)
- [PyPI Package](https://pypi.org/project/fastapi-env-banner/)
