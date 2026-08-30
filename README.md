# Career PathFinder — AI-Powered Personalized Learning Path Recommender

A full-stack SaaS app for engineering students: create an account, fill in a
profile, and the app matches you to a career, analyzes your real skill gaps,
builds a **prerequisite-ordered learning roadmap** of ranked courses, and lets you
track progress course-by-course. A grounded AI assistant answers questions about
*your* path.

- **Auth** — email/password with JWT (bcrypt-hashed).
- **Storage** — MongoDB Atlas. Every user, profile, path, and progress record is
  persisted server-side; the client only holds a JWT and always refetches.
- **Recommendation engine** — a local, explainable model (TF-IDF + Truncated SVD)
  over a synthetic ~18k-row course catalog. No API key required.
- **AI assistant + course quizzes** — use Gemini/OpenAI when a key is set,
  otherwise a grounded offline engine / built-in question bank.

> Deep technical documentation — every algorithm, the ML model, the CSV schema —
> is in [`docs/SYSTEM.md`](docs/SYSTEM.md). API reference: [`docs/API.md`](docs/API.md).
> Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## The user flow

```
Register / Sign in
      │  POST /api/auth/register|login → JWT (localStorage)
      ▼
Complete profile               (paste a résumé to auto-detect skills)
      │  POST /api/onboarding/profile → profiles collection
      ▼
Find My Career                 (interests / skills / prefs pre-filled, editable)
      │  POST /api/careers/discover → top-3 matches + clarification + compare
      ▼
Select a career → roadmap generated
      │  POST /api/paths/generate/{career_id} → learning_paths collection
      ▼
Track it
   • mark each course done / pending          → phase auto-completes when all done
   • add / remove courses from Recommendations
   • take a 3–4 question quiz per course       → passing raises job-readiness
   • regenerate the whole roadmap
   • "Why this path works" — per-phase AI explanation
      ▼
Dashboard: readiness %, hours, phases done, recent course progress, skill radar
```

---

## What's built

### Recommendation / path engine (`backend/app/ml/`)

The synthetic course catalog (`backend/app/data/courses.csv`, ~18k rows across 14
engineering branches and every taxonomy skill) is loaded once at startup and used
to fit a **hybrid TF-IDF + Truncated SVD (LSA)** retrieval space and a **NetworkX
prerequisite DAG**. From that:

- **Ranked course recommendations** — 8 explainable factors (goal fit, skill-gap
  coverage, branch fit, level fit, rating, prerequisite readiness, time fit,
  format) with per-learner weights that adapt from completions.
- **Prerequisite-ordered path** — tracks selected by goal similarity + biggest
  gaps, tier ladders walked, prerequisites topologically closed, grouped into ≤4
  phases, each with a project + a YouTube supplement block.

Accuracy is gated by `python -m scripts.eval_recommender` (mean precision ≈ 0.94,
topological validity, 0 unresolved prerequisites).

### Feature map

| Feature | Backend | Frontend |
|---|---|---|
| Auth (register / login / me) | `app/api/auth.py`, `app/core/security.py` | `context/AuthContext.jsx`, `pages/LoginPage.jsx`, `pages/RegisterPage.jsx` |
| Profile (persisted per user) | `app/api/onboarding.py`, `app/db/repository.py` | `pages/ProfilePage.jsx` |
| Résumé → skill extraction | `app/services/skill_extract.py` | `components/ResumeImport.jsx` |
| Career discovery & compare | `app/services/career_engine.py` | `pages/DiscoverPage.jsx` |
| Skill-gap analysis | `app/services/skill_gap_engine.py` | (dashboard radar) |
| Ranked course recommendations | `app/ml/ranker.py`, `engine.py` | `pages/CoursesPage.jsx` |
| Prerequisite-ordered roadmap | `app/ml/planner.py`, `graph.py` | `pages/RoadmapPage.jsx` |
| Course + phase progress tracking | `app/services/progress.py`, `app/api/paths.py` | `pages/RoadmapPage.jsx` |
| Add / remove courses, regenerate | `app/api/paths.py` | `pages/CoursesPage.jsx`, `pages/RoadmapPage.jsx` |
| Per-phase AI explanation | `app/services/path_explain.py` | `pages/RoadmapPage.jsx` |
| Per-course quizzes (3–4 Q) | `app/services/course_quiz.py`, `app/data/quiz_bank.py` | `components/QuizModal.jsx` |
| AI assistant (floating panel) | `app/services/ai_assistant.py` | `components/AssistantWidget.jsx`, `lib/Markdown.jsx` |
| Dashboard / analytics | `app/api/analytics.py` | `pages/DashboardPage.jsx` |
| Adaptive ranker weights | `app/ml/engine.py` `record_feedback()` | — |

---

## Project structure

```
backend/
  app/
    api/          FastAPI routers: auth, onboarding, careers, skills,
                  recommendations, paths, assessments, assistant, analytics, system
    core/         config (env), security (bcrypt + JWT + get_current_user)
    data/         taxonomy_data.py (careers/skills), quiz_bank.py, courses.csv
    db/           mongo.py (connection + collections), repository.py (data access)
    ml/           the engine — catalog, semantic (TF-IDF+SVD), graph (DAG),
                  ranker (8 factors), planner, explain, engine
    models/       Pydantic schemas
    services/     career_engine, skill_gap_engine, progress, path_explain,
                  course_quiz, skill_extract, ai_assistant, youtube_service
    main.py
  requirements.txt   fastapi, uvicorn, pymongo, dnspython, bcrypt, pyjwt,
                     pandas, scikit-learn, networkx, joblib  (+ optional openai / gemini)
frontend/
  src/
    api/client.js       fetch wrapper, attaches the JWT, 401 → logout
    context/            AuthContext, AppDataContext
    components/         AppLayout (sidebar), AssistantWidget, KeywordInput,
                        ResumeImport, QuizModal
    pages/              Landing, Login, Register, Dashboard, Profile, Discover,
                        Courses, Roadmap
    lib/Markdown.jsx    dependency-free markdown renderer (assistant replies)
    App.jsx             react-router routes
docs/  SYSTEM.md · ARCHITECTURE.md · API.md
```

---

## Running locally

### 1. MongoDB

Create a free cluster at <https://cloud.mongodb.com> and copy the connection
string. The app creates its collections and indexes on first startup.

### 2. Backend

```bash
cd backend
python -m venv venv
venv/Scripts/activate                 # Windows  (source venv/bin/activate elsewhere)
pip install -r requirements.txt
cp .env.example .env                   # fill in MONGODB_URI (+ optional AI keys)
python -m scripts.build_cache          # fit + cache the TF-IDF/SVD space (~12s cold)
uvicorn app.main:app --reload --port 8000
```

Startup log: `[mongo] connected to 'pathfinder'` then `[ml.engine] warm complete`.
API docs at <http://localhost:8000/docs>.

### 3. Frontend

```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
```

App at <http://localhost:5173>.

---

## Configuration (`backend/.env`)

| Var | Required | Effect |
|---|---|---|
| `MONGODB_URI` | **yes** | Atlas connection string. `MONGODB_USERNAME` / `MONGODB_PASSWORD` are injected if the URI omits them. `MONGODB_DB` defaults to `pathfinder`. |
| `SECRET_KEY` | prod | signs JWT access tokens (7-day expiry) |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` | no | live LLM for the assistant + path explanation; otherwise the grounded offline engine |
| `COURSE_QUIZ_LLM` | no | `true` to generate per-course quizzes with the LLM instead of the offline bank (slow, uses quota) |
| `YOUTUBE_API_KEY` | no | real ranked YouTube results instead of a search link |
| `CORS_ORIGINS` | no | comma-separated allowed browser origins |

---

## Notes / next steps

- The curated taxonomy (`app/data/taxonomy_data.py`) covers 20 careers and ~74
  skills; could be widened via O*NET / ESCO.
- Course *content* beyond YouTube (Coursera/edX) has no free public catalog API.
- Per-course quiz bank (`app/data/quiz_bank.py`) hand-covers ~73% of courses that
  appear in generated roadmaps; the rest fall back to a generic study check or,
  with `COURSE_QUIZ_LLM=true`, LLM generation (cached forever per course).
