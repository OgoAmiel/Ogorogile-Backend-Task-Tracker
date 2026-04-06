from rest_framework import serializers
from task_management.models import Task

class TaskModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'created_at']