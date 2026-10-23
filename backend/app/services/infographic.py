"""Infographic service providing Pollinations AI generated topic graphics and local SVG fallbacks."""

from __future__ import annotations

import logging
from pathlib import Path
import urllib.parse

logger = logging.getLogger(__name__)

INFOGRAPHICS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "public" / "infographics"


def build_topic_prompt(topic: str, grade: int = 5) -> str:
    """Build high quality, kid-friendly prompt for educational infographic generation."""
    topic_clean = topic.lower().strip()
    topic_descriptors = {
        "fractions": "fractions, numerator and denominator, colorful fraction bars, pizza slice parts, pie charts",
        "decimals": "decimals, tenths and hundredths place value, money coins, number line with decimal steps",
        "ratios": "ratios and proportions, visual comparison blocks, unit rates, fruit comparison diagrams",
        "geometry": "geometry shapes, rectangles and triangles, area and perimeter formulas, coordinate grid",
    }
    details = topic_descriptors.get(topic_clean, f"{topic_clean} concepts")
    return (
        f"Kid-friendly educational math infographic poster about {details} for Grade {grade} elementary students, "
        f"clean modern vector flat design, vibrant soft colors, high resolution, clear labels"
    )


def get_topic_infographic(
    topic: str,
    grade: int = 5,
    refresh: bool = False,
) -> dict[str, Any]:
    """Build and return Pollinations AI image URL from a topic prompt with local SVG fallback path."""
    topic_clean = topic.lower().strip()
    INFOGRAPHICS_DIR.mkdir(parents=True, exist_ok=True)

    svg_path = INFOGRAPHICS_DIR / f"{topic_clean}.svg"
    prompt = build_topic_prompt(topic_clean, grade=grade)
    encoded_prompt = urllib.parse.quote(prompt)
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"

    return {
        "topic": topic_clean,
        "grade": grade,
        "image_url": pollinations_url,
        "url": pollinations_url,
        "fallback_url": f"/infographics/{topic_clean}.svg",
        "prompt": prompt,
        "format": "svg" if (svg_path.exists() and not refresh) else "png",
        "source": "cache" if (svg_path.exists() and not refresh) else "pollinations_ai",
        "local_path": str(svg_path) if svg_path.exists() else "",
    }
