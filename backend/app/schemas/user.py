from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.schemas.role import Role
from app.schemas.profile import Profile

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
    device_mac_address: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: int

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    device_mac_address: Optional[str] = None
    role_id: Optional[int] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    role_id: int
    created_at: datetime
    updated_at: datetime
    role: Role
    profile: Optional[Profile] = None

    class Config:
        from_attributes = True
