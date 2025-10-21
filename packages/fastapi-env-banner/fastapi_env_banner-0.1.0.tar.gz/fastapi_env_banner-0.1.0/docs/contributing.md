# Contributing

Thank you for your interest in contributing to FastAPI Environment Banner! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- pip or uv for package management
- Git

### Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/fastapi-env-banner.git
cd fastapi-env-banner
```

2. **Install development dependencies**

```bash
pip install -e ".[dev]"
```

Or with uv:

```bash
uv pip install -e ".[dev]"
```

3. **Verify installation**

```bash
pytest
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=fastapi_env_banner --cov-report=html
```

### Run specific test file

```bash
pytest tests/test_config.py
```

### Run specific test

```bash
pytest tests/test_config.py::TestEnvironmentEnum::test_environment_values
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Example

```python
def get_banner_color(self) -> str:
    """Get the banner background color based on environment.
    
    Returns:
        str: Hexadecimal color code
    """
    if self.custom_color:
        return self.custom_color
    
    return self.color_map.get(self.environment, "#4CAF50")
```

## Testing Guidelines

- Write tests for all new features
- Ensure tests cover both happy path and edge cases
- Aim for >90% code coverage
- Use descriptive test names
- Group related tests in classes

### Test Structure

```python
class TestFeatureName:
    """Tests for feature description."""
    
    def test_happy_path(self):
        """Test the expected behavior."""
        # Arrange
        config = EnvBannerConfig()
        
        # Act
        result = config.get_banner_color()
        
        # Assert
        assert result == "#4CAF50"
    
    def test_edge_case(self):
        """Test edge case behavior."""
        # Test implementation
```

## Pull Request Process

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests and ensure they pass**

```bash
pytest
```

4. **Commit your changes**

```bash
git add .
git commit -m "Add feature: description of your changes"
```

5. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

6. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Submit the PR

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code follows project style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary files are included
- [ ] Branch is up to date with main

## Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Minimal steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: Python version, OS, library version
6. **Code Sample**: Minimal code that reproduces the issue

## Feature Requests

When requesting features, please include:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Any other relevant information

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all new functions and classes
- Update examples if behavior changes
- Keep documentation clear and concise

## Release Process

Releases are managed by maintainers. The process includes:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag
4. Build and publish to PyPI

## Questions?

If you have questions, feel free to:

- Open an issue for discussion
- Check existing issues and PRs
- Review the documentation

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards others

Thank you for contributing! 🎉
