# Architecture

## Stack

- **Backend**: FastAPI. Persistence is **MongoDB Atlas** via PyMongo — there is no
  ORM and no SQLite. Every user, profile, learning path, progress record,
  feedback event, assessment, and cached course quiz lives in a collection.
- **Auth**: email/password. Passwords are bcrypt-hashed; a signed **JWT** (7-day
  expiry) is issued on register/login and sent as `Authorization: Bearer`. The
  `get_current_user` dependency (`app/core/security.py`) protects every in-app
  endpoint.
- **Frontend**: React + Vite with **react-router**. `AuthContext` holds the JWT
  (localStorage) and hydrates the user via `GET /api/auth/me`; `AppDataContext`
  owns profile / discovery / active path / dashboard and always refetches from
  the server after a mutation. A slim left sidebar (`AppLayout`) replaces the old
  tab navbar.
- **AI/ML**: the local TF-IDF + Truncated-SVD engine (`app/ml/`) is unchanged and
  needs no key. An optional Gemini/OpenAI layer powers the chat assistant, the
  per-phase path explanation, and (opt-in) per-course quiz generation; all three
  have grounded offline fallbacks.

## Backend layout (`backend/app/`)

- `core/` — `config.py` (env), `security.py` (hash/verify password, create/decode
  JWT, `get_current_user`).
- `db/`
  - `mongo.py` — the `MongoClient`, collection handles (`users`, `profiles`,
    `learning_paths`, `path_progress`, `learner_models`, `assessments`,
    `skill_proficiencies`, `user_feedback`, `course_quizzes`), `ping()` and
    `ensure_indexes()`.
  - `repository.py` — all data access: user CRUD, profile upsert / hydration,
    path save/load (with the `Milestone`/`ResourceItem` ↔ dict mapping),
    progress get/set, learner-model get/set, assessment + skill-proficiency
    writes, course-quiz cache.
- `api/` — routers: `auth`, `onboarding`, `careers`, `skills`, `recommendations`,
  `paths`, `assessments`, `assistant`, `analytics`, `system`.
- `services/`
  - `career_engine.py` — career discovery/matching (branch fit + LSA
    interest/skill similarity + experience fit; clarification question; cross-
    branch advice).
  - `skill_gap_engine.py` — per-skill gap; prefers a quiz-verified proficiency
    (`skill_proficiencies` collection) over the self-reported estimate.
  - `progress.py` — `apply_progress()` overlays the learner's
    `completed_resource_ids` onto a path: sets `resource.completed`, flips a
    milestone to `completed` when all its courses are done (and back when one is
    un-done), recomputes readiness as
    `base + (100 - base) · done_hours / total_hours`, and refreshes `next_action`.
  - `path_explain.py` — per-phase "why these courses" + an overall overview,
    from the planner's real `why_now` / driver data (+ LLM if a key is set).
  - `course_quiz.py` — resolves a per-course quiz: offline `quiz_bank` keyed by
    the course's taxonomy skill → LLM (only if `COURSE_QUIZ_LLM=true`) → a
    generic study check. Cached per course in `course_quizzes` forever.
  - `skill_extract.py` — detect known skills from pasted résumé/bio text
    (word-boundary hits on skill names + an acronym table + a bounded LSA sweep).
  - `ai_assistant.py` — chat assistant grounded in the user's real
    profile/path/gaps/weights (Gemini / OpenAI / offline templating engine).
  - `youtube_service.py` — real YouTube Data API results when `YOUTUBE_API_KEY`
    is set, else a plain search link.
- `ml/` — `catalog` (load + index `courses.csv`), `semantic` (TF-IDF → SVD, hybrid
  retrieval, cached `.pkl`), `graph` (NetworkX prerequisite DAG), `ranker` (the
  8-factor model + adaptive per-learner weights), `planner` (path construction),
  `explain`, `engine` (orchestration).
- `data/` — `taxonomy_data.py` (20 careers, ~74 skills, 3 hand-authored skill
  quizzes), `quiz_bank.py` (~31 skill quiz sets for per-course quizzes),
  `keywords_data.py`, `courses.csv`.
- `models/schemas.py` — Pydantic request/response contracts.

## Data flow

1. **Register / login** (`POST /api/auth/register|login`) → bcrypt + JWT; an empty
   `profiles` doc is created on register.
2. **Profile** (`POST /api/onboarding/profile`, current user) upserts the
   `profiles` doc. `POST /api/onboarding/parse-resume` returns detected skills the
   user confirms client-side.
3. **Career discovery** (`POST /api/careers/discover`) persists the merged profile
   and scores every career in the taxonomy.
4. **Path generation** (`POST /api/paths/generate/{career_id}`) runs skill-gap →
   track selection → tier walk → prerequisite closure → phasing, persists to
   `learning_paths`, and returns it with any stored progress overlaid. A second
   call returns the stored path; `POST /regenerate/{career_id}` discards path +
   progress and rebuilds.
5. **Progress** — `POST /paths/progress/{career}/resource/{id}/toggle` and
   `.../milestone/{key}/toggle` mutate `path_progress.completed_resource_ids`,
   re-run `apply_progress`, and persist. `POST /paths/courses/{career}/add|remove`
   edit a milestone's resource list.
6. **Quiz** (`GET /assessments/course-quiz/{course_id}` → `POST /submit`) grades,
   writes a verified `skill_proficiencies` doc for the mapped taxonomy skill, and
   recomputes that path's `base_readiness_score`.
7. **Feedback** — marking a course done also records a `completed` event that
   nudges the learner's ranker weights (`learner_models`).
8. **Dashboard** (`POST /api/analytics/dashboard`) returns readiness, phase
   counts, hours, skill radar, `recent_courses`, and the progress-overlaid path.

## Notes

- No DB migrations — MongoDB is schemaless; new fields are additive.
- The ML semantic cache (`app/ml/cache/semantic.pkl`) is keyed by the dataset
  `(mtime, row count)` and rebuilt automatically when `courses.csv` changes.
