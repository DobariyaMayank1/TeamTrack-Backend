from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Workspace, WorkspaceMember, Task
from .serializers import WorkspaceSerializer, WorkspaceMemberSerializer, TaskSerializer


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
    


class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({"message": "Task created"})
        
        return Response(serializer.errors)


class CompleteTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"})

        # check if user is part of workspace
        is_member = WorkspaceMember.objects.filter(
            user=request.user,
            workspace=task.workspace
        ).exists()

        if not is_member:
            return Response({"error": "Not allowed"})

        task.status = 'completed'
        task.completed_by = request.user
        task.save()

        return Response({"message": "Task completed"})


class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workspace_id):
        status = request.GET.get('status')  # pending / completed

        tasks = Task.objects.filter(workspace_id=workspace_id)

        if status:
            tasks = tasks.filter(status=status)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)