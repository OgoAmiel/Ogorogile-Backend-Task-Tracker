from rest_framework import serializers
from task_management.models import Task

class TaskModelSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'owner', 'title', 'description', 'completed', 'created_at']