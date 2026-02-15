from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from bcrypt import checkpw, gensalt, hashpw
from jwt.exceptions import InvalidTokenError

from app.core.config import settings
from app.core.redis import redis_client

ALGORITHM = "HS256"

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str | Any, jti: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "jti": jti, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def get_token_payload(token: str) -> dict[str, Any]:
    """Decode token and return payload."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        return {}


def get_jti(token: str) -> str | None:
    """Extract JTI from token."""
    payload = get_token_payload(token)
    return payload.get("jti")


def blacklist_token(token: str) -> None:
    """Blacklist a token until it expires."""
    payload = get_token_payload(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    
    if not exp:
        return
        
    # Calculate TTL
    now = datetime.now(timezone.utc).timestamp()
    ttl = int(exp - now)
    
    if ttl > 0:
        # Use JTI if available (refresh tokens), otherwise use token itself (access tokens)
        key = f"blacklist:{jti or token}"
        redis_client.setex(key, ttl, "true")


def is_token_blacklisted(token: str) -> bool:
    """Check if a token or its JTI is blacklisted."""
    payload = get_token_payload(token)
    jti = payload.get("jti")
    
    key = f"blacklist:{jti or token}"
    return redis_client.exists(key) > 0

