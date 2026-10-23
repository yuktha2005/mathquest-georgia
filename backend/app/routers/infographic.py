"""Infographic retrieval endpoint."""

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from app.services.infographic import get_topic_infographic

router = APIRouter(tags=["infographic"])


@router.get("/api/infographic")
def get_infographic(
    topic: str = Query(default="fractions", description="fractions, decimals, ratios, or geometry"),
    refresh: bool = Query(default=False, description="Force live generation via Pollinations AI"),
    render_file: bool = Query(default=False, description="Return the direct image file instead of JSON"),
):
    """Retrieve educational topic infographic, preferring local cached asset."""
    info = get_topic_infographic(topic=topic, refresh=refresh)
    if render_file and info.get("local_path"):
        media_type = "image/svg+xml" if info.get("format") == "svg" else "image/png"
        return FileResponse(info["local_path"], media_type=media_type)
    return info
