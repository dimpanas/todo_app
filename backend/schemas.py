from __future__ import annotations

from models import UserRole
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)


class TodoPaginationResponse(BaseModel):
    items: list[TodoResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class TodoRequest(TodoBase):
    pass


class TodoResponse(TodoBase):
    id: int = Field(gt=0)
    owner_id: int
    owner: UserUsername

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str
    username: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    role: UserRole = UserRole.USER
    is_active: bool


class UserUsername(BaseModel):
    username: str

    class Config:
        from_attributes = True


class UserPaginationResponse(BaseModel):
    items: list[UserResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class UserRequest(UserBase):
    hashed_password: str = Field(min_length=8)


class UserResponse(UserBase):
    id: int = Field(gt=0)

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True
