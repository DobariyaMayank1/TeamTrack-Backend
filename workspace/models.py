from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Workspace(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workspaces')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    class Meta:
        unique_together = ('user', 'workspace')

    def __str__(self):
        return f"{self.user} - {self.workspace} ({self.role})"


class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=255)

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tasks')

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    description = models.TextField(blank=True)

    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_tasks'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Notification(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver}"