import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from exceptions import (
    AuthenticationException,
    UserAlreadyExist,
)
from models import UserRole, Users
from schemas import UserRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

db_dependencies = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


# LOGIN(JWT)
def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    expires = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": username, "id": user_id, "role": role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="auth/login"))],
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise AuthenticationException(details="Could not validate user")

        return {"username": username, "id": user_id, "role": role}
    except JWTError:
        raise AuthenticationException(details="Could not validate user")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    db: db_dependencies, from_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = db.query(Users).filter(Users.username == from_data.username).first()

    if not user:
        raise AuthenticationException(details="Username not found")

    password = bcrypt_context.verify(from_data.password, user.hashed_password)

    if not password:
        raise AuthenticationException(details="Incorrect Password")

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )

    return {"access_token": token, "token_type": "bearer"}


# REGISTER
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(db: db_dependencies, create_user_request: UserRequest):

    existing_email = (
        db.query(Users).filter(Users.email == create_user_request.email).first()
    )
    existing_username = (
        db.query(Users).filter(Users.username == create_user_request.username).first()
    )
    if existing_email:
        raise UserAlreadyExist(details="Email already registered")
    if existing_username:
        raise UserAlreadyExist(details="Username already registered")

    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=UserRole.USER,
        hashed_password=bcrypt_context.hash(create_user_request.hashed_password),
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model
