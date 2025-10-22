# OMAM AuthKit Python SDK

[![Python Version](https://img.shields.io/pypi/pyversions/omam-authkit)](https://pypi.org/project/omam-authkit/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Official Python SDK for integrating with OMAM AuthKit OAuth 2.0 authentication provider.

## Features

- 🔐 **OAuth 2.0 Authentication** - Full support for authorization code flow
- 🔄 **Automatic Token Refresh** - Built-in token management and refresh
- 🔒 **Secure Token Storage** - Encrypted token storage with cryptography
- 🪝 **Webhook Support** - Verify and handle webhook events
- 🌐 **Framework Integrations** - Django, Flask, and FastAPI support
- ✅ **Type Hints** - Full type annotation support
- 🧪 **Well Tested** - Comprehensive test coverage

## Installation

### Basic Installation

```bash
# Using pip
pip install omam-authkit

# Using poetry
poetry add omam-authkit

# For Django projects
pip install omam-authkit[django]
```

### System Requirements

- Python 3.8+
- Django 3.2+ (optional, for Django integration)
- requests library
- cryptography for secure token handling

## Quick Start

### Basic Python Integration

```python
from omam_authkit import AuthKitClient

# Initialize the client
client = AuthKitClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authkit_url="https://auth.yourdomain.com"
)

# Get authorization URL
auth_url = client.get_authorization_url(
    redirect_uri="http://localhost:8000/callback",
    scopes=["read", "write"]
)

# Exchange code for tokens
tokens = client.exchange_code_for_tokens(
    code="authorization_code",
    redirect_uri="http://localhost:8000/callback"
)

# Get user info
user_info = client.get_user_info(tokens["access_token"])
print(f"Hello, {user_info['email']}!")
```

### Django Integration

#### 1. Configure Settings

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.auth',
    'omam_authkit.django',  # Add this
    'your_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'omam_authkit.django.middleware.AuthKitMiddleware',  # Add this
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

AUTHKIT_CONFIG = {
    'CLIENT_ID': 'your-client-id',
    'CLIENT_SECRET': 'your-client-secret',
    'AUTHKIT_URL': 'https://auth.yourdomain.com',
    'REDIRECT_URI': 'http://localhost:8000/auth/callback'
}
```

#### 2. Configure URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('auth/', include('omam_authkit.django.urls')),
    path('', include('your_app.urls')),
]
```

#### 3. Protected Views

```python
from django.shortcuts import render
from omam_authkit.django.decorators import authkit_required
from omam_authkit.django.utils import get_current_user

@authkit_required
def dashboard(request):
    user = get_current_user(request)
    return render(request, 'dashboard.html', {'user': user})
```

### Flask Integration

```python
from flask import Flask, request, session, redirect
from omam_authkit import AuthKitClient

app = Flask(__name__)
app.secret_key = 'your-secret-key'

client = AuthKitClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authkit_url="https://auth.yourdomain.com"
)

@app.route('/login')
def login():
    auth_url = client.get_authorization_url(
        redirect_uri="http://localhost:5000/callback"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    tokens = client.exchange_code_for_tokens(code)
    session['access_token'] = tokens['access_token']
    return redirect('/dashboard')
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from omam_authkit import AuthKitClient

app = FastAPI()
client = AuthKitClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authkit_url="https://auth.yourdomain.com"
)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_info = client.get_user_info(credentials.credentials)
        return user_info
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected(user = Depends(verify_token)):
    return {"message": f"Hello {user['email']}"}
```

## Token Management

### Automatic Token Refresh

```python
from omam_authkit import TokenManager

# Initialize token manager
token_manager = TokenManager(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authkit_url="https://auth.yourdomain.com"
)

# Get valid access token (auto-refreshes if needed)
access_token = token_manager.get_valid_token(refresh_token)

# Check if token is expired
is_expired = token_manager.is_token_expired(access_token)
```

### Secure Token Storage

```python
from omam_authkit.storage import SecureTokenStorage

# Initialize secure storage
storage = SecureTokenStorage(
    encryption_key="your-encryption-key"
)

# Store tokens securely
storage.store_tokens("user_id", tokens)

# Retrieve tokens
tokens = storage.get_tokens("user_id")
```

## Webhook Integration

```python
from flask import Flask, request
from omam_authkit.webhooks import WebhookHandler

app = Flask(__name__)

webhook_handler = WebhookHandler(
    secret="your-webhook-secret"
)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        event = webhook_handler.verify_and_parse(request.data)

        if event['type'] == 'user.login':
            print(f"User {event['user_id']} logged in")
        elif event['type'] == 'user.logout':
            print(f"User {event['user_id']} logged out")

    except Exception as e:
        return {"error": str(e)}, 400

    return {"status": "success"}, 200
```

## API Reference

### AuthKitClient

#### `__init__(client_id, client_secret, authkit_url, timeout=30, retry_attempts=3)`

Initialize the AuthKit client.

#### `get_authorization_url(redirect_uri, scopes=None, state=None)`

Generate the authorization URL for OAuth 2.0 flow.

#### `exchange_code_for_tokens(code, redirect_uri)`

Exchange authorization code for access and refresh tokens.

#### `refresh_access_token(refresh_token)`

Refresh an expired access token using a refresh token.

#### `get_user_info(access_token)`

Get user information using an access token.

#### `revoke_token(token)`

Revoke an access or refresh token.

#### `introspect_token(token)`

Introspect a token to get its metadata.

#### `register_user(email, password, password_confirm, first_name=None, last_name=None)`

Register a new user account.

### TokenManager

#### `get_valid_token(refresh_token, force_refresh=False)`

Get a valid access token, refreshing if necessary.

#### `is_token_expired(access_token, buffer_seconds=60)`

Check if an access token is expired.

#### `validate_token(access_token)`

Validate a token using introspection endpoint.

### WebhookHandler

#### `verify_and_parse(payload, signature=None, timestamp=None)`

Verify webhook signature and parse the payload.

#### `verify_signature(payload, signature, timestamp=None)`

Verify webhook signature.

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `client_id` | string | - | Your OAuth 2.0 client ID |
| `client_secret` | string | - | Your OAuth 2.0 client secret |
| `authkit_url` | string | - | Base URL of your AuthKit instance |
| `timeout` | int | 30 | Request timeout in seconds |
| `retry_attempts` | int | 3 | Number of retry attempts for failed requests |

## Best Practices

### ✅ Do

- Always validate tokens before processing requests
- Use secure token storage with encryption
- Implement proper error handling for authentication failures
- Set up webhooks for real-time user event notifications
- Use environment variables for sensitive configuration
- Implement proper logging for authentication events

### ❌ Don't

- Don't store tokens in plain text
- Don't ignore token expiration checks
- Don't expose client secrets in your code
- Don't skip webhook signature verification
- Don't forget to handle network failures gracefully
- Don't log sensitive authentication data

## Examples

Check out the [examples](./examples/) directory for complete integration examples:

- [Flask Integration](./examples/flask_example.py)
- [FastAPI Integration](./examples/fastapi_example.py)
- [Django Integration](./examples/django_example.py)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/omam-authkit-python-sdk.git
cd omam-authkit-python-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=omam_authkit --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black omam_authkit

# Lint code
flake8 omam_authkit

# Type checking
mypy omam_authkit
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://docs.omam.com](https://docs.omam.com)
- Issues: [GitHub Issues](https://github.com/yourusername/omam-authkit-python-sdk/issues)
- Email: support@omam.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.
