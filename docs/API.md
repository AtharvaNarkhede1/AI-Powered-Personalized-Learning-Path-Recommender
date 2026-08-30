# API Reference

Base URL: `http://127.0.0.1:8000/api`. Interactive docs at `/docs`.

**Auth**: every endpoint below except `/auth/register`, `/auth/login`,
`/careers/detail`, `/careers/compare`, `/assessments/quiz/{skill_id}` and
`/system/status` requires an `Authorization: Bearer <jwt>` header. The learner is
identified by the token — there is no `user_id` in request bodies or paths.

## Auth (`/auth`)
- `POST /register` — `{email, password, full_name}` → `{access_token, user_id, email, full_name}`. Creates the user + an empty profile.
- `POST /login` — `{email, password}` → same shape. `401` on a bad password.
- `GET /me` → `{user_id, email, full_name}`.

## Onboarding / profile (`/onboarding`)
- `GET /keywords/search?q=` — interest/skill autocomplete.
- `GET /profile` — the signed-in user's profile (created empty if none).
- `POST /profile` — body: `ProfileOnboardingRequest`. Upserts the profile.
- `POST /parse-resume` — `{text, exclude[]}` → `{detected_skills: [{name, confidence, source}]}`. Suggestions only; the client confirms before adding.

## Careers (`/careers`)
- `POST /discover` — body: profile. Persists the merged profile, returns top-3 matches (percentage + sub-scores + missing/transferable skills), an optional clarification question, and cross-branch advice.
- `GET /detail/{career_id}` — full taxonomy entry.
- `POST /compare` — `{career_ids: [2–3]}` → detail for each.
- `GET /catalog` — all careers by branch.

## Skills (`/skills`)
- `POST /analyze-gap/{career_id}` — body: profile. Per-skill `current → required`, gap delta, status, prerequisite warnings, overall readiness %. Prefers quiz-verified proficiency.

## Recommendations (`/recommendations`)
- `POST /resources` — `{goal_text?, career_id?, limit}`. Ranked course list with per-factor `factor_contributions`. Uses the stored profile.
- `POST /feedback` — `{resource_id, feedback_type, comment?}`. `feedback_type` ∈ `upvote | downvote | dismiss | completed`; nudges the learner's ranker weights.
- `GET /model` — the learner's current ranker weights + deltas from default.

## Learning paths (`/paths`)
- `POST /generate/{career_id}` — body: profile. Returns the stored path (progress overlaid) or builds & persists a new one; sets it as the profile's target career.
- `POST /regenerate/{career_id}` — discard path + progress, rebuild fresh.
- `POST /progress/{career_id}/resource/{resource_id}/toggle` — mark a course done/pending. Recomputes milestone status + readiness. A completion also records a `completed` feedback event.
- `POST /progress/{career_id}/milestone/{milestone_key}/toggle` — mark a whole phase done/pending.
- `POST /courses/{career_id}/add` — `{course_id, milestone_key?}`. Resolve the catalog course and append it to a phase (defaults to the phase matching the course tier).
- `POST /courses/{career_id}/remove` — `{resource_id, milestone_key}`.
- `GET /explanation/{career_id}` → `{overview, phases: [{milestone_key, title, explanation}]}`.

All path endpoints return the full `LearningPathResponse` (`ResourceItem.completed`
reflects stored progress; `job_readiness_score` = `base_readiness_score` plus a
share of the remaining gap proportional to completed hours).

## Assessments (`/assessments`)
- `GET /quiz/{skill_id}` — a hand-authored skill quiz (`QUIZZES_DATABASE`).
- `GET /course-quiz/{course_id}` — a 3–4 question quiz for a specific course. Resolved from the offline bank → LLM (only if `COURSE_QUIZ_LLM=true`) → a generic study check, then cached forever.
- `POST /submit` — `{assessment_id, answers, career_id?, course_id?}`. Handles both quiz kinds (`cq_<course_id>` ids for course quizzes). Grades, writes a verified `skill_proficiencies` doc for the mapped skill, and recomputes that path's base readiness.

## Assistant (`/assistant`)
- `POST /chat` — `{message, context_career_id?}`. Grounded in the user's real profile, progress-overlaid path, skill gaps, and ranker weights. Uses Gemini/OpenAI if a key is set, else the offline templating engine. Replies may contain markdown.

## Analytics (`/analytics`)
- `POST /dashboard?target_career_id=` — readiness %, phase counts, hours logged/total, months remaining, `next_action`, `skill_radar_data`, `recent_courses`, `active_path`, and `has_path` (`false` before a career is chosen).

## System (`/system`)
- `GET /status` — app name/version + which LLM provider is active (read-only; keys are `.env` only).
