import math
from typing import Annotated

from database import get_db
from exceptions import (
    ResourceNotFoundException,
    UnauthorizedActionException,
)
from fastapi import APIRouter, Path, Request
from fastapi.params import Depends
from main import limiter
from models import Todos, Users
from schemas import TodoPaginationResponse, TodoRequest, TodoResponse
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


db_dependencies = Annotated[Session, Depends(get_db)]
user_dependencies = Annotated[dict, Depends(get_current_user)]


def get_todo(db: Session, user: dict, todo_id: int):

    query = db.query(Todos).filter(Todos.id == todo_id)

    if user.get("role") != "admin":
        query = query.filter(Todos.owner_id == user.get("id"))

    todo_model = query.first()

    if todo_model is None:
        raise ResourceNotFoundException(resource_name="Todo", resource_id=todo_id)

    return todo_model


# CREATE
@router.post(
    "/create_todo",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/minute")
async def create_todo(
    request: Request,
    user: user_dependencies,
    db: db_dependencies,
    todo_request: TodoRequest,
    target_user_id: int = None,
):
    final_owner_id = user.get("id")

    if target_user_id is not None:
        if user.get("role") != "admin":
            raise UnauthorizedActionException()
        check_user = db.query(Users).filter(Users.id == target_user_id).first()
        if not check_user:
            raise ResourceNotFoundException(
                resource_name="User", resource_id=target_user_id
            )
        final_owner_id = target_user_id

    todo_model = Todos(**todo_request.model_dump(), owner_id=final_owner_id)
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


# READ
@router.get("/", response_model=TodoPaginationResponse, status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
async def read_all_todos(
    request: Request,
    db: db_dependencies,
    user: user_dependencies,
    all_records: bool = False,
    page: int = 1,
    page_size: int = 10,
):
    skip = (page - 1) * page_size
    query = db.query(Todos)

    if not (all_records and user.get("role") == "admin"):
        query = query.filter(Todos.owner_id == user.get("id"))

    total_count = query.count()
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

    todos = query.offset(skip).limit(page_size).all()

    return {
        "items": todos,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get(
    "/todo/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK
)
async def read_todo(
    user: user_dependencies,
    db: db_dependencies,
    todo_id: Annotated[int, Path(gt=0)],
):
    return get_todo(db, user, todo_id)


# UPDATE
@router.put(
    "/todo/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Todo not found"},
        401: {"description": "User not found"},
    },
)
@limiter.limit("30/minute")
async def update_todo(
    request: Request,
    user: user_dependencies,
    db: db_dependencies,
    todo_id: Annotated[int, Path(gt=0)],
    todo_request: TodoRequest,
):
    todo_model = get_todo(db, user, todo_id)

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


# DELETE
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_todo(
    request: Request,
    user: user_dependencies,
    db: db_dependencies,
    todo_id: Annotated[int, Path(gt=0)],
):
    todo_model = get_todo(db, user, todo_id)
    db.delete(todo_model)
    db.commit()
