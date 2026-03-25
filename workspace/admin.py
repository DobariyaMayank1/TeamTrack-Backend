from django.contrib import admin
from .models import Workspace, WorkspaceMember, Task, Notification

admin.site.register(Workspace)
admin.site.register(WorkspaceMember)
admin.site.register(Task)
admin.site.register(Notification)