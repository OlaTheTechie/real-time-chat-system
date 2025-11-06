import redis
from app.core.config import settings

# redis client for caching and pub/sub
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client