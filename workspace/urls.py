from django.urls import path
from .views import CreateWorkspaceView, AddMemberView, WorkspaceMembersView

urlpatterns = [
    path('create/', CreateWorkspaceView.as_view()),
    path('add-member/', AddMemberView.as_view()),
    path('members/<int:workspace_id>/', WorkspaceMembersView.as_view()),
]