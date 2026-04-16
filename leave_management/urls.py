from django.urls import path

from leave_management.views import create_leave_request, get_leave_balances, get_leave_requests, cancel_leave_request

urlpatterns = [
    # Add URL patterns for leave management here
    path("create_leave_request/", create_leave_request, name="create_leave_request"),
    path("get_leave_requests/", get_leave_requests, name="get_leave_requests"),
    path("get_leave_balances/", get_leave_balances, name="get_leave_balances"),
    path("cancel_leave_request/", cancel_leave_request, name="cancel_leave_request"),
]