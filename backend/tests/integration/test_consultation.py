import pytest
import uuid
from httpx import AsyncClient
from app.modules.consultation.models import Consultation
from app.modules.diagnoses.models import Diagnosis
from app.modules.user.models import User, Role

@pytest.mark.asyncio
async def test_create_consultation_success(client: AsyncClient, doctor_token: str, async_session):
    """Test creating a consultation successfully."""
    # Create a diagnosis
    diag = Diagnosis(code="A00", description="Cholera")
    async_session.add(diag)
    await async_session.commit()
    await async_session.refresh(diag)
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    payload = {
        "patient_full_name": "John Doe",
        "notes": "Patient reports mild fever.",
        "diagnosis_ids": [str(diag.id)]
    }
    
    response = await client.post("/api/v1/consultation/", json=payload, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["notes"] == "Patient reports mild fever."
    assert data["patient_full_name"] == "John Doe"
    assert len(data["diagnoses"]) == 1
    assert data["diagnoses"][0]["code"] == "A00"

@pytest.mark.asyncio
async def test_list_consultations_permissions(client: AsyncClient, doctor_token: str, admin_token: str, async_session, doctor_user):
    """Test that doctors only see their own consultations while admins see all."""
    # Create another doctor
    other_doctor = User(
        email="other@test.com",
        full_name="Other Doctor",
        role=Role.DOCTOR,
        hashed_password="hashed",
    )
    async_session.add(other_doctor)
    
    # Consultation for doctor_user
    c1 = Consultation(patient_full_name="Patient 1", doctor_id=doctor_user.id, notes="Doc 1 notes")
    # Consultation for other_doctor
    c2 = Consultation(patient_full_name="Patient 2", doctor_id=other_doctor.id, notes="Doc 2 notes")
    
    async_session.add_all([c1, c2])
    await async_session.commit()
    
    # 1. Doctor list - should only see 1
    headers = {"Authorization": f"Bearer {doctor_token}"}
    response = await client.get("/api/v1/consultation/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["notes"] == "Doc 1 notes"
    
    # 2. Admin list - should see 2
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/v1/consultation/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2

@pytest.mark.asyncio
async def test_get_consultation_details(client: AsyncClient, doctor_token: str, async_session, doctor_user):
    """Test getting single consultation details."""
    consultation = Consultation(patient_full_name="Jane Doe", doctor_id=doctor_user.id, notes="Detail notes")
    async_session.add(consultation)
    await async_session.commit()
    await async_session.refresh(consultation)
    
    headers = {"Authorization": f"Bearer {doctor_token}"}
    response = await client.get(f"/api/v1/consultation/{consultation.id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "Detail notes"
    assert data["patient_full_name"] == "Jane Doe"

@pytest.mark.asyncio
async def test_get_consultation_forbidden(client: AsyncClient, doctor_token: str, async_session):
    """Test that a doctor cannot access another doctor's consultation."""
    # Create another doctor and their consultation
    other_doctor = User(email="other2@test.com", full_name="Other Doc", role=Role.DOCTOR, hashed_password="hashed")
    async_session.add(other_doctor)
    await async_session.flush()
    
    consultation = Consultation(patient_full_name="Others Patient", doctor_id=other_doctor.id, notes="Private notes")
    async_session.add(consultation)
    await async_session.commit()
    
    # Current doctor tries to access it
    headers = {"Authorization": f"Bearer {doctor_token}"}
    response = await client.get(f"/api/v1/consultation/{consultation.id}", headers=headers)
    
    assert response.status_code == 403
    assert "detail" in response.json()
