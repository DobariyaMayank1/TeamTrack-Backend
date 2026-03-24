from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(max_length=150)  # display name
    mobile = models.CharField(max_length=15, unique=True)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username