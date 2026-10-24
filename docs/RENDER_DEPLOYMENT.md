# Deploying MathQuest Backend on Render Free Tier

This guide provides comprehensive instructions for deploying the FastAPI backend of **MathQuest** to [Render](https://render.com/) on the **100% Free Tier**.

---

## 📋 Overview & Free Tier Details

Render's Free Web Service tier provides:
- **Compute**: 512 MB RAM, 0.1 vCPU.
- **HTTPS**: Automated TLS/SSL certificate generation for `https://<your-service>.onrender.com`.
- **Inactivity Sleep**: Services sleep after **15 minutes** of zero traffic. The next incoming request takes ~50 seconds to spin back up, after which requests process with standard sub-second latency.
- **Continuous Deployment**: Automatically re-deploys when changes are pushed to your Git `main` branch.

---

## 🔑 Strict Environment Variables

Conforming to **Rule 2 & 3** (Environment Variable Enforced Models and Zero Secrets in code/git), configure the following environment variables:

| Variable | Required | Example / Recommended | Description |
|---|---|---|---|
| `PYTHON_VERSION` | Yes | `3.11.9` | Pins the Python runtime environment on Render. |
| `GEMINI_API_KEY` | Yes | `AIzaSy...` | Google GenAI API key from [Google AI Studio](https://aistudio.google.com/). |
| `GEMINI_MODEL` | Yes | `gemini-2.5-flash` | The primary Gemini model for structured output generation. |
| `GEMINI_MODEL_ALT` | No | `gemini-2.5-pro` | Alternate model used for model comparison evaluations. |
| `GEMINI_EMBED_MODEL` | Yes | `text-embedding-004` | Embedding model for standards retrieval and Supabase pgvector. |
| `FRONTEND_URL` | Yes | `https://mathquest.vercel.app,http://localhost:3000` | Allowed CORS origin(s) (comma-separated). |
| `SUPABASE_URL` | Optional | `https://your-project.supabase.co` | Supabase Postgres project URL (falls back to local standards if omitted). |
| `SUPABASE_KEY` | Optional | `your_supabase_anon_key` | Supabase anonymous public API key. |
| `EVAL_SAMPLE_SIZE` | No | `3` | Sample size $N$ for automated prompt evaluation benchmarks. |

> [!NOTE]
> Render automatically injects the `$PORT` environment variable (typically `10000`). You do **not** need to manually define `PORT`.

---

## 🚀 Deployment Option A: One-Click Render Blueprint (Recommended)

MathQuest includes a root [`render.yaml`](file:///d:/mathquest-georgia/render.yaml) blueprint specification.

1. **Push your repository** to GitHub or GitLab.
2. Sign in to your [Render Dashboard](https://dashboard.render.com/).
3. In the top navigation bar, click **New +** and select **Blueprint**.
4. Select your `mathquest-georgia` repository and click **Connect**.
5. Render detects [`render.yaml`](file:///d:/mathquest-georgia/render.yaml) and shows the configuration:
   - **Service Name**: `mathquest-georgia-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
6. Fill in the prompted secret environment variables:
   - `GEMINI_API_KEY`: Your Gemini API key.
   - `FRONTEND_URL`: Your hosted frontend URL (e.g., `https://mathquest.vercel.app`) or `http://localhost:3000`.
   - `SUPABASE_URL` & `SUPABASE_KEY`: Your Supabase credentials (or leave blank to use local RAG markdown fallback).
7. Click **Apply**. Render will trigger the initial build and deploy your service.

---

## 🛠️ Deployment Option B: Manual Web Service Setup via Render Dashboard

If you prefer configuring the service manually without Blueprints:

1. Sign in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and choose **Web Service**.
3. Connect your Git repository.
4. Fill in the service parameters:
   - **Name**: `mathquest-georgia-backend`
   - **Region**: Select the region closest to your users (e.g., `Oregon (US West)` or `Ohio (US East)`).
   - **Branch**: `main`
   - **Root Directory**: `backend` *(CRITICAL: tells Render where requirements.txt and app/ are located)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Click **Advanced**:
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: `Yes`
6. Under **Environment Variables**, click **Add Environment Variable** for each:
   ```env
   PYTHON_VERSION = 3.11.9
   GEMINI_API_KEY = your_gemini_api_key_here
   GEMINI_MODEL = gemini-2.5-flash
   GEMINI_MODEL_ALT = gemini-2.5-pro
   GEMINI_EMBED_MODEL = text-embedding-004
   FRONTEND_URL = http://localhost:3000,https://your-frontend.vercel.app
   SUPABASE_URL = https://your-project.supabase.co
   SUPABASE_KEY = your_supabase_anon_key
   EVAL_SAMPLE_SIZE = 3
   ```
7. Click **Create Web Service**.

---

## 🔍 Verifying the Deployment

Once Render finishes deploying (indicated by a green **Live** badge), verify your service endpoints:

### 1. Health Check
```bash
curl https://mathquest-georgia-backend.onrender.com/health
```
**Expected Response:**
```json
{
  "status": "ok",
  "app": "MathQuest Georgia API",
  "version": "0.1.0"
}
```

### 2. Interactive Swagger Documentation
Open in your browser:
```
https://mathquest-georgia-backend.onrender.com/docs
```
You can inspect and execute all API endpoints (`/api/question`, `/api/questions`, `/api/question/batch`, `/api/curriculum/packs`, `/api/infographic`, `/api/eval`).

### 3. Generate a Math Question (Georgia MGSE)
```bash
curl -X POST https://mathquest-georgia-backend.onrender.com/api/question \
  -H "Content-Type: application/json" \
  -d '{"grade": 5, "topic": "fractions", "tier": "medium", "board": "georgia"}'
```

### 4. Generate a Math Question (CBSE Class 6)
```bash
curl -X POST https://mathquest-georgia-backend.onrender.com/api/question \
  -H "Content-Type: application/json" \
  -d '{"grade": 6, "topic": "factors_multiples", "tier": "easy", "board": "cbse"}'
```

---

## 💡 Tips for Free Tier Operation

1. **Free Tier Inactivity & Cold Starts**:
   - Free instances spin down after 15 minutes of inactivity.
   - The Nuxt frontend includes a child-friendly wake-up progress banner (`🚀 Waking up the MathQuest adventure server...`) that detects latencies > 2.5s and reassures young learners.
   - If you want to keep the instance warm for demo presentations, set up a free uptime monitor (such as [UptimeRobot](https://uptimerobot.com/) or [cron-job.org](https://cron-job.org/)) to ping `https://<your-service>.onrender.com/health` every 14 minutes.
2. **CORS Updates**:
   - Whenever your Nuxt frontend is deployed (e.g., to Vercel, Netlify, or Render Static Sites), update `FRONTEND_URL` in the Render environment variables tab to include your live frontend URL.
3. **Live Logs & Traceability**:
   - Access real-time logs directly in the Render dashboard under the **Logs** tab. Latencies, Gemini API retry logs, curriculum pack lookups, and math validation records stream live.
