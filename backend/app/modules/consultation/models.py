import uuid
from datetime import datetime, UTC
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.modules.user.models import User
    from app.modules.diagnoses.models import Diagnosis

class ConsultationDiagnosis(SQLModel, table=True):
    __tablename__ = "consultation_diagnoses"
    
    consultation_id: uuid.UUID = Field(foreign_key="consultation.id", primary_key=True)
    diagnosis_id: uuid.UUID = Field(foreign_key="diagnosis.id", primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))

class ConsultationBase(SQLModel):
    patient_full_name: str = Field(max_length=255)
    doctor_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    notes: str = Field(default="")

class Consultation(ConsultationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    doctor: "User" = Relationship()
    diagnoses: List["Diagnosis"] = Relationship(
        link_model=ConsultationDiagnosis
    )
