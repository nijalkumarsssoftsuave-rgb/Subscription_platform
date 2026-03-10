import redis
from django.conf import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)


def check_rate_limit(user_id, limit):

    key = f"user_limit:{user_id}"

    count = redis_client.get(key)

    if count and int(count) >= limit:
        return False

    redis_client.incr(key)

    redis_client.expire(key, 86400)

    return True