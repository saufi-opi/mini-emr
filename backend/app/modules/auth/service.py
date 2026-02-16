import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import Request, Response, HTTPException, status

from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    blacklist_token,
    get_token_payload,
    is_token_blacklisted,
)
from app.modules.user import service as user_service
from app.modules.auth.schemas import LoginRequest, TokenResponse

async def login(*, session: AsyncSession, body: LoginRequest, response: Response) -> TokenResponse:
    """
    Login with email and password.
    Returns access token and sets refresh token in an HTTP-only cookie.
    """
    user = await user_service.get_user_by_email(session=session, email=body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    refresh_token = create_refresh_token(
        subject=user.email, jti=jti, expires_delta=refresh_token_expires
    )

    # Set refresh token in cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        max_age=int(refresh_token_expires.total_seconds()),
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=int(access_token_expires.total_seconds()),
    )

async def refresh(*, session: AsyncSession, request: Request) -> TokenResponse:
    """
    Refresh access token using the refresh token from cookie.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    if is_token_blacklisted(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is blacklisted",
        )

    payload = get_token_payload(refresh_token)
    email = payload.get("sub")
    token_type = payload.get("type")
    
    if not email or token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = await user_service.get_user_by_email(session=session, email=email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=int(access_token_expires.total_seconds()),
    )

async def logout(*, request: Request, response: Response):
    """
    Logout by blacklisting the current tokens and clearing the cookie.
    """
    # Blacklist Access Token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]
        blacklist_token(access_token)

    # Blacklist Refresh Token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        blacklist_token(refresh_token)

    # Clear Cookie
    response.delete_cookie(key="refresh_token")
    
    return {"detail": "Successfully logged out"}
