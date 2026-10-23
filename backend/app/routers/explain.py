"""Router for pedagogical concept explanations."""

from fastapi import APIRouter, Request
from app.limiter import limiter
from app.schemas import ExplainRequest, ExplainResponse
from app.services.explainer import get_topic_explanation

router = APIRouter(tags=["explanation"])


@router.post("/api/explain", response_model=ExplainResponse)
@limiter.limit("30/minute")
def explain_topic(request: Request, payload: ExplainRequest) -> ExplainResponse:
    """Return structured pedagogical explanation for grade and topic with verified worked examples."""
    return get_topic_explanation(
        grade=payload.grade,
        topic=payload.topic,
        style=payload.style,
    )
