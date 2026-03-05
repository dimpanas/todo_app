from logging import raiseExceptions
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

import models
from data_validation import TodoRequest
from database import SessionLocal, engine
from models import Todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependencies = Annotated[Session, Depends(get_db)]


# CREATE
@app.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependencies, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


# READ
@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependencies):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependencies, todo_id: Annotated[int, Path(gt=0)]):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


# UPDATE
@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependencies, todo_id: Annotated[int, Path(gt=0)], todo_request: TodoRequest
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


# DELETE
@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependencies, todo_id: Annotated[int, Path(gt=0)]):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
