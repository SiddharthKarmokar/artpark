import redis
from app.core.config import settings

redis_client = redis.Redis.from_url(
    settings.redis_url,
    socket_connect_timeout=1,
    socket_timeout=1,
    retry_on_timeout=False,
)

def get_redis():
    return redis_client
