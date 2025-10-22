"""
Django utility functions for AuthKit
"""

from typing import Optional, Dict, Any
from django.http import HttpRequest
from django.conf import settings

from ..client import AuthKitClient


def get_current_user(request: HttpRequest) -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from the request.

    Args:
        request: Django HTTP request

    Returns:
        User info dictionary or None if not authenticated
    """
    return getattr(request, "authkit_user", None)


def is_authenticated(request: HttpRequest) -> bool:
    """
    Check if the request is authenticated.

    Args:
        request: Django HTTP request

    Returns:
        True if authenticated, False otherwise
    """
    return getattr(request, "authkit_authenticated", False)


def get_authkit_client() -> AuthKitClient:
    """
    Get an AuthKit client instance configured from Django settings.

    Returns:
        AuthKitClient instance

    Raises:
        ImproperlyConfigured: If AUTHKIT_CONFIG is not set
    """
    from django.core.exceptions import ImproperlyConfigured

    config = getattr(settings, "AUTHKIT_CONFIG", None)

    if not config:
        raise ImproperlyConfigured(
            "AUTHKIT_CONFIG is not set in Django settings"
        )

    return AuthKitClient(
        client_id=config.get("CLIENT_ID", ""),
        client_secret=config.get("CLIENT_SECRET", ""),
        authkit_url=config.get("AUTHKIT_URL", ""),
    )


def get_authorization_url(
    redirect_uri: str = None, scopes: list = None, state: str = None
) -> str:
    """
    Generate an authorization URL.

    Args:
        redirect_uri: Callback URL (defaults to AUTHKIT_CONFIG['REDIRECT_URI'])
        scopes: OAuth scopes (defaults to ['read'])
        state: State parameter for CSRF protection

    Returns:
        Authorization URL
    """
    client = get_authkit_client()
    config = getattr(settings, "AUTHKIT_CONFIG", {})

    redirect_uri = redirect_uri or config.get("REDIRECT_URI", "")

    return client.get_authorization_url(
        redirect_uri=redirect_uri, scopes=scopes, state=state
    )
