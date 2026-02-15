import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import EmailStr
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    full_name: Optional[str] = None
    role: Role = Role.DOCTOR
    is_active: bool = True

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
