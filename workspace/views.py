from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Workspace, WorkspaceMember
from .serializers import WorkspaceSerializer, WorkspaceMemberSerializer


class CreateWorkspaceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WorkspaceSerializer(data=request.data)
        if serializer.is_valid():
            workspace = serializer.save(created_by=request.user)

            # creator becomes admin automatically
            WorkspaceMember.objects.create(
                user=request.user,
                workspace=workspace,
                role='admin'
            )

            return Response({"message": "Workspace created"})
        return Response(serializer.errors)


class AddMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WorkspaceMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Member added"})
        return Response(serializer.errors)


class WorkspaceMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workspace_id):
        members = WorkspaceMember.objects.filter(workspace_id=workspace_id)
        serializer = WorkspaceMemberSerializer(members, many=True)
        return Response(serializer.data)