# MathQuest 🎮📐

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.15+-00DC82.svg?logo=nuxtdotjs&logoColor=white)](https://nuxt.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-06B6D4.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A gamified, curriculum-aware, adaptive math learning platform for **Grades 5 and 6**, designed for multi-board extensibility. Built as both a submission for **Developer Assessment Task 1** and a production-grade foundation for client handoff.

---

## 🌟 Core Principle

> **"The LLM writes, code verifies, the engine adapts."**

Large Language Models (LLMs) cannot be trusted as an authority on mathematical truth. In MathQuest:
- The LLM's role is restricted to proposing engaging narrative contexts, word problems, and LaTeX expressions.
- **Deterministic Python** validates mathematical correctness using an abstract syntax tree (AST) parser and exact rational arithmetic (`fractions.Fraction`).
- Zero `eval()` or `exec()` anywhere in the codebase.
- Distractors are not random numbers; each distractor is diagnostically crafted to diagnose a specific cognitive misconception.
- Real verification, hallucination, and repair rates are systematically measured and reported.

---

## 🏛️ Supported Curricula

MathQuest ships with full curriculum packs for two distinct educational systems:

### 1. Georgia Standards of Excellence (MGSE) — Grades 5 & 6
- **Grade 5**:
  - `fractions` (`MGSE5.NF.1`, `MGSE5.NF.2`, `MGSE5.NF.4`, `MGSE5.NF.7`): Adding, subtracting, and multiplying fractions with unlike denominators; fraction division word problems.
  - `decimals` (`MGSE5.NBT.7`): Add, subtract, multiply, and divide decimals to hundredths.
  - `geometry` (`MGSE5.G.1`, `MGSE5.G.2`): Coordinate graphing, 2D shape attributes, perimeter and area.
- **Grade 6**:
  - `ratios` (`MGSE6.RP.1`, `MGSE6.RP.2`, `MGSE6.RP.3`): Unit rates, ratio tables, percentage problems.
  - `fractions` (`MGSE6.NS.1`): Interpreting and computing quotients of fractions.
  - `geometry` (`MGSE6.G.1`): Area of right triangles, other triangles, special quadrilaterals, polygons.

### 2. CBSE Class 6 (*NCERT Ganita Prakash*)
- `factors_multiples` (`NCERT-6-MAT-CH05`): Prime vs composite numbers, tests of divisibility, prime factorisation, HCF, LCM.
- `fractions` (`NCERT-6-MAT-CH07`): Proper, improper, mixed fractions, fraction equivalence, addition/subtraction.
- `decimals` (`NCERT-6-MAT-CH08`): Tenths and hundredths place value, decimal money and metric measurement problems.
- `integers` (`NCERT-6-MAT-CH06`): Positive and negative integers, representation on number line, ordering and arithmetic.
- `ratios` (`NCERT-6-MAT-CH12`): Ratio concepts, proportions, and unitary method.
- `geometry` (`NCERT-6-MAT-CH10`): Perimeter of regular polygons, area of rectangles and composite figures.

### 🚀 Extensibility: Adding a New Board in 3 Steps (Zero Code Changes)
To add a new state or national curriculum (e.g., Texas TEKS, UK National Curriculum):
1. Create a JSON pack at `backend/data/packs/<board>-g<grade>.json` following the schema in `backend/app/schemas.py`.
2. Add pedagogical standards markdown summaries in `backend/data/standards/<board>/`.
3. Done! The backend auto-loads the pack, and the frontend dynamically renders the board tabs, grades, and topic cards.

---

## 🛠️ Technology Stack & Zero-Cost Architecture

Every service runs on **100% free-tier services** without requiring paid subscriptions or credit card holds:

- **Frontend (`/frontend`)**: [Nuxt 3](https://nuxt.com), [Vue 3](https://vuejs.org), [Pinia](https://pinia.vuejs.org), [Tailwind CSS](https://tailwindcss.com). Deployed on [Vercel](https://vercel.com).
- **Backend (`/backend`)**: [FastAPI](https://fastapi.tiangolo.com), [Pydantic v2](https://docs.pydantic.dev), [SlowAPI](https://github.com/laurentS/slowapi) rate limiting. Deployed on [Render](https://render.com).
- **LLM Engine**: Google Gemini via the official `google-genai` SDK. Model names are **strictly enforced via environment variables** (`GEMINI_MODEL`, `GEMINI_MODEL_ALT`, `GEMINI_EMBED_MODEL`).
- **Database & RAG**: [Supabase](https://supabase.com) PostgreSQL with `pgvector` for semantic standards retrieval, backed by an **automatic local markdown file fallback** if Supabase is offline or unconfigured.
- **Offline Fallback Bank**: 60 pre-verified, deterministic questions in `backend/data/fallback_bank.json` guaranteeing 100% platform availability if LLM quotas are exhausted.

---

## 📐 Safe Math Engine & Misconception Taxonomy

### 1. Deterministic AST Rational Evaluator (`services/verify.py`)
- Zero reliance on `eval()` or `exec()`.
- Converts all expressions to exact `fractions.Fraction` objects (no IEEE 754 floating-point errors).
- Recursively parses operators: `+`, `-`, `*`, `/`, `^`, parentheses, and mixed numbers ($2\frac{3}{4}$).
- Arithmetic geometry and number theory helpers (`is_prime`, `get_factors`, `gcd`, `lcm`, `coprime`).

### 2. Diagnostic Distractors (`services/misconceptions.py`)
Every multiple-choice option targets a real mathematical misconception:
- **Added Denominators**: $\frac{1}{3} + \frac{1}{4} = \frac{2}{7}$.
- **Inverted Dividend**: $\frac{2}{3} \div \frac{4}{5} = \frac{3}{2} \times \frac{4}{5}$.
- **Ignored Place Value**: $0.4 + 0.05 = 0.90$.
- **Perimeter vs. Area**: Reporting $2(l+w)$ when asked for $l \times w$.
- **Factors vs. Multiples**: Confusing factors of 12 with multiples of 12.

When a student selects an incorrect distractor, the adaptive engine (`services/adaptive.py`) delivers instant, targeted diagnostic feedback explaining the exact cognitive mistake.

---

## 🏆 Gamification & Adaptive Engine

- **Adaptive Tiers**:
  - `easy` (Warmup): Single-step, friendly whole numbers and simple fractions.
  - `medium` (Core): Standard curriculum grade-level word problems.
  - `hard` (Challenge): Multi-step problems with mixed operations.
  - *Tier Promotion*: 2 consecutive correct answers promote to the next tier.
  - *Tier Demotion*: 1 incorrect answer steps down to reinforce fundamentals.
- **Mastery Scoring**: Dynamically tracked from 0% to 100% per topic.
- **Hint Ladder**: 3-tier Socratic hint system (Conceptual hint $\to$ Strategic hint $\to$ Step-by-step formula hint).
- **Trophy Shelf**: 10 curriculum-aligned unlockable badges persisted in client `localStorage`:
  - `First Quest`: Answer your first question correctly.
  - `Fraction Wizard`: Master fractions.
  - `Decimal Dynamo`: Master decimals.
  - `Ratio Ranger`: Master ratios.
  - `Geometry Giant`: Master geometry.
  - `CBSE Champion`: Complete a CBSE topic.
  - `Streak Master`: Achieve a 5-in-a-row correct streak.
  - `Perfect Score`: Complete a quiz session with 100% accuracy.
  - `Speedy Solver`: Solve a problem in under 10 seconds.
  - `Tenacious Thinker`: Promote from Easy to Hard in a single session.

---

## ♿ Accessibility & Child Safety (a11y)

- **Dyslexia-Friendly Mode**: Toggle switch (`Aa` button) enabling the [Lexend](https://fonts.google.com/specimen/Lexend) font family, designed specifically to reduce visual stress for young readers.
- **Read-Aloud Narration**: Web Speech API (`window.speechSynthesis`) integration for question narration.
- **Keyboard Navigation**: Fully accessible tab stops with high-contrast `:focus-visible` outline rings.
- **Child-Safe Language**: Positive reinforcement, encouragement prompts, zero PII collection, and zero student data transmitted to external LLMs.

---

## 📊 Benchmarking & Empirical Verification (`/eval`)

We benchmarked real LLM output validity across topics, grades, and models using `backend/eval/run_eval.py`:

```bash
# Run benchmark with 40 questions across all boards and topics
backend/.venv/Scripts/python.exe backend/eval/run_eval.py -N 10 --mock
```

- Empirical evaluation metrics are displayed interactively on the frontend `/eval` route.
- Tracks: Total Questions, Initial Correctness %, Repair Rate %, Final Verified %, Fallback Engagement %, and Average Latency.

---

## 🚀 Quick Start & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### 1. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and supply GEMINI_API_KEY, GEMINI_MODEL, etc.

# Run tests
pytest -v

# Start development server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# NUXT_PUBLIC_API_BASE=http://localhost:8000

# Start Nuxt 3 dev server
npm run dev
# App will be available at http://localhost:3000
```

---

## 🚢 Deployment Documentation

- [Render Backend Deployment Guide](docs/RENDER_DEPLOYMENT.md): Complete setup for FastAPI on Render free tier, health checks, and environment configurations.
- [Vercel Frontend Deployment Guide](docs/VERCEL_DEPLOYMENT.md): Nuxt 3 serverless and static edge deployment instructions.
- [Curriculum Verification Audit](docs/UNVERIFIED_CONTENT.md): Cross-referenced standard codes and official GaDOE / NCERT source mappings.
- [Engineering Interview Notes](docs/INTERVIEW_NOTES.md): Deep dive into architectural decisions, threat models, and technical trade-offs.
- [Product & Technical Roadmap](docs/ROADMAP.md): Post-assessment vision, Grade 7–8 expansion, LMS integration, and teacher analytics.

---

## 🗺️ Completed Implementation Roadmap

- [x] **Phase 0**: Project rules, `.gitignore`, `.env.example` templates, `README.md`, folder scaffolding.
- [x] **Phase 1**: Core schemas, `verify.py` safe parser & rational arithmetic, `misconceptions.py` generator, 130 tests.
- [x] **Phase 2**: Curriculum pack schema, loader, Georgia G5/G6 & CBSE G6 packs, `docs/UNVERIFIED_CONTENT.md`.
- [x] **Phase 3**: `llm.py`, `question_builder.py`, `fallback_bank.json`, `/api/questions`, Render deployment guide.
- [x] **Phase 4**: `adaptive.py`, `/api/answer` progression engine, mastery scoring & 10 trophy badges.
- [x] **Phase 5**: Nuxt 3 multi-board scaffold, board/grade/topic navigation, quiz & results flow, Vercel guide.
- [x] **Phase 6**: Explanations, video lesson scripts, infographics, RAG standards retrieval, Web Speech narration, SVG diagrams, hint ladder.
- [x] **Phase 7**: Evaluation benchmark harness (`run_eval.py`), comparative metrics, `/eval` interactive dashboard.
- [x] **Phase 8**: Production hardening (slowapi rate limiting, error handlers, a11y, mobile responsiveness, CI workflow).
- [x] **Phase 9**: Final documentation (`INTERVIEW_NOTES.md`, `ROADMAP.md`), comprehensive audit (PASS/PARTIAL/FAIL).

---

## 📄 License

MIT License. Designed and engineered for the MathQuest developer assessment and client delivery.
