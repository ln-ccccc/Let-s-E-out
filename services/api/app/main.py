from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.env import load_env_file

load_env_file()

from app.api.router import api_router

app = FastAPI(title="tandian-fupan-api")


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = exc.detail if isinstance(exc.detail, str) else "INTERNAL_ERROR"
    message = code
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": message}},
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else None
    msg = first.get("msg") if isinstance(first, dict) else "validation error"
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "VALIDATION_ERROR", "message": msg, "details": first}},
    )


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


app.include_router(api_router, prefix="/api/v1")
