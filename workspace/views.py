from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Workspace, WorkspaceMember, Task, Notification
from .serializers import WorkspaceSerializer, WorkspaceMemberSerializer, TaskSerializer, NotificationSerializer, TaskListSerializer


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
            task = serializer.save(created_by=request.user)

            # 🔔 create notifications
            members = WorkspaceMember.objects.filter(workspace=task.workspace)

            for member in members:
                if member.user != request.user:
                    Notification.objects.create(
                        sender=request.user,
                        receiver=member.user,
                        task=task,
                        message=f"{request.user.username} created a new task: {task.title}"
                    )

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

        if task.status == "completed":
            return Response({"message": "Task already completed"})

        # ✅ read description from request body
        description = request.data.get("description", "").strip()

        if not description:
            return Response({"error": "Description is required"}, status=400)

        task.status = "completed"
        task.completed_by = request.user
        task.description = description  # ✅ save it
        task.save()

        # 🔔 create notifications
        members = WorkspaceMember.objects.filter(workspace=task.workspace)

        for member in members:
            if member.user != request.user:
                Notification.objects.create(
                    sender=request.user,
                    receiver=member.user,
                    task=task,
                    message=f"{request.user.username} completed task: {task.title}"
                )

        return Response({"message": "Task completed"})


class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workspace_id):
        status = request.query_params.get('status')

        tasks = Task.objects.filter(workspace_id=workspace_id).select_related('created_by', 'completed_by')

        if status:
            tasks = tasks.filter(status=status)

        serializer = TaskListSerializer(tasks, many=True)  # ✅ use new serializer
        return Response(serializer.data)
    

class UpdateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        # ✅ check workspace membership
        is_member = WorkspaceMember.objects.filter(
            user=request.user,
            workspace=task.workspace
        ).exists()

        if not is_member:
            return Response({"error": "Not allowed"}, status=403)

        # ✅ OPTIONAL: restrict edit (recommended)
        # if task.created_by != request.user:
        #     return Response({"error": "Only creator can edit"}, status=403)

        # ✅ update fields
        title = request.data.get("title")
        if title is not None and not title.strip():
            return Response({"error": "Title cannot be empty"}, status=400)

        if title:
            task.title = title.strip()
            
        task.description = request.data.get("description", task.description)

        task.save()

        return Response({"message": "Task updated successfully"})
    

class DeleteTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        # ✅ check workspace membership
        is_member = WorkspaceMember.objects.filter(
            user=request.user,
            workspace=task.workspace
        ).exists()

        if not is_member:
            return Response({"error": "Not allowed"}, status=403)

        # ✅ only creator can delete (recommended)
        # if task.created_by != request.user:
        #     return Response({"error": "Only creator can delete"}, status=403)

        task.delete()

        return Response({"message": "Task deleted successfully"})


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, receiver=request.user)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"})

        notification.is_read = True
        notification.save()

        return Response({"message": "Notification marked as read"})


class WorkspaceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 👉 get all workspaces where user is a member
        memberships = WorkspaceMember.objects.filter(user=request.user)

        workspaces = [member.workspace for member in memberships]

        serializer = WorkspaceSerializer(workspaces, many=True)

        return Response(serializer.data)