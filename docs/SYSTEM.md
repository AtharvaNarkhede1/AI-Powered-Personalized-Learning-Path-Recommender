# CareerPath AI — Full System Documentation

A local, explainable engine that turns an engineering student's profile into
(1) a **ranked list of courses** and (2) a **prerequisite-ordered, phased learning
path**, with YouTube playlists as a secondary supplement and a data-grounded chat
assistant on top.

Everything runs offline. No API key is required. `GEMINI_API_KEY` / `OPENAI_API_KEY`
only upgrade the (already grounded) chat assistant to a live LLM; `YOUTUBE_API_KEY`
only upgrades the YouTube section from a search link to ranked results.

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
  React SPA (Vite)  ───▶  │  FastAPI  (app/main.py, 10 routers)          │
  frontend/src/*         │                                             │
                         │  app/api/*      thin HTTP layer              │
                         │  app/services/* career match, skill gap,     │
                         │                 youtube, ai assistant,       │
                         │                 path persistence            │
                         │  app/ml/*       THE ENGINE  ◀── warmed once  │
                         │  app/data/*     courses.csv + taxonomy       │
                         │  app/db/*       SQLAlchemy + SQLite          │
                         └─────────────────────────────────────────────┘

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

1. `uvicorn app.main:app` → `Base.metadata.create_all()` creates the SQLite tables.
2. `@app.on_event("startup")` calls `engine.warm()`:
   - `load_catalog(courses.csv)` → pandas DataFrame + indices (§6.1)
   - `load_or_fit()` → loads `app/ml/cache/semantic.pkl` if its key
     `(csv_mtime, row_count)` matches, otherwise **fits** the TF-IDF+SVD space
     (~12 s cold) and pickles it (~43 MB, includes the raw TF-IDF matrix)
   - `build_graph()` → the prerequisite DAG
   - constructs `Ranker` and `Planner`
3. First request is now instant; subsequent restarts reload the cache in ~3 s.

### 3.2 A learner's journey

```
Onboarding wizard  (5 steps)
        │  POST /api/onboarding/{user_id}   → upserts LearnerProfileDB
        ▼
Career Discovery
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
        │        → persisted via path_store.save_path (LearningPathDB + MilestoneDB)
        ▼
Take a milestone quiz
        │  POST /api/assessments/submit
        │        grade → write SkillProficiencyDB(evidence_source="assessment")
        │        → re-run skill-gap analysis → update the path's readiness score
        ▼
Give feedback (👍/👎 on a course)
        │  POST /api/recommendations/feedback
        │        engine.record_feedback:
        │          nudge this learner's ranker weights toward/away from the
        │          factors that actually drove that course (stored in LearnerModelDB)
        ▼
Dashboard / Chat
           POST /api/analytics/dashboard   → readiness, milestone counts, skill radar
           POST /api/assistant/chat        → grounded answer from the real path/gaps
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
  `projects` · `compare` · `default`. Each template pulls the specific real values
  (e.g. `why_path` cites the first 3 courses and their real `why_now`;
  `weak_areas` lists the real top-3 gaps and the path courses that close them;
  `timeline` uses the real `estimated_weeks`).
- `suggested_followups` and `referenced_resources` are always dynamic (depend on
  intent + what's in the path). When an LLM answers, the offline engine still
  supplies those.

---

## 10. Inputs & outputs — the REST API

Base URL `http://localhost:8000/api`. No auth enforced; a learner is identified by
`user_id` in the body (default `"demo_user_1"`). Interactive docs at `/docs`.

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

## 11. Persistence — database models

SQLAlchemy + SQLite (`backend/learning_path.db`). Tables auto-created on startup;
**no migrations** — schema changes require deleting the DB file.

| Table | Key columns |
|---|---|
| `users` | `id`, `email`, `hashed_password` (stub) |
| `learner_profiles` | all 15 onboarding fields, `target_career_id`; 1 per user |
| `skill_proficiencies` | `profile_id`, `skill_id`, `current_proficiency`, `evidence_source` (`self_report` / `assessment` / `project`) — only `assessment` rows are trusted by the gap engine |
| `learning_paths` | `profile_id`, `career_id`, `is_active`, `job_readiness_score`, `estimated_total_hours/weeks`, `next_action` (JSON), `what_not_to_do_warnings` (JSON), `track_names` (JSON) |
| `milestones` | `path_id`, `milestone_key`, `sequence_order`, `title`, `target_skills` (JSON), `status`, `estimated_hours`, `resources` (JSON), `project` (JSON), `assessment` (JSON), `youtube_extras` (JSON) |
| `learner_models` | `profile_id` (unique), `weights` (JSON), `affinities` (JSON), `update_count` — the adaptive ranker state |
| `user_feedback` | `user_id`, `resource_id`, `feedback_type`, append-only |
| `assessment_submissions` | `user_id`, `assessment_id`, `skill_id`, `score_percentage`, `answers` (JSON) |

`app/services/path_store.py` is the persistence layer: `get_or_create_profile`,
`get_active_path`, `save_path` (upsert — deletes & re-inserts milestone rows),
`get_feedback_history`, `record_feedback`, and the `Milestone ↔ MilestoneDB` mappers.

---

## 12. Frontend

React 18 + Vite, single-page, tab-based (`frontend/src/App.jsx`), no router.
`frontend/src/api/client.js` is the fetch wrapper; base URL from
`VITE_API_BASE_URL` (`.env`) + `/api`.

| Tab / component | What it shows |
|---|---|
| `LandingPage` | pitch: ranked courses → prerequisite-ordered path → YouTube supplements |
| `OnboardingWizard` | the 5-step profile form; skill/interest autocomplete via `/onboarding/keywords/search` |
| `CareerDiscovery` | top-3 match cards + clarification question + 3-way compare modal |
| `RecommendationsView` | goal box, ranked course cards with driver % chips and 👍/👎, an explainer of what the %s mean — **the screen a career selection lands on** |
| `LearningPathTimeline` | the phased milestones: a numbered, rail-connected ordered course list with "start here / take this after X / prepares you for Y", a distinct "📺 Also recommended on YouTube" block, the milestone project, and a quiz button |
| `Dashboard` | readiness %, hours, milestone progress, a Recharts current-vs-required skill bar chart |
| `ChatInterface` | the assistant; quick-prompt chips |

There is **no API-key UI** — keys live in `backend/.env` only. The nav shows a
read-only badge with the active LLM mode from `/system/status`.

---

## 13. Configuration

`backend/.env` (copy from `.env.example`). All optional:

| Var | Effect if unset |
|---|---|
| `GEMINI_API_KEY` / `OPENAI_API_KEY` | assistant uses the grounded offline engine |
| `YOUTUBE_API_KEY` | YouTube block shows a playlist search link instead of ranked results |
| `DATABASE_URL` | `sqlite:///./learning_path.db` |
| `COURSES_CSV` | `app/data/courses.csv` |
| `ML_CACHE_DIR` | `app/ml/cache` |

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
python -m scripts.generate_dataset                 # ~18k rows -> app/data/courses.csv
python -m scripts.build_cache                       # fit + cache the semantic space
python -m scripts.eval_recommender                  # 14/14 expected
cp .env.example .env                                # optional: add GEMINI/OPENAI/YOUTUBE keys
uvicorn app.main:app --reload --port 8000           # startup log: "[ml.engine] warm complete in ~12s"
#   API docs: http://localhost:8000/docs

# ---- frontend ----
cd ../frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
#   app: http://localhost:5173
```

**Dependencies** (`requirements.txt`): `fastapi`, `uvicorn`, `pydantic`,
`sqlalchemy`, `pandas`, `scikit-learn`, `scipy`, `numpy`, `joblib`, `networkx`,
`requests`; `openai` + `google-generativeai` are optional (assistant only).
No `torch` / `transformers` / `sentence-transformers`.
