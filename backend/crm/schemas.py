from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str
    tags: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    tags: Optional[str] = None

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class ConversationOut(BaseModel):
    id: int
    user_id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        orm_mode = True