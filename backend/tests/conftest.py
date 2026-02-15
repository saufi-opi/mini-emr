import pytest
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from app.main import app

@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create a new FastAPI TestClient that uses the `app` fixture.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
