from rest_framework.views import APIView
from rest_framework.response import Response

from .models import APIUsage


class UsageAnalytics(APIView):

    def get(self, request):

        user = request.user

        total = APIUsage.objects.filter(user=user).count()

        return Response({

            "total_requests": total
        })