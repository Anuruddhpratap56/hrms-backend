from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status

from .attendance import model as attendance_model
from .attendance import router as attendance_router
from .employees import model as employee_model
from .employees import router as employee_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="HRMS Lite API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    errors = exc.errors()
    first_message = errors[0].get("msg", "Validation failed") if errors else "Validation failed"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": first_message, "errors": errors},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(employee_router.router)
app.include_router(attendance_router.router)
add_pagination(app)
