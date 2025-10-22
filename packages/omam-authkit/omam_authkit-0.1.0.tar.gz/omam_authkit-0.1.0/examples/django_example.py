"""
Django integration example for OMAM AuthKit

Add this to your Django project's settings.py:

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

# urls.py
from django.urls import path, include

urlpatterns = [
    path('auth/', include('omam_authkit.django.urls')),
    path('', include('your_app.urls')),
]
"""

# Example views in your Django app
from django.shortcuts import render
from django.http import JsonResponse
from omam_authkit.django.decorators import authkit_required
from omam_authkit.django.utils import get_current_user


def home(request):
    """Public home page"""
    user = get_current_user(request)
    return render(request, "home.html", {"user": user})


@authkit_required
def dashboard(request):
    """Protected dashboard - requires authentication"""
    user = get_current_user(request)
    return render(request, "dashboard.html", {"user": user})


@authkit_required(api_view=True)
def api_endpoint(request):
    """Protected API endpoint - returns JSON"""
    user = get_current_user(request)
    return JsonResponse(
        {
            "message": f"Hello {user['email']}",
            "user": user,
        }
    )


# Example: Custom view with manual authentication check
def profile(request):
    """User profile page"""
    from omam_authkit.django.utils import is_authenticated

    if not is_authenticated(request):
        from django.shortcuts import redirect

        return redirect("/auth/login")

    user = get_current_user(request)
    return render(request, "profile.html", {"user": user})
