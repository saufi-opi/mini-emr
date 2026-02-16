import uuid
from datetime import datetime
from app.modules.diagnoses.models import DiagnosisBase

class DiagnosisCreate(DiagnosisBase):
    pass

class DiagnosisRead(DiagnosisBase):
    id: uuid.UUID
    created_at: datetime
