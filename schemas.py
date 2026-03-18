from pydantic import BaseModel, Field

from models import UserRole


class TodoBase(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


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


class UserRequest(UserBase):
    hashed_password: str = Field(min_length=8)


class UserResponse(UserBase):
    id: int = Field(gt=0)

    class Config:
        from_attributes = True


class UserUsername(BaseModel):
    username: str

    class Config:
        from_attributes = True
