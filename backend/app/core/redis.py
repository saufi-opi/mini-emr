import redis
from app.core.config import settings

# Initialize Redis client
redis_client = redis.from_url(
    str(settings.REDIS_DSN),
    encoding="utf-8",
    decode_responses=True
)