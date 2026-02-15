from limits.typing import Any
from typing import Sequence
import uuid

from app.core.security import get_password_hash
from pydantic import EmailStr
from app.modules.user.models import User
from app.modules.user.schemas import UserCreate, UserUpdate
from app.modules.user.exceptions import UserAlreadyExistsException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.schemas import SortDirection
from app.core.query_builder import QueryBuilder, QueryResult
from app.core.schemas import PaginationParams, SortParams

async def get_user_by_id(*, session: AsyncSession, user_id: uuid.UUID) -> User | None:
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def get_user_by_email(*, session: AsyncSession, email: EmailStr) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def get_all_users(*, 
    session: AsyncSession, 
    pagination: PaginationParams, 
    sort: SortParams,
    search: str | None = None
) -> QueryResult[User]:
    query = QueryBuilder(User, session)
    query.paginate(pagination).sort(sort).search(search, [User.full_name])
    return await query.execute()

async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    existing_user = await get_user_by_email(session=session, email=user_create.email)
    if existing_user is not None:
        raise UserAlreadyExistsException()

    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        del user_data["password"]
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user



