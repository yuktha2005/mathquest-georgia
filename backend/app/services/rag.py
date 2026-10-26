"""Standards retrieval service (RAG) for Georgia Standards of Excellence (MGSE).

Attempts semantic vector retrieval via Supabase Postgres pgvector using Gemini embeddings.
If Supabase is unconfigured, unreachable, or encounters network errors,
falls back to local keyword matching over data/standards/*.md files.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import re
from typing import Any

logger = logging.getLogger(__name__)

STANDARDS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "standards"


def _search_local_standards(
    query: str = "",
    topic: str | None = None,
    grade: int | None = None,
    limit: int = 2,
) -> list[dict[str, Any]]:
    """Search data/standards/*.md using keyword relevance and filters."""
    results: list[dict[str, Any]] = []
    clean_query = (query or "").lower().strip()
    query_tokens = set(re.findall(r"\w+", clean_query))

    # Determine files to read
    if topic and (STANDARDS_DIR / f"{topic.lower()}.md").exists():
        files = [STANDARDS_DIR / f"{topic.lower()}.md"]
    else:
        files = sorted(STANDARDS_DIR.glob("*.md"))

    for filepath in files:
        file_topic = filepath.stem.lower()
        if topic and file_topic != topic.lower():
            continue

        content = filepath.read_text(encoding="utf-8")

        # Split into standard blocks by "### MGSE"
        sections = re.split(r"(?=###\s+MGSE)", content)
        for sec in sections:
            if not sec.strip().startswith("###"):
                continue

            lines = sec.strip().splitlines()
            header = lines[0].replace("###", "").strip()
            body_lines = [l.strip() for l in lines[1:] if l.strip()]

            # Extract standard code e.g. MGSE5.NF.1
            code_match = re.search(r"(MGSE\d\.[A-Z0-9\.]+)", header)
            code = code_match.group(1) if code_match else header

            # Extract grade from header e.g. MGSE5.NF.1 -> grade 5
            extracted_grade = None
            grade_match = re.search(r"MGSE(\d)", header)
            if grade_match:
                extracted_grade = int(grade_match.group(1))

            if grade and extracted_grade and grade != extracted_grade:
                continue

            # Extract summary
            summary = ""
            desc_lines = []
            for line in body_lines:
                if line.startswith("- Summary:"):
                    summary = line.replace("- Summary:", "").strip()
                elif not line.startswith("-"):
                    desc_lines.append(line)

            description = " ".join(desc_lines).strip()
            if not summary:
                summary = description or header

            sec_tokens = set(re.findall(r"\w+", sec.lower()))
            overlap = len(query_tokens & sec_tokens) if query_tokens else 1

            # Boost if query explicitly mentioned standard code or topic
            if any(token in header.lower() for token in query_tokens):
                overlap += 10
            if topic and topic.lower() in file_topic:
                overlap += 5
            if grade and extracted_grade == grade:
                overlap += 3

            results.append({
                "code": code,
                "standard_code": code,
                "topic": file_topic,
                "grade": extracted_grade or grade or 5,
                "title": f"Grade {extracted_grade or grade or 5} {file_topic.capitalize()} ({code})",
                "description": description,
                "summary": summary,
                "content": f"{code}: {summary}",
                "score": float(overlap),
                "source": "local_standards_fallback",
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def retrieve_standards(
    query: str = "",
    topic: str | None = None,
    grade: int | None = None,
    limit: int = 2,
) -> list[dict[str, Any]]:
    """Retrieve top relevant MGSE standards via Supabase pgvector, with automatic local fallback."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if os.getenv("TESTING") == "true":
        return _search_local_standards(query=query, topic=topic, grade=grade, limit=limit)

    if supabase_url and supabase_key:
        try:
            from supabase import ClientOptions, create_client
            client_options = ClientOptions(postgrest_client_timeout=2.0)
            supabase = create_client(supabase_url, supabase_key, options=client_options)

            # Try semantic pgvector search if query and Gemini key are present
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            search_query = query.strip() or f"{topic or ''} Grade {grade or ''}".strip()
            if search_query and gemini_api_key:
                try:
                    from google import genai
                    from google.genai import types

                    embed_model = os.getenv("GEMINI_EMBED_MODEL")
                    if not embed_model:
                        logger.warning("GEMINI_EMBED_MODEL not set; using local markdown standards fallback.")
                        return _search_local_standards(query=search_query, topic=topic, grade=grade, limit=limit)

                    client = genai.Client(
                        api_key=gemini_api_key,
                        http_options=types.HttpOptions(timeout=2.0),
                    )
                    embed_res = client.models.embed_content(
                        model=embed_model,
                        contents=search_query,
                        config=types.EmbedContentConfig(output_dimensionality=768),
                    )
                    if hasattr(embed_res, "embeddings") and embed_res.embeddings:
                        vec = list(embed_res.embeddings[0].values)
                        rpc_res = supabase.rpc(
                            "match_standards",
                            {
                                "query_embedding": vec,
                                "match_count": limit,
                                "filter_topic": topic.lower() if topic else None,
                                "filter_grade": grade,
                            },
                        ).execute()

                        if rpc_res.data:
                            return [
                                {
                                    "code": row.get("code", "MGSE"),
                                    "standard_code": row.get("code", "MGSE"),
                                    "topic": row.get("topic", topic or "general"),
                                    "grade": row.get("grade", grade or 5),
                                    "title": row.get("title", f"MGSE Standard {row.get('code')}"),
                                    "description": row.get("description", ""),
                                    "summary": row.get("summary", row.get("description", "")),
                                    "content": f"{row.get('code')}: {row.get('summary') or row.get('description')}",
                                    "score": float(row.get("similarity", 0.95)),
                                    "source": "supabase_pgvector",
                                }
                                for row in rpc_res.data
                            ]
                except Exception as rpc_exc:
                    logger.debug("pgvector RPC match_standards skipped or failed: %s", rpc_exc)

            # Fallback to standard Supabase table query if RPC was unavailable
            query_builder = supabase.table("standards").select("*")
            if topic:
                query_builder = query_builder.eq("topic", topic.lower())
            if grade:
                query_builder = query_builder.eq("grade", grade)
            if query.strip():
                query_builder = query_builder.ilike("description", f"%{query}%")

            table_res = query_builder.limit(limit).execute()
            if table_res.data:
                return [
                    {
                        "code": row.get("code", "MGSE"),
                        "standard_code": row.get("code", "MGSE"),
                        "topic": row.get("topic", topic or "general"),
                        "grade": row.get("grade", grade or 5),
                        "title": row.get("title", f"MGSE Standard {row.get('code')}"),
                        "description": row.get("description", ""),
                        "summary": row.get("summary", row.get("description", "")),
                        "content": f"{row.get('code')}: {row.get('summary') or row.get('description')}",
                        "score": 10.0,
                        "source": "supabase_table",
                    }
                    for row in table_res.data
                ]
        except Exception as exc:
            logger.warning("Supabase lookup failed (%s). Falling back to data/standards/*.md.", exc)

    logger.debug("Using local standards keyword matching fallback for query: '%s', topic: '%s', grade: %s", query, topic, grade)
    return _search_local_standards(query=query, topic=topic, grade=grade, limit=limit)


def format_standards_for_prompt(standards: list[dict[str, Any]]) -> str:
    """Format retrieved standards into clean instructions for LLM prompts."""
    if not standards:
        return "Georgia Standards of Excellence (MGSE): General Grade 5/6 math competency."

    lines: list[str] = []
    for s in standards:
        code = s.get("standard_code") or s.get("code") or "MGSE"
        summary = s.get("summary") or s.get("content") or s.get("description", "")
        lines.append(f"- {code}: {summary}")
    return "\n".join(lines)
