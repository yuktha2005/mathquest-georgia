# MathQuest — Manual Smoke Testing Runbook & Quality Checklist

This runbook documents manual verification scripts for the six primary end-to-end user journeys of the MathQuest platform. It provides exact step-by-step instructions, inputs, expected visual states, and failure triage.

---

## Pre-Requisites & Local Setup

1. **Backend Server Running**:
   ```bash
   cd backend
   .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
   *Verify: `http://127.0.0.1:8000/docs` returns Swagger UI.*

2. **Frontend Dev Server Running**:
   ```bash
   cd frontend
   npm run dev -- --port 3000
   ```
   *Verify: `http://localhost:3000` is accessible in the browser.*

3. **Storage Reset (Between Flows)**:
   - Open Developer Tools (`F12` or `Ctrl+Shift+I`) → **Application** tab → **Storage** → Click **Clear site data**.

---

## Test Flow 1: Guest → Topics → Learn → Quiz → Results

**Objective**: Verify that students can explore the entire curriculum, read lessons, take quizzes, and see diagnostic results without ever creating an account or providing personal information.

| Step | Action | Expected Visual State / Assertion | Pass/Fail |
|---|---|---|---|
| 1.1 | Visit `http://localhost:3000/login` in an incognito window. | Login card displays email/password inputs, and an orange **"Continue as Guest 🎒"** button. | [ ] |
| 1.2 | Click **"Continue as Guest 🎒"**. | Redirects to `/`. Top banner displays **"Exploring in Guest Mode"** with **"Sign Up Free ✨"**. Profile avatar shows `🎒`. | [ ] |
| 1.3 | Click on **"🍰 Unlike Fractions"** on the Territory Map. | Navigates to `/learn/5/fractions`. Topic title, pedagogical explanation, visual infographic, and audio player render. | [ ] |
| 1.4 | Click **"Practice Now ⚔️"**. | Enters distraction-free Focus layout (`/quiz?board=georgia&grade=5&topic=fractions`). Top navbar and mobile tab bar are hidden. | [ ] |
| 1.5 | Select an option (e.g. `Option A`) and click **"Confirm Answer"**. | Mathematical AST verification runs; feedback panel appears with points, streak update, and procedural explanation. | [ ] |
| 1.6 | Complete all 10 questions and click **"Complete Quest & View Results 🏆"**. | Navigates to `/results`. Confetti bursts; accuracy percentage, earned XP, best streak, and question-by-question review appear. | [ ] |
| 1.7 | Open browser DevTools → `localStorage`. | `mathquest_multi_curriculum_session_v2` contains updated score, streak, history, and badges. | [ ] |

---

## Test Flow 2: Signup → Setup (Onboarding) → Dashboard

**Objective**: Verify that new users can create an account, complete first-time profile personalization (nickname, grade, curriculum standard), and land on the customized dashboard.

| Step | Action | Expected Visual State / Assertion | Pass/Fail |
|---|---|---|---|
| 2.1 | Visit `http://localhost:3000/signup`. | Registration card with email, password, and confirm password fields. | [ ] |
| 2.2 | Enter a valid email (e.g. `test_explorer@mathquest.org`) and password $\ge 6$ characters. Click **"Create Free Account"**. | Account created in Supabase Auth. Browser automatically redirects to `/onboarding`. | [ ] |
| 2.3 | On `/onboarding`, enter display name `Alex The Quick`, select **Grade 6**, and select **CBSE Class 6 (NCERT)**. | Selected cards highlight with rings and checkmarks (`✓`). | [ ] |
| 2.4 | Click **"Launch My Adventure! 🚀"**. | Saves setup to Supabase `profiles` table. Redirects to `/dashboard`. | [ ] |
| 2.5 | Inspect `/dashboard` header and cards. | Greeting reads: **"Welcome back, Alex The Quick!"**. Grade reads **Grade 6 • CBSE Class 6 (NCERT)**. Explorer Account badge shows in emerald. | [ ] |

---

## Test Flow 3: Login → Dashboard

**Objective**: Verify that returning registered students can log in with their credentials and automatically load their cloud mastery, badges, and history.

| Step | Action | Expected Visual State / Assertion | Pass/Fail |
|---|---|---|---|
| 3.1 | Visit `http://localhost:3000/login`. | Sign-in page with email and password inputs. | [ ] |
| 3.2 | Enter demo credentials (`demo@mathquest.org` / `MathQuest2026!`) and submit. | Spinner appears on button (`Signing in...`). | [ ] |
| 3.3 | Verify post-login redirection. | Redirects to `/dashboard`. Profile data and display name load. | [ ] |
| 3.4 | Inspect Mastery & Recent Activity. | Saved mastery bars and unlocked trophies are populated from Supabase. | [ ] |

---

## Test Flow 4: Logout

**Objective**: Verify that logging out terminates the authenticated session, clears user state from the store, and returns the user to the login screen.

| Step | Action | Expected Visual State / Assertion | Pass/Fail |
|---|---|---|---|
| 4.1 | From `/dashboard`, click the profile dropdown in the top header and click **"🚪 Logout"**, or navigate to `/profile` and click **"Sign Out"**. | Session clears, auth cookies/tokens in localStorage are invalidated. | [ ] |
| 4.2 | Verify post-logout route. | Immediately redirects to `/login`. | [ ] |
| 4.3 | Click browser Back button. | Middleware prevents returning to `/dashboard`; user remains on `/login`. | [ ] |

---

## Test Flow 5: Protected Route Redirect and Return (Deep-Linking)

**Objective**: Verify that unauthenticated visitors attempting to access protected internal routes are redirected to `/login` with a `?redirect=` query param, and returning after login lands on the target page.

| Step | Action | Expected Visual State / Assertion | Pass/Fail |
|---|---|---|---|
| 5.1 | In a fresh incognito window (no guest mode, no login), directly type URL: `http://localhost:3000/progress`. | Route middleware intercepts. URL changes to `http://localhost:3000/login?redirect=%2Fprogress`. | [ ] |
| 5.2 | Sign in or click **"Continue as Guest"**. | User is authenticated/guested and automatically returned to the originally requested deep link (`/progress`). | [ ] |
| 5.3 | Verify page content. | `/progress` renders the Topic Mastery Radar and Session History Table without errors. | [ ] |

---

## Test Flow 6: Invalid Deep Link → Custom 404 Page

**Objective**: Verify that typing an invalid route displays the friendly custom 404 page and provides a clear way back.

| Step | Action | Expected Visual State / Assertion | Pass/Fail |
|---|---|---|---|
| 6.1 | Type invalid route in address bar: `http://localhost:3000/non-existent-secret-room`. | Custom 404 error page renders (`error.vue`). | [ ] |
| 6.2 | Verify visual elements. | Displays `404` badge, compass icon (`🧭`), and headline **"Lost in the Mathematical Wilderness"**. | [ ] |
| 6.3 | Click **"Return to Dashboard 🏠"**. | Navigates back to `/dashboard` without console errors. | [ ] |

---

## Automated Test Command

To run the automated Vitest test suite covering the auth store, route middleware, and session flow:
```bash
cd frontend
npm test
```
*Expected: 3 test files, 18 passed.*
