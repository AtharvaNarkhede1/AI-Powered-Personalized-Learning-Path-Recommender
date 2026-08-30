# API Reference

Base URL: `http://127.0.0.1:8000/api`. All learner-scoped endpoints take a `user_id` field (defaults to `"demo_user_1"` if omitted) in the request body -- there is no session/auth token required for the demo flow beyond `/auth/demo-login`.

## Auth (`/auth`)
- `POST /demo-login` -- creates/returns a demo user id.
- `POST /register`, `POST /login` -- standard email/password (present but not wired into the current UI).

## Onboarding (`/onboarding`)
- `GET /keywords/search?q=...` -- autocomplete for interests/skills.
- `POST /{user_id}` -- saves the 5-step onboarding profile.
- `GET /{user_id}` -- fetches the saved profile (or a fallback demo profile if none exists yet).

## Careers (`/careers`)
- `POST /discover` -- body: profile. Returns top 3 career matches with percentage scores, a clarification question if the top two are close, and cross-branch transition advice.
- `GET /detail/{career_id}` -- full career detail (responsibilities, required skills, day-in-the-life, what-not-to-do, etc).
- `POST /compare` -- body: `{career_ids: [...]}` (2-3), returns detail for each.
- `GET /catalog` -- full static catalog.

## Skills (`/skills`)
- `POST /analyze-gap/{career_id}` -- body: profile. Returns per-skill gap status (Mastered/Minor Gap/Major Gap/Missing), preferring quiz-verified proficiency over the self-reported estimate.

## Recommendations (`/recommendations`)
- `POST /resources` -- body: profile (+ optional `career_id`/`skill_filter`). Ranked resource list.
- `POST /feedback` -- body: `{resource_id, feedback_type, user_id, comment?}`. `feedback_type` is one of `upvote`/`downvote`/`dismiss`/`completed`; persisted per-user and affects future ranking.

## Learning Paths (`/paths`)
- `POST /generate/{career_id}` -- body: profile. Returns the persisted active path for this user+career, generating one if none exists yet.
- `POST /milestone/{career_id}/complete/{milestone_id}` -- body: profile. Marks the milestone complete, advances the next one, recomputes readiness, persists.

## Assessments (`/assessments`)
- `GET /quiz/{skill_id}` -- diagnostic quiz for a skill.
- `POST /submit` -- body: `{assessment_id, answers, user_id, career_id?}`. Grades the quiz, writes a verified skill proficiency, and adapts the user's own active path for that career (never other users' paths).

## Assistant (`/assistant`)
- `POST /chat` -- body: `{message, context_career_id?, user_id}`. Grounded in the user's real profile + active path context.

## Analytics (`/analytics`)
- `POST /dashboard?target_career_id=...` -- body: profile. Full dashboard payload: readiness %, milestone progress, real per-skill radar data, next action, active path.

## System (`/system`)
- `GET /status` -- which LLM provider is active.
- `POST /keys` -- set Gemini/OpenAI keys at runtime (session-only, not persisted to `.env`).
