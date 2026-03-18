from fastapi import FastAPI
from fastapi.responses import JSONResponse
from h11 import Request

import models
from database import engine
from exceptions import AppBaseException
from routers import admin, auth, todo

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.exception_handler(AppBaseException)
async def app_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "path": request.url.path,
            "method": request.method,
        },
    )


app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
