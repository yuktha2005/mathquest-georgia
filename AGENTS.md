# AGENTS.md — MathQuest Georgia Development Rules

## 1. Project Overview
- **Project**: MathQuest Georgia
- **Target Audience**: Grade 5 and Grade 6 students
- **Curriculum Alignment**: Georgia Standards of Excellence (MGSE)
- **Concept**: A gamified math learning platform designed to make math engaging, adaptive, and safe for young learners.

---

## 2. Technology Stack
- **Frontend** (`/frontend`): Nuxt 3, TypeScript, Tailwind CSS, Pinia
- **Backend** (`/backend`): FastAPI, Pydantic v2
- **Database**: Supabase Postgres with `pgvector`
- **LLM Engine**: Gemini API via the official `google-genai` SDK

---

## 3. Core Project Rules

1. **Never trust LLM math**: Every single generated question and mathematical calculation must be verified by `services/verify.py` before reaching the user.
2. **Strict schema validation & retry limit**: All LLM outputs must be validated using Pydantic models. A maximum of 2 repair retries is permitted; if validation fails after 2 retries, fall back immediately to `data/fallback_bank.json`.
3. **Deterministic distractors**: Multiple-choice distractors must always be generated in code using a curated misconception library—never generated hallucinated distractors from the LLM.
4. **Zero secrets in code**: Never hardcode secrets, API keys, or database credentials. Rely strictly on environment variables:
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `FRONTEND_URL`
5. **Mandatory test coverage**: Write comprehensive `pytest` unit tests for question verification (`services/verify.py`) and adaptive learning logic.
6. **Code quality & architecture**: Keep code simple, strictly typed, and thoroughly commented. Prefer modular, single-responsibility small files.
7. **Child safety & tone**: Strictly enforce grade-appropriate, encouraging, and child-safe language across all prompts, feedback, and user interfaces.
8. **Summary on completion**: After finishing any task, provide a concise summary of what was built and detailed instructions on how to run and test it.
