import logging
from core.redis_client import redis_client

logger = logging.getLogger(__name__)

def check_rate_limit(user_id, limit):
    """
    Check rate limit using Redis connection pool.
    Edge cases:
    - Redis down: fail open (allows request)
    - Redis error: log and fail open
    """
    if not redis_client:
        # Fail open policy: allow request if Redis is down
        return True

    key = f"user_limit:{user_id}"

    try:
        count = redis_client.get(key)

        if count and int(count) >= limit:
            return False

        # Use a pipeline to ensure atomicity
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 86400)  # Reset daily (could be configurable)
        pipe.execute()
        
        return True
    except Exception as e:
        logger.error(f"Rate Limiter Redis error: {e}")
        return True # Fail open
