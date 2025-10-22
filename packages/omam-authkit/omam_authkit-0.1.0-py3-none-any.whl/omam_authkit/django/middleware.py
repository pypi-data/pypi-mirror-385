"""
Django middleware for AuthKit authentication
"""

from typing import Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings

from ..client import AuthKitClient
from ..exceptions import InvalidTokenError, APIError


class AuthKitMiddleware:
    """
    Django middleware for AuthKit OAuth 2.0 authentication.

    Adds user information to the request object if a valid access token is present.

    Configuration in settings.py:
        AUTHKIT_CONFIG = {
            'CLIENT_ID': 'your-client-id',
            'CLIENT_SECRET': 'your-client-secret',
            'AUTHKIT_URL': 'https://auth.yourdomain.com',
            'REDIRECT_URI': 'http://localhost:8000/auth/callback'
        }

    Usage:
        Add to MIDDLEWARE in settings.py:
        MIDDLEWARE = [
            ...
            'omam_authkit.django.middleware.AuthKitMiddleware',
            ...
        ]
    """

    def __init__(self, get_response: Callable):
        """
        Initialize the middleware.

        Args:
            get_response: Django's get_response callable
        """
        self.get_response = get_response

        # Get configuration from Django settings
        config = getattr(settings, "AUTHKIT_CONFIG", {})

        # Allow HTTP in DEBUG mode, otherwise require HTTPS
        debug_mode = getattr(settings, "DEBUG", False)

        self.client = AuthKitClient(
            client_id=config.get("CLIENT_ID", ""),
            client_secret=config.get("CLIENT_SECRET", ""),
            authkit_url=config.get("AUTHKIT_URL", ""),
            allow_http=debug_mode,  # Only allow HTTP in development
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process the request.

        Args:
            request: Django HTTP request

        Returns:
            Django HTTP response
        """
        # Try to get access token from Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if auth_header.startswith("Bearer "):
            access_token = auth_header[7:]  # Remove "Bearer " prefix

            try:
                # Get user info
                user_info = self.client.get_user_info(access_token)
                request.authkit_user = user_info
                request.authkit_authenticated = True
            except (InvalidTokenError, APIError):
                request.authkit_user = None
                request.authkit_authenticated = False
        else:
            # Try to get token from session (for session-based auth)
            access_token = request.session.get("authkit_access_token")

            if access_token:
                try:
                    user_info = self.client.get_user_info(access_token)
                    request.authkit_user = user_info
                    request.authkit_authenticated = True
                except (InvalidTokenError, APIError):
                    request.authkit_user = None
                    request.authkit_authenticated = False
                    # Clear invalid token from session
                    request.session.pop("authkit_access_token", None)
            else:
                request.authkit_user = None
                request.authkit_authenticated = False

        response = self.get_response(request)
        return response
