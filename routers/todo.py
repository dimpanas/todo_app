from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models import Todos
from schemas import TodoRequest, TodoResponse

router = APIRouter()


db_dependencies = Annotated[Session, Depends(get_db)]

not_found = "Todo not found"


# CREATE
@router.post(
    "/create_todo", response_model=TodoResponse, status_code=status.HTTP_201_CREATED
)
async def create_todo(db: db_dependencies, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


# READ
@router.get("/", response_model=list[TodoResponse], status_code=status.HTTP_200_OK)
async def read_all_todos(db: db_dependencies):
    return db.query(Todos).all()


@router.get(
    "/todo/{todo_id}",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Todo not found"}},
)
async def read_todo(db: db_dependencies, todo_id: Annotated[int, Path(gt=0)]):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail=not_found)


# UPDATE
@router.put(
    "/todo/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Todo not found"}},
)
async def update_todo(
    db: db_dependencies, todo_id: Annotated[int, Path(gt=0)], todo_request: TodoRequest
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=not_found)

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


# DELETE
@router.delete(
    "/todo/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Todo not found"}},
)
async def delete_todo(db: db_dependencies, todo_id: Annotated[int, Path(gt=0)]):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=not_found)
    # db.query(Todos).filter(Todos.id == todo_id).delete()
    db.delete(todo_model)
    db.commit()
