from rest_framework import serializers
from .models import Workspace, WorkspaceMember, Task, Notification
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'created_by', 'created_at']
        read_only_fields = ['created_by']


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMember
        fields = ['id', 'user', 'workspace', 'role']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'completed_by', 'status']

    def validate(self, data):
        user = self.context['request'].user
        workspace = data['workspace']

        is_member = WorkspaceMember.objects.filter(
            user=user,
            workspace=workspace
        ).exists()

        if not is_member:
            raise serializers.ValidationError("You are not a member of this workspace")

        return data
    

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'sender',
            'sender_username',
            'receiver',
            'task',
            'message',
            'is_read',
            'created_at'
        ]