from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.routers import health, submissions

settings = get_settings()

app = FastAPI(title="Lyric Assistant API", version=settings.version)

app.include_router(health.router)
app.include_router(submissions.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        body = detail
    else:
        body = {"error": "http_error", "detail": str(detail)}
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "bad_request", "detail": exc.errors()},
    )
