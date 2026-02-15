from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import select

from app.core.config import settings
from app.core.database import AsyncSessionDep
from app.core.security import ALGORITHM, is_token_blacklisted
from app.modules.user.models import User, Role
from app.modules.user.exceptions import InactiveUserException
from app.modules.auth.exceptions import CredentialException, UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSessionDep,
) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise CredentialException()
    except InvalidTokenError:
        raise CredentialException()
    except ValidationError:
        raise CredentialException()
        
    if is_token_blacklisted(token):
        raise CredentialException()
        
    result = await db.execute(select(User).where(User.email == username))  # type: ignore[deprecated]
    user = result.scalar_one_or_none()
    
    if user is None:
        raise CredentialException()
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
       raise InactiveUserException()
    return current_user

async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.role != Role.ADMIN:
        raise UnauthorizedException()
    return current_user

CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]
CurrentAdminUserDep = Annotated[User, Depends(get_current_admin_user)]