"""Infographic service providing cached and live Pollinations-generated topic graphics.

Enforces caching: prefers pre-generated files in frontend/public/infographics/,
falling back to or optionally refreshing via Pollinations AI.
"""

from __future__ import annotations

import logging
from pathlib import Path
import urllib.parse
import httpx

logger = logging.getLogger(__name__)

INFOGRAPHICS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "public" / "infographics"


def get_topic_infographic(
    topic: str,
    refresh: bool = False,
) -> dict[str, str]:
    """Retrieve infographic path or url for a topic, preferring cached file.

    Args:
        topic: fractions, decimals, ratios, or geometry.
        refresh: Whether to force live regeneration from Pollinations AI.

    Returns:
        dict containing url, format, source, and local_path.
    """
    topic_clean = topic.lower().strip()
    INFOGRAPHICS_DIR.mkdir(parents=True, exist_ok=True)

    svg_path = INFOGRAPHICS_DIR / f"{topic_clean}.svg"
    png_path = INFOGRAPHICS_DIR / f"{topic_clean}.png"

    # 1. Prefer cached local file if refresh is not explicitly requested
    if not refresh:
        if svg_path.exists():
            return {
                "topic": topic_clean,
                "url": f"/infographics/{topic_clean}.svg",
                "format": "svg",
                "source": "cache",
                "local_path": str(svg_path),
            }
        if png_path.exists():
            return {
                "topic": topic_clean,
                "url": f"/infographics/{topic_clean}.png",
                "format": "png",
                "source": "cache",
                "local_path": str(png_path),
            }

    # 2. Live generation from Pollinations AI
    prompt = f"Educational math infographic poster about {topic_clean} for Grade 5 and 6 students, colorful clean diagrams, vector art style"
    encoded_prompt = urllib.parse.quote(prompt)
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"

    try:
        logger.info("Attempting live infographic generation via Pollinations AI for topic '%s'", topic_clean)
        response = httpx.get(pollinations_url, timeout=12.0)
        if response.status_code == 200 and len(response.content) > 1000:
            png_path.write_bytes(response.content)
            return {
                "topic": topic_clean,
                "url": f"/infographics/{topic_clean}.png",
                "format": "png",
                "source": "live_pollinations",
                "local_path": str(png_path),
            }
    except Exception as exc:
        logger.warning("Live Pollinations generation failed: %s. Falling back to cached asset.", exc)

    # 3. Fallback to cached SVG if live generation failed
    if svg_path.exists():
        return {
            "topic": topic_clean,
            "url": f"/infographics/{topic_clean}.svg",
            "format": "svg",
            "source": "cache_fallback",
            "local_path": str(svg_path),
        }

    return {
        "topic": topic_clean,
        "url": pollinations_url,
        "format": "remote_url",
        "source": "pollinations_direct_url",
        "local_path": "",
    }
