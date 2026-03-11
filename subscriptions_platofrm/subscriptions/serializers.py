from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'name_display', 'request_limit', 'price', 'duration_days']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.get_name_display', read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'plan', 'plan_name', 'start_date', 'end_date', 'active']
        read_only_fields = ['user', 'start_date', 'end_date', 'active']
