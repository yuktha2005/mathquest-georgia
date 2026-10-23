"""Main entrypoint for the MathQuest Georgia FastAPI backend."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.limiter import limiter
from app.schemas import HealthResponse
from app.routers.question import router as question_router
from app.routers.infographic import router as infographic_router
from app.routers.evaluation import router as eval_router
from app.routers.explain import router as explain_router
from app.routers.script import router as script_router

logger = logging.getLogger(__name__)

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="MathQuest Georgia API",
    description="Gamified, adaptive math learning platform backend for Grade 5 & 6 (MGSE).",
    version="0.1.0",
)

# Attach slowapi rate limiter state
app.state.limiter = limiter

# Global Exception Handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Child-friendly 429 response when request limits are exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too Many Requests",
            "message": "Whoa there, math explorer! Slow down a little bit so our server can catch its breath.",
            "detail": str(exc.detail),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Child-friendly 422 response for missing or invalid input parameters."""
    errors: list[dict[str, str]] = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        errors.append({
            "field": field_path or "request",
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Oops! Some information was missing or incorrect. Please check your inputs.",
            "details": errors,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Consistent JSON formatting for standard HTTP errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail if isinstance(exc.detail, str) else "Request error",
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all 500 handler preventing secrets or internal trace leaks to the client."""
    logger.error("Unhandled server exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Our math engine encountered an unexpected hiccup. Please try again in a moment.",
            "status_code": 500,
        },
    )


# Configure CORS reading FRONTEND_URL from environment
frontend_env = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in frontend_env.split(",") if origin.strip()]

# Ensure local dev default is always accessible
if "http://localhost:3000" not in allowed_origins:
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(question_router)
app.include_router(infographic_router)
app.include_router(explain_router)
app.include_router(script_router)
app.include_router(eval_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    """Service health check endpoint verifying server availability."""
    return HealthResponse(
        status="ok",
        app="MathQuest Georgia API",
        version="0.1.0",
    )


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    """Root welcoming endpoint with links to documentation."""
    return {
        "message": "Welcome to MathQuest Georgia API",
        "docs_url": "/docs",
        "health_url": "/health",
    }
