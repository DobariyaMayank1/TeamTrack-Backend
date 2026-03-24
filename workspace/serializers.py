from rest_framework import serializers
from .models import Workspace, WorkspaceMember
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