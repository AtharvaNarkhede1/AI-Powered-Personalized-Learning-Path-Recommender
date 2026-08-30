from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np
from app.ml.catalog import Catalog, Rung
FACTORS = ['goal_fit', 'skill_gain', 'branch_fit', 'level_fit', 'quality', 'prereq_ready', 'effort_fit', 'format_pref']
FACTOR_LABEL = {'goal_fit': 'matches your goal', 'skill_gain': 'closes your skill gaps', 'branch_fit': 'fits your engineering branch', 'level_fit': 'fits your level', 'quality': 'is highly rated', 'prereq_ready': "you're ready for it", 'effort_fit': 'fits your time budget', 'format_pref': 'matches your preferred format'}
DEFAULT_WEIGHTS = {'goal_fit': 0.26, 'skill_gain': 0.18, 'branch_fit': 0.13, 'level_fit': 0.12, 'quality': 0.1, 'prereq_ready': 0.1, 'effort_fit': 0.06, 'format_pref': 0.05}

@dataclass
class RankingContext:
    goal_sims: np.ndarray
    gap_terms: Dict[str, float]
    target_tier: int
    weekly_hours: int
    preferred_format: str
    satisfied_rungs: set
    preferred_branches: set = field(default_factory=set)
    home_branch: str = ''
    career_branches: set = field(default_factory=set)
    gap_sims: Optional[np.ndarray] = None
    weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    affinities: Dict[str, float] = field(default_factory=dict)

@dataclass
class ScoredCourse:
    pos: int
    score: float
    factors: Dict[str, float]
    contributions: Dict[str, float]
    rung: Rung

def _level_fit(tier: int, target: int) -> float:
    diff = tier - target
    pen = 0.14 * abs(diff) if diff <= 0 else 0.32 * diff
    return float(np.clip(1.0 - pen, 0.0, 1.0))

def _skill_gain_tokens(doc_skills: List[str], skills_text: str, gap_terms: Dict[str, float]) -> float:
    if not gap_terms:
        return 0.4
    hit = 0.0
    total = sum(gap_terms.values()) or 1.0
    for term, w in gap_terms.items():
        head = term.split('(')[0].strip()
        if head and (head in skills_text or any((head in s or s in head for s in doc_skills))):
            hit += w
    return float(np.clip(hit / total, 0.0, 1.0))

class Ranker:

    def __init__(self, catalog: Catalog, graph):
        self.cat = catalog
        self.graph = graph

    def _prereq_ready(self, rung: Rung, satisfied: set) -> float:
        if rung not in self.graph.g:
            return 1.0
        preds = list(self.graph.g.predecessors(rung))
        if not preds:
            return 1.0
        met = sum((1 for p in preds if p in satisfied))
        return float(0.25 + 0.75 * (met / len(preds)))

    def rank(self, ctx: RankingContext, positions: List[int], limit: int=12, exclude: set | None=None, one_per_rung: bool=True) -> List[ScoredCourse]:
        exclude = exclude or set()
        positions = [p for p in positions if p not in exclude]
        if not positions:
            return []
        weights = {f: ctx.weights.get(f, DEFAULT_WEIGHTS[f]) for f in FACTORS}
        if not ctx.home_branch and (not ctx.career_branches):
            weights['goal_fit'] += weights['branch_fit']
            weights['branch_fit'] = 0.0
        wsum = sum(weights.values()) or 1.0
        pool_goal_max = max((ctx.goal_sims[p] for p in positions), default=1.0) or 1.0
        pool_gap_max = 1.0
        if ctx.gap_sims is not None:
            pool_gap_max = max((ctx.gap_sims[p] for p in positions), default=1.0) or 1.0
        scored: List[ScoredCourse] = []
        for p in positions:
            row = self.cat.df.iloc[p]
            rung: Rung = (row['branch'], row['track'], int(self.cat.tiers[p]))
            if ctx.gap_sims is not None:
                skill_gain = float(ctx.gap_sims[p] / pool_gap_max)
            else:
                skill_gain = _skill_gain_tokens(self.cat.skill_lists[p], str(row['skills_taught']).lower(), ctx.gap_terms)
            b = row['branch']
            if ctx.home_branch and b == ctx.home_branch:
                branch_fit = 1.0
            elif b in ctx.career_branches:
                branch_fit = 0.82
            elif not ctx.preferred_branches or b in ctx.preferred_branches:
                branch_fit = 0.62
            else:
                branch_fit = 0.35
            fv = {'goal_fit': float(ctx.goal_sims[p] / pool_goal_max), 'skill_gain': skill_gain, 'branch_fit': branch_fit, 'level_fit': _level_fit(int(self.cat.tiers[p]), ctx.target_tier), 'quality': float(self.cat.quality[p]), 'prereq_ready': self._prereq_ready(rung, ctx.satisfied_rungs), 'effort_fit': float(np.clip(1.0 - (row['estimated_hours'] - 3 * ctx.weekly_hours) / max(1.0, 3 * ctx.weekly_hours), 0.0, 1.0)), 'format_pref': 1.0 if ctx.preferred_format and ctx.preferred_format.split('-')[0] in str(row['format']).lower() else 0.5}
            weighted = {f: fv[f] * weights[f] for f in FACTORS}
            base = sum(weighted.values()) / wsum
            aff = ctx.affinities.get(f'track:{row['track']}', 0.0) + ctx.affinities.get(f'provider:{row['provider']}', 0.0)
            score = float(np.clip(base + 0.05 * aff, 0.0, 1.2))
            rowsum = sum(weighted.values()) or 1.0
            contrib = {f: weighted[f] / rowsum for f in FACTORS}
            scored.append(ScoredCourse(pos=p, score=score, factors=fv, contributions=contrib, rung=rung))
        scored.sort(key=lambda s: -s.score)
        if one_per_rung:
            seen, out = (set(), [])
            for s in scored:
                if s.rung in seen:
                    continue
                seen.add(s.rung)
                out.append(s)
                if len(out) >= limit:
                    break
            return out
        return scored[:limit]
