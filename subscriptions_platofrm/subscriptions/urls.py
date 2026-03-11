from django.urls import path
from .views import SubscriptionPlanListView, UserSubscriptionCreateView, UserSubscriptionDetailView

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='plan-list'),
    path('subscribe/', UserSubscriptionCreateView.as_view(), name='subscribe'),
    path('my-subscription/', UserSubscriptionDetailView.as_view(), name='my-subscription'),
]
