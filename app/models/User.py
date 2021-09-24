import uuid

from typing import Optional

from pydantic import EmailStr, UUID4

from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: EmailStr
    fullname: Optional[str] = None
    


class User(UserBase):
    key: Optional[str]
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    key: str


class UserUpdate(SQLModel):
    password: Optional[str]
    fullname: Optional[str]
