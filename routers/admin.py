from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from fastapi.params import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models import Users
from schemas import UserRequest, UserResponse

from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db_dependencies = Annotated[Session, Depends(get_db)]
user_dependencies = Annotated[dict, Depends(get_current_user)]

auth_failed = "Authentication Failed"
user_not_found = "User not found"


# CREATE
@router.post(
    "/create_user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"description": "Username or email already registered"}},
)
async def create_user(
    user: user_dependencies, db: db_dependencies, create_user_request: UserRequest
):
    existing_email = (
        db.query(Users).filter(Users.email == create_user_request.email).first()
    )
    existing_username = (
        db.query(Users).filter(Users.username == create_user_request.username).first()
    )
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.hashed_password),
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model


# READ
@router.get(
    "/get_users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "User not found"}},
)
async def get_users(user: user_dependencies, db: db_dependencies):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail=auth_failed)
    return db.query(Users).all()


@router.get(
    "/get_user/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "User not found"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user: user_dependencies, db: db_dependencies, user_id: Annotated[int, Path(gt=0)]
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail=auth_failed)

    user_model = db.query(Users).filter(Users.id == user_id).first()

    if user_model is not None:
        return user_model
    raise HTTPException(status_code=404, detail=user_not_found)


# UPDATE
@router.put(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Todo not found"},
        401: {"description": "User not found"},
    },
)
async def update_user(
    user: user_dependencies,
    db: db_dependencies,
    user_id: Annotated[int, Path(gt=0)],
    user_request: UserRequest,
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail=auth_failed)

    user_model = db.query(Users).filter(Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail=user_not_found)

    user_model.email = user_request.email
    user_model.username = user_request.username
    user_model.first_name = user_request.first_name
    user_model.last_name = user_request.last_name
    user_model.role = user_request.role
    user_model.is_active = user_request.is_active
    db.add(user_model)
    db.commit()


# DELETE
@router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"description": "User not found"}},
)
async def delete_user(
    user: user_dependencies, db: db_dependencies, user_id=Annotated[int, Path(gt=0)]
):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail=auth_failed)

    user_model = db.query(Users).filter(Users.id == user_id).first()

    db.delete(user_model)
    db.commit()
