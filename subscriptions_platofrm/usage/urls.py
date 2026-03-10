from django.urls import path
from .views import UsageAnalytics


urlpatterns = [
    path("analytics/", UsageAnalytics.as_view()),
]

