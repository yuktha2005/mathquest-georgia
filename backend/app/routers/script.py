"""Router for educational 6-slide video scripts."""

from fastapi import APIRouter, Request
from app.limiter import limiter
from app.schemas import ScriptRequest, ScriptResponse
from app.services.script_generator import get_topic_script

router = APIRouter(tags=["script"])


@router.post("/api/script", response_model=ScriptResponse)
@limiter.limit("30/minute")
def generate_script(request: Request, payload: ScriptRequest) -> ScriptResponse:
    """Return a 6-slide educational video presentation script for a math topic."""
    return get_topic_script(
        grade=payload.grade,
        topic=payload.topic,
    )
