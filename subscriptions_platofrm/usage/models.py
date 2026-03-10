from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class APIUsage(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    endpoint = models.CharField(max_length=255)

    timestamp = models.DateTimeField(auto_now_add=True)

    status_code = models.IntegerField()

    ip_address = models.GenericIPAddressField(null=True)