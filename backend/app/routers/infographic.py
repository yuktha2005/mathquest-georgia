"""Infographic retrieval endpoint."""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
from app.limiter import limiter
from app.schemas import InfographicResponse, MathTopic
from app.services.infographic import get_topic_infographic

router = APIRouter(tags=["infographic"])

VALID_TOPICS = {t.value for t in MathTopic}


@router.get("/api/infographic", response_model=InfographicResponse)
@limiter.limit("60/minute")
def get_infographic(
    request: Request,
    topic: str = Query(default="fractions", description="fractions, decimals, ratios, or geometry"),
    grade: int = Query(default=5, ge=5, le=6, description="Grade level: 5 or 6"),
    refresh: bool = Query(default=False, description="Force refresh parameter"),
    render_file: bool = Query(default=False, description="Return the direct image file instead of JSON"),
):
    """Retrieve educational topic infographic with Pollinations.ai image URL and local SVG fallback."""
    clean_topic = topic.strip().lower()
    if clean_topic not in VALID_TOPICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid topic '{topic}'. Must be one of: {', '.join(sorted(VALID_TOPICS))}",
        )

    info = get_topic_infographic(topic=clean_topic, grade=grade, refresh=refresh)
    if render_file and info.get("local_path"):
        media_type = "image/svg+xml" if info["local_path"].endswith(".svg") else "image/png"
        return FileResponse(info["local_path"], media_type=media_type)
    return info
