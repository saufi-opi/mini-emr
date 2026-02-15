from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
import redis

# Initialize Redis client
redis_client = redis.from_url(
    str(settings.REDIS_DSN),
    encoding="utf-8",
    decode_responses=True
)

# Initialize Limiter with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=str(settings.REDIS_DSN),
    strategy="fixed-window"
)
