from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Initialize Limiter with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=str(settings.REDIS_DSN),
    strategy="fixed-window"
)
