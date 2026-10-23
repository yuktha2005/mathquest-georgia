# MathQuest Georgia 🎮📐

A gamified math learning platform for **Grade 5 and Grade 6** students, aligned to the **Georgia Standards of Excellence (MGSE)**.

---

## 🚀 Overview

MathQuest Georgia turns math practice into an adventure. Designed for 5th and 6th graders in Georgia, the platform provides adaptive challenges, gamified progression, and mathematically rigorous content verified against state standards.

### Key Tenets
- **Verified Math Integrity**: Never trust LLM calculations. Every problem is programmatically validated via `services/verify.py`.
- **Misconception-Driven Distractors**: Multiple-choice options are constructed using an algorithmic misconception library rather than LLM guesswork.
- **Fail-Safe Reliability**: Two repair retries for LLM responses before gracefully falling back to pre-vetted items in `data/fallback_bank.json`.
- **Child-Safe by Design**: Grade-appropriate phrasing, positive reinforcement, and high safety standards.

---

## 🛠️ Tech Stack

- **Frontend (`/frontend`)**: [Nuxt 3](https://nuxt.com/) + [TypeScript](https://www.typescriptlang.org/) + [Tailwind CSS](https://tailwindcss.com/) + [Pinia](https://pinia.vuejs.org/)
- **Backend (`/backend`)**: [FastAPI](https://fastapi.tiangolo.com/) + [Pydantic v2](https://docs.pydantic.dev/latest/)
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL + `pgvector`)
- **LLM Engine**: Google Gemini API via [`google-genai`](https://github.com/googleapis/python-genai)

---

## 🔐 Environment Variables

The project requires the following environment variables (stored in `.env` and never checked into source control):

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
FRONTEND_URL=http://localhost:3000
```

---

## 📁 Repository Structure

```text
mathquest-georgia/
├── AGENTS.md               # Rules and guidelines for AI and human contributors
├── README.md               # Project documentation
├── .gitignore              # Ignored files and folders
├── backend/                # FastAPI backend service
│   ├── data/               # Fallback bank and misconception catalog
│   ├── services/           # Math verification and core logic
│   └── tests/              # Pytest test suite
└── frontend/               # Nuxt 3 web application
```

---

## 🏃 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.11+)
- Supabase account with pgvector enabled

### Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
cd backend
pytest
```

---

## ☁️ Deployment on Render (Free Tier)

The backend is pre-configured for one-click deployment on Render Free Tier via [`render.yaml`](render.yaml).

- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

See [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) for full step-by-step instructions, environment variable setup, and tips for managing the free-tier sleep cycle.

