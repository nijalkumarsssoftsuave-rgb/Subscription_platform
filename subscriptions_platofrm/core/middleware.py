# import json
# import logging
# from django.http import JsonResponse
# from apikeys.models import APIKey
# from gateway.rate_limiter import check_rate_limit
# from django.utils.cache import patch_cache_control
# from asgiref.sync import sync_to_async
# from core.redis_client import redis_client
# from subscriptions.models import UserSubscription
#
# logger = logging.getLogger(__name__)
#
# # Cache configuration
# SUBSCRIPTION_CACHE_TTL = 3600  # 1 hour
#
# class APIGatewayMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self._async_check = True
#
#     async def __call__(self, request):
#         # Skip certain paths if needed
#         if request.path.startswith("/admin/") or request.path.startswith("/auth/"):
#             return await self.get_response(request)
#
#         # 1. API Key Authentication
#         api_key_str = request.headers.get("X-API-KEY")
#         if not api_key_str:
#             return JsonResponse({"error": "API key missing"}, status=401)
#
#         # Sync to async for ORM calls
#         try:
#             api_key = await sync_to_async(
#                 lambda: APIKey.objects.select_related('user').filter(key=api_key_str, active=True).first()
#             )()
#             if not api_key:
#                  return JsonResponse({"error": "Invalid API key"}, status=403)
#             request.user = api_key.user
#         except Exception as e:
#             logger.error(f"Auth error: {e}")
#             return JsonResponse({"error": "Authentication system error"}, status=500)
#
#         # 2. Rate Limiting and Subscription (with Redis Cache)
#         # We cache the user's subscription and rate limit to avoid DB hits
#         cache_key = f"user_sub_info:{request.user.id}"
#         sub_info = None
#
#         if redis_client:
#             try:
#                 cached_data = redis_client.get(cache_key)
#                 if cached_data:
#                     sub_info = json.loads(cached_data)
#             except Exception as e:
#                 logger.warning(f"Redis cache read error: {e}")
#
#         if not sub_info:
#             # DB hit if not in cache
#             try:
#                 active_sub = await sync_to_async(
#                     lambda: UserSubscription.objects.filter(user=api_key.user, active=True).first()
#                 )()
#
#                 if not active_sub or not await sync_to_async(active_sub.is_active)():
#                     return JsonResponse({"error": "No active subscription found"}, status=403)
#
#                 sub_info = {
#                     "request_limit": active_sub.plan.request_limit,
#                     "plan_id": active_sub.plan.id
#                 }
#
#                 # Update cache
#                 if redis_client:
#                     redis_client.setex(cache_key, SUBSCRIPTION_CACHE_TTL, json.dumps(sub_info))
#             except Exception as e:
#                 logger.error(f"Subscription check error: {e}")
#                 return JsonResponse({"error": "Internal subscription system error"}, status=500)
#
#         # Perform rate limit check (this uses the redis pool internally)
#         if not check_rate_limit(request.user.id, sub_info["request_limit"]):
#             return JsonResponse({"error": "Rate limit exceeded"}, status=429)
#
#         # Proceed to next middleware/view
#         response = await self.get_response(request)
#         return response
#
# class CDNCacheMiddleware:
#     """
#     Middleware to handle CDN and Browser Caching headers. (Async)
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self._async_check = True
#
#     async def __call__(self, request):
#         response = await self.get_response(request)
#
#         # Only cache GET and HEAD requests
#         if request.method in ["GET", "HEAD"] and response.status_code == 200:
#             # Tell CDN and Browser to cache for 5 minutes (300 seconds)
#             # patch_cache_control works on the response object
#             patch_cache_control(response, public=True, max_age=300, s_maxage=600)
#
#             return response
#         return response
import json
import logging
from django.http import JsonResponse
from django.utils.cache import patch_cache_control

from apikeys.models import APIKey
from subscriptions.models import UserSubscription
from gateway.rate_limiter import check_rate_limit
from core.redis_client import redis_client

logger = logging.getLogger(__name__)

SUBSCRIPTION_CACHE_TTL = 3600  # 1 hour


class APIGatewayMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

            # Apply API gateway only for API routes
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        # # Skip certain paths
        # EXCLUDED_PATHS = [
        #     "/admin/",
        #     "/auth/",
        #     "/static/",
        #     "/favicon.ico",
        # ]
        #
        # for path in EXCLUDED_PATHS:
        #     if request.path.startswith(path):
        #         return self.get_response(request)

        # -----------------------------
        # 1. API KEY AUTHENTICATION
        # -----------------------------
        api_key_str = request.headers.get("X-API-KEY")

        if not api_key_str:
            return JsonResponse({"error": "API key missing"}, status=401)

        try:
            api_key = APIKey.objects.select_related("user").filter(
                key=api_key_str,
                active=True
            ).first()

            if not api_key:
                return JsonResponse({"error": "Invalid API key"}, status=403)

            request.user = api_key.user

        except Exception as e:
            logger.error(f"Auth error: {e}")
            return JsonResponse({"error": "Authentication system error"}, status=500)

        # -----------------------------
        # 2. SUBSCRIPTION + CACHE
        # -----------------------------
        cache_key = f"user_sub_info:{request.user.id}"
        sub_info = None

        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)

                if cached_data:
                    sub_info = json.loads(cached_data)

            except Exception as e:
                logger.warning(f"Redis cache read error: {e}")

        if not sub_info:
            try:
                active_sub = UserSubscription.objects.filter(
                    user=api_key.user,
                    active=True
                ).select_related("plan").first()

                if not active_sub or not active_sub.is_active():
                    return JsonResponse(
                        {"error": "No active subscription found"},
                        status=403
                    )

                sub_info = {
                    "request_limit": active_sub.plan.request_limit,
                    "plan_id": active_sub.plan.id
                }

                if redis_client:
                    redis_client.setex(
                        cache_key,
                        SUBSCRIPTION_CACHE_TTL,
                        json.dumps(sub_info)
                    )

            except Exception as e:
                logger.error(f"Subscription check error: {e}")
                return JsonResponse(
                    {"error": "Internal subscription system error"},
                    status=500
                )

        # -----------------------------
        # 3. RATE LIMIT CHECK
        # -----------------------------
        if not check_rate_limit(request.user.id, sub_info["request_limit"]):
            return JsonResponse({"error": "Rate limit exceeded"}, status=429)

        # -----------------------------
        # PROCEED TO VIEW
        # -----------------------------
        response = self.get_response(request)

        return response


class CDNCacheMiddleware:
    """
    Middleware for CDN / Browser caching headers
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        # Cache only GET and HEAD
        if request.method in ["GET", "HEAD"] and response.status_code == 200:
            patch_cache_control(
                response,
                public=True,
                max_age=300,
                s_maxage=600
            )

        return response