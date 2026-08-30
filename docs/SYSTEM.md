# CareerPath AI — Full System Documentation

A local, explainable engine that turns an engineering student's profile into
(1) a **ranked list of courses** and (2) a **prerequisite-ordered, phased learning
path**, with YouTube playlists as a secondary supplement and a data-grounded chat
assistant on top.

The **ML engine** runs entirely offline — no API key. `GEMINI_API_KEY` /
`OPENAI_API_KEY` only upgrade the (already grounded) chat assistant, the per-phase
path explanation, and opt-in per-course quiz generation to a live LLM;
`YOUTUBE_API_KEY` only upgrades the YouTube block from a search link to ranked
results.

> **v2 (SaaS) — what changed since the sections below were first written.**
> The app now has real **email/password auth (JWT, bcrypt)** and stores everything
> in **MongoDB Atlas** (no SQLite, no `user_id` in requests — the JWT identifies
> the learner). The frontend is a **routed** app (react-router) with a left
> sidebar, not a tab shell; there is no demo mode. Progress is tracked
> **per course** (a phase auto-completes when all its courses are done);
> recommendations can **add/remove** courses and the roadmap can be regenerated;
> each course has a **3–4 question quiz**; you can **paste a résumé** to detect
> skills; the assistant is a floating panel that renders markdown.
> Current, authoritative surface docs: [`../README.md`](../README.md),
> [`ARCHITECTURE.md`](ARCHITECTURE.md), [`API.md`](API.md).
> §§ 4–9 (dataset, taxonomy, ML engine, career/skill-gap engines, YouTube,
> assistant grounding) are still accurate. §§ 2–3, 10–15 are updated inline below.

---

## Table of contents

1. [What the system does](#1-what-the-system-does)
2. [Architecture at a glance](#2-architecture-at-a-glance)
3. [End-to-end flow](#3-end-to-end-flow)
4. [The synthetic course dataset (`courses.csv`)](#4-the-synthetic-course-dataset-coursescsv)
5. [The curated taxonomy (`taxonomy_data.py`)](#5-the-curated-taxonomy-taxonomy_datapy)
6. [The ML engine (`app/ml/`)](#6-the-ml-engine-appml)
   - 6.1 [`catalog.py` — load & index](#61-catalogpy--load--index)
   - 6.2 [`semantic.py` — hybrid TF-IDF + LSA retrieval](#62-semanticpy--hybrid-tf-idf--lsa-retrieval)
   - 6.3 [`graph.py` — prerequisite DAG](#63-graphpy--prerequisite-dag)
   - 6.4 [`ranker.py` — the 8-factor ranking model](#64-rankerpy--the-8-factor-ranking-model)
   - 6.5 [`planner.py` — path construction](#65-plannerpy--path-construction)
   - 6.6 [`explain.py` — "why this course"](#66-explainpy--why-this-course)
   - 6.7 [`engine.py` — orchestration](#67-enginepy--orchestration)
7. [Career matching & skill-gap engines](#7-career-matching--skill-gap-engines)
8. [YouTube integration](#8-youtube-integration)
9. [AI assistant](#9-ai-assistant)
10. [Inputs & outputs — the REST API](#10-inputs--outputs--the-rest-api)
11. [Persistence — database models](#11-persistence--database-models)
12. [Frontend](#12-frontend)
13. [Configuration](#13-configuration)
14. [Scripts, training & evaluation](#14-scripts-training--evaluation)
15. [Running it](#15-running-it)

---

## 1. What the system does

| Feature | Input | Output |
|---|---|---|
| **Career discovery** | 5-step onboarding profile | Top-3 career matches with score breakdown + a clarifying question when close |
| **Skill-gap analysis** | profile + chosen career | Per-skill `current → required` levels, gap size, status, prerequisite warnings, overall readiness % |
| **Course recommendations** | profile + career (or a free-text goal) | A ranked, de-duplicated list of catalog courses, each with an explanation and per-factor contribution shares |
| **Learning path** | profile + career | 4–8 phased milestones, each an ordered set of courses ("do this first because…", "prepares you for…"), plus an auto project, an optional quiz, and a YouTube supplement block |
| **Diagnostic quizzes** | skill id | MCQ quiz; on submit → a verified proficiency that overrides the self-report and re-computes readiness |
| **AI assistant** | free-text question | An answer grounded in the learner's real path / gaps / weights (LLM if a key is set, otherwise a retrieval-templating engine) |
| **Progress dashboard** | profile + career | Readiness %, milestone counts, hours, skill radar, next action |

The **core value** is items 3 and 4. Both are produced by one local model fitted on
a synthetic ~18,000-row course catalog.

---

## 2. Architecture at a glance

```
                         ┌─────────────────────────────────────────────┐
  React + react-router ─▶ │  FastAPI  (app/main.py, 10 routers)          │
  frontend/src/*         │  JWT (Bearer) on every in-app request        │
   AuthContext           │                                             │
   AppDataContext        │  app/core/security.py  bcrypt + JWT + user   │
                         │  app/api/*      thin HTTP layer              │
                         │  app/services/* career match, skill gap,     │
                         │                 progress, path explain,      │
                         │                 course quiz, skill extract,  │
                         │                 youtube, ai assistant        │
                         │  app/ml/*       THE ENGINE  ◀── warmed once  │
                         │  app/data/*     courses.csv + taxonomy       │
                         │  app/db/*       mongo.py + repository.py      │
                         └──────────────────┬──────────────────────────┘
                                            ▼
                                   MongoDB Atlas (9 collections)

  app/ml/ engine (singleton, built at startup in ~12 s, cached to disk):

     courses.csv ──▶ catalog.py  ──▶  DataFrame + inverted indices
                          │
                          ├──▶ semantic.py  TF-IDF → TruncatedSVD (LSA) + raw TF-IDF
                          │                 → hybrid course vectors (cached .pkl)
                          │
                          └──▶ graph.py     NetworkX DiGraph over (branch, track, tier)
                                            "rungs", longest-path depth

     ranker.py   scores candidate courses on 8 factors + per-learner weights
     planner.py  picks tracks → walks tier ladders → closes prerequisites → phases
     explain.py  turns factor contributions into text
     engine.py   ties it together, produces API-shaped responses
```

**Why local / classical ML instead of an LLM or transformer embeddings:**
deterministic, explainable (every score decomposes into factor contributions),
fast (a path generates in well under 150 ms after warm-up), no per-request cost,
no external dependency, no hallucinated course names.

---

## 3. End-to-end flow

### 3.1 Startup

1. `uvicorn app.main:app` → startup pings MongoDB and calls `mongo.ensure_indexes()`.
2. `@app.on_event("startup")` also calls `engine.warm()`:
   - `load_catalog(courses.csv)` → pandas DataFrame + indices (§6.1)
   - `load_or_fit()` → loads `app/ml/cache/semantic.pkl` if its key
     `(csv_mtime, row_count)` matches, otherwise **fits** the TF-IDF+SVD space
     (~12 s cold) and pickles it (~43 MB, includes the raw TF-IDF matrix)
   - `build_graph()` → the prerequisite DAG
   - constructs `Ranker` and `Planner`
3. First request is now instant; subsequent restarts reload the cache in ~3 s.

### 3.2 A learner's journey

> **v2:** step 0 is `POST /api/auth/register|login` → JWT. The learner is the
> token; `LearnerProfileDB` → `profiles` doc, `LearningPathDB`/`MilestoneDB` →
> the embedded `milestones[]` on the `learning_paths` doc, `path_store` →
> `repository`. Progress is per-course (`path_progress`), the quiz is per-course
> (`GET /api/assessments/course-quiz/{course_id}`), and the 👍/👎 step is gone —
> marking a course done records the `completed` event instead.

```
Profile form  (name, branch, interests, skills, prefs)   [+ paste résumé]
        │  POST /api/onboarding/profile     → upserts the profiles doc
        ▼
Find My Career  (interests / skills / prefs pre-filled, editable)
        │  POST /api/careers/discover       → career_engine.calculate_career_matches
        │        weighted score: branch 30% · interest 35% · skill 25% · experience 10%
        │        semantic similarity comes from the same fitted TF-IDF+SVD space
        ▼   user picks a career  → profile.target_career_id set
Course Recommendations   (the headline screen)
        │  POST /api/recommendations/resources
        │        engine.recommend(profile, career_id)
        │          1. build RankingContext  (goal vector, gap vector, branch prefs,
        │             adaptive weights)
        │          2. candidate pool = career courses ∪ top-2500 by goal sim
        │                              ∪ all courses of the 18 closest tracks
        │          3. ranker.rank()  → score every candidate on 8 factors
        │          4. one course per track  →  MMR de-dup  →  relevance gate
        ▼
Learning Roadmap
        │  POST /api/paths/generate/{career_id}
        │        engine.build_path(profile, career_id)
        │          1. context + skill-gap analysis  → the gaps to close
        │          2. planner.build_plan():
        │               a. pick 3–6 tracks (biggest gaps forced in + goal similarity)
        │               b. for each track walk tiers Beginner→Capstone,
        │                  ranker picks the single best provider/angle variant per tier
        │               c. pull in unmet prerequisite rungs (topological closure)
        │               d. order by (graph depth, tier, −score)
        │               e. group into ≤4 phases by tier, split big phases into "(Part N)"
        │          3. attach an auto project + a matching quiz per milestone
        │          4. attach YouTube supplements per milestone (real skill names only)
        │          5. compute readiness %, weeks, "what NOT to do" warnings
        │        → repository.save_path  (learning_paths doc, milestones embedded)
        ▼
Track it
        │  toggle a course:  POST /api/paths/progress/{career}/resource/{id}/toggle
        │        → path_progress.completed_resource_ids; apply_progress re-derives
        │          milestone status + readiness; a completion also nudges ranker weights
        │  toggle a phase:   POST /api/paths/progress/{career}/milestone/{key}/toggle
        │  add/remove:       POST /api/paths/courses/{career}/add | /remove
        │  regenerate:       POST /api/paths/regenerate/{career}
        ▼
Take a per-course quiz  (3–4 questions)
        │  GET  /api/assessments/course-quiz/{course_id}   (bank → LLM → generic; cached)
        │  POST /api/assessments/submit  {assessment_id:"cq_<course_id>", ...}
        │        grade → write skill_proficiencies(evidence_source="assessment")
        │        → recompute the path's base_readiness_score
        ▼
Dashboard / Assistant
           POST /api/analytics/dashboard      → readiness, phases, hours, recent courses, radar
           GET  /api/paths/explanation/{career} → per-phase "why" + overview
           POST /api/assistant/chat            → grounded answer from the real path/gaps
```

---

## 4. The synthetic course dataset (`courses.csv`)

**Location:** `backend/app/data/courses.csv`
**Size:** ~17,940 rows · 14 engineering branches · 94 track names · 10 providers · 5 formats · 4 difficulty tiers (evenly balanced)
**Generator:** `backend/scripts/generate_dataset.py` (deterministic, `random.seed(42)`)

### 4.1 Column schema

| Column | Type | Meaning | Used by |
|---|---|---|---|
| `course_id` | string `C000001…` | unique id | everything |
| `branch` | string | one of the 14 engineering branches | `branch_fit` factor, path branch-scoping |
| `track` | string | the skill ladder this course belongs to (a taxonomy skill name, or `"<Career> Portfolio"`) | rung identity, planner track selection, de-dup |
| `course_title` | string | `"<Track>: <Foundations\|Applied\|Advanced\|Capstone>"` for the canonical variant, plus `" — <Angle>"` for the others | display, prerequisite resolution |
| `difficulty_level` | `Beginner` / `Intermediate` / `Advanced` / `Capstone` | tier; mapped to int 0–3 | `level_fit`, tier ladder, phasing |
| `provider` | string | NPTEL, Coursera, edX, Udacity, Pluralsight, MITx, Udemy, LinkedIn Learning, DataCamp, Great Learning | `is_free` (NPTEL/MITx/edX), provider affinity |
| `format` | string | Video Course / Interactive Lab / Project-Based / Instructor-led Live / Self-paced Reading | `format_pref` factor |
| `description` | long text | one of 4 templates × 6 "angle" blurbs → genuinely varied prose (this is the main TF-IDF signal) | semantic space |
| `skills_taught` | `;`-separated list | cumulative skill tokens up to that tier + angle-specific extras (e.g. "interview preparation", "first principles") | `skill_gain` fallback, YouTube query, milestone `target_skills` |
| `tools_covered` | `;`-separated list | from a category→tools table (e.g. `pytorch; scikit-learn; numpy`) | semantic space |
| `prerequisite_course_title` | string (may be empty) | the exact `course_title` of the canonical variant one tier down in the same track; for a Beginner course whose skill has taxonomy prerequisites → the Beginner canonical title of the first prerequisite skill (a **cross-track edge**) | `graph.py` DAG construction |
| `estimated_hours` | int | `~N(tier_base × angle_multiplier, 15%)` — Beginner ≈ 14 h, Capstone ≈ 50 h; Crash Course ×0.55, Project Track ×1.3 | `effort_fit`, milestone hours, readiness |
| `rating` | float 3.4–4.9 | `~N(4.35, 0.33)` clipped | `quality` factor (Bayesian-shrunk) |
| `num_reviews` | int ~40–7000 | `|N(1500, 1400)| + 40` | `quality` shrinkage weight |
| `career_paths` | `;`-separated list | every career title whose `required_skills` include this track's skill | `career_index`, recommendation pool seeding |
| `industry_sectors` | `;`-separated list | from a category→sectors table (e.g. `artificial intelligence; technology`) | semantic space |

### 4.2 How the dataset is generated

`generate_dataset.py`:

**Part 1 — one 4-tier track per (skill, branch):**
- For each skill in `SKILLS_DATABASE` (~74 skills), `_branches_for_skill()` returns
  the skill's home branch **plus** the primary branch of every career that requires
  it, plus compatible branches (capped at 5, ordered by importance). This is the
  cross-branch coverage — e.g. "3D CAD Modeling" exists for Mechanical, Robotics/
  Mechatronics, Automobile, Aerospace, Industrial.
- Each (skill, branch) becomes a track with 4 tiers.
- `skills_taught` is cumulative: Beginner = `[prereq_name?, skill]`, Intermediate =
  `[skill, all prereqs]`, Advanced adds `"<skill> optimisation"`, Capstone adds
  `"<skill> system design"`.
- **Angles.** Each tier is emitted as several distinct courses that differ by
  `(provider, angle)`. The 7 angles — *standard, Hands-On Lab, Project Track,
  Deep Theory, Crash Course, Interview & Exam Prep, Industry Practicum* — each carry
  their own `format`, an hours multiplier, a description blurb, and extra skill
  tokens. The **standard angle is always emitted** so `prerequisite_course_title`
  always resolves to a real course. `variants_per_rung` is computed to hit the
  ~18,000-row target (currently ~13 per rung).

**Part 2 — one "role portfolio" track per career:**
- Track name `"<Career title> Portfolio"`, single branch (the career's), skills =
  all of the career's required-skill names + "engineering project workflow",
  "job-readiness review", "technical interview prep".
- These are the *integrative capstone* track. They are **excluded from the flat
  recommendation list** (they'd always rank #1 and hide the concrete skill courses)
  but the planner includes one as the capstone thread of the path, starting at the
  Applied tier.

Regenerate any time with `python -m scripts.generate_dataset`. The engine detects
the changed file (cache key = `mtime + row count`) and re-fits on next start.

> The generator is schema-driven. To use a **real** course catalog instead, drop a
> CSV with the same 16 columns at `app/data/courses.csv` and delete the cache.

---

## 5. The curated taxonomy (`taxonomy_data.py`)

Hand-authored Python literals — the "ground truth" for careers and skills. The
dataset is generated *from* this, and career-matching / skill-gap / quizzes read it
directly.

- **`ENGINEERING_BRANCHES`** — 14 branch names.
- **`CAREERS_DATABASE`** — 20 careers. Each: `career_id`, `title`, `category`,
  `branch_primary`, `branches_compatible[]`, `description`, `avg_salary_range`,
  `job_demand`, `key_responsibilities[]`, `required_skills[{skill_id, name,
  level (0–1), critical bool}]`, `day_in_the_life`, `hard_realities[]`,
  `common_misconceptions[]`, `future_evolution[]`, `emerging_specializations[]`,
  `what_not_to_do[]`.
- **`SKILLS_DATABASE`** — ~74 skills. Each: `id`, `name`, `category`,
  `prerequisites[]` (skill ids). The `prerequisites` list is the coarse skill-level
  dependency graph used for skill-gap warnings and for seeding the dataset's
  cross-track prerequisite edges.
- **`QUIZZES_DATABASE`** — MCQ quizzes keyed by skill id. Each question has
  `question_text`, `options[]`, `correct_option_index`, `explanation`.

---

## 6. The ML engine (`app/ml/`)

### 6.1 `catalog.py` — load & index

`load_catalog(csv_path) -> Catalog`. Builds, once:

- `df` — the pandas DataFrame (numeric columns coerced, NA filled).
- `docs` — one **field-weighted pseudo-document** per course: each field repeated by
  its weight before vectorization —
  `course_title×3, track×3, skills_taught×2, career_paths×2, tools_covered×1,
  branch×1, industry_sectors×1, description×1`. This makes titles/tracks dominate the
  TF-IDF representation.
- `tiers` — int tier per row (`Beginner=0 … Capstone=3`).
- `quality` — **Bayesian-shrunk rating** in `[0, 1]`:
  `shrunk = (num_reviews·rating + 150·global_mean) / (num_reviews + 150)`, then
  mapped `(shrunk − 3)/2` and clipped. A 4.9 course with 50 reviews scores lower
  than a 4.4 course with 5000.
- `skill_lists`, `career_lists` — parsed `;`-lists per row.
- **Inverted indices:** `variant_index {(branch, track, tier) → [row positions]}`,
  `track_index {(branch, track) → [...]}`, `title_index {lower title → [...]}`,
  `career_index {career lower → [...]}`.
- Vocab lists: `skills_vocab`, `careers_vocab`, `tracks_vocab`, `branches_vocab`.

A `Rung` is the tuple `(branch, track, tier)` — one step on one curriculum ladder.

### 6.2 `semantic.py` — hybrid TF-IDF + LSA retrieval

**Fit (`SemanticSpace.fit`):**

1. `TfidfVectorizer(ngram_range=(1,2), stop_words="english", sublinear_tf=True,
   min_df=3, max_df=0.6, max_features=24000)` → sparse TF-IDF matrix over the
   field-weighted docs.
2. `TruncatedSVD(n_components=240, n_iter=7, random_state=42)` → dense **LSA**
   (Latent Semantic Analysis) space; `course_vectors` are L2-normalized.
3. The raw TF-IDF matrix is **also kept** (L2-normalized, sparse) for the hybrid.

**Query methods:**

- `encode(text)` — project a query string into the 240-dim LSA space (L2-norm).
- `cosine_to_courses(vec)` — LSA cosine of a query vector against every course.
- **`hybrid_to_courses(text)`** — the one used for recommendations:
  `0.55 · LSA_cosine + 0.45 · rawTF-IDF_cosine`.
  LSA captures synonyms ("JS" ≈ "JavaScript", "chip design" ≈ "VLSI"); the raw
  lexical term keeps short queries honest (so "data pipeline" doesn't drift into
  "test pipeline").
- `similar_courses(text, k)` / `similar_to_course(pos, k)` — content-based neighbours.
- `text_similarity(a, b)` — LSA cosine of two free strings; used by the career-match
  and skill-gap engines (replaces the old substring matching, and the previous
  `sentence-transformers` dependency, which has been removed).

**Pseudo-relevance feedback (`engine._query_sims`).** For short user-typed goals
(≤ 7 words) the initial top-10 hits' skill tokens are folded back into the query and
re-scored; the final score is `0.55·original + 0.45·expanded`. This is what lets
"cybersecurity" surface networking / crypto / linux courses and not just the one
literal "pen testing" match.

**Cache.** `app/ml/cache/semantic.pkl` (joblib, compressed). Key = dataset
`(mtime, row count)`. Contains the vectorizer, the SVD, the L2-normalized LSA course
matrix, and the raw TF-IDF matrix (~43 MB). `.gitignore`d.

### 6.3 `graph.py` — prerequisite DAG

`build_graph(catalog) -> PrereqGraph` (a `networkx.DiGraph`):

- **Nodes** = every rung `(branch, track, tier)`.
- **Edges** from `prerequisite_course_title`: resolve the title to a rung via a
  global `title → rungs` map, preferring a target in the same track; if unresolved,
  fall back to the tier below in the same track.
- **Tier chaining:** within every track add `tier-1 → tier` edges so a bare ladder
  is always ordered.
- **Cycle breaking:** while the graph isn't a DAG, find a cycle and drop the edge
  whose head is the highest tier.
- **Depth:** topological sort → `depth[rung] = 1 + max(depth[pred])` (longest path).
  Entry rungs have depth 0.
- Reports `unresolved` (currently **0** on the shipped dataset).

Used by the ranker (`prereq_ready`) and the planner (ordering, prerequisite closure).

### 6.4 `ranker.py` — the 8-factor ranking model

`Ranker.rank(ctx, positions, limit) -> [ScoredCourse]`.

For each candidate course, compute 8 factor values in `[0, 1]`:

| Factor | Default weight | How it's computed |
|---|---|---|
| `goal_fit` | **0.26** | `ctx.goal_sims[course] / pool_max` — the hybrid similarity to the goal, pool-normalized so the best candidate = 1.0. On a pure goal search (no branch/career) `branch_fit`'s weight is added to this. |
| `skill_gain` | **0.18** | `ctx.gap_sims[course] / pool_max` — hybrid similarity to the **gap-profile vector** (the encoded concatenation of the skills the learner still needs). Falls back to weighted token overlap if no gap vector. |
| `branch_fit` | **0.13** | graded: `1.0` if the course branch == the learner's own branch · `0.82` if it's one of the target career's branches · `0.62` if otherwise "preferred" · `0.35` else. |
| `level_fit` | **0.12** | asymmetric distance from the learner's target tier: `1 − 0.14·|Δ|` if the course is at/below the target, `1 − 0.32·Δ` if above (over-shooting is penalized harder). |
| `quality` | **0.10** | the Bayesian-shrunk rating from the catalog. |
| `prereq_ready` | **0.10** | `0.25 + 0.75 · (satisfied predecessors / all predecessors)` — floors at 0.25, never 0. |
| `effort_fit` | **0.06** | `1 − (hours − 3·weekly) / (3·weekly)`, clipped — is it completable within ~3 weeks of the learner's budget? |
| `format_pref` | **0.05** | `1.0` if the learner's preferred format matches the course format, else `0.5`. |

**Score:** `score = Σ(factor · weight) / Σ(weights)`, then a small additive
`+0.05 · (track_affinity + provider_affinity)` from learned feedback, clipped to
`[0, 1.2]`.

**Contribution shares:** `contribution[f] = (factor·weight) / Σ(factor·weight)` —
each factor's % of *why this course ranked where it did*. Surfaced to the UI as
"drivers" and used by the feedback loop.

**Per-learner adaptive weights.** `LearnerModelDB` stores a `weights` dict and an
`affinities` dict per learner. `engine.record_feedback(event_type, course_id)`:
- `sign = {upvote:+1, completed:+0.6, downvote:−1, dismiss:−0.6}`
- for each factor that drove that course: `w[f] *= 1 + sign · 0.12 · contribution[f]`
  → so a 👎 on a course that ranked mostly for `quality` lowers *that learner's*
  `quality` weight, not a global fudge. Weights are re-normalized to sum 1.
- track/provider affinity: `±0.15` per event, clipped `[−1, 1]`.

`one_per_rung=True` keeps only the top variant of each `(branch, track, tier)`.

### 6.5 `planner.py` — path construction

`Planner.build_plan(ctx, goal_vec, weekly, timeline_weeks, target_tier, must_tracks)`:

1. **Track selection (`_pick_tracks`).** Score every `(branch, track)` by
   `centroid · goal_vec` (centroid = mean LSA vector of the track's courses),
   `−0.15` if the branch isn't in the learner's preferred set. Then:
   - **force in** the `must_tracks` first — these are the learner's biggest
     skill-gap skills (top 5 by gap delta) plus the career's portfolio track — each
     via its best branch variant;
   - fill the rest by similarity, no duplicate track names;
   - count `n = clip(weekly · timeline_weeks // 70, 3, 6)`.
2. **Ladder walk.** For each selected track, walk tiers `Beginner→Capstone`. The
   learner's stated level **waives** lower tiers (`start_tier = min(target_tier, 2)`),
   recording each waiver; the portfolio track starts at Applied. For each remaining
   tier the ranker picks the single best `(provider, angle)` variant.
3. **Prerequisite closure.** BFS over the DAG: for every chosen rung, pull in any
   unmet predecessor rung (its best variant) — unless a same-`(track, tier)` rung
   from another branch is already chosen. Guarantees topological validity.
4. **Collapse** remaining `(track, tier)` duplicates, keeping the higher score.
5. **Order** all chosen courses by `(graph depth, tier, −score)`.
6. **Phasing.** Group by tier → phase 0..3 (`Foundations / Applied Engineering &
   Systems / Advanced Specialisation / Industry Capstone & Job Readiness`). A phase
   with > 7 courses is split into balanced "(Part N)" milestones (~6 each, no tiny
   tails).
7. Each course carries **`why_now`** ("Start here…" or "Take this after
   *<real earlier course title>*. …") and **`unlocks`** (titles of the courses in
   the plan that directly depend on it).

### 6.6 `explain.py` — "why this course"

`explain(scored_course, row) -> {headline, drivers[], caveats[]}`:
- `drivers` — factors with contribution ≥ **0.08**, top 3, as
  `{factor label, share}`.
- `headline` — `"Recommended because it <driver1> and <driver2>."`
- `caveats` — factor *values* below **0.35** mapped to a phrase
  ("some prerequisites aren't complete yet", "thinner rating history", …).

### 6.7 `engine.py` — orchestration

The `Engine` singleton (`from app.ml.engine import engine`):

| Method | Purpose |
|---|---|
| `warm()` | build catalog / semantic / graph / ranker / planner once |
| `interpret_profile(profile, career_id, gap_names)` | compose the goal text: career title + category + description + top-3 responsibilities + required-skill names + interests + branch + focus skills |
| `_context(...)` | run skill-gap analysis, build the `RankingContext` — goal sims (`_query_sims`), gap sims, branch prefs, target tier, adaptive weights |
| `recommend(...)` | candidate pool → `ranker.rank` → one-per-track → MMR → relevance gate → `CourseRecommendationResponse` |
| `build_path(...)` | `planner.build_plan` → milestones (courses + project + quiz + YouTube) → readiness + warnings → `LearningPathResponse` |
| `youtube_extras(skill_names)` | call `youtube_service` for real skill names only, map to `ResourceItem`s |
| `record_feedback(...)` | update `LearnerModelDB` (see §6.4) |
| `model_snapshot(db, profile_id)` | the learner's current weights + deltas from default, for the UI / assistant |

**Diversity — `_mmr`.** After ranking, greedily drop any course whose LSA vector has
cosine > 0.93 to one already picked (kills near-identical rows).

**Relevance gate (recommendations).** Keep the first 2, then keep a course only if
`goal_sim ≥ 0.30·best AND score ≥ 0.52·best_score`. Returns a short strong list
rather than padding to `limit` with weak matches.

**Readiness (`_readiness`).**
`score = clip((Σ min(current, required) / Σ required) · 100, 15, 100)`;
`hours = max(30, round(Σ gap_delta · 75))`; `weeks = hours / weekly_hours`.

**Warnings (`_warnings`).** The career's first 2 `what_not_to_do` entries + a
prerequisite warning if a critical skill is Missing/Major-Gap + a
"ship projects, not certificates" note for video/text learners + a pacing note
below 5 h/week.

---

## 7. Career matching & skill-gap engines

### `career_engine.calculate_career_matches(profile) -> CareerDiscoveryResponse`

Score every career:

| Component | Weight | Computation |
|---|---|---|
| Branch compatibility | 30% | `1.0` primary · `0.85` compatible · `0.55` cross-branch |
| Interest alignment | 35% | mean `semantic.text_similarity(interest, career_text)` over the learner's interests, where `career_text` = title + category + description + responsibilities |
| Skill overlap | 25% | fraction of the career's required skills for which `best_text_similarity(skill_name, known_skills) ≥ 0.55` |
| Experience fit | 10% | `1 − |experience_rank − mean_required_level|` |

`match% = clip(raw·100, 5, 99)`. Top-3 returned. If the top two are within 7% →
`clarification_needed` with a 2-option question. If the top match's branch ≠ the
learner's branch → `cross_branch_advice` naming up to 2 critical bridge skills.

### `skill_gap_engine.analyze_skill_gaps(career_id, profile, db, profile_id)`

For each required skill of the career:

1. **Proficiency source, in priority order:**
   - a **quiz-verified** proficiency (`SkillProficiencyDB` row with
     `evidence_source="assessment"`) — a real tested signal;
   - else semantic match: if `best_text_similarity(skill_name, known_skills) ≥ 0.55`,
     `current = min(1, base_prof + 0.2·match)` where `base_prof` is 0.25 / 0.5 / 0.75
     for beginner / intermediate / advanced;
   - else `0.0`.
2. `gap_delta = max(0, required − current)`.
3. Status: `Mastered` (0) · `Missing` (current 0) · `Minor Gap` (≤ 0.3) · `Major Gap`.
4. Prerequisite warning if `current < 0.3` and the skill has taxonomy prerequisites.

Returns per-skill items + `overall_readiness_pct` + up to 3 `prerequisite_warnings`.
This is what feeds the ranker's gap vector, the planner's `must_tracks`, the
dashboard skill radar, and the assistant's "weak areas".

---

## 8. YouTube integration

**File:** `app/services/youtube_service.py`. **Role:** a *secondary* supplement —
never mixed into the ranked course pool; surfaced as `Milestone.youtube_extras`
(its own UI block under the course list).

**Entry point:** `get_dynamic_youtube_resources(skill_name, category) -> [dict]`
(≤ 3 items, `@lru_cache(512)` keyed by `(skill, category, _CACHE_VERSION)` — bump
`_CACHE_VERSION` to invalidate a long-lived process). **Never raises.**

**Which skill names are queried:** `engine._plan_to_milestones` only passes **real
`SKILLS_DATABASE` names** (filler tokens like "portfolio project", "first principles"
are filtered out); if a milestone has none, it falls back to the track names.

### With `YOUTUBE_API_KEY` set (`_real_youtube_search`)

1. **Playlist search** — `search.list?type=playlist&q="<skill> tutorial playlist"&maxResults=2`.
   A curated "learn X" playlist is usually the best single resource, so up to one
   playlist is placed **first**. Item id `yt_pl_<playlistId>`, url
   `youtube.com/playlist?list=<id>`, estimated `duration_hours=6`.
2. **Long-form video search** — `search.list?type=video&videoDuration=long&q="<skill> full course"&maxResults=5`.
3. **`videos.list?part=snippet,contentDetails,statistics`** for the found ids →
   real ISO-8601 durations parsed to hours; `viewCount` / `likeCount` read.
4. Videos are **re-ranked by view count** (most-watched first).
5. `rating` is an engagement proxy, not a fabricated number:
   `min(5.0, 3.6 + (likes / views) · 120)`.
6. Merge: `[playlist] + videos + [extra playlist]`, take 3.

Requests use a 6 s timeout; any HTTP/parse error → falls through to the link.

### Without a key (`_fallback_search_link`)

Returns one honest item: a link to YouTube's **playlist-filtered** results page —
`youtube.com/results?search_query=<skill>+full+course&sp=EgIQAw%3D%3D`
(`sp=EgIQAw%3D%3D` is YouTube's stable "type: playlist" filter token). `rating` is a
neutral `4.0` explicitly labelled "not a quality claim", and `match_reason` tells
the user to set `YOUTUBE_API_KEY` for ranked results.

Free-tier quota is 10,000 units/day; the in-process cache keeps a typical session
well under that.

---

## 9. AI assistant

**File:** `app/services/ai_assistant.py`. Route: `POST /api/assistant/chat`.

### Grounding (`_collect_grounding` → `Grounding`)

Assembled from the learner's **real** state:
- the chosen career's taxonomy entry (`day_in_the_life`, `hard_realities`,
  `what_not_to_do`, `key_responsibilities`);
- the **actual ordered course list** from their persisted path — milestone titles,
  each course title, and the planner's real `why_now` string per course;
- the **real skill-gap analysis** (skill, `current → required`, delta, status),
  sorted largest-gap-first;
- readiness %, estimated weeks/months;
- the learner's **personalised ranker weights** (`engine.model_snapshot`) — the
  top-3 factors currently driving their recommendations.

`_grounding_text(g)` renders all of that into a plain-text block.

### Answering

- **If `GEMINI_API_KEY` or `OPENAI_API_KEY` is set** (env only — there is no runtime
  key endpoint): the grounding block is sent as the system context with strict
  rules — *"Answer ONLY from the learner context. Do NOT invent course names,
  numbers, timelines. Cite the learner's real course titles / gap numbers."*
  Models: `gemini-1.5-flash` / `gpt-4o-mini`, `temperature 0.4`. Any failure →
  offline engine.
- **Offline engine (`_offline_answer`)** — a retrieval + light-templating engine, not
  canned prose. `_classify()` routes the message to an intent:
  `why_path` · `next_step` · `timeline` · `weak_areas` · `avoid` · `day` ·
  `projects` · `compare` · `default`. Each template pulls specific real values:
  - **`why_path`** — for the first 4 courses: the prerequisite placement
    ("Take this after *&lt;real earlier course&gt;*, which it builds on"), the
    **ranking drivers as percentages** from that course's `factor_contributions`
    (e.g. "goal match 30% · skill-gap coverage 20% · branch fit 15%"), what it
    unlocks, and the learner's overall factor weighting;
  - **`next_step`** — the exact next course, its milestone, its driver %s, unlocks;
  - **`weak_areas`** — the real top-3 gaps (`current% vs needed%`, status) + the
    path courses that close them;
  - **`timeline`** — the real `estimated_weeks`, readiness %, milestones done;
  - **`avoid` / `day` / `projects`** — straight from the career taxonomy entry and
    the milestones' auto-generated projects.
- `suggested_followups` and `referenced_resources` are always dynamic (depend on
  intent + what's in the path). When an LLM answers, the offline engine still
  supplies those.

---

## 10. Inputs & outputs — the REST API

Base URL `http://localhost:8000/api`. Interactive docs at `/docs`.

> **v2:** the learner is identified by a **JWT** (`Authorization: Bearer`), issued
> by `POST /auth/register` / `POST /auth/login`, **not** by a `user_id` field.
> Endpoints that took `/{user_id}` are now unauthenticated-body current-user
> endpoints (e.g. `POST /onboarding/profile`, `GET /onboarding/profile`). The full
> current endpoint list with request/response shapes is in [`API.md`](API.md);
> the table below is kept for the field-level detail on `ProfileOnboardingRequest`
> and the response models, which are unchanged apart from the additions noted.
>
> **New since v1:** `GET /auth/me`, `POST /onboarding/parse-resume`,
> `POST /paths/regenerate/{career_id}`,
> `POST /paths/progress/{career_id}/resource/{resource_id}/toggle`,
> `POST /paths/progress/{career_id}/milestone/{milestone_key}/toggle`,
> `POST /paths/courses/{career_id}/add`, `POST /paths/courses/{career_id}/remove`,
> `GET /paths/explanation/{career_id}`, `GET /assessments/course-quiz/{course_id}`.
> **Removed:** `POST /auth/demo-login`,
> `POST /paths/milestone/{career_id}/complete/{milestone_id}`.
> `ResourceItem` gained `completed: bool`; `LearningPathResponse` gained
> `base_readiness_score`; `DashboardMetricsResponse` gained `recent_courses[]` and
> `has_path`.

### The core input — `ProfileOnboardingRequest`

| Field | Type | Notes |
|---|---|---|
| `user_id` | str | identity |
| `user_status` | str | Engineering Student / Recent Graduate / Working Professional / Career Switcher |
| `engineering_branch` | str | one of the 14 branches — drives `branch_fit` |
| `college_name` | str? | |
| `current_year`, `graduation_year` | str, int | |
| `interests` | str[] | free text + autocomplete — feeds the goal vector & interest match |
| `career_goal_status` | str | |
| `target_career_id` | str? | set after Career Discovery — the ranking anchor |
| `known_skills` | str[] | feeds skill-gap analysis & skill match |
| `experience_level` | str | Beginner / Intermediate / Advanced → target tier |
| `hours_per_week` | int | → `effort_fit`, timeline, phase weeks |
| `preferred_format` | str | project-based / video / text / mixed → `format_pref` |
| `learning_style`, `max_budget` | str | reserved |
| `target_timeline_months` | int | → planner track count, timeline |

### Endpoints

| Method · path | Body | Response |
|---|---|---|
| `POST /auth/demo-login` · `/register` · `/login` | — / credentials | `{access_token, user_id, email}` (token is a stub, not verified) |
| `GET /onboarding/keywords/search?q=` | — | `string[]` autocomplete |
| `POST /onboarding/{user_id}` | `ProfileOnboardingRequest` | `ProfileResponse` (upserts `LearnerProfileDB`) |
| `GET /onboarding/{user_id}` | — | `ProfileResponse` |
| `POST /careers/discover` | `ProfileOnboardingRequest` | `CareerDiscoveryResponse` — `top_matches[3]` with `match_percentage`, 3 sub-scores, `missing_critical_skills[]`, `transferable_skills[]`; optional `clarification_question`; optional `cross_branch_advice` |
| `GET /careers/detail/{career_id}` | — | `CareerDetail` (full taxonomy entry) |
| `POST /careers/compare` | `{career_ids: [2–3]}` | `CareerDetail[]` |
| `POST /skills/analyze-gap/{career_id}` | `ProfileOnboardingRequest` | `SkillGapAnalysisResponse` — `gaps[]` (`current_level`, `required_level`, `gap_delta`, `status`), `overall_readiness_pct`, `prerequisite_warnings[]` |
| `POST /recommendations/resources` | `RecommendationRequest {user_id, goal_text?, career_id?, limit=12, exclude_planned=false}` | `CourseRecommendationResponse {goal, count, results: ResourceItem[]}` |
| `POST /recommendations/feedback` | `{user_id, resource_id, feedback_type}` | `{status, adaptation: {updated, weights, update_count}}` |
| `GET /recommendations/model/{user_id}` | — | `{weights[], affinities[], update_count, personalised}` |
| `POST /paths/generate/{career_id}` | `ProfileOnboardingRequest` | `LearningPathResponse` (see below) — persisted; a second call returns the stored path |
| `POST /paths/milestone/{career_id}/complete/{milestone_id}` | `ProfileOnboardingRequest` | updated `LearningPathResponse` (advances the next milestone, bumps readiness by that milestone's hour share) |
| `GET /assessments/quiz/{skill_id}` | — | `AssessmentDetail` (questions + options) |
| `POST /assessments/submit` | `{assessment_id, answers: {q_id: idx}, user_id, career_id?}` | `QuizSubmissionResponse {score_percentage, passed, new_proficiency_level, feedback, detailed_results[]}` — side effects: writes `AssessmentSubmissionDB` + `SkillProficiencyDB`, re-computes the path's readiness |
| `POST /assistant/chat` | `{message, context_career_id?, user_id}` | `ChatResponse {reply, suggested_followups[], referenced_resources: ResourceItem[], referenced_warnings[]}` |
| `POST /analytics/dashboard?target_career_id=` | `ProfileOnboardingRequest` | `DashboardMetricsResponse` — readiness %, milestone counts, hours logged / total, months remaining, `next_action`, `skill_radar_data[{skill, current, required}]`, full `active_path` |
| `GET /system/status` | — | `{app_name, version, gemini_key_configured, openai_key_configured, youtube_key_configured, active_llm_mode}` |

### `ResourceItem` (a recommended / path course)

```jsonc
{
  "id": "C001234", "course_id": "C001234",
  "title": "Deep Learning & PyTorch: Applied",
  "type": "course", "provider": "edX", "url": "https://www.google.com/search?q=...",
  "duration_hours": 24.0, "difficulty": "intermediate",
  "skills_covered": ["deep learning & pytorch", "classical machine learning"],
  "rating": 4.4, "num_reviews": 3120, "is_free": true,
  "track": "Deep Learning & PyTorch", "branch": "Computer Engineering / IT",
  "match_reason": "Recommended because it matches your goal and closes your skill gaps.",
  "why_now": "Take this after Classical Machine Learning: Foundations. …",   // path only
  "unlocks": ["LLMs, Embeddings & RAG Systems: Applied"],                    // path only
  "factor_contributions": { "goal_fit": 0.41, "skill_gain": 0.19, "branch_fit": 0.14, ... }
}
```

### `LearningPathResponse`

```jsonc
{
  "id": "path_aiml_eng", "career_id": "aiml_eng", "career_title": "AI & Machine Learning Engineer",
  "job_readiness_score": 32.0, "estimated_total_hours": 540, "estimated_weeks": 45, "hours_per_week": 12,
  "track_names": ["Advanced Python & Scientific Computing", "Linear Algebra…", "Classical Machine Learning…", "Deep Learning & PyTorch"],
  "what_not_to_do_warnings": ["DON'T jump into LLM fine-tuning before …", …],
  "next_action": { "action_type": "start_course", "title": "Start '…'", "milestone_id": "ms_1", "resource_id": "C0…" },
  "milestones": [
    {
      "id": "ms_1", "sequence_order": 1, "title": "Phase 1: Foundations & Core Tools",
      "description": "Build the base vocabulary, math, and tooling every later step assumes.",
      "estimated_hours": 65, "estimated_weeks": 6, "status": "in_progress",
      "target_skills": ["advanced python & scientific computing", "linear algebra, calculus & probability", …],
      "resources": [ ResourceItem, … ],          // ordered — do these in sequence
      "project":  { "title": "…", "description": "…", "required_deliverable": "GitHub repo link + short demo video" },
      "assessment": { "assessment_id": "quiz_python_core", "title": "…", "description": "…" },   // null if no quiz matches
      "youtube_extras": [ ResourceItem(type:"video"), … ]      // the secondary supplement
    },
    …
  ]
}
```

---

## 11. Persistence — MongoDB

**MongoDB Atlas** via PyMongo. No ORM, no SQLite, **no migrations** (schemaless).
Connection + collection handles in `app/db/mongo.py`; all reads/writes go through
`app/db/repository.py`. Indexes are created on startup by `ensure_indexes()`.

| Collection | Key fields | Unique index |
|---|---|---|
| `users` | `_id` (uuid), `email`, `password_hash` (bcrypt), `full_name` | `email` |
| `profiles` | `user_id`, the 15 onboarding fields, `target_career_id` | `user_id` |
| `learning_paths` | `user_id`, `career_id`, `career_title`, `job_readiness_score`, `base_readiness_score`, `milestones[]`, `next_action`, `what_not_to_do_warnings[]`, `track_names[]` | `(user_id, career_id)` |
| `path_progress` | `user_id`, `career_id`, `completed_resource_ids[]` | `(user_id, career_id)` |
| `skill_proficiencies` | `user_id`, `skill_id`, `current_proficiency`, `evidence_source` — only `"assessment"` is trusted by the gap engine | `(user_id, skill_id)` |
| `learner_models` | `user_id`, `weights`, `affinities`, `update_count` — adaptive ranker state | `user_id` |
| `user_feedback` | `user_id`, `resource_id`, `feedback_type`, append-only | — |
| `assessments` | `user_id`, `assessment_id`, `skill_id`, `score_percentage`, `answers` | — |
| `course_quizzes` | `course_id`, `questions[]`, `source`, `matched_skill` — cached per-course quiz | `course_id` |

Milestones are stored as an embedded array on the path doc (not a separate
collection). `repository.save_path` upserts by `(user_id, career_id)`;
`apply_progress` (`app/services/progress.py`) overlays `path_progress` onto a path
on every read.

---

## 12. Frontend

React 18 + Vite + **react-router** (`frontend/src/App.jsx` is a `<Routes>` tree).
`frontend/src/api/client.js` is the fetch wrapper — it attaches the JWT and, on a
`401`, dispatches `auth:logout`. Two contexts: `AuthContext` (token in
`localStorage`, hydrates via `GET /auth/me`) and `AppDataContext` (profile /
discovery / active path / dashboard; always refetches after a mutation).

| Route / component | What it shows |
|---|---|
| `/` `pages/LandingPage` | honest pitch; CTA → register (or `/app` if signed in) |
| `/login`, `/register` `pages/LoginPage` `RegisterPage` | auth forms |
| `/app` `components/AppLayout` | left sidebar (Dashboard · Profile · Find My Career · Course Recommendations · Roadmap) + the floating assistant; logo → `/` |
| `/app/dashboard` `pages/DashboardPage` | readiness %, hours, phase progress, **recent course progress**, skill bar chart |
| `/app/profile` `pages/ProfilePage` | full profile form + **`ResumeImport`** (paste résumé → detected-skill chips) |
| `/app/discover` `pages/DiscoverPage` | 3 quick steps (interests / skills+level / prefs), pre-filled from the profile → top-3 match cards + clarification + compare |
| `/app/courses` `pages/CoursesPage` | goal box + ranked course cards with driver % chips and **Add / Remove from roadmap** (no 👍/👎) |
| `/app/roadmap` `pages/RoadmapPage` | phases with per-course **done ↔ pending** toggles, per-phase toggle, **Regenerate**, per-course **Quiz**, YouTube block, project, and a bottom **"Why this path works"** AI explanation |
| `components/AssistantWidget` | fixed top-right button → right-side slide-over chat; replies rendered via `lib/Markdown.jsx` (so `**bold**` renders) |
| `components/QuizModal` | 3–4 question course quiz |

No API-key UI, no LLM-mode badge — keys are `backend/.env` only.

---

## 13. Configuration

`backend/.env` (copy from `.env.example`).

| Var | Required | Effect |
|---|---|---|
| `MONGODB_URI` (+ `MONGODB_USERNAME` / `MONGODB_PASSWORD` / `MONGODB_DB`) | **yes** | Atlas connection; DB defaults to `pathfinder` |
| `SECRET_KEY` | prod | signs JWT access tokens (7-day expiry) |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` | no | live LLM for assistant + path explanation; else grounded offline engine |
| `COURSE_QUIZ_LLM` | no | `true` → generate per-course quizzes with the LLM instead of the offline `quiz_bank` |
| `YOUTUBE_API_KEY` | no | ranked YouTube results instead of a search link |
| `COURSES_CSV` / `ML_CACHE_DIR` | no | dataset + semantic-cache paths |

Tunable constants in code: `ranker.DEFAULT_WEIGHTS`, `semantic.SVD_COMPONENTS` (240),
`semantic.TFIDF_MAX_FEATURES` (24000), `semantic.HYBRID_LSA_WEIGHT` (0.55),
`catalog.RATING_PRIOR_WEIGHT` (150), the MMR / relevance-gate thresholds in
`engine.recommend`, `generate_dataset.TARGET_ROWS` (18000).

---

## 14. Scripts, training & evaluation

| Script | What it does |
|---|---|
| `python -m scripts.generate_dataset` | (re)writes `app/data/courses.csv` deterministically |
| `python -m scripts.build_cache` | fits the TF-IDF+SVD space and pickles it (cold ≈ 12 s) so the first request is instant |
| `python -m scripts.eval_recommender` | the **accuracy gate** — 14 checks, exits non-zero on failure |

"Training" here = fitting the `TfidfVectorizer` + `TruncatedSVD` on the course
corpus (done in `build_cache` / at startup) and building the DAG. There is no
gradient training loop; the per-learner ranker weights are the only online-learned
parameters.

**`eval_recommender` checks:**
1. engine warms; cold fit < 120 s.
2. For 8 sample goals, ≥ 65% of the returned courses are on-topic (matched against a
   hand-listed relevant vocabulary per goal).
3. **Mean precision ≥ 0.85** (currently ≈ **0.94**).
4. Every generated path is topologically valid (no course before its prerequisite).
5. 0 unresolved prerequisites in the dataset.
6. A 👎 on a quality-driven course lowers that learner's `quality` weight.

---

## 15. Running it

```bash
# ---- backend ----
cd backend
python -m venv venv && venv/Scripts/activate      # Windows;  source venv/bin/activate elsewhere
pip install -r requirements.txt
cp .env.example .env                                # REQUIRED: set MONGODB_URI (+ optional AI keys)
python -m scripts.build_cache                       # fit + cache the semantic space (~12s cold)
python -m scripts.eval_recommender                  # accuracy gate
uvicorn app.main:app --reload --port 8000           # log: "[mongo] connected" then "[ml.engine] warm complete"
#   API docs: http://localhost:8000/docs

# ---- frontend ----
cd ../frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
#   app: http://localhost:5173  (register → profile → Find My Career → roadmap)
```

**Dependencies** (`requirements.txt`): `fastapi`, `uvicorn`, `pydantic`,
`pymongo`, `dnspython`, `bcrypt`, `pyjwt`, `pandas`, `scikit-learn`, `scipy`,
`numpy`, `joblib`, `networkx`, `requests`; `openai` + `google-generativeai` are
optional (assistant / path explanation / opt-in quiz generation).
No `sqlalchemy`, no `torch` / `transformers` / `sentence-transformers`.
