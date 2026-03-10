from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class SubscriptionPlan(models.Model):

    name = models.CharField(max_length=100)

    request_limit = models.IntegerField()

    price = models.FloatField()

    duration_days = models.IntegerField()

    def __str__(self):
        return self.name


class UserSubscription(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)

    start_date = models.DateTimeField(default=timezone.now)

    end_date = models.DateTimeField()

    active = models.BooleanField(default=True)

    def is_active(self):

        return self.active and self.end_date > timezone.now()

from django.db import models
from django.conf import settings

class Plan(models.Model):

    PLAN_CHOICES = [
        ("FREE", "Free"),
        ("PLUS", "Plus"),
        ("PRO", "Pro"),
    ]

    name = models.CharField(max_length=10, choices=PLAN_CHOICES)

    price = models.DecimalField(max_digits=6, decimal_places=2)

    request_limit = models.IntegerField()

    def __str__(self):
        return self.name


class UserPlan(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    subscribed_at = models.DateTimeField(auto_now_add=True)