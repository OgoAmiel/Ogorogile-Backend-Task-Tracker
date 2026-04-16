from django.urls import path

from user_management.views import get_user

urlpatterns = [
    # Add URL patterns for user management here
    path("get_user/", get_user, name="get_user"),
]