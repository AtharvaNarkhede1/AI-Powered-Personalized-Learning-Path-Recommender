"""Phased, prerequisite-ordered path planner.

1. pick 1-3 tracks most similar to the goal (bounded by the time budget)
2. walk each track's tier ladder, ranker picks the best provider variant per tier
3. pull in any unmet prerequisite rungs (topological validity by construction)
4. order every course by (graph depth, tier, -score) and split into <=4 phases
5. attach an auto project + a diagnostic quiz per phase
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from app.ml.catalog import Catalog, Rung, TIER_NAME
from app.ml.explain import explain
from app.ml.ranker import Ranker, RankingContext, ScoredCourse

PHASE_TITLES = {
    0: "Phase 1: Foundations & Core Tools",
    1: "Phase 2: Applied Engineering & Systems",
    2: "Phase 3: Advanced Specialisation",
    3: "Phase 4: Industry Capstone & Job Readiness",
}
PHASE_DESC = {
    0: "Build the base vocabulary, math, and tooling every later step assumes.",
    1: "Apply the fundamentals to real components and workflows.",
    2: "Go deep on the specialised skills that define the role.",
    3: "Ship an end-to-end portfolio project and close remaining gaps.",
}


@dataclass
class PlanItem:
    pos: int
    rung: Rung
    tier: int
    score: float
    factors: Dict[str, float]
    contributions: Dict[str, float]
    why_now: str
    unlocks: List[str]
    phase: int


@dataclass
class LearningPlan:
    tracks: List[str]
    items: List[PlanItem]
    waivers: List[str] = field(default_factory=list)
    phases: List[int] = field(default_factory=list)


class Planner:
    def __init__(self, catalog: Catalog, graph, ranker: Ranker, semantic):
        self.cat = catalog
        self.graph = graph
        self.ranker = ranker
        self.sem = semantic
        self._track_centroids = self._build_track_centroids()

    def _build_track_centroids(self) -> Dict[tuple, np.ndarray]:
        out = {}
        for key, positions in self.cat.track_index.items():
            out[key] = self.sem.course_vectors[positions].mean(axis=0)
        return out

    def _pick_tracks(self, ctx: RankingContext, goal_vec: np.ndarray, weekly: int,
                     timeline_weeks: int, must_tracks: List[str] | None = None) -> List[tuple]:
        pref = ctx.preferred_branches
        must = [m.lower() for m in (must_tracks or [])]
        scored = []
        for (branch, track), cen in self._track_centroids.items():
            s = float(np.dot(cen, goal_vec))
            if pref and branch not in pref:
                s -= 0.15                      # keep the path within the learner's branches
            scored.append((s, (branch, track)))
        scored.sort(key=lambda x: -x[0])

        capacity = max(1, weekly) * max(2, timeline_weeks)
        n = int(np.clip(capacity // 70, 3, 6))

        picked, seen = [], set()

        def _add(key):
            if key[1].lower() in seen:
                return
            seen.add(key[1].lower())
            picked.append(key)

        # 1) forced tracks (biggest gaps + role portfolio), best branch variant
        by_name: Dict[str, tuple] = {}
        for s, key in scored:
            by_name.setdefault(key[1].lower(), (s, key))
        for m in must:
            if m in by_name and len(picked) < n:
                _add(by_name[m][1])
        # 2) fill the rest by similarity
        for _, key in scored:
            if len(picked) >= n:
                break
            _add(key)
        return picked

    def _best_variant(self, ctx: RankingContext, rung: Rung, exclude: set) -> ScoredCourse | None:
        positions = self.cat.variant_index.get(rung, [])
        ranked = self.ranker.rank(ctx, positions, limit=1, exclude=exclude, one_per_rung=False)
        return ranked[0] if ranked else None

    def build_plan(self, ctx: RankingContext, goal_vec: np.ndarray, weekly: int,
                   timeline_weeks: int, target_tier: int, must_tracks=None) -> LearningPlan:
        tracks = self._pick_tracks(ctx, goal_vec, weekly, timeline_weeks, must_tracks)
        # a stated level waives lower rungs; prerequisite closure pulls back
        # anything genuinely required, so this never breaks ordering
        start_tier = min(target_tier, 2)

        chosen: Dict[Rung, ScoredCourse] = {}
        waivers: List[str] = []
        used_pos: set = set()

        is_portfolio = lambda t: t.lower().endswith("portfolio")
        for (branch, track) in tracks:
            for tier in range(4):
                rung = (branch, track, tier)
                if rung not in self.cat.variant_index:
                    continue
                if is_portfolio(track) and tier < 1:
                    continue                    # the role portfolio starts at Applied, not Foundations
                if tier < start_tier:
                    ctx.satisfied_rungs.add(rung)
                    waivers.append(f"{track} - {TIER_NAME[tier]} (waived: matches your stated level)")
                    continue
                sc = self._best_variant(ctx, rung, used_pos)
                if sc:
                    chosen[rung] = sc
                    used_pos.add(sc.pos)

        # prerequisite closure -- but never add a rung whose (track, tier) is
        # already covered by another branch's variant we've picked
        def _covered(r):
            return any(r[1] == k[1] and r[2] == k[2] for k in chosen)

        queue = list(chosen.keys())
        while queue:
            rung = queue.pop()
            for pre in self.graph.prereq_rungs(rung):
                if pre in chosen or pre in ctx.satisfied_rungs or _covered(pre):
                    continue
                if pre not in self.cat.variant_index:
                    continue
                sc = self._best_variant(ctx, pre, used_pos)
                if sc:
                    chosen[pre] = sc
                    used_pos.add(sc.pos)
                    queue.append(pre)

        if not chosen:
            return LearningPlan(tracks=[t for _, t in tracks], items=[])

        # collapse any remaining (track, tier) duplicates, keeping the best score
        best_by_key: Dict[tuple, tuple] = {}
        for rung, sc in chosen.items():
            key = (rung[1], rung[2])
            if key not in best_by_key or sc.score > best_by_key[key][1].score:
                best_by_key[key] = (rung, sc)
        chosen = {rung: sc for rung, sc in best_by_key.values()}

        ordered = sorted(
            chosen.items(),
            key=lambda kv: (self.graph.depth.get(kv[0], 0), kv[0][2], -kv[1].score),
        )

        # phase = tier, collapsed so we never exceed 4 and never skip
        tiers_present = sorted({r[2] for r, _ in ordered})
        phase_of = {t: i for i, t in enumerate(tiers_present)}

        items: List[PlanItem] = []
        for rung, sc in ordered:
            row = self.cat.df.iloc[sc.pos]
            info = explain(sc, row)
            unlocks = [
                self.cat.df.iloc[chosen[succ].pos]["course_title"]
                for succ in self.graph.g.successors(rung) if succ in chosen
            ] if rung in self.graph.g else []
            prereq_titles = [
                self.cat.df.iloc[chosen[pre].pos]["course_title"]
                for pre in self.graph.prereq_rungs(rung) if pre in chosen
            ]
            if prereq_titles:
                why = f"Take this after {prereq_titles[0]}. {info['headline']}"
            else:
                why = f"Start here. {info['headline']}"
            items.append(PlanItem(
                pos=sc.pos, rung=rung, tier=rung[2], score=sc.score,
                factors=sc.factors, contributions=sc.contributions,
                why_now=why, unlocks=unlocks, phase=phase_of[rung[2]],
            ))

        return LearningPlan(
            tracks=[t for _, t in tracks], items=items, waivers=waivers,
            phases=sorted(phase_of.values()),
        )
