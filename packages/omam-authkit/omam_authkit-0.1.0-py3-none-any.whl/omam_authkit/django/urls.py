"""
Django URL patterns for AuthKit OAuth flow
"""

from django.urls import path
from . import views

app_name = "omam_authkit"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("callback/", views.callback_view, name="callback"),
    path("logout/", views.logout_view, name="logout"),
]
