"""
Django views for AuthKit OAuth flow
"""

from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import secrets

from .utils import get_authkit_client, get_authorization_url


@require_http_methods(["GET"])
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Initiate OAuth login flow.

    Redirects to AuthKit authorization endpoint.
    """
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session["authkit_state"] = state

    # Get authorization URL
    auth_url = get_authorization_url(state=state)

    return redirect(auth_url)


@require_http_methods(["GET"])
def callback_view(request: HttpRequest) -> HttpResponse:
    """
    Handle OAuth callback.

    Exchanges authorization code for tokens and stores them in session.
    """
    # Get code and state from query parameters
    code = request.GET.get("code")
    state = request.GET.get("state")

    # Verify state to prevent CSRF
    session_state = request.session.get("authkit_state")

    if not code:
        return JsonResponse({"error": "No authorization code provided"}, status=400)

    if state != session_state:
        return JsonResponse({"error": "Invalid state parameter"}, status=400)

    # Clear state from session
    request.session.pop("authkit_state", None)

    try:
        # Exchange code for tokens
        client = get_authkit_client()
        from django.conf import settings

        config = getattr(settings, "AUTHKIT_CONFIG", {})
        redirect_uri = config.get("REDIRECT_URI", "")

        tokens = client.exchange_code_for_tokens(code, redirect_uri)

        # Store tokens in session
        request.session["authkit_access_token"] = tokens["access_token"]
        request.session["authkit_refresh_token"] = tokens["refresh_token"]

        # Redirect to success page or home
        success_url = request.GET.get("next", "/")
        return redirect(success_url)

    except Exception as e:
        return JsonResponse(
            {"error": f"Authentication failed: {str(e)}"}, status=400
        )


@require_http_methods(["POST"])
@csrf_protect
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Log out the user by clearing session tokens.

    Note: This endpoint only accepts POST requests for security (CSRF protection).
    """
    # Clear tokens from session
    request.session.pop("authkit_access_token", None)
    request.session.pop("authkit_refresh_token", None)

    # Redirect to home or specified URL from POST data
    next_url = request.POST.get("next") or request.GET.get("next", "/")
    return redirect(next_url)
