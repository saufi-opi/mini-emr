import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.modules.consultation.models import ConsultationBase
from app.modules.diagnoses.schemas import DiagnosisRead

# Consultation Schemas
class ConsultationCreate(ConsultationBase):
    diagnosis_ids: List[uuid.UUID] = []

class ConsultationRead(ConsultationBase):
    id: uuid.UUID
    created_at: datetime
    diagnoses: List[DiagnosisRead]

class ConsultationList(BaseModel):
    id: uuid.UUID
    patient_full_name: str
    doctor_name: str
    created_at: datetime
    diagnosis_count: int
