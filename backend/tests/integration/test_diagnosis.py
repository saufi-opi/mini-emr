import pytest
from httpx import AsyncClient
from app.modules.diagnoses.models import Diagnosis

@pytest.mark.asyncio
async def test_search_diagnoses_unauthenticated(client: AsyncClient):
    """Test searching diagnoses without authentication returns 401."""
    response = await client.get("/api/v1/diagnosis/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_search_diagnoses_authenticated(client: AsyncClient, doctor_token: str, async_session):
    """Test searching diagnoses with authentication returns 200."""
    # Add some test data
    diag = Diagnosis(code="H00", description="Hordeolum and chalazion")
    async_session.add(diag)
    await async_session.commit()
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    response = await client.get("/api/v1/diagnosis/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["code"] == "H00"

@pytest.mark.asyncio
async def test_search_diagnoses_with_query(client: AsyncClient, doctor_token: str, async_session):
    """Test searching diagnoses with a search query."""
    # Add test data
    diagnoses = [
        Diagnosis(code="I00", description="Rheumatic fever"),
        Diagnosis(code="I10", description="Essential (primary) hypertension"),
    ]
    for d in diagnoses:
        async_session.add(d)
    await async_session.commit()
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    # Search for "Hypertension"
    response = await client.get("/api/v1/diagnosis/?search=hypertension", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["code"] == "I10"

@pytest.mark.asyncio
async def test_search_diagnoses_pagination(client: AsyncClient, doctor_token: str, async_session):
    """Test searching diagnoses with pagination."""
    # Add test data
    for i in range(10):
        diag = Diagnosis(code=f"J{i:02d}", description=f"Desc {i}")
        async_session.add(diag)
    await async_session.commit()
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    # Get first page
    response = await client.get("/api/v1/diagnosis/?limit=5&skip=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["count"] == 10
    
    # Get second page
    response = await client.get("/api/v1/diagnosis/?limit=5&skip=5", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5

