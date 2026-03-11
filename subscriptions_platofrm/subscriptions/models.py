from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

User = settings.AUTH_USER_MODEL


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ("FREE", "Free"),
        ("PLUS", "Plus"),
        ("PRO", "Pro"),
        ("ULTRA", "Ultra"),
    ]

    name = models.CharField(max_length=100, choices=PLAN_CHOICES, unique=True)
    request_limit = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)

    def __str__(self):
        return self.get_name_display()


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def is_active(self):
        return self.active and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
