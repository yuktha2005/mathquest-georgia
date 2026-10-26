# MathQuest 🎮📐

[![Live Demo](https://img.shields.io/badge/Live_Demo-mathquest--georgia.vercel.app-6366F1?style=for-the-badge&logo=vercel&logoColor=white)](https://mathquest-georgia.vercel.app/signup)
[![GitHub Repository](https://img.shields.io/badge/GitHub_Repo-yuktha2005%2Fmathquest--georgia-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yuktha2005/mathquest-georgia)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.15+-00DC82.svg?logo=nuxtdotjs&logoColor=white)](https://nuxt.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-06B6D4.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

A gamified, curriculum-aware, adaptive math learning platform for **Grades 5 and 6**, engineered for multi-board extensibility. Built as a submission for **Developer Assessment Task 1** and a production-grade foundation for classroom learning.

---

## 👤 Candidate Details

- **Full Name**: Yuktha S
- **Register Number**: `921023243027`
- **College Name & Department**: Nadar Saraswathi College of Engineering and Technology / AI&DS
- **Year of Study / Expected Graduation**: Final Year (2023–2027)
- **Mobile Number**: `6369771791`
- **Email Address**: `yukthaa2005@gmail.com`
- **Task Chosen**: Task 1 - Gamified Math Learning Platform for Grades 5 and 6
- **Live Demo URL**: [https://mathquest-georgia.vercel.app/signup](https://mathquest-georgia.vercel.app/signup)
- **GitHub Repository**: [https://github.com/yuktha2005/mathquest-georgia](https://github.com/yuktha2005/mathquest-georgia)

---

## 🌟 Core Architectural Principle

> **"The LLM writes, code verifies, the engine adapts."**

Large Language Models (LLMs) cannot be treated as an authority on mathematical truth. In MathQuest:
- The LLM's role is strictly restricted to proposing engaging narrative scenarios, word problems, and LaTeX expressions.
- **Deterministic Python** validates mathematical correctness using an abstract syntax tree (AST) parser and exact rational arithmetic (`fractions.Fraction`).
- Zero `eval()` or `exec()` anywhere in the codebase.
- Distractors are not random offsets; each distractor diagnostically pinpoints a documented cognitive misconception.
- Real verification, hallucination, and repair rates are systematically measured and reported on an interactive `/eval` dashboard.

---

## 🏛️ Supported Curricula & Multi-Board Extensibility

MathQuest ships with pre-configured curriculum packs for two major educational systems:

### 1. Georgia Standards of Excellence (MGSE) — Grades 5 & 6
- **Grade 5**:
  - `fractions` (`MGSE5.NF.1`, `MGSE5.NF.2`, `MGSE5.NF.4`, `MGSE5.NF.7`): Unlike denominator addition/subtraction, mixed numbers, fraction division word problems.
  - `decimals` (`MGSE5.NBT.7`): Decimal computation to hundredths using place value strategies.
  - `ratios` (`MGSE5.NF.5`): Multiplication as scaling and coordinate pattern relationships.
  - `geometry` (`MGSE5.MD.5`, `MGSE5.G.1`): 2D shape attributes, coordinate grids, area, and perimeter.
- **Grade 6**:
  - `fractions` (`MGSE6.NS.1`): Interpreting and computing quotients of fractions.
  - `decimals` (`MGSE6.NS.3`): Multi-digit decimal operations with standard algorithms.
  - `ratios` (`MGSE6.RP.1`, `MGSE6.RP.2`, `MGSE6.RP.3`): Unit rates, ratio tables, and percentage problems.
  - `geometry` (`MGSE6.G.1`): Decomposing polygons, area of triangles and special quadrilaterals.

### 2. CBSE Class 6 (*NCERT Ganita Prakash*)
- `factors_multiples` (`CBSE6.MATH.03`): Prime vs composite, divisibility rules, HCF, and LCM.
- `fractions` (`CBSE6.MATH.07`): Proper, improper, mixed fractions, equivalence, and arithmetic.
- `decimals` (`CBSE6.MATH.08`): Tenths, hundredths, place value, and practical metric units.
- `integers` (`CBSE6.MATH.06`): Number line representation, ordering, and directed arithmetic.
- `ratios` (`CBSE6.MATH.12`): Ratio concepts, proportions, and the unitary method.
- `geometry` (`CBSE6.MATH.10`): Perimeter of regular polygons, area of rectangles and composite figures.

### 🚀 Zero-Code Expansion
Adding any new curriculum (e.g. Texas TEKS, California CCSS, UK National Curriculum):
1. Add a JSON pack file at `backend/data/packs/<board>-g<grade>.json`.
2. Add pedagogical standard markdown files in `backend/data/standards/<board>/`.
3. The platform automatically renders the new board, grades, and topic cards dynamically with zero code modifications.

---

## 🛠️ Technologies & Frameworks Used

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend Framework** | [Nuxt 3](https://nuxt.com) (v3.21+) & [Vue 3](https://vuejs.org) | Modern full-stack SSR/SPA framework with file-based routing |
| **Language (Frontend)** | [TypeScript 5](https://www.typescriptlang.org) | End-to-end type safety for props, emits, and API payloads |
| **Styling** | [Tailwind CSS 3](https://tailwindcss.com) | Responsive utility styling, custom warm-neutral gamified themes |
| **State Management** | [Pinia](https://pinia.vuejs.org) | Centralized reactive stores for auth, sessions, streaks, and progress |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com) (v0.115+) | High-performance Python async web framework with automatic OpenAPI docs |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev) | Strict schema validation, mathematical model serialization |
| **Safe Math Parser** | Python `ast` + `fractions.Fraction` | Deterministic rational math evaluator (zero floating-point inaccuracies) |
| **Rate Limiting** | [SlowAPI](https://github.com/laurentS/slowapi) | Tiered client request throttling (e.g., 20 questions/min per IP) |
| **Database & Cloud Auth**| [Supabase](https://supabase.com) (PostgreSQL) | Auth (email/password), Row-Level Security (RLS), `pgvector` standards |
| **Hosting (Frontend)** | [Vercel](https://vercel.com) | Edge-network serverless deployment with instant previews |
| **Hosting (Backend)** | [Render](https://render.com) | Containerized FastAPI cloud service with automatic TLS/SSL |
| **Testing** | [Vitest](https://vitest.dev) & [Pytest](https://pytest.org) | Automated unit, store, integration, and security test suites |

---

## 🤖 AI Models, APIs, & Services Used

All services operate on **100% free-tier services** with zero paid API requirements:

1. **Google Gemini API (`google-genai` SDK)**:
   - **`GEMINI_MODEL` (`gemini-2.5-flash`)**: Primary model utilized for structured question generation, pedagogical lesson explanations, and narrative video scripts.
   - **`GEMINI_MODEL_ALT` (`gemini-2.5-pro`)**: Comparative alternate model for automated benchmark evaluations.
   - **`GEMINI_EMBED_MODEL` (`text-embedding-004`)**: Generates 768-dimensional embeddings for curriculum standards stored in Supabase pgvector for RAG retrieval.
2. **Supabase PostgreSQL & Auth**:
   - Cloud database storing student `profiles`, practice `sessions`, individual `answers`, topic `mastery`, and `badges`.
   - Client access enforced via PostgreSQL **Row-Level Security (RLS)** (`auth.uid() = user_id`).
3. **Web Speech API (`window.speechSynthesis`)**:
   - In-browser accessibility narration providing read-aloud support for early readers and dyslexic students without third-party audio API latency.
4. **Offline Curated Fallback Bank**:
   - `backend/data/fallback_bank.json` contains 60 pre-verified, deterministic questions across all grades and topics, ensuring complete platform availability during offline states or API quota exhaustion.

---

## 🔑 Required Environment Variables (No Secret Values)

### Backend Environment Variables (`backend/.env`)

| Variable Name | Required | Default / Example Value | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | *(Your Google AI Studio API Key)* | API key for Google Gemini model inference |
| `GEMINI_MODEL` | Yes | `gemini-2.5-flash` | Enforced primary Gemini model identifier |
| `GEMINI_MODEL_ALT` | No | `gemini-2.5-pro` | Alternate model for comparative benchmarking |
| `GEMINI_EMBED_MODEL` | Yes | `text-embedding-004` | Embedding model for standards retrieval |
| `FRONTEND_URL` | Yes | `https://mathquest-georgia.vercel.app,http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `SUPABASE_URL` | Optional | `https://<your-project>.supabase.co` | Supabase project URL (falls back to local storage if omitted) |
| `SUPABASE_KEY` | Optional | *(Your Supabase anon key)* | Supabase public anonymous API key |
| `PYTHON_VERSION` | Yes | `3.11.9` | Runtime Python version on Render cloud |
| `PORT` | No | `8000` | Server listening port (injected automatically on Render) |
| `EVAL_SAMPLE_SIZE` | No | `3` | Sample size for evaluation benchmark sweeps |

### Frontend Environment Variables (`frontend/.env`)

| Variable Name | Required | Default / Example Value | Description |
|---|---|---|---|
| `NUXT_PUBLIC_API_BASE` | Yes | `https://mathquest-georgia-backend.onrender.com` or `http://localhost:8000` | Target URL of the running FastAPI backend |
| `NUXT_PUBLIC_SUPABASE_URL` | Optional | `https://<your-project>.supabase.co` | Supabase project URL for cloud auth & sync |
| `NUXT_PUBLIC_SUPABASE_KEY` | Optional | *(Your Supabase anon key)* | Supabase public anonymous API key |

> [!NOTE]
> MathQuest is architected with complete offline resilience: if Supabase credentials are not provided, the platform automatically utilizes browser `localStorage` and local JSON curriculum packs without degradation of learning features.

---

## 📁 Repository & Folder Structure

```
mathquest-georgia/
├── candidate_details.txt        # Assessment candidate and submission metadata
├── README.md                   # Complete setup, architecture, and testing documentation
├── AGENTS.md                   # Multi-curriculum rules and architectural constraints
├── render.yaml                 # Render cloud blueprint deployment specification
├── .gitignore                  # Git ignore rules for node_modules, venvs, and caches
│
├── backend/                    # FastAPI Backend Service
│   ├── .env.example            # Backend environment template (names only, no secrets)
│   ├── requirements.txt        # Python dependency manifest (FastAPI, pydantic, google-genai)
│   ├── .python-version         # Python version lock (3.11.9)
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint, CORS, rate limits, and routers
│   │   ├── schemas.py          # Pydantic v2 domain schemas (Question, Answer, Mastery)
│   │   └── services/
│   │       ├── adaptive.py     # Progression engine (promotion, demotion, mastery calculation)
│   │       ├── curriculum.py   # Pack loader, topic validator, and syllabus registry
│   │       ├── explain.py      # Socratic step-by-step explanations and hint generator
│   │       ├── llm.py          # Official google-genai SDK wrapper and repair handler
│   │       ├── misconceptions.py# Cognitive distractor engine (diagnoses specific student errors)
│   │       ├── question_builder.py# Question generation pipeline with AST verification
│   │       ├── rag.py          # Standards retrieval (pgvector with local markdown fallback)
│   │       ├── script.py       # Narrative video lesson script synthesizer
│   │       └── verify.py       # Deterministic AST rational evaluator (fractions.Fraction)
│   ├── data/
│   │   ├── fallback_bank.json  # 60 pre-verified questions for offline/quota guarantee
│   │   ├── explanations_cache.json # High-performance cached pedagogical explanations
│   │   ├── scripts_cache.json  # Cached video lesson scripts
│   │   ├── standards_manifest.json # Structured curriculum standards mapping
│   │   ├── packs/              # Modular curriculum JSON packs
│   │   │   ├── georgia-g5.json # Georgia GSE Grade 5 curriculum pack
│   │   │   ├── georgia-g6.json # Georgia GSE Grade 6 curriculum pack
│   │   │   └── cbse-g6.json    # CBSE Class 6 NCERT Ganita Prakash curriculum pack
│   │   └── standards/          # Original pedagogical standard summaries (Markdown)
│   │       ├── georgia/        # MGSE standards (fractions, decimals, ratios, geometry)
│   │       └── cbse/           # CBSE standards (factors, integers, fractions, etc.)
│   ├── eval/                   # Empirical Evaluation Harness
│   │   ├── run_eval.py         # Benchmark runner (accuracy, repair rates, fallback rates)
│   │   ├── prompts/            # Ground-truth evaluation prompt templates
│   │   └── results/            # Saved evaluation benchmark JSON outputs
│   ├── migrations/             # Database migrations
│   │   └── 001_create_standards_pgvector.sql # pgvector schema for standards RAG
│   ├── scripts/
│   │   └── ingest_standards.py # CLI utility to embed & ingest standards into pgvector
│   └── tests/                  # 153 Comprehensive Backend Unit & Security Tests
│       ├── test_adaptive.py
│       ├── test_api_security_and_validation.py
│       ├── test_curriculum.py
│       ├── test_evaluation_benchmark.py
│       ├── test_explain_and_rag.py
│       ├── test_health_and_schemas.py
│       ├── test_misconceptions.py
│       ├── test_question_builder.py
│       ├── test_script.py
│       └── test_verify.py
│
├── frontend/                   # Nuxt 3 / Vue 3 Frontend Web Application
│   ├── .env.example            # Frontend environment template
│   ├── package.json            # Node.js dependencies and run scripts
│   ├── nuxt.config.ts          # Nuxt configuration, runtimeConfig, and meta tags
│   ├── tailwind.config.ts      # Gamified palette, animations, and typography tokens
│   ├── tsconfig.json           # TypeScript configuration
│   ├── vitest.config.ts        # Vitest test runner configuration
│   ├── app.vue                 # Nuxt root component
│   ├── error.vue               # Custom 404 & error recovery page
│   ├── assets/css/main.css     # Global CSS rules, typography imports, and dyslexia styles
│   ├── components/             # Reusable UI Components
│   │   ├── Card.vue            # Interactive card container with hover transitions
│   │   ├── FeedbackPanel.vue   # Diagnostic feedback display with procedure & hints
│   │   ├── HintLadder.vue      # 3-tier progressive hint ladder
│   │   ├── Infographic.vue     # Educational SVG data visualizations
│   │   ├── MockVideoPlayer.vue # Interactive video lesson player with speech playback
│   │   ├── NavBar.vue          # Top navigational toolbar with board & grade selectors
│   │   ├── ProgressCircle.vue  # SVG circular mastery ring indicator
│   │   ├── QuestionCard.vue    # Question presentation card with multiple choice options
│   │   ├── ShapeDiagram.vue    # Clean SVG geometry diagram generator
│   │   ├── StatsCard.vue       # Metrics summary card (XP, Streak, Accuracy)
│   │   └── XPBar.vue           # Dynamic level progression & XP progress bar
│   ├── composables/            # Nuxt Composables & Utilities
│   │   ├── useAccessibility.ts # Dyslexia font toggle and speech narration composable
│   │   ├── useApi.ts           # HTTP client with timeout handling & cold-start notice
│   │   ├── useAuth.ts          # Auth helper wrapping the Pinia auth store
│   │   ├── useProgressSync.ts  # Cloud-to-local sync and offline queue manager
│   │   └── useSupabase.ts      # Supabase client singleton provider
│   ├── layouts/
│   │   ├── default.vue         # Main layout with responsive header, nav, and footer
│   │   └── focus.vue           # Distraction-free quiz layout for practice sessions
│   ├── middleware/
│   │   └── auth.global.ts      # Global route protection, guest routing, and onboarding guard
│   ├── pages/                  # Application Routes
│   │   ├── index.vue           # Territory Map (board selector, grade toggle, topic cards)
│   │   ├── login.vue           # Sign-in page with demo account shortcuts & guest access
│   │   ├── signup.vue          # Account registration page
│   │   ├── onboarding.vue      # First-time profile setup (nickname, grade, board)
│   │   ├── forgot.vue          # Password recovery page
│   │   ├── dashboard.vue       # Student command center (XP, streak, daily goal, topics)
│   │   ├── quiz.vue            # 10-question adaptive quiz player with live feedback
│   │   ├── results.vue         # Post-quiz celebration, question review, and XP tally
│   │   ├── progress.vue        # Mastery breakdown, accuracy chart, and session history
│   │   ├── profile.vue         # Settings, board preference, and data management
│   │   ├── eval.vue            # Interactive benchmark metrics dashboard
│   │   ├── learn/[grade]/[topic].vue # Pedagogical lesson page, infographic, and video script
│   │   └── [...slug].vue       # Catch-all custom 404 page
│   ├── stores/                 # Pinia State Management
│   │   ├── auth.ts             # User profile, cloud session, and local storage account store
│   │   └── session.ts          # Quiz round state, current grade/board, and earned badges
│   └── tests/                  # 20 Automated Frontend Unit & Store Tests
│       ├── auth.store.spec.ts  # Pinia auth store tests
│       ├── middleware.spec.ts  # Route guard and deep-linking redirect tests
│       ├── session.spec.ts     # Quiz scoring and badge unlock tests
│       └── smoke.playwright.spec.ts # Playwright E2E smoke test suite
│
└── supabase/                   # Supabase Database Migrations
    └── migrations/
        └── 001_app_schema.sql  # Full schema: profiles, sessions, answers, mastery, badges & RLS
```

---

## 🚀 Setup & Execution Instructions

### Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/yuktha2005/mathquest-georgia.git
cd mathquest-georgia
```

#### 2. Backend Setup
```bash
cd backend

# Create and activate Python virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Open .env and insert your GEMINI_API_KEY and GEMINI_MODEL=gemini-2.5-flash

# Run the backend test suite (153 tests)
pytest

# Launch the FastAPI development server
uvicorn app.main:app --reload --port 8000
```
*Backend Swagger UI will be available at `http://127.0.0.1:8000/docs`.*

#### 3. Frontend Setup
```bash
cd ../frontend

# Install Node dependencies
npm install

# Configure environment variables
cp .env.example .env
# Set NUXT_PUBLIC_API_BASE=http://localhost:8000

# Run the frontend test suite (20 tests)
npm test

# Launch the Nuxt 3 development server
npm run dev
```
*Frontend application will be accessible at `http://localhost:3000`.*

---

## 🧪 Instructions for Testing the Main Features

### 1. Automated Test Execution

Run both test suites to verify system integrity:

```bash
# 1. Run all 153 backend tests (AST verification, misconceptions, adaptive engine, API security)
cd backend
.venv\Scripts\pytest

# 2. Run all 20 frontend unit & store tests (Pinia stores, route middleware, scoring)
cd ../frontend
npm test

# 3. (Optional) Run LLM benchmark verification harness with mock generator
cd ../backend
python eval/run_eval.py -N 10 --mock
```

---

### 2. Manual Step-by-Step Feature Test Scripts

For quick assessment without signing up, use the pre-provisioned demo explorer account or frictionless Guest Mode:
- **Demo Account**: `demo@mathquest.org` / `MathQuest2026!`
- **Guest Mode**: Click **"Continue as Guest 🎒"** on the login or signup page.

#### Feature Journey 1: Frictionless Guest Learning & Adaptive Quiz
1. Navigate to `http://localhost:3000/login` (or the live URL) and click **"Continue as Guest 🎒"**.
2. Notice the top banner displays `Playing in Guest Mode` with no personal information requested.
3. On the **Territory Map**, switch between **Georgia GSE (MGSE)** and **CBSE Class 6 (NCERT)**.
4. Click on **"🍰 Unlike Fractions"** (Grade 5).
5. Inspect the pedagogical lesson: read the step-by-step breakdown, view the SVG infographic, and click the **Play Lesson Narration** button to test Web Speech audio.
6. Click **"Practice Now ⚔️"** to enter the distraction-free Focus Quiz.
7. Select an answer and click **"Confirm Answer"**. Observe instant deterministic AST verification.
8. Expand the **Hint Ladder** (Clue 1, 2, 3) to test progressive pedagogical hints.
9. Complete all 10 questions and click **"Complete Quest & View Results 🏆"**.
10. Verify confetti celebration, earned XP, accuracy rating, and unlocked badges on `/results`.

#### Feature Journey 2: User Registration, Onboarding Personalization, & Dashboard
1. Open a new incognito window and visit `/signup`.
2. Enter an email address and a password ($\ge 6$ characters). Click **"Start My Adventure 🌟"**.
3. You will be automatically directed to `/onboarding`.
4. Enter an adventurer nickname (e.g. `Speedy Solver`), select **Grade 6**, and select **Georgia Standards (GSE)**.
5. Click **"Launch My Adventure! 🚀"**.
6. Verify seamless redirection to `/dashboard`.
7. Verify that the personalized greeting reads: **"Welcome back, Speedy Solver!"** with **Grade 6 • Georgia GSE** pre-selected.

#### Feature Journey 3: Diagnostic Misconception Detection
1. Start a quiz in **Unlike Fractions** (`MGSE5.NF.1`).
2. Given a problem such as $\frac{1}{3} + \frac{1}{4}$, select the distractor $\frac{2}{7}$ (the classic "added denominators" error).
3. Confirm the answer.
4. Observe the red diagnostic feedback banner: rather than simply saying "Incorrect", it specifically diagnoses:
   > *"Denominators represent total parts in a whole—find a common denominator first!"*
5. Answer the next 2 questions correctly and observe adaptive tier promotion from **Easy** to **Medium**.

#### Feature Journey 4: Accessibility & Dyslexia Mode
1. In the top navbar, click the **"Aa Dyslexia Font"** toggle button.
2. Observe all headings and body typography immediately transition to the [Lexend](https://fonts.google.com/specimen/Lexend) font family, engineered to reduce visual crowding.
3. Use the `Tab` and `Shift+Tab` keys to navigate throughout the page; observe high-contrast focus rings on all interactive elements.

#### Feature Journey 5: Deep-Linking & Protected Route Middleware
1. In a fresh private window, directly enter the protected URL `/progress`.
2. Notice the route middleware automatically intercepts and redirects to `/signup?redirect=%2Fprogress`.
3. Click **"Sign In here"** and submit the demo credentials.
4. Verify that upon login, you are immediately routed to `/progress` (the originally requested deep link).

---

## ⚠️ Known Limitations & Incomplete Features

1. **Client-Orchestrated Quiz Sessions**:
   - While every individual math problem and distractor diagnosis is verified deterministically on the backend (`/api/answer`), the frontend coordinates 10-question session tallies. In a formal standardized testing environment, total quiz state would be signed server-side.
2. **Classroom Parental Consent Gateway**:
   - MathQuest is built as a developer assessment prototype and classroom demo. It does not currently implement a formalized verifiable parental consent (VPC) gateway or COPPA email verification workflow before signup.
3. **Render Free-Tier Inactivity Sleep**:
   - The backend is deployed on Render's free tier, which puts containers to sleep after 15 minutes of inactivity. When asleep, the first incoming request can take ~50 seconds to wake up. An animated in-app wake-up banner informs the user while the server starts.
4. **Browser-Dependent Text-to-Speech**:
   - Narration relies on the browser's native Web Speech API (`window.speechSynthesis`). Voice accent and quality depend on the host operating system's installed speech synthesis voices.

---

## 📄 License

MIT License. Developed and engineered for the MathQuest developer assessment.
