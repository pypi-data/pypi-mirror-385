# Mercately WhatsApp Client

A Python client library for integrating Django applications with the Mercately WhatsApp service. This package provides both synchronous and asynchronous clients for easy WhatsApp template message sending.

## Features

- 🚀 **Easy Integration**: Simple API for sending WhatsApp messages
- 🔄 **Sync & Async**: Both synchronous and asynchronous clients
- 📱 **Template Messages**: Send WhatsApp template messages with parameters
- 👥 **Customer Management**: Create and manage customers
- 🔒 **Error Handling**: Comprehensive exception hierarchy
- 📊 **Logging**: Structured logging with privacy protection
- 🔧 **Auto-Configuration**: Automatic discovery from Django settings

## Installation

```bash
pip install mb-mercately-client
```

## Quick Start

### 1. Configuration

Add to your Django `settings.py`:

```python
MERCATELY_CLIENT = {
    'SERVICE_URL': 'https://your-mercately-service-url',
    'AUTH_TOKEN': 'your-auth-token',
    'TIMEOUT': 30,
    'RETRY_ATTEMPTS': 3,
    'RETRY_DELAY': 1,
}
```

Or use environment variables:
```bash
export MERCATELY_SERVICE_URL="https://your-mercately-service-url"
export MERCATELY_SERVICE_TOKEN="your-auth-token"
```

### 2. Basic Usage

```python
from mb_mercately_client import MercatelyClient

# Create client (auto-discovers configuration)
client = MercatelyClient()

# Send a template message
response = client.send_template(
    phone="+1234567890",
    template_id="welcome_template",
    template_params=["John", "Doe"]
)

# Get message identifier (falls back to created_time if message_id is null)
message_id = response.get_message_identifier()
print(f"Message sent! ID: {message_id}")
print(f"Status: {response.get_message_status()}")
print(f"Destination: {response.get_destination()}")
```

### 3. Async Usage

```python
from mercately_client import AsyncMercatelyClient

async def send_message():
    async with AsyncMercatelyClient() as client:
        response = await client.send_template(
            phone="+1234567890",
            template_id="welcome_template",
            template_params=["John", "Doe"]
        )
        print(f"Message sent! ID: {response.message_id}")
```

## Django Integration Examples

### Synchronous View

```python
from django.http import JsonResponse
from mb_mercately_client import MercatelyClient
from mb_mercately_client.exceptions import MercatelyClientError

def send_welcome(request):
    try:
        client = MercatelyClient()
        response = client.send_template(
            phone=request.POST['phone'],
            template_id='welcome_template',
            template_params=[request.user.first_name]
        )
        return JsonResponse({'message_id': response.message_id})
    except MercatelyClientError as e:
        return JsonResponse({'error': str(e)}, status=500)
```


## API Reference

### MercatelyClient

The main synchronous client for the Mercately API.

#### Methods

##### `send_template(phone, template_id, template_params=None, auto_create_customer=True)`

Send a WhatsApp template message.

**Parameters:**
- `phone` (str): Phone number with country code (e.g., '+1234567890')
- `template_id` (str): Template identifier
- `template_params` (List[str], optional): Template parameters in order
- `auto_create_customer` (bool): Whether to create customer if not exists

**Returns:** `TemplateResponse` with message details

**Raises:**
- `InvalidPhoneNumberError`: If phone number format is invalid
- `TemplateNotFoundError`: If template is not found
- `MercatelyAPIError`: If API request fails

##### `get_templates()`

Get available WhatsApp templates.

**Returns:** List of `Template` objects

##### `create_customer(phone, first_name=None, last_name=None, email=None, metadata=None)`

Create a new customer.

**Parameters:**
- `phone` (str): Phone number with country code
- `first_name` (str, optional): Customer first name
- `last_name` (str, optional): Customer last name
- `email` (str, optional): Customer email
- `metadata` (Dict, optional): Additional customer metadata

**Returns:** `Customer` object

##### `get_customer(phone)`

Get customer by phone number.

**Parameters:**
- `phone` (str): Phone number with country code

**Returns:** `Customer` object

**Raises:**
- `CustomerNotFoundError`: If customer is not found

##### `health_check()`

Check service health.

**Returns:** `HealthResponse` with service status

### AsyncMercatelyClient

Asynchronous version of the client with the same methods as `MercatelyClient`, but all methods are async and return awaitable objects.

```python
async with AsyncMercatelyClient() as client:
    response = await client.send_template(...)
```


## Error Handling

The package provides a comprehensive exception hierarchy:

```python
from mb_mercately_client.exceptions import (
    MercatelyClientError,          # Base exception
    MercatelyAPIError,             # API-specific errors
    MercatelyTimeoutError,         # Timeout errors
    MercatelyAuthenticationError,  # Authentication errors
    MercatelyConnectionError,      # Connection errors
    InvalidPhoneNumberError,       # Phone validation errors
    TemplateNotFoundError,         # Template not found
    CustomerNotFoundError,         # Customer not found
    RateLimitError,                # Rate limiting
    ConfigurationError,            # Configuration errors
    ValidationError,               # Data validation errors
)

try:
    response = client.send_template(...)
except InvalidPhoneNumberError:
    print("Invalid phone number format")
except TemplateNotFoundError:
    print("Template not found")
except MercatelyAPIError as e:
    print(f"API Error {e.status_code}: {e.message}")
except MercatelyTimeoutError:
    print("Request timed out")
except MercatelyClientError as e:
    print(f"General error: {e.message}")
```

## Configuration Options

### Django Settings

```python
MERCATELY_CLIENT = {
    'SERVICE_URL': 'https://your-mercately-service-url',
    'AUTH_TOKEN': 'your-auth-token',
    'TIMEOUT': 30,                 # Request timeout in seconds
    'RETRY_ATTEMPTS': 3,           # Number of retry attempts
    'RETRY_DELAY': 1,              # Base delay between retries
}
```

### Environment Variables

```bash
MERCATELY_SERVICE_URL="https://your-mercately-service-url"
MERCATELY_SERVICE_TOKEN="your-auth-token"
```

### Explicit Configuration

```python
client = MercatelyClient(
    service_url="https://api.example.com",
    auth_token="your-token",
    timeout=30,
    retry_attempts=3,
    retry_delay=1.0
)
```

## Testing

For testing your Django application, you can mock the client:

```python
from unittest.mock import patch, Mock

# Mock the client in tests
with patch('mb_mercately_client.MercatelyClient') as mock_client:
    mock_instance = Mock()
    mock_response = Mock()
    mock_response.get_message_identifier.return_value = "test_msg_123"
    mock_instance.send_template.return_value = mock_response
    mock_client.return_value = mock_instance

    # Your test code here
    response = self.client.post('/send-message/', {
        'phone': '+1234567890',
        'template_id': 'welcome'
    })
    self.assertEqual(response.status_code, 200)
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=mercately_client --cov-report=html

# Run type checking
mypy src/mercately_client

# Format code
black src tests examples
isort src tests examples
```

### Project Structure

```
mb-mercately-client/
├── src/
│   └── mb_mercately_client/
│       ├── __init__.py           # Package exports
│       ├── client.py             # Synchronous client
│       ├── async_client.py       # Asynchronous client
│       ├── models.py             # Pydantic models
│       └── exceptions.py         # Custom exceptions
├── tests/                        # Test suite
├── examples/                     # Usage examples
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## Requirements

- Python 3.8+
- requests>=2.28.0
- pydantic>=2.0.0
- httpx>=0.24.0 (for async client)


## API Endpoints

The client communicates with these Mercately API endpoints:

- `POST /whatsapp/template` - Send WhatsApp template messages
- `GET /templates` - Get available templates
- `POST /customers` - Create customer
- `GET /customers/{phone}` - Get customer by phone
- `GET /health` - Health check (no authentication required)

## Phone Number Format

Phone numbers must include the country code and start with '+':

✅ Correct: `+1234567890`, `+521234567890`
❌ Incorrect: `1234567890`, `234567890`

## Logging

The client provides structured logging with privacy protection:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mercately_client')

# Phone numbers are automatically masked in logs
# +1234567890 becomes +12***890
```

## Publishing & Updates

### Initial PyPI Setup

1. **Install build tools:**
```bash
uv add --dev build twine
```

2. **Create PyPI account:**
   - Sign up at [PyPI](https://pypi.org/account/register/)
   - Create API token at [PyPI Token Management](https://pypi.org/manage/account/token/)

3. **Configure authentication:**
```bash
# Create ~/.pypirc file
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
EOF
```

### First Release

1. **Ensure tests pass:**
```bash
uv pip install -e ".[dev]"
pytest
```

2. **Build the package:**
```bash
python -m build
```

3. **Upload to PyPI:**
```bash
twine upload dist/*
```

### Version Updates & New Releases

When adding new features or fixes:

1. **Update version in `pyproject.toml`:**
```toml
[project]
version = "0.2.0"  # Increment version
```

2. **Follow semantic versioning:**
   - `0.1.0` → `0.1.1` (patch: bug fixes)
   - `0.1.0` → `0.2.0` (minor: new features, backward compatible)
   - `0.1.0` → `1.0.0` (major: breaking changes)

3. **Update changelog (optional but recommended):**
```bash
# Add to CHANGELOG.md or include in commit messages
## [0.2.0] - 2024-01-15
### Added
- New feature X
### Fixed
- Bug Y
```

4. **Clean previous builds:**
```bash
rm -rf dist/ build/
```

5. **Build and upload:**
```bash
python -m build
twine upload dist/*
```

### Automated Release Workflow (Recommended)

Create `.github/workflows/release.yml` for automatic releases:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### Quick Release Checklist

- [ ] All tests pass (`pytest`)
- [ ] Version updated in `pyproject.toml`
- [ ] Changes documented
- [ ] Clean build (`rm -rf dist/ build/`)
- [ ] Build package (`python -m build`)
- [ ] Upload to PyPI (`twine upload dist/*`)

### Testing Before Release

Test your package locally before publishing:

```bash
# Build the package
python -m build

# Install locally from wheel
pip install dist/mb_mercately_client-*.whl

# Test in another environment
python -c "from mb_mercately_client import MercatelyClient; print('Import successful')"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Report issues: [GitHub Issues](https://github.com/yourcompany/mb-mercately-client/issues)
- Documentation: [API Documentation](https://docs.yourcompany.com/mercately-client)
- Email: dev@yourcompany.com