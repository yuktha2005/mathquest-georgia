# Supabase Setup Guide — MathQuest Multi-Curriculum Platform

This guide outlines the exact, step-by-step setup for configuring Supabase as the backend database and authentication service for **MathQuest Georgia**.

---

## 📋 Overview

Supabase provides:
1. **User Authentication:** Email/password or OAuth signup and session management.
2. **Postgres Database:** Relational tables with Row Level Security (RLS) for student profiles, sessions, answers, mastery, and badges.
3. **pgvector (Optional RAG):** Semantic search for curriculum standards grounding.

---

## 🚀 Step 1: Create a Supabase Project

1. Navigate to [Supabase](https://supabase.com/) and sign in (or create a free account).
2. From the dashboard, click **"New Project"**.
3. Select your organization.
4. Configure your project:
   - **Name:** `mathquest-georgia` (or `mathquest`)
   - **Database Password:** Generate or choose a strong password (save this securely).
   - **Region:** Choose a region geographically close to your target users (e.g., `East US (North Virginia)`).
   - **Pricing Plan:** **Free Tier** ($0/month).
5. Click **"Create new project"** and wait ~1–2 minutes for the database cluster to provision.

---

## 🗄️ Step 2: Run the Database Migrations

### 2.1 Run Application Schema Migration
1. In your Supabase project dashboard, navigate to the **SQL Editor** tab (the `>_` terminal icon in the left sidebar).
2. Click **"New Query"**.
3. Open [`supabase/migrations/001_app_schema.sql`](../supabase/migrations/001_app_schema.sql) in your code editor, copy its entire contents, and paste them into the SQL editor.
4. Click the green **"Run"** button (or press `Ctrl+Enter` / `Cmd+Enter`).
5. Verify in the **Table Editor** that the following 5 tables are created:
   - `profiles`: Student details, grade, XP, and profile settings.
   - `sessions`: Practice rounds, overall scores, streaks, and accuracy metrics.
   - `answers`: Individual question responses, correctness, and misconception tags.
   - `mastery`: Per-topic student proficiency tracking (0–100%).
   - `badges`: Unlocked student achievements.

> [!NOTE]
> All tables automatically have **Row Level Security (RLS)** enabled with strict policies: users can only `SELECT`, `INSERT`, `UPDATE`, and `DELETE` their own rows (`auth.uid() = user_id`).
> An automated trigger (`on_auth_user_created`) automatically provisions a corresponding `public.profiles` row upon any new user registration in Supabase Auth.

---

## ✉️ Step 3: Turn Email Confirmation OFF

For local development and streamlined classroom onboarding, disable email confirmation so students can register and immediately log in:

1. In the Supabase left navigation bar, go to **Authentication** $\to$ **Configuration** $\to$ **Providers**.
2. Click on the **Email** provider accordion to expand its settings.
3. Scroll down to **"Confirm email"**.
4. Toggle **"Confirm email"** to **OFF** (Disabled).
5. Click **"Save"**.

*(Now students can sign up and immediately sign in without needing an external email verification step).*

---

## 🔑 Step 4: Copy Project URL and Anon Key into Frontend Environment

1. In the Supabase left navigation bar, click **Project Settings** (the gear icon at the bottom).
2. Click **API** under Configuration.
3. Locate the **Project API keys** and **Project URL** sections:
   - **Project URL:** `https://<project-ref>.supabase.co`
   - **Project API Keys $\to$ `anon` `public`:** `eyJhbGciOi...`
4. Open `frontend/.env` (or create it from `frontend/.env.example`) and supply:

```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000
NUXT_PUBLIC_SUPABASE_URL=https://<your-project-ref>.supabase.co
NUXT_PUBLIC_SUPABASE_KEY=<your-supabase-anon-key>
```

5. When deploying to **Vercel** or your hosting provider, add these same environment variable names under **Project Settings $\to$ Environment Variables**.

---

## ⚠️ Step 5: Critical Security Rule — Never Use Service-Role Key in the Frontend

> [!CAUTION]
> **NEVER EXPOSE THE `service_role` SECRET KEY IN THE FRONTEND CODEBASE OR CLIENT `.env`!**
>
> * The `service_role` key bypasses **all Row Level Security (RLS)** rules. If bundled into client-side JavaScript, any student could modify other users' grades, scores, or accounts.
> * The Nuxt frontend must **strictly** use the public `anon` key (`NUXT_PUBLIC_SUPABASE_KEY`).
> * With the `anon` key and our RLS policies, PostgreSQL securely enforces that users can only ever read and write their own data.

---

## 🧪 Step 6: Verification Checklist

| Step | Action | Expected Result |
| :--- | :--- | :--- |
| **1** | Register new user in frontend or Supabase Auth | User appears in `auth.users` |
| **2** | Check `public.profiles` table in Supabase | Row auto-created by `handle_new_user()` trigger |
| **3** | Submit a quiz answer | Record saved to `public.answers` with authenticated `user_id` |
| **4** | Complete a quiz round | Session saved to `public.sessions`; badges recorded in `public.badges` |
| **5** | RLS cross-user test | Querying rows where `user_id != auth.uid()` returns 0 rows |
