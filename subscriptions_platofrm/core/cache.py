import json
import logging
from functools import wraps
from django.http import JsonResponse
from core.redis_client import redis_client
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

def async_api_cache(timeout=300, key_prefix="api_cache"):
    """
    Decorator for async DRF/Django views to cache responses in Redis.
    """
    def decorator(view_func):
        @wraps(view_func)
        async def _wrapped_view(self, request, *args, **kwargs):
            if request.method != "GET":
                return await view_func(self, request, *args, **kwargs)

            # Generate cache key based on path and query params
            cache_key = f"{key_prefix}:{request.get_full_path()}"
            
            if redis_client:
                try:
                    # Use a short timeout for redis operations to prevent blocking
                    cached_data = redis_client.get(cache_key)
                    if cached_data:
                        data = json.loads(cached_data)
                        return JsonResponse(data, safe=False)
                except Exception as e:
                    logger.warning(f"Cache read error: {e}")

            # Call the actual view function
            response = await view_func(self, request, *args, **kwargs)

            # Cache the response data if successful
            if response.status_code == 200 and redis_client:
                try:
                    # For DRF Response objects, use .data
                    content = getattr(response, 'data', response.content)
                    if hasattr(response, 'render'):
                         await sync_to_async(response.render)()
                         content = response.data

                    redis_client.setex(cache_key, timeout, json.dumps(content))
                except Exception as e:
                    logger.warning(f"Cache write error: {e}")

            return response
        return _wrapped_view
    return decorator
