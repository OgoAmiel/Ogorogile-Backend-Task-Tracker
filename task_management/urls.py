from django.urls import path
from task_management.views import create_task, delete_task, get_tasks, update_task

urlpatterns = [
    path("create_task/",
        view=create_task,
        name="create_task"
    ),

    path("get_tasks/",
        view=get_tasks,
        name="get_tasks"
    ),

    path("update_task/",
        view=update_task,
        name="update_task"
    ),

    path("delete_task/",
        view=delete_task,
        name="delete_task"
    ),
]