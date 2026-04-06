from django.urls import path
from task_management.views import create_task

urlpatterns = [
    path("create_task/", view=create_task, name="create_task"),
]