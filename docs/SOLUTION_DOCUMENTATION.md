# Solution Documentation — AI-Powered Personalized Learning Path Recommender

**Project:** Career PathFinder
**Type:** Full-stack web application (React SPA + FastAPI service + MongoDB Atlas)
**Core idea:** Turn a short learner profile into a career match, a real skill-gap
analysis, and a **prerequisite-ordered, explainable learning roadmap** of ranked
courses that the learner can track course-by-course, with a grounded AI assistant
on top.

---

## 1. Problem Understanding

### 1.1 The problem
Engineering students and early-career switchers face three compounding problems
when trying to become job-ready:

1. **Career ambiguity.** They don't know which roles actually fit their branch,
   interests, and current skills — and generic "top 10 careers" lists ignore
   their starting point.
2. **Unknown skill gaps.** Even after picking a target role, they can't tell
   *which specific skills* they are missing and *how far* they are from the level
   the role needs.
3. **Unstructured learning.** Course marketplaces return thousands of results
   ranked by popularity or marketing spend, with no notion of *order*. Learners
   routinely jump into advanced material without prerequisites, collect
   completion certificates without shipping projects, and lose motivation because
   there is no visible finish line.

### 1.2 What a good solution must do
- Match a learner to careers using **their** branch, interests, skills, and
  experience — not population averages.
- Quantify the gap between "what the learner has" and "what the role needs" at the
  individual-skill level, and prefer **verified** proficiency (quiz results) over
  self-reported estimates.
- Produce a **sequenced** path: foundations first, each step only assuming what
  earlier steps taught.
- **Explain every decision** — why this course, why here, what it unlocks — so the
  learner trusts and follows the plan.
- Work **offline / zero-cost by default** (no mandatory paid LLM API), while
  optionally using an LLM when a key is available.
- Persist everything server-side so progress survives across devices and sessions.

### 1.3 Constraints and assumptions
- No licensed commercial course dataset is available → the catalog is a
  **synthetic but internally consistent** ~18,000-row dataset with realistic
  tracks, tiers, prerequisites, ratings, and provider mix.
- LLM access is optional and rate-limited → all "intelligence" that the product
  depends on must run locally with classical ML.
- Target users are non-experts → explanations must be plain-language, and the
  onboarding must accept free-text ("paste your résumé / describe your goal").

---

## 2. Solution Approach

The system is a pipeline of specialized engines, each independently testable, all
orchestrated behind a REST API:

```
Profile (branch, interests, skills, experience, hours/week, timeline)
   │
   ├─▶ Career Engine ───────▶ Top-3 career matches (+ clarification, cross-branch advice)
   │
   ├─▶ Skill-Gap Engine ────▶ Per-skill delta, status tags, prerequisite warnings
   │
   └─▶ ML Recommendation Engine
          ├─ Semantic space (TF-IDF + Truncated SVD / LSA)
          ├─ Prerequisite graph (DiGraph over branch×track×tier "rungs")
          ├─ Multi-factor Ranker (8 weighted factors, per-learner weights)
          ├─ Planner (track selection → tier walk → prereq closure → phasing)
          └─ Explainer (factor contributions → plain-language "why")
                 │
                 ▼
        Learning Path: 4 phases → milestones → ordered courses
                 + per-milestone project, diagnostic quiz, YouTube extras
                 │
                 ▼
        Progress tracking → readiness recompute → next-action
                 │
                 ▼
        Grounded AI Assistant (answers ONLY from this learner's real data)
```

**Design principles**

| Principle | How it shows up |
|---|---|
| Explainable by construction | The ranker returns normalized per-factor *contributions* for every course; the explainer turns them into sentences. Nothing is a black box. |
| Deterministic core, optional LLM | TF-IDF/SVD/graph are deterministic and cached. LLMs only *rephrase* grounded facts (assistant, phase explanations) or generate quiz questions — never invent path structure. |
| Personalization as feedback loop | Thumbs-up/down and course completion nudge that learner's 8 ranker weights and track/provider affinities, stored in `learner_models`. |
| Server-authoritative state | The React client holds only a JWT; every screen refetches from MongoDB. |

---

## 3. System Architecture

### 3.1 High-level

```
┌────────────────────┐     HTTPS/JSON      ┌──────────────────────────┐
│  React 18 SPA       │ ◀────────────────▶ │  FastAPI (Uvicorn)       │
│  Vite, react-router │   Bearer JWT       │  app/api/*  routers      │
│  Recharts, context  │                    │  app/services/*  engines │
└────────────────────┘                    │  app/ml/*  ML pipeline   │
                                          │  app/db/*  repository    │
                                          └───────────┬──────────────┘
                                                      │ pymongo (TLS)
                                              ┌───────▼─────────┐
                                              │  MongoDB Atlas  │
                                              │  9 collections  │
                                              └─────────────────┘
   Optional outbound: Google Gemini / OpenAI (chat, quiz gen), YouTube Data API v3
```

### 3.2 Backend layout (`backend/app/`)

| Package | Responsibility |
|---|---|
| `main.py` | FastAPI app, CORS, router registration, startup hook (Mongo ping + index creation + ML engine warm-up), global `PyMongoError → 503` handler. |
| `core/config.py` | Env-driven `Settings` (Mongo URI builder with credential injection, JWT config, LLM/YouTube keys, CSV & cache paths, CORS origins). |
| `core/security.py` | bcrypt password hashing, JWT create/verify, `get_current_user` dependency. |
| `api/` | 10 routers: `auth`, `onboarding`, `careers`, `skills`, `recommendations`, `paths`, `assessments`, `assistant`, `analytics`, `system`. |
| `services/` | Business engines: `career_engine`, `skill_gap_engine`, `ai_assistant`, `path_explain`, `progress`, `skill_extract`, `intake_parse`, `course_quiz`, `youtube_service`. |
| `ml/` | `catalog` (CSV loader + indices), `semantic` (TF-IDF+SVD), `graph` (prereq DiGraph), `ranker` (8-factor scorer), `planner` (path builder), `explain` (rationale), `engine` (facade + learner-model adaptation). |
| `data/` | `courses.csv` (~17.9k rows), `taxonomy_data.py` (careers, skills, quizzes DB), `quiz_bank.py` (per-skill MCQ bank), `keywords_data.py` (autocomplete vocab). |
| `db/` | `mongo.py` (client, collections, index definitions), `repository.py` (all persistence — users, profiles, paths, progress, learner models, assessments, proficiencies, feedback, course quizzes). |
| `models/schemas.py` | ~40 Pydantic request/response models — the API contract. |

### 3.3 Data model (MongoDB collections)

| Collection | Key | Holds |
|---|---|---|
| `users` | `email` (unique) | credentials, full name |
| `profiles` | `user_id` (unique) | branch, interests, known skills, experience, hours/week, timeline, target career |
| `learning_paths` | `user_id + career_id` (unique) | full generated roadmap (milestones, resources, projects, quizzes, warnings, base readiness) |
| `path_progress` | `user_id + career_id` (unique) | list of completed resource IDs |
| `learner_models` | `user_id` (unique) | personalized ranker weights, track/provider affinities, update count |
| `skill_proficiencies` | `user_id + skill_id` (unique) | verified proficiency + evidence source |
| `assessments` | `user_id` | quiz submissions and scores |
| `user_feedback` | `user_id` | thumbs up/down / completed / dismissed events |
| `course_quizzes` | `course_id` (unique) | cached generated/bank concept-check quizzes |

### 3.4 Frontend (`frontend/src/`)
- `App.jsx` — routes: public (`/`, `/login`, `/register`) and guarded `/app/*`
  (`dashboard`, `profile`, `discover`, `courses`, `roadmap`) behind `RequireAuth`.
- `context/AuthContext` + `AuthContext` — JWT in `localStorage`, global
  `auth:logout` event on any 401 to an authenticated endpoint.
- `context/AppDataContext` — shared profile / career / path state.
- `api/client.js` — single typed fetch wrapper; attaches Bearer token; maps 503 to
  a friendly "database unavailable" message.
- Components: `IntakeBox` / `ResumeImport` (free-text onboarding), `KeywordInput`
  (autocomplete), `QuizModal`, `AssistantWidget`.
- `Recharts` for the dashboard skill radar and progress charts.

### 3.5 Request lifecycle (example: generate roadmap)
1. `POST /api/paths/generate/{career_id}` with the profile + Bearer JWT.
2. `get_current_user` decodes the JWT → user doc.
3. Profile is upserted; target career is set.
4. If a path already exists → return it with progress overlaid (`apply_progress`).
5. Else `engine.build_path(profile, career_id, user_id)`:
   - build ranking context (goal text, skill-gap terms, learner weights, target tier, branch preferences);
   - pick 3–6 skill tracks whose semantic centroid is closest to the goal vector, forcing in the gap-skill tracks + a portfolio track;
   - walk tiers 0→3 per track, choosing the best course *variant* per rung;
   - close prerequisites transitively via the graph;
   - collapse to one course per (track, tier), topologically order by prereq depth;
   - group into 4 phases → milestones (split if a phase has >7 courses);
   - attach a project, a matched diagnostic quiz, and YouTube extras per milestone;
   - compute base job-readiness from the skill gap.
6. Path is persisted to `learning_paths` and returned.

---

## 4. AI / ML Techniques Used

### 4.1 Semantic course representation — TF-IDF + Latent Semantic Analysis
- Each course is flattened into a **weighted document**: title×3, track×3,
  skills×2, career paths×2, tools/branch/sectors/description×1
  (`catalog._build_doc`).
- `TfidfVectorizer(ngram_range=(1,2), sublinear_tf, min_df=3, max_df=0.6,
  max_features=24000, stop_words="english")`.
- `TruncatedSVD(n_components=240)` reduces the TF-IDF matrix to a dense 240-dim
  **LSA space**; vectors are L2-normalized so dot product = cosine.
- **Hybrid similarity** (`hybrid_to_courses`): `0.55 × LSA cosine + 0.45 ×
  raw TF-IDF cosine` — LSA captures synonyms ("neural nets" ≈ "deep learning"),
  raw TF-IDF stops short lexical queries from over-generalizing.
- **Pseudo-relevance feedback** for short queries (`engine._query_sims`): take the
  skill tokens of the top-10 initial hits, fold them back into the query, re-score,
  and blend — so "cybersecurity" also pulls in networking/crypto courses.
- The fitted vectorizer + SVD + matrices are **cached to disk** (`joblib`, keyed on
  CSV mtime + row count) so warm-up is instant after the first run.
- The same space powers non-ML-looking features: career matching, résumé skill
  extraction, and skill-name → catalog-track mapping all call
  `text_similarity` / `best_text_similarity` instead of substring matching.

### 4.2 Prerequisite graph — directed acyclic "rung" graph
- A **rung** = `(branch, track, tier)` where tier ∈ {Beginner 0, Intermediate 1,
  Advanced 2, Capstone 3}.
- Edges come from (a) each course's `prerequisite_course_title` resolved to a rung,
  and (b) implicit tier chains (tier *t-1* → tier *t* within a track).
- Cycles are broken deterministically (remove the edge into the highest tier of any
  detected cycle) → guaranteed **DAG**.
- `depth[rung]` = longest path from a root; used to order the final plan.
- The ranker uses it for the `prereq_ready` factor; the planner uses it for
  transitive prerequisite closure.

### 4.3 Multi-factor learning-to-rank (linear, explainable)
`ranker.py` scores every candidate course on **8 factors**, each in [0, 1]:

| Factor | Meaning |
|---|---|
| `goal_fit` | pool-normalized hybrid similarity of the course to the goal text |
| `skill_gain` | how much of the weighted skill-gap the course covers (via gap-term token match or gap-vector similarity) |
| `branch_fit` | 1.0 home branch · 0.82 career-compatible branch · 0.62 neutral · 0.35 off-branch |
| `level_fit` | asymmetric penalty for being below (mild) / above (steep) the learner's target tier |
| `quality` | Bayesian-shrunk rating: `(v·r + 150·global_mean) / (v + 150)` mapped to [0,1] |
| `prereq_ready` | fraction of the rung's predecessors already satisfied |
| `effort_fit` | course length vs. the learner's weekly-hours budget |
| `format_pref` | match to preferred format (video / lab / project-based) |

- **Score** = weighted mean of factors (weights sum-normalized) + `0.05 ×`
  track/provider affinity bonus.
- **Contributions** = each factor's share of the weighted score → this is what the
  explainer and the assistant cite ("goal match 41% · skill-gap coverage 22%").
- Default weights favor `goal_fit` (0.26) and `skill_gain` (0.18); if the learner
  has no branch signal, `branch_fit`'s weight is folded into `goal_fit`.

### 4.4 Personalization — online weight adaptation
`engine.record_feedback`: on upvote (+1.0), completed (+0.6), downvote (−1.0),
dismiss (−0.6), multiply each weight by `(1 + sign × 0.12 × factor_share)` using
the **stored contributions of the course the learner reacted to**, then
re-normalize. Track/provider **affinities** move by `±0.15` (clamped to [−1, 1]).
State is persisted per user in `learner_models` and reloaded into every future
ranking context. This is a lightweight bandit-style preference learner — the
learner's own behavior reshapes what "a good course" means for them.

### 4.5 Path planner — constrained sequencing
1. **Track selection**: score every `(branch, track)` centroid against the goal
   vector; subtract 0.15 for off-preferred-branch; force in tracks named by the
   top skill gaps + a `"<career> portfolio"` track; cap count by
   `capacity // 70` (capacity = weekly_hours × timeline_weeks), clamped to 3–6.
2. **Tier walk**: for each track, tiers below the learner's stated level are
   *waived* (marked satisfied, with an audit note); from the start tier up, pick
   the best-ranked course variant for that rung.
3. **Prerequisite closure**: BFS over graph predecessors, adding the best variant
   for any uncovered prerequisite rung.
4. **Dedup & order**: keep the highest-scoring course per `(track, tier)`, sort by
   `(prereq depth, tier, −score)`.
5. **Phasing**: map present tiers → 4 phases (Foundations, Applied, Advanced,
   Capstone); MMR-style diversification avoids near-duplicate rows.

### 4.6 Diversification — Maximal Marginal Relevance
`engine._mmr`: walk the ranked list; skip any course whose LSA-space cosine to an
already-picked course exceeds 0.93 — so recommendations aren't 10 near-identical
"Intro to X" rows. A one-course-per-track filter runs first.

### 4.7 Career matching
Weighted blend: `branch (0.30) + interest (0.35) + skill (0.25) + goal-level
(0.10)`, where interest score is the mean semantic similarity of each interest to
the career's text, and skill score is the fraction of required skills the learner
semantically matches (≥ 0.55). If the top two careers are within 7 points, a
**clarification question** is generated; if the top match is off-branch, a
**cross-branch bridge advice** string names the 2 critical bridge skills.

### 4.8 Skill-gap analysis
For each required skill of the target role: prefer a **quiz-verified proficiency**;
else derive `current_level` from experience baseline (0.25 / 0.5 / 0.75) boosted
by semantic match to a known skill. `gap_delta = max(0, required − current)`,
bucketed into Mastered / Minor Gap / Major Gap / Missing. Overall readiness =
`Σ min(current, required) / Σ required`. Prerequisite skills below 0.3 raise
explicit warnings.

### 4.9 Résumé / free-text intake parsing
`skill_extract` — word-boundary regex over the 100+ skill taxonomy plus an alias
map (`pytorch → Deep Learning & PyTorch`, `k8s → Kubernetes`, …); if fewer than 6
hits, fall back to semantic similarity (≥ 0.6) against the résumé snippet.
`intake_parse` — rule tables extract status, experience, branch, weekly hours,
and timeline from natural-language onboarding text, plus a "want to learn X"
pattern for custom keywords. Everything is a **suggestion the user confirms**.

### 4.10 Diagnostic quizzes
`course_quiz` — match a course's track/title to a curated **per-skill MCQ bank**
(fuzzy set-overlap ≥ 0.5); if no bank match and `COURSE_QUIZ_LLM=true` + a key is
set, generate 4 validated MCQs via Gemini/OpenAI (strict JSON schema validation);
else fall back to a generic bank. Results are cached in `course_quizzes` and feed
back into `skill_proficiencies` → skill gap → readiness.

### 4.11 Grounded AI assistant
`ai_assistant` builds a **grounding block** from the learner's real profile,
path, milestones (with per-course rationale), skill gaps, and personalized ranker
weights. Two modes:
- **LLM mode** (if `GEMINI_API_KEY` / `OPENAI_API_KEY` set): a strict system
  prompt — *"answer ONLY from the context, never invent course names, numbers or
  timelines"* — with the grounding block; the deterministic engine still supplies
  the `referenced_resources` / `suggested_followups`.
- **Offline mode** (default): intent classifier (`why_path`, `next_step`,
  `timeline`, `weak_areas`, `avoid`, `day`, `projects`, `compare`) → templated
  answer assembled from the same grounding data, citing real course titles and
  gap numbers.

### 4.12 YouTube enrichment
`youtube_service` — if `YOUTUBE_API_KEY` is set: search playlists + long-form
videos, pull view/like stats, synthesize a rating from the like/view ratio, sort
by views, return the top 3 (LRU-cached). Otherwise return a deep-link to
YouTube's playlist search results. Never raises.

### 4.13 External Integrations & APIs (consolidated)

All third-party APIs are **strictly optional**. The product delivers its full core
value — career match, skill-gap analysis, prerequisite-ordered roadmap,
explanations, progress tracking, offline assistant, and bank-based quizzes — with
**no API keys at all**. External APIs only *enhance* specific touch-points, and
each one degrades gracefully to a built-in fallback.

| API | Used by | What it adds | Model / endpoint | Behaviour when key is absent |
|---|---|---|---|---|
| **Google Gemini API** (`google-generativeai`) | AI assistant (`services/ai_assistant.py`), per-phase path explanations (`services/path_explain.py`), diagnostic quiz generation (`services/course_quiz.py`) | Natural-language rephrasing of grounded facts; free-text answers to learner questions; auto-authored 4-question course quizzes | Tries `gemini-flash-latest`, then `gemini-2.5-flash` (and `gemini-3.5-flash` for the assistant), in order; falls through on any error | Falls back to the **grounded offline engine** (intent-classified templated answers) / template phase explanations / the curated MCQ bank |
| **OpenAI API** (`openai`) | Same three features, as the **secondary** LLM provider (used only if there is no Gemini key or Gemini fails) | Same as above | `gpt-4o-mini`, `chat.completions`, temperature 0.4–0.5, JSON-object response format for quizzes | Same offline fallbacks as Gemini |
| **YouTube Data API v3** (`requests`) | Milestone "YouTube extras" (`services/youtube_service.py`, called from `ml/engine.youtube_extras`) | Ranked real playlists + long-form course videos per milestone skill, sorted by view count, with a rating synthesized from the like/view ratio | `GET /youtube/v3/search` (playlist + video) and `GET /youtube/v3/videos` (`snippet,contentDetails,statistics`), 6 s timeout, LRU-cached (512 entries) | Returns a **deep-link** to YouTube's filtered playlist-search results for the skill — still useful, just not ranked |

**Provider selection.** `DEFAULT_LLM_PROVIDER` (`auto` / `gemini` / `openai`) plus
the presence of `GEMINI_API_KEY` / `OPENAI_API_KEY` decides the active mode.
`GET /api/system/status` reports it live as `"Google Gemini (live)"`,
`"OpenAI (live)"`, or `"Grounded offline engine"`, along with the three
`*_key_configured` booleans and `youtube_key_configured`.

**The AI assistant in detail** (`/api/assistant/chat`):

1. The endpoint loads the learner's real profile, active path (with progress
   overlaid), skill-gap analysis, and personalised ranker weights.
2. `_collect_grounding` + `_grounding_text` assemble a **grounding block**: branch,
   experience, weekly hours, known skills; target career with day-in-the-life,
   hard realities and "what not to do"; current readiness %, estimated
   weeks/months; every milestone with its status and course titles; the planner's
   rationale for the first courses; the six largest skill gaps with have-vs-need
   numbers; and which ranking factors this learner's model currently leans on.
3. **If an LLM key is set:** Gemini (or OpenAI) is called with a locked system
   prompt — *"Answer ONLY from the learner context below. Do NOT invent course
   names, numbers, timelines, or facts. If the context doesn't contain the answer,
   say so."* — plus the grounding block. The deterministic engine still supplies
   the `referenced_resources` and `suggested_followups` so every citation stays
   real.
4. **If no key (default):** an intent classifier routes the question to one of
   `why_path`, `next_step`, `timeline`, `weak_areas`, `avoid`, `day`, `projects`,
   `compare`, or `default`, and a templated answer is assembled from the *same*
   grounding data — citing the learner's actual course titles and gap figures.
5. Either way the response is the same `ChatResponse` shape: `reply`,
   `suggested_followups`, `referenced_resources`, `referenced_warnings`.

**Why grounded-only.** LLMs are never allowed to generate path structure,
ordering, timelines, or readiness numbers — those come exclusively from the
deterministic ML pipeline. LLM output is limited to (a) rephrasing facts already
in the grounding block and (b) quiz questions, which are JSON-schema validated
(question text, ≥ 3 options, valid correct-index) before being stored or served.
This keeps answers trustworthy and the product fully functional offline.

**Data sent externally.** Only when a key is configured: the grounding block
(learner's branch, experience, skills, career, path, gaps — never email, password,
or raw credentials) goes to the chosen LLM; skill/course names go to YouTube.
Nothing is sent to any external service in the default no-key configuration.

---

## 5. Key Features and Workflows

### 5.1 Feature list

| Feature | Endpoint(s) | Engine |
|---|---|---|
| Email/password auth (JWT, bcrypt) | `/api/auth/register`, `/login`, `/me` | `core/security` |
| Profile + résumé/intake auto-fill | `/api/onboarding/*` | `skill_extract`, `intake_parse` |
| Career discovery (top-3 + clarification + cross-branch) | `/api/careers/discover`, `/detail/{id}`, `/compare`, `/catalog` | `career_engine` |
| Skill-gap analysis (verified > self-reported) | `/api/skills/analyze-gap/{career_id}` | `skill_gap_engine` |
| Explainable course recommendations | `/api/recommendations/resources` | `ml.engine` |
| Feedback → personalized re-ranking | `/api/recommendations/feedback`, `/model` | `ml.engine.record_feedback` |
| Prerequisite-ordered roadmap (4 phases) | `/api/paths/generate/{id}`, `/regenerate/{id}` | `ml.engine.build_path` |
| Course-by-course + phase progress tracking | `/api/paths/progress/...` | `progress` |
| Add / remove courses from the roadmap | `/api/paths/courses/{id}/add`\|`/remove` | `ml.engine` + `progress` |
| Per-phase plain-language explanation | `/api/paths/explanation/{career_id}` | `path_explain` |
| Diagnostic quizzes (bank / LLM / generic) | `/api/assessments/quiz/{skill}`, `/course-quiz/{course}`, `/submit` | `course_quiz` |
| Grounded AI assistant | `/api/assistant/chat` | `ai_assistant` |
| Dashboard metrics + skill radar | `/api/analytics/dashboard` | `analytics` + all engines |
| System / LLM-mode status | `/api/system/status` | — |

### 5.2 Primary workflow — from sign-up to job-readiness

```
1. Register / sign in ─────────────▶ JWT stored client-side
2. Complete profile
      • paste résumé → skills auto-detected (confirm)
      • describe goal in free text → hours, timeline, branch parsed
3. "Find My Career" ───────────────▶ top-3 matches, %-scored, with reasons
      • if top-2 within 7 pts → answer a clarification question
      • if off-branch → cross-branch bridge advice
4. Select a career ────────────────▶ Skill-gap analysis runs
      • per-skill: have X% vs need Y%  → Mastered / Minor / Major / Missing
5. Roadmap generated ──────────────▶ 4 phases → milestones → ordered courses
      • each course: "why now", "unlocks", factor contributions
      • each milestone: portfolio project + diagnostic quiz + YouTube extras
      • "what NOT to do" warnings from role data + profile heuristics
6. Track progress
      • tick courses done → phase auto-completes → readiness % rises
      • take a diagnostic quiz → verified proficiency → gap & readiness recompute
      • thumbs-up/down a recommendation → your ranker weights adapt
      • add/remove courses; regenerate for a clean slate
7. Ask the assistant ──────────────▶ "Why is my path ordered this way?",
      "What should I start today?", "How long until I'm job-ready?"
      answered only from your real data.
```

### 5.3 Adaptation loop (what makes it "personalized")
`completion / upvote / downvote / dismiss` → `record_feedback` → per-learner
weight & affinity update in `learner_models` → every subsequent recommendation and
roadmap regeneration uses the updated model → `/recommendations/model` exposes the
current weights and their delta from default so the learner can see how their
profile has shifted.

---

## 6. System Working — Internals Reference

### 6.1 Startup (`main.py::_startup`)
1. `mongo.ping()` — verify Atlas connectivity (TLS via `certifi` for `mongodb+srv`).
2. `mongo.ensure_indexes()` — create the 9 unique/compound indexes (idempotent).
3. `engine.warm()` — load CSV → build catalog & indices → load/fit semantic space
   (from `joblib` cache if fresh) → build prereq graph → instantiate ranker &
   planner. Logs course count, rung count, unresolved-prereq count. Failures are
   caught so the API still boots (engine warms lazily on first use).

### 6.2 Course catalog (`ml/catalog.py`)
- Reads `courses.csv` (16 columns: id, branch, track, title, difficulty, provider,
  format, description, skills_taught, tools_covered, prerequisite_course_title,
  estimated_hours, rating, num_reviews, career_paths, industry_sectors).
- Coerces numerics, fills NA, builds: `variant_index` (rung → rows),
  `track_index`, `title_index`, `career_index`, and vocab lists.
- `quality` = Bayesian-shrunk rating (prior weight 150) → [0, 1].
- `tiers` = difficulty mapped to 0–3.

### 6.3 Ranking context (`engine._context`)
Assembles: goal text (`interpret_profile` — career title + responsibilities +
required skills + interests + branch + focus skills), goal vector, per-course goal
similarities (with PRF expansion), gap terms & gap-vector similarities, learner
weights & affinities, target tier, preferred/ career/ home branches, weekly hours,
preferred format.

### 6.4 Readiness & next-action (`services/progress.py`)
- `apply_progress` overlays completed-resource IDs onto a stored path: sets
  per-resource `completed`, per-milestone `status` (completed / in_progress /
  not_started, with the first not-started bumped to in_progress), recomputes
  `job_readiness_score = base + (100 − base) × (done_hours / total_hours)`, and
  rebuilds `next_action` (continue next incomplete course, or "build capstone").
- `base_readiness_score` is set from the skill gap at generation time and updated
  after each quiz submission.

### 6.5 Explanation generation (`ml/explain.py`, `services/path_explain.py`)
- `explain()` — take factor contributions ≥ 0.08, name the top 2
  ("Recommended because it matches your goal and closes your skill gaps"), and
  surface caveats when a factor is < 0.35 ("some prerequisites aren't complete
  yet").
- `path_explain` — per-phase paragraph from target skills + lead course rationale
  + top ranking factors + what the phase unlocks; optionally rephrased by an LLM
  under a "use ONLY the context" prompt.

### 6.6 Error handling & resilience
- Any `PyMongoError` → HTTP 503 with a friendly message (global handler); the
  React client maps 503 to a ret' banner.
- Every optional integration (LLM, YouTube, verified proficiency lookup, learner
  model load) is wrapped so a failure degrades gracefully to the deterministic
  path.
- LLM calls try multiple model names in sequence and fall back to the offline
  engine on any exception.
- 401 on an authenticated request → global `auth:logout` event → redirect to login
  (login/register 401s are excluded so bad credentials don't force a logout).

### 6.7 Security
- Passwords: bcrypt. Tokens: HS256 JWT, 7-day expiry, `SECRET_KEY` from env.
- Every non-public endpoint depends on `get_current_user`.
- CORS restricted to configured origins.
- Mongo credentials injected into the URI at runtime (never committed); TLS CA
  bundle via `certifi`.
- LLM prompts are constrained to grounded context to prevent fabrication; quiz
  JSON from LLMs is schema-validated before use.

### 6.8 Configuration (`backend/.env`)

| Var | Purpose | Default |
|---|---|---|
| `MONGODB_URI` / `MONGODB_USERNAME` / `MONGODB_PASSWORD` / `MONGODB_DB` | Atlas connection | `mongodb://localhost:27017`, db `pathfinder` |
| `SECRET_KEY` | JWT signing | dev fallback |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` | optional LLM for assistant + quiz gen | unset → offline engine |
| `DEFAULT_LLM_PROVIDER` | `auto` / `gemini` / `openai` | `auto` |
| `YOUTUBE_API_KEY` | ranked YouTube extras | unset → search deep-link |
| `COURSE_QUIZ_LLM` | allow LLM quiz generation | `false` |
| `COURSES_CSV` / `ML_CACHE_DIR` | dataset & cache paths | under `backend/app/` |
| `CORS_ORIGINS` | allowed frontends | localhost:5173/3000 |

### 6.9 Running locally
```
# 1. MongoDB — local mongod OR an Atlas URI in backend/.env
# 2. Backend
cd backend
python -m venv venv && venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload                       # http://127.0.0.1:8000  (docs at /docs)
# 3. Frontend
cd frontend
npm install
npm run dev                                          # http://localhost:5173
```

### 6.10 Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, react-router-dom, Recharts, Context API |
| Backend | FastAPI 0.115, Uvicorn, Pydantic 2 |
| ML | scikit-learn 1.5 (TF-IDF, TruncatedSVD), NumPy, SciPy, pandas, NetworkX, joblib |
| Persistence | MongoDB Atlas via PyMongo 4.9 (+ dnspython, certifi) |
| Auth | bcrypt, PyJWT |
| Optional | google-generativeai, openai, YouTube Data API v3 |

---

## 7. Challenges Faced and How They Were Solved

| # | Challenge | Resolution |
|---|---|---|
| 1 | **No commercial course dataset.** | Built a synthetic ~17.9k-row catalog with internally consistent branches, tracks, 4 difficulty tiers, realistic prerequisite chains, provider mix, and shrunk ratings — rich enough for meaningful ML without licensing. |
| 2 | **Short queries over-generalize** in pure LSA (e.g. "data pipeline" ≈ "test pipeline"). | Hybrid similarity (0.55 LSA + 0.45 raw TF-IDF) plus pseudo-relevance-feedback query expansion for queries under 8 tokens. |
| 3 | **Prerequisite data forms cycles** (course A needs B, B's tier implies A). | Model prerequisites at the `(branch, track, tier)` rung level, add implicit tier edges, then deterministically break every cycle by dropping the edge into the highest tier — guaranteeing a DAG for topological ordering. |
| 4 | **Unresolved prerequisite titles** (a listed prereq course doesn't exist). | Resolve to the same-track lower tier as a fallback; log the count of unresolved edges at warm-up for observability. |
| 5 | **Recommendations were 10 near-identical "Intro to X" rows.** | One-course-per-track filter + MMR de-duplication in the 240-dim LSA space (cosine > 0.93 → skip). |
| 6 | **"Explainable AI" can't be bolted on afterward.** | The ranker emits normalized per-factor *contributions* as a first-class output; the explainer and assistant consume them directly — the explanation is derived from the exact math that produced the score. |
| 7 | **LLMs hallucinate course names, timelines, and numbers.** | Grounded-only architecture: LLMs receive a strict "answer only from this context" prompt and never generate path structure; a full deterministic offline engine produces the same answers when no key is set; LLM quiz output is JSON-schema-validated. |
| 8 | **Self-reported skill levels are unreliable.** | Diagnostic quizzes write *verified* proficiency to `skill_proficiencies`; the skill-gap engine always prefers verified over self-reported, and readiness recomputes after each submission. |
| 9 | **Personalization without a training pipeline.** | Lightweight online weight adaptation: feedback events nudge that learner's 8 ranker weights by the stored factor contributions of the course they reacted to, persisted per user — a bandit-style loop, no offline retraining. |
| 10 | **First request was slow** (fitting TF-IDF + SVD over 18k docs). | Cache the fitted vectorizer, SVD, and matrices to disk with `joblib`, keyed on CSV mtime + row count; warm the engine on startup. |
| 11 | **Cold DB / Atlas hiccups crashed requests.** | Global `PyMongoError → 503` handler with a friendly message; the client shows a retry banner; startup tolerates a failed DB ping. |
| 12 | **Free-text onboarding is ambiguous.** | Deterministic rule tables + alias maps + a semantic fallback, and everything surfaces as a *suggestion the user confirms* before it touches their profile. |
| 13 | **Phases with 15+ courses were unreadable.** | Auto-split any phase with more than 7 courses into "Part N" milestones sized to ~6 courses each. |
| 14 | **Session expiry vs. bad credentials both return 401.** | Client whitelists `/auth/login` and `/auth/register` so their 401s show "invalid credentials" instead of triggering the global logout/redirect. |
| 15 | **Adding a course shouldn't break ordering.** | Manually added courses are placed by their catalog tier into the matching phase, estimated-hours recomputed, and flagged "Added by you" so the rationale stays honest. |

---

## 8. Possible Extensions
- Replace TF-IDF/SVD with sentence-transformer embeddings (kept out for zero-dependency, offline-first operation).
- Real course-catalog ingestion (Coursera/edX APIs) behind the same `Catalog` interface.
- Collaborative-filtering signal from aggregated `user_feedback` across learners.
- Spaced-repetition scheduling for quiz re-tests.
- Multi-career "portfolio" planning and time-boxed sprints.
