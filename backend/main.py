from config import settings
from exceptions import AppBaseException
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import admin, auth, todo
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute", "1000/hour"],
)

app = FastAPI()

# models.Base.metadata.create_all(bind=engine)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGIN,
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
