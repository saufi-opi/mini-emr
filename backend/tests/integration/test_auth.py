import pytest
from httpx import AsyncClient
from app.modules.user.models import Role
from app.core.security import get_password_hash

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user):
    """Test successful login returns access token and sets refresh cookie."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "testpassword123"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_login_failure(client: AsyncClient, admin_user):
    """Test login with incorrect password returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "wrongpassword"},
    )
    
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_rate_limit(client: AsyncClient, admin_user):
    """Test login rate limiting (5 per hour)."""
    # Note: This test might depend on the Redis state and how limiter is configured for tests.
    # In a real test environment, we might need to flush redis or use a mock.
    
    for _ in range(5):
        await client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "wrongpassword"},
        )
    
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "wrongpassword"},
    )
    
    assert response.status_code == 429
    assert "too many requests" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, admin_user):
    """Test refreshing access token using refresh cookie."""
    # First login to get the cookie
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "testpassword123"},
    )
    
    # Use the cookie from the login response for the refresh request
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        cookies=login_response.cookies
    )
    
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


@pytest.mark.asyncio
async def test_logout_blacklists_tokens(client: AsyncClient, admin_user):
    """Test logout blacklists access token and clears cookies."""
    # 1. Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "testpassword123"},
    )
    access_token = login_response.json()["access_token"]
    
    # 2. Verify access works
    me_response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_response.status_code == 200
    
    # 3. Logout
    logout_response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        cookies=login_response.cookies
    )
    assert logout_response.status_code == 200
    assert "refresh_token" not in logout_response.cookies or logout_response.cookies.get("refresh_token") == ""
    
    # 4. Verify original access token no longer works (blacklisted)
    blocked_response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert blocked_response.status_code == 401
    
    # 5. Verify refresh token no longer works
    blocked_refresh = await client.post(
        "/api/v1/auth/refresh",
        cookies=login_response.cookies
    )
    assert blocked_refresh.status_code == 401
