from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models import Users
from schemas import UserResponse

router = APIRouter()

db_dependencies = Annotated[Session, Depends(get_db)]


# READ
@router.get(
    "/get_users", response_model=list[UserResponse], status_code=status.HTTP_200_OK
)
async def get_users(db: db_dependencies):
    return db.query(Users).all()


# UPDATE


# DELETE
