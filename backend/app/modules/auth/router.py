import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status

from app.core.database import AsyncSessionDep
from app.core.rate_limiter import limiter
from app.modules.auth import service as auth_service
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.user.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
@limiter.limit("1000/hour")
async def login(
    request: Request,
    response: Response,
    session: AsyncSessionDep,
    login_request: LoginRequest,
):
    """
    Login with email and password.
    Returns access token and sets refresh token in an HTTP-only cookie.
    """
    return await auth_service.login(session=session, body=login_request, response=response)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
async def refresh(
    request: Request,
    session: AsyncSessionDep,
):
    """
    Refresh access token using the refresh token from cookie.
    """
    return await auth_service.refresh(session=session, request=request)


@router.post("/logout")
@limiter.limit("30/minute")
async def logout(
    request: Request,
    response: Response,
):
    """
    Logout by blacklisting the current tokens and clearing the cookie.
    """
    return await auth_service.logout(request=request, response=response)
