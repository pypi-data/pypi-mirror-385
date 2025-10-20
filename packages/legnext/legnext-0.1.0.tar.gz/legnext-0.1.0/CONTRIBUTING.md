# Contributing to Legnext Python SDK

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/legnext-python
   cd legnext-python
   ```

2. Install dependencies with uv:
   ```bash
   uv pip install -e ".[dev]"
   ```

3. Set up pre-commit hooks (optional):
   ```bash
   pre-commit install
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=legnext --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run tests matching pattern
pytest -k "test_client"
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint
ruff check src tests

# Type check
mypy src

# Run all checks
black src tests && isort src tests && ruff check src tests && mypy src
```

### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests

3. Run tests and linting:
   ```bash
   pytest
   black src tests
   ruff check src tests
   mypy src
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

5. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

- Write clear, descriptive commit messages
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow the existing code style
- Keep PRs focused on a single feature/fix

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for public APIs
- Maximum line length: 100 characters
- Use Black for formatting
- Use isort for import sorting

## Testing Guidelines

- Write tests for all new features
- Maintain test coverage above 80%
- Use fixtures for common test data
- Mock external API calls
- Test both success and error cases

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include usage examples in docstrings
- Update CHANGELOG.md with notable changes

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- MAJOR version for incompatible API changes
- MINOR version for new functionality (backwards compatible)
- PATCH version for bug fixes (backwards compatible)

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a GitHub release
4. CI will automatically publish to PyPI

## Questions?

Feel free to open an issue for any questions or concerns.

Thank you for contributing!
