from django.contrib.auth.models import AbstractUser
from django.db import models

# class User(AbstractUser):
#
#     email = models.EmailField(unique=True)
#
#     company_name = models.CharField(max_length=200, null=True)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     REQUIRED_FIELDS = ["email"]

class User(AbstractUser):

    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    otp = models.CharField(max_length=6, null=True, blank=True)

    otp_created = models.DateTimeField(null=True, blank=True)