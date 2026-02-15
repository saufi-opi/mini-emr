import pytest
from datetime import timedelta
from app.core import security
from app.core.security import verify_password, get_password_hash, create_access_token
import jwt

def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_jwt_token_creation():
    data = "user@example.com"
    token = create_access_token(subject=data, expires_delta=timedelta(minutes=15))
    decoded = jwt.decode(token, security.settings.JWT_SECRET_KEY, algorithms=[security.ALGORITHM])
    assert decoded["sub"] == data
    assert "exp" in decoded

def test_jwt_token_expiration():
    data = "user@example.com"
    token = create_access_token(subject=data, expires_delta=timedelta(seconds=-1))
    
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, security.settings.JWT_SECRET_KEY, algorithms=[security.ALGORITHM])
