from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class UserRole(str, Enum):
    CLIENT = "client"
    LAWYER = "lawyer"


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str
    role: UserRole = Field(default=UserRole.CLIENT)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    # Social Network
    posts: List["Post"] = Relationship(back_populates="author")


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class PostBase(SQLModel):
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id")
    author: User = Relationship(back_populates="posts")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
