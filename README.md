# Career PathFinder - AI-Powered Personalized Learning Path Recommender

An AI-powered career & learning assistant for engineering students: it matches you to
career paths from an onboarding profile, analyzes your real skill gaps against each
career's requirements, and builds a milestone-based learning roadmap with real
resources, diagnostic quizzes, and an explainable AI chat assistant.

## What's built

The **core** of the app is a local, dataset-driven engine (`backend/app/ml/`): a
synthetic course catalog (`backend/app/data/courses.csv`, **~18k rows** across all
14 engineering branches and every skill in the taxonomy) is loaded once at startup
and used to fit a **hybrid TF-IDF + Truncated SVD (LSA)** retrieval space, build a
**NetworkX prerequisite DAG**, and serve (a) ranked course recommendations and
(b) a prerequisite-ordered, phased learning path. Ranking uses 8 explainable
factors (goal fit, skill-gap coverage, branch fit, level fit, rating, prerequisite
readiness, time fit, format) with per-learner weights that adapt from feedback;
short queries get pseudo-relevance-feedback expansion. YouTube is a **secondary**
"also recommended" section per milestone. No LLM/API key is required — configure
`GEMINI_API_KEY` / `OPENAI_API_KEY` in `backend/.env` only to upgrade the (already
data-grounded) chat assistant to a live model.

Accuracy is gated by `python -m scripts.eval_recommender` (14 checks: fit time,
per-goal precision, mean precision ≥ 0.85 — currently ~0.94, topological validity,
0 unresolved prerequisites, feedback-loop effect).

> **Full technical documentation — every algorithm, the ML model, the CSV schema,
> the YouTube integration, all inputs/outputs and the end-to-end flow — is in
> [`docs/SYSTEM.md`](docs/SYSTEM.md).**

| Feature | Where |
|---|---|
| 5-step onboarding wizard | `frontend/src/components/OnboardingWizard.jsx` + `backend/app/api/onboarding.py` |
| Career discovery & matching | `backend/app/services/career_engine.py` (branch fit + LSA interest/skill similarity) |
| Skill gap analysis | `backend/app/services/skill_gap_engine.py` (quiz-verified proficiency preferred over self-report) |
| **Course recommendations (ranked)** | `backend/app/ml/ranker.py` + `frontend/src/components/RecommendationsView.jsx` |
| **Prerequisite-ordered learning path** | `backend/app/ml/planner.py` + `graph.py` (NetworkX DAG) + `frontend/src/components/LearningPathTimeline.jsx` |
| Semantic space (TF-IDF + SVD) | `backend/app/ml/semantic.py` (fitted on `courses.csv`, cached to `app/ml/cache/`) |
| Adaptive ranker weights from feedback | `backend/app/ml/engine.py` `record_feedback()` + `LearnerModelDB` |
| YouTube "also recommended" (secondary) | `backend/app/services/youtube_service.py` (only via `engine.youtube_extras`) |
| Diagnostic quizzes | `backend/app/api/assessments.py` + `frontend/src/components/QuizModal.jsx` |
| AI chat assistant (optional) | `backend/app/services/ai_assistant.py` (Gemini/OpenAI, or grounded offline fallback) |
| Progress dashboard | `frontend/src/components/Dashboard.jsx` + `backend/app/api/analytics.py` |

### Dataset / training

```bash
cd backend
python -m scripts.generate_dataset     # (re)build app/data/courses.csv
python -m scripts.build_cache          # fit + pickle the TF-IDF/SVD space
python -m scripts.eval_recommender     # regression gate (13 checks)
```

## Project structure

```
backend/
  app/
    api/            # FastAPI routers (one file per feature area)
    core/           # config (env vars)
    data/           # curated career/skill taxonomy (taxonomy_data.py)
    db/             # SQLAlchemy models + engine (SQLite by default)
    models/         # Pydantic request/response schemas
    services/       # career matching, skill gaps, path generation, recommendations, AI assistant
    main.py         # FastAPI app entrypoint
  requirements.txt
  .env.example
frontend/
  src/
    api/client.js   # fetch wrapper around the backend REST API
    components/      # OnboardingWizard, CareerDiscovery, LearningPathTimeline, Dashboard, ChatInterface, ...
    App.jsx          # single-page tab-based app shell
  package.json
  .env.example
docs/
  ARCHITECTURE.md
  API.md
```

## AI / ML components used

- **Semantic matching**: local `sentence-transformers` embeddings (`services/embedding_service.py`)
  replace literal substring matching for interest/skill/career matching, so e.g. "JS" and
  "JavaScript" are correctly recognized as related. Falls back to token-overlap matching if the
  optional dependency isn't installed, so the app never hard-crashes.
- **Career matching**: weighted score across branch compatibility, semantic interest alignment,
  semantic skill overlap, and experience-vs-required-level fit -- every match ships with a
  human-readable reason and a clarification question when the top two scores are close.
- **Skill gap analysis**: prefers a quiz-verified proficiency (persisted per-skill after a
  diagnostic quiz) over the self-reported estimate whenever one exists.
- **Path generator**: topological sort (NetworkX) over the skill prerequisite graph, grouped into
  milestones with a project + quiz attached, resources ranked by a hybrid score (rating +
  semantic relevance + format/difficulty fit + upvote/downvote feedback).
- **AI assistant**: optionally backed by Gemini or OpenAI (whichever key is set), grounded in the
  user's real profile/career/skill-gap data; falls back to a templated-but-still-grounded offline
  engine so the whole app runs without any API key.
- **Real resource data**: YouTube Data API v3 integration (`services/youtube_service.py`) when
  `YOUTUBE_API_KEY` is set -- real titles, channels, durations, and an engagement-based rating;
  falls back to a plain search link (no fabricated ratings) otherwise.

## Running locally

### Backend

```bash
cd backend
python -m venv venv
venv/Scripts/activate       # Windows
pip install -r requirements.txt
cp .env.example .env        # optionally add GEMINI_API_KEY / OPENAI_API_KEY / YOUTUBE_API_KEY
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: http://localhost:5173

## Known limitations / next steps

- The static career/skill catalog (`backend/app/data/taxonomy_data.py`) covers 9 careers and
  ~45 skills -- could be expanded via free sources like O*NET (occupation/skill taxonomy) or
  ESCO (EU skills taxonomy).
- Course *content* beyond YouTube (e.g. Coursera/edX) has no free public catalog API and isn't
  integrated; resources are currently YouTube-only.
- No authentication UI beyond demo-login; `POST /api/auth/register` exists but has no frontend
  entry point yet.
