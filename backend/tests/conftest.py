import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from datetime import timedelta
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.core.redis import redis_client
from app.core.config import settings, AppEnv
from app.modules.user.models import User, Role
from app.modules.user.schemas import UserCreate

# Override settings for testing
settings.APP_ENV = AppEnv.TEST
settings.SESSION_COOKIE_SECURE = False

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async_session_maker = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )  # type: ignore
    
    async with async_session_maker() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture(autouse=True)
def flush_redis():
    """Flush Redis before each test to clear rate limits and blacklists."""
    redis_client.flushdb()

@pytest_asyncio.fixture(scope="function")
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database override."""
    async def override_get_db():
        yield async_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def admin_user(async_session: AsyncSession) -> User:
    """Create an admin user for testing."""
    user = User(
        email="admin@test.com",
        full_name="Admin Test User",
        role=Role.ADMIN,
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def doctor_user(async_session: AsyncSession) -> User:
    """Create a doctor user for testing."""
    user = User(
        email="doctor@test.com",
        full_name="Doctor Test User",
        role=Role.DOCTOR,
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user

@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate JWT token for admin user."""
    return create_access_token(subject=str(admin_user.email), expires_delta=timedelta(hours=1))

@pytest.fixture
def doctor_token(doctor_user: User) -> str:
    """Generate JWT token for doctor user."""
    return create_access_token(subject=str(doctor_user.email), expires_delta=timedelta(hours=1))

