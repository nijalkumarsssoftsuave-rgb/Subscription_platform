import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class APIKey(models.Model):

    key = models.UUIDField(default=uuid.uuid4, unique=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)