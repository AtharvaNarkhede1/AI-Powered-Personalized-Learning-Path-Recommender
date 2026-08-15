# Architecture

## Overview

Career PathFinder is split into a stateless-ish FastAPI backend and a React
(Vite) single-page frontend. The backend holds all "intelligence": learner
profiling, recommendations, path generation, progress tracking, and the AI
assistant. The frontend is a thin client that renders whatever the backend
returns.

```
frontend (React)  <-- REST/JSON -->  backend (FastAPI)
                                         |
                                         v
                              app/data/*.json (course catalog, goal->skill map)
                              app/db.py (in-memory learner state - swap for a
                                         real DB before production)
```

## Backend modules (backend/app/)

| Module | Responsibility |
|---|---|
| `services/profiling_engine.py` | Builds/updates a `LearnerProfile` from form input or free-text chat (keyword + regex extraction). |
| `services/recommendation_engine.py` | Scores the course catalog against a learner's goal/interests/skill level/completed courses. |
| `services/path_generator.py` | Orders relevant courses by prerequisite (topological sort), groups them into milestones, appends a capstone project. |
| `services/progress_tracker.py` | Computes completion %, per-skill proficiency growth, and "next actions" from a learner's `LearningPath`. |
| `services/ai_assistant.py` | Chat replies + "why was this recommended" explanations + free-form Q&A. Uses OpenAI if `OPENAI_API_KEY` is set, otherwise falls back to templated responses so the prototype runs offline. |
| `api/*.py` | Thin FastAPI routers that wire the above services to HTTP endpoints. |

## Data flow for a typical session

1. Learner talks to the assistant (`POST /api/chat`) or fills the profile form (`PUT /api/profile/{id}`).
2. `profiling_engine` extracts/updates fields on the `LearnerProfile`.
3. Frontend calls `GET /api/recommend/{id}` to preview top course matches, each with a `reason` string.
4. Learner generates a full roadmap (`POST /api/path/{id}/generate`) -> `path_generator` returns ordered `Milestone`s with prerequisites and an estimated hour total.
5. As the learner progresses, `PUT /api/progress/{id}` updates milestone status; `GET /api/progress/{id}` (`progress_tracker`) recomputes the dashboard snapshot.

## Known prototype limitations (see per-file TODOs)

- State is in-memory (`app/db.py`) - restarting the backend wipes all learner data. Swap for SQLAlchemy + a real DB (`DATABASE_URL` is already wired up in `core/config.py`) before deploying for real users.
- Recommendation scoring is a hand-tuned heuristic, not a trained model - documented as a TODO in `recommendation_engine.py` for when real interaction data exists.
- No auth - `learner_id` is a client-generated random string stored in `localStorage`.
