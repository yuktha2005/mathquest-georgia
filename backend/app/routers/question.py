"""Question generation endpoints."""

import logging
from fastapi import APIRouter
from app.schemas import BatchQuestionResponse, Question, QuestionRequest
from app.services.question_builder import (
    build_question_pipeline,
    build_questions_batch,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["question"])


@router.post("/api/question")
@router.post("/question")
def create_question(request: QuestionRequest) -> Question | BatchQuestionResponse:
    """Generate a single verified question or a batch of questions (e.g. 10 for a round).

    Applies strict math verification, repair retries, and fallback safety per question.
    """
    if request.count > 1:
        questions, total_retries, latency_ms = build_questions_batch(
            grade=request.grade,
            topic=request.topic,
            tier=request.tier,
            count=request.count,
        )
        logger.info(
            "POST /api/question (batch %d) completed in %.2fms | total retries: %d | topic: %s | tier: %s",
            len(questions),
            latency_ms,
            total_retries,
            request.topic,
            request.tier.value,
        )
        return BatchQuestionResponse(
            questions=questions,
            count=len(questions),
            topic=request.topic,
            tier=request.tier,
        )

    question, retries, latency_ms, used_fallback = build_question_pipeline(
        grade=request.grade,
        topic=request.topic,
        tier=request.tier,
    )

    logger.info(
        "POST /api/question completed in %.2fms | retries: %d | fallback: %s | topic: %s | tier: %s | id: %s",
        latency_ms,
        retries,
        used_fallback,
        request.topic,
        request.tier.value,
        question.id,
    )

    return question


@router.post("/api/question/batch", response_model=BatchQuestionResponse)
def create_question_batch(request: QuestionRequest) -> BatchQuestionResponse:
    """Explicit batch endpoint generating up to 10 questions for a game round or prefetching."""
    count = max(1, min(request.count if request.count > 1 else 10, 10))
    questions, total_retries, latency_ms = build_questions_batch(
        grade=request.grade,
        topic=request.topic,
        tier=request.tier,
        count=count,
    )
    logger.info(
        "POST /api/question/batch (%d questions) completed in %.2fms | total retries: %d",
        len(questions),
        latency_ms,
        total_retries,
    )
    return BatchQuestionResponse(
        questions=questions,
        count=len(questions),
        topic=request.topic,
        tier=request.tier,
    )
