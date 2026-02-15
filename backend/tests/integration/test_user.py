import pytest
from httpx import AsyncClient

from app.modules.user.models import User, Role


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient, admin_user: User, admin_token: str):
    """Test POST /api/v1/users/ with valid data."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@test.com",
            "full_name": "New User",
            "role": "doctor",
            "password": "securepass123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "doctor"
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, admin_user: User, admin_token: str):
    """Test POST /api/v1/users/ with duplicate email returns 400."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": admin_user.email,  # Duplicate email
            "full_name": "Duplicate User",
            "role": "doctor",
            "password": "password123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "email" in data["detail"].lower()


@pytest.mark.asyncio
async def test_create_user_invalid_email(client: AsyncClient, admin_user: User, admin_token: str):
    """Test POST /api/v1/users/ with invalid email returns 422."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "not-an-email",
            "full_name": "Test User",
            "role": "doctor",
            "password": "password123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_missing_fields(client: AsyncClient, admin_user: User, admin_token: str):
    """Test POST /api/v1/users/ with missing required fields returns 422."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@test.com",
            # Missing password and other fields
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_users_list(client: AsyncClient, admin_user: User, doctor_user: User, admin_token: str):
    """Test GET /api/v1/users/ returns paginated list."""
    response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert data["count"] >= 2  # At least admin and doctor users
    assert len(data["data"]) >= 2


@pytest.mark.asyncio
async def test_get_users_with_pagination(client: AsyncClient, admin_user: User, doctor_user: User, admin_token: str):
    """Test GET /api/v1/users/ with skip/limit parameters."""
    # Get first page
    response = await client.get(
        "/api/v1/users/?skip=0&limit=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["count"] >= 2
    
    # Get second page
    response = await client.get(
        "/api/v1/users/?skip=1&limit=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1


@pytest.mark.asyncio
async def test_get_users_with_sorting_asc(client: AsyncClient, admin_user: User, doctor_user: User, admin_token: str):
    """Test GET /api/v1/users/ with ascending sort parameter."""
    response = await client.get(
        "/api/v1/users/?sort=email",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    emails = [user["email"] for user in data["data"]]
    assert emails == sorted(emails)  # Should be in ascending order


@pytest.mark.asyncio
async def test_get_users_with_sorting_desc(client: AsyncClient, admin_user: User, doctor_user: User, admin_token: str):
    """Test GET /api/v1/users/ with descending sort parameter."""
    response = await client.get(
        "/api/v1/users/?sort=-email",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    emails = [user["email"] for user in data["data"]]
    assert emails == sorted(emails, reverse=True)  # Should be in descending order


@pytest.mark.asyncio
async def test_get_users_with_search(client: AsyncClient, admin_user: User, doctor_user: User, admin_token: str):
    """Test GET /api/v1/users/ with search parameter."""
    # Search for "Admin" in full_name
    response = await client.get(
        "/api/v1/users/?search=Admin",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    # All results should contain "Admin" in full_name
    for user in data["data"]:
        assert "Admin" in user["full_name"]


@pytest.mark.asyncio
async def test_get_users_unauthorized(client: AsyncClient):
    """Test GET /api/v1/users/ without authentication returns 401."""
    response = await client.get("/api/v1/users/")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_unauthorized(client: AsyncClient):
    """Test POST /api/v1/users/ without authentication returns 401."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@test.com",
            "full_name": "Test User",
            "role": "doctor",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_forbidden_doctor(client: AsyncClient, doctor_user: User, doctor_token: str):
    """Test POST /api/v1/users/ with doctor role returns 403 (only admin can create users)."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@test.com",
            "full_name": "New User",
            "role": "doctor",
            "password": "password123"
        },
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    # Should be forbidden since only admins can create users
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_users_forbidden_doctor(client: AsyncClient, doctor_user: User, doctor_token: str):
    """Test GET /api/v1/users/ with doctor role returns 403 (only admin can list users)."""
    response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    # Should be forbidden since only admins can list users
    assert response.status_code == 403
