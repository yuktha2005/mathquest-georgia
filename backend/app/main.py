"""Main entrypoint for the MathQuest Georgia FastAPI backend."""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import HealthResponse
from app.routers.questions import router as questions_router
from app.routers.question import router as question_router
from app.routers.infographic import router as infographic_router
from app.routers.evaluation import router as eval_router

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="MathQuest Georgia API",
    description="Gamified, adaptive math learning platform backend for Grade 5 & 6 (MGSE).",
    version="0.1.0",
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
app.include_router(questions_router)
app.include_router(question_router)
app.include_router(infographic_router)
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
