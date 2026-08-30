# Architecture

## Stack

- **Backend**: FastAPI + SQLAlchemy (SQLite by default, swap `DATABASE_URL` for Postgres in production). No in-memory caches -- every learner's profile, path, feedback, and assessment history is persisted per-user in the DB (`app/db/models.py`).
- **Frontend**: React (Vite), single-page tab-based UI in `App.jsx` (no client-side routing).
- **AI/ML**: local `sentence-transformers` embeddings for semantic skill/interest/career matching (`app/services/embedding_service.py`), with an optional Gemini/OpenAI LLM layer for the chat assistant that falls back to a grounded offline rule engine if no API key is configured.

## Backend layout (`backend/app/`)

- `api/` -- FastAPI routers, one per domain: `auth`, `onboarding`, `careers`, `skills`, `recommendations`, `paths`, `assessments`, `assistant`, `analytics`, `system`.
- `services/` -- business logic, called by routers:
  - `career_engine.py` -- career discovery/matching (branch fit, semantic interest/skill similarity, experience-vs-required-level fit).
  - `skill_gap_engine.py` -- per-skill gap analysis; prefers a quiz-verified proficiency (`SkillProficiencyDB`) over the self-reported estimate when one exists.
  - `graph_engine.py` -- builds the skill prerequisite DAG (NetworkX) and topologically sorts target skills.
  - `path_generator.py` -- assembles the milestone roadmap from the sorted skill list + ranked resources.
  - `recommendation_engine.py` -- two-stage resource retrieval + multi-factor ranking (rating, semantic relevance, format/difficulty fit, upvote/downvote feedback).
  - `adaptive_engine.py` / `readiness_calculator.py` -- readiness scoring; `readiness_calculator` is the source of truth, recomputed from real skill-gap data after a quiz.
  - `what_not_to_do_engine.py` -- personalized pitfall warnings.
  - `embedding_service.py` -- local semantic similarity (falls back to substring/token overlap if `sentence-transformers` isn't installed, so the app never hard-crashes on a missing optional dependency).
  - `youtube_service.py` -- real YouTube Data API v3 results when `YOUTUBE_API_KEY` is set; otherwise a plain search link (no fabricated ratings).
  - `ai_assistant.py` -- chat assistant, grounded in the user's real profile/career/skill-gap data (Gemini / OpenAI / offline rule engine).
  - `path_store.py` -- DB persistence helpers (profile upsert, active-path read/write, feedback history) used by the routers instead of module-level caches.
- `data/taxonomy_data.py` -- the curated static catalog: engineering branches, careers, skills (with YouTube resources), and diagnostic quizzes. This is hand-authored content, not scraped.
- `db/models.py` -- SQLAlchemy models: `User`, `LearnerProfileDB`, `SkillProficiencyDB`, `LearningPathDB`/`MilestoneDB`, `UserFeedbackDB`, `AssessmentSubmissionDB`, `ChatMessageDB`.
- `models/schemas.py` -- Pydantic request/response contracts.

## Data flow

1. **Onboarding** (`POST /api/onboarding/{user_id}`) persists a `LearnerProfileDB` row.
2. **Career discovery** (`POST /api/careers/discover`) scores every career in the static catalog against the profile (branch/interest/skill/experience fit) and returns top matches + clarification question if ambiguous.
3. **Path generation** (`POST /api/paths/generate/{career_id}`) runs skill-gap analysis -> topological sort -> resource ranking -> milestone grouping, then persists the result. A second call for the same user+career returns the persisted path instead of regenerating (so completed-milestone progress isn't lost).
4. **Quiz submission** (`POST /api/assessments/submit`) grades the quiz, writes a verified `SkillProficiencyDB` row, and recomputes readiness for that user's own active path only.
5. **Feedback** (`POST /api/recommendations/feedback`) is persisted per-user and actually changes future resource ranking (upvote/downvote adjust the ranking score).

## Known limitations / next steps

See the improvement plan discussed with the maintainer: the static catalog (9 careers, ~45 skills after the taxonomy gap-fill) could be expanded via O*NET/ESCO; course *content* beyond YouTube (Coursera/edX) has no free public catalog API and isn't integrated.
