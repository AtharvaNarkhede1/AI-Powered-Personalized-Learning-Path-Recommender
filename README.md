# Career PathFinder - AI-Powered Personalized Learning Path Recommender

An AI-powered learning assistant that turns a learner's goals, interests, and
current skill level into a structured, milestone-based learning roadmap -
with explanations for every recommendation and a dashboard to track progress.

## Problem

Online learning platforms offer thousands of courses, but learners struggle
to figure out the right *sequence* of courses, projects, and assessments to
reach a specific goal. Career PathFinder bridges that gap: describe your goal
in plain language, and it builds a personalized roadmap with prerequisites,
milestones, and clear reasoning behind every suggestion.

## What's built

| Requirement | Where |
|---|---|
| Conversational interface | `frontend/src/components/ChatInterface.jsx` + `backend/app/api/chat.py` |
| Learner profiling engine | `backend/app/services/profiling_engine.py` |
| Recommendation engine | `backend/app/services/recommendation_engine.py` |
| Learning path generator (prerequisites + milestones) | `backend/app/services/path_generator.py` |
| AI assistant (explanations + Q&A) | `backend/app/services/ai_assistant.py` |
| Progress dashboard | `frontend/src/components/Dashboard.jsx` + `backend/app/services/progress_tracker.py` |

## Project structure

```
backend/
  app/
    api/            # FastAPI routers (one file per feature area)
    core/           # config (env vars)
    data/           # sample course catalog + goal->skill map (JSON)
    models/         # Pydantic request/response schemas
    services/       # the actual "AI" - profiling, recommending, path-building, chat
    db.py           # in-memory learner store (swap for a real DB later)
    main.py         # FastAPI app entrypoint
  requirements.txt
  .env.example
frontend/
  src/
    api/client.js   # fetch wrapper around the backend REST API
    components/      # ChatInterface, ProfileForm, RecommendationCard, Dashboard, ...
    pages/           # Home, ChatPage, PathPage, DashboardPage
  package.json
  .env.example
docs/
  ARCHITECTURE.md
  API.md
```

## AI / ML components used

- **Profiling engine**: keyword + regex based extraction of goals, interests,
  and skill level from free-text chat messages (see
  `profiling_engine.extract_from_message`). Designed to be swapped for an LLM
  function-calling extraction step without changing its interface.
- **Recommendation engine**: a transparent, explainable weighted-scoring
  heuristic (skill overlap with goal, interest overlap, difficulty fit,
  prerequisite penalty) rather than a black-box model - every recommendation
  ships with a human-readable `reason` string.
- **Path generator**: topological sort over course prerequisites to guarantee
  a learner never sees a course before its prerequisites, grouped into
  milestones with a capstone project at the end.
- **AI assistant**: optionally backed by the OpenAI API (`OPENAI_API_KEY`) for
  richer conversational replies and Q&A; falls back to templated responses so
  the whole app runs fully offline for local grading/demoing.

## UX decisions

- Chat and a structured form both feed the *same* learner profile, so a
  learner can describe their goal conversationally or fill out a quick form -
  whichever they prefer.
- Every recommendation and milestone shows *why* it's there (skill tags +
  reason text), because trust in a recommender depends on explainability.
- The dashboard's skill-growth chart and stat tiles follow a validated,
  colorblind-safe palette (see `frontend/src/styles/index.css`) with a single
  consistent hue per series and light/dark theme support.

## Running locally

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # optionally add OPENAI_API_KEY
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

## Deployment (prototype)

- Backend: any container/PaaS host that runs `uvicorn app.main:app` (Render,
  Railway, Fly.io, etc.), with `DATABASE_URL` pointed at a real Postgres
  instance instead of the default in-memory store.
- Frontend: static hosting (Vercel/Netlify) with `VITE_API_BASE_URL` pointed
  at the deployed backend.

## Known limitations / next steps

See inline `TODO` comments throughout `backend/app/` and
`docs/ARCHITECTURE.md` for the full list. Highlights:

- Learner data is in-memory and resets on backend restart - needs a real
  database before this is anything but a prototype.
- No authentication yet; a learner is identified by a random ID stored in
  the browser's `localStorage`.
- Recommendation scoring is a heuristic, not a trained model - the interface
  is designed so it can be swapped for one once real usage data exists.
