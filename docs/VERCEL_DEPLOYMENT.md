# Deploying MathQuest Frontend on Vercel Free Tier

This guide provides step-by-step instructions for deploying the **Nuxt 3** frontend of **MathQuest** to [Vercel](https://vercel.com/) on the **100% Free Tier (Hobby Plan)**.

---

## 📋 Overview & Free Tier Details

Vercel's Hobby Plan provides:
- **Global Edge Network**: High-speed CDN with automatic HTTPS/TLS certificates.
- **Native Nuxt 3 Support**: Automatic Nitro serverless/edge SSR preset detection and optimization.
- **Continuous Deployment**: Automatic preview deployments on pull requests and production deployment on push to `main`.
- **Zero Configuration Necessary**: Uses standard Nuxt build commands and outputs.

---

## 🔑 Strict Environment Variables

In compliance with **Rule 3** (Strict Secrets & Env Isolation), the frontend requires only one public environment variable:

| Variable | Required | Example | Description |
|---|---|---|---|
| `NUXT_PUBLIC_API_BASE` | Yes | `https://mathquest-georgia-backend.onrender.com` | Base URL of the deployed FastAPI backend on Render. |

> [!NOTE]
> For local testing or pre-deployment validation, `NUXT_PUBLIC_API_BASE` defaults to `http://localhost:8000`.

---

## 🚀 Deployment Instructions

### Step 1: Import Project into Vercel
1. Log in to [Vercel](https://vercel.com/) using your GitHub account.
2. In your Vercel Dashboard, click **Add New...** and select **Project**.
3. Locate your `mathquest-georgia` repository and click **Import**.

### Step 2: Configure Project Settings
In the Project Configuration screen:
1. **Project Name**: `mathquest-georgia` (or custom name of your choice).
2. **Framework Preset**: Select **Nuxt.js** (Vercel usually autodetects this).
3. **Root Directory**: Click **Edit** and set Root Directory to `frontend`.
4. **Build and Output Settings**:
   - **Build Command**: `npm run build` (or leave as default)
   - **Output Directory**: `.output` (or leave default `.output`)
   - **Install Command**: `npm install` (or leave default)

### Step 3: Add Environment Variables
Expand the **Environment Variables** section and add:
- **Key**: `NUXT_PUBLIC_API_BASE`
- **Value**: `https://<your-render-backend-name>.onrender.com` (your live Render backend URL)

### Step 4: Deploy
1. Click **Deploy**.
2. Vercel will install dependencies, build the Nuxt application with Nitro and Vite, and assign a production URL (e.g., `https://mathquest-georgia.vercel.app`).

---

## 🔗 Connecting Frontend & Backend (CORS)

Once Vercel finishes deploying, configure your Render backend to accept API requests from your new Vercel domain:
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Select your `mathquest-georgia-backend` service.
3. In **Environment**, update `FRONTEND_URL` to include your Vercel domain:
   ```env
   FRONTEND_URL = http://localhost:3000,https://mathquest-georgia.vercel.app
   ```
4. Save changes. Render will automatically redeploy with the updated CORS configuration.

---

## 🧪 Verifying the Live Frontend

1. **Visit your Vercel URL**:
   Open `https://mathquest-georgia.vercel.app` in your browser.
2. **Test Board Selection**:
   - Toggle between **Georgia GSE (MGSE)** and **CBSE Class 6 (NCERT Ganita Prakash)**.
   - Verify that Grade 5 and 6 options appear for Georgia, and Class 6 appears for CBSE.
3. **Test Practice Quest**:
   - Click **Start Quest** on any territory (e.g. Fractions or Factors & Multiples).
   - Verify question loading, adaptive scoring, confetti on correct answers, and trophy shelf badge tracking.
4. **Test Study Guides & Narration**:
   - Open a **Learn Guide** (`/learn/5/fractions` or `/learn/6/factors_multiples`).
   - Check interactive video narration and vector infographic diagram rendering.
