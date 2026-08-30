from __future__ import annotations
import time
from typing import Dict, List, Optional
import numpy as np
from app.core.config import settings
from app.ml.catalog import Catalog, TIER_NAME, load_catalog
from app.ml.graph import PrereqGraph, build_graph
from app.ml.planner import LearningPlan, Planner
from app.ml.ranker import DEFAULT_WEIGHTS, FACTORS, Ranker, RankingContext
from app.ml.semantic import SemanticSpace, load_or_fit
from app.models.schemas import (
    LearningPathResponse, Milestone, NextRecommendedAction, ResourceItem,
)
EXP_TIER = {"beginner": 0, "intermediate": 1, "advanced": 2}
class Engine:
    def __init__(self) -> None:
        self.catalog: Optional[Catalog] = None
        self.semantic: Optional[SemanticSpace] = None
        self.graph: Optional[PrereqGraph] = None
        self.ranker: Optional[Ranker] = None
        self.planner: Optional[Planner] = None
        self._ready = False
    def warm(self) -> None:
        if self._ready:
            return
        t0 = time.time()
        self.catalog = load_catalog(settings.COURSES_CSV)
        self.semantic = load_or_fit(self.catalog, settings.COURSES_CSV, settings.ML_CACHE_DIR)
        self.graph = build_graph(self.catalog)
        self.ranker = Ranker(self.catalog, self.graph)
        self.planner = Planner(self.catalog, self.graph, self.ranker, self.semantic)
        self._ready = True
        print(f"[ml.engine] warm complete in {time.time() - t0:.2f}s "
              f"({len(self.catalog)} courses, {len(self.graph.g)} rungs, "
              f"{len(self.graph.unresolved)} unresolved prereqs)")
    def _require(self) -> None:
        if not self._ready:
            self.warm()
    def text_sim(self, a: str, b: str) -> float:
        self._require()
        return self.semantic.text_similarity(a, b)
    def best_text_sim(self, query: str, candidates) -> float:
        self._require()
        return self.semantic.best_text_similarity(query, candidates)
    def _query_sims(self, text: str) -> np.ndarray:
        """Hybrid similarity of every course to `text`, with pseudo-relevance
        feedback for short queries: the skill tokens of the initial top matches
        are folded back into the query so 'cybersecurity' also pulls in
        networking/crypto courses, not just the one lexical hit."""
        sims = self.semantic.hybrid_to_courses(text)
        if len((text or "").split()) > 7:
            return sims
        top = np.argsort(-sims)[:10]
        toks: List[str] = []
        for p in top:
            toks.extend(self.catalog.skill_lists[p][:3])
            toks.append(str(self.catalog.df.iloc[p]["track"]).lower())
        expanded = text + " " + " ".join(dict.fromkeys(toks))
        sims2 = self.semantic.hybrid_to_courses(expanded)
        return np.clip(0.55 * sims + 0.45 * sims2, 0.0, 1.0)
    def interpret_profile(self, profile, career_id: Optional[str] = None,
                          gap_names: Optional[List[str]] = None) -> str:
        from app.data.taxonomy_data import CAREERS_DATABASE
        bits: List[str] = []
        cid = career_id or getattr(profile, "target_career_id", None)
        if cid:
            c = next((c for c in CAREERS_DATABASE if c["career_id"] == cid), None)
            if c:
                bits.append(f"{c['title']}. {c['category']}. {c['description']}")
                bits.append(" ".join(c["key_responsibilities"][:3]))
                bits.append(" ".join(s["name"] for s in c["required_skills"]))
        if getattr(profile, "interests", None):
            bits.append("interests: " + ", ".join(profile.interests))
        if getattr(profile, "engineering_branch", None):
            bits.append("branch: " + profile.engineering_branch)
        if gap_names:
            bits.append("focus skills: " + ", ".join(gap_names[:8]))
        return ". ".join(bits) or "engineering career skills"
    def _learner_model(self, user_id: Optional[str]):
        weights = dict(DEFAULT_WEIGHTS)
        affinities: Dict[str, float] = {}
        if not user_id:
            return weights, affinities, None
        try:
            from app.db import repository
            row = repository.get_learner_model(user_id)
            if row:
                weights.update({k: v for k, v in (row.get("weights") or {}).items() if k in FACTORS})
                affinities.update(row.get("affinities") or {})
            return weights, affinities, row
        except Exception:
            return weights, affinities, None

    def _context(self, profile, career_id, user_id=None):
        self._require()
        from app.services.skill_gap_engine import analyze_skill_gaps
        gap = None
        gap_terms: Dict[str, float] = {}
        gap_names: List[str] = []
        try:
            gap = analyze_skill_gaps(career_id, profile, user_id=user_id) if career_id else None
        except Exception:
            gap = None
        if gap:
            for g in gap.gaps:
                if g.gap_delta > 0:
                    gap_terms[g.skill_name.lower()] = float(g.gap_delta)
                    gap_names.append(g.skill_name)
        if not gap_terms and career_id:
            from app.data.taxonomy_data import CAREERS_DATABASE
            c = next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), None)
            if c:
                for r in c["required_skills"]:
                    gap_terms[r["name"].lower()] = 0.5
                    gap_names.append(r["name"])
        goal_text = self.interpret_profile(profile, career_id, gap_names)
        goal_vec = self.semantic.encode(goal_text)
        goal_sims = self._query_sims(goal_text)
        gap_sims = None
        if gap_names:
            gap_sims = self._query_sims(" . ".join(gap_names))
        weights, affinities, _ = self._learner_model(user_id)
        exp = (getattr(profile, "experience_level", "intermediate") or "intermediate").lower()
        target_tier = EXP_TIER.get(next((k for k in EXP_TIER if k in exp), "intermediate"), 1)
        home_branch = getattr(profile, "engineering_branch", "") or ""
        career_branches: set = set()
        if career_id:
            from app.data.taxonomy_data import CAREERS_DATABASE
            c = next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), None)
            if c:
                career_branches.add(c["branch_primary"])
                career_branches.update(c.get("branches_compatible", []))
        preferred = set(career_branches)
        if home_branch:
            preferred.add(home_branch)
        ctx = RankingContext(
            goal_sims=goal_sims, gap_terms=gap_terms, gap_sims=gap_sims,
            target_tier=target_tier, preferred_branches=preferred,
            home_branch=home_branch, career_branches=career_branches,
            weekly_hours=max(3, int(getattr(profile, "hours_per_week", 10) or 10)),
            preferred_format=(getattr(profile, "preferred_format", "") or "").lower(),
            satisfied_rungs=set(), weights=weights, affinities=affinities,
        )
        return ctx, goal_vec, goal_text, gap, gap_names
    def _candidate_pool(self, ctx: RankingContext, career_id: Optional[str],
                        goal_vec: Optional[np.ndarray] = None) -> List[int]:
        cat = self.catalog
        pool: set = set()
        if career_id:
            from app.data.taxonomy_data import CAREERS_DATABASE
            c = next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), None)
            if c:
                pool |= set(cat.career_index.get(c["title"].lower(), []))
        pool |= {int(p) for p in np.argsort(-ctx.goal_sims)[:2500]}
        if goal_vec is not None and self.planner is not None:
            tsim = sorted(
                ((float(np.dot(cen, goal_vec)), key) for key, cen in self.planner._track_centroids.items()),
                key=lambda x: -x[0],
            )[:18]
            for _, key in tsim:
                pool |= set(cat.track_index.get(key, []))
        pool = [p for p in pool if not str(cat.df.iloc[p]["track"]).endswith("Portfolio")]
        return sorted(pool)
    def _mmr(self, ranked, limit: int, lam: float = 0.72):
        """Greedy MMR: keep the ranked order but skip a course too similar (in the
        LSA space) to one already picked, so the list isn't 10 near-identical rows."""
        picked, picked_vecs = [], []
        for sc in ranked:
            v = self.semantic.course_vectors[sc.pos]
            if picked_vecs:
                max_sim = max(float(v @ pv) for pv in picked_vecs)
            else:
                max_sim = 0.0
            if max_sim > 0.93:
                continue
            picked.append(sc)
            picked_vecs.append(v)
            if len(picked) >= limit:
                break
        return picked
    def recommend(self, profile, user_id: Optional[str] = None, goal_text: Optional[str] = None,
                  career_id: Optional[str] = None, limit: int = 12,
                  exclude_planned: bool = False) -> dict:
        self._require()
        ctx, goal_vec, derived_goal, gap, _ = self._context(profile, career_id, user_id)
        if goal_text:
            goal_vec = self.semantic.encode(goal_text)
            ctx.goal_sims = self._query_sims(goal_text)
            derived_goal = goal_text
        exclude: set = set()
        if exclude_planned and user_id:
            exclude = self._planned_positions(user_id)

        pool = [p for p in self._candidate_pool(ctx, career_id, goal_vec) if p not in exclude]
        ranked = self.ranker.rank(ctx, pool, limit=limit * 8, one_per_rung=True)
        seen_track, dedup = set(), []
        for sc in ranked:
            tr = str(self.catalog.df.iloc[sc.pos]["track"]).lower()
            if tr in seen_track:
                continue
            seen_track.add(tr)
            dedup.append(sc)
        final = self._mmr(dedup, limit)
        if final:
            keep_min = min(2, len(final))
            best_sim = max(ctx.goal_sims[sc.pos] for sc in final)
            best_score = final[0].score
            final = [sc for i, sc in enumerate(final)
                     if i < keep_min
                     or (ctx.goal_sims[sc.pos] >= 0.30 * best_sim and sc.score >= 0.52 * best_score)]
        results = [self._resource_item(sc.pos, sc) for sc in final]
        return {"goal": derived_goal, "count": len(results), "results": [r.model_dump() for r in results]}
    def _planned_positions(self, user_id) -> set:
        try:
            from app.db import repository
            out = set()
            for title in repository.planned_resource_titles(user_id):
                out |= set(self.catalog.title_index.get(title, []))
            return out
        except Exception:
            return set()
    def resource_for_course_id(self, course_id: str) -> Optional[ResourceItem]:
        self._require()
        pos = self.catalog.df.index[self.catalog.df["course_id"] == course_id].tolist()
        if not pos:
            return None
        return self._resource_item(int(pos[0]))
    def tier_for_course_id(self, course_id: str) -> int:
        self._require()
        pos = self.catalog.df.index[self.catalog.df["course_id"] == course_id].tolist()
        return int(self.catalog.tiers[int(pos[0])]) if pos else 0
    def _resource_item(self, pos: int, sc=None) -> ResourceItem:
        row = self.catalog.df.iloc[pos]
        cid = str(row["course_id"])
        skills = self.catalog.skill_lists[pos]
        item = ResourceItem(
            id=cid, course_id=cid, title=str(row["course_title"]),
            type="course", provider=str(row["provider"]),
            url=f"https://www.google.com/search?q=" + str(row["course_title"]).replace(" ", "+") + "+" + str(row["provider"]).replace(" ", "+"),
            duration_hours=float(row["estimated_hours"]),
            difficulty=str(row["difficulty_level"]).lower(),
            skills_covered=skills[:8],
            rating=float(row["rating"]), num_reviews=int(row["num_reviews"]),
            is_free=str(row["provider"]) in ("NPTEL", "MITx", "edX"),
            track=str(row["track"]), branch=str(row["branch"]),
        )
        if sc is not None:
            from app.ml.explain import explain
            info = explain(sc, row)
            item.match_reason = info["headline"]
            item.factor_contributions = {k: round(v, 3) for k, v in sc.contributions.items()}
        return item
    def build_path(self, profile, career_id: str, user_id=None) -> LearningPathResponse:
        self._require()
        from app.data.taxonomy_data import CAREERS_DATABASE
        career = next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), CAREERS_DATABASE[0])
        ctx, goal_vec, goal_text, gap, gap_names = self._context(profile, career["career_id"], user_id)
        weekly = ctx.weekly_hours
        timeline_weeks = max(4, int(getattr(profile, "target_timeline_months", 6) or 6) * 4)
        must_tracks: List[str] = []
        for name in gap_names[:5]:
            key = name.lower()
            for tname in self.catalog.tracks_vocab:
                if tname == key:
                    must_tracks.append(tname)
                    break
        must_tracks.append(f"{career['title'].lower()} portfolio")
        plan: LearningPlan = self.planner.build_plan(
            ctx, goal_vec, weekly, timeline_weeks, ctx.target_tier, must_tracks=must_tracks)
        milestones = self._plan_to_milestones(plan, weekly)
        readiness = self._readiness(gap, profile)
        warnings = self._warnings(profile, career, gap.gaps if gap else [])
        first = milestones[0].resources[0] if milestones and milestones[0].resources else None
        next_action = NextRecommendedAction(
            action_type="start_course",
            title=f"Start '{first.title}'" if first else "Begin your first milestone",
            description=(f"Kick off {milestones[0].title} to build momentum." if milestones
                        else "Complete onboarding to generate your path."),
            milestone_id=milestones[0].id if milestones else "ms_1",
            resource_id=first.id if first else None, estimated_minutes=45, urgency="high",
        )
        return LearningPathResponse(
            id=f"path_{career['career_id']}", career_id=career["career_id"],
            career_title=career["title"], job_readiness_score=readiness["score"],
            base_readiness_score=readiness["score"],
            estimated_total_hours=readiness["hours"], estimated_weeks=readiness["weeks"],
            hours_per_week=weekly, milestones=milestones, next_action=next_action,
            what_not_to_do_warnings=warnings, track_names=plan.tracks,
        )
    def _plan_to_milestones(self, plan: LearningPlan, weekly: int) -> List[Milestone]:
        from app.data.taxonomy_data import QUIZZES_DATABASE, SKILLS_DATABASE
        from app.ml.planner import PHASE_DESC, PHASE_TITLES
        real_skill_names = {s["name"].lower() for s in SKILLS_DATABASE.values()}
        by_phase: Dict[int, list] = {}
        for it in plan.items:
            by_phase.setdefault(it.phase, []).append(it)
        import math
        groups: List[tuple] = []
        for phase in sorted(by_phase):
            ph_items = by_phase[phase]
            if len(ph_items) <= 7:
                groups.append((phase, 0, ph_items))
                continue
            k = math.ceil(len(ph_items) / 6)
            size = math.ceil(len(ph_items) / k)
            for i in range(0, len(ph_items), size):
                groups.append((phase, i // size + 1, ph_items[i:i + size]))
        milestones: List[Milestone] = []
        for seq, (phase, part, items) in enumerate(groups, start=1):
            resources: List[ResourceItem] = []
            skill_names: List[str] = []
            for it in items:
                ri = self._resource_item(it.pos)
                ri.match_reason = it.why_now
                ri.why_now = it.why_now
                ri.unlocks = it.unlocks
                ri.factor_contributions = {k: round(v, 3) for k, v in it.contributions.items()}
                resources.append(ri)
                skill_names.extend(ri.skills_covered)
            skill_names = list(dict.fromkeys(skill_names))[:8]
            est_hours = int(sum(r.duration_hours for r in resources) + 6)
            yt_terms = [s for s in skill_names if s in real_skill_names][:3] \
                or [it.rung[1] for it in items[:3]]
            yt = self.youtube_extras(yt_terms)
            quiz = None
            for it in items:
                row = self.catalog.df.iloc[it.pos]
                for sid, q in QUIZZES_DATABASE.items():
                    if q["skill_name"].lower() in str(row["skills_taught"]).lower() or sid in str(row["track"]).lower():
                        quiz = {"assessment_id": q["assessment_id"], "title": q["title"], "description": q["description"]}
                        break
                if quiz:
                    break
            ttl = PHASE_TITLES.get(phase, f"Phase {seq}")
            if part:
                ttl = f"{ttl} (Part {part})"
            milestones.append(Milestone(
                id=f"ms_{seq}", sequence_order=seq,
                title=ttl,
                description=PHASE_DESC.get(phase, "Work through these courses in order."),
                estimated_hours=est_hours, estimated_weeks=max(1, round(est_hours / max(1, weekly))),
                status="in_progress" if seq == 1 else "not_started",
                target_skills=skill_names, resources=resources,
                project={
                    "title": f"{PHASE_TITLES.get(phase, 'Milestone').split(':')[-1].strip()} Project",
                    "description": f"Build a portfolio project using {', '.join(skill_names[:3])}.",
                    "required_deliverable": "GitHub repo link + short demo video",
                },
                assessment=quiz, youtube_extras=yt,
            ))
        return milestones
    def youtube_extras(self, skill_names: List[str], per_skill: int = 1) -> List[ResourceItem]:
        from app.services.youtube_service import get_dynamic_youtube_resources
        out: List[ResourceItem] = []
        seen = set()
        for name in skill_names:
            for r in get_dynamic_youtube_resources(name)[:per_skill]:
                if r["id"] in seen:
                    continue
                seen.add(r["id"])
                out.append(ResourceItem(
                    id=r["id"], title=r["title"], type="video", provider=r["provider"],
                    url=r["url"], duration_hours=float(r.get("duration_hours", 1.0)),
                    difficulty=r.get("difficulty", "beginner"),
                    skills_covered=r.get("skills_covered", [name]),
                    rating=float(r.get("rating", 4.0)), is_free=True,
                    match_reason=r.get("match_reason", f"YouTube pick for {name}"),
                ))
        return out
    def _readiness(self, gap, profile) -> dict:
        weekly = max(3, int(getattr(profile, "hours_per_week", 10) or 10))
        if not gap or not gap.gaps:
            return {"score": 35.0, "hours": 100, "weeks": max(2, round(100 / weekly))}
        total_req = sum(g.required_level for g in gap.gaps) or 0.1
        total_acq = sum(min(g.current_level, g.required_level) for g in gap.gaps)
        score = float(np.clip((total_acq / total_req) * 100, 15.0, 100.0))
        remaining = sum(g.gap_delta for g in gap.gaps)
        hours = max(30, round(remaining * 75))
        return {"score": round(score, 1), "hours": hours, "weeks": max(2, round(hours / weekly))}
    def _warnings(self, profile, career: dict, gaps) -> List[str]:
        out: List[str] = list(career.get("what_not_to_do", [])[:2])
        missing = [g.skill_name for g in gaps if getattr(g, "status", "") in ("Missing", "Major Gap") and getattr(g, "is_prerequisite", False)]
        if missing:
            out.append(f"DON'T jump to advanced {career['title']} work while {', '.join(missing[:2])} are still weak.")
        if (getattr(profile, "preferred_format", "") or "") in ("video", "text"):
            out.append("DON'T collect course completions without shipping at least 2 end-to-end portfolio projects.")
        if int(getattr(profile, "hours_per_week", 10) or 10) < 5:
            out.append("DON'T expect job-readiness in 6 months at under 5 hrs/week -- consistency drives the timeline.")
        seen, uniq = set(), []
        for w in out:
            if w not in seen:
                seen.add(w)
                uniq.append(w)
        return uniq[:4]
    def record_feedback(self, user_id: Optional[str], event_type: str,
                        course_id: Optional[str] = None, factors: Optional[dict] = None) -> dict:
        """Nudge this learner's ranker weights toward / away from the factors that
        actually drove the course they reacted to."""
        self._require()
        sign = {"upvote": 1.0, "completed": 0.6, "downvote": -1.0, "dismiss": -0.6}.get(event_type, 0.0)
        if not sign or not user_id:
            return {"updated": False}
        from app.db import repository
        weights, affinities, row = self._learner_model(user_id)
        if factors is None and course_id:
            factors = self._stored_contributions(user_id, course_id)
        factors = factors or {}
        lr = 0.12
        for f, share in factors.items():
            if f in weights:
                weights[f] = float(np.clip(weights[f] * (1.0 + sign * lr * float(share)), 0.01, 0.6))
        tot = sum(weights.values()) or 1.0
        weights = {k: v / tot for k, v in weights.items()}
        if course_id:
            pos = self.catalog.df.index[self.catalog.df["course_id"] == course_id].tolist()
            if pos:
                r = self.catalog.df.iloc[pos[0]]
                for key in (f"track:{r['track']}", f"provider:{r['provider']}"):
                    affinities[key] = float(np.clip(affinities.get(key, 0.0) + sign * 0.15, -1.0, 1.0))
        update_count = ((row or {}).get("update_count", 0) if row else 0) + 1
        repository.save_learner_model(user_id, weights, affinities, update_count)
        return {"updated": True, "weights": weights, "update_count": update_count}
    def _stored_contributions(self, user_id, course_id) -> dict:
        try:
            from app.db import repository
            return repository.stored_contributions(user_id, course_id)
        except Exception:
            return {}
    def model_snapshot(self, user_id) -> dict:
        weights, affinities, row = self._learner_model(user_id)
        return {
            "weights": [{"factor": f, "weight": round(weights[f], 3), "default": DEFAULT_WEIGHTS[f],
                         "delta": round(weights[f] - DEFAULT_WEIGHTS[f], 3)} for f in FACTORS],
            "affinities": [{"key": k, "value": round(v, 3)} for k, v in affinities.items()],
            "update_count": ((row or {}).get("update_count", 0) if row else 0),
            "personalised": bool(row),
        }
engine = Engine()