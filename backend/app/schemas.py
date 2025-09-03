from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ---------- User Schemas ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # (orm_mode in Pydantic v1)


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str


# ---------- Task Schemas ----------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
