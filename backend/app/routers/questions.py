"""Question generation and submission endpoints."""

from fastapi import APIRouter
from app.schemas import Question, AnswerSubmission, AnswerResult

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/placeholder", response_model=dict)
def get_questions_info() -> dict[str, str]:
    """Information endpoint for question pipeline."""
    return {
        "status": "ready",
        "message": "Question generation and evaluation router initialized.",
    }
