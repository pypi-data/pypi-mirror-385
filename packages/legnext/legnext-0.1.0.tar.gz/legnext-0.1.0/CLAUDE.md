# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Legnext Python SDK** - an official Python client library for the Legnext AI API. The SDK provides comprehensive access to Midjourney-powered image and video generation capabilities with both synchronous and asynchronous support.

## Quick Reference

### Most Common Commands
```bash
# Setup
uv pip install -e ".[dev]"         # Install package in dev mode

# Testing
pytest                              # Run all tests
pytest tests/test_client.py         # Run specific file
pytest -k "test_client"             # Run tests by name pattern
pytest -v                           # Verbose output
pytest --cov=legnext                # With coverage report

# Code Quality
make format                         # Format with black + isort
make lint                           # Lint with ruff
make type-check                     # Type check with mypy
make dev                            # Run all checks + tests
```

## Development Commands

### Setup
```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Testing
```bash
# Run all tests with coverage
pytest

# Or using make
make test

# Run specific test file
pytest tests/test_client.py

# Run specific test function
pytest tests/test_client.py::test_client_initialization

# Run tests matching a pattern
pytest -k "test_client"

# Run with verbose output
pytest -v

# Run async tests only
pytest -k "async"
```

### Code Quality
```bash
# Format code (runs black and isort)
make format

# Lint code
make lint

# Type check
make type-check

# Run all quality checks + tests
make dev
```

### Building & Publishing
```bash
# Build distribution packages
make build

# Publish to PyPI (requires credentials)
make publish
```

## Architecture

### Client Design Pattern

The SDK follows a **resource-based architecture** similar to the OpenAI SDK:

1. **Client Layer** (`client.py`):
   - `Client` (sync) and `AsyncClient` (async) are the entry points
   - Each client initializes an HTTP client and resource objects
   - Support context managers for automatic cleanup

2. **HTTP Client Layer** (`_internal/http_client.py`):
   - `HTTPClient` (sync) and `AsyncHTTPClient` (async)
   - Handles authentication via `x-api-key` header
   - Implements exponential backoff retry logic (default: 3 retries)
   - Automatic error parsing and exception raising
   - Default timeout: 60s, Base URL: `https://api.legnext.ai/api`

3. **Resource Layer** (`resources/`):
   - Each resource maps to an API domain (midjourney, tasks, account)
   - Methods directly correspond to API endpoints
   - Both sync and async implementations for each resource
   - Resources receive the HTTP client in their constructor

4. **Types Layer** (`types/`):
   - `requests.py`: Pydantic request models for all operations
   - `responses.py`: Pydantic response models
   - `enums.py`: Type-safe enums (JobStatus, TaskType, etc.)
   - `errors.py`: Custom exception hierarchy

### Key Design Decisions

1. **Method Naming**: Resource methods are named exactly as API endpoints (e.g., `diffusion()`, `variation()`, `upscale()`) for clarity and direct mapping to API docs.

2. **Type Safety**: All request/response data uses Pydantic v2 models with strict validation. The SDK uses `mypy --strict` mode.

3. **Dual API**: Complete parallel implementations for sync (`Client`) and async (`AsyncClient`) to support both use cases without compromise.

4. **Error Handling**: Specific exception types for each HTTP status code:
   - `AuthenticationError` (401)
   - `NotFoundError` (404)
   - `RateLimitError` (429)
   - `ValidationError` (400)
   - `ServerError` (5xx)

5. **Task Polling**: The `tasks.wait_for_completion()` method provides built-in polling with configurable timeout, interval, and progress callbacks.

## Code Organization

```
src/legnext/
├── __init__.py           # Public API exports
├── client.py             # Client and AsyncClient classes
├── webhook.py            # Webhook verification and handling
├── _internal/            # Internal implementation details
│   └── http_client.py    # HTTP client with retry logic
├── resources/            # API resource classes
│   ├── midjourney.py     # 19 image/video operations
│   ├── tasks.py          # Task management and polling
│   └── account.py        # Account info and active tasks
└── types/                # Data models
    ├── enums.py          # Enums (JobStatus, TaskType, etc.)
    ├── requests.py       # Request models (19 different types)
    ├── responses.py      # Response models
    ├── errors.py         # Exception classes
    └── shared.py         # Shared models (ImageSize, etc.)
```

## API Coverage

The SDK provides **19 Midjourney operations** across three categories:

**Image Generation (15 operations):**
- Basic: `diffusion`, `variation`, `upscale`, `reroll`
- Composition: `blend`, `describe`, `shorten`
- Extension: `pan`, `outpaint`
- Editing: `inpaint`, `remix`, `edit`, `upload_paint`
- Enhancement: `retexture`, `remove_background`, `enhance`

**Video Generation (3 operations):**
- `video_diffusion`, `extend_video`, `video_upscale`

**Utilities:**
- Task polling with `tasks.wait_for_completion()`
- Account management with `account.get_info()` and `account.get_active_tasks()`

## Testing with Pytest

### Pytest Basics

**What is pytest?**
Pytest is a testing framework that makes it easy to write small, readable tests. It automatically discovers test files (starting with `test_`) and test functions (starting with `test_`).

**Running tests:**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_client.py

# Run specific test function
pytest tests/test_client.py::test_client_initialization

# Run tests matching a pattern
pytest -k "test_client"

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=legnext --cov-report=term-missing
```

### Test Organization

```
tests/
├── conftest.py          # Shared fixtures (api_key, mock_job_id, etc.)
├── test_client.py       # Client initialization and context manager tests
├── test_types.py        # Pydantic model validation tests
├── test_webhook.py      # Webhook verification tests
└── test_errors.py       # Error handling tests
```

### Using Fixtures

**What are fixtures?**
Fixtures are reusable test data or setup code. They're defined in `conftest.py` and automatically available to all tests.

**Available fixtures:**
- `api_key` - Returns `"test_api_key_12345"`
- `mock_job_id` - Returns a UUID string
- `mock_task_response` - Returns a complete task response dict
- `mock_account_info` - Returns account info dict

**Example usage:**
```python
def test_client_initialization(api_key):
    """The api_key fixture is automatically injected."""
    client = Client(api_key=api_key)
    assert client._http.api_key == api_key
```

### Writing Tests

**Basic test structure:**
```python
def test_something():
    """Always include a docstring explaining what you're testing."""
    # Arrange: Set up test data
    request = DiffusionRequest(text="a sunset")

    # Act: Execute the code being tested
    result = request.text

    # Assert: Check the results
    assert result == "a sunset"
```

**Testing validation with pytest.raises:**
```python
def test_diffusion_request_validation():
    """Test that validation errors are raised correctly."""
    with pytest.raises(ValidationError):
        DiffusionRequest(text="")  # Text too short
```

**Testing context managers:**
```python
def test_client_context_manager(api_key):
    """Test that resources are properly cleaned up."""
    with Client(api_key=api_key) as client:
        assert client._http._client is not None

    # After exiting, client should be closed
    assert client._http._client is None
```

### Async Tests

For testing async code, use `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_client_context_manager(api_key):
    """Test async client as context manager."""
    from legnext import AsyncClient

    async with AsyncClient(api_key=api_key) as client:
        assert client._http._client is not None

    assert client._http._client is None
```

**Note:** The `asyncio_mode = "auto"` in `pyproject.toml` means pytest automatically detects async tests.

### Mocking HTTP Requests

To test without making real API calls, use `pytest-mock`:

```python
def test_diffusion_with_mock(api_key, mocker, mock_task_response):
    """Test diffusion with mocked HTTP response."""
    # Create a mock that returns mock_task_response
    mock_request = mocker.patch(
        "legnext._internal.http_client.HTTPClient.request",
        return_value=mock_task_response
    )

    client = Client(api_key=api_key)
    response = client.midjourney.diffusion(text="test")

    # Verify the mock was called correctly
    mock_request.assert_called_once()
    assert response.job_id == mock_task_response["job_id"]
```

### Test Coverage

**Viewing coverage:**
```bash
# Terminal output with missing lines
pytest --cov=legnext --cov-report=term-missing

# Generate HTML report (opens in browser)
pytest --cov=legnext --cov-report=html
open htmlcov/index.html
```

**Coverage expectations:**
- Maintain coverage above 80%
- All public APIs should have tests
- Test both success and error cases
- Test edge cases (empty strings, None values, boundary conditions)

### Common Testing Patterns

**1. Testing Pydantic Models:**
```python
def test_model_valid():
    """Test valid model creation."""
    model = DiffusionRequest(text="test")
    assert model.text == "test"

def test_model_validation():
    """Test validation errors."""
    with pytest.raises(ValidationError):
        DiffusionRequest(text="")
```

**2. Testing Enums:**
```python
def test_enum_values():
    """Test enum string values."""
    assert JobStatus.PENDING == "pending"
    assert JobStatus.COMPLETED == "completed"
```

**3. Testing Resource Methods:**
```python
def test_resource_method(api_key, mocker, mock_task_response):
    """Test a resource method."""
    mock_request = mocker.patch(
        "legnext._internal.http_client.HTTPClient.request",
        return_value=mock_task_response
    )

    client = Client(api_key=api_key)
    response = client.midjourney.diffusion(text="test")

    # Verify HTTP request was correct
    mock_request.assert_called_once_with(
        "POST",
        "/diffusion",
        json={"text": "test", "callback": None}
    )
```

### Testing Guidelines

- Write a test for every new feature or bug fix
- Test both sync and async code paths
- Mock external HTTP calls - never make real API requests in tests
- Use descriptive test names that explain what's being tested
- Include docstrings in test functions
- Test error cases, not just happy paths
- Keep tests independent - one test shouldn't depend on another

## Type Checking

The project uses strict mypy configuration:
- All functions must have type hints
- `disallow_untyped_defs = true`
- Use `Union[X, None]` instead of `Optional[X]` for consistency

## Formatting & Style

- **Black**: Line length 100, Python 3.10+ targets
- **isort**: Black-compatible profile
- **Ruff**: Targets py310, enforces E/F/I/N/W/B/C90 rules
- Use `make format` before committing

## Python Version Support

- Requires Python 3.10+
- CI tests on Python 3.10, 3.11, 3.12
- CI tests on Ubuntu, macOS, Windows

## Dependencies

**Core runtime:**
- `pydantic>=2.0.0` - Data validation
- `httpx>=0.27.0` - HTTP client (sync + async)
- `typing-extensions>=4.5.0` - Backports

**Development only:**
- pytest, pytest-asyncio, pytest-cov, pytest-mock
- mypy, ruff, black, isort

## Common Patterns

### Creating a New Resource Method

1. Define request model in `types/requests.py` if needed
2. Add method to both sync and async resource classes
3. Method should: validate input → call `_http.request()` → return validated response
4. Include docstring with Args, Returns, and Example
5. Add tests for both sync and async versions

### Adding a New Enum

1. Add to `types/enums.py` as a string enum
2. Export from `types/__init__.py`
3. Use in request/response models as needed

### Error Handling Best Practices

- Let exceptions bubble up from HTTP client - don't catch unless handling specifically
- Use specific exception types to help users handle different error cases
- Include original error in exception chain for debugging

## Webhook Support

The SDK includes webhook utilities:
- `WebhookVerifier`: Validates webhook signatures
- `WebhookHandler`: Decorator-based event handling
- Built-in Flask-compatible webhook server for testing

See `examples/06_webhook_handler.py` for usage patterns.

## CI/CD

GitHub Actions workflows:
- **Test**: Runs on push/PR, tests across OS and Python versions
- **Publish**: Triggers on GitHub release, publishes to PyPI

Pre-commit hooks enforce formatting and linting before commits.
