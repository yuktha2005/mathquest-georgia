"""Ingestion script for Georgia Standards of Excellence (MGSE).

Parses data/standards/*.md files, generates semantic embeddings via the official
google-genai SDK (text-embedding-004, 768 dimensions), and upserts them
into Supabase Postgres with pgvector.

Usage:
    python scripts/ingest_standards.py
    python scripts/ingest_standards.py --dry-run
    python scripts/ingest_standards.py --export-json data/standards_embedded.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_standards")

# Base directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
STANDARDS_DIR = BACKEND_DIR / "data" / "standards"

# Load backend/.env if available
load_dotenv(dotenv_path=BACKEND_DIR / ".env")


def parse_standards_markdown(directory: Path = STANDARDS_DIR) -> list[dict]:
    """Parse all markdown files in data/standards/ into structured standard dictionaries."""
    standards: list[dict] = []

    if not directory.exists():
        logger.error("Standards directory not found at: %s", directory)
        return standards

    for md_file in sorted(directory.glob("*.md")):
        topic = md_file.stem.lower()
        content = md_file.read_text(encoding="utf-8")

        # Split on standard headers: "### MGSE"
        sections = re.split(r"(?=###\s+MGSE)", content)
        for section in sections:
            section = section.strip()
            if not section.startswith("###"):
                continue

            lines = section.splitlines()
            code_line = lines[0].replace("###", "").strip()

            # Parse standard code (e.g., MGSE5.NF.1)
            code_match = re.search(r"(MGSE\d\.[A-Z0-9\.]+)", code_line)
            if not code_match:
                continue
            code = code_match.group(1)

            # Extract grade from code e.g. MGSE5 -> 5, MGSE6 -> 6
            grade_match = re.search(r"MGSE(\d)", code)
            grade = int(grade_match.group(1)) if grade_match else 5

            # Extract summary, key concepts, and description
            description_lines = []
            summary = ""
            key_concepts: list[str] = []

            for line in lines[1:]:
                clean_line = line.strip()
                if not clean_line:
                    continue
                if clean_line.startswith("- Summary:"):
                    summary = clean_line.replace("- Summary:", "").strip()
                elif clean_line.startswith("- Key concepts:"):
                    raw_concepts = clean_line.replace("- Key concepts:", "").strip()
                    key_concepts = [c.strip() for c in raw_concepts.split(",") if c.strip()]
                elif not clean_line.startswith("- Formula/Rule:"):
                    description_lines.append(clean_line)

            description = " ".join(description_lines).strip()
            if not summary:
                summary = description

            standards.append({
                "code": code,
                "topic": topic,
                "grade": grade,
                "title": f"Grade {grade} {topic.capitalize()} - {code}",
                "description": description,
                "summary": summary,
                "key_concepts": key_concepts,
            })

    logger.info("Parsed %d standards across %s", len(standards), [f.stem for f in directory.glob("*.md")])
    return standards


def generate_embedding(text: str, api_key: str | None = None) -> list[float]:
    """Generate 768-dimensional embedding using google-genai text-embedding-004."""
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required to generate embeddings.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768),
    )
    # The SDK returns response.embeddings as a list of ContentEmbedding objects
    if hasattr(response, "embeddings") and response.embeddings:
        return list(response.embeddings[0].values)
    raise RuntimeError(f"Failed to generate embedding: empty response from Gemini API")


def ingest_standards(dry_run: bool = False, export_path: Path | None = None) -> int:
    """Run full ingestion pipeline."""
    standards = parse_standards_markdown()
    if not standards:
        logger.warning("No standards found to ingest.")
        return 0

    gemini_key = os.getenv("GEMINI_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    embedded_standards: list[dict] = []

    for item in standards:
        embed_input = f"{item['code']} Grade {item['grade']} {item['topic']}: {item['description']} Summary: {item['summary']} Concepts: {', '.join(item['key_concepts'])}"
        if dry_run or not gemini_key:
            logger.info("[Dry Run] Would embed %s: '%s...'", item["code"], embed_input[:60])
            item["embedding"] = [0.0] * 768
        else:
            logger.info("Generating embedding for %s...", item["code"])
            try:
                vec = generate_embedding(embed_input, api_key=gemini_key)
                item["embedding"] = vec
                logger.info("Generated %d-dim vector for %s", len(vec), item["code"])
            except Exception as exc:
                logger.error("Embedding generation failed for %s: %s", item["code"], exc)
                item["embedding"] = None

        embedded_standards.append(item)

    # Optional local JSON export
    if export_path:
        export_path.parent.mkdir(parents=True, exist_ok=True)
        # Exclude massive vectors if requested, or keep for vector replay
        export_data = [
            {k: v for k, v in item.items() if k != "embedding"}
            for item in embedded_standards
        ]
        export_path.write_text(json.dumps(export_data, indent=2), encoding="utf-8")
        logger.info("Exported standards metadata to %s", export_path)

    if dry_run:
        logger.info("Dry run finished. Ingestion to Supabase skipped.")
        return len(embedded_standards)

    if not supabase_url or not supabase_key:
        logger.warning(
            "SUPABASE_URL and/or SUPABASE_KEY not set. Standards were parsed successfully, "
            "but database upsert was skipped. Local RAG fallback will be used at runtime."
        )
        return len(embedded_standards)

    # Upsert to Supabase
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)

        records_to_upsert = [
            {
                "code": item["code"],
                "topic": item["topic"],
                "grade": item["grade"],
                "title": item["title"],
                "description": item["description"],
                "summary": item["summary"],
                "key_concepts": item["key_concepts"],
                "embedding": item["embedding"],
            }
            for item in embedded_standards
            if item.get("embedding") and any(item["embedding"])
        ]

        if records_to_upsert:
            logger.info("Upserting %d records into Supabase 'standards' table...", len(records_to_upsert))
            res = supabase.table("standards").upsert(records_to_upsert, on_conflict="code").execute()
            logger.info("Successfully upserted standards to Supabase: %s", len(res.data) if res.data else "OK")
    except Exception as exc:
        logger.error("Failed to upsert to Supabase: %s", exc)
        return 0

    return len(embedded_standards)


def main():
    parser = argparse.ArgumentParser(description="Ingest Georgia Standards of Excellence into Supabase pgvector.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and log without calling external APIs or DB")
    parser.add_argument("--export-json", type=str, default="", help="Optional path to export parsed standards JSON")
    args = parser.parse_args()

    export_path = Path(args.export_json) if args.export_json else None
    count = ingest_standards(dry_run=args.dry_run, export_path=export_path)
    logger.info("Ingestion completed with %d standards processed.", count)


if __name__ == "__main__":
    main()
