from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import SubscriptionPlan, UserSubscription
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer
from django.utils import timezone
from asgiref.sync import sync_to_async
from core.cache import async_api_cache

class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    @async_api_cache(timeout=3600)  # Cache plans for 1 hour
    async def get(self, request, *args, **kwargs):
        # DRF generics aren't async by default, we override get
        plans = await sync_to_async(list)(self.get_queryset())
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)

class UserSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request, *args, **kwargs):
        return await super().post(request, *args, **kwargs)

    @sync_to_async
    def perform_create(self, serializer):
        # Mark all previous subscriptions as inactive
        UserSubscription.objects.filter(user=self.request.user, active=True).update(active=False)
        serializer.save(user=self.request.user)

class UserSubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request, *args, **kwargs):
        subscription = await sync_to_async(
            lambda: UserSubscription.objects.filter(user=request.user, active=True).first()
        )()
        if not subscription:
            return Response({"error": "No active subscription found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
