from fastapi.requests import Request
import uuid
from typing import Any, Sequence, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from app.modules.user.models import User
from app.modules.user.schemas import UserRead, UserCreate
from app.modules.user import service as user_service
from app.modules.user.dependencies import get_current_admin_user, get_current_active_user
from app.core.database import AsyncSessionDep
from app.core.rate_limiter import limiter
from app.core.schemas import PaginationParams, SortParams, SearchParams
from app.core.query_builder import QueryResult

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=UserRead)
@limiter.limit("60/minute")
async def read_user_me(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current user.
    """
    return current_user


@router.get(
    "/",
    dependencies=[Depends(get_current_admin_user)],
    response_model=QueryResult[UserRead],
)
@limiter.limit("60/minute")
async def read_users(
    request: Request,
    session: AsyncSessionDep,
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: SearchParams = Depends(),
) -> QueryResult[User]:
    """
    Retrieve users.

    Requires: admin role
    """
    return await user_service.get_all_users(
        session=session,
        pagination=pagination,
        sort=sort,
        search=search,
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_admin_user)],
    response_model=UserRead,
)
@limiter.limit("60/minute")
async def create_user(
    request: Request,
    session: AsyncSessionDep,
    user: UserCreate,
) -> User:
    """
    Create a new user.

    Requires: admin role
    """
    return await user_service.create_user(
        session=session,
        user_create=user,
    )
