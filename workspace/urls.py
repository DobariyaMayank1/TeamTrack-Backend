from django.urls import path
from .views import CreateWorkspaceView, AddMemberView, WorkspaceMembersView, CreateTaskView, CompleteTaskView, TaskListView, NotificationListView, MarkAsReadView, WorkspaceListView

urlpatterns = [
    path('create/', CreateWorkspaceView.as_view()),
    path('add-member/', AddMemberView.as_view()),
    path('members/<int:workspace_id>/', WorkspaceMembersView.as_view()),
    path('task/create/', CreateTaskView.as_view()),
    path('task/complete/<int:task_id>/', CompleteTaskView.as_view()),
    path('task/list/<int:workspace_id>/', TaskListView.as_view()),
    path('notifications/', NotificationListView.as_view()),
    path('notifications/read/<int:notification_id>/', MarkAsReadView.as_view()),
    path('list/', WorkspaceListView.as_view()),
]