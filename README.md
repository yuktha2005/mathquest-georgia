# MathQuest 🎮📐

A gamified, curriculum-aware math learning platform for **Grades 5 and 6**, designed for multi-board extensibility.

---

## 🌟 Core Principle

> **"The LLM writes, code verifies, the engine adapts."**

Treat every LLM output as untrusted. The LLM proposes narrative word problems and claimed answers. Deterministic Python verifies mathematical expressions using exact rational arithmetic (`fractions.Fraction`) and generates diagnostic distractors with curated misconceptions. We measure and report real verification rates rather than claiming guaranteed outputs.

---

## 🏛️ Supported Curricula

MathQuest is architected around **Curriculum Packs** (`backend/data/packs/<board>-g<grade>.json`):
1. **Georgia Standards of Excellence (MGSE)**: Grade 5 & Grade 6 (Fractions, Decimals, Ratios, Geometry).
2. **CBSE Class 6 (*NCERT Ganita Prakash*)**: Fractions, Perimeter & Area, Lines & Angles / Symmetry, Prime Time (Factors & Multiples), Number Play.
3. **Pluggable Architecture**: Adding new state or national boards requires adding data JSON files and standard markdown summaries—**never** changing core application code.

---

## 🛠️ Technology Stack

- **Frontend (`/frontend`)**: Nuxt 3, TypeScript, Tailwind CSS, Pinia
- **Backend (`/backend`)**: FastAPI, Pydantic v2
- **LLM Engine**: Gemini via official `google-genai` SDK (Model names injected via environment variables)
- **Database & RAG**: Supabase Postgres with `pgvector` (with automatic local markdown fallback)
- **Deployment**: Vercel (Frontend), Render (Backend)

---

## 🔐 Environment Variables

Environment variables are isolated and never checked into source control. Template `.env.example` files contain names only:

### Backend (`/backend/.env.example`)
```env
GEMINI_API_KEY=
GEMINI_MODEL=
GEMINI_MODEL_ALT=
GEMINI_EMBED_MODEL=
SUPABASE_URL=
SUPABASE_KEY=
FRONTEND_URL=
```

### Frontend (`/frontend/.env.example`)
```env
NUXT_PUBLIC_API_BASE=
```

---

## 🗺️ Implementation Roadmap

- [x] **Phase 0**: Project rules, `.gitignore`, `.env.example` templates, `README.md`, folder structure.
- [x] **Phase 1**: Core schemas, `verify.py` safe parser & arithmetic, `misconceptions.py` generator + test suite.
- [x] **Phase 2**: Curriculum pack schema, loader, Georgia G5/G6 & CBSE G6 packs, `docs/UNVERIFIED_CONTENT.md`.
- [x] **Phase 3**: `llm.py`, `question_builder.py`, `fallback_bank.json`, `/api/questions`, Render deployment instructions.
- [x] **Phase 4**: `adaptive.py`, `/api/answer` progression engine, mastery & badge tests.
- [x] **Phase 5**: Nuxt 3 multi-board scaffold, board/grade/topic navigation, quiz & results flow, Vercel deployment guide.
- [x] **Phase 6**: Explanations, video scripts, infographics, RAG retrieval, Web Speech narration, SVG diagrams, hint ladder.
- [x] **Phase 7**: Evaluation benchmark harness (`run_eval.py`), comparative metrics, `/eval` dashboard.
- [x] **Phase 8**: Production hardening (slowapi rate limiting, error handlers, a11y, mobile responsiveness, CI workflow).
- [ ] **Phase 9**: Final documentation (`INTERVIEW_NOTES.md`, `ROADMAP.md`), comprehensive audit (PASS/PARTIAL/FAIL).
