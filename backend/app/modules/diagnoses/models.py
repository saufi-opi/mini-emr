import uuid
from datetime import datetime, UTC
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel

class DiagnosisBase(SQLModel):
    code: str = Field(unique=True, index=True, max_length=10)
    description: str = Field(max_length=255)

class Diagnosis(DiagnosisBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
