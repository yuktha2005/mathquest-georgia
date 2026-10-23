"""Question generation endpoints."""

import logging
from fastapi import APIRouter, Request
from app.limiter import limiter
from app.schemas import (
    AnswerResult,
    AnswerSubmission,
    BatchQuestionResponse,
    Question,
    QuestionRequest,
)
from app.services.adaptive import evaluate_submission
from app.services.question_builder import (
    build_question_pipeline,
    build_questions_batch,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["question"])


@router.post("/api/question")
@router.post("/question")
@limiter.limit("60/minute")
def create_question(request: Request, payload: QuestionRequest) -> Question | BatchQuestionResponse:
    """Generate a single verified question or a batch of questions (e.g. 10 for a round).

    Applies strict math verification, repair retries, and fallback safety per question.
    """
    if payload.count > 1:
        questions, total_retries, latency_ms = build_questions_batch(
            grade=payload.grade,
            topic=payload.topic,
            tier=payload.tier,
            count=payload.count,
        )
        logger.info(
            "POST /api/question (batch %d) completed in %.2fms | total retries: %d | topic: %s | tier: %s",
            len(questions),
            latency_ms,
            total_retries,
            payload.topic,
            payload.tier.value,
        )
        return BatchQuestionResponse(
            questions=questions,
            count=len(questions),
            topic=payload.topic,
            tier=payload.tier,
        )

    question, retries, latency_ms, used_fallback = build_question_pipeline(
        grade=payload.grade,
        topic=payload.topic,
        tier=payload.tier,
    )

    logger.info(
        "POST /api/question completed in %.2fms | retries: %d | fallback: %s | topic: %s | tier: %s | id: %s",
        latency_ms,
        retries,
        used_fallback,
        payload.topic,
        payload.tier.value,
        question.id,
    )

    return question


@router.post("/api/question/batch", response_model=BatchQuestionResponse)
@limiter.limit("20/minute")
def create_question_batch(request: Request, payload: QuestionRequest) -> BatchQuestionResponse:
    """Explicit batch endpoint generating up to 10 questions for a game round or prefetching."""
    count = max(1, min(payload.count if payload.count > 1 else 10, 10))
    questions, total_retries, latency_ms = build_questions_batch(
        grade=payload.grade,
        topic=payload.topic,
        tier=payload.tier,
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
        topic=payload.topic,
        tier=payload.tier,
    )


@router.post("/api/answer", response_model=AnswerResult)
@router.post("/answer", response_model=AnswerResult)
@router.post("/api/question/answer", response_model=AnswerResult)
@limiter.limit("120/minute")
def submit_answer(request: Request, submission: AnswerSubmission) -> AnswerResult:
    """Evaluate a student's answer submission.

    Returns correctness, correct answer, explanation, misconception feedback,
    awarded points, next difficulty tier, updated mastery score, and newly unlocked badges.
    """
    result = evaluate_submission(submission)
    logger.info(
        "POST /api/answer: q_id=%s | correct=%s | points=%d | next_tier=%s | mastery=%.1f | badges=%s",
        submission.question_id,
        result.is_correct,
        result.points,
        result.next_tier.value,
        result.new_mastery,
        result.new_badges,
    )
    return result
