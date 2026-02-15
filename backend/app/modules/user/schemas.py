from app.modules.user.models import UserBase
from typing import Optional
from sqlmodel import SQLModel
from pydantic import EmailStr
import uuid

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: uuid.UUID

class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None