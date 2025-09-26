import re
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

class UserRole(str, Enum):
    admin = "admin"
    staff = "staff"

class UserBase(BaseModel):
    username: str = Field(..., min_length=6, max_length=15, pattern=r"^[a-z0-9]+$")
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=20)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@]", v):
            raise ValueError("Password must contain at least one of the special characters: !@")
        if not re.match(r"^[a-zA-Z0-9!@]+$", v):
            raise ValueError("Password contains invalid characters. Only alphanumeric and !@ are allowed.")
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=6, max_length=15, pattern=r"^[a-z0-9]+$")
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

class User(UserBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)