"""Standards retrieval service (RAG) for Georgia Standards of Excellence (MGSE).

Attempts retrieval via Supabase Postgres vector search.
If Supabase is unconfigured, unreachable, or encounters network errors,
falls back to local keyword matching over data/standards/*.md files.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import re

logger = logging.getLogger(__name__)

STANDARDS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "standards"


def _search_local_standards(
    query: str,
    topic: str | None = None,
    grade: int | None = None,
    limit: int = 3,
) -> list[dict]:
    """Search data/standards/*.md using keyword relevance."""
    results: list[dict] = []
    query_tokens = set(re.findall(r"\w+", query.lower()))

    # Determine files to read
    if topic and (STANDARDS_DIR / f"{topic.lower()}.md").exists():
        files = [STANDARDS_DIR / f"{topic.lower()}.md"]
    else:
        files = list(STANDARDS_DIR.glob("*.md"))

    for filepath in files:
        file_topic = filepath.stem
        content = filepath.read_text(encoding="utf-8")

        # Split into standard blocks by "### MGSE"
        sections = re.split(r"(?=###\s+MGSE)", content)
        for sec in sections:
            if not sec.strip().startswith("###"):
                continue

            lines = sec.strip().splitlines()
            header = lines[0].replace("###", "").strip()
            body = "\n".join(lines[1:]).strip()

            # Extract grade from header e.g. MGSE5.NF.1 -> grade 5
            extracted_grade = None
            grade_match = re.search(r"MGSE(\d)", header)
            if grade_match:
                extracted_grade = int(grade_match.group(1))

            if grade and extracted_grade and grade != extracted_grade:
                continue

            sec_tokens = set(re.findall(r"\w+", sec.lower()))
            overlap = len(query_tokens & sec_tokens)

            # Boost if query explicitly mentioned standard code
            if any(token in header.lower() for token in query_tokens):
                overlap += 5

            results.append({
                "standard_code": header,
                "topic": file_topic,
                "grade": extracted_grade or grade or 5,
                "content": body,
                "score": overlap,
                "source": "local_standards_fallback",
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def retrieve_standards(
    query: str,
    topic: str | None = None,
    grade: int | None = None,
    limit: int = 3,
) -> list[dict]:
    """Retrieve relevant MGSE standards via Supabase, with automatic local fallback."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            client = create_client(supabase_url, supabase_key)
            query_builder = client.table("standards").select("*")
            if topic:
                query_builder = query_builder.eq("topic", topic.lower())
            if grade:
                query_builder = query_builder.eq("grade", grade)
            response = query_builder.ilike("description", f"%{query}%").limit(limit).execute()
            if response.data:
                return [
                    {
                        "standard_code": row.get("code", "MGSE"),
                        "topic": row.get("topic", topic or "general"),
                        "grade": row.get("grade", grade or 5),
                        "content": row.get("description", ""),
                        "score": 10,
                        "source": "supabase",
                    }
                    for row in response.data
                ]
        except Exception as exc:
            logger.warning("Supabase lookup failed (%s). Falling back to data/standards/*.md.", exc)

    logger.info("Using local standards keyword matching fallback for query: '%s'", query)
    return _search_local_standards(query=query, topic=topic, grade=grade, limit=limit)
