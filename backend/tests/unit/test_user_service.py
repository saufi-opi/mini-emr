import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.user import service as user_service
from app.modules.user.models import User, Role
from app.modules.user.schemas import UserCreate, UserUpdate
from app.modules.user.exceptions import UserAlreadyExistsException
from app.core.schemas import PaginationParams, SortParams, SearchParams
from app.core.security import verify_password


@pytest.mark.asyncio
async def test_get_user_by_id_success(async_session: AsyncSession, admin_user: User):
    """Test retrieving a user by ID successfully."""
    result = await user_service.get_user_by_id(session=async_session, user_id=admin_user.id)
    
    assert result is not None
    assert result.id == admin_user.id
    assert result.email == admin_user.email
    assert result.full_name == admin_user.full_name


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(async_session: AsyncSession):
    """Test retrieving a non-existent user by ID returns None."""
    import uuid
    non_existent_id = uuid.uuid4()
    
    result = await user_service.get_user_by_id(session=async_session, user_id=non_existent_id)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_user_by_email_success(async_session: AsyncSession, admin_user: User):
    """Test retrieving a user by email successfully."""
    result = await user_service.get_user_by_email(session=async_session, email=admin_user.email)
    
    assert result is not None
    assert result.email == admin_user.email
    assert result.id == admin_user.id


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(async_session: AsyncSession):
    """Test retrieving a non-existent user by email returns None."""
    result = await user_service.get_user_by_email(session=async_session, email="nonexistent@test.com")
    
    assert result is None


@pytest.mark.asyncio
async def test_create_user_success(async_session: AsyncSession):
    """Test creating a new user with password hashing."""
    user_data = UserCreate(
        email="newuser@test.com",
        full_name="New Test User",
        role=Role.DOCTOR,
        password="securepassword123"
    )
    
    result = await user_service.create_user(session=async_session, user_create=user_data)
    
    assert result.email == user_data.email
    assert result.full_name == user_data.full_name
    assert result.role == user_data.role
    assert result.is_active is True
    assert verify_password("securepassword123", result.hashed_password)


@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_session: AsyncSession, admin_user: User):
    """Test creating a user with duplicate email raises exception."""
    user_data = UserCreate(
        email=admin_user.email,  # Duplicate email
        full_name="Duplicate User",
        role=Role.DOCTOR,
        password="password123"
    )
    
    with pytest.raises(UserAlreadyExistsException):
        await user_service.create_user(session=async_session, user_create=user_data)


@pytest.mark.asyncio
async def test_update_user_success(async_session: AsyncSession, doctor_user: User):
    """Test updating user fields."""
    update_data = UserUpdate(
        full_name="Updated Name",
        is_active=False
    )
    
    result = await user_service.update_user(
        session=async_session,
        db_user=doctor_user,
        user_in=update_data
    )
    
    assert result.full_name == "Updated Name"
    assert result.is_active is False
    assert result.email == doctor_user.email  # Email unchanged


@pytest.mark.asyncio
async def test_update_user_password_excluded(async_session: AsyncSession, doctor_user: User):
    """Test that password field is excluded from updates."""
    original_password = doctor_user.hashed_password
    
    update_data = UserUpdate(
        full_name="Updated Name",
        password="newpassword123"  # This should be ignored
    )
    
    result = await user_service.update_user(
        session=async_session,
        db_user=doctor_user,
        user_in=update_data
    )
    
    assert result.hashed_password == original_password  # Password unchanged


@pytest.mark.asyncio
async def test_get_all_users_pagination(async_session: AsyncSession, admin_user: User, doctor_user: User):
    """Test pagination functionality."""
    # Create additional users
    for i in range(5):
        user = User(
            email=f"user{i}@test.com",
            full_name=f"Test User {i}",
            role=Role.DOCTOR,
            hashed_password="hashedpass",
            is_active=True
        )
        async_session.add(user)
    await async_session.commit()
    
    # Test first page
    pagination = PaginationParams(skip=0, limit=3)
    sort = SortParams(sort="email")
    search = SearchParams(search="")
    
    result = await user_service.get_all_users(
        session=async_session,
        pagination=pagination,
        sort=sort,
        search=search
    )
    
    assert len(result.data) == 3
    assert result.count == 7  # 2 fixture users + 5 created users
    
    # Test second page
    pagination = PaginationParams(skip=3, limit=3)
    result = await user_service.get_all_users(
        session=async_session,
        pagination=pagination,
        sort=sort,
        search=search
    )
    
    assert len(result.data) == 3
    assert result.count == 7


@pytest.mark.asyncio
async def test_get_all_users_sorting(async_session: AsyncSession):
    """Test sorting functionality."""
    # Create users with different names
    users_data = [
        ("charlie@test.com", "Charlie"),
        ("alice@test.com", "Alice"),
        ("bob@test.com", "Bob"),
    ]
    
    for email, name in users_data:
        user = User(
            email=email,
            full_name=name,
            role=Role.DOCTOR,
            hashed_password="hashedpass",
            is_active=True
        )
        async_session.add(user)
    await async_session.commit()
    
    # Test ascending sort
    pagination = PaginationParams(skip=0, limit=10)
    sort = SortParams(sort="full_name")
    search = SearchParams(search="")
    
    result = await user_service.get_all_users(
        session=async_session,
        pagination=pagination,
        sort=sort,
        search=search
    )
    
    assert result.data[0].full_name == "Alice"
    assert result.data[1].full_name == "Bob"
    assert result.data[2].full_name == "Charlie"
    
    # Test descending sort
    sort = SortParams(sort="-full_name")
    
    result = await user_service.get_all_users(
        session=async_session,
        pagination=pagination,
        sort=sort,
        search=search
    )
    
    assert result.data[0].full_name == "Charlie"
    assert result.data[1].full_name == "Bob"
    assert result.data[2].full_name == "Alice"


@pytest.mark.asyncio
async def test_get_all_users_search(async_session: AsyncSession):
    """Test search functionality."""
    # Create users with different names
    users_data = [
        ("john@test.com", "John Smith"),
        ("jane@test.com", "Jane Doe"),
        ("johnny@test.com", "Johnny Walker"),
    ]
    
    for email, name in users_data:
        user = User(
            email=email,
            full_name=name,
            role=Role.DOCTOR,
            hashed_password="hashedpass",
            is_active=True
        )
        async_session.add(user)
    await async_session.commit()
    
    pagination = PaginationParams(skip=0, limit=10)
    sort = SortParams(sort="full_name")
    
    # Search for "John" - should match "John Smith" and "Johnny Walker"
    search = SearchParams(search="John")
    result = await user_service.get_all_users(
        session=async_session,
        pagination=pagination,
        sort=sort,
        search=search
    )
    
    assert result.count == 2
    assert all("John" in user.full_name if user.full_name else False for user in result.data)
    
    # Search for "Doe" - should match only "Jane Doe"
    search = SearchParams(search="Doe")
    result = await user_service.get_all_users(
        session=async_session,
        pagination=pagination,
        sort=sort,
        search=search
    )
    
    assert result.count == 1
    assert result.data[0].full_name == "Jane Doe"
