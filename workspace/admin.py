from django.contrib import admin
from .models import Workspace, WorkspaceMember
from .models import Task

admin.site.register(Workspace)
admin.site.register(WorkspaceMember)
admin.site.register(Task)