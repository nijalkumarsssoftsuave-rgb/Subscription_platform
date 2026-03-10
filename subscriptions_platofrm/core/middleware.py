from django.http import JsonResponse
from apikeys.models import APIKey


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Skip admin and auth routes if needed
        if request.path.startswith("/admin/"):
            return self.get_response(request)

        # Read API key from header
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return JsonResponse(
                {"error": "API key missing"},
                status=401
            )

        # Validate API key
        try:
            key = APIKey.objects.get(key=api_key, is_active=True)
            request.api_key = key
        except APIKey.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid API key"},
                status=403
            )

        response = self.get_response(request)
        return response
