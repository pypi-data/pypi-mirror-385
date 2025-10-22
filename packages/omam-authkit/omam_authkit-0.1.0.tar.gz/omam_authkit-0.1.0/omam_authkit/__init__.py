"""
OMAM AuthKit Python SDK

A Python client library for integrating with Omam AuthKit OAuth 2.0 authentication provider.
"""

from .client import AuthKitClient
from .token_manager import TokenManager
from .exceptions import (
    AuthKitError,
    AuthenticationError,
    TokenExpiredError,
    InvalidTokenError,
    APIError,
)

__version__ = "0.1.0"
__all__ = [
    "AuthKitClient",
    "TokenManager",
    "AuthKitError",
    "AuthenticationError",
    "TokenExpiredError",
    "InvalidTokenError",
    "APIError",
]
