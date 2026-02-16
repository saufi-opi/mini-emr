import asyncio
import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import engine
from app.core.security import get_password_hash
from app.modules.user.models import User, Role
from app.modules.user.service import create_user, get_user_by_email
from app.modules.user.schemas import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_initial_data(session: AsyncSession) -> None:
    async with session:
        # Check for Admin
        user = await get_user_by_email(session=session, email="admin@example.com")
        if not user:
            await create_user(
                session=session,
                user_create=UserCreate(
                    email="admin@example.com",
                    full_name="Admin User",
                    role=Role.ADMIN,
                    password="aaAA1234",
                ),
            )
            logger.info("Admin user created")
        else:
            logger.info("Admin user already exists")

        # Check for Doctor
        user = await get_user_by_email(session=session, email="doctor@example.com")
        if not user:
            await create_user(
                session=session,
                user_create=UserCreate(
                    email="doctor@example.com",
                    full_name="Doctor User",
                    role=Role.DOCTOR,
                    password="aaAA1234",
                ),
            )
            logger.info("Doctor user created")
        else:
            logger.info("Doctor user already exists")

async def main() -> None:
    logger.info("Creating initial data")
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )  # type: ignore
    await create_initial_data(async_session())
    logger.info("Initial data created")

if __name__ == "__main__":
    asyncio.run(main())
