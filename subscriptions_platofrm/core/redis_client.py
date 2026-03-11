import redis
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Redis Connection Pooling configuration
REDIS_POOL = redis.ConnectionPool(
    host=getattr(settings, "REDIS_HOST", "localhost"),
    port=getattr(settings, "REDIS_PORT", 6379),
    db=getattr(settings, "REDIS_DB", 0),
    max_connections=getattr(settings, "REDIS_MAX_CONNECTIONS", 20),
    decode_responses=True
)

def get_redis_client():
    """Returns a Redis client from the connection pool."""
    try:
        client = redis.Redis(connection_pool=REDIS_POOL)
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None

# Singleton-like client instance
redis_client = get_redis_client()
