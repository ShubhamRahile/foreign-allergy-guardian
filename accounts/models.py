from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Emergency contact phone number.")

    def __str__(self):
        return self.username
