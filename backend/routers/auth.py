from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Request
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from config import settings
from database import get_db
from exceptions import (
    AuthenticationException,
    ResourceNotFoundException,
    UnauthorizedActionException,
    UserAlreadyExist,
)
from limiter import limiter
from models import UserRole, Users
from schemas import TokenResponse, UserRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

db_dependencies = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY


def create_refresh_token(username: str, user_id: int):
    expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": username, "id": user_id, "exp": expires}
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    expires = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": username, "id": user_id, "role": role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="auth/login"))],
    db: db_dependencies,
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise AuthenticationException(details="Could not validate user")

        user_model = db.query(Users).filter(Users.id == user_id).first()
        if user_model is None:
            raise ResourceNotFoundException(resource_name="User", resource_id=user_id)

        if user_model.refresh_token is None:
            raise UnauthorizedActionException("Session expired. Please login again.")

        if not user_model.is_active:
            raise UnauthorizedActionException(details="User account is deactivated")

        return {"username": username, "id": user_id, "role": role}

    except JWTError:
        raise UnauthorizedActionException(details="Access token expired or invalid")


def get_admin_user(user: Annotated[dict, Depends(get_current_user)]):
    if user is None:
        raise AuthenticationException()

    if user.get("role") != "admin":
        raise UnauthorizedActionException(details="Admin privileges required")
    return user


# LOGIN
@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    db: db_dependencies,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = db.query(Users).filter(Users.username == form_data.username).first()

    if not user:
        raise AuthenticationException(details="Username not found")

    password = bcrypt_context.verify(form_data.password, user.hashed_password)

    if not password:
        raise AuthenticationException(details="Incorrect Password")

    refresh_token = create_refresh_token(user.username, user.id)

    user.refresh_token = refresh_token
    db.add(user)
    db.commit()

    access_token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# REFRESH
@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_login(db: db_dependencies, refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise AuthenticationException(details="Invalid refresh token")
    except JWTError:
        raise AuthenticationException(details="Refresh token expired or invalid")

    user = db.query(Users).filter(Users.id == user_id).first()

    if not user or user.refresh_token != refresh_token:
        raise AuthenticationException(details="Refresh token does not match")

    access_token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )

    new_refresh_token = create_refresh_token(user.username, user.id)

    user.refresh_token = new_refresh_token
    db.add(user)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# REGISTER
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("3/hour")
async def create_user(
    request: Request, db: db_dependencies, create_user_request: UserRequest
):

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


# LOGOUT
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(db: db_dependencies, user: Annotated[dict, Depends(get_current_user)]):

    if user is None:
        raise AuthenticationException()

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model:
        user_model.refresh_token = None
        db.add(user_model)
        db.commit()
    else:
        raise ResourceNotFoundException(
            resource_name="User", resource_id=user.get("id")
        )
