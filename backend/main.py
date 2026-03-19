from exceptions import AppBaseException
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import admin, auth, todo

origins = [
    "http://localhost:5173",  # Vite default
    "https://yourdomain.com",
]
app = FastAPI()

# models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
