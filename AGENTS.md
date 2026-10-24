# AGENTS.md — MathQuest Multi-Curriculum Platform Rules

## 1. Project Overview & Role
- **Project**: MathQuest — Gamified, curriculum-aware math learning platform for Grades 5 and 6.
- **Submissions & Audience**: Submission for "Developer Assessment, Task 1" and foundation of a production product for client handoff.
- **Curricula Supported**:
  1. **Primary**: Georgia Standards of Excellence (MGSE), Grades 5 & 6.
  2. **Secondary**: CBSE Class 6 (*NCERT Ganita Prakash*).
- **Core Extensibility**: Expanding boards requires adding data files (`backend/data/packs/<board>-g<grade>.json` and standards markdown), **never** changing application code.

---

## 2. Core Architectural Principle
> *"The LLM writes, code verifies, the engine adapts."*
- Every LLM output is strictly untrusted. The LLM only proposes narrative scenarios, expressions, and claimed answers.
- Deterministic Python logic (`services/verify.py` and `services/misconceptions.py`) validates mathematical correctness, evaluates expressions using exact `fractions.Fraction` arithmetic, and generates curated diagnostic distractors.
- Never claim LLM output is guaranteed correct; empirical rates are systematically benchmarked and reported in `backend/eval/`.

---

## 3. Hard Constraints

1. **100% Free-Tier Services**: Zero paid APIs or card dependencies.
   - Stack: Frontend Nuxt 3 + TypeScript + Tailwind CSS + Pinia (`/frontend`).
   - Backend: FastAPI + Pydantic v2 (`/backend`).
   - LLM: Gemini API via official `google-genai` SDK.
   - Database/RAG: Supabase Postgres with `pgvector` (with local markdown fallback).
   - Deployment: Vercel (Frontend), Render (Backend).
2. **Environment Variable Enforced Models**:
   - Model names come **strictly** from environment variables: `GEMINI_MODEL`, `GEMINI_MODEL_ALT`, and `GEMINI_EMBED_MODEL`.
   - Never hardcode model names in code or prompts.
3. **Strict Secrets & Env Isolation**:
   - Backend env vars: `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_MODEL_ALT`, `GEMINI_EMBED_MODEL`, `SUPABASE_URL`, `SUPABASE_KEY`, `FRONTEND_URL`.
   - Frontend env vars: `NUXT_PUBLIC_API_BASE`.
   - `.env.example` files contain variable **names only** without default secrets or values.
   - Zero secrets in code or git history.
4. **Safety & Integrity**:
   - No `eval()` or `exec()` anywhere in the codebase.
   - Never transmit student personal data to the LLM (client progress is persisted in client `localStorage`).
   - Child-safe tone: grade-appropriate language, positive reinforcement, and safety prompts on every generation.
5. **Authentic Curriculum Content**:
   - Do not invent curriculum facts. Standard codes, chapter names, or topics that cannot be cross-verified must have `"verified": false` in the pack and be cataloged in `docs/UNVERIFIED_CONTENT.md`.
   - Never copy copyrighted textbook text verbatim (NCERT, publishers, GaDOE). Write original, short pedagogical summaries.

---

## 4. Phase-by-Phase Workflow

All implementation proceeds strictly phase-by-phase. At the conclusion of each phase:
1. Run all unit tests.
2. Start or build the application to verify behavior.
3. Output a concise report (what was built, what was tested, what is unverified).
4. **STOP** and await explicit user confirmation ("continue") before proceeding to the next phase.

- **Phase 0**: AGENTS.md, .gitignore, README placeholder, .env.example files, folder structure.
- **Phase 1**: schemas.py, verify.py, misconceptions.py + comprehensive tests.
- **Phase 2**: curriculum pack schema, loader, georgia-g5/g6 & cbse-g6 packs, UNVERIFIED_CONTENT.md.
- **Phase 3**: llm.py, question_builder, fallback bank, /api/questions, mocked LLM tests, Render deployment doc.
- **Phase 4**: adaptive.py, /api/answer, mastery & badge tests.
- **Phase 5**: Nuxt scaffold, board/grade/topic navigation, quiz & results flow, Vercel deployment doc.
- **Phase 6**: explain/script/infographic/RAG services, learn page, video player, SVG diagrams, hints.
- **Phase 7**: eval harness (run_eval.py), saved results, frontend eval page.
- **Phase 8**: rate limits, error handling, mobile responsiveness (375/768/1280), a11y, CI workflow.
- **Phase 9**: README, docs/INTERVIEW_NOTES.md, docs/ROADMAP.md, final audit (PASS/PARTIAL/FAIL).
