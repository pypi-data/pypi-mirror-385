"""
Django decorators for AuthKit authentication
"""

from functools import wraps
from typing import Callable
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.conf import settings


def authkit_required(
    redirect_url: str = None, api_view: bool = False
) -> Callable:
    """
    Decorator to require AuthKit authentication for Django views.

    Args:
        redirect_url: URL to redirect to if not authenticated (default: /auth/login)
        api_view: If True, return JSON error instead of redirect (for API endpoints)

    Example:
        @authkit_required
        def dashboard(request):
            user = get_current_user(request)
            return render(request, 'dashboard.html', {'user': user})

        @authkit_required(api_view=True)
        def api_endpoint(request):
            user = get_current_user(request)
            return JsonResponse({'user': user})
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped_view(request: HttpRequest, *args, **kwargs):
            # Check if user is authenticated via AuthKit middleware
            if not getattr(request, "authkit_authenticated", False):
                if api_view:
                    return JsonResponse(
                        {"error": "Authentication required"}, status=401
                    )
                else:
                    # Redirect to login
                    login_url = redirect_url or getattr(
                        settings, "AUTHKIT_LOGIN_URL", "/auth/login"
                    )
                    return redirect(login_url)

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


def authkit_optional(view_func: Callable) -> Callable:
    """
    Decorator that adds AuthKit user info if available, but doesn't require it.

    Example:
        @authkit_optional
        def home(request):
            user = get_current_user(request)  # May be None
            return render(request, 'home.html', {'user': user})
    """

    @wraps(view_func)
    def wrapped_view(request: HttpRequest, *args, **kwargs):
        # Just pass through - middleware already added user info if available
        return view_func(request, *args, **kwargs)

    return wrapped_view
